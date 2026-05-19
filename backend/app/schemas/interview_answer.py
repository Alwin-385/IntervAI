"""Interview answer API schemas."""

from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class InterviewAnswerCreate(SchemaBase):
    question_id: UUID
    answer_text: str | None = None
    audio_storage_path: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)
    word_count: int | None = Field(default=None, ge=0)


class InterviewAnswerUpdate(SchemaBase):
    answer_text: str | None = None
    audio_storage_path: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)
    word_count: int | None = Field(default=None, ge=0)


class InterviewAnswerResponse(UUIDSchema, TimestampSchema):
    question_id: UUID
    answer_text: str | None
    audio_storage_path: str | None
    duration_seconds: float | None
    word_count: int | None
