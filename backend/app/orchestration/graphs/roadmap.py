"""Roadmap Agent graph."""

from __future__ import annotations

from uuid import UUID

from app.orchestration.state import AgentWorkflowState, merge_memory
from app.schemas.roadmap_engine import GenerateRoadmapRequest
from app.services.roadmap_engine import RoadmapEngineService


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = state["input"]
    # Service instance injected via payload for async contexts; sync path uses pre-built output
    if "roadmap_response" in payload:
        response = payload["roadmap_response"]
        output = {
            "phases": [p if isinstance(p, dict) else p for p in (response.get("phases") or [])],
            "summary": response.get("summary", ""),
            "title": response.get("title", ""),
            "target_role": response.get("target_role"),
            "total_items": response.get("total_items", 0),
        }
    else:
        raise ValueError(
            "roadmap agent requires roadmap_response in input (pre-computed by RoadmapEngineService)"
        )

    memory = merge_memory(state, {"roadmap": {"total_items": output.get("total_items", 0)}})
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
    graph.add_node("roadmap", _execute)
    graph.set_entry_point("roadmap")
    graph.add_edge("roadmap", END)
    return graph.compile()


def run_roadmap_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_roadmap_graph():
    return _build_langgraph


async def run_roadmap_via_service(
    service: RoadmapEngineService,
    user_id: UUID,
    request: GenerateRoadmapRequest,
) -> dict:
    """Helper for async callers — runs engine then packages for graph validation."""
    result = await service.generate_roadmap(user_id, request)
    return {
        "roadmap_response": {
            "phases": [p.model_dump() for p in result.phases],
            "summary": result.summary,
            "title": result.title,
            "target_role": result.target_role,
            "total_items": result.total_items,
        }
    }
