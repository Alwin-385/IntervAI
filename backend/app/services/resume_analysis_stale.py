"""Fail or restart resume analyses that never finish."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from app.core.logging import get_logger
from app.models.enums import AnalysisStatus
from app.models.resume_analysis import ResumeAnalysis
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.schemas.resume_analyzer import AnalysisProgress

logger = get_logger(__name__)

# Only for orphaned rows on a new POST — not used during polling
STALE_SECONDS = 180


async def cancel_active_analyses(
    repo: ResumeAnalysisRepository,
    resume_id: UUID,
) -> int:
    """Fail in-flight analyses so a new run can start immediately."""
    session = repo.session
    stmt = select(ResumeAnalysis).where(
        ResumeAnalysis.resume_id == resume_id,
        ResumeAnalysis.status.in_([AnalysisStatus.PENDING, AnalysisStatus.PROCESSING]),
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    for row in rows:
        raw = dict(row.raw_analysis or {})
        raw["error_message"] = "Cancelled — starting a new analysis run."
        raw["progress"] = AnalysisProgress(
            step="failed",
            percent=0,
            message="Cancelled",
        ).model_dump()
        row.status = AnalysisStatus.FAILED
        row.raw_analysis = raw
    if rows:
        await session.flush()
    return len(rows)


async def recover_stale_for_resume(
    repo: ResumeAnalysisRepository,
    resume_id: UUID,
    *,
    max_age_seconds: int = STALE_SECONDS,
) -> int:
    """Mark very old pending/processing rows as failed (startup cleanup only)."""
    session = repo.session
    stmt = select(ResumeAnalysis).where(
        ResumeAnalysis.resume_id == resume_id,
        ResumeAnalysis.status.in_([AnalysisStatus.PENDING, AnalysisStatus.PROCESSING]),
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    recovered = 0
    now = datetime.now(UTC)
    for row in rows:
        updated = row.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=UTC)
        age = (now - updated).total_seconds()
        if age < max_age_seconds:
            continue
        raw = dict(row.raw_analysis or {})
        raw["error_message"] = (
            "Previous analysis did not finish. Click Analyze resume to try again."
        )
        raw["progress"] = AnalysisProgress(
            step="failed",
            percent=0,
            message="Previous run incomplete",
        ).model_dump()
        row.status = AnalysisStatus.FAILED
        row.raw_analysis = raw
        recovered += 1
        logger.warning(
            "resume_analysis_stale_recovered",
            analysis_id=str(row.id),
            age_seconds=int(age),
        )
    if recovered:
        await session.flush()
    return recovered
