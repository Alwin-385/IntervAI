"""Phase 15 — Roadmap engine schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema

RoadmapPhaseKind = Literal["immediate", "short_term", "advanced"]
RoadmapItemPriority = Literal["high", "medium", "low"]


class RoadmapItem(SchemaBase):
    id: str
    title: str
    description: str
    priority: RoadmapItemPriority
    phase: RoadmapPhaseKind
    category: str
    estimated_time: str
    practice_recommendation: str
    resources: list[str] = Field(default_factory=list)
    weak_area_kind: str | None = None
    completed: bool = False
    completed_at: datetime | None = None


class RoadmapPhase(SchemaBase):
    phase: RoadmapPhaseKind
    title: str
    subtitle: str
    estimated_duration: str
    items: list[RoadmapItem]


class GeneratedRoadmapResponse(UUIDSchema, TimestampSchema):
    title: str
    description: str | None
    target_role: str | None
    status: str
    phases: list[RoadmapPhase]
    summary: str
    total_items: int
    weak_areas_addressed: list[str]
    generated_at: datetime
    job_id: str | None = None


class GenerateRoadmapRequest(SchemaBase):
    target_role: str | None = None
    force_regenerate: bool = False


class RoadmapItemUpdateRequest(SchemaBase):
    completed: bool
