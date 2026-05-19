"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.endpoints.me import get_current_user_profile
from app.api.v1.router import api_router
from app.core.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import MeResponse
from app.core.config import Settings, get_settings
from app.core.database import db_manager
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import get_logger, setup_logging

settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    db_manager.init(settings)
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    yield
    await db_manager.close()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered interview preparation and evaluation API",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    application.add_exception_handler(AppException, app_exception_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/api/me", response_model=MeResponse, tags=["auth"])
    async def get_me_alias(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> MeResponse:
        """Alias for GET /api/v1/me (spec-compatible path)."""
        return await get_current_user_profile(current_user)

    @application.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "version": __version__,
            "docs": f"{settings.api_v1_prefix}/health",
        }

    return application


app = create_app()
