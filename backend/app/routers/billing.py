import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.enums import UserPlan
from app.models.upgrade_interest import UpgradeInterest
from app.models.user import User
from app.services.billing import create_razorpay_checkout


router = APIRouter(prefix="/billing", tags=["billing"])
logger = logging.getLogger(__name__)


class UpgradeInterestRequest(BaseModel):
    source: str = "upgrade_modal"


@router.post("/create-checkout-session")
async def create_checkout_session(current_user: User = Depends(get_current_user)):
    try:
        status_payload = create_razorpay_checkout(current_user)
    except Exception:
        logger.exception("Failed to create Razorpay checkout")
        status_payload = {
            "status": "provider_error",
            "provider": "razorpay",
            "message": "Could not create Razorpay checkout right now.",
            "checkout_url": None,
        }

    logger.info(
        "Checkout session requested",
        extra={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "provider": status_payload["provider"],
            "status": status_payload["status"],
        },
    )
    return status_payload


@router.post("/upgrade-interest")
async def record_upgrade_interest(
    payload: UpgradeInterestRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recorded_at = datetime.utcnow()
    source = (payload.source if payload else "upgrade_modal").strip() or "upgrade_modal"
    source = source[:50]

    result = await db.execute(
        select(UpgradeInterest)
        .where(UpgradeInterest.user_id == current_user.id)
        .where(UpgradeInterest.source == source)
    )
    upgrade_interest = result.scalar_one_or_none()
    already_recorded = upgrade_interest is not None

    if upgrade_interest:
        upgrade_interest.email = current_user.email
        upgrade_interest.updated_at = recorded_at
    else:
        upgrade_interest = UpgradeInterest(
            user_id=current_user.id,
            email=current_user.email,
            source=source,
        )
        db.add(upgrade_interest)

    await db.commit()

    logger.info(
        "Upgrade interest recorded",
        extra={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "plan": current_user.plan.value
            if hasattr(current_user.plan, "value")
            else str(current_user.plan),
            "source": source,
            "recorded_at": recorded_at.isoformat(),
            "already_recorded": already_recorded,
        },
    )

    return {
        "status": "recorded",
        "message": "You are on the Pro interest list.",
        "recorded_at": recorded_at,
        "already_recorded": already_recorded,
    }


@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Razorpay calls this endpoint directly (not the frontend) when a payment
    event happens. We verify the signature to make sure the request really
    came from Razorpay, then act on the event.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not settings.RAZORPAY_WEBHOOK_SECRET:
        logger.error("RAZORPAY_WEBHOOK_SECRET is not set; rejecting webhook")
        raise HTTPException(status_code=500, detail="Webhook not configured")

    expected_signature = hmac.new(
        key=settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.warning("Razorpay webhook signature mismatch")
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = json.loads(raw_body)
    event = payload.get("event", "")

    logger.info("Razorpay webhook received", extra={"event": event})

    if event in ("subscription.charged", "payment.captured"):
        await _handle_payment_success(payload, db)
    elif event in ("subscription.cancelled", "subscription.halted", "payment.failed"):
        await _handle_payment_failure(payload, db)
    else:
        logger.info("Unhandled Razorpay webhook event", extra={"event": event})

    # Razorpay expects a 200 response quickly, or it will retry the webhook.
    return {"status": "ok"}


async def _extract_user_id(payload: dict) -> str | None:
    """
    Pulls user_id out of the notes we attached when creating the
    subscription in create_razorpay_checkout(). Checks subscription notes
    first, falls back to payment notes.
    """
    entity = payload.get("payload", {})

    sub_notes = entity.get("subscription", {}).get("entity", {}).get("notes", {})
    if sub_notes.get("user_id"):
        return sub_notes["user_id"]

    payment_notes = entity.get("payment", {}).get("entity", {}).get("notes", {})
    return payment_notes.get("user_id")


async def _handle_payment_success(payload: dict, db: AsyncSession):
    user_id_raw = await _extract_user_id(payload)
    if not user_id_raw:
        logger.warning("Razorpay webhook: no user_id found in payload notes")
        return

    try:
        user_id = uuid.UUID(user_id_raw)
    except ValueError:
        logger.warning(
            "Razorpay webhook: user_id is not a valid UUID",
            extra={"user_id": user_id_raw},
        )
        return

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning("Razorpay webhook: user not found", extra={"user_id": user_id})
        return

    if user.plan != UserPlan.PRO:
        user.plan = UserPlan.PRO
        await db.commit()
        logger.info("User upgraded to Pro via Razorpay webhook", extra={"user_id": user_id})
    else:
        logger.info("User already on Pro plan, skipping upgrade", extra={"user_id": user_id})


async def _handle_payment_failure(payload: dict, db: AsyncSession):
    user_id = await _extract_user_id(payload)
    logger.info(
        "Razorpay payment failed/cancelled",
        extra={"user_id": user_id, "event": payload.get("event")},
    )
    # Optional: downgrade user back to Free plan here if you want that behavior
    # on subscription.cancelled / subscription.halted.