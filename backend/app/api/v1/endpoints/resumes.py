"""Resume CRUD endpoints (authenticated)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import get_pagination, get_resume_service
from app.core.exceptions import UnauthorizedError
from app.models.resume import Resume
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.services.resume import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _ensure_owner(resume: Resume, user: User) -> None:
    if resume.user_id != user.id:
        raise UnauthorizedError("You do not have access to this resume")


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    payload: ResumeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    return await service.create_resume(current_user.id, payload)


@router.get("/me", response_model=PaginatedResponse[ResumeResponse])
async def list_my_resumes(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[ResumeResponse]:
    return await service.list_resumes(current_user.id, pagination)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    resume = await service.get_resume(resume_id)
    entity = await service.repository.get_by_id_or_raise(resume_id, resource="Resume")
    _ensure_owner(entity, current_user)
    return resume


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
) -> MessageResponse:
    entity = await service.repository.get_by_id_or_raise(resume_id, resource="Resume")
    _ensure_owner(entity, current_user)
    await service.delete_resume(resume_id)
    return MessageResponse(message="Resume deleted successfully")
