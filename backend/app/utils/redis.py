"""Redis connection utilities."""

from functools import lru_cache

import redis.asyncio as aioredis

from app.core.config import Settings, get_settings


@lru_cache
def get_redis_pool(settings: Settings | None = None) -> aioredis.ConnectionPool:
    cfg = settings or get_settings()
    return aioredis.ConnectionPool.from_url(
        str(cfg.redis_url),
        decode_responses=True,
    )


async def get_redis() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=get_redis_pool())
