"""Resume CRUD and upload endpoints (authenticated)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.dependencies import (
    get_pagination,
    get_resume_service,
    get_resume_upload_service,
)
from app.core.exceptions import UnauthorizedError, ValidationAppError
from app.models.resume import Resume
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.resume import ResumeResponse, ResumeUpdate, ResumeUploadResponse
from app.services.resume import ResumeService
from app.services.resume_upload import ResumeUploadService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _ensure_owner(resume: Resume, user: User) -> None:
    if resume.user_id != user.id:
        raise UnauthorizedError("You do not have access to this resume")


async def _read_upload_limited(file: UploadFile, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1024 * 64)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValidationAppError(
                f"File exceeds maximum size of {max_bytes / (1024 * 1024):.1f} MB",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    current_user: Annotated[User, Depends(get_current_user)],
    upload_service: Annotated[ResumeUploadService, Depends(get_resume_upload_service)],
    file: UploadFile = File(..., description="PDF resume file"),
    title: str | None = Form(default=None),
    replace_resume_id: UUID | None = Form(default=None),
) -> ResumeUploadResponse:
    """Upload or replace a PDF resume."""
    if not file.filename:
        raise ValidationAppError("File name is required")

    settings = get_settings()
    data = await _read_upload_limited(file, settings.resume_max_size_bytes)

    return await upload_service.upload_pdf(
        current_user.id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        title=title,
        replace_resume_id=replace_resume_id,
    )


@router.get("", response_model=PaginatedResponse[ResumeResponse])
async def list_resumes(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[ResumeResponse]:
    """List all resumes for the authenticated user."""
    return await service.list_resumes(current_user.id, pagination)


@router.get("/me", response_model=PaginatedResponse[ResumeResponse])
async def list_my_resumes(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[ResumeResponse]:
    """Alias for listing the current user's resumes."""
    return await service.list_resumes(current_user.id, pagination)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    entity = await service.repository.get_by_id_or_raise(resume_id, resource="Resume")
    _ensure_owner(entity, current_user)
    return await service.get_resume(resume_id)


@router.patch("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: UUID,
    payload: ResumeUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    entity = await service.repository.get_by_id_or_raise(resume_id, resource="Resume")
    _ensure_owner(entity, current_user)
    return await service.update_resume(resume_id, payload)


@router.delete("/{resume_id}", response_model=MessageResponse)
async def delete_resume(
    resume_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
    upload_service: Annotated[ResumeUploadService, Depends(get_resume_upload_service)],
) -> MessageResponse:
    entity = await service.repository.get_by_id_or_raise(resume_id, resource="Resume")
    _ensure_owner(entity, current_user)
    try:
        await upload_service.storage.delete(entity.storage_key)
    except Exception:
        pass
    await service.delete_resume(resume_id)
    return MessageResponse(message="Resume deleted successfully")
