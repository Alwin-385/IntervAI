"""Map InterviewQuestion ORM rows to API detail schemas."""

from __future__ import annotations

from app.models.enums import InterviewCategory, InterviewDifficulty
from app.models.interview_question import InterviewQuestion
from app.schemas.interview_questions_gen import InterviewQuestionDetail


def to_question_detail(row: InterviewQuestion) -> InterviewQuestionDetail:
    meta = row.question_metadata or {}
    category_raw = meta.get("category", "mixed")
    difficulty_raw = meta.get("difficulty", "intermediate")
    try:
        category = InterviewCategory(category_raw)
    except ValueError:
        category = InterviewCategory.MIXED
    try:
        difficulty = InterviewDifficulty(difficulty_raw)
    except ValueError:
        difficulty = InterviewDifficulty.INTERMEDIATE

    return InterviewQuestionDetail(
        id=row.id,
        session_id=row.session_id,
        question_text=row.question_text,
        question_type=row.question_type,
        order_index=row.order_index,
        time_limit_seconds=row.time_limit_seconds,
        category=category,
        difficulty=difficulty,
        expected_answer_points=list(meta.get("expected_answer_points") or []),
        evaluation_criteria=list(meta.get("evaluation_criteria") or []),
        source_hint=meta.get("source_hint"),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
