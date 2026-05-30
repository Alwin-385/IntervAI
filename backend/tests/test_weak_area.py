"""Tests for weak area detection types and detection logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

pytestmark = pytest.mark.unit


def _make_answer_item(
    rubric_score: float = 70.0,
    technical_score: float = 70.0,
    communication_score: float = 70.0,
    category: str = "technical",
):
    """Scores are 0–100 as the detector expects."""
    from app.analytics.weak_area_detector import AnswerHistoryItem

    return AnswerHistoryItem(
        session_id=uuid.uuid4(),
        answer_id=uuid.uuid4(),
        recorded_at=datetime.now(UTC),
        interview_category=category,
        correctness_verdict="correct",
        rubric_score=rubric_score,
        communication_score=communication_score,
        technical_score=technical_score,
        clarity_score=communication_score,
        completeness_score=rubric_score,
        technical_accuracy_score=technical_score,
        star_overall=None,
        dsa_optimality=None,
        rubric_points_missed=[],
        weaknesses=[],
        missing_concepts=[],
    )


def _make_speech_item(
    communication_score: float = 70.0,
    confidence_score: float = 70.0,
    fluency_score: float = 70.0,
    filler_count: int = 2,
    wpm: float = 140.0,
):
    from app.analytics.weak_area_detector import SpeechHistoryItem

    return SpeechHistoryItem(
        session_id=uuid.uuid4(),
        answer_id=uuid.uuid4(),
        recorded_at=datetime.now(UTC),
        communication_score=communication_score,
        confidence_score=confidence_score,
        fluency_score=fluency_score,
        filler_word_count=filler_count,
        words_per_minute=wpm,
        weak_patterns=[],
    )


class TestWeakAreaDefinitions:
    def test_all_kinds_have_definitions(self):
        from app.analytics.weak_area_types import WEAK_AREA_DEFINITIONS

        expected_kinds = {
            "communication_issues",
            "confidence_problems",
            "weak_technical_explanations",
            "poor_behavioral_storytelling",
            "dsa_explanation_issues",
            "filler_word_overuse",
            "lack_of_structure",
        }
        assert expected_kinds.issubset(set(WEAK_AREA_DEFINITIONS.keys()))

    def test_each_definition_has_required_fields(self):
        from app.analytics.weak_area_types import WEAK_AREA_DEFINITIONS

        for kind, defn in WEAK_AREA_DEFINITIONS.items():
            assert defn.area_name
            assert defn.category
            assert defn.description
            assert defn.kind == kind


class TestWeakAreaDetector:
    def test_detect_from_strong_answers_returns_no_high_severity(self):
        from app.analytics.weak_area_detector import detect_weak_areas

        # Scores above all thresholds (62+ for communication, 58+ for technical)
        answers = [
            _make_answer_item(rubric_score=90.0, technical_score=90.0, communication_score=90.0)
            for _ in range(5)
        ]
        speech = [
            _make_speech_item(communication_score=90.0, confidence_score=90.0, filler_count=0)
            for _ in range(5)
        ]
        result = detect_weak_areas(answers, speech)
        high_severity = [w for w in result if w.priority == "high"]
        assert len(high_severity) == 0

    def test_detect_from_weak_technical_answers(self):
        from app.analytics.weak_area_detector import detect_weak_areas

        answers = [_make_answer_item(technical_score=30.0, rubric_score=30.0) for _ in range(6)]
        speech = [_make_speech_item() for _ in range(4)]
        result = detect_weak_areas(answers, speech)
        kinds = [w.kind for w in result]
        assert "weak_technical_explanations" in kinds

    def test_detect_filler_word_overuse(self):
        from app.analytics.weak_area_detector import detect_weak_areas

        answers = [_make_answer_item() for _ in range(4)]
        speech = [_make_speech_item(filler_count=20, fluency_score=30.0) for _ in range(5)]
        result = detect_weak_areas(answers, speech)
        kinds = [w.kind for w in result]
        assert "filler_word_overuse" in kinds

    def test_returns_list_of_detected_weak_areas(self):
        from app.analytics.weak_area_detector import detect_weak_areas

        result = detect_weak_areas([], [])
        assert isinstance(result, list)

    def test_empty_history_returns_empty(self):
        from app.analytics.weak_area_detector import detect_weak_areas

        result = detect_weak_areas([], [])
        assert result == []
