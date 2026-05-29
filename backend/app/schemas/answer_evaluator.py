"""Structured answer evaluation schemas (Phase 13)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from typing import Literal

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema

CorrectnessVerdict = Literal["correct", "partially_correct", "incorrect"]


class StarMethodFeedback(SchemaBase):
    situation_score: float = Field(ge=0, le=100)
    task_score: float = Field(ge=0, le=100)
    action_score: float = Field(ge=0, le=100)
    result_score: float = Field(ge=0, le=100)
    overall_star_score: float = Field(ge=0, le=100)
    feedback: str
    missing_elements: list[str] = Field(default_factory=list)
    improved_star_outline: str = ""


class DsaComplexityFeedback(SchemaBase):
    time_complexity: str = ""
    space_complexity: str = ""
    correctness_score: float = Field(ge=0, le=100, default=0)
    optimality_score: float = Field(ge=0, le=100, default=0)
    feedback: str = ""
    suggested_improvements: list[str] = Field(default_factory=list)


class AnswerScoreBreakdown(SchemaBase):
    overall_score: float = Field(ge=0, le=100)
    communication_score: float = Field(ge=0, le=100)
    technical_score: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    relevance_score: float = Field(ge=0, le=100)
    clarity_score: float = Field(ge=0, le=100)
    technical_accuracy_score: float = Field(ge=0, le=100)
    professionalism_score: float = Field(ge=0, le=100)
    role_alignment_score: float = Field(ge=0, le=100)


class SpeechContextSnapshot(SchemaBase):
    """Phase 12 speech metrics fed into answer scoring when available."""

    communication_score: float | None = None
    confidence_score: float | None = None
    fluency_score: float | None = None
    words_per_minute: float | None = None


class StructuredAnswerEvaluation(SchemaBase):
    """Full evaluator output before persistence."""

    version: str = "phase13_v3"
    interview_category: str
    question_type: str
    target_role: str
    scores: AnswerScoreBreakdown
    correctness_verdict: CorrectnessVerdict
    is_correct: bool
    rubric_score: float = Field(ge=0, le=100)
    rubric_points_matched: list[str] = Field(default_factory=list)
    rubric_points_missed: list[str] = Field(default_factory=list)
    rubric_criteria_matched: list[str] = Field(default_factory=list)
    rubric_criteria_missed: list[str] = Field(default_factory=list)
    reference_answer: str = ""
    correct_answer: str = ""
    correctness_explanation: str = ""
    speech_context: SpeechContextSnapshot | None = None
    summary_feedback: str = Field(min_length=1)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    improved_answer: str = ""
    improvement_suggestions: list[str] = Field(default_factory=list)
    technical_feedback: str | None = None
    star_feedback: StarMethodFeedback | None = None
    dsa_feedback: DsaComplexityFeedback | None = None
    dimension_notes: dict[str, str] = Field(default_factory=dict)


class AnswerEvaluationContext(SchemaBase):
    """Inputs loaded from DB for the evaluator agent."""

    answer_id: UUID
    question_id: UUID
    session_id: UUID
    question_text: str
    answer_text: str
    target_role: str
    interview_category: str
    difficulty: str
    question_type: str
    evaluation_criteria: list[str] = Field(default_factory=list)
    expected_answer_points: list[str] = Field(default_factory=list)
    speech_context: SpeechContextSnapshot | None = None


class AnswerEvaluationDetailResponse(UUIDSchema, TimestampSchema):
    """Rich API response for GET/POST evaluation."""

    answer_id: UUID
    question_id: UUID
    session_id: UUID
    question_text: str
    answer_preview: str
    interview_category: str
    scores: AnswerScoreBreakdown
    correctness_verdict: CorrectnessVerdict = "incorrect"
    is_correct: bool = False
    rubric_score: float = 0
    rubric_points_matched: list[str] = Field(default_factory=list)
    rubric_points_missed: list[str] = Field(default_factory=list)
    reference_answer: str = ""
    correct_answer: str = ""
    correctness_explanation: str = ""
    summary_feedback: str
    strengths: list[str]
    weaknesses: list[str]
    missing_concepts: list[str]
    improved_answer: str
    improvement_suggestions: list[str]
    technical_feedback: str | None = None
    star_feedback: StarMethodFeedback | None = None
    dsa_feedback: DsaComplexityFeedback | None = None
    criteria_breakdown: dict[str, Any] | None = None


class EvaluateAnswerRequest(SchemaBase):
    force: bool = False


class EvaluateSessionRequest(SchemaBase):
    session_id: UUID
    force: bool = False


class QuestionAnswerEvaluation(SchemaBase):
    question_id: UUID
    question_text: str
    order_index: int
    answer_id: UUID | None = None
    answer_preview: str = ""
    evaluation: AnswerEvaluationDetailResponse | None = None


class SessionEvaluationSummary(SchemaBase):
    total_questions: int = 0
    answered_count: int = 0
    evaluated_count: int = 0
    skipped_count: int = 0
    correct_count: int = 0
    partially_correct_count: int = 0
    incorrect_count: int = 0
    marks_obtained: float = 0
    marks_display: str = "0/0"
    avg_overall_score: float = 0
    avg_communication_score: float = 0
    avg_technical_score: float = 0
    avg_completeness_score: float = 0
    avg_confidence_score: float = 0
    highlight_strengths: list[str] = Field(default_factory=list)
    highlight_weaknesses: list[str] = Field(default_factory=list)


class SessionAnswerEvaluationResponse(SchemaBase):
    session_id: UUID
    session_title: str | None = None
    target_role: str | None = None
    questions: list[QuestionAnswerEvaluation]
    summary: SessionEvaluationSummary
    job_id: str | None = None
    status: str = "completed"
