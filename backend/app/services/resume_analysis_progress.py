"""Persist analysis progress for UI polling."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.core.sync_database import sync_db_session
from app.models.enums import AnalysisStatus
from app.models.resume_analysis import ResumeAnalysis
from app.schemas.resume_analyzer import AnalysisProgress


def persist_analysis_progress(analysis_id: UUID | str, progress: AnalysisProgress) -> None:
    aid = analysis_id if isinstance(analysis_id, UUID) else UUID(str(analysis_id))
    now = datetime.now(UTC)
    with sync_db_session() as session:
        row = session.get(ResumeAnalysis, aid)
        if row is None:
            return
        raw = dict(row.raw_analysis or {})
        raw["progress"] = progress.model_dump()
        raw["progress_at"] = now.isoformat()
        row.raw_analysis = raw
        row.status = AnalysisStatus.PROCESSING
        row.updated_at = now
        session.flush()
