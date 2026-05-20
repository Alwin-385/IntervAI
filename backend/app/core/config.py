"""Typed environment configuration via pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI Interview Intelligence Platform"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated allowed CORS origins",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = False

    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/intervai"
    )
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    clerk_secret_key: str | None = None
    clerk_jwt_issuer: str | None = Field(
        default=None,
        description="Clerk JWT issuer, e.g. https://your-app.clerk.accounts.dev",
    )

    storage_backend: Literal["local", "s3"] = "local"
    storage_local_path: str = "./storage/resumes"
    resume_max_size_bytes: int = 5 * 1024 * 1024  # 5 MB

    s3_bucket: str | None = None
    s3_region: str = "us-east-1"
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
