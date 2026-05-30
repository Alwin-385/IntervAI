"""FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.endpoints import resumes as resumes_endpoints
from app.api.v1.endpoints.me import get_current_user_profile
from app.api.v1.router import api_router
from app.core.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.database import db_manager
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import get_logger, setup_logging
from app.core.security import RateLimitMiddleware, SecureHeadersMiddleware
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.schemas.user import MeResponse

settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)


def _init_sentry() -> None:
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            release=settings.app_version,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            send_default_pii=False,
        )
        logger.info("sentry_initialised", environment=settings.environment)
    except ImportError:
        logger.warning("sentry_sdk_not_installed")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _init_sentry()
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

    # Middleware is applied LIFO — outermost first in request path
    application.add_middleware(SecureHeadersMiddleware)
    if not settings.is_development:
        application.add_middleware(RateLimitMiddleware)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    # Spec-compatible resume API aliases (/api/resumes/*)
    application.add_api_route(
        "/api/resumes/upload",
        resumes_endpoints.upload_resume,
        methods=["POST"],
        response_model=ResumeUploadResponse,
        tags=["resumes"],
    )
    application.add_api_route(
        "/api/resumes",
        resumes_endpoints.list_resumes,
        methods=["GET"],
        response_model=PaginatedResponse[ResumeResponse],
        tags=["resumes"],
    )
    application.add_api_route(
        "/api/resumes/{resume_id}",
        resumes_endpoints.get_resume,
        methods=["GET"],
        response_model=ResumeResponse,
        tags=["resumes"],
    )

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
