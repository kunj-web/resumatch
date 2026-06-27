from typing import Optional

from app.models.enums import UserPlan
from app.models.user import User


FREE_TAILOR_RESUME_CREDIT_LIMIT = 10


def get_tailor_resume_credit_limit(user: User) -> Optional[int]:
    if user.plan == UserPlan.PRO:
        return None
    return FREE_TAILOR_RESUME_CREDIT_LIMIT


def get_tailor_resume_credits_remaining(user: User) -> Optional[int]:
    limit = get_tailor_resume_credit_limit(user)
    if limit is None:
        return None
    return max(limit - user.tailor_resume_credits_used, 0)


def can_tailor_resume(user: User) -> bool:
    remaining = get_tailor_resume_credits_remaining(user)
    return remaining is None or remaining > 0


def consume_tailor_resume_credit(user: User) -> None:
    if user.plan == UserPlan.PRO:
        return
    user.tailor_resume_credits_used += 1
