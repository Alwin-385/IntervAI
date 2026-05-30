"""Cross-entity queries for analytics (Phase 14)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.answer_evaluation import AnswerEvaluation
from app.models.interview_answer import InterviewAnswer
from app.models.interview_question import InterviewQuestion
from app.models.interview_session import InterviewSession
from app.models.speech_analysis import SpeechAnalysis


class AnalyticsQueryRepository:
    """Read-only aggregates across sessions owned by a user."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_answer_evaluations_for_user(
        self, user_id: UUID
    ) -> list[tuple[AnswerEvaluation, InterviewAnswer, InterviewQuestion, InterviewSession]]:
        stmt = (
            select(AnswerEvaluation, InterviewAnswer, InterviewQuestion, InterviewSession)
            .join(InterviewAnswer, AnswerEvaluation.answer_id == InterviewAnswer.id)
            .join(InterviewQuestion, InterviewAnswer.question_id == InterviewQuestion.id)
            .join(InterviewSession, InterviewQuestion.session_id == InterviewSession.id)
            .where(InterviewSession.user_id == user_id)
            .order_by(AnswerEvaluation.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.all())

    async def list_speech_analyses_for_user(
        self, user_id: UUID
    ) -> list[tuple[SpeechAnalysis, InterviewSession]]:
        stmt = (
            select(SpeechAnalysis, InterviewSession)
            .join(InterviewSession, SpeechAnalysis.session_id == InterviewSession.id)
            .where(InterviewSession.user_id == user_id)
            .order_by(SpeechAnalysis.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.all())
