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
    file_name: Optional[str]
    file_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    finalized_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TailoredResumeUpdate(BaseModel):
    edited_content: dict
