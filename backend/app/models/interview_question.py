"""Interview question ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import QuestionType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_answer import InterviewAnswer
    from app.models.interview_session import InterviewSession


class InterviewQuestion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "interview_questions"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "order_index",
            name="uq_interview_questions_session_order",
        ),
        Index("ix_interview_questions_session_id", "session_id"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        ENUM(QuestionType, name="question_type", create_type=True),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session: Mapped[InterviewSession] = relationship(back_populates="questions")
    answers: Mapped[list[InterviewAnswer]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )
