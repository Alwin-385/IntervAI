"""Feedback Report Agent — session-level recruiter report."""

from __future__ import annotations

from datetime import UTC, datetime

from app.orchestration.prompts.common import RECRUITER_TONE
from app.orchestration.state import AgentWorkflowState, merge_memory
from app.schemas.orchestration import FeedbackReport, FeedbackReportSection


def _build_heuristic_report(payload: dict) -> FeedbackReport:
    evaluations = payload.get("evaluations") or []
    speech_scores = payload.get("speech_scores") or []
    session_summary = payload.get("session_summary") or {}

    overall_scores = [
        float(e.get("overall_score") or e.get("scores", {}).get("overall_score") or 0)
        for e in evaluations
        if e
    ]
    avg = round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else None

    strengths: list[str] = []
    weaknesses: list[str] = []
    for ev in evaluations[:10]:
        for s in ev.get("strengths") or []:
            if s and s not in strengths:
                strengths.append(str(s))
        for w in ev.get("weaknesses") or []:
            if w and w not in weaknesses:
                weaknesses.append(str(w))

    comm_avg = None
    if speech_scores:
        comm_avg = round(
            sum(float(s.get("communication_score", 0)) for s in speech_scores) / len(speech_scores),
            1,
        )

    target_role = session_summary.get("target_role") or payload.get("target_role") or "your target role"
    marks = session_summary.get("marks_display") or ""

    executive = (
        f"Session review for {target_role}. "
        + (f"Marks: {marks}. " if marks else "")
        + (f"Average answer quality score: {avg}%. " if avg is not None else "")
        + (f"Average communication delivery: {comm_avg}%. " if comm_avg is not None else "")
        + "Focus on the highest-impact gaps below before your next mock."
    )

    sections = [
        FeedbackReportSection(
            title="Answer quality",
            body=(
                f"Based on {len(evaluations)} evaluated answer(s). "
                "Review rubric-missed points on incorrect items and rewrite using the model answers."
            ),
            priority="high" if avg is not None and avg < 65 else "medium",
        ),
        FeedbackReportSection(
            title="Communication & delivery",
            body=(
                f"Speech analyses: {len(speech_scores)}. "
                "Practice pacing, reduce fillers, and signpost structure (First… Then… Finally…)."
            ),
            priority="medium",
        ),
    ]

    next_steps = [
        "Re-attempt your lowest-scoring question with the rubric visible.",
        "Run one voice answer per day focusing on filler reduction.",
    ]
    if weaknesses:
        next_steps.insert(0, f"Address: {weaknesses[0][:120]}")

    return FeedbackReport(
        session_id=session_summary.get("session_id"),
        target_role=target_role,
        overall_score=avg,
        marks_display=marks,
        executive_summary=executive,
        strengths=strengths[:6],
        weaknesses=weaknesses[:6],
        sections=sections,
        next_steps=next_steps[:5],
        generated_at=datetime.now(UTC),
    )


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = state["input"]
    report = _build_heuristic_report(payload)

    # Optional LLM polish when enabled
    from app.core.config import get_settings
    from app.ai.providers.factory import get_llm_provider
    import json

    settings = get_settings()
    if not settings.orchestration_feedback_llm and not (
        settings.openai_api_key and not settings.answer_evaluation_heuristic_only
    ):
        pass
    elif settings.openai_api_key:
        try:
            llm = get_llm_provider(settings)
            system = RECRUITER_TONE + "\nReturn JSON for FeedbackReport schema fields."
            user = json.dumps(
                {
                    "draft": report.model_dump(mode="json"),
                    "evaluations_count": len(payload.get("evaluations") or []),
                },
                default=str,
            )[:12000]
            raw = llm.complete_json(system=system, user=user)
            polished = FeedbackReport.model_validate(json.loads(raw))
            report = polished
        except Exception:
            pass

    memory = merge_memory(state, {"feedback_report": {"overall_score": report.overall_score}})
    return {
        **state,
        "output": {"report": report.model_dump(mode="json")},
        "memory": memory,
        "status": "completed",
        "step": "done",
    }


def _build_langgraph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentWorkflowState)
    graph.add_node("report", _execute)
    graph.set_entry_point("report")
    graph.add_edge("report", END)
    return graph.compile()


def run_feedback_report_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_feedback_report_graph():
    return _build_langgraph
