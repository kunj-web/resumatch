import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base
from app.models.enums import LocationType, JobType, ExtractionStatus, JobStatus


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # -------------------------
    # Raw Input
    # -------------------------

    # One of these will always be present
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)

    # -------------------------
    # AI Extracted Fields
    # -------------------------

    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    location_type: Mapped[Optional[LocationType]] = mapped_column(
        Enum(LocationType), nullable=True
    )

    job_type: Mapped[Optional[JobType]] = mapped_column(Enum(JobType), nullable=True)

    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    salary_currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD"
    )

    experience_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    experience_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    education: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Shape: [{"name": "React", "category": "technical"}]
    required_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Shape: [{"name": "Docker", "category": "tool"}]
    preferred_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    extraction_status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus), nullable=False, default=ExtractionStatus.PENDING
    )

    # -------------------------
    # Match Fields
    # Computed when resume is uploaded or job is added
    # -------------------------

    # 0 to 100
    match_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Shape: ["React", "PostgreSQL", "Python"]
    matched_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Shape: [{"name": "Docker", "category": "tool"}]
    missing_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Shape: [{"keyword": "Docker", "category": "tool", "priority": "high", "context": "mentioned 3 times"}]
    keyword_gaps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # -------------------------
    # User Controlled Fields
    # -------------------------

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), nullable=False, default=JobStatus.SAVED
    )

    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # -------------------------
    # Timestamps
    # -------------------------

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Set when user moves status to APPLIED
    applied_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Soft delete — row stays in DB, excluded from all queries
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # -------------------------
    # Relationships
    # -------------------------

    user: Mapped["User"] = relationship("User", back_populates="jobs")

    tailored_resumes: Mapped[list["TailoredResume"]] = relationship(
        "TailoredResume", back_populates="job", cascade="all, delete-orphan"
    )
