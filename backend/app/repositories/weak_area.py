"""Weak area repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.weak_area import WeakArea
from app.repositories.base import BaseRepository


class WeakAreaRepository(BaseRepository[WeakArea]):
    model = WeakArea

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        stmt = (
            select(WeakArea).where(WeakArea.user_id == user_id).order_by(WeakArea.created_at.desc())
        )
        return await self.list(page=page, page_size=page_size, stmt=stmt)
