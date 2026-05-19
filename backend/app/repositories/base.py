"""Generic async repository base class."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.exceptions import NotFoundError
from app.utils.pagination import Page, paginate

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Reusable CRUD operations for SQLAlchemy models."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_select(self) -> Select[tuple[ModelT]]:
        return select(self.model)

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def get_by_id_or_raise(self, entity_id: UUID, *, resource: str | None = None) -> ModelT:
        entity = await self.get_by_id(entity_id)
        if entity is None:
            raise NotFoundError(resource or self.model.__tablename__, str(entity_id))
        return entity

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        stmt: Select[tuple[ModelT]] | None = None,
    ) -> Page[ModelT]:
        query = stmt if stmt is not None else self._base_select()
        return await paginate(self.session, query, page=page, page_size=page_size)

    async def count(self, stmt: Select[tuple[ModelT]] | None = None) -> int:
        query = stmt if stmt is not None else self._base_select()
        count_stmt = select(func.count()).select_from(query.subquery())
        result = await self.session.execute(count_stmt)
        return int(result.scalar_one())

    async def create(self, data: dict[str, Any]) -> ModelT:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()
