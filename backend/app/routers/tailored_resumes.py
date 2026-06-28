import uuid
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.ratelimit import check_rate_limit
from app.models.job import Job
from app.models.enums import TailoredResumeStatus
from app.models.resume import Resume
from app.models.tailored_resume import TailoredResume
from app.models.user import User
from app.schemas.tailored_resume import (
    TailoredResumeDownloadResponse,
    TailoredResumeFinalizeRequest,
    TailoredResumeResponse,
    TailoredResumeUpdate,
)
from app.services.document_generator import generate_resume_document, get_content_type
from app.services.plans import can_tailor_resume, consume_tailor_resume_credit
from app.services.resume_renderer import render_resume_content
from app.services.resume_templates import (
    is_allowed_output_format,
    is_allowed_template_key,
)
from app.services.supabase_storage import StorageUploadError, get_signed_url, upload_file
from app.services.tailor import tailor_resume_to_job


router = APIRouter(tags=["tailored-resumes"])
logger = logging.getLogger(__name__)


@router.post(
    "/jobs/{job_id}/tailored-resumes",
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

    if not can_tailor_resume(current_user):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="You have used all 10 free tailored resumes. Upgrade to Pro for unlimited tailoring.",
        )

    is_allowed, info = check_rate_limit(current_user.id, "improve_resume")
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. You can make {info['limit']} resume tailoring requests per hour. Try again in {info['retry_after']} seconds.",
        )

    try:
        draft_content = await tailor_resume_to_job(
            resume_text=resume.raw_text,
            job_description=job.raw_description,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            missing_skills=job.missing_skills,
            keyword_gaps=job.keyword_gaps,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate tailored resume draft. Please try again.",
        )

    tailored_resume = TailoredResume(
        user_id=current_user.id,
        job_id=job.id,
        source_resume_id=resume.id,
        draft_content={
            **draft_content,
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
        unsupported_gaps=draft_content.get("unsupported_gaps") or [],
    )

    db.add(tailored_resume)
    consume_tailor_resume_credit(current_user)
    await db.commit()
    await db.refresh(tailored_resume)

    return tailored_resume


@router.get(
    "/tailored-resumes/{tailored_resume_id}",
    response_model=TailoredResumeResponse,
)
async def get_tailored_resume(
    tailored_resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume)
        .where(TailoredResume.id == tailored_resume_id)
        .where(TailoredResume.user_id == current_user.id)
    )
    tailored_resume = result.scalar_one_or_none()

    if not tailored_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found",
        )

    return tailored_resume


@router.patch(
    "/tailored-resumes/{tailored_resume_id}",
    response_model=TailoredResumeResponse,
)
async def update_tailored_resume(
    tailored_resume_id: uuid.UUID,
    payload: TailoredResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume)
        .where(TailoredResume.id == tailored_resume_id)
        .where(TailoredResume.user_id == current_user.id)
    )
    tailored_resume = result.scalar_one_or_none()

    if not tailored_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found",
        )

    if "edited_content" in payload.model_fields_set:
        tailored_resume.edited_content = payload.edited_content

    if payload.template_key is not None:
        if not is_allowed_template_key(payload.template_key):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unsupported resume template",
            )
        tailored_resume.template_key = payload.template_key

    if payload.output_format is not None:
        if not is_allowed_output_format(payload.output_format):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unsupported output format",
            )
        tailored_resume.output_format = payload.output_format

    await db.commit()
    await db.refresh(tailored_resume)

    return tailored_resume


@router.post(
    "/tailored-resumes/{tailored_resume_id}/finalize",
    response_model=TailoredResumeResponse,
)
async def finalize_tailored_resume(
    tailored_resume_id: uuid.UUID,
    payload: TailoredResumeFinalizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume)
        .where(TailoredResume.id == tailored_resume_id)
        .where(TailoredResume.user_id == current_user.id)
    )
    tailored_resume = result.scalar_one_or_none()

    if not tailored_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found",
        )

    template_key = payload.template_key or tailored_resume.template_key
    output_format = payload.output_format or tailored_resume.output_format

    if not is_allowed_template_key(template_key):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported resume template",
        )

    if not is_allowed_output_format(output_format):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported output format",
        )

    content = tailored_resume.edited_content or tailored_resume.draft_content
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No tailored resume content found",
        )

    resume_result = await db.execute(
        select(Resume)
        .where(Resume.id == tailored_resume.source_resume_id)
        .where(Resume.user_id == current_user.id)
    )
    source_resume = resume_result.scalar_one_or_none()

    if not source_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source resume not found",
        )

    rendered_content = render_resume_content(
        content=content,
        template_key=template_key,
        source_resume_text=source_resume.raw_text,
    )

    try:
        file_bytes = generate_resume_document(
            rendered_content,
            template_key,
            output_format,
        )
    except Exception:
        logger.exception("Failed to generate final resume document")
        tailored_resume.status = TailoredResumeStatus.FAILED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate final resume",
        )

    final_file_name = f"tailored-resume-{tailored_resume.id}.{output_format}"
    storage_path = f"tailored-resumes/{current_user.id}/{final_file_name}"

    try:
        final_file_path = await upload_file(
            file_bytes,
            storage_path,
            get_content_type(output_format),
            upsert=True,
        )
    except StorageUploadError as exc:
        logger.exception("Failed to upload final tailored resume")
        tailored_resume.status = TailoredResumeStatus.FAILED
        await db.commit()

        if output_format == "docx" and "invalid_mime_type" in exc.response_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "DOCX uploads are not allowed by the current Supabase bucket "
                    "settings. Choose PDF or allow DOCX MIME type in Supabase Storage."
                ),
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not upload final resume",
        )
    except Exception:
        logger.exception("Failed to upload final tailored resume")
        tailored_resume.status = TailoredResumeStatus.FAILED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not upload final resume",
        )

    tailored_resume.template_key = template_key
    tailored_resume.output_format = output_format
    tailored_resume.rendered_content = rendered_content
    tailored_resume.final_file_name = final_file_name
    tailored_resume.final_file_path = final_file_path
    tailored_resume.file_name = final_file_name
    tailored_resume.file_path = final_file_path
    tailored_resume.status = TailoredResumeStatus.FINALIZED
    tailored_resume.finalized_at = datetime.utcnow()

    await db.commit()
    await db.refresh(tailored_resume)

    return tailored_resume


@router.get(
    "/tailored-resumes/{tailored_resume_id}/download",
    response_model=TailoredResumeDownloadResponse,
)
async def download_tailored_resume(
    tailored_resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume)
        .where(TailoredResume.id == tailored_resume_id)
        .where(TailoredResume.user_id == current_user.id)
    )
    tailored_resume = result.scalar_one_or_none()

    if not tailored_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tailored resume not found",
        )

    if not tailored_resume.final_file_path or not tailored_resume.final_file_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final resume has not been generated yet",
        )

    try:
        signed_url = await get_signed_url(tailored_resume.final_file_path)
    except Exception:
        logger.exception("Failed to create tailored resume download link")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create download link",
        )

    return TailoredResumeDownloadResponse(
        url=signed_url,
        file_name=tailored_resume.final_file_name,
    )
