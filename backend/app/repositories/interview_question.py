"""Interview question repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.interview_question import InterviewQuestion
from app.repositories.base import BaseRepository


class InterviewQuestionRepository(BaseRepository[InterviewQuestion]):
    model = InterviewQuestion

    async def list_by_session(self, session_id: UUID) -> list[InterviewQuestion]:
        stmt = (
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
