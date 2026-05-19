"""Weak area CRUD endpoints (authenticated)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import get_pagination, get_weak_area_service
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.models.weak_area import WeakArea
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.weak_area import WeakAreaCreate, WeakAreaResponse, WeakAreaUpdate
from app.services.weak_area import WeakAreaService

router = APIRouter(prefix="/weak-areas", tags=["weak-areas"])


def _ensure_owner(area: WeakArea, user: User) -> None:
    if area.user_id != user.id:
        raise UnauthorizedError("You do not have access to this weak area")


@router.post("", response_model=WeakAreaResponse, status_code=status.HTTP_201_CREATED)
async def create_weak_area(
    payload: WeakAreaCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> WeakAreaResponse:
    return await service.create(current_user.id, payload)


@router.get("/me", response_model=PaginatedResponse[WeakAreaResponse])
async def list_my_weak_areas(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[WeakAreaResponse]:
    return await service.list_for_user(current_user.id, pagination)


@router.get("/{area_id}", response_model=WeakAreaResponse)
async def get_weak_area(
    area_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> WeakAreaResponse:
    entity = await service.repository.get_by_id_or_raise(area_id, resource="WeakArea")
    _ensure_owner(entity, current_user)
    return await service.get(area_id)


@router.patch("/{area_id}", response_model=WeakAreaResponse)
async def update_weak_area(
    area_id: UUID,
    payload: WeakAreaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> WeakAreaResponse:
    entity = await service.repository.get_by_id_or_raise(area_id, resource="WeakArea")
    _ensure_owner(entity, current_user)
    return await service.update(area_id, payload)


@router.delete("/{area_id}", response_model=MessageResponse)
async def delete_weak_area(
    area_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> MessageResponse:
    entity = await service.repository.get_by_id_or_raise(area_id, resource="WeakArea")
    _ensure_owner(entity, current_user)
    await service.delete(area_id)
    return MessageResponse(message="Weak area deleted successfully")
