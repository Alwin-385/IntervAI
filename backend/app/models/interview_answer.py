"""Interview answer ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.answer_evaluation import AnswerEvaluation
    from app.models.interview_question import InterviewQuestion
    from app.models.speech_analysis import SpeechAnalysis


class InterviewAnswer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "interview_answers"
    __table_args__ = (Index("ix_interview_answers_question_id", "question_id"),)

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    question: Mapped[InterviewQuestion] = relationship(back_populates="answers")
    evaluation: Mapped[AnswerEvaluation | None] = relationship(
        back_populates="answer",
        uselist=False,
        cascade="all, delete-orphan",
    )
    speech_analyses: Mapped[list[SpeechAnalysis]] = relationship(
        back_populates="answer",
        cascade="all, delete-orphan",
    )
