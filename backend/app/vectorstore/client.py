"""Qdrant client factory."""

from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.core.config import Settings, get_settings


@lru_cache
def get_qdrant_client(settings: Settings | None = None) -> AsyncQdrantClient:
    cfg = settings or get_settings()
    return AsyncQdrantClient(
        url=cfg.qdrant_url,
        api_key=cfg.qdrant_api_key,
    )
