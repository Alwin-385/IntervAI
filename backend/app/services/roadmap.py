"""Roadmap business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.roadmap import Roadmap
from app.repositories.roadmap import RoadmapRepository
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.schemas.roadmap import RoadmapCreate, RoadmapResponse, RoadmapUpdate
from app.services.base import BaseService


class RoadmapService(BaseService[RoadmapRepository, RoadmapResponse]):
    def __init__(
        self,
        repository: RoadmapRepository,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(repository)
        self.user_repository = user_repository

    @staticmethod
    def _to_response(roadmap: Roadmap) -> RoadmapResponse:
        return RoadmapResponse.model_validate(roadmap)

    async def create(self, user_id: UUID, payload: RoadmapCreate) -> RoadmapResponse:
        if await self.user_repository.get_by_id(user_id) is None:
            raise NotFoundError("User", str(user_id))
        entity = await self.repository.create(
            {"user_id": user_id, **payload.model_dump()},
        )
        return self._to_response(entity)

    async def get(self, roadmap_id: UUID) -> RoadmapResponse:
        entity = await self.repository.get_by_id_or_raise(roadmap_id, resource="Roadmap")
        return self._to_response(entity)

    async def list_for_user(
        self,
        user_id: UUID,
        pagination: PaginationQuery,
    ) -> PaginatedResponse[RoadmapResponse]:
        page, page_size = self.pagination_params(pagination)
        result = await self.repository.list_by_user(user_id, page=page, page_size=page_size)
        return self.to_paginated_response(result, self._to_response)

    async def update(self, roadmap_id: UUID, payload: RoadmapUpdate) -> RoadmapResponse:
        entity = await self.repository.get_by_id_or_raise(roadmap_id, resource="Roadmap")
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, roadmap_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(roadmap_id, resource="Roadmap")
        await self.repository.delete(entity)
