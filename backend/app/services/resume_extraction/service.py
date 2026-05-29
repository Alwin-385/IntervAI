"""Orchestrates PDF parsing, cleaning, structuring, and chunking."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.resume_extraction import ExtractedResumeData, ResumeTextChunk
from app.services.resume_extraction.chunker import chunk_resume_text
from app.services.resume_extraction.pdf_parser import extract_raw_text_from_pdf
from app.services.resume_extraction.section_parser import parse_structured_resume
from app.services.resume_extraction.text_cleaner import clean_resume_text


@dataclass(frozen=True)
class ResumeExtractionResult:
    raw_text: str
    cleaned_text: str
    extracted_data: ExtractedResumeData
    chunks: list[ResumeTextChunk]


class ResumeExtractionService:
    """Pure extraction pipeline (no I/O)."""

    def extract_from_pdf_bytes(self, data: bytes) -> ResumeExtractionResult:
        raw_text = extract_raw_text_from_pdf(data)
        cleaned_text = clean_resume_text(raw_text)
        if len(cleaned_text.strip()) < 20:
            raise ValueError("Extracted text is too short to process")

        extracted_data = parse_structured_resume(cleaned_text)
        if not extracted_data.name:
            extracted_data = extracted_data.model_copy(
                update={"name": _fallback_name(cleaned_text)},
            )

        chunks = chunk_resume_text(cleaned_text)
        return ResumeExtractionResult(
            raw_text=raw_text[:80_000],
            cleaned_text=cleaned_text,
            extracted_data=extracted_data,
            chunks=chunks,
        )


def _fallback_name(cleaned_text: str) -> str | None:
    for line in cleaned_text.split("\n")[:4]:
        candidate = line.strip()
        if 2 <= len(candidate.split()) <= 5 and len(candidate) <= 60:
            return candidate
    return None
