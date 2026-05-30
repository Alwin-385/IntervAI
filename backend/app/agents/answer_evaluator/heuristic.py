"""Rubric-based answer evaluation (no OpenAI required)."""

from __future__ import annotations

import re

from app.agents.answer_evaluator.rubric import apply_rubric_to_evaluation, assess_answer_rubric
from app.models.enums import InterviewCategory
from app.schemas.answer_evaluator import (
    AnswerEvaluationContext,
    AnswerScoreBreakdown,
    DsaComplexityFeedback,
    StarMethodFeedback,
    StructuredAnswerEvaluation,
)

_WORD_RE = re.compile(r"[a-z0-9]+", re.I)
_STAR_SITUATION = re.compile(
    r"\b(situation|context|when|at\s+\w+|previously|last\s+year|project)\b",
    re.I,
)
_STAR_TASK = re.compile(r"\b(task|goal|objective|responsible|needed to|challenge)\b", re.I)
_STAR_ACTION = re.compile(
    r"\b(i\s+|we\s+|implemented|built|led|designed|created|developed|fixed|improved)\b",
    re.I,
)
_STAR_RESULT = re.compile(
    r"\b(result|outcome|impact|increased|decreased|reduced|saved|achieved|%\b|\d+%|\d+\s*(users|ms|hours))",
    re.I,
)
_COMPLEXITY = re.compile(
    r"\bO\s*\(\s*[^)]+\)|time\s+complexity|space\s+complexity|linear|quadratic|log\s*n\b",
    re.I,
)


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)}


def _coverage(answer_tokens: set[str], phrases: list[str]) -> float:
    if not phrases:
        return 0.65
    hits = 0
    for phrase in phrases:
        pt = _tokens(phrase)
        if not pt:
            continue
        overlap = len(pt & answer_tokens) / len(pt)
        if overlap >= 0.4:
            hits += 1
    return hits / len(phrases) if phrases else 0.65


def _clamp(v: float) -> float:
    return max(0.0, min(100.0, round(v, 1)))


def _word_score(count: int, difficulty: str) -> float:
    targets = {"beginner": 40, "intermediate": 70, "advanced": 100}
    target = targets.get(difficulty.lower(), 70)
    if count >= target:
        return 88.0
    if count >= target * 0.6:
        return 72.0
    if count >= target * 0.35:
        return 58.0
    if count >= 15:
        return 48.0
    return 32.0


