import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import LocationType, JobType, ExtractionStatus, JobStatus


class JobCreate(BaseModel):
    source_url: Optional[str] = None
    raw_description: Optional[str] = None


class JobStatusUpdate(BaseModel):
    status: JobStatus


class JobNotesUpdate(BaseModel):
    notes: str


class JobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

    source_url: Optional[str]
    raw_description: str

    title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    location_type: Optional[LocationType]
    job_type: Optional[JobType]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: str
    experience_min: Optional[int]
    experience_max: Optional[int]
    education: Optional[str]
    required_skills: list
    preferred_skills: list
    extraction_status: ExtractionStatus

    match_score: Optional[int]
    matched_skills: list
    missing_skills: list
    keyword_gaps: list

    status: JobStatus
    notes: str

    created_at: datetime
    updated_at: datetime
    applied_at: Optional[datetime]

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    location_type: Optional[LocationType]
    job_type: Optional[JobType]
    match_score: Optional[int]
    status: JobStatus
    extraction_status: ExtractionStatus
    created_at: datetime
    applied_at: Optional[datetime]

    model_config = {"from_attributes": True}