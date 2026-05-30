"""Run resume analysis (sync worker — invoked via asyncio.to_thread from API)."""

from __future__ import annotations

from uuid import UUID

from app.agents.resume_analyzer.graph import run_resume_analyzer
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.sync_database import sync_db_session
from app.models.enums import AnalysisStatus, WeakAreaSeverity
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.weak_area import WeakArea
from app.orchestration import AgentName, get_orchestration_service
from app.schemas.resume_analyzer import AnalysisProgress, StructuredResumeAnalysis
from app.services.resume_analysis_progress import persist_analysis_progress
from app.services.resume_text import is_ready_for_analysis, resolve_resume_text

logger = get_logger(__name__)


def execute_resume_analysis(analysis_id: UUID) -> dict[str, str]:
    """Run full analysis pipeline; must complete within this call."""
    logger.info("resume_analysis_execute_start", analysis_id=str(analysis_id))
    try:
        ctx = _read_context(analysis_id)
        if ctx is None:
            return {"status": "not_found"}

        persist_analysis_progress(
            analysis_id,
            AnalysisProgress(step="analysis", percent=45, message="Scoring your resume…"),
        )

        result = _run_resume_analysis(ctx)

        persist_analysis_progress(
            analysis_id,
            AnalysisProgress(step="done", percent=95, message="Saving results…"),
        )

        with sync_db_session() as session:
            analysis = session.get(ResumeAnalysis, analysis_id)
            if analysis is None:
                return {"status": "not_found"}

            analysis.status = AnalysisStatus.COMPLETED
            analysis.overall_score = result.scores.role_readiness_score
            analysis.summary = result.recruiter_feedback[:4000]
            analysis.skills_extracted = result.extracted_skills
            analysis.gaps_identified = {
                "missing_keywords": result.missing_keywords,
                "missing_technologies": result.missing_technologies,
                "weaknesses": result.weaknesses,
            }
            analysis.raw_analysis = result.model_dump()
            session.flush()

            resume = session.get(Resume, analysis.resume_id)
            if resume:
                _sync_weak_areas(session, resume.user_id, analysis.id, result)
            session.flush()

        logger.info("resume_analysis_completed", analysis_id=str(analysis_id))
        return {"status": AnalysisStatus.COMPLETED.value}

    except Exception as exc:
        logger.exception("resume_analysis_failed", analysis_id=str(analysis_id), error=str(exc))
        _mark_failed(analysis_id, str(exc)[:2000])
        return {"status": AnalysisStatus.FAILED.value, "error": str(exc)}


def _read_context(analysis_id: UUID) -> dict | None:
    with sync_db_session() as session:
        analysis = session.get(ResumeAnalysis, analysis_id)
        if analysis is None:
            return None

        resume = session.get(Resume, analysis.resume_id)
        if resume is None:
            return None

        if not is_ready_for_analysis(resume):
            raise ValueError("Resume extraction must be completed before analysis")

        body_text = resolve_resume_text(resume)
        if body_text and not (resume.cleaned_text and resume.cleaned_text.strip()):
            resume.cleaned_text = body_text

        raw = dict(analysis.raw_analysis or {})
        target_role = raw.get("role_target")
        analysis.status = AnalysisStatus.PROCESSING
        session.flush()

        return {
            "resume_id": str(resume.id),
            "analysis_id": str(analysis.id),
            "user_id": str(resume.user_id),
            "target_role": target_role,
            "cleaned_text": body_text,
            "extracted_data": resume.extracted_data or {},
            "chunks": resume.text_chunks or [],
        }


def _sync_weak_areas(
    session, user_id: UUID, analysis_id: UUID, result: StructuredResumeAnalysis
) -> None:
    from sqlalchemy import delete

    session.execute(
        delete(WeakArea).where(WeakArea.resume_analysis_id == analysis_id),
    )
    for idx, weakness in enumerate(result.weaknesses[:8]):
        session.add(
            WeakArea(
                user_id=user_id,
                resume_analysis_id=analysis_id,
                area_name=weakness[:255],
                category="resume_analysis",
                severity=WeakAreaSeverity.HIGH if idx < 2 else WeakAreaSeverity.MEDIUM,
                description=weakness,
            )
        )


def _mark_failed(analysis_id: UUID, message: str) -> None:
    with sync_db_session() as session:
        analysis = session.get(ResumeAnalysis, analysis_id)
        if analysis is None:
            return
        analysis.status = AnalysisStatus.FAILED
        raw = dict(analysis.raw_analysis or {})
        raw["error_message"] = message
        raw["progress"] = AnalysisProgress(
            step="failed",
            percent=0,
            message=message,
        ).model_dump()
        analysis.raw_analysis = raw


def _run_resume_analysis(ctx: dict) -> StructuredResumeAnalysis:
    payload = {
        "resume_id": ctx["resume_id"],
        "analysis_id": ctx["analysis_id"],
        "user_id": ctx["user_id"],
        "target_role": ctx["target_role"],
        "cleaned_text": ctx["cleaned_text"],
        "extracted_data": ctx["extracted_data"],
        "chunks": ctx["chunks"],
    }
    settings = get_settings()
    if settings.orchestration_enabled:
        run = get_orchestration_service().run_agent(
            AgentName.RESUME_ANALYSIS,
            payload,
        )
        if run.status == "completed":
            return StructuredResumeAnalysis.model_validate(
                run.output.get("analysis") or run.output,
            )
    return run_resume_analyzer(**payload)
