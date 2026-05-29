"""Resume pipeline: parse → analyze."""

from __future__ import annotations

from typing import Any

from app.orchestration.observability import new_workflow_id, trace_workflow
from app.orchestration.registry import get_agent_registry
from app.orchestration.runner import OrchestrationRunner
from app.orchestration.types import AgentName, WorkflowName
from app.schemas.orchestration import WorkflowRunResult


def run_resume_pipeline_workflow(
    *,
    pdf_bytes: bytes,
    resume_id: str,
    analysis_id: str,
    user_id: str,
    target_role: str | None = None,
    workflow_id: str | None = None,
) -> WorkflowRunResult:
    wf_id = workflow_id or new_workflow_id()
    runner = OrchestrationRunner()
    registry = get_agent_registry()
    memory: dict[str, Any] = {}
    outputs: dict[str, dict[str, Any]] = {}
    completed: list[str] = []

    with trace_workflow(workflow_id=wf_id, agent="workflow", step=WorkflowName.RESUME_PIPELINE.value):
        parse_result = runner.run_agent_graph(
            AgentName.RESUME_PARSER,
            {"pdf_bytes": pdf_bytes},
            workflow_id=wf_id,
            memory=memory,
            direct_fn=registry.get_executor(AgentName.RESUME_PARSER),
            graph_builder=registry.get_graph_builder(AgentName.RESUME_PARSER),
        )
        if parse_result.status != "completed":
            return WorkflowRunResult(
                workflow_id=wf_id,
                workflow_name=WorkflowName.RESUME_PIPELINE.value,
                status="failed",
                outputs=outputs,
                completed_agents=completed,
                error=parse_result.error,
            )
        outputs["resume_parser"] = parse_result.output
        completed.append(AgentName.RESUME_PARSER.value)
        memory.update(parse_result.output)

        analyze_payload = {
            "resume_id": resume_id,
            "analysis_id": analysis_id,
            "user_id": user_id,
            "target_role": target_role,
            "cleaned_text": parse_result.output.get("cleaned_text", ""),
            "extracted_data": parse_result.output.get("extracted_data", {}),
            "chunks": parse_result.output.get("chunks", []),
        }
        analyze_result = runner.run_agent_graph(
            AgentName.RESUME_ANALYSIS,
            analyze_payload,
            workflow_id=wf_id,
            memory=memory,
            direct_fn=registry.get_executor(AgentName.RESUME_ANALYSIS),
            graph_builder=registry.get_graph_builder(AgentName.RESUME_ANALYSIS),
        )
        if analyze_result.status != "completed":
            return WorkflowRunResult(
                workflow_id=wf_id,
                workflow_name=WorkflowName.RESUME_PIPELINE.value,
                status="partial",
                outputs=outputs,
                completed_agents=completed,
                error=analyze_result.error,
            )
        outputs["resume_analysis"] = analyze_result.output
        completed.append(AgentName.RESUME_ANALYSIS.value)

    return WorkflowRunResult(
        workflow_id=wf_id,
        workflow_name=WorkflowName.RESUME_PIPELINE.value,
        status="completed",
        outputs=outputs,
        completed_agents=completed,
    )
