"""Answer evaluation ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_answer import InterviewAnswer


class AnswerEvaluation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "answer_evaluations"
    __table_args__ = (
        UniqueConstraint("answer_id", name="uq_answer_evaluations_answer_id"),
        Index("ix_answer_evaluations_answer_id", "answer_id"),
    )

    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_answers.id", ondelete="CASCADE"),
        nullable=False,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    clarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    criteria_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    strengths: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    improvements: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)

    answer: Mapped[InterviewAnswer] = relationship(back_populates="evaluation")
