import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import TailoredResumeStatus


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[TailoredResumeStatus] = mapped_column(
        Enum(TailoredResumeStatus),
        nullable=False,
        default=TailoredResumeStatus.DRAFT,
    )

    # Structured resume draft used by the review/edit UI.
    draft_content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # User-edited content, stored separately from the AI draft.
    edited_content: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Missing skills/keyword gaps that were not safe to insert.
    unsupported_gaps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    template_key: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ats_classic"
    )
    output_format: Mapped[str] = mapped_column(String(10), nullable=False, default="docx")
    final_file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    final_file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    finalized_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="tailored_resumes")
    job: Mapped["Job"] = relationship("Job", back_populates="tailored_resumes")
    source_resume: Mapped["Resume"] = relationship(
        "Resume", back_populates="tailored_resumes"
    )
