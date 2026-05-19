"""Roadmap CRUD endpoints (authenticated)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import get_pagination, get_roadmap_service
from app.core.exceptions import UnauthorizedError
from app.models.roadmap import Roadmap
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.roadmap import RoadmapCreate, RoadmapResponse, RoadmapUpdate
from app.services.roadmap import RoadmapService

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


def _ensure_owner(roadmap: Roadmap, user: User) -> None:
    if roadmap.user_id != user.id:
        raise UnauthorizedError("You do not have access to this roadmap")


@router.post("", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    payload: RoadmapCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> RoadmapResponse:
    return await service.create(current_user.id, payload)


@router.get("/me", response_model=PaginatedResponse[RoadmapResponse])
async def list_my_roadmaps(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[RoadmapResponse]:
    return await service.list_for_user(current_user.id, pagination)


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> RoadmapResponse:
    entity = await service.repository.get_by_id_or_raise(roadmap_id, resource="Roadmap")
    _ensure_owner(entity, current_user)
    return await service.get(roadmap_id)


@router.patch("/{roadmap_id}", response_model=RoadmapResponse)
async def update_roadmap(
    roadmap_id: UUID,
    payload: RoadmapUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> RoadmapResponse:
    entity = await service.repository.get_by_id_or_raise(roadmap_id, resource="Roadmap")
    _ensure_owner(entity, current_user)
    return await service.update(roadmap_id, payload)


@router.delete("/{roadmap_id}", response_model=MessageResponse)
async def delete_roadmap(
    roadmap_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> MessageResponse:
    entity = await service.repository.get_by_id_or_raise(roadmap_id, resource="Roadmap")
    _ensure_owner(entity, current_user)
    await service.delete(roadmap_id)
    return MessageResponse(message="Roadmap deleted successfully")
