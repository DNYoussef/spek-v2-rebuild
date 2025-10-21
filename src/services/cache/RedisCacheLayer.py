"""
RedisCacheLayer - High-performance caching with Redis backend

Features:
- TTL-based expiration (30-day default)
- Automatic serialization/deserialization
- Batch get/set operations
- Cache hit/miss metrics
- Namespace isolation

Week 4 Day 4
Version: 8.0.0
"""

import asyncio
import json
import pickle
from typing import Any, Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict
import time
import redis.asyncio as aioredis


# ============================================================================
# Types
# ============================================================================

@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    key: str
    value: Any
    ttl_seconds: int
    created_at: float
    namespace: str


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100


# ============================================================================
# RedisCacheLayer Class
# ============================================================================

class RedisCacheLayer:
    """
    Redis-backed caching layer with TTL and metrics.

    Features:
    - Automatic serialization (JSON for dicts, pickle for objects)
    - TTL management (30-day default)
    - Namespace isolation (project:key format)
    - Batch operations (get_many, set_many)
    - Hit/miss tracking

    Usage:
        cache = RedisCacheLayer(redis_url="redis://localhost:6379")
        await cache.connect()

        await cache.set("user:123", {"name": "Alice"}, ttl=3600)
        user = await cache.get("user:123")
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 2592000,  # 30 days
        namespace: str = "spek"
    ):
        """
        Initialize Redis cache layer.

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (30 days)
            namespace: Cache key namespace prefix
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.namespace = namespace

        self.client: Optional[aioredis.Redis] = None
        self.metrics = CacheMetrics()

    async def connect(self) -> None:
        """Connect to Redis server."""
        if self.client:
            return

        self.client = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=False  # Handle binary data
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.client:
            await self.client.close()
            self.client = None

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        return f"{self.namespace}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.client:
            raise RuntimeError("Cache not connected")

        namespaced_key = self._make_key(key)

        try:
            value = await self.client.get(namespaced_key)

            if value is None:
                self.metrics.misses += 1
                return None

            self.metrics.hits += 1
            return self._deserialize(value)

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Cache get error: {e}")

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)

        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Cache not connected")

        namespaced_key = self._make_key(key)
        ttl_seconds = ttl if ttl is not None else self.default_ttl

        try:
            serialized = self._serialize(value)
            await self.client.setex(
                namespaced_key,
                ttl_seconds,
                serialized
            )

            self.metrics.sets += 1
            return True

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Cache set error: {e}")

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted
        """
        if not self.client:
            raise RuntimeError("Cache not connected")

        namespaced_key = self._make_key(key)

        try:
            result = await self.client.delete(namespaced_key)

            if result > 0:
                self.metrics.deletes += 1
                return True

            return False

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Cache delete error: {e}")

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values in single round-trip.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of {key: value} for found keys
        """
        if not self.client:
            raise RuntimeError("Cache not connected")

        namespaced_keys = [self._make_key(k) for k in keys]

        try:
            values = await self.client.mget(namespaced_keys)

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
                    self.metrics.hits += 1
                else:
                    self.metrics.misses += 1

            return result

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Cache get_many error: {e}")

    async def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> int:
        """
        Set multiple values efficiently.

        Args:
            items: Dictionary of {key: value} to cache
            ttl: TTL in seconds (uses default if None)

        Returns:
            Number of items successfully set
        """
        if not self.client:
            raise RuntimeError("Cache not connected")

        ttl_seconds = ttl if ttl is not None else self.default_ttl

        try:
            pipeline = self.client.pipeline()

            for key, value in items.items():
                namespaced_key = self._make_key(key)
                serialized = self._serialize(value)
                pipeline.setex(namespaced_key, ttl_seconds, serialized)

            await pipeline.execute()

            self.metrics.sets += len(items)
            return len(items)

        except Exception as e:
            self.metrics.errors += 1
            raise RuntimeError(f"Cache set_many error: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.client:
            raise RuntimeError("Cache not connected")

        namespaced_key = self._make_key(key)
        result = await self.client.exists(namespaced_key)
        return result > 0

    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key in seconds."""
        if not self.client:
            raise RuntimeError("Cache not connected")

        namespaced_key = self._make_key(key)
        ttl = await self.client.ttl(namespaced_key)

        if ttl < 0:
            return None  # Key doesn't exist or has no TTL

        return ttl

    def _serialize(self, value: Any) -> bytes:
        """
        Serialize value for Redis storage.

        Uses JSON for dicts/lists, pickle for objects.
        """
        if isinstance(value, (dict, list, str, int, float, bool, type(None))):
            # Use JSON for simple types
            return json.dumps(value).encode('utf-8')
        else:
            # Use pickle for complex objects
            return pickle.dumps(value)

    def _deserialize(self, value: bytes) -> Any:
        """
        Deserialize value from Redis.

        Tries JSON first, falls back to pickle.
        """
        try:
            # Try JSON first
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(value)

    def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics."""
        return self.metrics

    def reset_metrics(self) -> None:
        """Reset metrics to zero."""
        self.metrics = CacheMetrics()


# ============================================================================
# Factory Functions
# ============================================================================

def create_cache_layer(
    redis_url: str = "redis://localhost:6379",
    namespace: str = "spek",
    ttl_days: int = 30
) -> RedisCacheLayer:
    """
    Factory function to create RedisCacheLayer.

    Args:
        redis_url: Redis connection URL
        namespace: Cache key namespace
        ttl_days: Default TTL in days

    Returns:
        RedisCacheLayer instance
    """
    ttl_seconds = ttl_days * 24 * 60 * 60
    return RedisCacheLayer(
        redis_url=redis_url,
        default_ttl=ttl_seconds,
        namespace=namespace
    )
