"""Background job API schemas (Phase 18)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.models.enums import BackgroundJobStatus, BackgroundJobType
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class BackgroundJobResponse(UUIDSchema, TimestampSchema):
    user_id: UUID
    job_type: BackgroundJobType
    status: BackgroundJobStatus
    celery_task_id: str | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    progress_percent: int = Field(ge=0, le=100)
    progress_step: str | None = None
    progress_message: str | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    started_at: datetime | None = None
    completed_at: datetime | None = None
    is_terminal: bool = False


class BackgroundJobListResponse(SchemaBase):
    items: list[BackgroundJobResponse]
    total: int
