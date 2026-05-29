"""Dashboard overview schemas."""

from datetime import datetime

from app.schemas.common import SchemaBase


class DashboardStats(SchemaBase):
    mock_interviews: int = 0
    resumes_total: int = 0
    resumes_analyzed: int = 0
    resumes_processing: int = 0
    average_score: float | None = None
    practice_hours: float = 0.0


class DashboardActivityItem(SchemaBase):
    kind: str
    title: str
    subtitle: str
    timestamp: datetime
    status: str | None = None


class DashboardOverview(SchemaBase):
    stats: DashboardStats
    recent_activity: list[DashboardActivityItem]
