"""Regression tests for analytics dashboard aggregation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

pytestmark = pytest.mark.unit


def test_build_weak_summary_accepts_answer_lists_for_analytics():
    """Analytics dashboard must pass answer/speech lists, not counts."""
    from app.analytics.weak_area_detector import AnswerHistoryItem
    from app.services.weak_area_detection_engine import _build_summary as build_weak_summary

    answers = [
        AnswerHistoryItem(
            session_id=uuid.uuid4(),
            answer_id=uuid.uuid4(),
            recorded_at=datetime.now(UTC),
            interview_category="technical",
            correctness_verdict="correct",
            rubric_score=80.0,
            communication_score=75.0,
            technical_score=82.0,
            clarity_score=75.0,
            completeness_score=80.0,
            technical_accuracy_score=82.0,
            star_overall=None,
            dsa_optimality=None,
            rubric_points_missed=[],
            weaknesses=[],
            missing_concepts=[],
        )
    ]

    summary = build_weak_summary(
        interviews=1,
        answers=answers,
        speeches=[],
        items=[],
    )

    assert summary.answers_analyzed == 1
    assert summary.overall_improvement_score > 0
