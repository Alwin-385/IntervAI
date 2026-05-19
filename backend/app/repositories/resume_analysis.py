"""Resume analysis repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.resume_analysis import ResumeAnalysis
from app.repositories.base import BaseRepository


class ResumeAnalysisRepository(BaseRepository[ResumeAnalysis]):
    model = ResumeAnalysis

    async def list_by_resume(
        self,
        resume_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        stmt = (
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == resume_id)
            .order_by(ResumeAnalysis.created_at.desc())
        )
        return await self.list(page=page, page_size=page_size, stmt=stmt)
