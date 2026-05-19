"""Roadmap repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.roadmap import Roadmap
from app.repositories.base import BaseRepository


class RoadmapRepository(BaseRepository[Roadmap]):
    model = Roadmap

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        stmt = (
            select(Roadmap)
            .where(Roadmap.user_id == user_id)
            .order_by(Roadmap.created_at.desc())
        )
        return await self.list(page=page, page_size=page_size, stmt=stmt)
