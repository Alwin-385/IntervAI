"""Health and readiness endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.core.logging import get_logger
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Liveness probe — confirms the API process is running."""
    logger.info("health_check", environment=settings.environment)
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(UTC),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> ReadinessResponse:
    """Readiness probe — verifies database connectivity."""
    db_status = "unknown"
    try:
        await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.warning("readiness_db_failed", error=str(exc))
        db_status = "disconnected"

    ready = db_status == "connected"
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        database=db_status,
        service=settings.app_name,
        timestamp=datetime.now(UTC),
    )
