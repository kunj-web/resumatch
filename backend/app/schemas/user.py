import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator

from app.models.enums import UserPlan


FREE_TAILOR_RESUME_CREDIT_LIMIT = 10


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        # Check for common TLDs, reject single-letter TLDs
        email_lower = v.lower()
        if not any(
            email_lower.endswith(tld)
            for tld in [
                ".com",
                ".org",
                ".net",
                ".edu",
                ".co",
                ".io",
                ".dev",
                ".app",
                ".uk",
                ".in",
                ".de",
                ".fr",
            ]
        ):
            raise ValueError("Email must have a valid domain (e.g., .com, .org, .io)")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    plan: UserPlan
    tailor_resume_credits_used: int
    created_at: datetime

    @computed_field
    @property
    def tailor_resume_credit_limit(self) -> Optional[int]:
        if self.plan == UserPlan.PRO:
            return None
        return FREE_TAILOR_RESUME_CREDIT_LIMIT

    @computed_field
    @property
    def tailor_resume_credits_remaining(self) -> Optional[int]:
        if self.plan == UserPlan.PRO:
            return None
        return max(
            FREE_TAILOR_RESUME_CREDIT_LIMIT - self.tailor_resume_credits_used,
            0,
        )

    model_config = {"from_attributes": True}
