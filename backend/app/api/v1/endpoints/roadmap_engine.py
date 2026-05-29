"""Phase 15 — roadmap generation endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.dependencies import get_background_job_dispatcher, get_roadmap_engine_service
from app.models.enums import BackgroundJobType
from app.models.user import User
from app.schemas.roadmap_engine import (
    GeneratedRoadmapResponse,
    GenerateRoadmapRequest,
    RoadmapItemUpdateRequest,
)
from app.services.background_job_dispatch import BackgroundJobDispatcher
from app.services.roadmap_engine import RoadmapEngineService

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post(
    "/generate",
    response_model=GeneratedRoadmapResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_roadmap(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapEngineService, Depends(get_roadmap_engine_service)],
    dispatcher: Annotated[BackgroundJobDispatcher, Depends(get_background_job_dispatcher)],
    body: GenerateRoadmapRequest | None = None,
) -> GeneratedRoadmapResponse:
    """Generate a personalized AI improvement roadmap from interview history."""
    req = body or GenerateRoadmapRequest()
    settings = get_settings()
    if settings.background_jobs_enabled and settings.background_jobs_async_roadmap_generation:
        from datetime import UTC, datetime

        from app.services.background_job_dispatch import run_roadmap_generation_job

        job = await dispatcher.dispatch(
            current_user.id,
            BackgroundJobType.ROADMAP_GENERATION,
            resource_type="roadmap",
            resource_id=current_user.id,
            payload={
                "user_id": str(current_user.id),
                "target_role": req.target_role,
            },
            thread_runner=run_roadmap_generation_job,
        )
        return GeneratedRoadmapResponse(
            id=job.id,
            created_at=job.created_at,
            updated_at=job.updated_at,
            title="Generating roadmap…",
            description=None,
            target_role=req.target_role,
            status="processing",
            phases=[],
            summary="Your personalized roadmap is being generated.",
            total_items=0,
            weak_areas_addressed=[],
            generated_at=datetime.now(UTC),
            job_id=str(job.id),
        )
    return await service.generate_roadmap(current_user.id, req)


@router.get("", response_model=GeneratedRoadmapResponse | None)
async def get_roadmap(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapEngineService, Depends(get_roadmap_engine_service)],
    target_role: str | None = Query(default=None),
) -> GeneratedRoadmapResponse | None:
    """Return the user's latest active roadmap, or null if none exists."""
    return await service.get_latest_roadmap(current_user.id, target_role=target_role)


@router.patch(
    "/{roadmap_id}/items/{item_id}",
    response_model=GeneratedRoadmapResponse,
)
async def update_roadmap_item(
    roadmap_id: UUID,
    item_id: str,
    body: RoadmapItemUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[RoadmapEngineService, Depends(get_roadmap_engine_service)],
) -> GeneratedRoadmapResponse:
    """Mark a roadmap task as completed or incomplete."""
    return await service.update_item_completion(
        current_user.id, roadmap_id, item_id, body.completed
    )
