"""Speech analysis API schemas (Phase 12)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class FillerWordStat(SchemaBase):
    word: str
    count: int = Field(ge=0)


class SpeechAnalyzeRequest(SchemaBase):
    answer_id: UUID
    transcript: str | None = Field(
        default=None,
        description="Optional override; otherwise loaded from the stored answer",
    )
    duration_seconds: float | None = Field(default=None, ge=0)


class SpeechAnalyzeResponse(UUIDSchema, TimestampSchema):
    answer_id: UUID | None
    session_id: UUID | None
    fluency_score: float = Field(ge=0, le=100)
    communication_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    speaking_speed_score: float = Field(ge=0, le=100)
    pause_score: float = Field(ge=0, le=100)
    words_per_minute: float = Field(ge=0)
    filler_word_count: int = Field(ge=0)
    filler_word_stats: list[FillerWordStat]
    pause_count: int = Field(ge=0)
    hesitation_count: int = Field(ge=0)
    weak_patterns: list[str]
    communication_tips: list[str]
    confidence_indicators: dict[str, float]
    metrics: dict[str, Any]
    clarity_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Alias for communication clarity (stored on entity)",
    )


class SpeechAnalyzeSessionRequest(SchemaBase):
    session_id: UUID
    force: bool = Field(
        default=False,
        description="Re-run analysis even when stored results exist",
    )


class QuestionSpeechAnalysis(SchemaBase):
    question_id: UUID
    question_text: str
    order_index: int
    answer_id: UUID | None = None
    answer_preview: str = ""
    analysis: SpeechAnalyzeResponse | None = None


class SessionSpeechSummary(SchemaBase):
    analyzed_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    avg_communication_score: float = Field(ge=0, le=100)
    avg_fluency_score: float = Field(ge=0, le=100)
    avg_confidence_score: float = Field(ge=0, le=100)
    avg_speaking_speed_score: float = Field(ge=0, le=100)
    avg_words_per_minute: float = Field(ge=0)
    total_filler_words: int = Field(ge=0)
    highlight_weak_patterns: list[str]
    highlight_tips: list[str]


class SpeechSessionResultsResponse(SchemaBase):
    session_id: UUID
    session_title: str
    target_role: str
    questions: list[QuestionSpeechAnalysis]
    summary: SessionSpeechSummary
