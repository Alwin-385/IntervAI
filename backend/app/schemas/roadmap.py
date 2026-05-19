"""Roadmap API schemas."""

from typing import Any
from uuid import UUID

from pydantic import Field

from app.models.enums import RoadmapStatus
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class RoadmapCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: RoadmapStatus = RoadmapStatus.DRAFT
    target_role: str | None = None
    milestones: list[Any] | None = None


class RoadmapUpdate(SchemaBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: RoadmapStatus | None = None
    target_role: str | None = None
    milestones: list[Any] | None = None


class RoadmapResponse(UUIDSchema, TimestampSchema):
    user_id: UUID
    title: str
    description: str | None
    status: RoadmapStatus
    target_role: str | None
    milestones: list[Any] | None
