"""Upload interview audio and transcribe (Phase 11)."""

from __future__ import annotations

import uuid
from uuid import UUID

from app.core.config import Settings, get_settings
from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationAppError
from app.core.logging import get_logger
from app.repositories.interview_answer import InterviewAnswerRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.speech_analysis import SpeechAnalysisRepository
from app.schemas.speech import SpeechCapabilitiesResponse, TranscribeResponse, TranscriptionSource
from app.speech.transcript_cleanup import collapse_repeated_phrases as _collapse_repeated_phrases
from app.speech.transcription import WhisperTranscriptionService
from app.storage.base import StorageBackend
from app.storage.factory import get_audio_storage_backend
from app.utils.audio_validation import ALLOWED_AUDIO_EXTENSIONS, validate_audio_upload

logger = get_logger(__name__)


def _openai_user_message(exc: Exception) -> str:
    msg = str(exc).lower()
    if "insufficient_quota" in msg or "exceeded your current quota" in msg:
        return (
            "OpenAI API quota exceeded. Set SPEECH_TRANSCRIPTION_MODE=browser in backend/.env "
            "or add billing at https://platform.openai.com/account/billing."
        )
    if "rate_limit" in msg or "429" in msg:
        return "OpenAI rate limit reached. Wait a moment and try again."
    return f"Whisper transcription failed: {str(exc)[:240]}"


