"""Pagination and filtering utilities."""

import math
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass
class Page(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def pages(self) -> int:
        if self.total == 0:
            return 0
        return math.ceil(self.total / self.page_size)


async def paginate(
    session: AsyncSession,
    stmt: Select[tuple[T]],
    *,
    page: int = 1,
    page_size: int = 20,
) -> Page[T]:
    """Execute a select statement with offset/limit and total count."""
    skip = (page - 1) * page_size

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total = int(total_result.scalar_one())

    result = await session.execute(stmt.offset(skip).limit(page_size))
    items = list(result.scalars().all())

    return Page(items=items, total=total, page=page, page_size=page_size)


def apply_filters(stmt: Select[tuple[T]], *conditions: ColumnElement[bool]) -> Select[tuple[T]]:
    for condition in conditions:
        stmt = stmt.where(condition)
    return stmt
