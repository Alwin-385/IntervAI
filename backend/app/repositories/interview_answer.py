"""Interview answer repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.interview_answer import InterviewAnswer
from app.repositories.base import BaseRepository


class InterviewAnswerRepository(BaseRepository[InterviewAnswer]):
    model = InterviewAnswer

    async def list_by_question(self, question_id: UUID) -> list[InterviewAnswer]:
        stmt = select(InterviewAnswer).where(InterviewAnswer.question_id == question_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
