"""Interview answer repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.interview_answer import InterviewAnswer
from app.models.interview_question import InterviewQuestion
from app.repositories.base import BaseRepository


class InterviewAnswerRepository(BaseRepository[InterviewAnswer]):
    model = InterviewAnswer

    async def list_by_question(self, question_id: UUID) -> list[InterviewAnswer]:
        stmt = select(InterviewAnswer).where(InterviewAnswer.question_id == question_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_question(self, question_id: UUID) -> InterviewAnswer | None:
        stmt = (
            select(InterviewAnswer)
            .where(InterviewAnswer.question_id == question_id)
            .order_by(InterviewAnswer.updated_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_session(self, session_id: UUID) -> list[InterviewAnswer]:
        stmt = (
            select(InterviewAnswer)
            .join(InterviewQuestion, InterviewAnswer.question_id == InterviewQuestion.id)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.order_index, InterviewAnswer.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
