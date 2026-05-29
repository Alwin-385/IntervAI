"""Background job lifecycle (async API layer)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.models.background_job import BackgroundJob
from app.models.enums import BackgroundJobStatus, BackgroundJobType
from app.repositories.background_job import BackgroundJobRepository
from app.schemas.background_job import BackgroundJobListResponse, BackgroundJobResponse
from app.services.background_job_cache import cache_job_snapshot, get_cached_job


_TERMINAL = frozenset({
    BackgroundJobStatus.COMPLETED,
    BackgroundJobStatus.FAILED,
    BackgroundJobStatus.CANCELLED,
})


class BackgroundJobService:
    def __init__(self, repository: BackgroundJobRepository) -> None:
        self.repository = repository

    @staticmethod
    def _to_response(job: BackgroundJob) -> BackgroundJobResponse:
        return BackgroundJobResponse(
            id=job.id,
            created_at=job.created_at,
            updated_at=job.updated_at,
            user_id=job.user_id,
            job_type=job.job_type,
            status=job.status,
            celery_task_id=job.celery_task_id,
            resource_type=job.resource_type,
            resource_id=job.resource_id,
            progress_percent=job.progress_percent,
            progress_step=job.progress_step,
            progress_message=job.progress_message,
            result=job.result,
            error_message=job.error_message,
            retry_count=job.retry_count,
            max_retries=job.max_retries,
            started_at=job.started_at,
            completed_at=job.completed_at,
            is_terminal=job.status in _TERMINAL,
        )

    async def create_job(
        self,
        user_id: UUID,
        job_type: BackgroundJobType,
        *,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        payload: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> BackgroundJob:
        job = await self.repository.create(
            {
                "user_id": user_id,
                "job_type": job_type,
                "status": BackgroundJobStatus.PENDING,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "payload": payload,
                "max_retries": max_retries,
                "progress_percent": 0,
                "progress_message": "Queued",
                "progress_step": "queued",
            },
        )
        cache_job_snapshot(
            job.id,
            {
                "id": str(job.id),
                "status": job.status.value,
                "job_type": job.job_type.value,
                "progress_percent": 0,
                "progress_step": "queued",
                "progress_message": "Queued",
            },
        )
        return job

    async def get_job(self, user_id: UUID, job_id: UUID) -> BackgroundJobResponse:
        cached = get_cached_job(job_id)
        job = await self.repository.get_for_user(job_id, user_id)
        if job is None:
            raise NotFoundError("BackgroundJob", str(job_id))
        resp = self._to_response(job)
        if cached and not resp.is_terminal:
            resp.progress_percent = int(cached.get("progress_percent", resp.progress_percent))
            if cached.get("progress_message"):
                resp.progress_message = cached["progress_message"]
            if cached.get("progress_step"):
                resp.progress_step = cached["progress_step"]
        return resp

    async def list_by_resource(
        self,
        user_id: UUID,
        *,
        resource_type: str,
        resource_id: UUID,
    ) -> BackgroundJobListResponse:
        jobs = await self.repository.list_by_resource(
            user_id,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        items = [self._to_response(j) for j in jobs]
        return BackgroundJobListResponse(items=items, total=len(items))

    async def update_job(
        self,
        job: BackgroundJob,
        data: dict[str, Any],
    ) -> BackgroundJob:
        updated = await self.repository.update(job, data)
        cache_job_snapshot(updated.id, {
            "id": str(updated.id),
            "status": updated.status.value,
            "job_type": updated.job_type.value,
            "progress_percent": updated.progress_percent,
            "progress_step": updated.progress_step,
            "progress_message": updated.progress_message,
            "error_message": updated.error_message,
            "result": updated.result,
        })
        return updated
