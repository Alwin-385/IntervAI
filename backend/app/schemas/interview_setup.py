"""Interview wizard creation schemas (Phase 8)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator

from app.models.enums import (
    AnswerMode,
    InterviewCategory,
    InterviewDifficulty,
    InterviewSessionStatus,
)
from app.schemas.common import SchemaBase
from app.schemas.interview_session import InterviewSessionResponse

PRESET_ROLES = (
    "Software Engineer",
    "AI Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "ML Engineer",
    "DevOps Engineer",
)

MIN_QUESTIONS = 3
MAX_QUESTIONS = 25


class InterviewCreateRequest(SchemaBase):
    """Payload from the interview setup wizard."""

    target_role: Annotated[str, Field(min_length=1, max_length=120)]
    category: InterviewCategory
    difficulty: InterviewDifficulty
    answer_mode: AnswerMode
    question_count: Annotated[int, Field(ge=MIN_QUESTIONS, le=MAX_QUESTIONS)]
    resume_id: UUID | None = None
    title: Annotated[str | None, Field(default=None, max_length=255)] = None
    notes: Annotated[str | None, Field(default=None, max_length=4000)] = None

    @field_validator("target_role")
    @classmethod
    def _strip_role(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("target_role cannot be empty")
        return cleaned


class InterviewSetupResponse(InterviewSessionResponse):
    """Created session enriched with the wizard fields."""

    category: InterviewCategory
    difficulty: InterviewDifficulty
    answer_mode: AnswerMode
    question_count: int


def default_title(role: str, category: InterviewCategory, difficulty: InterviewDifficulty) -> str:
    label = {
        InterviewCategory.HR: "HR",
        InterviewCategory.TECHNICAL: "Technical",
        InterviewCategory.BEHAVIORAL: "Behavioral",
        InterviewCategory.DSA: "DSA",
        InterviewCategory.RESUME_BASED: "Resume-based",
        InterviewCategory.MIXED: "Mixed",
    }[category]
    tier = difficulty.value.capitalize()
    return f"{label} interview — {role} ({tier})"


def ensure_resume_for_category(category: InterviewCategory, resume_id: UUID | None) -> None:
    if category == InterviewCategory.RESUME_BASED and resume_id is None:
        raise ValueError("resume_id is required for resume-based interviews")


__all__ = [
    "InterviewCreateRequest",
    "InterviewSetupResponse",
    "PRESET_ROLES",
    "MIN_QUESTIONS",
    "MAX_QUESTIONS",
    "default_title",
    "ensure_resume_for_category",
    "InterviewSessionStatus",
]
