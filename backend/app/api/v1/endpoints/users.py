"""User CRUD endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_pagination, get_user_service
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.create_user(payload)


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
    active_only: bool = Query(default=True),
) -> PaginatedResponse[UserResponse]:
    return await service.list_users(pagination, active_only=active_only)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.update_user(user_id, payload)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> MessageResponse:
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")
