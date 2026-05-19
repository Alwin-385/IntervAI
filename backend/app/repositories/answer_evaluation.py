"""Answer evaluation repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.answer_evaluation import AnswerEvaluation
from app.repositories.base import BaseRepository


class AnswerEvaluationRepository(BaseRepository[AnswerEvaluation]):
    model = AnswerEvaluation

    async def get_by_answer_id(self, answer_id: UUID) -> AnswerEvaluation | None:
        stmt = select(AnswerEvaluation).where(AnswerEvaluation.answer_id == answer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
