"""Answer evaluation endpoints (Phase 13)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.dependencies import (
    get_answer_evaluator_engine_service,
    get_background_job_dispatcher,
)
from app.models.enums import BackgroundJobType
from app.schemas.answer_evaluator import SessionEvaluationSummary
from app.models.user import User
from app.schemas.answer_evaluator import (
    AnswerEvaluationDetailResponse,
    EvaluateAnswerRequest,
    EvaluateSessionRequest,
    SessionAnswerEvaluationResponse,
)
from app.services.answer_evaluator_engine import AnswerEvaluatorEngineService
from app.services.background_job_dispatch import BackgroundJobDispatcher

router = APIRouter(prefix="/answers", tags=["answers"])


@router.post("/{answer_id}/evaluate", response_model=AnswerEvaluationDetailResponse)
async def evaluate_answer(
    answer_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnswerEvaluatorEngineService, Depends(get_answer_evaluator_engine_service)],
    body: EvaluateAnswerRequest | None = None,
) -> AnswerEvaluationDetailResponse:
    """Evaluate a single interview answer (content quality, STAR/DSA feedback)."""
    force = body.force if body else False
    return await service.evaluate(current_user.id, answer_id, force=force)


@router.get("/{answer_id}/evaluation", response_model=AnswerEvaluationDetailResponse)
async def get_answer_evaluation(
    answer_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnswerEvaluatorEngineService, Depends(get_answer_evaluator_engine_service)],
) -> AnswerEvaluationDetailResponse:
    """Return persisted evaluation for an answer."""
    return await service.get_evaluation(current_user.id, answer_id)


@router.post("/session/{session_id}/evaluate", response_model=SessionAnswerEvaluationResponse)
async def evaluate_interview_session_answers(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnswerEvaluatorEngineService, Depends(get_answer_evaluator_engine_service)],
    dispatcher: Annotated[BackgroundJobDispatcher, Depends(get_background_job_dispatcher)],
    body: EvaluateSessionRequest | None = None,
) -> SessionAnswerEvaluationResponse:
    """Evaluate all submitted answers in a session."""
    force = body.force if body else False
    settings = get_settings()
    if settings.background_jobs_enabled and settings.background_jobs_async_answer_evaluation:
        from app.services.background_job_dispatch import run_answer_evaluation_job

        job = await dispatcher.dispatch(
            current_user.id,
            BackgroundJobType.ANSWER_EVALUATION,
            resource_type="interview_session",
            resource_id=session_id,
            payload={
                "session_id": str(session_id),
                "user_id": str(current_user.id),
                "force": force,
            },
            thread_runner=run_answer_evaluation_job,
        )
        empty_summary = SessionEvaluationSummary()
        return SessionAnswerEvaluationResponse(
            session_id=session_id,
            questions=[],
            summary=empty_summary,
            job_id=str(job.id),
            status="processing",
        )
    return await service.evaluate_session(
        current_user.id,
        EvaluateSessionRequest(session_id=session_id, force=force),
    )


@router.get("/session/{session_id}/evaluation", response_model=SessionAnswerEvaluationResponse)
async def get_session_answer_evaluations(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AnswerEvaluatorEngineService, Depends(get_answer_evaluator_engine_service)],
) -> SessionAnswerEvaluationResponse:
    """Return answer evaluations per question (runs evaluation if missing)."""
    return await service.get_session_results(current_user.id, session_id)
