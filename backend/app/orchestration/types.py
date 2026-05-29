"""Orchestration type definitions (Phase 17)."""

from __future__ import annotations

import enum
from typing import Any, Literal

WorkflowStatus = Literal["pending", "running", "completed", "failed", "retrying"]


class AgentName(str, enum.Enum):
    RESUME_PARSER = "resume_parser"
    RESUME_ANALYSIS = "resume_analysis"
    QUESTION_GENERATION = "question_generation"
    INTERVIEW_EVALUATION = "interview_evaluation"
    SPEECH_ANALYSIS = "speech_analysis"
    WEAK_AREA_DETECTION = "weak_area_detection"
    FEEDBACK_REPORT = "feedback_report"
    ROADMAP = "roadmap"


class WorkflowName(str, enum.Enum):
    RESUME_PIPELINE = "resume_pipeline"
    QUESTION_GENERATION = "question_generation"
    POST_INTERVIEW = "post_interview"
    ROADMAP_GENERATION = "roadmap_generation"


AgentInput = dict[str, Any]
AgentOutput = dict[str, Any]
