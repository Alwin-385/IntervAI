"""Roadmap CRUD endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_pagination, get_roadmap_service
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationQuery
from app.schemas.roadmap import RoadmapCreate, RoadmapResponse, RoadmapUpdate
from app.services.roadmap import RoadmapService

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


@router.post("", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    payload: RoadmapCreate,
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> RoadmapResponse:
    return await service.create(payload)


@router.get("/user/{user_id}", response_model=PaginatedResponse[RoadmapResponse])
async def list_user_roadmaps(
    user_id: UUID,
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
) -> PaginatedResponse[RoadmapResponse]:
    return await service.list_for_user(user_id, pagination)


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap(
    roadmap_id: UUID,
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> RoadmapResponse:
    return await service.get(roadmap_id)


@router.patch("/{roadmap_id}", response_model=RoadmapResponse)
async def update_roadmap(
    roadmap_id: UUID,
    payload: RoadmapUpdate,
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> RoadmapResponse:
    return await service.update(roadmap_id, payload)


@router.delete("/{roadmap_id}", response_model=MessageResponse)
async def delete_roadmap(
    roadmap_id: UUID,
    service: Annotated[RoadmapService, Depends(get_roadmap_service)],
) -> MessageResponse:
    await service.delete(roadmap_id)
    return MessageResponse(message="Roadmap deleted successfully")
