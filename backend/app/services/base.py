"""Base service layer."""

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from app.repositories.base import BaseRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.utils.pagination import Page

RepoT = TypeVar("RepoT", bound=BaseRepository)
SchemaT = TypeVar("SchemaT")


class BaseService(Generic[RepoT, SchemaT]):
    """Maps repository results to response schemas."""

    def __init__(self, repository: RepoT) -> None:
        self.repository = repository

    def to_paginated_response(
        self,
        page: Page[Any],
        item_mapper: Callable[[Any], Any],
    ) -> PaginatedResponse[Any]:
        return PaginatedResponse(
            items=[item_mapper(item) for item in page.items],
            total=page.total,
            page=page.page,
            page_size=page.page_size,
            pages=page.pages,
        )

    @staticmethod
    def pagination_params(query: PaginationQuery) -> tuple[int, int]:
        return query.page, query.page_size
