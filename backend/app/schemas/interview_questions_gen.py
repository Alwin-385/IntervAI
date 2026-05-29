"""Structured interview question generation schemas (Phase 9)."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.models.enums import InterviewCategory, InterviewDifficulty, QuestionType
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class GeneratedQuestion(SchemaBase):
    """Single AI-generated interview question."""

    question_text: str = Field(min_length=10, max_length=4000)
    category: InterviewCategory
    difficulty: InterviewDifficulty
    question_type: QuestionType
    expected_answer_points: list[str] = Field(min_length=1, max_length=12)
    evaluation_criteria: list[str] = Field(min_length=1, max_length=10)
    time_limit_seconds: int = Field(ge=60, le=900)
    order_index: int = Field(ge=0)
    source_hint: str | None = Field(
        default=None,
        description="Resume project/skill reference when applicable",
    )


class QuestionGenerationResult(SchemaBase):
    version: str = "1"
    session_id: str
    target_role: str
    session_category: InterviewCategory
    questions: list[GeneratedQuestion]
    rag_chunks_used: int = 0
    weak_areas_targeted: list[str] = Field(default_factory=list)


class InterviewQuestionDetail(UUIDSchema, TimestampSchema):
    session_id: UUID
    question_text: str
    question_type: QuestionType
    order_index: int
    time_limit_seconds: int | None
    category: InterviewCategory
    difficulty: InterviewDifficulty
    expected_answer_points: list[str]
    evaluation_criteria: list[str]
    source_hint: str | None = None


class GenerateQuestionsResponse(SchemaBase):
    session_id: UUID
    count: int
    questions: list[InterviewQuestionDetail]
    generation: QuestionGenerationResult
    job_id: str | None = None
    status: str = "completed"
