"""Rubric correctness matching tests."""

from uuid import uuid4

from app.agents.answer_evaluator.rubric import assess_answer_rubric
from app.schemas.answer_evaluator import AnswerEvaluationContext


def _ctx(answer: str, points: list[str], criteria: list[str] | None = None):
    return AnswerEvaluationContext(
        answer_id=uuid4(),
        question_id=uuid4(),
        session_id=uuid4(),
        question_text="Tell me about a challenging project.",
        answer_text=answer,
        target_role="Software Engineer",
        interview_category="behavioral",
        difficulty="intermediate",
        question_type="behavioral",
        evaluation_criteria=criteria
        or [
            "Clarity and relevance to the question",
            "Depth appropriate to stated difficulty",
            "Ownership, reflection, and outcome metrics",
        ],
        expected_answer_points=points,
    )


def test_star_answer_marked_correct():
    answer = (
        "In my last role the situation was a failing release. My task was to stabilize prod. "
        "I led the rollback, added monitoring, and fixed the root cause. "
        "We reduced incidents by 40% over two months."
    )
    points = [
        "Clear structure (context → action → result)",
        "Specific examples, not generic claims",
        "Uses STAR format with measurable outcome",
    ]
    r = assess_answer_rubric(_ctx(answer, points))
    assert r.verdict in ("correct", "partially_correct")
    assert len(r.points_matched) >= 2


def test_technical_complexity_answer():
    answer = (
        "I use binary search on a sorted array. Time complexity is O(log n) and space is O(1). "
        "Edge cases include empty array and duplicates."
    )
    points = [
        "States time/space complexity",
        "Covers edge cases and test strategy",
        "Specific examples, not generic claims",
    ]
    r = assess_answer_rubric(
        _ctx(answer, points, criteria=["Technical accuracy and justified design choices"]),
    )
    assert r.verdict == "correct"
    assert r.is_correct
