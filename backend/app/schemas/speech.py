"""Speech transcription API schemas (Phase 11)."""

from typing import Literal
from uuid import UUID

from app.schemas.common import SchemaBase

TranscriptionSource = Literal["whisper", "browser"]


class TranscribeResponse(SchemaBase):
    transcript: str
    audio_storage_path: str
    duration_seconds: float | None = None
    mime_type: str
    file_size_bytes: int
    transcription_source: TranscriptionSource
    speech_analysis_id: UUID | None = None
    answer_id: UUID | None = None
    whisper_available: bool = True


class SpeechCapabilitiesResponse(SchemaBase):
    transcription_mode: Literal["browser", "whisper"]
    whisper_available: bool
    max_size_bytes: int
    allowed_extensions: list[str]
