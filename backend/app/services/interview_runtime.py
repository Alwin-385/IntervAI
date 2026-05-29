"""Mock interview session runtime: answers, progress, completion (Phase 10)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationAppError
from app.models.enums import InterviewSessionStatus
from app.models.interview_answer import InterviewAnswer
from app.models.interview_question import InterviewQuestion
from app.models.interview_session import InterviewSession
from app.repositories.interview_answer import InterviewAnswerRepository
from app.repositories.interview_question import InterviewQuestionRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.schemas.interview_answer import InterviewAnswerResponse
from app.schemas.interview_runtime import (
    CompleteInterviewResponse,
    InterviewProgress,
    InterviewSessionStateResponse,
    QuestionAnswerState,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.interview_question_mapper import to_question_detail

SECONDS_PER_QUESTION = 120


def _word_count(text: str | None) -> int | None:
    if not text or not text.strip():
        return None
    return len(text.split())


def _has_answer_content(answer: InterviewAnswer) -> bool:
    if (answer.answer_text or "").strip():
        return True
    return bool(answer.audio_storage_path)


def _build_progress(
    session: InterviewSession,
    answered_count: int,
    *,
    total_questions: int,
) -> InterviewProgress:
    total = max(total_questions, 1)
    current = min(session.current_question_index, max(total - 1, 0))
    percent = round((answered_count / total) * 100, 1) if total else 0.0
    return InterviewProgress(
        total_questions=total,
        answered_count=answered_count,
        current_question_index=current,
        percent_complete=min(percent, 100.0),
    )


class InterviewRuntimeService:
    def __init__(
        self,
        session_repo: InterviewSessionRepository,
        question_repo: InterviewQuestionRepository,
        answer_repo: InterviewAnswerRepository,
    ) -> None:
        self.session_repo = session_repo
        self.question_repo = question_repo
        self.answer_repo = answer_repo

    async def _get_owned_session(self, session_id: UUID, user_id: UUID) -> InterviewSession:
        session = await self.session_repo.get_by_id_or_raise(
            session_id,
            resource="InterviewSession",
        )
        if session.user_id != user_id:
            raise UnauthorizedError("You do not have access to this interview session")
        return session

    async def _load_questions(self, session_id: UUID) -> list[InterviewQuestion]:
        return await self.question_repo.list_by_session(session_id)

    def _answers_by_question(
        self,
        answers: list[InterviewAnswer],
    ) -> dict[UUID, InterviewAnswer]:
        latest: dict[UUID, InterviewAnswer] = {}
        for answer in answers:
            existing = latest.get(answer.question_id)
            if existing is None or answer.updated_at >= existing.updated_at:
                latest[answer.question_id] = answer
        return latest

    async def get_session_state(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> InterviewSessionStateResponse:
        session = await self._get_owned_session(session_id, user_id)
        questions = await self._load_questions(session_id)
        if not questions:
            raise ValidationAppError(
                "No questions found for this session. Generate questions before starting.",
            )

        answers = self._answers_by_question(await self.answer_repo.list_by_session(session_id))
        answered_count = sum(
            1
            for q in questions
            if answers.get(q.id) and _has_answer_content(answers[q.id])
        )

        states = [
            QuestionAnswerState(
                question=to_question_detail(q),
                answer=(
                    InterviewAnswerResponse.model_validate(answers[q.id])
                    if q.id in answers
                    else None
                ),
            )
            for q in questions
        ]

        total_q = len(questions)
        return InterviewSessionStateResponse(
            session_id=session.id,
            title=session.title,
            target_role=session.target_role,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            progress=_build_progress(session, answered_count, total_questions=total_q),
            questions=states,
            seconds_per_question=SECONDS_PER_QUESTION,
            total_duration_seconds=total_q * SECONDS_PER_QUESTION,
            answer_mode=session.answer_mode,
        )

    async def submit_answer(
        self,
        session_id: UUID,
        user_id: UUID,
        payload: SubmitAnswerRequest,
    ) -> SubmitAnswerResponse:
        session = await self._get_owned_session(session_id, user_id)

        if session.status == InterviewSessionStatus.COMPLETED:
            raise ValidationAppError("This interview is already completed.")
        if session.status == InterviewSessionStatus.CANCELLED:
            raise ValidationAppError("This interview was cancelled.")

        question = await self.question_repo.get_by_id(payload.question_id)
        if question is None or question.session_id != session.id:
            raise NotFoundError("InterviewQuestion", str(payload.question_id))

        questions = await self._load_questions(session_id)
        if not questions:
            raise ValidationAppError("No questions available for this session.")

        now = datetime.now(UTC)
        if session.status == InterviewSessionStatus.SCHEDULED:
            session.status = InterviewSessionStatus.IN_PROGRESS
            session.started_at = session.started_at or now

        text = (payload.answer_text or "").strip()
        word_count = _word_count(text)
        answer_data = {
            "answer_text": text or None,
            "audio_storage_path": payload.audio_storage_path,
            "duration_seconds": payload.duration_seconds,
            "word_count": word_count,
        }

        existing = await self.answer_repo.get_latest_by_question(question.id)
        if existing:
            answer = await self.answer_repo.update(existing, answer_data)
        else:
            answer = await self.answer_repo.create(
                {"question_id": question.id, **answer_data},
            )

        if payload.resume_question_index is not None:
            session.current_question_index = min(
                payload.resume_question_index,
                max(len(questions) - 1, 0),
            )
        elif payload.advance and not payload.autosave:
            session.current_question_index = min(
                question.order_index + 1,
                max(len(questions) - 1, 0),
            )

        await self.session_repo.update(
            session,
            {
                "status": session.status,
                "started_at": session.started_at,
                "current_question_index": session.current_question_index,
            },
        )

        all_answers = self._answers_by_question(await self.answer_repo.list_by_session(session_id))
        answered_count = sum(
            1
            for q in questions
            if all_answers.get(q.id) and _has_answer_content(all_answers[q.id])
        )

        return SubmitAnswerResponse(
            answer=InterviewAnswerResponse.model_validate(answer),
            progress=_build_progress(
                session,
                answered_count,
                total_questions=len(questions),
            ),
            saved_at=answer.updated_at,
        )

    async def complete_session(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> CompleteInterviewResponse:
        session = await self._get_owned_session(session_id, user_id)

        if session.status == InterviewSessionStatus.COMPLETED:
            raise ValidationAppError("This interview is already completed.")
        if session.status == InterviewSessionStatus.CANCELLED:
            raise ValidationAppError("This interview was cancelled.")

        questions = await self._load_questions(session_id)
        if not questions:
            raise ValidationAppError("Cannot complete an interview with no questions.")

        now = datetime.now(UTC)
        session.status = InterviewSessionStatus.COMPLETED
        session.completed_at = now
        if session.started_at is None:
            session.started_at = now

        total_time: float | None = None
        if session.started_at:
            total_time = (now - session.started_at).total_seconds()

        session.current_question_index = len(questions)
        await self.session_repo.update(
            session,
            {
                "status": session.status,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
                "current_question_index": session.current_question_index,
            },
        )

        all_answers = self._answers_by_question(await self.answer_repo.list_by_session(session_id))
        answered_count = sum(
            1
            for q in questions
            if all_answers.get(q.id) and _has_answer_content(all_answers[q.id])
        )

        return CompleteInterviewResponse(
            session_id=session.id,
            status=session.status,
            completed_at=now,
            progress=_build_progress(
                session,
                answered_count,
                total_questions=len(questions),
            ),
            total_time_seconds=total_time,
        )
