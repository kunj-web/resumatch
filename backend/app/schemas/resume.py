import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import ResumeProcessingStatus


class ResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    raw_text: str
    is_active: bool
    processing_status: ResumeProcessingStatus
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class ResumeUploadResponse(BaseModel):
    message: str
    resume: ResumeResponse
