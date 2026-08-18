# Standard library
import json

# Redis
from redis import asyncio as aioredis

# Core
from app.core.config import settings


class CacheManager:
    def __init__(self):
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(settings.redis_url)
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        if not self.redis:
            return None

        try:
            value = await self.redis.get(key)

            if value is None:
                return None

            return json.loads(value)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl: int):
        """Set value in cache."""
        if not self.redis:
            return

        try:
            await self.redis.setex(key, ttl, json.dumps(value))
        except Exception:
            pass

    async def delete(self, key: str):
        """Delete value from cache."""
        if not self.redis:
            return

        try:
            await self.redis.delete(key)
        except Exception:
            pass

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern using SCAN (non-blocking)."""
        if not self.redis:
            return
        try:
            async for key in self.redis.scan_iter(pattern):
                await self.redis.delete(key)
        except Exception:
            pass

cache_manager = CacheManager()