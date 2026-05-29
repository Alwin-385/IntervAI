"""Background worker for session answer evaluation."""

from __future__ import annotations

import asyncio
from uuid import UUID

from app.services.background_job_sync import sync_job_update_progress


def execute_session_evaluation_sync(payload: dict) -> dict:
    from app.core.database import db_manager
    from app.repositories.answer_evaluation import AnswerEvaluationRepository
    from app.repositories.interview_answer import InterviewAnswerRepository
    from app.repositories.interview_question import InterviewQuestionRepository
    from app.repositories.interview_session import InterviewSessionRepository
    from app.repositories.speech_analysis import SpeechAnalysisRepository
    from app.schemas.answer_evaluator import EvaluateSessionRequest
    from app.services.answer_evaluator_engine import AnswerEvaluatorEngineService

    job_id = payload.get("job_id")
    session_id = UUID(payload["session_id"])
    user_id = UUID(payload["user_id"])
    force = bool(payload.get("force", False))

    async def _run():
        async with db_manager.session_factory() as session:
            svc = AnswerEvaluatorEngineService(
                InterviewSessionRepository(session),
                InterviewQuestionRepository(session),
                InterviewAnswerRepository(session),
                AnswerEvaluationRepository(session),
                SpeechAnalysisRepository(session),
            )
            return await svc.evaluate_session(
                user_id,
                EvaluateSessionRequest(session_id=session_id, force=force),
            )

    loop = asyncio.new_event_loop()
    try:
        if job_id:
            sync_job_update_progress(job_id, percent=30, message="Evaluating answers…")
        result = loop.run_until_complete(_run())
    finally:
        loop.close()

    return {
        "session_id": str(result.session_id),
        "evaluated_count": result.summary.evaluated_count,
        "status": "completed",
    }
