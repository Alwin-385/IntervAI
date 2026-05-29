"""Start and fetch AI resume analyses."""

from __future__ import annotations

from uuid import UUID

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.enums import AnalysisStatus, BackgroundJobType
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.schemas.resume_analyzer import AnalysisProgress, ResumeAnalyzeRequest, ResumeAnalysisDetailResponse
from app.repositories.background_job import BackgroundJobRepository
from app.services.background_job_dispatch import BackgroundJobDispatcher, run_resume_analysis_job
from app.services.background_job_service import BackgroundJobService
from app.services.resume_analysis_job import execute_resume_analysis
from app.services.resume_analysis_mapper import to_detail_response
from app.services.resume_analysis_stale import cancel_active_analyses, recover_stale_for_resume
from app.services.resume_text import (
    is_ready_for_analysis,
    normalize_resume_status,
    resolve_resume_text,
)


class ResumeAnalysisOrchestrator:
    def __init__(
        self,
        analysis_repo: ResumeAnalysisRepository,
        resume_repo: ResumeRepository,
    ) -> None:
        self.analysis_repo = analysis_repo
        self.resume_repo = resume_repo

    async def get_latest(self, resume_id: UUID, user_id: UUID) -> ResumeAnalysisDetailResponse:
        resume = await self._get_owned_resume(resume_id, user_id)
        analysis = await self.analysis_repo.get_latest_by_resume(resume.id)
        if analysis is None:
            raise NotFoundError("ResumeAnalysis", str(resume_id))
        return to_detail_response(analysis)

    async def start_analysis(
        self,
        resume_id: UUID,
        user_id: UUID,
        payload: ResumeAnalyzeRequest,
    ) -> ResumeAnalysisDetailResponse:
        resume = await self._get_owned_resume(resume_id, user_id)
        if normalize_resume_status(resume.status).value != "completed":
            raise ValidationAppError(
                "Resume must finish text extraction before AI analysis. Wait for Ready status.",
            )
        if not is_ready_for_analysis(resume):
            raise ValidationAppError(
                "No extracted resume text available for analysis. "
                "Open Resumes and use Re-extract on this PDF, then try again.",
            )
        text = resolve_resume_text(resume)
        if text and not (resume.cleaned_text and resume.cleaned_text.strip()):
            await self.resume_repo.update(resume, {"cleaned_text": text})

        await recover_stale_for_resume(self.analysis_repo, resume.id)
        await cancel_active_analyses(self.analysis_repo, resume.id)

        raw: dict = {}
        if payload.target_role:
            raw["role_target"] = payload.target_role.strip()
        raw["progress"] = AnalysisProgress(
            step="starting",
            percent=20,
            message="Starting analysis…",
        ).model_dump()

        analysis = await self.analysis_repo.create(
            {
                "resume_id": resume.id,
                "status": AnalysisStatus.PROCESSING,
                "raw_analysis": raw,
            },
        )
        analysis_id = analysis.id

        await self.analysis_repo.session.commit()

        settings = get_settings()
        if settings.background_jobs_enabled and settings.background_jobs_async_resume_analysis:
            job_repo = BackgroundJobRepository(self.analysis_repo.session)
            dispatcher = BackgroundJobDispatcher(BackgroundJobService(job_repo), job_repo)
            job = await dispatcher.dispatch(
                user_id,
                BackgroundJobType.RESUME_ANALYSIS,
                resource_type="resume_analysis",
                resource_id=analysis_id,
                payload={"analysis_id": str(analysis_id)},
                thread_runner=run_resume_analysis_job,
            )
            raw["job_id"] = str(job.id)
            analysis = await self.analysis_repo.update(analysis, {"raw_analysis": raw})
            await self.analysis_repo.session.commit()
            resp = to_detail_response(analysis)
            return resp.model_copy(update={"job_id": str(job.id)})

        import asyncio

        await asyncio.to_thread(execute_resume_analysis, analysis_id)
        from app.models.resume_analysis import ResumeAnalysis

        refreshed = await self.analysis_repo.session.get(ResumeAnalysis, analysis_id)
        if refreshed is None:
            raise NotFoundError("ResumeAnalysis", str(analysis_id))
        await self.analysis_repo.session.refresh(refreshed)
        return to_detail_response(refreshed)

    async def _get_owned_resume(self, resume_id: UUID, user_id: UUID) -> Resume:
        resume = await self.resume_repo.get_by_id_or_raise(resume_id, resource="Resume")
        if resume.user_id != user_id:
            raise NotFoundError("Resume", str(resume_id))
        return resume
