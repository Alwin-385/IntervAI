"""Weak area CRUD endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_pagination, get_weak_area_service
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.weak_area import WeakAreaCreate, WeakAreaResponse, WeakAreaUpdate
from app.services.weak_area import WeakAreaService

router = APIRouter(prefix="/weak-areas", tags=["weak-areas"])


@router.post("", response_model=WeakAreaResponse, status_code=status.HTTP_201_CREATED)
async def create_weak_area(
    payload: WeakAreaCreate,
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> WeakAreaResponse:
    return await service.create(payload)


@router.get("/user/{user_id}", response_model=PaginatedResponse[WeakAreaResponse])
async def list_user_weak_areas(
    user_id: UUID,
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[WeakAreaResponse]:
    return await service.list_for_user(user_id, pagination)


@router.get("/{area_id}", response_model=WeakAreaResponse)
async def get_weak_area(
    area_id: UUID,
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> WeakAreaResponse:
    return await service.get(area_id)


@router.patch("/{area_id}", response_model=WeakAreaResponse)
async def update_weak_area(
    area_id: UUID,
    payload: WeakAreaUpdate,
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> WeakAreaResponse:
    return await service.update(area_id, payload)


@router.delete("/{area_id}", response_model=MessageResponse)
async def delete_weak_area(
    area_id: UUID,
    service: Annotated[WeakAreaService, Depends(get_weak_area_service)],
) -> MessageResponse:
    await service.delete(area_id)
    return MessageResponse(message="Weak area deleted successfully")
