"""Weak area API schemas."""

from uuid import UUID

from pydantic import Field

from app.models.enums import WeakAreaSeverity
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class WeakAreaCreate(SchemaBase):
    area_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=128)
    severity: WeakAreaSeverity = WeakAreaSeverity.MEDIUM
    description: str = Field(min_length=1)
    resume_analysis_id: UUID | None = None


class WeakAreaUpdate(SchemaBase):
    area_name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = None
    severity: WeakAreaSeverity | None = None
    description: str | None = None
    resume_analysis_id: UUID | None = None


class WeakAreaResponse(UUIDSchema, TimestampSchema):
    user_id: UUID
    resume_analysis_id: UUID | None
    area_name: str
    category: str
    severity: WeakAreaSeverity
    description: str
