"""Resume analysis ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AnalysisStatus
from app.models.pg_enum import pg_enum
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.weak_area import WeakArea


class ResumeAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resume_analyses"
    __table_args__ = (
        Index("ix_resume_analyses_resume_id", "resume_id"),
        Index("ix_resume_analyses_status", "status"),
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[AnalysisStatus] = mapped_column(
        pg_enum(AnalysisStatus, name="analysis_status", create_type=True),
        default=AnalysisStatus.PENDING,
        nullable=False,
    )
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_extracted: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    gaps_identified: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    raw_analysis: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    resume: Mapped[Resume] = relationship(back_populates="analyses")
    weak_areas: Mapped[list[WeakArea]] = relationship(
        back_populates="resume_analysis",
        cascade="all, delete-orphan",
    )
