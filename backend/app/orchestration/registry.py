"""Agent registry mapping names to graph executors (Phase 17)."""

from __future__ import annotations

from collections.abc import Callable

from app.orchestration.graphs import (
    build_feedback_report_graph,
    build_interview_evaluation_graph,
    build_question_generation_graph,
    build_resume_analysis_graph,
    build_resume_parser_graph,
    build_roadmap_graph,
    build_speech_analysis_graph,
    build_weak_area_detection_graph,
    run_feedback_report_graph,
    run_interview_evaluation_graph,
    run_question_generation_graph,
    run_resume_analysis_graph,
    run_resume_parser_graph,
    run_roadmap_graph,
    run_speech_analysis_graph,
    run_weak_area_detection_graph,
)
from app.orchestration.state import AgentWorkflowState
from app.orchestration.types import AgentName

AgentExecutor = Callable[[AgentWorkflowState], AgentWorkflowState]
GraphBuilder = Callable[[], object]


class AgentRegistry:
    def __init__(self) -> None:
        self._executors: dict[AgentName, AgentExecutor] = {
            AgentName.RESUME_PARSER: run_resume_parser_graph,
            AgentName.RESUME_ANALYSIS: run_resume_analysis_graph,
            AgentName.QUESTION_GENERATION: run_question_generation_graph,
            AgentName.INTERVIEW_EVALUATION: run_interview_evaluation_graph,
            AgentName.SPEECH_ANALYSIS: run_speech_analysis_graph,
            AgentName.WEAK_AREA_DETECTION: run_weak_area_detection_graph,
            AgentName.FEEDBACK_REPORT: run_feedback_report_graph,
            AgentName.ROADMAP: run_roadmap_graph,
        }
        self._graph_builders: dict[AgentName, GraphBuilder] = {
            AgentName.RESUME_PARSER: build_resume_parser_graph,
            AgentName.RESUME_ANALYSIS: build_resume_analysis_graph,
            AgentName.QUESTION_GENERATION: build_question_generation_graph,
            AgentName.INTERVIEW_EVALUATION: build_interview_evaluation_graph,
            AgentName.SPEECH_ANALYSIS: build_speech_analysis_graph,
            AgentName.WEAK_AREA_DETECTION: build_weak_area_detection_graph,
            AgentName.FEEDBACK_REPORT: build_feedback_report_graph,
            AgentName.ROADMAP: build_roadmap_graph,
        }

    def get_executor(self, agent: AgentName) -> AgentExecutor:
        if agent not in self._executors:
            raise KeyError(f"Unknown agent: {agent}")
        return self._executors[agent]

    def get_graph_builder(self, agent: AgentName) -> GraphBuilder:
        return self._graph_builders[agent]


_default_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = AgentRegistry()
    return _default_registry
