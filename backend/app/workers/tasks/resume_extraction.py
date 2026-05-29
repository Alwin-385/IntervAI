"""Celery task: resume PDF text extraction (legacy name resume.extract)."""

from __future__ import annotations

from typing import Any

from app.workers.base import JobTask
from app.workers.celery_app import celery_app
from app.workers.tasks.jobs import resume_extraction_task


@celery_app.task(
    bind=True,
    base=JobTask,
    name="resume.extract",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="resume",
)
def extract_resume_task(self, resume_id: str, job_id: str | None = None) -> dict[str, str]:
    payload: dict[str, Any] = {"resume_id": resume_id}
    if job_id:
        payload["job_id"] = job_id
    return resume_extraction_task(payload)
