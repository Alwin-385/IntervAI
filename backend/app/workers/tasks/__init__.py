"""Celery task modules (auto-discovered)."""

from app.workers.tasks import jobs, resume_extraction  # noqa: F401
