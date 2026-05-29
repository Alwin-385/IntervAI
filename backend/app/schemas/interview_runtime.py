"""Mock interview session runtime schemas (Phase 10)."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.enums import AnswerMode, InterviewSessionStatus
from app.schemas.common import SchemaBase
from app.schemas.interview_answer import InterviewAnswerResponse
from app.schemas.interview_questions_gen import InterviewQuestionDetail


class InterviewProgress(SchemaBase):
    total_questions: int
    answered_count: int
    current_question_index: int
    percent_complete: float = Field(ge=0, le=100)


class QuestionAnswerState(SchemaBase):
    question: InterviewQuestionDetail
    answer: InterviewAnswerResponse | None = None


class InterviewSessionStateResponse(SchemaBase):
    session_id: UUID
    title: str
    target_role: str
    status: InterviewSessionStatus
    started_at: datetime | None
    completed_at: datetime | None
    progress: InterviewProgress
    questions: list[QuestionAnswerState]
    seconds_per_question: int = Field(default=120, ge=60, le=600)
    total_duration_seconds: int = Field(ge=60)
    answer_mode: AnswerMode = AnswerMode.TEXT


class SubmitAnswerRequest(SchemaBase):
    question_id: UUID
    answer_text: str | None = None
    audio_storage_path: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)
    autosave: bool = False
    advance: bool = False
    resume_question_index: int | None = Field(
        default=None,
        ge=0,
        description="Set active question index without advancing (navigation)",
    )


class SubmitAnswerResponse(SchemaBase):
    answer: InterviewAnswerResponse
    progress: InterviewProgress
    saved_at: datetime


class CompleteInterviewResponse(SchemaBase):
    session_id: UUID
    status: InterviewSessionStatus
    completed_at: datetime
    progress: InterviewProgress
    total_time_seconds: float | None = None
