"""User API schemas."""

from uuid import UUID

from pydantic import EmailStr, Field

from app.models.enums import UserRole
from app.schemas.common import SchemaBase, TimestampSchema, UUIDSchema


class UserCreate(SchemaBase):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.CANDIDATE


class UserUpdate(SchemaBase):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(UUIDSchema, TimestampSchema):
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
