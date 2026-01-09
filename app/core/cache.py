from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Callable, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

class CacheManager:
    __slots__ = ("_redis", "_default_ttl", "_prefix", "_redis_url")

    def __init__(
        self,
        redis_url: str,
        default_ttl: int = 300,
        prefix: str = "fitmetrics",
    ) -> None:
        self._redis: Optional[Redis] = None
        self._default_ttl = default_ttl
        self._prefix = prefix
        self._redis_url = redis_url

    async def connect(self) -> None:
        self._redis = await aioredis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
        logger.info("Redis connection pool initialized")

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection pool closed")

    def _make_key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        if not self._redis:
            logger.warning("Redis not connected, cache disabled")
            return None

        full_key = self._make_key(key)
        try:
            value = await self._redis.get(full_key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as exc:
            logger.error("Cache GET error for %s: %s", full_key, exc)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        if not self._redis:
            logger.warning("Redis not connected, skipping cache")
            return False

        full_key = self._make_key(key)
        ttl = ttl or self._default_ttl

        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            await self._redis.setex(full_key, ttl, value)
            return True
        except Exception as exc:
            logger.error("Cache SET error for %s: %s", full_key, exc)
            return False

    async def delete(self, key: str) -> bool:
        if not self._redis:
            return False

        full_key = self._make_key(key)
        try:
            deleted = await self._redis.delete(full_key)
            return deleted > 0
        except Exception as exc:
            logger.error("Cache DELETE error for %s: %s", full_key, exc)
            return False

    async def delete_pattern(self, pattern: str) -> int:
        if not self._redis:
            return 0

        full_pattern = self._make_key(pattern)
        deleted_count = 0
        try:
            async for key in self._redis.scan_iter(match=full_pattern, count=100):
                await self._redis.delete(key)
                deleted_count += 1
            logger.info("Deleted %s keys matching %s", deleted_count, full_pattern)
            return deleted_count
        except Exception as exc:
            logger.error("Cache DELETE_PATTERN error: %s", exc)
            return deleted_count

    @asynccontextmanager
    async def pipeline(self):
        if not self._redis:
            raise RuntimeError("Redis not connected")

        pipe: Pipeline = self._redis.pipeline()
        try:
            yield pipe
        finally:
            pass

    async def health_check(self) -> bool:
        if not self._redis:
            return False
        try:
            pong = await self._redis.ping()
            return pong is True
        except Exception as exc:
            logger.error("Redis health check failed: %s", exc)
            return False


cache_manager = CacheManager(
    redis_url="",          # будет установлен в main.py из настроек
    default_ttl=300,
    prefix="fitmetrics",
)


def cached(
    key_pattern: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                try:
                    cache_key = key_pattern.format(**kwargs)
                except KeyError:
                    logger.warning("Cannot build cache key from pattern %s", key_pattern)
                    return await func(*args, **kwargs)

            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache HIT: %s", cache_key)
                return cached_result

            logger.debug("Cache MISS: %s", cache_key)
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
