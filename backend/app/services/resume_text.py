"""Resolve resume body text and extraction-ready status for analysis."""

from __future__ import annotations

from app.models.enums import ResumeStatus
from app.models.resume import Resume
from app.schemas.resume_extraction import ExtractedResumeData

_LEGACY_STATUS: dict[str, ResumeStatus] = {
    "uploaded": ResumeStatus.QUEUED,
    "processing": ResumeStatus.EXTRACTING_RESUME,
    "ready": ResumeStatus.COMPLETED,
}


def normalize_resume_status(status: ResumeStatus | str) -> ResumeStatus:
    if isinstance(status, ResumeStatus):
        return status
    raw = str(status).lower()
    if raw in _LEGACY_STATUS:
        return _LEGACY_STATUS[raw]
    try:
        return ResumeStatus(raw)
    except ValueError:
        return ResumeStatus.QUEUED


def resolve_resume_text(resume: Resume) -> str:
    """Best available plain text for AI analysis."""
    if resume.cleaned_text and resume.cleaned_text.strip():
        return resume.cleaned_text.strip()
    if resume.content_text and resume.content_text.strip():
        return resume.content_text.strip()
    if resume.extracted_data:
        return text_from_extracted(resume.extracted_data)
    if resume.text_chunks:
        joined = "\n\n".join(
            c.get("text", "") if isinstance(c, dict) else str(c) for c in resume.text_chunks if c
        ).strip()
        if joined:
            return joined
    return ""


def text_from_extracted(data: dict) -> str:
    extracted = ExtractedResumeData.model_validate(data)
    blocks: list[str] = []
    if extracted.name:
        blocks.append(extracted.name)
    for label, items in (
        ("Skills", extracted.skills),
        ("Experience", extracted.experience),
        ("Education", extracted.education),
        ("Projects", extracted.projects),
        ("Internships", extracted.internships),
        ("Certifications", extracted.certifications),
        ("Achievements", extracted.achievements),
    ):
        if items:
            blocks.append(f"\n{label}\n" + "\n".join(items))
    return "\n\n".join(blocks).strip()


def is_ready_for_analysis(resume: Resume) -> bool:
    status = normalize_resume_status(resume.status)
    if status != ResumeStatus.COMPLETED:
        return False
    return bool(resolve_resume_text(resume))
