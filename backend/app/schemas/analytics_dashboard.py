"""Phase 16 — Analytics dashboard API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase

TrendDirection = Literal["improving", "declining", "stable", "insufficient_data"]


class AnalyticsFiltersApplied(SchemaBase):
    target_role: str | None = None
    category: str | None = None
    days: int | None = None


class AnalyticsSummary(SchemaBase):
    total_interviews: int = 0
    completed_interviews: int = 0
    total_answers_evaluated: int = 0
    average_score: float | None = None
    average_communication: float | None = None
    average_confidence: float | None = None
    average_technical: float | None = None
    improvement_score: float | None = Field(
        default=None,
        description="0–100 composite improvement index",
    )
    score_trend: TrendDirection = "insufficient_data"
    score_trend_delta: float = 0.0


class ScoreTrendPoint(SchemaBase):
    label: str
    date: datetime
    session_id: UUID | None = None
    average_score: float
    target_role: str | None = None
    category: str | None = None


class MetricTrendPoint(SchemaBase):
    label: str
    date: datetime
    value: float


class InterviewHistoryItem(SchemaBase):
    session_id: UUID
    title: str
    target_role: str
    category: str
    status: str
    difficulty: str
    completed_at: datetime | None = None
    created_at: datetime
    question_count: int = 0
    answered_count: int = 0
    average_score: float | None = None
    communication_score: float | None = None
    confidence_score: float | None = None
    technical_score: float | None = None
    correctness_rate: float | None = None


class WeakAreaFrequencyItem(SchemaBase):
    kind: str
    area_name: str
    frequency: int
    frequency_rate: float = Field(ge=0, le=1)
    priority: str


class RoleReadinessItem(SchemaBase):
    target_role: str
    readiness_score: float = Field(ge=0, le=100)
    interviews_completed: int
    average_score: float | None = None
    trend: TrendDirection = "insufficient_data"


class ImprovementProgressSnapshot(SchemaBase):
    roadmap_completion_rate: float = Field(ge=0, le=100)
    roadmap_items_completed: int = 0
    roadmap_items_total: int = 0
    weak_areas_high_priority: int = 0
    weak_areas_improving: int = 0
    weak_areas_declining: int = 0
    overall_improvement_score: float | None = None


class AnalyticsDashboardResponse(SchemaBase):
    version: str = "phase16"
    generated_at: datetime
    filters_applied: AnalyticsFiltersApplied
    available_roles: list[str] = Field(default_factory=list)
    available_categories: list[str] = Field(default_factory=list)
    summary: AnalyticsSummary
    score_over_time: list[ScoreTrendPoint] = Field(default_factory=list)
    communication_trend: list[MetricTrendPoint] = Field(default_factory=list)
    confidence_trend: list[MetricTrendPoint] = Field(default_factory=list)
    technical_trend: list[MetricTrendPoint] = Field(default_factory=list)
    interview_history: list[InterviewHistoryItem] = Field(default_factory=list)
    interview_history_total: int = 0
    interview_history_page: int = 1
    interview_history_page_size: int = 10
    interview_history_pages: int = 0
    weak_area_frequency: list[WeakAreaFrequencyItem] = Field(default_factory=list)
    role_readiness: list[RoleReadinessItem] = Field(default_factory=list)
    improvement_progress: ImprovementProgressSnapshot


class AnalyticsProgressResponse(SchemaBase):
    version: str = "phase16"
    generated_at: datetime
    filters_applied: AnalyticsFiltersApplied
    improvement_score_over_time: list[MetricTrendPoint] = Field(default_factory=list)
    correctness_over_time: list[MetricTrendPoint] = Field(default_factory=list)
    roadmap_completion_over_time: list[MetricTrendPoint] = Field(default_factory=list)
    improvement_progress: ImprovementProgressSnapshot
