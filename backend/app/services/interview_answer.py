"""Interview answer business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.interview_answer import InterviewAnswer
from app.repositories.interview_answer import InterviewAnswerRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.schemas.interview_answer import (
    InterviewAnswerCreate,
    InterviewAnswerResponse,
    InterviewAnswerUpdate,
)
from app.services.base import BaseService


class InterviewAnswerService(BaseService[InterviewAnswerRepository, InterviewAnswerResponse]):
    def __init__(
        self,
        repository: InterviewAnswerRepository,
        question_repository: InterviewQuestionRepository,
    ) -> None:
        super().__init__(repository)
        self.question_repository = question_repository

    @staticmethod
    def _to_response(answer: InterviewAnswer) -> InterviewAnswerResponse:
        return InterviewAnswerResponse.model_validate(answer)

    async def create(self, payload: InterviewAnswerCreate) -> InterviewAnswerResponse:
        if await self.question_repository.get_by_id(payload.question_id) is None:
            raise NotFoundError("InterviewQuestion", str(payload.question_id))
        entity = await self.repository.create(payload.model_dump())
        return self._to_response(entity)

    async def get(self, answer_id: UUID) -> InterviewAnswerResponse:
        entity = await self.repository.get_by_id_or_raise(
            answer_id,
            resource="InterviewAnswer",
        )
        return self._to_response(entity)

    async def update(
        self,
        answer_id: UUID,
        payload: InterviewAnswerUpdate,
    ) -> InterviewAnswerResponse:
        entity = await self.repository.get_by_id_or_raise(
            answer_id,
            resource="InterviewAnswer",
        )
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, answer_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(
            answer_id,
            resource="InterviewAnswer",
        )
        await self.repository.delete(entity)
