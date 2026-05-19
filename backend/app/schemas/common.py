"""Shared Pydantic schemas."""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimestampSchema(SchemaBase):
    created_at: datetime
    updated_at: datetime


class UUIDSchema(SchemaBase):
    id: UUID


class PaginationQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(SchemaBase, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class MessageResponse(SchemaBase):
    message: str


class ErrorDetail(SchemaBase):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(SchemaBase):
    error: ErrorDetail
