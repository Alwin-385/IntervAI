"""Interview session repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.enums import InterviewSessionStatus
from app.models.interview_session import InterviewSession
from app.repositories.base import BaseRepository


class InterviewSessionRepository(BaseRepository[InterviewSession]):
    model = InterviewSession

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: InterviewSessionStatus | None = None,
    ):
        stmt = select(InterviewSession).where(InterviewSession.user_id == user_id)
        if status is not None:
            stmt = stmt.where(InterviewSession.status == status)
        stmt = stmt.order_by(InterviewSession.created_at.desc())
        return await self.list(page=page, page_size=page_size, stmt=stmt)
