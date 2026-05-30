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
    resume_extraction_mode: Literal["background", "celery"] = Field(
        default="background",
        description="background = thread; celery = Redis Celery worker (Phase 18)",
    )
    background_jobs_enabled: bool = Field(
        default=True,
        description="Track and dispatch long-running work via background jobs",
    )
    background_jobs_mode: Literal["thread", "celery", "auto"] = Field(
        default="auto",
        description="auto = Celery when Redis broker is reachable, else thread",
    )
    background_jobs_async_resume_extraction: bool = True
    background_jobs_async_resume_analysis: bool = True
    background_jobs_async_question_generation: bool = True
    background_jobs_async_answer_evaluation: bool = True
    background_jobs_async_roadmap_generation: bool = True

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_request_timeout_seconds: float = 45.0
    qdrant_timeout_seconds: float = 5.0
    resume_analysis_skip_embeddings: bool = Field(
        default=True,
        description="Skip Qdrant indexing (faster; set false when Qdrant is running)",
    )
    resume_analysis_heuristic_only: bool = Field(
        default=True,
        description="Use fast structured scoring (set false + OPENAI_API_KEY for GPT analysis)",
    )
    interview_questions_heuristic_only: bool = Field(
        default=True,
        description="Use fast template-based questions (recommended). False calls OpenAI and may be slow.",
    )
    interview_questions_use_openai: bool = Field(
        default=False,
        description="When true and OPENAI_API_KEY is set, use GPT instead of templates",
    )
    interview_questions_skip_rag: bool = Field(
        default=True,
        description="Skip Qdrant retrieval during question generation",
    )
    answer_evaluation_heuristic_only: bool = Field(
        default=True,
        description="Use rubric-based answer scoring (no API key). False + OPENAI_API_KEY = GPT evaluation.",
    )
    orchestration_enabled: bool = Field(
        default=True,
        description="Route AI agents through the Phase 17 orchestration layer (retry, validation, logging).",
    )
    orchestration_max_retries: int = Field(default=3, ge=1, le=10)
    orchestration_retry_delay_seconds: float = Field(default=0.5, ge=0.1, le=30.0)
    orchestration_use_langgraph_invoke: bool = Field(
        default=False,
        description="Use compiled LangGraph invoke(); False runs direct node functions (recommended).",
    )
    orchestration_feedback_llm: bool = Field(
        default=False,
        description="Polish feedback reports with GPT when OPENAI_API_KEY is set.",
    )

    clerk_secret_key: str | None = None
    clerk_jwt_issuer: str | None = Field(
        default=None,
        description="Clerk JWT issuer, e.g. https://your-app.clerk.accounts.dev",
    )

    storage_backend: Literal["local", "s3"] = "local"
    storage_local_path: str = "./storage/resumes"
    storage_audio_path: str = "./storage/audio"
    resume_max_size_bytes: int = 5 * 1024 * 1024  # 5 MB
    speech_max_size_bytes: int = 25 * 1024 * 1024  # 25 MB
    speech_transcription_mode: Literal["browser", "whisper"] = Field(
        default="browser",
        description=(
            "browser = free Web Speech API text from the client (no OpenAI). "
            "whisper = OpenAI Whisper (paid API; requires OPENAI_API_KEY)."
        ),
    )
    openai_whisper_model: str = "whisper-1"

    s3_bucket: str | None = None
    s3_region: str = "us-east-1"
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    # Security
    rate_limiting_enabled: bool = Field(
        default=True,
        description="Enable IP-based rate limiting (auto-disabled in development)",
    )
    rate_limit_default_rpm: int = Field(
        default=120, description="Default requests per minute per IP"
    )
    rate_limit_ai_rpm: int = Field(default=30, description="AI endpoint requests per minute per IP")
    rate_limit_upload_rpm: int = Field(default=10, description="Upload requests per minute per IP")

    # Monitoring
    sentry_dsn: str | None = Field(default=None, description="Sentry DSN for error tracking")
    sentry_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
