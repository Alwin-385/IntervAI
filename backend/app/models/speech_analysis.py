"""Speech analysis ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_answer import InterviewAnswer
    from app.models.interview_session import InterviewSession


class SpeechAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "speech_analyses"
    __table_args__ = (
        CheckConstraint(
            "(answer_id IS NOT NULL) OR (session_id IS NOT NULL)",
            name="ck_speech_analyses_reference",
        ),
        Index("ix_speech_analyses_answer_id", "answer_id"),
        Index("ix_speech_analyses_session_id", "session_id"),
    )

    answer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        nullable=True,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=True,
    )
    words_per_minute: Mapped[float | None] = mapped_column(Float, nullable=True)
    filler_word_count: Mapped[int | None] = mapped_column(nullable=True)
    clarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    answer: Mapped[InterviewAnswer | None] = relationship(back_populates="speech_analyses")
    session: Mapped[InterviewSession | None] = relationship(back_populates="speech_analyses")
