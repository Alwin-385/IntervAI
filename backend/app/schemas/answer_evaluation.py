"""Answer evaluation API schemas."""

from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class AnswerEvaluationCreate(SchemaBase):
    answer_id: UUID
    overall_score: float = Field(ge=0, le=100)
    relevance_score: float | None = Field(default=None, ge=0, le=100)
    depth_score: float | None = Field(default=None, ge=0, le=100)
    clarity_score: float | None = Field(default=None, ge=0, le=100)
    feedback: str = Field(min_length=1)
    criteria_breakdown: dict[str, Any] | None = None
    strengths: list[Any] | None = None
    improvements: list[Any] | None = None


class AnswerEvaluationUpdate(SchemaBase):
    overall_score: float | None = Field(default=None, ge=0, le=100)
    relevance_score: float | None = Field(default=None, ge=0, le=100)
    depth_score: float | None = Field(default=None, ge=0, le=100)
    clarity_score: float | None = Field(default=None, ge=0, le=100)
    feedback: str | None = None
    criteria_breakdown: dict[str, Any] | None = None
    strengths: list[Any] | None = None
    improvements: list[Any] | None = None


class AnswerEvaluationResponse(UUIDSchema, TimestampSchema):
    answer_id: UUID
    overall_score: float
    relevance_score: float | None
    depth_score: float | None
    clarity_score: float | None
    feedback: str
    criteria_breakdown: dict[str, Any] | None
    strengths: list[Any] | None
    improvements: list[Any] | None
