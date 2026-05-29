"""Celery task base with retry + job progress hooks (Phase 18)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from celery import Task

from app.core.logging import get_logger
from app.services.background_job_sync import (
    sync_job_complete,
    sync_job_fail,
    sync_job_mark_retrying,
    sync_job_mark_running,
)

logger = get_logger(__name__)


class JobTask(Task):
    """Base task that updates BackgroundJob rows on lifecycle events."""

    autoretry_for = ()

    def _job_id_from_payload(self, payload: dict[str, Any]) -> UUID | None:
        raw = payload.get("job_id")
        if not raw:
            return None
        return UUID(str(raw))

    def before_start(self, task_id, args, kwargs):
        payload = args[0] if args else kwargs.get("payload") or {}
        job_id = self._job_id_from_payload(payload)
        if job_id:
            sync_job_mark_running(job_id, message="Worker picked up task")

    def on_success(self, retval, task_id, args, kwargs):
        payload = args[0] if args else {}
        job_id = self._job_id_from_payload(payload)
        if job_id and isinstance(retval, dict):
            sync_job_complete(job_id, retval)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        payload = args[0] if args else {}
        job_id = self._job_id_from_payload(payload)
        if job_id:
            sync_job_fail(job_id, str(exc))
        logger.exception("celery_task_failed", task_id=task_id, error=str(exc))

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        payload = args[0] if args else {}
        job_id = self._job_id_from_payload(payload)
        if job_id:
            sync_job_mark_retrying(job_id, message=f"Retrying: {exc}")
