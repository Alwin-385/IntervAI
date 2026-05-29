"""Interview question repository."""

from uuid import UUID

from sqlalchemy import delete, select

from app.models.interview_question import InterviewQuestion
from app.repositories.base import BaseRepository


class InterviewQuestionRepository(BaseRepository[InterviewQuestion]):
    model = InterviewQuestion

    async def list_by_session(self, session_id: UUID) -> list[InterviewQuestion]:
        stmt = (
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id == session_id)
            .order_by(InterviewQuestion.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_session(self, session_id: UUID) -> int:
        stmt = delete(InterviewQuestion).where(
            InterviewQuestion.session_id == session_id,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return int(result.rowcount or 0)

    async def bulk_create(self, rows: list[dict]) -> list[InterviewQuestion]:
        instances = [InterviewQuestion(**data) for data in rows]
        self.session.add_all(instances)
        await self.session.flush()
        for inst in instances:
            await self.session.refresh(inst)
        return instances
