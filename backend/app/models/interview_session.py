"""Interview session ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import (
    AnswerMode,
    InterviewCategory,
    InterviewDifficulty,
    InterviewSessionStatus,
)
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.pg_enum import pg_enum

if TYPE_CHECKING:
    from app.models.interview_question import InterviewQuestion
    from app.models.resume import Resume
    from app.models.speech_analysis import SpeechAnalysis
    from app.models.user import User


class InterviewSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "interview_sessions"
    __table_args__ = (
        Index("ix_interview_sessions_user_id", "user_id"),
        Index("ix_interview_sessions_status", "status"),
        Index("ix_interview_sessions_resume_id", "resume_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[InterviewSessionStatus] = mapped_column(
        pg_enum(InterviewSessionStatus, name="interview_session_status", create_type=True),
        default=InterviewSessionStatus.SCHEDULED,
        nullable=False,
    )
    category: Mapped[InterviewCategory] = mapped_column(
        pg_enum(InterviewCategory, name="interview_category", create_type=True),
        default=InterviewCategory.MIXED,
        nullable=False,
    )
    difficulty: Mapped[InterviewDifficulty] = mapped_column(
        pg_enum(InterviewDifficulty, name="interview_difficulty", create_type=True),
        default=InterviewDifficulty.INTERMEDIATE,
        nullable=False,
    )
    answer_mode: Mapped[AnswerMode] = mapped_column(
        pg_enum(AnswerMode, name="answer_mode", create_type=True),
        default=AnswerMode.TEXT,
        nullable=False,
    )
    question_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_question_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[User] = relationship(back_populates="interview_sessions")
    resume: Mapped[Resume | None] = relationship(back_populates="interview_sessions")
    questions: Mapped[list[InterviewQuestion]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.order_index",
    )
    speech_analyses: Mapped[list[SpeechAnalysis]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
