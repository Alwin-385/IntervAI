"""Speech analysis business logic."""

from uuid import UUID

from app.core.exceptions import ValidationAppError
from app.models.speech_analysis import SpeechAnalysis
from app.repositories.speech_analysis import SpeechAnalysisRepository
from app.schemas.speech_analysis import (
    SpeechAnalysisCreate,
    SpeechAnalysisResponse,
    SpeechAnalysisUpdate,
)
from app.services.base import BaseService


class SpeechAnalysisService(BaseService[SpeechAnalysisRepository, SpeechAnalysisResponse]):
    @staticmethod
    def _to_response(analysis: SpeechAnalysis) -> SpeechAnalysisResponse:
        return SpeechAnalysisResponse.model_validate(analysis)

    async def create(self, payload: SpeechAnalysisCreate) -> SpeechAnalysisResponse:
        if not payload.answer_id and not payload.session_id:
            raise ValidationAppError(
                "Either answer_id or session_id must be provided",
            )
        entity = await self.repository.create(payload.model_dump())
        return self._to_response(entity)

    async def get(self, analysis_id: UUID) -> SpeechAnalysisResponse:
        entity = await self.repository.get_by_id_or_raise(
            analysis_id,
            resource="SpeechAnalysis",
        )
        return self._to_response(entity)

    async def update(
        self,
        analysis_id: UUID,
        payload: SpeechAnalysisUpdate,
    ) -> SpeechAnalysisResponse:
        entity = await self.repository.get_by_id_or_raise(
            analysis_id,
            resource="SpeechAnalysis",
        )
        updated = await self.repository.update(entity, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete(self, analysis_id: UUID) -> None:
        entity = await self.repository.get_by_id_or_raise(
            analysis_id,
            resource="SpeechAnalysis",
        )
        await self.repository.delete(entity)
