"""Interview session business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.interview_session import InterviewSession
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.resume import ResumeRepository
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.schemas.interview_session import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionUpdate,
)
from app.services.base import BaseService


class InterviewSessionService(BaseService[InterviewSessionRepository, InterviewSessionResponse]):
    def __init__(
        self,
        repository: InterviewSessionRepository,
        user_repository: UserRepository,
        resume_repository: ResumeRepository,
    ) -> None:
        super().__init__(repository)
        self.user_repository = user_repository
        self.resume_repository = resume_repository

    @staticmethod
    def _to_response(session: InterviewSession) -> InterviewSessionResponse:
        return InterviewSessionResponse.model_validate(session)

    async def _validate_refs(self, user_id: UUID, resume_id: UUID | None) -> None:
        if await self.user_repository.get_by_id(user_id) is None:
            raise NotFoundError("User", str(user_id))
        if resume_id and await self.resume_repository.get_by_id(resume_id) is None:
            raise NotFoundError("Resume", str(resume_id))

    async def create_session(
        self,
        user_id: UUID,
        payload: InterviewSessionCreate,
    ) -> InterviewSessionResponse:
        await self._validate_refs(user_id, payload.resume_id)
        session = await self.repository.create(
            {"user_id": user_id, **payload.model_dump()},
        )
        return self._to_response(session)

    async def get_session(self, session_id: UUID) -> InterviewSessionResponse:
        session = await self.repository.get_by_id_or_raise(
            session_id,
            resource="InterviewSession",
        )
        return self._to_response(session)

    async def list_sessions(
        self,
        user_id: UUID,
        pagination: PaginationQuery,
    ) -> PaginatedResponse[InterviewSessionResponse]:
        page, page_size = self.pagination_params(pagination)
        result = await self.repository.list_by_user(user_id, page=page, page_size=page_size)
        return self.to_paginated_response(result, self._to_response)

    async def update_session(
        self,
        session_id: UUID,
        payload: InterviewSessionUpdate,
    ) -> InterviewSessionResponse:
        session = await self.repository.get_by_id_or_raise(
            session_id,
            resource="InterviewSession",
        )
        data = payload.model_dump(exclude_unset=True)
        if "resume_id" in data and data["resume_id"]:
            if await self.resume_repository.get_by_id(data["resume_id"]) is None:
                raise NotFoundError("Resume", str(data["resume_id"]))
        updated = await self.repository.update(session, data)
        return self._to_response(updated)

    async def delete_session(self, session_id: UUID) -> None:
        session = await self.repository.get_by_id_or_raise(
            session_id,
            resource="InterviewSession",
        )
        await self.repository.delete(session)
