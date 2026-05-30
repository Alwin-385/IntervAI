"""Output validators for orchestrated agents (Phase 17)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError

from app.orchestration.types import AgentName
from app.schemas.answer_evaluator import StructuredAnswerEvaluation
from app.schemas.interview_questions_gen import GeneratedQuestion
from app.schemas.orchestration import FeedbackReport, WeakAreaDetectionOutput
from app.schemas.resume_analyzer import StructuredResumeAnalysis
from app.schemas.resume_extraction import ExtractedResumeData, ResumeTextChunk


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []
    normalized: dict[str, Any] | None = None


def validate_agent_output(agent: AgentName, output: dict[str, Any]) -> ValidationResult:
    try:
        normalized = _validate_for_agent(agent, output)
        return ValidationResult(valid=True, normalized=normalized)
    except ValidationError as exc:
        return ValidationResult(
            valid=False,
            errors=[f"{e['loc']}: {e['msg']}" for e in exc.errors()],
        )
    except Exception as exc:
        return ValidationResult(valid=False, errors=[str(exc)])


def _validate_for_agent(agent: AgentName, output: dict[str, Any]) -> dict[str, Any]:
    if agent == AgentName.RESUME_PARSER:
        ExtractedResumeData.model_validate(output.get("extracted_data") or {})
        chunks = output.get("chunks") or []
        for c in chunks:
            ResumeTextChunk.model_validate(c)
        if not (output.get("cleaned_text") or "").strip():
            raise ValueError("cleaned_text is required")
        return output

    if agent == AgentName.RESUME_ANALYSIS:
        return StructuredResumeAnalysis.model_validate(
            output.get("analysis") or output
        ).model_dump()

    if agent == AgentName.QUESTION_GENERATION:
        questions = output.get("questions") or []
        validated = [GeneratedQuestion.model_validate(q).model_dump() for q in questions]
        if not validated:
            raise ValueError("questions must not be empty")
        return {**output, "questions": validated}

    if agent == AgentName.INTERVIEW_EVALUATION:
        return StructuredAnswerEvaluation.model_validate(
            output.get("evaluation") or output
        ).model_dump()

    if agent == AgentName.SPEECH_ANALYSIS:
        if output.get("transcript") is None and not output.get("scores"):
            raise ValueError("speech analysis output missing scores")
        return output

    if agent == AgentName.WEAK_AREA_DETECTION:
        return WeakAreaDetectionOutput.model_validate(output).model_dump()

    if agent == AgentName.FEEDBACK_REPORT:
        return FeedbackReport.model_validate(output.get("report") or output).model_dump()

    if agent == AgentName.ROADMAP:
        phases = output.get("phases") or []
        if not phases and not output.get("summary"):
            raise ValueError("roadmap output must include phases or summary")
        return output

    return output
