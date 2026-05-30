"""Background worker for Whisper transcription (heavy audio)."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from app.services.background_job_sync import sync_job_update_progress


def execute_transcription_sync(payload: dict[str, Any]) -> dict[str, Any]:
    from app.core.database import db_manager
    from app.repositories.interview_answer import InterviewAnswerRepository
    from app.repositories.interview_question import InterviewQuestionRepository
    from app.repositories.interview_session import InterviewSessionRepository
    from app.services.speech_transcription import SpeechTranscriptionService

    job_id = payload.get("job_id")
    user_id = UUID(payload["user_id"])

    async def _run():
        async with db_manager.session_factory() as session:
            svc = SpeechTranscriptionService(
                InterviewSessionRepository(session),
                InterviewQuestionRepository(session),
                InterviewAnswerRepository(session),
            )
            return await svc.transcribe_upload(
                user_id,
                filename=payload.get("filename") or "recording.webm",
                content_type=payload.get("content_type"),
                data=bytes(payload.get("audio_bytes") or b""),
                session_id=UUID(payload["session_id"]) if payload.get("session_id") else None,
                question_id=UUID(payload["question_id"]) if payload.get("question_id") else None,
                duration_seconds=payload.get("duration_seconds"),
                browser_transcript=payload.get("browser_transcript"),
                previous_transcript=payload.get("previous_transcript"),
            )

    loop = asyncio.new_event_loop()
    try:
        if job_id:
            sync_job_update_progress(job_id, percent=35, message="Transcribing…")
        result = loop.run_until_complete(_run())
    finally:
        loop.close()

    return {
        "transcript": result.transcript,
        "storage_path": result.storage_path,
        "status": "completed",
    }
