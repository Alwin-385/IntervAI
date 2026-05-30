"""Learning roadmap ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RoadmapStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.pg_enum import pg_enum

if TYPE_CHECKING:
    from app.models.user import User


class Roadmap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roadmaps"
    __table_args__ = (
        Index("ix_roadmaps_user_id", "user_id"),
        Index("ix_roadmaps_status", "status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RoadmapStatus] = mapped_column(
        pg_enum(RoadmapStatus, name="roadmap_status", create_type=True),
        default=RoadmapStatus.DRAFT,
        nullable=False,
    )
    target_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    milestones: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)

    user: Mapped[User] = relationship(back_populates="roadmaps")
