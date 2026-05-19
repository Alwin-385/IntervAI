"""Answer evaluation business logic."""

from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.models.answer_evaluation import AnswerEvaluation
from app.repositories.answer_evaluation import AnswerEvaluationRepository
from app.repositories.interview_answer import InterviewAnswerRepository
from app.schemas.answer_evaluation import (
    AnswerEvaluationCreate,
    AnswerEvaluationResponse,
    AnswerEvaluationUpdate,
)
from app.services.base import BaseService


class AnswerEvaluationService(
    BaseService[AnswerEvaluationRepository, AnswerEvaluationResponse]
):
    def __init__(
        self,
        repository: AnswerEvaluationRepository,
        answer_repository: InterviewAnswerRepository,
    ) -> None:
        super().__init__(repository)
        self.answer_repository = answer_repository

    @staticmethod
    def _to_response(evaluation: AnswerEvaluation) -> AnswerEvaluationResponse:
        return AnswerEvaluationResponse.model_validate(evaluation)

    async def create(self, payload: AnswerEvaluationCreate) -> AnswerEvaluationResponse:
        if await self.answer_repository.get_by_id(payload.answer_id) is None:
            raise NotFoundError("InterviewAnswer", str(payload.answer_id))
        existing = await self.repository.get_by_answer_id(payload.answer_id)
        if existing:
            raise ConflictError("Evaluation already exists for this answer")
        entity = await self.repository.create(payload.model_dump())
        return self._to_response(entity)

    async def get(self, evaluation_id: UUID) -> AnswerEvaluationResponse:
        entity = await self.repository.get_by_id_or_raise(
            evaluation_id,
            resource="AnswerEvaluation",
        )
        return self._to_response(entity)

    async def update(
        self,
        evaluation_id: UUID,
        payload: AnswerEvaluationUpdate,
    ) -> AnswerEvaluationResponse:
        entity = await self.repository.get_by_id_or_raise(
            evaluation_id,
            resource="AnswerEvaluation",
        )
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, evaluation_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(
            evaluation_id,
            resource="AnswerEvaluation",
        )
        await self.repository.delete(entity)
