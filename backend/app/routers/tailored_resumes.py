import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.job import Job
from app.models.resume import Resume
from app.models.tailored_resume import TailoredResume
from app.models.user import User
from app.schemas.tailored_resume import TailoredResumeResponse
from app.services.plans import can_tailor_resume


router = APIRouter(prefix="/jobs", tags=["tailored-resumes"])


@router.post(
    "/{job_id}/tailored-resumes",
    response_model=TailoredResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tailored_resume(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if not job.missing_skills and not job.keyword_gaps:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No missing skills or keyword gaps found for this job",
        )

    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .where(Resume.is_active == True)
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active resume found. Please upload your resume first.",
        )

    if resume.file_type not in ("pdf", "docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upload a PDF or DOCX resume to tailor it",
        )

    if not can_tailor_resume(current_user):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="You have used all 10 free tailored resumes. Upgrade to Pro for unlimited tailoring.",
        )

    existing_result = await db.execute(
        select(TailoredResume)
        .where(TailoredResume.user_id == current_user.id)
        .where(TailoredResume.job_id == job.id)
        .where(TailoredResume.source_resume_id == resume.id)
        .order_by(TailoredResume.created_at.desc())
        .limit(1)
    )
    existing_tailored_resume = existing_result.scalar_one_or_none()

    if existing_tailored_resume:
        return existing_tailored_resume

    tailored_resume = TailoredResume(
        user_id=current_user.id,
        job_id=job.id,
        source_resume_id=resume.id,
        draft_content={
            "version": 1,
            "status": "pending_generation",
            "source_resume": {
                "id": str(resume.id),
                "file_name": resume.file_name,
                "file_type": resume.file_type,
            },
            "job": {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
            },
            "target_gaps": {
                "missing_skills": job.missing_skills,
                "keyword_gaps": job.keyword_gaps,
            },
        },
        unsupported_gaps=[],
    )

    db.add(tailored_resume)
    await db.commit()
    await db.refresh(tailored_resume)

    return tailored_resume
