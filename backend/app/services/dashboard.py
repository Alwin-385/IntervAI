"""Dashboard aggregates for the current user."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import case, func, select

from app.models.enums import InterviewSessionStatus, ResumeStatus
from app.models.interview_session import InterviewSession
from app.models.resume import Resume
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.resume import ResumeRepository
from app.schemas.dashboard import DashboardActivityItem, DashboardOverview, DashboardStats


class DashboardService:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        session_repo: InterviewSessionRepository,
    ) -> None:
        self.resume_repo = resume_repo
        self.session_repo = session_repo

    async def get_overview(self, user_id: UUID) -> DashboardOverview:
        stats = await self._build_stats(user_id)
        activity = await self._build_activity(user_id)
        return DashboardOverview(stats=stats, recent_activity=activity)

    async def _build_stats(self, user_id: UUID) -> DashboardStats:
        session = self.resume_repo.session

        # Single query for all resume counts using conditional aggregation.
        resume_stmt = select(
            func.count().label("total"),
            func.sum(case((Resume.status == ResumeStatus.COMPLETED, 1), else_=0)).label("analyzed"),
            func.sum(
                case(
                    (Resume.status.in_([ResumeStatus.QUEUED, ResumeStatus.EXTRACTING_RESUME]), 1),
                    else_=0,
                )
            ).label("processing"),
        ).where(Resume.user_id == user_id)

        # Single query for all interview counts using conditional aggregation.
        interview_stmt = select(
            func.count().label("total"),
            func.sum(
                case((InterviewSession.status == InterviewSessionStatus.COMPLETED, 1), else_=0)
            ).label("completed"),
        ).where(InterviewSession.user_id == user_id)

        resume_row = (await session.execute(resume_stmt)).one()
        interview_row = (await session.execute(interview_stmt)).one()

        total = int(resume_row.total or 0)
        analyzed = int(resume_row.analyzed or 0)
        processing = int(resume_row.processing or 0)
        interviews = int(interview_row.total or 0)
        completed_sessions = int(interview_row.completed or 0)

        return DashboardStats(
            mock_interviews=interviews,
            resumes_total=total,
            resumes_analyzed=analyzed,
            resumes_processing=processing,
            average_score=None,
            practice_hours=round(completed_sessions * 0.5, 1),
        )

    async def _build_activity(self, user_id: UUID) -> list[DashboardActivityItem]:
        session = self.resume_repo.session
        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.updated_at.desc())
            .limit(10)
        )
        result = await session.execute(stmt)
        resumes = list(result.scalars().all())

        items: list[DashboardActivityItem] = []
        for resume in resumes:
            if resume.status == ResumeStatus.COMPLETED:
                items.append(
                    DashboardActivityItem(
                        kind="resume_analyzed",
                        title=f"Resume analyzed — {resume.title}",
                        subtitle=resume.file_name,
                        timestamp=resume.updated_at,
                        status=resume.status.value,
                    )
                )
            elif resume.status == ResumeStatus.FAILED:
                items.append(
                    DashboardActivityItem(
                        kind="resume_failed",
                        title=f"Resume extraction failed — {resume.title}",
                        subtitle=resume.extraction_error or resume.file_name,
                        timestamp=resume.updated_at,
                        status=resume.status.value,
                    )
                )
            elif resume.status in (ResumeStatus.QUEUED, ResumeStatus.EXTRACTING_RESUME):
                items.append(
                    DashboardActivityItem(
                        kind="resume_processing",
                        title=f"Resume processing — {resume.title}",
                        subtitle=resume.file_name,
                        timestamp=resume.updated_at,
                        status=resume.status.value,
                    )
                )
            else:
                items.append(
                    DashboardActivityItem(
                        kind="resume_upload",
                        title=f"Resume uploaded — {resume.title}",
                        subtitle=resume.file_name,
                        timestamp=resume.created_at,
                        status=resume.status.value,
                    )
                )

        items.sort(key=lambda item: item.timestamp, reverse=True)
        return items[:8]