def build_heuristic_evaluation(ctx: AnswerEvaluationContext) -> StructuredAnswerEvaluation:
    """Score answer against criteria and category-specific rubrics."""
    answer = (ctx.answer_text or "").strip()
    words = answer.split()
    word_count = len(words)
    answer_tokens = _tokens(answer)

    criteria_cov = _coverage(answer_tokens, ctx.evaluation_criteria)
    points_cov = _coverage(answer_tokens, ctx.expected_answer_points)
    completeness = _clamp((criteria_cov * 0.45 + points_cov * 0.55) * 100)

    relevance = _clamp(55 + points_cov * 40 + (10 if word_count > 25 else -15))
    clarity = _clamp(
        _word_score(word_count, ctx.difficulty) * 0.35 + 40 + min(word_count, 120) * 0.35
    )
    if len(words) > 8:
        avg_len = sum(len(w) for w in words) / len(words)
        if avg_len > 12:
            clarity -= 8
        if avg_len < 4:
            clarity -= 5
    clarity = _clamp(clarity)

    category = ctx.interview_category.lower()
    technical = 50.0
    professionalism = _clamp(
        50 + len(_tokens(answer) & _tokens("team stakeholder communicate professional respect")) * 8
    )
    confidence = _clamp(
        45 + min(word_count, 90) * 0.45 + (12 if re.search(r"\b(i|we)\b", answer, re.I) else -8)
    )
    role_alignment = _clamp(50 + _coverage(answer_tokens, [ctx.target_role]) * 45)

    technical_accuracy = technical
    technical_feedback: str | None = None
    star_feedback: StarMethodFeedback | None = None
    dsa_feedback: DsaComplexityFeedback | None = None

    if category in (
        InterviewCategory.TECHNICAL.value,
        InterviewCategory.DSA.value,
        InterviewCategory.MIXED.value,
    ):
        tech_terms = _tokens(
            "api database algorithm system design latency cache deploy test debug architecture "
            "complexity stack queue hash tree graph",
        )
        tech_hits = len(answer_tokens & tech_terms)
        technical_accuracy = _clamp(48 + tech_hits * 6 + points_cov * 25)
        technical = _clamp((technical_accuracy + completeness) / 2)
        technical_feedback = (
            "You touched on relevant technical themes, but depth and trade-off discussion could be stronger. "
            "Name concrete technologies, constraints, and how you validated the solution."
            if technical < 70
            else "Solid technical framing. Add more specifics on trade-offs, failure modes, and metrics to stand out."
        )

    if category == InterviewCategory.BEHAVIORAL.value:
        s = 70.0 if _STAR_SITUATION.search(answer) else 35.0
        t = 70.0 if _STAR_TASK.search(answer) else 35.0
        a = 75.0 if _STAR_ACTION.search(answer) else 40.0
        r = 75.0 if _STAR_RESULT.search(answer) else 30.0
        star_overall = _clamp((s + t + a + r) / 4)
        missing: list[str] = []
        if s < 50:
            missing.append("Clear situation / context")
        if t < 50:
            missing.append("Specific task or goal")
        if a < 50:
            missing.append("Your actions (use 'I' and concrete steps)")
        if r < 50:
            missing.append("Quantified result or business impact")
        star_feedback = StarMethodFeedback(
            situation_score=_clamp(s),
            task_score=_clamp(t),
            action_score=_clamp(a),
            result_score=_clamp(r),
            overall_star_score=star_overall,
            feedback=(
                "Structure your story with STAR: situation, task, your actions, and measurable results."
                if star_overall < 65
                else "Good STAR structure. Tighten metrics and make your personal contribution unmistakable."
            ),
            missing_elements=missing,
            improved_star_outline=(
                "Situation: [team/company context]. Task: [your goal]. Action: [3 steps you took]. "
                "Result: [metric + outcome]."
            ),
        )
        professionalism = _clamp(max(professionalism, star_overall * 0.9))

    if category == InterviewCategory.DSA.value:
        has_complexity = bool(_COMPLEXITY.search(answer))
        time_c = (
            "O(n)"
            if "linear" in answer.lower()
            else ("Discussed" if has_complexity else "Not stated")
        )
        space_c = (
            "O(1)"
            if re.search(r"\bconstant\s+space\b|O\s*\(\s*1\s*\)", answer, re.I)
            else ("Not stated" if not has_complexity else "Discussed")
        )
        correctness = _clamp(50 + points_cov * 35 + (15 if has_complexity else -10))
        optimality = _clamp(correctness - (10 if not has_complexity else 0))
        dsa_feedback = DsaComplexityFeedback(
            time_complexity=time_c,
            space_complexity=space_c,
            correctness_score=correctness,
            optimality_score=optimality,
            feedback=(
                "State time and space complexity explicitly and justify why your approach is appropriate."
                if not has_complexity
                else "Complexity mentioned — compare alternatives and edge cases (empty input, duplicates)."
            ),
            suggested_improvements=[
                "State brute-force vs optimized complexity before coding.",
                "Walk through a small example and edge case.",
                "Mention space/time trade-offs if you use extra structures.",
            ],
        )
        technical_accuracy = _clamp((correctness + optimality) / 2)
        technical = technical_accuracy

    if category == InterviewCategory.HR.value:
        professionalism = _clamp(professionalism + 10)
        role_alignment = _clamp(role_alignment + 8)
        technical = _clamp(technical * 0.7 + professionalism * 0.3)

    communication = _clamp((clarity + professionalism + confidence) / 3)
    overall = _clamp(
        relevance * 0.15
        + clarity * 0.1
        + technical_accuracy * 0.15
        + completeness * 0.15
        + communication * 0.1
        + professionalism * 0.1
        + confidence * 0.1
        + role_alignment * 0.15,
    )

    missing_concepts: list[str] = []
    for point in ctx.expected_answer_points:
        pt = _tokens(point)
        if pt and len(pt & answer_tokens) / len(pt) < 0.35:
            missing_concepts.append(point)
    for crit in ctx.evaluation_criteria:
        ct = _tokens(crit)
        if ct and len(ct & answer_tokens) / len(ct) < 0.3 and crit not in missing_concepts:
            missing_concepts.append(crit)
    missing_concepts = missing_concepts[:6]

    strengths: list[str] = []
    if relevance >= 70:
        strengths.append("Stays on topic and addresses the question directly.")
    if clarity >= 68:
        strengths.append("Answer is structured and easy to follow.")
    if completeness >= 65:
        strengths.append("Covers several expected points from the rubric.")
    if confidence >= 65:
        strengths.append("Sounds confident with clear ownership of your work.")
    if not strengths:
        strengths.append("You attempted a substantive response — good base to refine.")

    weaknesses: list[str] = []
    if completeness < 60:
        weaknesses.append("Several expected points from the rubric are missing.")
    if clarity < 58:
        weaknesses.append("Clarify structure: context → approach → outcome.")
    if relevance < 60:
        weaknesses.append("Tie your answer more directly to the question asked.")
    if word_count < 40:
        weaknesses.append("Answer is too brief for this difficulty level.")
    if not weaknesses:
        weaknesses.append("Add quantified impact and deeper technical trade-offs.")

    improved = _build_improved_sample(ctx, answer, missing_concepts)
    suggestions = [
        "Lead with a one-sentence thesis that answers the question.",
        "Use 2–3 concrete examples with metrics (%, time saved, scale).",
        "End with what you learned or how you'd apply this at " + ctx.target_role + ".",
    ]
    if star_feedback and star_feedback.overall_star_score < 70:
        suggestions.insert(0, "Reframe using STAR with a quantified result in the final sentence.")
    if dsa_feedback and dsa_feedback.optimality_score < 65:
        suggestions.insert(
            0, "State brute-force and optimal complexity before describing the algorithm."
        )

    summary = (
        f"For a {ctx.difficulty} {ctx.interview_category} question targeting {ctx.target_role}, "
        f"this answer scores {_clamp(overall):.0f}/100. "
        + (
            "Focus on missing rubric points and sharper structure."
            if overall < 65
            else "Solid foundation — polish depth and measurable outcomes."
        )
    )

    base = StructuredAnswerEvaluation(
        interview_category=ctx.interview_category,
        question_type=ctx.question_type,
        target_role=ctx.target_role,
        correctness_verdict="incorrect",
        is_correct=False,
        rubric_score=0,
        scores=AnswerScoreBreakdown(
            overall_score=_clamp(overall),
            communication_score=_clamp(communication),
            technical_score=_clamp(technical),
            completeness_score=_clamp(completeness),
            confidence_score=_clamp(confidence),
            relevance_score=_clamp(relevance),
            clarity_score=_clamp(clarity),
            technical_accuracy_score=_clamp(technical_accuracy),
            professionalism_score=_clamp(professionalism),
            role_alignment_score=_clamp(role_alignment),
        ),
        summary_feedback=summary,
        strengths=strengths[:5],
        weaknesses=weaknesses[:5],
        missing_concepts=missing_concepts,
        improved_answer=improved,
        improvement_suggestions=suggestions[:6],
        technical_feedback=technical_feedback,
        star_feedback=star_feedback,
        dsa_feedback=dsa_feedback,
        dimension_notes={
            "relevance": "How directly the answer addresses the question and role.",
            "clarity": "Logical flow and ease of understanding.",
            "technical_accuracy": "Correctness and depth of technical claims.",
            "completeness": "Coverage of rubric and expected points.",
            "communication_quality": "Delivery, structure, and professional tone.",
            "professionalism": "Appropriate language and interview presence.",
            "confidence": "Ownership and assertiveness without vagueness.",
            "role_alignment": "Fit for the stated target role.",
        },
    )
    return apply_rubric_to_evaluation(base, ctx, assess_answer_rubric(ctx))


def _build_improved_sample(
    ctx: AnswerEvaluationContext,
    answer: str,
    missing: list[str],
) -> str:
    if answer and len(answer.split()) > 60:
        tail = " ".join(answer.split()[:80])
        extra = (
            f" I would also emphasize: {', '.join(missing[:2])}."
            if missing
            else " I would add specific metrics and trade-offs."
        )
        return (tail + extra).strip()[:1200]

    points = ", ".join(ctx.expected_answer_points[:3]) or "the core requirements"
    return (
        f"For this {ctx.interview_category} question, I would open with a direct answer, then explain my approach "
        f"with a concrete example from my experience. I'd cover {points}, describe the actions I took personally, "
        f"and close with a measurable result and how it prepares me for {ctx.target_role}."
    )
