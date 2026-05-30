"""Weak area ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import WeakAreaSeverity
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.pg_enum import pg_enum

if TYPE_CHECKING:
    from app.models.resume_analysis import ResumeAnalysis
    from app.models.user import User


class WeakArea(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "weak_areas"
    __table_args__ = (
        Index("ix_weak_areas_user_id", "user_id"),
        Index("ix_weak_areas_resume_analysis_id", "resume_analysis_id"),
        Index("ix_weak_areas_severity", "severity"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_analysis_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_analyses.id", ondelete="SET NULL"),
        nullable=True,
    )
    area_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[WeakAreaSeverity] = mapped_column(
        pg_enum(WeakAreaSeverity, name="weak_area_severity", create_type=True),
        default=WeakAreaSeverity.MEDIUM,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped[User] = relationship(back_populates="weak_areas")
    resume_analysis: Mapped[ResumeAnalysis | None] = relationship(
        back_populates="weak_areas",
    )
