"""Resume Parser Agent — PDF/text extraction graph."""

from __future__ import annotations

from typing import Any

from app.orchestration.state import AgentWorkflowState, merge_memory
from app.services.resume_extraction.service import ResumeExtractionService


def _execute(state: AgentWorkflowState) -> AgentWorkflowState:
    payload = state["input"]
    pdf_bytes = payload.get("pdf_bytes")
    if not pdf_bytes:
        raise ValueError("pdf_bytes is required for resume_parser agent")

    service = ResumeExtractionService()
    result = service.extract_from_pdf_bytes(pdf_bytes)

    output: dict[str, Any] = {
        "raw_text": result.raw_text,
        "cleaned_text": result.cleaned_text,
        "extracted_data": result.extracted_data.model_dump(),
        "chunks": [c.model_dump() for c in result.chunks],
    }
    memory = merge_memory(state, {"resume_parser": {"chunk_count": len(result.chunks)}})
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
    graph.add_node("parse", _execute)
    graph.set_entry_point("parse")
    graph.add_edge("parse", END)
    return graph.compile()


def run_resume_parser_graph(state: AgentWorkflowState) -> AgentWorkflowState:
    return _execute(state)


def build_resume_parser_graph():
    return _build_langgraph
