"""Background job polling API (Phase 18)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import get_background_job_service
from app.models.user import User
from app.schemas.background_job import BackgroundJobListResponse, BackgroundJobResponse
from app.services.background_job_service import BackgroundJobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=BackgroundJobResponse)
async def get_job_status(
    job_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BackgroundJobService, Depends(get_background_job_service)],
) -> BackgroundJobResponse:
    """Poll background job progress and result."""
    return await service.get_job(job_id, current_user.id)


@router.get("", response_model=BackgroundJobListResponse)
async def list_jobs_for_resource(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BackgroundJobService, Depends(get_background_job_service)],
    resource_type: str = Query(..., min_length=1, max_length=64),
    resource_id: UUID = Query(...),
) -> BackgroundJobListResponse:
    """List recent jobs for a resource (e.g. interview_session, resume)."""
    return await service.list_by_resource(
        current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
