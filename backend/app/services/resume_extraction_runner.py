"""Kick off resume PDF extraction via background jobs (Phase 18)."""

from __future__ import annotations

import asyncio
import threading
from uuid import UUID

from app.core.config import get_settings
from app.core.database import db_manager
from app.core.logging import get_logger
from app.models.enums import BackgroundJobType
from app.repositories.background_job import BackgroundJobRepository
from app.services.background_job_dispatch import BackgroundJobDispatcher, run_resume_extraction_job
from app.services.background_job_service import BackgroundJobService
from app.services.resume_extraction_job import execute_resume_extraction

logger = get_logger(__name__)


async def start_resume_extraction_async(user_id: UUID, resume_id: UUID) -> UUID | None:
    """Queue extraction; returns job id when tracked."""
    settings = get_settings()
    if not settings.background_jobs_enabled:
        _start_legacy_thread(resume_id)
        return None

    async with db_manager.session_factory() as session:
        job_repo = BackgroundJobRepository(session)
        dispatcher = BackgroundJobDispatcher(BackgroundJobService(job_repo), job_repo)
        job = await dispatcher.dispatch(
            user_id,
            BackgroundJobType.RESUME_EXTRACTION,
            resource_type="resume",
            resource_id=resume_id,
            payload={"resume_id": str(resume_id)},
            thread_runner=run_resume_extraction_job,
        )
        await session.commit()
        return job.id


def start_resume_extraction(resume_id: UUID, user_id: UUID | None = None) -> None:
    """Run extraction in background (Celery when available, else daemon thread)."""
    if user_id is not None and get_settings().background_jobs_enabled:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(start_resume_extraction_async(user_id, resume_id))
            return
        except RuntimeError:
            asyncio.run(start_resume_extraction_async(user_id, resume_id))
            return
    _start_legacy_thread(resume_id)


def _start_legacy_thread(resume_id: UUID) -> None:
    def _run() -> None:
        try:
            execute_resume_extraction(resume_id)
        except Exception as exc:
            logger.exception(
                "resume_extract_thread_failed", resume_id=str(resume_id), error=str(exc)
            )

    threading.Thread(
        target=_run,
        name=f"resume-extract-{str(resume_id)[:8]}",
        daemon=True,
    ).start()
