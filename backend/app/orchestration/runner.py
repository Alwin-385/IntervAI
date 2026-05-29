"""LangGraph runner with retry, validation, and observability (Phase 17)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from app.core.config import get_settings
from app.orchestration.observability import new_workflow_id, trace_workflow
from app.orchestration.retry import RetryPolicy, run_with_retry
from app.orchestration.state import AgentWorkflowState, initial_agent_state
from app.orchestration.types import AgentName
from app.orchestration.validators import validate_agent_output
from app.schemas.orchestration import AgentRunResult


def _default_retry_policy() -> RetryPolicy:
    settings = get_settings()
    return RetryPolicy(
        max_attempts=max(1, settings.orchestration_max_retries),
        base_delay_seconds=settings.orchestration_retry_delay_seconds,
    )


class OrchestrationRunner:
    """Execute agent graphs with standardized lifecycle."""

    def run_agent_graph(
        self,
        agent: AgentName,
        payload: dict[str, Any],
        *,
        workflow_id: str | None = None,
        memory: dict[str, Any] | None = None,
        graph_builder: Callable[[], Any] | None = None,
        direct_fn: Callable[[AgentWorkflowState], AgentWorkflowState] | None = None,
    ) -> AgentRunResult:
        settings = get_settings()
        wf_id = workflow_id or new_workflow_id()
        policy = _default_retry_policy()
        state = initial_agent_state(
            agent,
            payload,
            workflow_id=wf_id,
            max_retries=policy.max_attempts,
            memory=memory,
        )
        started = time.perf_counter()

        def _execute() -> AgentWorkflowState:
            state["status"] = "running"
            state["step"] = "execute"
            if settings.orchestration_use_langgraph_invoke and graph_builder is not None:
                app = graph_builder()
                final = app.invoke(state)
                return final  # type: ignore[return-value]
            if direct_fn is None:
                raise RuntimeError(f"No executor registered for agent {agent.value}")
            return direct_fn(state)

        try:
            with trace_workflow(workflow_id=wf_id, agent=agent.value, step="execute"):
                final_state = run_with_retry(
                    lambda: _execute(),
                    policy=policy,
                    workflow_id=wf_id,
                    agent=agent.value,
                    step="execute",
                )
        except Exception as exc:
            return AgentRunResult(
                workflow_id=wf_id,
                agent=agent.value,
                status="failed",
                error=str(exc),
                retry_count=state.get("retry_count", 0),
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )

        output = dict(final_state.get("output") or {})
        with trace_workflow(workflow_id=wf_id, agent=agent.value, step="validate"):
            validation = validate_agent_output(agent, output)
            if not validation.valid:
                return AgentRunResult(
                    workflow_id=wf_id,
                    agent=agent.value,
                    status="failed",
                    output=output,
                    error="; ".join(validation.errors),
                    duration_ms=round((time.perf_counter() - started) * 1000, 2),
                )
            if validation.normalized is not None:
                output = validation.normalized

        return AgentRunResult(
            workflow_id=wf_id,
            agent=agent.value,
            status="completed",
            output=output,
            retry_count=int(final_state.get("retry_count") or 0),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
