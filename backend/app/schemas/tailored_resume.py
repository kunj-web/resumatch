import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums import TailoredResumeStatus


class TailoredResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    source_resume_id: uuid.UUID
    status: TailoredResumeStatus
    draft_content: dict
    edited_content: Optional[dict]
    unsupported_gaps: list
    template_key: str
    output_format: str
    final_file_name: Optional[str]
    final_file_path: Optional[str]
    file_name: Optional[str]
    file_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    finalized_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TailoredResumeUpdate(BaseModel):
    edited_content: Optional[dict] = None
    template_key: Optional[str] = None
    output_format: Optional[str] = None


class TailoredResumeFinalizeRequest(BaseModel):
    template_key: Optional[str] = None
    output_format: Optional[str] = None


class TailoredResumeDownloadResponse(BaseModel):
    url: str
    file_name: str
