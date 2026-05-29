"""Background worker entry for question generation."""

from __future__ import annotations

import asyncio
from uuid import UUID

from app.services.background_job_sync import sync_job_update_progress


def execute_question_generation_sync(payload: dict) -> dict:
    from app.core.database import db_manager
    from app.repositories.interview_question import InterviewQuestionRepository
    from app.repositories.interview_session import InterviewSessionRepository
    from app.services.interview_question_generator import InterviewQuestionGeneratorService

    job_id = payload.get("job_id")
    session_id = UUID(payload["session_id"])
    user_id = UUID(payload["user_id"])
    replace_existing = bool(payload.get("replace_existing", True))

    if job_id:
        sync_job_update_progress(job_id, percent=25, message="Loading session…")

    async def _run():
        async with db_manager.session_factory() as session:
            session_repo = InterviewSessionRepository(session)
            question_repo = InterviewQuestionRepository(session)
            svc = InterviewQuestionGeneratorService(session_repo, question_repo)
            return await svc.generate_for_session(
                session_id,
                user_id,
                replace_existing=replace_existing,
                run_inline=True,
            )

    loop = asyncio.new_event_loop()
    try:
        if job_id:
            sync_job_update_progress(job_id, percent=50, message="Generating questions…")
        response = loop.run_until_complete(_run())
    finally:
        loop.close()

    return {
        "session_id": str(response.session_id),
        "count": response.count,
        "status": "completed",
    }
