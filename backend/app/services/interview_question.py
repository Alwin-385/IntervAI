"""Interview question business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.interview_question import InterviewQuestion
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.schemas.interview_question import (
    InterviewQuestionCreate,
    InterviewQuestionResponse,
    InterviewQuestionUpdate,
)
from app.services.base import BaseService


class InterviewQuestionService(BaseService[InterviewQuestionRepository, InterviewQuestionResponse]):
    def __init__(
        self,
        repository: InterviewQuestionRepository,
        session_repository: InterviewSessionRepository,
    ) -> None:
        super().__init__(repository)
        self.session_repository = session_repository

    @staticmethod
    def _to_response(question: InterviewQuestion) -> InterviewQuestionResponse:
        return InterviewQuestionResponse.model_validate(question)

    async def create(self, payload: InterviewQuestionCreate) -> InterviewQuestionResponse:
        if await self.session_repository.get_by_id(payload.session_id) is None:
            raise NotFoundError("InterviewSession", str(payload.session_id))
        entity = await self.repository.create(payload.model_dump())
        return self._to_response(entity)

    async def get(self, question_id: UUID) -> InterviewQuestionResponse:
        entity = await self.repository.get_by_id_or_raise(
            question_id,
            resource="InterviewQuestion",
        )
        return self._to_response(entity)

    async def list_for_session(self, session_id: UUID) -> list[InterviewQuestionResponse]:
        return [self._to_response(q) for q in await self.repository.list_by_session(session_id)]

    async def update(
        self,
        question_id: UUID,
        payload: InterviewQuestionUpdate,
    ) -> InterviewQuestionResponse:
        entity = await self.repository.get_by_id_or_raise(
            question_id,
            resource="InterviewQuestion",
        )
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, question_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(
            question_id,
            resource="InterviewQuestion",
        )
        await self.repository.delete(entity)
