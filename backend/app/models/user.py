"""User ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.resume import Resume
    from app.models.roadmap import Roadmap
    from app.models.weak_area import WeakArea


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("clerk_id", name="uq_users_clerk_id"),
        Index("ix_users_email", "email"),
        Index("ix_users_clerk_id", "clerk_id"),
        Index("ix_users_is_active", "is_active"),
    )

    clerk_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="user_role", create_type=True),
        default=UserRole.CANDIDATE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    resumes: Mapped[list[Resume]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    interview_sessions: Mapped[list[InterviewSession]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    weak_areas: Mapped[list[WeakArea]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    roadmaps: Mapped[list[Roadmap]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
