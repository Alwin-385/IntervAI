"""Optional Celery queue for resume extraction."""

from __future__ import annotations

from uuid import UUID

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _celery_broker_reachable() -> bool:
    try:
        import redis

        settings = get_settings()
        client = redis.from_url(settings.celery_broker_url, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False


def try_enqueue_celery_extraction(resume_id: UUID) -> bool:
    """Return True if a Celery task was queued."""
    if not _celery_broker_reachable():
        return False
    try:
        from app.workers.tasks.resume_extraction import extract_resume_task

        async_result = extract_resume_task.delay(str(resume_id))
        logger.info(
            "resume_extract_celery_queued",
            resume_id=str(resume_id),
            task_id=async_result.id,
        )
        return True
    except Exception as exc:
        logger.warning(
            "resume_extract_celery_enqueue_failed",
            resume_id=str(resume_id),
            error=str(exc),
        )
        return False
