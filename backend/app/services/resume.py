"""Resume business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.services.base import BaseService


class ResumeService(BaseService[ResumeRepository, ResumeResponse]):
    def __init__(
        self,
        repository: ResumeRepository,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(repository)
        self.user_repository = user_repository

    @staticmethod
    def _to_response(resume: Resume) -> ResumeResponse:
        return ResumeResponse.model_validate(resume)

    async def _ensure_user(self, user_id: UUID) -> None:
        if await self.user_repository.get_by_id(user_id) is None:
            raise NotFoundError("User", str(user_id))

    async def create_resume(self, user_id: UUID, payload: ResumeCreate) -> ResumeResponse:
        await self._ensure_user(user_id)
        resume = await self.repository.create(
            {"user_id": user_id, **payload.model_dump()},
        )
        return self._to_response(resume)

    async def get_resume(self, resume_id: UUID) -> ResumeResponse:
        resume = await self.repository.get_by_id_or_raise(resume_id, resource="Resume")
        return self._to_response(resume)

    async def list_resumes(
        self,
        user_id: UUID,
        pagination: PaginationQuery,
    ) -> PaginatedResponse[ResumeResponse]:
        await self._ensure_user(user_id)
        page, page_size = self.pagination_params(pagination)
        result = await self.repository.list_by_user(user_id, page=page, page_size=page_size)
        return self.to_paginated_response(result, self._to_response)

    async def update_resume(self, resume_id: UUID, payload: ResumeUpdate) -> ResumeResponse:
        resume = await self.repository.get_by_id_or_raise(resume_id, resource="Resume")
        updated = await self.repository.update(
            resume,
            payload.model_dump(exclude_unset=True),
        )
        return self._to_response(updated)

    async def delete_resume(self, resume_id: UUID) -> None:
        resume = await self.repository.get_by_id_or_raise(resume_id, resource="Resume")
        await self.repository.delete(resume)
