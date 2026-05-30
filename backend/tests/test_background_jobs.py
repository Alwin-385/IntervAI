"""Tests for background job service and dispatch logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _make_job(job_type="resume_extraction", status="pending"):
    from app.models.enums import BackgroundJobStatus, BackgroundJobType

    # Use MagicMock WITHOUT spec so attribute access doesn't return AsyncMock
    job = MagicMock()
    job.id = uuid.uuid4()
    job.user_id = uuid.uuid4()
    job.job_type = BackgroundJobType(job_type)
    job.status = BackgroundJobStatus(status)
    job.progress_percent = 0
    job.progress_step = None
    job.progress_message = None
    job.error_message = None
    job.result = None
    job.retry_count = 0
    job.max_retries = 3
    job.celery_task_id = None
    job.resource_type = "resume"
    job.resource_id = uuid.uuid4()
    job.payload = {}
    job.created_at = datetime.now(UTC)
    job.updated_at = datetime.now(UTC)
    job.started_at = None
    job.completed_at = None
    return job


class TestBackgroundJobService:
    @pytest.fixture
    def repo(self):
        r = AsyncMock()
        r.get_by_id = AsyncMock()
        r.create = AsyncMock()
        r.list_by_user = AsyncMock()
        return r

    @pytest.fixture
    def service(self, repo):
        from app.services.background_job_service import BackgroundJobService

        return BackgroundJobService(repo)

    @pytest.mark.asyncio
    async def test_get_job_returns_job(self, service, repo):
        job = _make_job()
        repo.get_for_user = AsyncMock(return_value=job)
        result = await service.get_job(job.user_id, job.id)
        assert result.id == job.id

    @pytest.mark.asyncio
    async def test_get_job_not_found_raises(self, service, repo):
        from app.core.exceptions import NotFoundError

        repo.get_for_user = AsyncMock(return_value=None)
        with pytest.raises(NotFoundError):
            await service.get_job(uuid.uuid4(), uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_job(self, service, repo):
        from app.models.enums import BackgroundJobType

        job = _make_job()
        repo.create.return_value = job
        result = await service.create_job(
            user_id=job.user_id,
            job_type=BackgroundJobType.RESUME_EXTRACTION,
            resource_type="resume",
            resource_id=job.resource_id,
            payload={},
        )
        assert result.id == job.id
        repo.create.assert_called_once()


class TestJobsApiEndpoint:
    def test_get_job_returns_200(self, client, auth_headers, mock_user):
        from app.services.background_job_service import BackgroundJobService

        job = _make_job()
        job.user_id = mock_user.id
        with patch.object(
            BackgroundJobService, "get_job", new_callable=AsyncMock, return_value=job
        ):
            response = client.get(f"/api/v1/jobs/{job.id}", headers=auth_headers)
        assert response.status_code == 200

    def test_get_job_not_found_returns_404(self, client, auth_headers):
        from app.core.exceptions import NotFoundError
        from app.services.background_job_service import BackgroundJobService

        with patch.object(
            BackgroundJobService,
            "get_job",
            new_callable=AsyncMock,
            side_effect=NotFoundError("Job not found"),
        ):
            response = client.get(f"/api/v1/jobs/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404
