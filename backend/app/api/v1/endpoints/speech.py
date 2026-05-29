"""Speech transcription endpoints (Phase 11)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import (
    get_speech_analyzer_engine_service,
    get_speech_transcription_service,
)
from app.models.user import User
from app.schemas.speech import SpeechCapabilitiesResponse, TranscribeResponse
from app.schemas.speech_analyze import (
    SpeechAnalyzeRequest,
    SpeechAnalyzeResponse,
    SpeechAnalyzeSessionRequest,
    SpeechSessionResultsResponse,
)
from app.services.speech_analyzer_engine import SpeechAnalyzerEngineService
from app.services.speech_transcription import SpeechTranscriptionService

router = APIRouter(prefix="/speech", tags=["speech"])


@router.get("/capabilities", response_model=SpeechCapabilitiesResponse)
async def get_speech_capabilities(
    service: Annotated[SpeechTranscriptionService, Depends(get_speech_transcription_service)],
) -> SpeechCapabilitiesResponse:
    """Whisper availability and upload limits for the voice UI."""
    return service.capabilities()


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: Annotated[UploadFile, File(description="Recorded audio (webm, wav, mp3, etc.)")],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SpeechTranscriptionService, Depends(get_speech_transcription_service)],
    session_id: Annotated[UUID | None, Form()] = None,
    question_id: Annotated[UUID | None, Form()] = None,
    duration_seconds: Annotated[float | None, Form()] = None,
    browser_transcript: Annotated[
        str | None,
        Form(description="Client-side Web Speech API transcript when Whisper is unavailable"),
    ] = None,
    previous_transcript: Annotated[
        str | None,
        Form(description="Existing answer text to append after (preserves recording order)"),
    ] = None,
) -> TranscribeResponse:
    """Upload audio, transcribe via Whisper (or accept browser transcript), store metadata."""
    data = await file.read()
    return await service.transcribe_upload(
        current_user.id,
        filename=file.filename or "recording.webm",
        content_type=file.content_type,
        data=data,
        session_id=session_id,
        question_id=question_id,
        duration_seconds=duration_seconds,
        browser_transcript=browser_transcript,
        previous_transcript=previous_transcript,
    )


@router.post("/analyze", response_model=SpeechAnalyzeResponse)
async def analyze_speech(
    payload: SpeechAnalyzeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SpeechAnalyzerEngineService, Depends(get_speech_analyzer_engine_service)],
) -> SpeechAnalyzeResponse:
    """Analyze communication quality for a submitted interview answer."""
    return await service.analyze(current_user.id, payload)


@router.get("/analysis/{answer_id}", response_model=SpeechAnalyzeResponse)
async def get_speech_analysis(
    answer_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SpeechAnalyzerEngineService, Depends(get_speech_analyzer_engine_service)],
) -> SpeechAnalyzeResponse:
    """Return the latest speech analysis for an answer."""
    return await service.get_by_answer(current_user.id, answer_id)


@router.post("/analyze-session", response_model=SpeechSessionResultsResponse)
async def analyze_interview_session(
    payload: SpeechAnalyzeSessionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SpeechAnalyzerEngineService, Depends(get_speech_analyzer_engine_service)],
) -> SpeechSessionResultsResponse:
    """Analyze all submitted answers in an interview (post-interview results)."""
    return await service.analyze_session(current_user.id, payload)


@router.get("/session/{session_id}/results", response_model=SpeechSessionResultsResponse)
async def get_session_speech_results(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SpeechAnalyzerEngineService, Depends(get_speech_analyzer_engine_service)],
) -> SpeechSessionResultsResponse:
    """Return speech analysis for each answered question (runs analysis if missing)."""
    return await service.get_session_results(current_user.id, session_id)
