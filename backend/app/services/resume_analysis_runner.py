"""Start resume analysis in a background thread."""

from __future__ import annotations

import threading
from uuid import UUID

from app.core.logging import get_logger
from app.services.resume_analysis_job import execute_resume_analysis

logger = get_logger(__name__)
_threads: dict[str, threading.Thread] = {}


def _run(analysis_id: UUID) -> None:
    try:
        logger.info("resume_analysis_thread_run", analysis_id=str(analysis_id))
        execute_resume_analysis(analysis_id)
    except Exception as exc:
        logger.exception(
            "resume_analysis_thread_failed",
            analysis_id=str(analysis_id),
            error=str(exc),
        )
    finally:
        _threads.pop(str(analysis_id), None)


def clear_thread(analysis_id: UUID) -> None:
    _threads.pop(str(analysis_id), None)


def start_resume_analysis(analysis_id: UUID) -> None:
    key = str(analysis_id)
    existing = _threads.get(key)
    if existing is not None:
        if existing.is_alive():
            logger.debug("resume_analysis_thread_already_running", analysis_id=key)
            return
        _threads.pop(key, None)

    thread = threading.Thread(
        target=_run,
        args=(analysis_id,),
        name=f"resume-analysis-{key[:8]}",
        daemon=True,
    )
    _threads[key] = thread
    thread.start()
    logger.info("resume_analysis_thread_started", analysis_id=key)
