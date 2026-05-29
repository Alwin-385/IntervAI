"""Phase 17 orchestration unit tests."""

from app.orchestration.types import AgentName
from app.orchestration.validators import validate_agent_output
from app.schemas.orchestration import FeedbackReport


def test_validate_feedback_report():
    report = FeedbackReport(
        executive_summary="Strong technical depth with room to improve communication pacing.",
        strengths=["Clear problem decomposition"],
        weaknesses=["Limited metrics in examples"],
    )
    result = validate_agent_output(
        AgentName.FEEDBACK_REPORT,
        {"report": report.model_dump(mode="json")},
    )
    assert result.valid is True
    assert result.normalized is not None


def test_validate_speech_output():
    result = validate_agent_output(
        AgentName.SPEECH_ANALYSIS,
        {
            "transcript": "I led the migration and improved latency by forty percent.",
            "scores": {"communication_score": 75, "confidence_score": 70},
        },
    )
    assert result.valid is True
