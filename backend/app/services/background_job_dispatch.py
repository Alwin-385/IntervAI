"""Dispatch background jobs to Celery or daemon threads (Phase 18)."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.background_job import BackgroundJob
from app.models.enums import BackgroundJobType
from app.repositories.background_job import BackgroundJobRepository
from app.services.background_job_service import BackgroundJobService
from app.services.background_job_sync import (
    sync_job_complete,
    sync_job_fail,
    sync_job_mark_running,
    sync_job_set_celery_task_id,
)

logger = get_logger(__name__)

_threads: dict[str, threading.Thread] = {}


def _celery_broker_reachable() -> bool:
    try:
        import redis

        client = redis.from_url(get_settings().celery_broker_url, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False


def _use_celery() -> bool:
    settings = get_settings()
    if not settings.background_jobs_enabled:
        return False
    mode = settings.background_jobs_mode
    if mode == "celery":
        return _celery_broker_reachable()
    if mode == "auto":
        return _celery_broker_reachable()
    return False


_TASK_MAP: dict[BackgroundJobType, str] = {
    BackgroundJobType.RESUME_EXTRACTION: "jobs.resume_extraction",
    BackgroundJobType.RESUME_ANALYSIS: "jobs.resume_analysis",
    BackgroundJobType.QUESTION_GENERATION: "jobs.question_generation",
    BackgroundJobType.TRANSCRIPTION: "jobs.transcription",
    BackgroundJobType.ANSWER_EVALUATION: "jobs.answer_evaluation",
    BackgroundJobType.ROADMAP_GENERATION: "jobs.roadmap_generation",
}


class BackgroundJobDispatcher:
    def __init__(
        self,
        job_service: BackgroundJobService,
        job_repo: BackgroundJobRepository,
    ) -> None:
        self.job_service = job_service
        self.job_repo = job_repo

    async def dispatch(
        self,
        user_id: UUID,
        job_type: BackgroundJobType,
        *,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        payload: dict[str, Any] | None = None,
        thread_runner: Callable[[UUID, dict[str, Any]], dict[str, Any]] | None = None,
    ) -> BackgroundJob:
        job = await self.job_service.create_job(
            user_id,
            job_type,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload,
        )
        job_id = job.id
        payload_with_job = {**(payload or {}), "job_id": str(job_id)}

        if _use_celery():
            task_name = _TASK_MAP.get(job_type)
            if task_name and self._enqueue_celery(task_name, job_id, payload_with_job):
                return await self.job_repo.get_by_id_or_raise(job_id, resource="BackgroundJob")

        if thread_runner is not None:
            self._run_in_thread(job_id, payload_with_job, thread_runner)
            return await self.job_repo.get_by_id_or_raise(job_id, resource="BackgroundJob")

        raise RuntimeError(f"No runner configured for job type {job_type.value}")

    def _enqueue_celery(
        self,
        task_name: str,
        job_id: UUID,
        payload: dict[str, Any],
    ) -> bool:
        try:
            from app.workers.celery_app import celery_app

            task = celery_app.send_task(task_name, args=[payload])
            sync_job_set_celery_task_id(job_id, task.id)
            logger.info(
                "background_job_celery_queued",
                job_id=str(job_id),
                task=task_name,
                celery_task_id=task.id,
            )
            return True
        except Exception as exc:
            logger.warning(
                "background_job_celery_enqueue_failed",
                job_id=str(job_id),
                task=task_name,
                error=str(exc),
            )
            return False

    def _run_in_thread(
        self,
        job_id: UUID,
        payload: dict[str, Any],
        runner: Callable[[UUID, dict[str, Any]], dict[str, Any]],
    ) -> None:
        key = str(job_id)
        existing = _threads.get(key)
        if existing is not None and existing.is_alive():
            return

        def _target() -> None:
            try:
                sync_job_mark_running(job_id, message="Starting…")
                result = runner(job_id, payload)
                sync_job_complete(job_id, result)
            except Exception as exc:
                logger.exception("background_job_thread_failed", job_id=key, error=str(exc))
                sync_job_fail(job_id, str(exc))
            finally:
                _threads.pop(key, None)

        thread = threading.Thread(
            target=_target,
            name=f"bg-job-{key[:8]}",
            daemon=True,
        )
        _threads[key] = thread
        thread.start()
        logger.info("background_job_thread_started", job_id=key)


# Thread runners (import lazily to avoid circular imports)


def run_resume_extraction_job(job_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.resume_extraction_job import execute_resume_extraction

    sync_job_mark_running(job_id, step="extract", message="Extracting PDF text…")
    resume_id = UUID(payload["resume_id"])
    return execute_resume_extraction(resume_id)


def run_resume_analysis_job(job_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.background_job_sync import sync_job_update_progress
    from app.services.resume_analysis_job import execute_resume_analysis

    sync_job_update_progress(job_id, percent=15, step="analysis", message="Analyzing resume…")
    analysis_id = UUID(payload["analysis_id"])
    return execute_resume_analysis(analysis_id)


def run_question_generation_job(job_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.question_generation_job import execute_question_generation_sync

    return execute_question_generation_sync(payload)


def run_transcription_job(job_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.background_job_sync import sync_job_update_progress
    from app.services.speech_transcription_job import execute_transcription_sync

    sync_job_update_progress(job_id, percent=25, step="transcribe", message="Transcribing audio…")
    return execute_transcription_sync(payload)


def run_answer_evaluation_job(job_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.answer_evaluator_job import execute_session_evaluation_sync
    from app.services.background_job_sync import sync_job_update_progress

    sync_job_update_progress(job_id, percent=10, step="evaluate", message="Evaluating answers…")
    return execute_session_evaluation_sync(payload)


def run_roadmap_generation_job(job_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
    from app.services.background_job_sync import sync_job_update_progress
    from app.services.roadmap_generation_job import execute_roadmap_generation_sync

    sync_job_update_progress(job_id, percent=20, step="roadmap", message="Building your roadmap…")
    return execute_roadmap_generation_sync(payload)
