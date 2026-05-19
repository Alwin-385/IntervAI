"""Interview session API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.enums import InterviewSessionStatus
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class InterviewSessionCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    resume_id: UUID | None = None
    status: InterviewSessionStatus = InterviewSessionStatus.SCHEDULED
    notes: str | None = None
    scheduled_at: datetime | None = None


class InterviewSessionUpdate(SchemaBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    target_role: str | None = None
    resume_id: UUID | None = None
    status: InterviewSessionStatus | None = None
    notes: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class InterviewSessionResponse(UUIDSchema, TimestampSchema):
    user_id: UUID
    resume_id: UUID | None
    title: str
    target_role: str
    status: InterviewSessionStatus
    notes: str | None
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
