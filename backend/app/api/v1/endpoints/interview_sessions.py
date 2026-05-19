"""Interview session CRUD endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_interview_session_service, get_pagination
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.interview_session import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionUpdate,
)
from app.services.interview_session import InterviewSessionService

router = APIRouter(prefix="/interview-sessions", tags=["interview-sessions"])


@router.post("", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: InterviewSessionCreate,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewSessionResponse:
    return await service.create_session(payload)


@router.get("/user/{user_id}", response_model=PaginatedResponse[InterviewSessionResponse])
async def list_user_sessions(
    user_id: UUID,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[InterviewSessionResponse]:
    return await service.list_sessions(user_id, pagination)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_session(
    session_id: UUID,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewSessionResponse:
    return await service.get_session(session_id)


@router.patch("/{session_id}", response_model=InterviewSessionResponse)
async def update_session(
    session_id: UUID,
    payload: InterviewSessionUpdate,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewSessionResponse:
    return await service.update_session(session_id, payload)


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: UUID,
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> MessageResponse:
    await service.delete_session(session_id)
    return MessageResponse(message="Interview session deleted successfully")
