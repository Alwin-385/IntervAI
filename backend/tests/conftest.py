"""Shared pytest fixtures for IntervAI backend tests."""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

# Ensure backend package root is importable in CI and local pytest runs.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Configure test environment BEFORE importing app modules
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/intervai_test"
)
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/15")
os.environ.setdefault("BACKGROUND_JOBS_ENABLED", "false")
os.environ.setdefault("ORCHESTRATION_ENABLED", "false")
os.environ.setdefault("RESUME_ANALYSIS_HEURISTIC_ONLY", "true")
os.environ.setdefault("INTERVIEW_QUESTIONS_HEURISTIC_ONLY", "true")
os.environ.setdefault("ANSWER_EVALUATION_HEURISTIC_ONLY", "true")
os.environ.setdefault("SENTRY_DSN", "")


@pytest.fixture(scope="session")
def settings():
    from app.core.config import get_settings

    return get_settings()


@pytest.fixture
def mock_user():
    from app.models.enums import UserRole
    from app.models.user import User

    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.clerk_user_id = "user_test_123"
    user.clerk_id = "user_test_123"
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.role = UserRole.CANDIDATE
    user.is_active = True
    user.avatar_url = None
    user.hashed_password = ""
    user.created_at = "2026-01-01T00:00:00Z"
    user.updated_at = "2026-01-01T00:00:00Z"
    return user


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token-value"}


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.get = AsyncMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def app(mock_user, mock_db_session):
    """Return configured FastAPI test app with auth and DB mocked out."""
    from app.core.auth.dependencies import get_current_user
    from app.core.database import get_db_session
    from app.main import create_app

    application = create_app()

    async def _fake_auth():
        return mock_user

    async def _fake_db():
        yield mock_db_session

    application.dependency_overrides[get_current_user] = _fake_auth
    application.dependency_overrides[get_db_session] = _fake_db
    return application


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
