import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.enums import ResumeProcessingStatus
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.services.matcher import match_resume_to_job
from app.services.parser import parse_resume
from app.services.supabase_storage import upload_file, delete_file

router = APIRouter(prefix="/resume", tags=["resume"])

SUPPORTED_RESUME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post(
    "/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    original_file_name = file.filename or ""
    file_type = original_file_name.rsplit(".", 1)[-1].lower()

    # Validate file type
    if file_type not in SUPPORTED_RESUME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are accepted",
        )

    # Read file bytes
    file_bytes = await file.read()

    # Parse text from resume
    try:
        raw_text = parse_resume(file_bytes, file_type)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract text from {file_type.upper()}",
        )

    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume appears to be empty or unreadable",
        )

    # Upload to Supabase Storage
    file_name = f"{uuid.uuid4()}.{file_type}"
    try:
        storage_path = await upload_file(
            file_bytes, file_name, SUPPORTED_RESUME_TYPES[file_type]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File storage failed: {str(e)}",
        )

    # Deactivate all previous resumes for this user
    await db.execute(
        update(Resume).where(Resume.user_id == current_user.id).values(is_active=False)
    )

    # Save new resume to DB — file_path now stores the Supabase storage path
    resume = Resume(
        user_id=current_user.id,
        file_name=original_file_name,
        file_type=file_type,
        file_path=storage_path,
        raw_text=raw_text,
        is_active=True,
        processing_status=ResumeProcessingStatus.PARSED,
    )

    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    await rematch_existing_jobs(db, current_user.id, resume.raw_text)

    return ResumeUploadResponse(
        message="Resume uploaded and parsed successfully", resume=resume
    )


async def rematch_existing_jobs(
    db: AsyncSession,
    user_id: uuid.UUID,
    resume_text: str,
) -> None:
    result = await db.execute(
        select(Job)
        .where(Job.user_id == user_id)
        .where(Job.deleted_at == None)
    )
    jobs = result.scalars().all()

    for job in jobs:
        if not job.required_skills:
            continue

        try:
            match = await match_resume_to_job(
                resume_text=resume_text,
                required_skills=job.required_skills,
                preferred_skills=job.preferred_skills,
            )
        except Exception:
            continue

        job.match_score = match.get("match_score")
        job.matched_skills = match.get("matched_skills") or []
        job.missing_skills = match.get("missing_skills") or []
        job.keyword_gaps = match.get("keyword_gaps") or []

    await db.commit()


@router.get("/me", response_model=ResumeResponse)
async def get_my_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .where(Resume.is_active == True)
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload your resume first.",
        )

    return resume


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .where(Resume.is_active == True)
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active resume found",
        )

    # Delete from Supabase Storage
    try:
        await delete_file(resume.file_path)
    except Exception:
        pass  # Don't block DB delete if storage delete fails

    await db.delete(resume)
    await db.commit()
