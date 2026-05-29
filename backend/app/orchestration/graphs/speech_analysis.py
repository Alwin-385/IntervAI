"""Speech Analysis Agent graph."""

from __future__ import annotations

from app.orchestration.state import AgentWorkflowState, merge_memory
from app.speech.analyzer import analyze_speech
from app.speech.transcript_cleanup import collapse_repeated_phrases


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = state["input"]
    transcript = collapse_repeated_phrases((payload.get("transcript") or "").strip())
    if not transcript:
        raise ValueError("transcript is required for speech_analysis agent")

    duration = payload.get("duration_seconds")
    result = analyze_speech(transcript, duration_seconds=duration)

    scores = {
        "communication_score": result.communication_score,
        "confidence_score": result.confidence_score,
        "fluency_score": result.fluency_score,
        "speaking_speed_score": result.speaking_speed_score,
        "pause_score": result.pause_score,
    }
    output = {
        "transcript": transcript,
        "scores": scores,
        "filler_breakdown": [{"word": f.word, "count": f.count} for f in result.filler_word_stats],
        "weak_patterns": result.weak_patterns,
        "communication_tips": result.communication_tips,
        "metrics": dict(result.metrics),
        "analysis_version": "phase12",
        "words_per_minute": result.words_per_minute,
        "filler_word_count": result.filler_word_count,
        "word_count": result.word_count,
        "pause_count": result.pause_count,
        "hesitation_count": result.hesitation_count,
        "confidence_indicators": dict(result.confidence_indicators),
        "duration_seconds": result.duration_seconds,
    }
    memory = merge_memory(
        state,
        {
            "speech_analysis": {
                "filler_count": result.filler_word_count,
                "confidence": result.confidence_score,
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
    graph.add_node("analyze", _execute)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)
    return graph.compile()


def run_speech_analysis_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_speech_analysis_graph():
    return _build_langgraph
