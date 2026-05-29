"""Weak-area analytics API schemas (Phase 14)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.enums import WeakAreaSeverity
from app.schemas.common import SchemaBase

PriorityLevel = Literal["high", "medium", "low"]
TrendDirection = Literal["improving", "declining", "stable", "insufficient_data"]


class WeakAreaTrendPoint(SchemaBase):
    period_label: str
    hit_count: int
    opportunity_count: int
    rate: float


class DetectedWeakAreaItem(SchemaBase):
    kind: str
    area_name: str
    category: str
    priority: PriorityLevel
    severity: WeakAreaSeverity
    frequency: int = Field(description="Times this weakness appeared in analyzed history")
    total_opportunities: int
    frequency_rate: float = Field(ge=0, le=1, description="frequency / opportunities")
    frequency_label: str = Field(description="Human-readable e.g. '5 of 12 responses'")
    trend: TrendDirection
    trend_delta: float
    description: str
    improvement_suggestions: list[str]
    practice_recommendations: list[str]
    evidence: list[str] = Field(default_factory=list)
    last_seen_at: datetime | None = None


class WeakAreaProgressSummary(SchemaBase):
    interviews_analyzed: int
    answers_analyzed: int
    speech_analyses_analyzed: int
    overall_improvement_score: float = Field(
        ge=0,
        le=100,
        description="Higher = fewer high-priority weak areas recently",
    )
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int


class WeakAreasAnalyticsResponse(SchemaBase):
    version: str = "phase14"
    generated_at: datetime
    weak_areas: list[DetectedWeakAreaItem]
    summary: WeakAreaProgressSummary
    personalized_recommendations: list[str] = Field(default_factory=list)
    trend_overview: list[WeakAreaTrendPoint] = Field(default_factory=list)
