"""Post-interview workflow: feedback report (+ optional weak-area refresh)."""

from __future__ import annotations

from typing import Any

from app.orchestration.observability import new_workflow_id, trace_workflow
from app.orchestration.registry import get_agent_registry
from app.orchestration.runner import OrchestrationRunner
from app.orchestration.types import AgentName, WorkflowName
from app.schemas.orchestration import WorkflowRunResult


def run_post_interview_workflow(
    *,
    session_summary: dict[str, Any],
    evaluations: list[dict[str, Any]],
    speech_scores: list[dict[str, Any]],
    answers_history: list[dict[str, Any]] | None = None,
    speeches_history: list[dict[str, Any]] | None = None,
    workflow_id: str | None = None,
    run_weak_areas: bool = True,
) -> WorkflowRunResult:
    wf_id = workflow_id or new_workflow_id()
    runner = OrchestrationRunner()
    registry = get_agent_registry()
    outputs: dict[str, dict[str, Any]] = {}
    completed: list[str] = []
    memory: dict[str, Any] = {"session": session_summary}

    with trace_workflow(
        workflow_id=wf_id, agent="workflow", step=WorkflowName.POST_INTERVIEW.value
    ):
        if run_weak_areas and answers_history is not None:
            weak_result = runner.run_agent_graph(
                AgentName.WEAK_AREA_DETECTION,
                {
                    "answers": answers_history,
                    "speeches": speeches_history or [],
                },
                workflow_id=wf_id,
                memory=memory,
                direct_fn=registry.get_executor(AgentName.WEAK_AREA_DETECTION),
                graph_builder=registry.get_graph_builder(AgentName.WEAK_AREA_DETECTION),
            )
            if weak_result.status == "completed":
                outputs["weak_area_detection"] = weak_result.output
                completed.append(AgentName.WEAK_AREA_DETECTION.value)
                memory["weak_areas"] = weak_result.output

        feedback_result = runner.run_agent_graph(
            AgentName.FEEDBACK_REPORT,
            {
                "session_summary": session_summary,
                "evaluations": evaluations,
                "speech_scores": speech_scores,
                "target_role": session_summary.get("target_role"),
            },
            workflow_id=wf_id,
            memory=memory,
            direct_fn=registry.get_executor(AgentName.FEEDBACK_REPORT),
            graph_builder=registry.get_graph_builder(AgentName.FEEDBACK_REPORT),
        )
        if feedback_result.status != "completed":
            return WorkflowRunResult(
                workflow_id=wf_id,
                workflow_name=WorkflowName.POST_INTERVIEW.value,
                status="partial" if completed else "failed",
                outputs=outputs,
                completed_agents=completed,
                error=feedback_result.error,
            )
        outputs["feedback_report"] = feedback_result.output
        completed.append(AgentName.FEEDBACK_REPORT.value)

    return WorkflowRunResult(
        workflow_id=wf_id,
        workflow_name=WorkflowName.POST_INTERVIEW.value,
        status="completed",
        outputs=outputs,
        completed_agents=completed,
    )
