"""Resume PDF upload and replacement logic."""

import uuid
from pathlib import Path
from uuid import UUID

from app.core.config import Settings, get_settings
from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationAppError
from app.core.logging import get_logger
from app.models.enums import ResumeStatus
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository
from app.storage.base import StorageBackend
from app.storage.factory import get_storage_backend
from app.schemas.resume import ResumeResponse, ResumeUploadResponse
from app.utils.file_validation import (
    extract_pdf_text,
    sanitize_filename,
    validate_pdf_upload,
)

logger = get_logger(__name__)


class ResumeUploadService:
    def __init__(
        self,
        repository: ResumeRepository,
        storage: StorageBackend | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.repository = repository
        self.storage = storage or get_storage_backend()
        self.settings = settings or get_settings()

    @staticmethod
    def _to_response(resume: Resume, message: str | None = None) -> ResumeUploadResponse:
        base = ResumeResponse.model_validate(resume)
        return ResumeUploadResponse(
            **base.model_dump(),
            message=message or "Resume uploaded successfully",
        )

    def _build_storage_key(self, user_id: UUID, file_id: uuid.UUID) -> str:
        return f"{user_id}/{file_id}.pdf"

    async def upload_pdf(
        self,
        user_id: UUID,
        *,
        filename: str,
        content_type: str | None,
        data: bytes,
        title: str | None = None,
        replace_resume_id: UUID | None = None,
    ) -> ResumeUploadResponse:
        validate_pdf_upload(
            filename=filename,
            content_type=content_type,
            data=data,
            settings=self.settings,
        )

        safe_filename = sanitize_filename(filename)
        file_id = uuid.uuid4()
        storage_key = self._build_storage_key(user_id, file_id)
        mime_type = (content_type or "application/pdf").split(";")[0].strip()

        stored = await self.storage.save(storage_key, data, mime_type)
        content_text = extract_pdf_text(data)
        display_title = (title or Path(safe_filename).stem).strip()[:255] or "My Resume"

        if replace_resume_id:
            return await self._replace_resume(
                user_id=user_id,
                replace_resume_id=replace_resume_id,
                safe_filename=safe_filename,
                storage_key=storage_key,
                stored_uri=stored.uri,
                mime_type=mime_type,
                file_size=stored.size_bytes,
                content_text=content_text,
                display_title=display_title,
            )

        resume = await self.repository.create(
            {
                "user_id": user_id,
                "title": display_title,
                "file_name": safe_filename,
                "storage_path": stored.uri,
                "storage_key": storage_key,
                "mime_type": mime_type,
                "file_size_bytes": stored.size_bytes,
                "content_text": content_text,
                "status": ResumeStatus.UPLOADED,
            }
        )
        logger.info(
            "resume_uploaded",
            user_id=str(user_id),
            resume_id=str(resume.id),
            size=stored.size_bytes,
        )
        return self._to_response(resume)

    async def _replace_resume(
        self,
        *,
        user_id: UUID,
        replace_resume_id: UUID,
        safe_filename: str,
        storage_key: str,
        stored_uri: str,
        mime_type: str,
        file_size: int,
        content_text: str | None,
        display_title: str,
    ) -> ResumeUploadResponse:
        existing = await self.repository.get_by_id_or_raise(
            replace_resume_id,
            resource="Resume",
        )
        if existing.user_id != user_id:
            raise UnauthorizedError("You do not have access to this resume")

        old_key = existing.storage_key
        updated = await self.repository.update(
            existing,
            {
                "title": display_title,
                "file_name": safe_filename,
                "storage_path": stored_uri,
                "storage_key": storage_key,
                "mime_type": mime_type,
                "file_size_bytes": file_size,
                "content_text": content_text,
                "status": ResumeStatus.UPLOADED,
            },
        )
        if old_key != storage_key:
            try:
                await self.storage.delete(old_key)
            except Exception as exc:
                logger.warning("resume_storage_delete_failed", key=old_key, error=str(exc))

        logger.info("resume_replaced", resume_id=str(replace_resume_id))
        return self._to_response(updated, message="Resume replaced successfully")
