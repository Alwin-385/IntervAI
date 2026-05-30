"""Background job repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.background_job import BackgroundJob
from app.models.enums import BackgroundJobType
from app.repositories.base import BaseRepository


class BackgroundJobRepository(BaseRepository[BackgroundJob]):
    model = BackgroundJob

    async def get_for_user(self, job_id: UUID, user_id: UUID) -> BackgroundJob | None:
        stmt = select(BackgroundJob).where(
            BackgroundJob.id == job_id,
            BackgroundJob.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_resource(
        self,
        user_id: UUID,
        *,
        resource_type: str,
        resource_id: UUID,
        limit: int = 10,
    ) -> list[BackgroundJob]:
        stmt = (
            select(BackgroundJob)
            .where(
                BackgroundJob.user_id == user_id,
                BackgroundJob.resource_type == resource_type,
                BackgroundJob.resource_id == resource_id,
            )
            .order_by(BackgroundJob.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_resource(
        self,
        user_id: UUID,
        *,
        resource_type: str,
        resource_id: UUID,
        job_type: BackgroundJobType | None = None,
    ) -> BackgroundJob | None:
        stmt = (
            select(BackgroundJob)
            .where(
                BackgroundJob.user_id == user_id,
                BackgroundJob.resource_type == resource_type,
                BackgroundJob.resource_id == resource_id,
            )
            .order_by(BackgroundJob.created_at.desc())
            .limit(1)
        )
        if job_type is not None:
            stmt = stmt.where(BackgroundJob.job_type == job_type)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
