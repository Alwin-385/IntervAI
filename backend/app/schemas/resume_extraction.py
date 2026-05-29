"""Schemas for resume text extraction."""

from uuid import UUID

from pydantic import Field

from app.models.enums import ResumeStatus
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class ExtractedResumeData(SchemaBase):
    """Structured fields parsed from resume text."""

    name: str | None = None
    contact: dict[str, str] = Field(
        default_factory=dict,
        description="Keys: email, phone, linkedin, github, address, website",
    )
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    internships: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class ResumeTextChunk(SchemaBase):
    index: int
    text: str
    char_start: int
    char_end: int


class ResumeExtractionStatusResponse(UUIDSchema, TimestampSchema):
    resume_id: UUID
    status: ResumeStatus
    extraction_error: str | None = None
    has_cleaned_text: bool = False
    chunk_count: int = 0
    extracted_data: ExtractedResumeData | None = None
