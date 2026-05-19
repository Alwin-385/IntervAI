"""Resume analysis business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.resume_analysis import ResumeAnalysis
from app.repositories.resume import ResumeRepository
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.schemas.resume_analysis import (
    ResumeAnalysisCreate,
    ResumeAnalysisResponse,
    ResumeAnalysisUpdate,
)
from app.services.base import BaseService


class ResumeAnalysisService(
    BaseService[ResumeAnalysisRepository, ResumeAnalysisResponse]
):
    def __init__(
        self,
        repository: ResumeAnalysisRepository,
        resume_repository: ResumeRepository,
    ) -> None:
        super().__init__(repository)
        self.resume_repository = resume_repository

    @staticmethod
    def _to_response(analysis: ResumeAnalysis) -> ResumeAnalysisResponse:
        return ResumeAnalysisResponse.model_validate(analysis)

    async def create(self, payload: ResumeAnalysisCreate) -> ResumeAnalysisResponse:
        if await self.resume_repository.get_by_id(payload.resume_id) is None:
            raise NotFoundError("Resume", str(payload.resume_id))
        entity = await self.repository.create(payload.model_dump())
        return self._to_response(entity)

    async def get(self, analysis_id: UUID) -> ResumeAnalysisResponse:
        entity = await self.repository.get_by_id_or_raise(
            analysis_id,
            resource="ResumeAnalysis",
        )
        return self._to_response(entity)

    async def list_for_resume(
        self,
        resume_id: UUID,
        pagination: PaginationQuery,
    ) -> PaginatedResponse[ResumeAnalysisResponse]:
        page, page_size = self.pagination_params(pagination)
        result = await self.repository.list_by_resume(
            resume_id,
            page=page,
            page_size=page_size,
        )
        return self.to_paginated_response(result, self._to_response)

    async def update(
        self,
        analysis_id: UUID,
        payload: ResumeAnalysisUpdate,
    ) -> ResumeAnalysisResponse:
        entity = await self.repository.get_by_id_or_raise(
            analysis_id,
            resource="ResumeAnalysis",
        )
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, analysis_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(
            analysis_id,
            resource="ResumeAnalysis",
        )
        await self.repository.delete(entity)
