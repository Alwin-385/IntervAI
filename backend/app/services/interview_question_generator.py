"""Orchestrate AI interview question generation (Phase 9)."""

from __future__ import annotations

import asyncio
import time
from uuid import UUID

from sqlalchemy import select

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.logging import get_logger
from app.models.enums import BackgroundJobType, InterviewCategory, InterviewSessionStatus
from app.models.interview_session import InterviewSession
from app.models.resume import Resume
from app.models.weak_area import WeakArea
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.schemas.interview_questions_gen import (
    GeneratedQuestion,
    GenerateQuestionsResponse,
    InterviewQuestionDetail,
    QuestionGenerationResult,
)
from app.services.interview_question_mapper import to_question_detail
from app.services.resume_text import resolve_resume_text

logger = get_logger(__name__)

GENERATION_TIMEOUT_SECONDS = 90


class InterviewQuestionGeneratorService:
    def __init__(
        self,
        session_repo: InterviewSessionRepository,
        question_repo: InterviewQuestionRepository,
    ) -> None:
        self.session_repo = session_repo
        self.question_repo = question_repo

    async def generate_for_session(
        self,
        session_id: UUID,
        user_id: UUID,
        *,
        replace_existing: bool = True,
        run_inline: bool = False,
    ) -> GenerateQuestionsResponse:
        session = await self._get_owned_session(session_id, user_id)

        if session.status == InterviewSessionStatus.CANCELLED:
            raise ValidationAppError("Cannot generate questions for a cancelled session.")

        if session.category == InterviewCategory.RESUME_BASED and not session.resume_id:
            raise ValidationAppError(
                "Resume-based interviews require a linked resume. Re-create the session with a resume.",
            )

        resume = await self._load_resume(session.resume_id) if session.resume_id else None
        weak_areas = await self._load_weak_areas(user_id)
        existing = await self.question_repo.list_by_session(session.id)

        if existing and not replace_existing:
            return self._response_from_existing(session, existing, weak_areas)

        if replace_existing and existing:
            existing_texts = [q.question_text for q in existing]
            await self.question_repo.delete_by_session(session.id)
            logger.info(
                "question_gen_replace",
                session_id=str(session_id),
                deleted=len(existing_texts),
            )
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

        settings = get_settings()
        if (
            not run_inline
            and settings.background_jobs_enabled
            and settings.background_jobs_async_question_generation
        ):
            from app.repositories.background_job import BackgroundJobRepository
            from app.services.background_job_dispatch import (
                BackgroundJobDispatcher,
                run_question_generation_job,
            )
            from app.services.background_job_service import BackgroundJobService

            job_repo = BackgroundJobRepository(self.session_repo.session)
            dispatcher = BackgroundJobDispatcher(BackgroundJobService(job_repo), job_repo)
            job = await dispatcher.dispatch(
                user_id,
                BackgroundJobType.QUESTION_GENERATION,
                resource_type="interview_session",
                resource_id=session.id,
                payload={
                    "session_id": str(session.id),
                    "user_id": str(user_id),
                    "replace_existing": replace_existing,
                },
                thread_runner=run_question_generation_job,
            )
            return GenerateQuestionsResponse(
                session_id=session.id,
                count=0,
                questions=[],
                generation=QuestionGenerationResult(
                    session_id=str(session.id),
                    target_role=session.target_role,
                    session_category=session.category,
                    questions=[],
                    weak_areas_targeted=weak_areas[:6],
                ),
                job_id=str(job.id),
                status="processing",
            )

        target_count = session.question_count
        logger.info("question_gen_start", session_id=str(session_id), target_count=target_count)
        try:
            result_state = await asyncio.wait_for(
                asyncio.to_thread(_run_question_generator, initial),
                timeout=GENERATION_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            raise ValidationAppError(
                f"Question generation timed out after {GENERATION_TIMEOUT_SECONDS}s.",
            ) from exc

        raw_questions = result_state.get("questions") or []
        if not raw_questions:
            raise ValidationAppError("Question generator produced no questions.")

        generated = [GeneratedQuestion.model_validate(q) for q in raw_questions]
        rows = []
        for g in generated:
            rows.append(
                {
                    "session_id": session.id,
                    "question_text": g.question_text,
                    "question_type": g.question_type,
                    "order_index": g.order_index,
                    "time_limit_seconds": g.time_limit_seconds,
                    "question_metadata": {
                        "category": g.category.value,
                        "difficulty": g.difficulty.value,
                        "expected_answer_points": g.expected_answer_points,
                        "evaluation_criteria": g.evaluation_criteria,
                        "source_hint": g.source_hint,
                    },
                },
            )
        created = await self.question_repo.bulk_create(rows)
        questions_detail = [to_question_detail(q) for q in created]
        gen = QuestionGenerationResult(
            session_id=str(session.id),
            target_role=session.target_role,
            session_category=session.category,
            questions=generated,
            rag_chunks_used=len(result_state.get("rag_snippets") or []),
            weak_areas_targeted=weak_areas[:6],
        )
        return GenerateQuestionsResponse(
            session_id=session.id,
            count=len(questions_detail),
            questions=questions_detail,
            generation=gen,
            status="completed",
        )

    async def list_questions(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> list[InterviewQuestionDetail]:
        await self._get_owned_session(session_id, user_id)
        rows = await self.question_repo.list_by_session(session_id)
        return [to_question_detail(q) for q in rows]

    async def _get_owned_session(self, session_id: UUID, user_id: UUID) -> InterviewSession:
        session = await self.session_repo.get_by_id_or_raise(
            session_id,
            resource="InterviewSession",
        )
        if session.user_id != user_id:
            raise NotFoundError("InterviewSession", str(session_id))
        return session

    async def _load_resume(self, resume_id: UUID) -> Resume | None:
        result = await self.session_repo.session.execute(
            select(Resume).where(Resume.id == resume_id),
        )
        return result.scalar_one_or_none()

    async def _load_weak_areas(self, user_id: UUID) -> list[str]:
        result = await self.session_repo.session.execute(
            select(WeakArea.area_name).where(WeakArea.user_id == user_id).limit(12),
        )
        return [row[0] for row in result.all() if row[0]]

    def _response_from_existing(
        self,
        session: InterviewSession,
        existing: list,
        weak_areas: list[str],
    ) -> GenerateQuestionsResponse:
        questions_detail = [to_question_detail(q) for q in existing]
        gen = QuestionGenerationResult(
            session_id=str(session.id),
            target_role=session.target_role,
            session_category=session.category,
            questions=[],
            weak_areas_targeted=weak_areas[:6],
        )
        return GenerateQuestionsResponse(
            session_id=session.id,
            count=len(questions_detail),
            questions=questions_detail,
            generation=gen,
            status="completed",
        )


def _run_question_generator(initial: dict) -> dict:
    from app.agents.question_generator.graph import run_question_generator as run_qg_pipeline

    settings = get_settings()
    if settings.orchestration_enabled:
        from app.orchestration import AgentName, get_orchestration_service

        run = get_orchestration_service().run_agent(
            AgentName.QUESTION_GENERATION,
            initial,
        )
        if run.status == "completed":
            return run.output
    return run_qg_pipeline(initial)
