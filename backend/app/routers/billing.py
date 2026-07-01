import logging
from datetime import datetime

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/billing", tags=["billing"])
logger = logging.getLogger(__name__)


@router.post("/upgrade-interest")
async def record_upgrade_interest(current_user: User = Depends(get_current_user)):
    recorded_at = datetime.utcnow()
    logger.info(
        "Upgrade interest recorded",
        extra={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "plan": current_user.plan.value
            if hasattr(current_user.plan, "value")
            else str(current_user.plan),
            "recorded_at": recorded_at.isoformat(),
        },
    )

    return {
        "status": "recorded",
        "message": "You are on the Pro interest list.",
        "recorded_at": recorded_at,
    }
