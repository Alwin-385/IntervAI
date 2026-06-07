"""Background worker entry for question generation."""

from __future__ import annotations

import time
from uuid import UUID

from sqlalchemy import delete, select

from app.core.sync_database import sync_db_session
from app.models.enums import InterviewCategory, InterviewSessionStatus
from app.models.interview_question import InterviewQuestion
from app.models.interview_session import InterviewSession
from app.models.resume import Resume
from app.models.weak_area import WeakArea
from app.schemas.interview_questions_gen import GeneratedQuestion
from app.services.background_job_sync import sync_job_update_progress
from app.services.interview_question_generator import _run_question_generator
from app.services.resume_text import resolve_resume_text


def execute_question_generation_sync(payload: dict) -> dict:
    """Run question generation in a background thread using sync DB sessions."""
    job_id = payload.get("job_id")
    session_id = UUID(payload["session_id"])
    user_id = UUID(payload["user_id"])
    replace_existing = bool(payload.get("replace_existing", True))

    if job_id:
        sync_job_update_progress(job_id, percent=25, message="Loading session…")

    with sync_db_session() as db:
        session = db.get(InterviewSession, session_id)
        if session is None or session.user_id != user_id:
            raise ValueError("Interview session not found")
        if session.status == InterviewSessionStatus.CANCELLED:
            raise ValueError("Cannot generate questions for a cancelled session.")
        if session.category == InterviewCategory.RESUME_BASED and not session.resume_id:
            raise ValueError("Resume-based interviews require a linked resume.")

        resume = db.get(Resume, session.resume_id) if session.resume_id else None
        weak_areas = [
            row[0]
            for row in db.execute(
                select(WeakArea.area_name).where(WeakArea.user_id == user_id).limit(12),
            ).all()
            if row[0]
        ]
        existing = list(
            db.scalars(
                select(InterviewQuestion)
                .where(InterviewQuestion.session_id == session.id)
                .order_by(InterviewQuestion.order_index),
            ).all(),
        )

        if existing and not replace_existing:
            return {
                "session_id": str(session_id),
                "count": len(existing),
                "status": "completed",
            }

        if replace_existing and existing:
            db.execute(
                delete(InterviewQuestion).where(InterviewQuestion.session_id == session.id),
            )
            db.flush()
            existing_texts = [q.question_text for q in existing]
        else:
            existing_texts = [q.question_text for q in existing]

        initial = {
            "session_id": str(session.id),
            "target_role": session.target_role,
            "session_category": session.category.value,
            "difficulty": session.difficulty.value,
            "question_count": session.question_count,
            "resume_id": str(session.resume_id) if session.resume_id else None,
            "user_id": str(user_id),
            "cleaned_text": resolve_resume_text(resume) if resume else "",
            "extracted_data": (resume.extracted_data or {}) if resume else {},
            "weak_areas": weak_areas,
            "existing_questions": existing_texts,
            "generation_nonce": str(time.time_ns()),
        }

    if job_id:
        sync_job_update_progress(job_id, percent=50, message="Generating questions…")

    result_state = _run_question_generator(initial)
    raw_questions = result_state.get("questions") or []
    if not raw_questions:
        raise ValueError("Question generator produced no questions.")

    generated = [GeneratedQuestion.model_validate(q) for q in raw_questions]

    with sync_db_session() as db:
        db.add_all(
            [
                InterviewQuestion(
                    session_id=session_id,
                    question_text=g.question_text,
                    question_type=g.question_type,
                    order_index=g.order_index,
                    time_limit_seconds=g.time_limit_seconds,
                    question_metadata={
                        "category": g.category.value,
                        "difficulty": g.difficulty.value,
                        "expected_answer_points": g.expected_answer_points,
                        "evaluation_criteria": g.evaluation_criteria,
                        "source_hint": g.source_hint,
                    },
                )
                for g in generated
            ],
        )
        db.flush()

    return {
        "session_id": str(session_id),
        "count": len(generated),
        "status": "completed",
    }
