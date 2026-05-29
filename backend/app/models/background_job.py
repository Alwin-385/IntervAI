"""Background job tracking for async Celery / thread workers (Phase 18)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BackgroundJobStatus, BackgroundJobType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.pg_enum import pg_enum

if TYPE_CHECKING:
    from app.models.user import User


class BackgroundJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "background_jobs"
    __table_args__ = (
        Index("ix_background_jobs_user_id", "user_id"),
        Index("ix_background_jobs_status", "status"),
        Index("ix_background_jobs_job_type", "job_type"),
        Index("ix_background_jobs_resource", "resource_type", "resource_id"),
        Index("ix_background_jobs_celery_task_id", "celery_task_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_type: Mapped[BackgroundJobType] = mapped_column(
        pg_enum(BackgroundJobType, name="background_job_type", create_type=True),
        nullable=False,
    )
    status: Mapped[BackgroundJobStatus] = mapped_column(
        pg_enum(BackgroundJobStatus, name="background_job_status", create_type=True),
        default=BackgroundJobStatus.PENDING,
        nullable=False,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress_step: Mapped[str | None] = mapped_column(String(64), nullable=True)
    progress_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship()
