"""Dashboard overview for authenticated users."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import get_dashboard_service
from app.models.user import User
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardOverview:
    """Stats and recent activity derived from the user's resumes and sessions."""
    return await service.get_overview(current_user.id)
