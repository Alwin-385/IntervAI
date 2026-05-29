"""Resume Analysis Agent graph."""

from __future__ import annotations

from app.agents.resume_analyzer.graph import run_resume_analyzer
from app.orchestration.state import AgentWorkflowState, merge_memory


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = state["input"]
    result = run_resume_analyzer(
        resume_id=payload["resume_id"],
        analysis_id=payload["analysis_id"],
        user_id=payload["user_id"],
        target_role=payload.get("target_role"),
        cleaned_text=payload.get("cleaned_text") or "",
        extracted_data=payload.get("extracted_data") or {},
        chunks=payload.get("chunks") or [],
    )
    memory = merge_memory(
        state,
        {
            "resume_analysis": {
                "readiness_score": result.scores.role_readiness_score,
                "embeddings_indexed": result.embeddings_indexed,
            }
        },
    )
    return {
        **state,
        "output": {"analysis": result.model_dump()},
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


def run_resume_analysis_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_resume_analysis_graph():
    return _build_langgraph
