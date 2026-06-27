import uuid
from datetime import datetime

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ResumeProcessingStatus


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String, nullable=False)

    # pdf or docx. DOCX is preferred for format-preserving tailoring.
    file_type: Mapped[str] = mapped_column(String(10), nullable=False, default="pdf")

    # Local filesystem path e.g. /uploads/resumes/<uuid>.pdf
    file_path: Mapped[str] = mapped_column(String, nullable=False)

    # Plain text extracted by pdfplumber on upload
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    # True = currently active resume used for matching
    # False = old resume, replaced by a newer upload
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    processing_status: Mapped[ResumeProcessingStatus] = mapped_column(
        Enum(ResumeProcessingStatus),
        nullable=False,
        default=ResumeProcessingStatus.UPLOADED,
    )

    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
