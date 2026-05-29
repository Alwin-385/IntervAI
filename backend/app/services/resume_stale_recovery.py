"""Re-process resumes stuck in queued state."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select

from app.core.logging import get_logger
from app.core.sync_database import sync_db_session
from app.models.enums import ResumeStatus
from app.models.resume import Resume
from app.services.resume_extraction_runner import start_resume_extraction

logger = get_logger(__name__)

STALE_AFTER_SECONDS = 5


def recover_stale_queued_resumes(*, max_age_seconds: int = STALE_AFTER_SECONDS) -> int:
    """Kick extraction for resumes left in queued (e.g. after a prior bug)."""
    cutoff = datetime.now(UTC) - timedelta(seconds=max_age_seconds)
    stale_ids: list[UUID] = []

    with sync_db_session() as session:
        stmt = (
            select(Resume.id)
            .where(Resume.status == ResumeStatus.QUEUED)
            .where(Resume.updated_at < cutoff)
        )
        stale_ids = list(session.scalars(stmt).all())

    for resume_id in stale_ids:
        logger.info("resume_extract_stale_recovery", resume_id=str(resume_id))
        start_resume_extraction(resume_id)

    return len(stale_ids)
