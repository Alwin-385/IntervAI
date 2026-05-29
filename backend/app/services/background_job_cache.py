"""Redis cache for fast job status polling (Phase 18)."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_CACHE_PREFIX = "job:"
_DEFAULT_TTL = 86_400  # 24h


def _client():
    import redis

    settings = get_settings()
    return redis.from_url(
        str(settings.redis_url),
        socket_connect_timeout=1,
        decode_responses=True,
    )


def cache_job_snapshot(job_id: UUID | str, snapshot: dict[str, Any]) -> None:
    try:
        client = _client()
        key = f"{_CACHE_PREFIX}{job_id}"
        client.setex(key, _DEFAULT_TTL, json.dumps(snapshot, default=str))
    except Exception as exc:
        logger.debug("job_cache_set_failed", job_id=str(job_id), error=str(exc))


def get_cached_job(job_id: UUID | str) -> dict[str, Any] | None:
    try:
        client = _client()
        raw = client.get(f"{_CACHE_PREFIX}{job_id}")
        if not raw:
            return None
        return json.loads(raw)
    except Exception:
        return None


def invalidate_job_cache(job_id: UUID | str) -> None:
    try:
        client = _client()
        client.delete(f"{_CACHE_PREFIX}{job_id}")
    except Exception:
        pass
