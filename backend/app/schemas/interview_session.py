"""Interview session API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.enums import (
    AnswerMode,
    InterviewCategory,
    InterviewDifficulty,
    InterviewSessionStatus,
)
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class InterviewSessionCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    resume_id: UUID | None = None
    status: InterviewSessionStatus = InterviewSessionStatus.SCHEDULED
    category: InterviewCategory = InterviewCategory.MIXED
    difficulty: InterviewDifficulty = InterviewDifficulty.INTERMEDIATE
    answer_mode: AnswerMode = AnswerMode.TEXT
    question_count: int = Field(default=5, ge=1, le=50)
    notes: str | None = None
    scheduled_at: datetime | None = None


class InterviewSessionUpdate(SchemaBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    target_role: str | None = None
    resume_id: UUID | None = None
    status: InterviewSessionStatus | None = None
    category: InterviewCategory | None = None
    difficulty: InterviewDifficulty | None = None
    answer_mode: AnswerMode | None = None
    question_count: int | None = Field(default=None, ge=1, le=50)
    notes: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    current_question_index: int | None = None


class InterviewSessionResponse(UUIDSchema, TimestampSchema):
    user_id: UUID
    resume_id: UUID | None
    title: str
    target_role: str
    status: InterviewSessionStatus
    category: InterviewCategory
    difficulty: InterviewDifficulty
    answer_mode: AnswerMode
    question_count: int
    notes: str | None
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    current_question_index: int = 0
