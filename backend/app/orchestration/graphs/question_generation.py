"""Question Generation Agent graph."""

from __future__ import annotations

from app.agents.question_generator.graph import run_question_generator
from app.orchestration.state import AgentWorkflowState, merge_memory


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = dict(state["input"])
    result_state = run_question_generator(payload)
    questions = result_state.get("questions") or []
    if not questions:
        raise ValueError("Question generator produced no questions")
    memory = merge_memory(
        state,
        {
            "question_generation": {
                "count": len(questions),
                "rag_chunks": len(payload.get("rag_snippets") or []),
            }
        },
    )
    return {
        **state,
        "output": {"questions": questions, "rag_snippets": result_state.get("rag_snippets") or []},
        "memory": memory,
        "status": "completed",
        "step": "done",
    }


def _build_langgraph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentWorkflowState)
    graph.add_node("generate", _execute)
    graph.set_entry_point("generate")
    graph.add_edge("generate", END)
    return graph.compile()


def run_question_generation_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_question_generation_graph():
    return _build_langgraph
