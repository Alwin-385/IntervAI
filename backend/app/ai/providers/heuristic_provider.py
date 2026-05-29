"""Structured resume analysis using an evidence-based scoring rubric."""

from __future__ import annotations

from app.schemas.resume_analyzer import StructuredResumeAnalysis
from app.schemas.resume_extraction import ExtractedResumeData
from app.services.resume_scoring_rubric import audit_resume, score_resume

__all__ = ["build_heuristic_analysis"]


def build_heuristic_analysis(
    extracted: ExtractedResumeData,
    *,
    target_role: str | None,
    cleaned_text: str,
) -> StructuredResumeAnalysis:
    audit = audit_resume(extracted, target_role=target_role, cleaned_text=cleaned_text)
    return score_resume(audit)
