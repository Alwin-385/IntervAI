"""Speech analysis repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.speech_analysis import SpeechAnalysis
from app.repositories.base import BaseRepository


class SpeechAnalysisRepository(BaseRepository[SpeechAnalysis]):
    model = SpeechAnalysis

    async def list_by_answer(self, answer_id: UUID) -> list[SpeechAnalysis]:
        stmt = select(SpeechAnalysis).where(SpeechAnalysis.answer_id == answer_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_session(self, session_id: UUID) -> list[SpeechAnalysis]:
        stmt = select(SpeechAnalysis).where(SpeechAnalysis.session_id == session_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
