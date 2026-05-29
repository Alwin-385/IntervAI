"""Central orchestration service (Phase 17)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.logging import get_logger
from app.orchestration.registry import get_agent_registry
from app.orchestration.runner import OrchestrationRunner
from app.orchestration.types import AgentName, WorkflowName
from app.orchestration.workflows.post_interview import run_post_interview_workflow
from app.orchestration.workflows.resume_pipeline import run_resume_pipeline_workflow
from app.schemas.orchestration import AgentRunResult, WorkflowRunResult

logger = get_logger(__name__)


class OrchestrationService:
    """Production entry point for all LangGraph-coordinated AI workflows."""

    def __init__(self) -> None:
        self._runner = OrchestrationRunner()
        self._registry = get_agent_registry()

    @property
    def enabled(self) -> bool:
        return get_settings().orchestration_enabled

    def run_agent(
        self,
        agent: AgentName,
        payload: dict[str, Any],
        *,
        workflow_id: str | None = None,
        memory: dict[str, Any] | None = None,
    ) -> AgentRunResult:
        if not self.enabled:
            return self._runner.run_agent_graph(
                agent,
                payload,
                workflow_id=workflow_id,
                memory=memory,
                direct_fn=self._registry.get_executor(agent),
                graph_builder=self._registry.get_graph_builder(agent),
            )

        logger.info("orchestration_run_agent", agent=agent.value, workflow_id=workflow_id)
        return self._runner.run_agent_graph(
            agent,
            payload,
            workflow_id=workflow_id,
            memory=memory,
            direct_fn=self._registry.get_executor(agent),
            graph_builder=self._registry.get_graph_builder(agent),
        )

    def run_workflow(
        self,
        workflow: WorkflowName,
        **kwargs: Any,
    ) -> WorkflowRunResult:
        logger.info("orchestration_run_workflow", workflow=workflow.value)
        if workflow == WorkflowName.RESUME_PIPELINE:
            return run_resume_pipeline_workflow(**kwargs)
        if workflow == WorkflowName.POST_INTERVIEW:
            return run_post_interview_workflow(**kwargs)
        raise ValueError(f"Unknown workflow: {workflow}")


_orchestration_service: OrchestrationService | None = None


def get_orchestration_service() -> OrchestrationService:
    global _orchestration_service
    if _orchestration_service is None:
        _orchestration_service = OrchestrationService()
    return _orchestration_service
