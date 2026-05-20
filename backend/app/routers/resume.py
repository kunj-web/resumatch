import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.enums import ResumeProcessingStatus
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.services.parser import parse_resume
from app.services.supabase_storage import upload_file, delete_file

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post(
    "/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted",
        )

    # Read file bytes
    file_bytes = await file.read()

    # Parse text from PDF
    try:
        raw_text = parse_resume(file_bytes)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text from PDF",
        )

    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PDF appears to be empty or scanned — paste your resume as text instead",
        )

    # Upload to Supabase Storage
    file_name = f"{uuid.uuid4()}.pdf"
    try:
        storage_path = await upload_file(file_bytes, file_name)
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
        file_name=file.filename,
        file_path=storage_path,
        raw_text=raw_text,
        is_active=True,
        processing_status=ResumeProcessingStatus.PARSED,
    )

    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return ResumeUploadResponse(
        message="Resume uploaded and parsed successfully", resume=resume
    )


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