"""Answer evaluation pipeline — load context → evaluate (LLM or heuristic)."""

from __future__ import annotations

import json
from typing import Any, TypedDict

from app.agents.answer_evaluator.heuristic import build_heuristic_evaluation
from app.agents.answer_evaluator.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from app.agents.answer_evaluator.rubric import apply_rubric_to_evaluation
from app.ai.providers.factory import get_llm_provider
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.answer_evaluator import AnswerEvaluationContext, StructuredAnswerEvaluation

logger = get_logger(__name__)


def _speech_block(ctx: AnswerEvaluationContext) -> str:
    sc = ctx.speech_context
    if not sc:
        return "Speech delivery analysis: not available."
    parts = []
    if sc.communication_score is not None:
        parts.append(f"communication={sc.communication_score:.0f}")
    if sc.confidence_score is not None:
        parts.append(f"confidence={sc.confidence_score:.0f}")
    if sc.fluency_score is not None:
        parts.append(f"fluency={sc.fluency_score:.0f}")
    if sc.words_per_minute is not None:
        parts.append(f"wpm={sc.words_per_minute:.0f}")
    if not parts:
        return "Speech delivery analysis: not available."
    return (
        "Speech delivery (Phase 12): "
        + ", ".join(parts)
        + ". Factor delivery into communication/confidence scores."
    )


class EvaluatorState(TypedDict, total=False):
    context: dict[str, Any]
    evaluation: dict[str, Any]


def _evaluate_step(state: EvaluatorState) -> EvaluatorState:
    ctx = AnswerEvaluationContext.model_validate(state["context"])
    settings = get_settings()
    evaluation: StructuredAnswerEvaluation | None = None

    use_llm = not settings.answer_evaluation_heuristic_only and bool(settings.openai_api_key)

    if use_llm:
        llm = get_llm_provider(settings)
        try:
            criteria_block = (
                "\n".join(f"- {c}" for c in ctx.evaluation_criteria) or "- General quality"
            )
            points_block = "\n".join(f"- {p}" for p in ctx.expected_answer_points) or "- N/A"
            speech_block = _speech_block(ctx)
            user_msg = USER_TEMPLATE.format(
                target_role=ctx.target_role,
                interview_category=ctx.interview_category,
                difficulty=ctx.difficulty,
                question_type=ctx.question_type,
                question_text=ctx.question_text[:4000],
                criteria_block=criteria_block,
                points_block=points_block,
                answer_text=ctx.answer_text[:12000],
                speech_block=speech_block,
            )
            raw = llm.complete_json(system=SYSTEM_PROMPT, user=user_msg)
            payload = json.loads(raw)
            payload.setdefault("version", "phase13_v3")
            payload.setdefault("target_role", ctx.target_role)
            payload.setdefault("interview_category", ctx.interview_category)
            payload.setdefault("question_type", ctx.question_type)
            payload.setdefault("correctness_verdict", "incorrect")
            payload.setdefault("is_correct", False)
            payload.setdefault("rubric_score", 0)
            payload.setdefault("reference_answer", "")
            payload.setdefault("correct_answer", "")
            payload.setdefault("correctness_explanation", "")
            evaluation = StructuredAnswerEvaluation.model_validate(payload)
            evaluation = apply_rubric_to_evaluation(evaluation, ctx)
            logger.info("answer_evaluation_llm_ok", answer_id=str(ctx.answer_id))
        except Exception as exc:
            logger.warning(
                "answer_evaluation_llm_failed", error=str(exc), answer_id=str(ctx.answer_id)
            )

    if evaluation is None:
        evaluation = build_heuristic_evaluation(ctx)

    return {**state, "evaluation": evaluation.model_dump()}


def _build_graph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(EvaluatorState)
    graph.add_node("evaluate", _evaluate_step)
    graph.set_entry_point("evaluate")
    graph.add_edge("evaluate", END)
    return graph.compile()


def run_answer_evaluator(context: AnswerEvaluationContext) -> StructuredAnswerEvaluation:
    """Direct execution (default — fast, reliable)."""
    state: EvaluatorState = {"context": context.model_dump(mode="json")}
    result = _evaluate_step(state)
    return StructuredAnswerEvaluation.model_validate(result["evaluation"])


def run_answer_evaluator_via_graph(context: AnswerEvaluationContext) -> StructuredAnswerEvaluation:
    """LangGraph-compiled path (same logic, for workflow extension)."""
    app = _build_graph()
    final = app.invoke({"context": context.model_dump(mode="json")})
    return StructuredAnswerEvaluation.model_validate(final["evaluation"])
