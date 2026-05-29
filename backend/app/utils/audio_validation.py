"""Audio upload validation for speech transcription."""

from __future__ import annotations

from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import ValidationAppError

ALLOWED_AUDIO_EXTENSIONS = {".webm", ".ogg", ".mp4", ".m4a", ".mpeg", ".mp3", ".wav"}
ALLOWED_AUDIO_MIME_PREFIXES = (
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp3",
)


def validate_audio_upload(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
    settings: Settings,
) -> str:
    if not data:
        raise ValidationAppError("Audio file is empty.")
    if len(data) > settings.speech_max_size_bytes:
        max_mb = settings.speech_max_size_bytes / (1024 * 1024)
        raise ValidationAppError(f"Audio file exceeds maximum size of {max_mb:.0f} MB.")

    ext = Path(filename or "").suffix.lower()
    if ext and ext not in ALLOWED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
        raise ValidationAppError(f"Unsupported audio format '{ext}'. Allowed: {allowed}")

    mime = (content_type or "").split(";")[0].strip().lower()
    if (
        mime
        and not any(mime.startswith(p) for p in ALLOWED_AUDIO_MIME_PREFIXES)
        and (not ext or ext not in ALLOWED_AUDIO_EXTENSIONS)
    ):
        raise ValidationAppError(f"Unsupported audio content type: {mime}")

    return mime or "audio/webm"
