"""Interview question API schemas."""

from uuid import UUID

from pydantic import Field

from app.models.enums import QuestionType
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class InterviewQuestionCreate(SchemaBase):
    session_id: UUID
    question_text: str = Field(min_length=1)
    question_type: QuestionType
    order_index: int = Field(ge=0)
    time_limit_seconds: int | None = Field(default=None, ge=1)


class InterviewQuestionUpdate(SchemaBase):
    question_text: str | None = Field(default=None, min_length=1)
    question_type: QuestionType | None = None
    order_index: int | None = Field(default=None, ge=0)
    time_limit_seconds: int | None = None


class InterviewQuestionResponse(UUIDSchema, TimestampSchema):
    session_id: UUID
    question_text: str
    question_type: QuestionType
    order_index: int
    time_limit_seconds: int | None
