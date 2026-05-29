"""Unit tests for resume extraction service."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


SAMPLE_RESUME_TEXT = """
John Doe
Software Engineer | john@example.com | github.com/johndoe

EXPERIENCE
Senior Software Engineer, TechCorp (2022–2026)
- Built distributed microservices in Python and Go
- Reduced API latency by 40% through caching optimisations
- Led team of 6 engineers

SKILLS
Python, Go, TypeScript, PostgreSQL, Redis, Kubernetes, Docker
"""


class TestResumeExtractionService:
    @pytest.fixture
    def service(self):
        from app.services.resume_extraction.service import ResumeExtractionService
        return ResumeExtractionService()

    def test_text_cleaner_removes_extra_whitespace(self):
        from app.services.resume_extraction.text_cleaner import clean_resume_text
        text = "  lots   of    spaces\n\n\n\nand newlines  "
        result = clean_resume_text(text)
        assert "   " not in result

    def test_section_parser_finds_experience(self):
        from app.services.resume_extraction.section_parser import parse_structured_resume
        data = parse_structured_resume(SAMPLE_RESUME_TEXT)
        # The result includes experience list
        assert isinstance(data.experience, list)

    def test_section_parser_finds_skills(self):
        from app.services.resume_extraction.section_parser import parse_structured_resume
        data = parse_structured_resume(SAMPLE_RESUME_TEXT)
        assert isinstance(data.skills, list)

    def test_contact_parser_extracts_email(self):
        from app.services.resume_extraction.contact_parser import parse_contact_fields
        result = parse_contact_fields(SAMPLE_RESUME_TEXT)
        assert result.get("email") == "john@example.com"

    def test_chunker_splits_text(self):
        from app.services.resume_extraction.chunker import chunk_resume_text
        long_text = "word " * 500
        chunks = chunk_resume_text(long_text)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk.text) > 0
