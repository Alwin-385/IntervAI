"""Weak-Area Detection Agent graph."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.analytics.weak_area_detector import (
    AnswerHistoryItem,
    SpeechHistoryItem,
    detect_weak_areas,
)
from app.orchestration.state import AgentWorkflowState, merge_memory
from app.services.weak_area_detection_engine import (
    _build_summary,
    _personalized_recommendations,
    _to_api_item,
)


def _parse_dt(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _answer_from_dict(d: dict) -> AnswerHistoryItem:
    return AnswerHistoryItem(
        session_id=UUID(str(d["session_id"])),
        answer_id=UUID(str(d["answer_id"])),
        recorded_at=_parse_dt(d["recorded_at"]),
        interview_category=str(d["interview_category"]),
        correctness_verdict=str(d["correctness_verdict"]),
        rubric_score=float(d["rubric_score"]),
        communication_score=float(d["communication_score"]),
        technical_score=float(d["technical_score"]),
        clarity_score=float(d["clarity_score"]),
        completeness_score=float(d["completeness_score"]),
        technical_accuracy_score=float(d["technical_accuracy_score"]),
        star_overall=d.get("star_overall"),
        dsa_optimality=d.get("dsa_optimality"),
        rubric_points_missed=list(d.get("rubric_points_missed") or []),
        weaknesses=list(d.get("weaknesses") or []),
        missing_concepts=list(d.get("missing_concepts") or []),
    )


def _speech_from_dict(d: dict) -> SpeechHistoryItem:
    return SpeechHistoryItem(
        session_id=UUID(str(d["session_id"])),
        answer_id=UUID(str(d["answer_id"])),
        recorded_at=_parse_dt(d["recorded_at"]),
        communication_score=float(d["communication_score"]),
        confidence_score=float(d["confidence_score"]),
        fluency_score=float(d["fluency_score"]),
        filler_word_count=int(d["filler_word_count"]),
        words_per_minute=float(d["words_per_minute"]),
        weak_patterns=list(d.get("weak_patterns") or []),
    )


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = state["input"]
    answers = [_answer_from_dict(a) for a in (payload.get("answers") or [])]
    speeches = [_speech_from_dict(s) for s in (payload.get("speeches") or [])]

    min_freq = int(payload.get("min_frequency") or (1 if len(answers) + len(speeches) < 6 else 2))
    detected = detect_weak_areas(answers, speeches, min_frequency=min_freq)
    items = [_to_api_item(d) for d in detected]
    session_ids = {a.session_id for a in answers} | {s.session_id for s in speeches}
    summary = _build_summary(
        interviews=len(session_ids),
        answers=len(answers),
        speeches=len(speeches),
        items=items,
    )
    recommendations = _personalized_recommendations(items)

    output = {
        "weak_areas": [i.model_dump() for i in items],
        "summary": summary.model_dump(),
        "recommendations": recommendations,
    }
    memory = merge_memory(
        state,
        {
            "weak_area_detection": {
                "count": len(items),
                "high_priority": summary.high_priority_count,
            }
        },
    )
    return {
        **state,
        "output": output,
        "memory": memory,
        "status": "completed",
        "step": "done",
    }


def _build_langgraph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentWorkflowState)
    graph.add_node("detect", _execute)
    graph.set_entry_point("detect")
    graph.add_edge("detect", END)
    return graph.compile()


def run_weak_area_detection_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_weak_area_detection_graph():
    return _build_langgraph
