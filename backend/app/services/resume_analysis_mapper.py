"""Map ResumeAnalysis ORM to API detail responses."""

from __future__ import annotations

from app.models.enums import AnalysisStatus
from app.models.resume_analysis import ResumeAnalysis
from app.schemas.resume_analyzer import (
    AnalysisProgress,
    ResumeAnalysisDetailResponse,
    StructuredResumeAnalysis,
)


def to_detail_response(analysis: ResumeAnalysis) -> ResumeAnalysisDetailResponse:
    structured: StructuredResumeAnalysis | None = None
    progress: AnalysisProgress | None = None
    error_message: str | None = None
    raw = analysis.raw_analysis or {}

    if raw.get("progress"):
        try:
            progress = AnalysisProgress.model_validate(raw["progress"])
        except Exception:
            pass

    if analysis.status == AnalysisStatus.FAILED:
        error_message = raw.get("error_message")

    if analysis.status == AnalysisStatus.COMPLETED:
        try:
            structured = StructuredResumeAnalysis.model_validate(raw)
        except Exception:
            pass

    job_id = raw.get("job_id")

    return ResumeAnalysisDetailResponse(
        id=str(analysis.id),
        resume_id=str(analysis.resume_id),
        status=analysis.status.value,
        overall_score=analysis.overall_score,
        summary=analysis.summary,
        created_at=analysis.created_at.isoformat(),
        updated_at=analysis.updated_at.isoformat(),
        progress=progress,
        analysis=structured,
        error_message=error_message,
        job_id=str(job_id) if job_id else None,
    )
