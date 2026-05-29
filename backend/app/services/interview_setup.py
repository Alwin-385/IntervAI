"""Interview setup orchestration (Phase 8 — wizard creation flow)."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.enums import (
    AnswerMode,
    InterviewCategory,
    InterviewDifficulty,
    InterviewSessionStatus,
)
from app.models.interview_session import InterviewSession
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.resume import ResumeRepository
from app.schemas.interview_setup import (
    InterviewCreateRequest,
    InterviewSetupResponse,
    default_title,
    ensure_resume_for_category,
)


class InterviewSetupService:
    def __init__(
        self,
        session_repo: InterviewSessionRepository,
        resume_repo: ResumeRepository,
    ) -> None:
        self.session_repo = session_repo
        self.resume_repo = resume_repo

    async def create_interview(
        self,
        user_id: UUID,
        payload: InterviewCreateRequest,
    ) -> InterviewSetupResponse:
        try:
            ensure_resume_for_category(payload.category, payload.resume_id)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        if payload.resume_id is not None:
            resume = await self.resume_repo.get_by_id(payload.resume_id)
            if resume is None:
                raise NotFoundError("Resume", str(payload.resume_id))
            if resume.user_id != user_id:
                raise NotFoundError("Resume", str(payload.resume_id))

        title = (payload.title or default_title(
            payload.target_role,
            payload.category,
            payload.difficulty,
        )).strip()

        data = {
            "user_id": user_id,
            "resume_id": payload.resume_id,
            "title": title,
            "target_role": payload.target_role,
            "status": InterviewSessionStatus.SCHEDULED,
            "category": payload.category,
            "difficulty": payload.difficulty,
            "answer_mode": payload.answer_mode,
            "question_count": payload.question_count,
            "notes": payload.notes,
        }
        session = await self.session_repo.create(data)
        return _to_setup_response(session)


def _to_setup_response(session: InterviewSession) -> InterviewSetupResponse:
    return InterviewSetupResponse.model_validate(session)
