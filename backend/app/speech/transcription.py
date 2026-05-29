"""Speech-to-text via OpenAI Whisper (Phase 11)."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Literal

from openai import OpenAI

from app.core.config import Settings, get_settings
from app.core.exceptions import ValidationAppError

TranscriptionSource = Literal["whisper", "browser"]


@dataclass(frozen=True)
class TranscriptionResult:
    transcript: str
    source: TranscriptionSource
    model: str | None = None


class WhisperTranscriptionService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: OpenAI | None = None

    def is_available(self) -> bool:
        return bool(self._settings.openai_api_key)

    def _client_or_raise(self) -> OpenAI:
        if not self.is_available():
            raise ValidationAppError(
                "Server transcription is unavailable. Use browser speech recognition "
                "or set OPENAI_API_KEY for Whisper.",
            )
        if self._client is None:
            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                timeout=self._settings.openai_request_timeout_seconds,
                max_retries=1,
            )
        return self._client

    def transcribe(
        self,
        *,
        data: bytes,
        filename: str,
        mime_type: str,
    ) -> TranscriptionResult:
        client = self._client_or_raise()
        buffer = io.BytesIO(data)
        buffer.name = filename or "recording.webm"

        response = client.audio.transcriptions.create(
            model=self._settings.openai_whisper_model,
            file=(buffer.name, buffer, mime_type),
            response_format="text",
        )
        text = response if isinstance(response, str) else str(response)
        transcript = text.strip()
        if not transcript:
            raise ValidationAppError("Transcription returned empty text. Try recording again.")

        return TranscriptionResult(
            transcript=transcript,
            source="whisper",
            model=self._settings.openai_whisper_model,
        )
