"""Map ORM resume rows to API responses."""

from __future__ import annotations

from app.models.enums import ResumeStatus
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse
from app.schemas.resume_extraction import ExtractedResumeData, ResumeTextChunk
from app.services.resume_extraction.contact_parser import (
    is_plausible_address,
    parse_contact_fields,
    parse_header_address,
)

_LEGACY_STATUS: dict[str, ResumeStatus] = {
    "uploaded": ResumeStatus.QUEUED,
    "processing": ResumeStatus.EXTRACTING_RESUME,
    "ready": ResumeStatus.COMPLETED,
}


def resume_to_response(resume: Resume) -> ResumeResponse:
    if isinstance(resume.status, ResumeStatus):
        raw_status = resume.status.value
    else:
        raw_status = str(resume.status)
    if raw_status in _LEGACY_STATUS:
        status = _LEGACY_STATUS[raw_status]
    else:
        try:
            status = ResumeStatus(raw_status)
        except ValueError:
            status = ResumeStatus.QUEUED

    extracted = None
    if resume.extracted_data:
        extracted = ExtractedResumeData.model_validate(resume.extracted_data)
        extracted = _enrich_contact(extracted, resume.cleaned_text)

    chunks = None
    if resume.text_chunks:
        chunks = [ResumeTextChunk.model_validate(c) for c in resume.text_chunks]

    return ResumeResponse(
        id=resume.id,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        user_id=resume.user_id,
        title=resume.title,
        file_name=resume.file_name,
        storage_path=resume.storage_path,
        storage_key=resume.storage_key,
        mime_type=resume.mime_type,
        file_size_bytes=resume.file_size_bytes,
        content_text=resume.content_text,
        cleaned_text=resume.cleaned_text,
        extracted_data=extracted,
        text_chunks=chunks,
        extraction_error=resume.extraction_error,
        status=status,
    )


def _enrich_contact(
    extracted: ExtractedResumeData,
    cleaned_text: str | None,
) -> ExtractedResumeData:
    """Fill missing contact fields from cleaned header text (e.g. legacy extractions)."""
    if not cleaned_text:
        return extracted
    contact = dict(extracted.contact or {})
    parsed = parse_contact_fields(cleaned_text[:4000])
    updated = False
    for key, value in parsed.items():
        if not value or contact.get(key):
            continue
        if key == "address" and not is_plausible_address(value):
            continue
        contact[key] = value
        updated = True
    if not contact.get("address") and extracted.name:
        header_addr = parse_header_address(cleaned_text[:2500], extracted.name)
        if header_addr:
            contact["address"] = header_addr
            updated = True
    if contact.get("address") and not is_plausible_address(contact["address"]):
        contact.pop("address", None)
        updated = True
    if not updated:
        return extracted
    return extracted.model_copy(update={"contact": contact})
