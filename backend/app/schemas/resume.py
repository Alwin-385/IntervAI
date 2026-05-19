"""Resume API schemas."""

from uuid import UUID

from pydantic import Field

from app.models.enums import ResumeStatus
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class ResumeCreate(SchemaBase):
    user_id: UUID
    title: str = Field(min_length=1, max_length=255)
    file_name: str = Field(min_length=1, max_length=512)
    storage_path: str = Field(min_length=1, max_length=1024)
    content_text: str | None = None
    status: ResumeStatus = ResumeStatus.UPLOADED


class ResumeUpdate(SchemaBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    file_name: str | None = None
    storage_path: str | None = None
    content_text: str | None = None
    status: ResumeStatus | None = None


class ResumeResponse(UUIDSchema, TimestampSchema):
    user_id: UUID
    title: str
    file_name: str
    storage_path: str
    content_text: str | None
    status: ResumeStatus
