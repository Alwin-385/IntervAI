"""Resume ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ResumeStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.resume_analysis import ResumeAnalysis
    from app.models.user import User


class Resume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resumes"
    __table_args__ = (
        Index("ix_resumes_user_id", "user_id"),
        Index("ix_resumes_status", "status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False, default="application/pdf")
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ResumeStatus] = mapped_column(
        ENUM(ResumeStatus, name="resume_status", create_type=True),
        default=ResumeStatus.UPLOADED,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="resumes")
    analyses: Mapped[list[ResumeAnalysis]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
    )
    interview_sessions: Mapped[list[InterviewSession]] = relationship(
        back_populates="resume",
    )
