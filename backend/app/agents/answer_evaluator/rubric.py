"""Rubric alignment against question metadata (same source as question generator)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from app.schemas.answer_evaluator import AnswerEvaluationContext, StructuredAnswerEvaluation

_WORD_RE = re.compile(r"[a-z0-9]+", re.I)
_STOPWORDS = frozenset(
    "a an the and or but in on at to for of is are was were be been being "
    "with by from as it its this that these those you your our their i we they "
    "he she not no so if then than also very can will would should could".split(),
)

CorrectnessVerdict = Literal["correct", "partially_correct", "incorrect"]

# Maps rubric bullet text → patterns that indicate the candidate satisfied it in natural speech.
_POINT_SIGNALS: list[tuple[re.Pattern, re.Pattern]] = [
    (
        re.compile(r"star|measurable\s+outcome", re.I),
        re.compile(
            r"\b(star|situation|task|action|result|outcome|impact|achieved|improved|"
            r"increased|decreased|saved|\d+%|\d+\s*(users|ms|hours|days))\b",
            re.I,
        ),
    ),
    (
        re.compile(r"time/space\s+complexity|states\s+time", re.I),
        re.compile(
            r"\b(o\s*\(|complexity|log\s*n|linear|quadratic|constant\s+space|"
            r"time\s+complexity|space\s+complexity)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"clear\s+structure|context.*action.*result", re.I),
        re.compile(
            r"\b(context|situation|first|then|next|finally|approach|step|result|"
            r"outcome|because|therefore|summary)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"specific\s+examples|not\s+generic", re.I),
        re.compile(
            r"\b(for\s+example|instance|when\s+i|we\s+(built|implemented|designed|fixed|led)|"
            r"project|feature|production|deployed|wrote|created)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"trade.?off|alternatives|lessons\s+learned", re.I),
        re.compile(
            r"\b(trade.?off|versus|vs\.?|alternative|instead|however|pros|cons|"
            r"downside|benefit|lesson)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"edge\s+cases|test\s+strategy", re.I),
        re.compile(
            r"\b(edge\s+case|empty|null|duplicate|boundary|test|unit\s+test|"
            r"integration|validation|corner)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"technical\s+accuracy|design\s+choices", re.I),
        re.compile(
            r"\b(api|database|algorithm|architecture|system|code|bug|debug|"
            r"latency|cache|deploy|server|client|stack|framework)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"clarity\s+and\s+relevance|depth\s+appropriate", re.I),
        re.compile(r".{40,}", re.I),
    ),
    (
        re.compile(r"authentic\s+motivation|role\s+alignment", re.I),
        re.compile(
            r"\b(motivat|passion|interest|align|role|team|culture|grow|learn|"
            r"contribute|mission|values)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"ownership|reflection|outcome\s+metrics", re.I),
        re.compile(
            r"\b(i\s+|my\s+|owned|led|responsible|reflect|learned|metric|"
            r"measured|result|impact)\b",
            re.I,
        ),
    ),
    (
        re.compile(r"references\s+.+\s+with", re.I),
        re.compile(
            r"\b(built|implemented|worked|developed|using|with|stack|project|"
            r"experience|shipped)\b",
            re.I,
        ),
    ),
]


@dataclass(frozen=True)
class RubricAssessment:
    verdict: CorrectnessVerdict
    is_correct: bool
    points_matched: list[str]
    points_missed: list[str]
    criteria_matched: list[str]
    criteria_missed: list[str]
    points_coverage: float
    criteria_coverage: float
    rubric_score: float
    reference_answer: str
    correctness_explanation: str


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text) if w.lower() not in _STOPWORDS}


def _significant_tokens(text: str) -> set[str]:
    return {t for t in _tokens(text) if len(t) >= 3}


def _signal_match(answer_text: str, point_text: str) -> bool:
    for point_pat, answer_pat in _POINT_SIGNALS:
        if point_pat.search(point_text):
            return bool(answer_pat.search(answer_text))
    return False


def _phrase_match(answer_tokens: set[str], answer_text: str, phrase: str) -> bool:
    """Match rubric bullets against natural-language answers (not exact wording)."""
    if _signal_match(answer_text, phrase):
        return True

    phrase_tokens = _significant_tokens(phrase)
    if not phrase_tokens:
        return len(answer_text.strip()) >= 30

    overlap = len(phrase_tokens & answer_tokens) / len(phrase_tokens)
    if overlap >= 0.28:
        return True

    # Any two significant terms from the rubric line appear in the answer
    hits = sum(1 for t in phrase_tokens if t in answer_text.lower())
    if hits >= min(2, len(phrase_tokens)):
        return True

    # Long rubric line: one strong keyword (5+ chars) is enough
    long_terms = [t for t in phrase_tokens if len(t) >= 5]
    if long_terms and any(t in answer_text.lower() for t in long_terms):
        return True

    return False


def _match_lists(
    answer_tokens: set[str],
    answer_text: str,
    items: list[str],
) -> tuple[list[str], list[str], float]:
    if not items:
        return [], [], 0.0
    matched: list[str] = []
    missed: list[str] = []
    for item in items:
        if _phrase_match(answer_tokens, answer_text, item):
            matched.append(item)
        else:
            missed.append(item)
    coverage = len(matched) / len(items)
    return matched, missed, coverage


def _build_reference_answer(ctx: AnswerEvaluationContext) -> str:
    points = [p.strip() for p in ctx.expected_answer_points if p.strip()]
    if not points:
        return (
            f"A strong answer for this {ctx.interview_category} question should directly address: "
            f"{ctx.question_text[:300]}. "
            f"Cover role-relevant examples for {ctx.target_role} with clear structure and measurable outcomes."
        )
    lines = [f"• {p}" for p in points]
    intro = (
        f"For «{ctx.question_text[:180]}{'…' if len(ctx.question_text) > 180 else ''}», "
        f"a complete answer should include:"
    )
    return f"{intro}\n" + "\n".join(lines)


def _verdict_from_coverage(
    points_cov: float,
    criteria_cov: float,
    *,
    difficulty: str,
    points_matched_count: int = 0,
    n_points: int = 0,
    n_criteria_matched: int = 0,
    n_criteria_total: int = 0,
    answer_word_count: int = 0,
) -> CorrectnessVerdict:
    """Human-aligned: majority of rubric points satisfied ⇒ correct."""
    min_points_for_correct = max(1, (n_points + 1) // 2) if n_points else 0

    substantive = answer_word_count >= 25

    if n_points == 0 and not n_criteria_total:
        if substantive and answer_word_count >= 50:
            return "correct"
        if substantive:
            return "partially_correct"
        return "incorrect"

    # Correct: at least half of expected points, or strong coverage
    if n_points > 0 and points_matched_count >= min_points_for_correct:
        return "correct"
    if points_cov >= 0.5 and substantive:
        return "correct"
    if points_matched_count >= 2 and points_cov >= 0.4:
        return "correct"

    # Criteria-only boost when points are generic but answer is strong
    if (
        n_criteria_total > 0
        and n_criteria_matched >= max(1, (n_criteria_total + 1) // 2)
        and points_matched_count >= 1
        and substantive
    ):
        return "correct"

    # Partial: at least one rubric hit or moderate coverage
    if points_matched_count >= 1 or points_cov >= 0.25:
        return "partially_correct"
    if criteria_cov >= 0.34 and substantive:
        return "partially_correct"

    # Short empty-ish answers
    if answer_word_count < 12:
        return "incorrect"

    if substantive and (points_cov >= 0.15 or criteria_cov >= 0.25):
        return "partially_correct"

    return "incorrect"


def assess_answer_rubric(ctx: AnswerEvaluationContext) -> RubricAssessment:
    answer_text = (ctx.answer_text or "").strip()
    answer_tokens = _tokens(answer_text)
    word_count = len(answer_text.split())

    points_matched, points_missed, points_cov = _match_lists(
        answer_tokens,
        answer_text,
        ctx.expected_answer_points,
    )
    crit_matched, crit_missed, crit_cov = _match_lists(
        answer_tokens,
        answer_text,
        ctx.evaluation_criteria,
    )

    if not ctx.expected_answer_points and not ctx.evaluation_criteria:
        points_cov = 0.7 if word_count >= 40 else (0.45 if word_count >= 20 else 0.2)
        crit_cov = points_cov

    n_points = len(ctx.expected_answer_points)
    n_crit = len(ctx.evaluation_criteria)

    verdict = _verdict_from_coverage(
        points_cov,
        crit_cov,
        difficulty=ctx.difficulty,
        points_matched_count=len(points_matched),
        n_points=n_points,
        n_criteria_matched=len(crit_matched),
        n_criteria_total=n_crit,
        answer_word_count=word_count,
    )

    rubric_score = _clamp((points_cov * 0.65 + crit_cov * 0.35) * 100)
    if verdict == "correct":
        rubric_score = max(rubric_score, 72.0)
    elif verdict == "partially_correct":
        rubric_score = max(min(rubric_score, 68.0), 45.0)

    reference = _build_reference_answer(ctx)
    if verdict == "correct":
        explanation = (
            f"Correct: your answer addresses {len(points_matched)}/{max(n_points, 1)} "
            f"expected points from the interview rubric."
        )
    elif verdict == "partially_correct":
        explanation = (
            f"Partially correct: you covered {len(points_matched)} of {max(n_points, 1)} "
            f"expected points — see the model answer for missing elements."
        )
    else:
        explanation = (
            f"Incorrect or incomplete: only {len(points_matched)} of {max(n_points, 1)} "
            f"expected points were detected in your answer."
        )

    return RubricAssessment(
        verdict=verdict,
        is_correct=verdict == "correct",
        points_matched=points_matched,
        points_missed=points_missed,
        criteria_matched=crit_matched,
        criteria_missed=crit_missed,
        points_coverage=round(points_cov, 3),
        criteria_coverage=round(crit_cov, 3),
        rubric_score=round(rubric_score, 1),
        reference_answer=reference,
        correctness_explanation=explanation,
    )


def _clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


def blend_with_speech(
    rubric_score: float,
    delivery_score: float | None,
    *,
    weight_rubric: float = 0.75,
) -> float:
    if delivery_score is None:
        return rubric_score
    w = weight_rubric
    return _clamp(rubric_score * w + delivery_score * (1 - w))


def speech_delivery_score(ctx: AnswerEvaluationContext) -> float | None:
    sc = ctx.speech_context
    if sc is None:
        return None
    parts = [sc.communication_score, sc.confidence_score, sc.fluency_score]
    vals = [p for p in parts if p is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def apply_rubric_to_evaluation(
    evaluation: StructuredAnswerEvaluation,
    ctx: AnswerEvaluationContext,
    rubric: RubricAssessment | None = None,
) -> StructuredAnswerEvaluation:
    rubric = rubric or assess_answer_rubric(ctx)
    delivery = speech_delivery_score(ctx)
    rubric_blended = blend_with_speech(rubric.rubric_score, delivery)

    s = evaluation.scores
    style_avg = (
        s.communication_score
        + s.clarity_score
        + s.confidence_score
        + s.professionalism_score
    ) / 4
    overall = _clamp(rubric_blended * 0.62 + style_avg * 0.38)

    if rubric.verdict == "incorrect":
        overall = min(overall, 52.0)
    elif rubric.verdict == "partially_correct":
        overall = min(max(overall, 48.0), 78.0)
    elif rubric.verdict == "correct":
        overall = max(overall, 68.0)

    technical_accuracy = _clamp(rubric.rubric_score * 0.7 + s.technical_accuracy_score * 0.3)
    completeness = _clamp(rubric.points_coverage * 100 * 0.85 + s.completeness_score * 0.15)

    correct_answer = ""
    if not rubric.is_correct:
        correct_answer = rubric.reference_answer

    summary_prefix = {
        "correct": "Correct — ",
        "partially_correct": "Partially correct — ",
        "incorrect": "Incorrect — ",
    }[rubric.verdict]

    summary = summary_prefix + rubric.correctness_explanation + " " + evaluation.summary_feedback

    return evaluation.model_copy(
        update={
            "version": "phase13_v3",
            "correctness_verdict": rubric.verdict,
            "is_correct": rubric.is_correct,
            "rubric_score": rubric.rubric_score,
            "rubric_points_matched": rubric.points_matched,
            "rubric_points_missed": rubric.points_missed,
            "rubric_criteria_matched": rubric.criteria_matched,
            "rubric_criteria_missed": rubric.criteria_missed,
            "reference_answer": rubric.reference_answer,
            "correct_answer": correct_answer,
            "correctness_explanation": rubric.correctness_explanation,
            "speech_context": ctx.speech_context,
            "summary_feedback": summary.strip()[:2000],
            "missing_concepts": list(
                dict.fromkeys(rubric.points_missed + evaluation.missing_concepts),
            )[:8],
            "scores": s.model_copy(
                update={
                    "overall_score": overall,
                    "technical_accuracy_score": technical_accuracy,
                    "completeness_score": completeness,
                    "relevance_score": _clamp(rubric.points_coverage * 100),
                },
            ),
        },
    )
