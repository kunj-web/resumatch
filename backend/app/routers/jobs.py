import uuid
import httpx
from bs4 import BeautifulSoup

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.ratelimit import check_rate_limit
from fastapi import HTTPException, status
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.enums import ExtractionStatus, JobStatus
from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobListResponse,
    JobStatusUpdate,
    JobNotesUpdate,
)
from app.services.groq import extract_job_details
from app.services.matcher import match_resume_to_job
from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobListResponse,
    JobStatusUpdate,
    JobNotesUpdate,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


async def fetch_url_content(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        return soup.get_text(separator="\n", strip=True)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # Rate limit check
    is_allowed, info = check_rate_limit(current_user.id, "extract_job")
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. You can make {info['limit']} extractions per hour. Try again in {info['retry_after']} seconds.",
        )
    # Must have either URL or raw description
    if not payload.source_url and not payload.raw_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either a job URL or paste the job description",
        )

    raw_description = payload.raw_description

    # If URL provided, fetch and parse it
    if payload.source_url:
        try:
            raw_description = await fetch_url_content(payload.source_url)
        except Exception:
            if not payload.raw_description:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not fetch the URL. Please paste the job description manually.",
                )
            raw_description = payload.raw_description

    # Create job with pending status
    job = Job(
        user_id=current_user.id,
        source_url=payload.source_url,
        raw_description=raw_description,
        extraction_status=ExtractionStatus.PENDING,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Extract job details with AI
    # Extract job details with AI
    try:
        extracted = await extract_job_details(raw_description)

        job.title = extracted.get("title")
        job.company = extracted.get("company")
        job.location = extracted.get("location")
        job.location_type = extracted.get("location_type")
        job.job_type = extracted.get("job_type")
        job.salary_min = extracted.get("salary_min")
        job.salary_max = extracted.get("salary_max")
        job.salary_currency = extracted.get("salary_currency") or "USD"
        job.experience_min = extracted.get("experience_min")
        job.experience_max = extracted.get("experience_max")
        job.education = extracted.get("education")
        job.required_skills = extracted.get("required_skills") or []
        job.preferred_skills = extracted.get("preferred_skills") or []
        job.extraction_status = ExtractionStatus.SUCCESS

    except Exception as e:
        print("EXTRACTION ERROR:", type(e).__name__, str(e))
        job.extraction_status = ExtractionStatus.FAILED
        await db.commit()
        await db.refresh(job)
        return job

    # Match against active resume if exists
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .where(Resume.is_active == True)
    )
    resume = result.scalar_one_or_none()

    if resume and job.required_skills:
        try:
            match = await match_resume_to_job(
                resume_text=resume.raw_text,
                required_skills=job.required_skills,
                preferred_skills=job.preferred_skills,
            )

            job.match_score = match.get("match_score")
            job.matched_skills = match.get("matched_skills") or []
            job.missing_skills = match.get("missing_skills") or []
            job.keyword_gaps = match.get("keyword_gaps") or []

        except Exception:
            pass

    await db.commit()
    await db.refresh(job)
    return job


@router.get("/", response_model=list[JobListResponse])
async def get_jobs(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Job)
        .where(Job.user_id == current_user.id)
        .where(Job.deleted_at == None)
        .order_by(Job.created_at.desc())
    )
    jobs = result.scalars().all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.user_id == current_user.id)
        .where(Job.deleted_at == None)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    return job


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    job_id: uuid.UUID,
    payload: JobStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.user_id == current_user.id)
        .where(Job.deleted_at == None)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    job.status = payload.status

    # Auto set applied_at when status moves to applied
    if payload.status == JobStatus.APPLIED and not job.applied_at:
        from datetime import datetime, timezone

        job.applied_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()
    await db.refresh(job)
    return job


@router.patch("/{job_id}/notes", response_model=JobResponse)
async def update_job_notes(
    job_id: uuid.UUID,
    payload: JobNotesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.user_id == current_user.id)
        .where(Job.deleted_at == None)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    job.notes = payload.notes
    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id)
        .where(Job.user_id == current_user.id)
        .where(Job.deleted_at == None)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    from datetime import datetime, timezone

    job.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
