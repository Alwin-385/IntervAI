"""Read and retry resume extraction status."""

from __future__ import annotations

from uuid import UUID

from app.models.enums import ResumeStatus
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository
from app.schemas.resume_extraction import ExtractedResumeData, ResumeExtractionStatusResponse


class ResumeExtractionStatusService:
    def __init__(self, repository: ResumeRepository) -> None:
        self.repository = repository

    def _build_status(self, resume: Resume) -> ResumeExtractionStatusResponse:
        extracted: ExtractedResumeData | None = None
        if resume.extracted_data:
            extracted = ExtractedResumeData.model_validate(resume.extracted_data)

        chunks = resume.text_chunks or []
        return ResumeExtractionStatusResponse(
            id=resume.id,
            resume_id=resume.id,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            status=resume.status,
            extraction_error=resume.extraction_error,
            has_cleaned_text=bool(resume.cleaned_text),
            chunk_count=len(chunks),
            extracted_data=extracted,
        )

    async def get_status(self, resume_id: UUID) -> ResumeExtractionStatusResponse:
        resume = await self.repository.get_by_id_or_raise(resume_id, resource="Resume")
        return self._build_status(resume)

    async def retry_extraction(self, resume_id: UUID) -> ResumeExtractionStatusResponse:
        resume = await self.repository.get_by_id_or_raise(resume_id, resource="Resume")
        updated = await self.repository.update(
            resume,
            {
                "status": ResumeStatus.QUEUED,
                "extraction_error": None,
                "content_text": None,
                "cleaned_text": None,
                "extracted_data": None,
                "text_chunks": None,
            },
        )
        return self._build_status(updated)
