"""Health check schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["healthy"] = "healthy"
    service: str
    version: str
    environment: str
    timestamp: datetime = Field(description="UTC timestamp of the health check")


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    database: str
    service: str
    timestamp: datetime