def _word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def _dedupe_immediate_repeat(text: str, *, max_phrase_words: int = 12) -> str:
    """Remove adjacent duplicate tail phrase (browser speech), without touching long answers."""
    words = text.split()
    n = len(words)
    if n < 4:
        return text
    cap = min(n // 2, max_phrase_words)
    for size in range(cap, 0, -1):
        if words[-size:] == words[-2 * size : -size]:
            return " ".join(words[:-size])
    return text


def _suffix_prefix_overlap_words(a: str, b: str) -> int:
    a_words = a.split()
    b_words = b.split()
    max_overlap = min(len(a_words), len(b_words), 80)
    for size in range(max_overlap, 0, -1):
        if [w.lower() for w in a_words[-size:]] == [w.lower() for w in b_words[:size]]:
            return size
    return 0


def _longest_common_prefix_words(a: str, b: str) -> int:
    a_words = a.split()
    b_words = b.split()
    shared = 0
    while shared < len(a_words) and shared < len(b_words):
        if a_words[shared].lower() != b_words[shared].lower():
            break
        shared += 1
    return shared


def _merge_transcripts(previous: str | None, new_segment: str) -> str:
    prior = " ".join((previous or "").split())
    segment = " ".join((new_segment or "").split())
    if not prior:
        return segment
    if not segment:
        return prior
    if prior == segment:
        return prior
    prior_lower = prior.lower()
    segment_lower = segment.lower()
    if prior_lower.startswith(segment_lower):
        return prior
    if segment_lower.startswith(prior_lower):
        return segment

    overlap = _suffix_prefix_overlap_words(prior, segment)
    if overlap:
        segment_words = segment.split()
        tail = " ".join(segment_words[overlap:])
        return f"{prior} {tail}".strip() if tail else prior
    if len(segment) < len(prior) and segment_lower in prior_lower:
        return prior
    if len(segment) > len(prior) and prior_lower in segment_lower:
        return segment
    merged = f"{prior} {segment}"
    return _collapse_repeated_phrases(merged)


class SpeechTranscriptionService:
    def __init__(
        self,
        session_repo: InterviewSessionRepository,
        question_repo: InterviewQuestionRepository,
        answer_repo: InterviewAnswerRepository,
        speech_repo: SpeechAnalysisRepository,
        storage: StorageBackend | None = None,
        whisper: WhisperTranscriptionService | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.session_repo = session_repo
        self.question_repo = question_repo
        self.answer_repo = answer_repo
        self.speech_repo = speech_repo
        self.storage = storage or get_audio_storage_backend()
        self.whisper = whisper or WhisperTranscriptionService()
        self.settings = settings or get_settings()

    def capabilities(self) -> SpeechCapabilitiesResponse:
        mode = self.settings.speech_transcription_mode
        whisper_ready = mode == "whisper" and self.whisper.is_available()
        return SpeechCapabilitiesResponse(
            transcription_mode=mode,
            whisper_available=whisper_ready,
            max_size_bytes=self.settings.speech_max_size_bytes,
            allowed_extensions=sorted(ALLOWED_AUDIO_EXTENSIONS),
        )

    def _transcribe_clip(
        self,
        *,
        data: bytes,
        filename: str,
        mime_type: str,
        browser_transcript: str | None,
    ) -> tuple[str, TranscriptionSource, str | None]:
        browser = (browser_transcript or "").strip()
        use_whisper = self.settings.speech_transcription_mode == "whisper"

        if use_whisper and self.whisper.is_available():
            try:
                result = self.whisper.transcribe(
                    data=data,
                    filename=filename,
                    mime_type=mime_type,
                )
                return result.transcript, result.source, result.model
            except Exception as exc:
                logger.warning("whisper_transcribe_failed", error=str(exc))
                if browser:
                    return browser, "browser", None
                raise ValidationAppError(_openai_user_message(exc)) from exc

        if browser:
            return browser, "browser", None

        # Audio saved without live captions — transcript can be typed/edited after upload.
        return "", "browser", None

    async def _verify_question_access(
        self,
        user_id: UUID,
        question_id: UUID,
    ) -> tuple[UUID, UUID]:
        question = await self.question_repo.get_by_id(question_id)
        if question is None:
            raise NotFoundError("InterviewQuestion", str(question_id))
        session = await self.session_repo.get_by_id(question.session_id)
        if session is None:
            raise NotFoundError("InterviewSession", str(question.session_id))
        if session.user_id != user_id:
            raise UnauthorizedError("You do not have access to this interview session")
        return session.id, question.id

    async def transcribe_upload(
        self,
        user_id: UUID,
        *,
        filename: str,
        content_type: str | None,
        data: bytes,
        session_id: UUID | None = None,
        question_id: UUID | None = None,
        duration_seconds: float | None = None,
        browser_transcript: str | None = None,
        previous_transcript: str | None = None,
    ) -> TranscribeResponse:
        mime_type = validate_audio_upload(
            filename=filename,
            content_type=content_type,
            data=data,
            settings=self.settings,
        )

        resolved_question_id = question_id

        if question_id:
            _, resolved_question_id = await self._verify_question_access(
                user_id,
                question_id,
            )
        elif session_id:
            session = await self.session_repo.get_by_id_or_raise(
                session_id,
                resource="InterviewSession",
            )
            if session.user_id != user_id:
                raise UnauthorizedError("You do not have access to this interview session")

        ext = "." + (filename.rsplit(".", 1)[-1] if "." in filename else "webm")
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            ext = ".webm"
        storage_key = f"{user_id}/{uuid.uuid4()}{ext}"
        stored = await self.storage.save(storage_key, data, mime_type)

        transcript, source, _model = self._transcribe_clip(
            data=data,
            filename=filename,
            mime_type=mime_type,
            browser_transcript=browser_transcript,
        )

        transcript = _dedupe_immediate_repeat(transcript)
        transcript = _merge_transcripts(previous_transcript, transcript)
        transcript = _collapse_repeated_phrases(transcript)

        answer_id: UUID | None = None
        if resolved_question_id:
            answer_id = await self._upsert_answer(
                question_id=resolved_question_id,
                transcript=transcript,
                audio_uri=stored.uri,
                duration_seconds=duration_seconds,
            )

        return TranscribeResponse(
            transcript=transcript,
            audio_storage_path=stored.uri,
            duration_seconds=duration_seconds,
            mime_type=mime_type,
            file_size_bytes=stored.size_bytes,
            transcription_source=source,
            speech_analysis_id=None,
            answer_id=answer_id,
            whisper_available=self.capabilities().whisper_available,
        )

    async def _upsert_answer(
        self,
        *,
        question_id: UUID,
        transcript: str,
        audio_uri: str,
        duration_seconds: float | None,
    ) -> UUID:
        existing = await self.answer_repo.get_latest_by_question(question_id)
        payload = {
            "answer_text": transcript,
            "audio_storage_path": audio_uri,
            "duration_seconds": duration_seconds,
            "word_count": _word_count(transcript),
        }
        if existing:
            updated = await self.answer_repo.update(existing, payload)
            return updated.id
        created = await self.answer_repo.create({"question_id": question_id, **payload})
        return created.id


def _estimate_filler_count(transcript: str) -> int:
    fillers = ("um", "uh", "like", "you know", "actually", "basically")
    lower = transcript.lower()
    return sum(lower.count(f" {word} ") for word in fillers)
