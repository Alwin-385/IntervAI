"""Resume repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.resume import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        return await self.list(page=page, page_size=page_size, stmt=stmt)
