"""Synchronous job progress updates (Celery workers / threads)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.sync_database import sync_db_session
from app.models.background_job import BackgroundJob
from app.models.enums import BackgroundJobStatus
from app.services.background_job_cache import cache_job_snapshot


def _snapshot(job: BackgroundJob) -> dict[str, Any]:
    return {
        "id": str(job.id),
        "status": job.status.value,
        "job_type": job.job_type.value,
        "progress_percent": job.progress_percent,
        "progress_step": job.progress_step,
        "progress_message": job.progress_message,
        "error_message": job.error_message,
        "result": job.result,
        "retry_count": job.retry_count,
    }


def sync_job_mark_running(
    job_id: UUID | str, *, step: str = "running", message: str | None = None
) -> None:
    jid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    now = datetime.now(UTC)
    with sync_db_session() as session:
        job = session.get(BackgroundJob, jid)
        if job is None:
            return
        job.status = BackgroundJobStatus.RUNNING
        job.started_at = job.started_at or now
        job.progress_step = step
        if message:
            job.progress_message = message
        job.updated_at = now
        session.flush()
        cache_job_snapshot(jid, _snapshot(job))


def sync_job_update_progress(
    job_id: UUID | str,
    *,
    percent: int,
    step: str | None = None,
    message: str | None = None,
) -> None:
    jid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    now = datetime.now(UTC)
    with sync_db_session() as session:
        job = session.get(BackgroundJob, jid)
        if job is None:
            return
        if job.status in (BackgroundJobStatus.COMPLETED, BackgroundJobStatus.FAILED):
            return
        job.status = BackgroundJobStatus.RUNNING
        job.progress_percent = max(0, min(100, percent))
        if step:
            job.progress_step = step
        if message:
            job.progress_message = message
        job.updated_at = now
        session.flush()
        cache_job_snapshot(jid, _snapshot(job))


def sync_job_mark_retrying(job_id: UUID | str, *, message: str | None = None) -> None:
    jid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    now = datetime.now(UTC)
    with sync_db_session() as session:
        job = session.get(BackgroundJob, jid)
        if job is None:
            return
        job.status = BackgroundJobStatus.RETRYING
        job.retry_count = (job.retry_count or 0) + 1
        if message:
            job.progress_message = message
        job.updated_at = now
        session.flush()
        cache_job_snapshot(jid, _snapshot(job))


def sync_job_complete(job_id: UUID | str, result: dict[str, Any] | None = None) -> None:
    jid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    now = datetime.now(UTC)
    with sync_db_session() as session:
        job = session.get(BackgroundJob, jid)
        if job is None:
            return
        job.status = BackgroundJobStatus.COMPLETED
        job.progress_percent = 100
        job.progress_step = "done"
        job.progress_message = job.progress_message or "Completed"
        job.result = result
        job.completed_at = now
        job.updated_at = now
        session.flush()
        cache_job_snapshot(jid, _snapshot(job))


def sync_job_fail(job_id: UUID | str, error: str) -> None:
    jid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    now = datetime.now(UTC)
    with sync_db_session() as session:
        job = session.get(BackgroundJob, jid)
        if job is None:
            return
        job.status = BackgroundJobStatus.FAILED
        job.error_message = error[:4000]
        job.progress_step = "failed"
        job.completed_at = now
        job.updated_at = now
        session.flush()
        cache_job_snapshot(jid, _snapshot(job))


def sync_job_set_celery_task_id(job_id: UUID | str, celery_task_id: str) -> None:
    jid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    with sync_db_session() as session:
        job = session.get(BackgroundJob, jid)
        if job is None:
            return
        job.celery_task_id = celery_task_id
        session.flush()
