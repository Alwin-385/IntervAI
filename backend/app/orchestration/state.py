"""Workflow state models for LangGraph agents (Phase 17)."""

from __future__ import annotations

from typing import Any, TypedDict

from app.orchestration.types import AgentName, WorkflowStatus


class AgentWorkflowState(TypedDict, total=False):
    """Standard state passed through every agent graph."""

    workflow_id: str
    agent: str
    status: WorkflowStatus
    step: str
    retry_count: int
    max_retries: int
    error: str | None
    input: dict[str, Any]
    output: dict[str, Any]
    memory: dict[str, Any]
    metadata: dict[str, Any]


class CompositeWorkflowState(TypedDict, total=False):
    """Multi-agent pipeline state with shared memory."""

    workflow_id: str
    workflow_name: str
    status: WorkflowStatus
    current_agent: str | None
    completed_agents: list[str]
    retry_count: int
    error: str | None
    input: dict[str, Any]
    memory: dict[str, Any]
    outputs: dict[str, dict[str, Any]]


def initial_agent_state(
    agent: AgentName,
    payload: dict[str, Any],
    *,
    workflow_id: str,
    max_retries: int = 3,
    memory: dict[str, Any] | None = None,
) -> AgentWorkflowState:
    return {
        "workflow_id": workflow_id,
        "agent": agent.value,
        "status": "pending",
        "step": "init",
        "retry_count": 0,
        "max_retries": max_retries,
        "error": None,
        "input": payload,
        "output": {},
        "memory": dict(memory or {}),
        "metadata": {},
    }


def merge_memory(state: AgentWorkflowState, updates: dict[str, Any]) -> dict[str, Any]:
    memory = dict(state.get("memory") or {})
    memory.update(updates)
    return memory
