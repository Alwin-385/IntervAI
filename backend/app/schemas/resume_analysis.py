"""Resume analysis API schemas."""

from typing import Any
from uuid import UUID

from pydantic import Field

from app.models.enums import AnalysisStatus
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class ResumeAnalysisCreate(SchemaBase):
    resume_id: UUID
    status: AnalysisStatus = AnalysisStatus.PENDING
    overall_score: float | None = Field(default=None, ge=0, le=100)
    summary: str | None = None
    skills_extracted: list[Any] | None = None
    gaps_identified: list[Any] | None = None
    raw_analysis: dict[str, Any] | None = None


class ResumeAnalysisUpdate(SchemaBase):
    status: AnalysisStatus | None = None
    overall_score: float | None = Field(default=None, ge=0, le=100)
    summary: str | None = None
    skills_extracted: list[Any] | None = None
    gaps_identified: list[Any] | None = None
    raw_analysis: dict[str, Any] | None = None


class ResumeAnalysisResponse(UUIDSchema, TimestampSchema):
    resume_id: UUID
    status: AnalysisStatus
    overall_score: float | None
    summary: str | None
    skills_extracted: list[Any] | None
    gaps_identified: list[Any] | None
    raw_analysis: dict[str, Any] | None
