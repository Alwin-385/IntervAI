"""Weak area business logic."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.weak_area import WeakArea
from app.repositories.user import UserRepository
from app.repositories.weak_area import WeakAreaRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.schemas.weak_area import WeakAreaCreate, WeakAreaResponse, WeakAreaUpdate
from app.services.base import BaseService


class WeakAreaService(BaseService[WeakAreaRepository, WeakAreaResponse]):
    def __init__(
        self,
        repository: WeakAreaRepository,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(repository)
        self.user_repository = user_repository

    @staticmethod
    def _to_response(area: WeakArea) -> WeakAreaResponse:
        return WeakAreaResponse.model_validate(area)

    async def create(self, user_id: UUID, payload: WeakAreaCreate) -> WeakAreaResponse:
        if await self.user_repository.get_by_id(user_id) is None:
            raise NotFoundError("User", str(user_id))
        entity = await self.repository.create(
            {"user_id": user_id, **payload.model_dump()},
        )
        return self._to_response(entity)

    async def get(self, area_id: UUID) -> WeakAreaResponse:
        entity = await self.repository.get_by_id_or_raise(area_id, resource="WeakArea")
        return self._to_response(entity)

    async def list_for_user(
        self,
        user_id: UUID,
        pagination: PaginationQuery,
    ) -> PaginatedResponse[WeakAreaResponse]:
        page, page_size = self.pagination_params(pagination)
        result = await self.repository.list_by_user(user_id, page=page, page_size=page_size)
        return self.to_paginated_response(result, self._to_response)

    async def update(self, area_id: UUID, payload: WeakAreaUpdate) -> WeakAreaResponse:
        entity = await self.repository.get_by_id_or_raise(area_id, resource="WeakArea")
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, area_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(area_id, resource="WeakArea")
        await self.repository.delete(entity)
