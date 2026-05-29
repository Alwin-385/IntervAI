"""Run resume PDF extraction and persist results (Celery or in-process)."""

from __future__ import annotations

from uuid import UUID

from app.core.logging import get_logger
from app.core.sync_database import sync_db_session
from app.models.enums import ResumeStatus
from app.models.resume import Resume
from app.services.resume_extraction import ResumeExtractionService
from app.storage.sync_io import read_storage_bytes

logger = get_logger(__name__)


def execute_resume_extraction(resume_id: UUID) -> dict[str, str]:
    """Extract text from stored PDF and update the resume row."""
    extraction = ResumeExtractionService()

    try:
        with sync_db_session() as session:
            resume = session.get(Resume, resume_id)
            if resume is None:
                logger.warning("resume_extract_missing", resume_id=str(resume_id))
                return {"status": "not_found"}

            resume.status = ResumeStatus.EXTRACTING_RESUME
            resume.extraction_error = None
            session.flush()

            pdf_bytes = read_storage_bytes(resume.storage_key)
            result = extraction.extract_from_pdf_bytes(pdf_bytes)

            resume.content_text = result.raw_text
            resume.cleaned_text = result.cleaned_text
            resume.extracted_data = result.extracted_data.model_dump()
            resume.text_chunks = [chunk.model_dump() for chunk in result.chunks]
            resume.status = ResumeStatus.COMPLETED
            resume.extraction_error = None
            session.flush()

        logger.info("resume_extract_completed", resume_id=str(resume_id))
        return {"status": ResumeStatus.COMPLETED.value}

    except Exception as exc:
        logger.exception("resume_extract_failed", resume_id=str(resume_id), error=str(exc))
        _mark_failed(resume_id, str(exc)[:2000])
        return {"status": ResumeStatus.FAILED.value, "error": str(exc)}


def _mark_failed(resume_id: UUID, message: str) -> None:
    with sync_db_session() as session:
        resume = session.get(Resume, resume_id)
        if resume is None:
            return
        resume.status = ResumeStatus.FAILED
        resume.extraction_error = message
