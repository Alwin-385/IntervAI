"""Interview creation and question generation endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.auth.dependencies import get_current_user
from app.core.dependencies import (
    get_interview_question_generator_service,
    get_interview_runtime_service,
    get_interview_session_service,
    get_interview_setup_service,
)
from app.core.exceptions import UnauthorizedError
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.interview_questions_gen import (
    GenerateQuestionsResponse,
    InterviewQuestionDetail,
)
from app.schemas.interview_runtime import (
    CompleteInterviewResponse,
    InterviewSessionStateResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.schemas.interview_setup import (
    MAX_QUESTIONS,
    MIN_QUESTIONS,
    PRESET_ROLES,
    InterviewCreateRequest,
    InterviewSetupResponse,
)
from app.services.interview_question_generator import InterviewQuestionGeneratorService
from app.services.interview_runtime import InterviewRuntimeService
from app.services.interview_session import InterviewSessionService
from app.services.interview_setup import InterviewSetupService

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _ensure_owner(session: InterviewSession, user: User) -> None:
    if session.user_id != user.id:
        raise UnauthorizedError("You do not have access to this interview session")


@router.get("/config")
async def get_interview_config() -> dict:
    """Wizard metadata (roles, categories, etc.) for the frontend."""
    return {
        "preset_roles": list(PRESET_ROLES),
        "categories": ["hr", "technical", "behavioral", "dsa", "resume_based", "mixed"],
        "difficulties": ["beginner", "intermediate", "advanced"],
        "answer_modes": ["text", "voice"],
        "question_count": {
            "min": MIN_QUESTIONS,
            "max": MAX_QUESTIONS,
            "presets": [5, 8, 10, 15, 20],
            "default": 8,
        },
    }


@router.post(
    "/create",
    response_model=InterviewSetupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_interview(
    payload: InterviewCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewSetupService, Depends(get_interview_setup_service)],
) -> InterviewSetupResponse:
    """Create an interview session from the setup wizard."""
    return await service.create_interview(current_user.id, payload)


@router.post(
    "/{session_id}/generate-questions",
    response_model=GenerateQuestionsResponse,
)
async def generate_interview_questions(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    generator: Annotated[
        InterviewQuestionGeneratorService,
        Depends(get_interview_question_generator_service),
    ],
    replace_existing: bool = Query(
        default=True,
        description="Replace prior questions for this session",
    ),
) -> GenerateQuestionsResponse:
    """Generate personalized interview questions (RAG + LangGraph + structured JSON)."""
    return await generator.generate_for_session(
        session_id,
        current_user.id,
        replace_existing=replace_existing,
    )


@router.get(
    "/{session_id}/questions",
    response_model=list[InterviewQuestionDetail],
)
async def list_interview_questions(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    generator: Annotated[
        InterviewQuestionGeneratorService,
        Depends(get_interview_question_generator_service),
    ],
) -> list[InterviewQuestionDetail]:
    """List generated questions for an interview session."""
    return await generator.list_questions(session_id, current_user.id)


@router.get(
    "/{session_id}/state",
    response_model=InterviewSessionStateResponse,
)
async def get_interview_session_state(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    runtime: Annotated[InterviewRuntimeService, Depends(get_interview_runtime_service)],
) -> InterviewSessionStateResponse:
    """Full mock-interview state: questions, saved answers, and progress."""
    return await runtime.get_session_state(session_id, current_user.id)


@router.post(
    "/{session_id}/submit-answer",
    response_model=SubmitAnswerResponse,
)
async def submit_interview_answer(
    session_id: UUID,
    payload: SubmitAnswerRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    runtime: Annotated[InterviewRuntimeService, Depends(get_interview_runtime_service)],
) -> SubmitAnswerResponse:
    """Save or autosave an answer; optionally advance to the next question."""
    return await runtime.submit_answer(session_id, current_user.id, payload)


@router.post(
    "/{session_id}/complete",
    response_model=CompleteInterviewResponse,
)
async def complete_interview(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    runtime: Annotated[InterviewRuntimeService, Depends(get_interview_runtime_service)],
) -> CompleteInterviewResponse:
    """Mark the mock interview session as completed."""
    return await runtime.complete_session(session_id, current_user.id)


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_interview(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session_service: Annotated[InterviewSessionService, Depends(get_interview_session_service)],
) -> MessageResponse:
    """Delete an interview session and its questions (cascade)."""
    entity = await session_service.repository.get_by_id_or_raise(
        session_id,
        resource="InterviewSession",
    )
    _ensure_owner(entity, current_user)
    await session_service.delete_session(session_id)
    return MessageResponse(message="Interview deleted successfully")
