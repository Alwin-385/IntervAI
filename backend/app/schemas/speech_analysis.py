"""Speech analysis API schemas."""

from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class SpeechAnalysisCreate(SchemaBase):
    answer_id: UUID | None = None
    session_id: UUID | None = None
    words_per_minute: float | None = Field(default=None, ge=0)
    filler_word_count: int | None = Field(default=None, ge=0)
    clarity_score: float | None = Field(default=None, ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=100)
    metrics: dict[str, Any] | None = None


class SpeechAnalysisUpdate(SchemaBase):
    words_per_minute: float | None = Field(default=None, ge=0)
    filler_word_count: int | None = Field(default=None, ge=0)
    clarity_score: float | None = Field(default=None, ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=100)
    metrics: dict[str, Any] | None = None


class SpeechAnalysisResponse(UUIDSchema, TimestampSchema):
    answer_id: UUID | None
    session_id: UUID | None
    words_per_minute: float | None
    filler_word_count: int | None
    clarity_score: float | None
    confidence_score: float | None
    metrics: dict[str, Any] | None
