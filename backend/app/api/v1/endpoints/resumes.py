"""Resume CRUD endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_pagination, get_resume_service
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.services.resume import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    payload: ResumeCreate,
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    return await service.create_resume(payload)


@router.get("/user/{user_id}", response_model=PaginatedResponse[ResumeResponse])
async def list_user_resumes(
    user_id: UUID,
    service: Annotated[ResumeService, Depends(get_resume_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[ResumeResponse]:
    return await service.list_resumes(user_id, pagination)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    return await service.get_resume(resume_id)


@router.patch("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: UUID,
    payload: ResumeUpdate,
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    return await service.update_resume(resume_id, payload)


@router.delete("/{resume_id}", response_model=MessageResponse)
async def delete_resume(
    resume_id: UUID,
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> MessageResponse:
    await service.delete_resume(resume_id)
    return MessageResponse(message="Resume deleted successfully")
