import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
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
