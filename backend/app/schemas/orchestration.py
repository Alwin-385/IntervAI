"""Orchestration workflow schemas (Phase 17)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import SchemaBase
from app.schemas.weak_area_analytics import DetectedWeakAreaItem, WeakAreaProgressSummary


class FeedbackReportSection(SchemaBase):
    title: str
    body: str
    priority: Literal["high", "medium", "low"] = "medium"


class FeedbackReport(SchemaBase):
    version: str = "phase17"
    session_id: str | None = None
    target_role: str = ""
    overall_score: float | None = None
    marks_display: str = ""
    executive_summary: str = Field(min_length=1)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    sections: list[FeedbackReportSection] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    generated_at: datetime | None = None


class WeakAreaDetectionOutput(SchemaBase):
    weak_areas: list[DetectedWeakAreaItem]
    summary: WeakAreaProgressSummary
    recommendations: list[str] = Field(default_factory=list)


class AgentRunResult(SchemaBase):
    workflow_id: str
    agent: str
    status: Literal["completed", "failed"]
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    retry_count: int = 0
    duration_ms: float | None = None


class WorkflowRunResult(SchemaBase):
    workflow_id: str
    workflow_name: str
    status: Literal["completed", "failed", "partial"]
    outputs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    completed_agents: list[str] = Field(default_factory=list)
    error: str | None = None
