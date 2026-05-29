"""Interview Evaluation Agent graph."""

from __future__ import annotations

from app.agents.answer_evaluator.graph import run_answer_evaluator
from app.orchestration.state import AgentWorkflowState, merge_memory
from app.schemas.answer_evaluator import AnswerEvaluationContext


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    ctx = AnswerEvaluationContext.model_validate(state["input"])
    result = run_answer_evaluator(ctx)
    memory = merge_memory(
        state,
        {
            "interview_evaluation": {
                "answer_id": str(ctx.answer_id),
                "verdict": result.correctness_verdict,
                "overall": result.scores.overall_score,
            }
        },
    )
    return {
        **state,
        "output": {"evaluation": result.model_dump()},
        "memory": memory,
        "status": "completed",
        "step": "done",
    }


def _build_langgraph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AgentWorkflowState)
    graph.add_node("evaluate", _execute)
    graph.set_entry_point("evaluate")
    graph.add_edge("evaluate", END)
    return graph.compile()


def run_interview_evaluation_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_interview_evaluation_graph():
    return _build_langgraph
