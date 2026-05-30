"""Analytics endpoints (Phase 14 + Phase 16)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import (
    get_analytics_dashboard_engine_service,
    get_pagination,
    get_weak_area_detection_engine_service,
)
from app.models.user import User
from app.schemas.analytics_dashboard import (
    AnalyticsDashboardResponse,
    AnalyticsProgressResponse,
)
from app.schemas.common import PaginationQuery
from app.schemas.weak_area_analytics import WeakAreasAnalyticsResponse
from app.services.analytics_dashboard_engine import AnalyticsDashboardEngineService
from app.services.weak_area_detection_engine import WeakAreaDetectionEngineService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/weak-areas", response_model=WeakAreasAnalyticsResponse)
async def get_weak_areas_analytics(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        WeakAreaDetectionEngineService, Depends(get_weak_area_detection_engine_service)
    ],
) -> WeakAreasAnalyticsResponse:
    """
    Detect recurring weaknesses from historical answer evaluations and speech analyses.
    Syncs detected areas to the user profile for interview question targeting.
    """
    return await service.get_weak_areas_analytics(current_user.id, sync_to_profile=True)


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        AnalyticsDashboardEngineService, Depends(get_analytics_dashboard_engine_service)
    ],
    pagination: Annotated[PaginationQuery, Depends(get_pagination)],
    target_role: str | None = Query(default=None),
    category: str | None = Query(default=None),
    days: int | None = Query(default=None, ge=7, le=365),
) -> AnalyticsDashboardResponse:
    """Full analytics dashboard: trends, history, weak areas, role readiness."""
    return await service.get_dashboard(
        current_user.id,
        page=pagination.page,
        page_size=min(pagination.page_size, 50),
        target_role=target_role,
        category=category,
        days=days,
    )


@router.get("/progress", response_model=AnalyticsProgressResponse)
async def get_analytics_progress(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[
        AnalyticsDashboardEngineService, Depends(get_analytics_dashboard_engine_service)
    ],
    target_role: str | None = Query(default=None),
    category: str | None = Query(default=None),
    days: int | None = Query(default=None, ge=7, le=365),
) -> AnalyticsProgressResponse:
    """Improvement progress time series and roadmap completion trends."""
    return await service.get_progress(
        current_user.id,
        target_role=target_role,
        category=category,
        days=days,
    )
