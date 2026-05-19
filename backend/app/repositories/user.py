"""User repository."""

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_clerk_id(self, clerk_id: str) -> User | None:
        stmt = select(User).where(User.clerk_id == clerk_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        active_only: bool = True,
    ):
        stmt = select(User)
        if active_only:
            stmt = stmt.where(User.is_active.is_(True))
        stmt = stmt.order_by(User.created_at.desc())
        return await self.list(page=page, page_size=page_size, stmt=stmt)
