"""Interview session CRUD endpoints (authenticated)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import get_interview_session_service, get_pagination
from app.core.exceptions import UnauthorizedError
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.interview_session import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionUpdate,
)
from app.services.interview_session import InterviewSessionService

router = APIRouter(prefix="/interview-sessions", tags=["interview-sessions"])


def _ensure_owner(session: InterviewSession, user: User) -> None:
    if session.user_id != user.id:
        raise UnauthorizedError("You do not have access to this interview session")


@router.post("", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: InterviewSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewSessionResponse:
    return await service.create_session(current_user.id, payload)


@router.get("/me", response_model=PaginatedResponse[InterviewSessionResponse])
async def list_my_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[InterviewSessionResponse]:
    return await service.list_sessions(current_user.id, pagination)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_session(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewSessionResponse:
    entity = await service.repository.get_by_id_or_raise(
        session_id,
        resource="InterviewSession",
    )
    _ensure_owner(entity, current_user)
    return await service.get_session(session_id)


@router.patch("/{session_id}", response_model=InterviewSessionResponse)
async def update_session(
    session_id: UUID,
    payload: InterviewSessionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> InterviewSessionResponse:
    entity = await service.repository.get_by_id_or_raise(
        session_id,
        resource="InterviewSession",
    )
    _ensure_owner(entity, current_user)
    return await service.update_session(session_id, payload)


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> MessageResponse:
    entity = await service.repository.get_by_id_or_raise(
        session_id,
        resource="InterviewSession",
    )
    _ensure_owner(entity, current_user)
    await service.delete_session(session_id)
    return MessageResponse(message="Interview session deleted successfully")
