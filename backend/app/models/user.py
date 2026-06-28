import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import UserPlan


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    full_name: Mapped[str] = mapped_column(String, nullable=False)

    plan: Mapped[UserPlan] = mapped_column(
        Enum(UserPlan), nullable=False, default=UserPlan.FREE
    )

    tailor_resume_credits_used: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )

    jobs: Mapped[list["Job"]] = relationship(
        "Job", back_populates="user", cascade="all, delete-orphan"
    )

    tailored_resumes: Mapped[list["TailoredResume"]] = relationship(
        "TailoredResume", back_populates="user", cascade="all, delete-orphan"
    )
