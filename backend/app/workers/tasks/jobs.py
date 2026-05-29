"""Unified Celery tasks for Phase 18 background jobs."""

from __future__ import annotations

from typing import Any

from app.services.background_job_dispatch import (
    run_answer_evaluation_job,
    run_question_generation_job,
    run_resume_analysis_job,
    run_resume_extraction_job,
    run_roadmap_generation_job,
    run_transcription_job,
)
from app.workers.base import JobTask
from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    base=JobTask,
    name="jobs.resume_extraction",
    max_retries=3,
    acks_late=True,
    queue="resume",
)
def resume_extraction_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from uuid import UUID

    return run_resume_extraction_job(UUID(payload["job_id"]), payload)


@celery_app.task(
    bind=True,
    base=JobTask,
    name="jobs.resume_analysis",
    max_retries=3,
    acks_late=True,
    queue="resume",
)
def resume_analysis_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from uuid import UUID

    return run_resume_analysis_job(UUID(payload["job_id"]), payload)


@celery_app.task(
    bind=True,
    base=JobTask,
    name="jobs.question_generation",
    max_retries=2,
    acks_late=True,
    queue="interview",
    soft_time_limit=120,
    time_limit=150,
)
def question_generation_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from uuid import UUID

    return run_question_generation_job(UUID(payload["job_id"]), payload)


@celery_app.task(
    bind=True,
    base=JobTask,
    name="jobs.transcription",
    max_retries=2,
    acks_late=True,
    queue="interview",
    soft_time_limit=90,
    time_limit=120,
)
def transcription_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from uuid import UUID

    return run_transcription_job(UUID(payload["job_id"]), payload)


@celery_app.task(
    bind=True,
    base=JobTask,
    name="jobs.answer_evaluation",
    max_retries=2,
    acks_late=True,
    queue="ai",
    soft_time_limit=180,
    time_limit=240,
)
def answer_evaluation_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from uuid import UUID

    return run_answer_evaluation_job(UUID(payload["job_id"]), payload)


@celery_app.task(
    bind=True,
    base=JobTask,
    name="jobs.roadmap_generation",
    max_retries=2,
    acks_late=True,
    queue="ai",
    soft_time_limit=120,
    time_limit=150,
)
def roadmap_generation_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    from uuid import UUID

    return run_roadmap_generation_job(UUID(payload["job_id"]), payload)
