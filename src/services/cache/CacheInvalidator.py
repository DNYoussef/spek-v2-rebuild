"""
CacheInvalidator - Smart cache invalidation strategies

Strategies:
- Time-based (TTL expiration)
- Event-based (git commit, file change)
- Pattern-based (wildcard key matching)
- Dependency-based (cascade invalidation)

Week 4 Day 4
Version: 8.0.0
"""

import asyncio
from typing import List, Optional, Set, Dict, Any
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as aioredis


# ============================================================================
# Types
# ============================================================================

class InvalidationStrategy(Enum):
    """Cache invalidation strategies."""
    TIME_BASED = "time_based"      # TTL expiration
    EVENT_BASED = "event_based"    # Git commit, file change
    PATTERN_BASED = "pattern"      # Wildcard matching
    DEPENDENCY = "dependency"      # Cascade invalidation


@dataclass
class InvalidationEvent:
    """Event that triggers cache invalidation."""
    event_type: str
    affected_keys: List[str]
    metadata: Dict[str, Any]
    timestamp: float


@dataclass
class InvalidationResult:
    """Result of invalidation operation."""
    keys_deleted: int
    keys_scanned: int
    strategy: InvalidationStrategy
    duration_ms: int


# ============================================================================
# CacheInvalidator Class
# ============================================================================

class CacheInvalidator:
    """
    Smart cache invalidation with multiple strategies.

    Strategies:
    1. Time-based: TTL expiration (handled by Redis)
    2. Event-based: Git commit → invalidate project vectors
    3. Pattern-based: Delete keys matching pattern
    4. Dependency-based: Cascade to dependent caches

    Usage:
        invalidator = CacheInvalidator(redis_client)

        # Pattern invalidation
        await invalidator.invalidate_pattern("project:123:*")

        # Event-based invalidation
        await invalidator.on_git_commit("project:123", commit_hash)
    """

    def __init__(
        self,
        redis_client: aioredis.Redis,
        namespace: str = "spek"
    ):
        """
        Initialize cache invalidator.

        Args:
            redis_client: Connected Redis client
            namespace: Cache key namespace
        """
        self.client = redis_client
        self.namespace = namespace

        # Track invalidation events
        self.events: List[InvalidationEvent] = []

    async def invalidate_pattern(self, pattern: str) -> InvalidationResult:
        """
        Invalidate keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "project:*:vectors")

        Returns:
            InvalidationResult with deletion count
        """
        import time
        start_time = time.time()

        namespaced_pattern = f"{self.namespace}:{pattern}"

        # Scan for matching keys
        keys_to_delete = []
        async for key in self.client.scan_iter(match=namespaced_pattern):
            keys_to_delete.append(key)

        # Delete in batches
        deleted_count = 0
        if keys_to_delete:
            deleted_count = await self.client.delete(*keys_to_delete)

        duration_ms = int((time.time() - start_time) * 1000)

        return InvalidationResult(
            keys_deleted=deleted_count,
            keys_scanned=len(keys_to_delete),
            strategy=InvalidationStrategy.PATTERN_BASED,
            duration_ms=duration_ms
        )

    async def on_git_commit(
        self,
        project_id: str,
        commit_hash: str
    ) -> InvalidationResult:
        """
        Invalidate caches when git commit detected.

        Args:
            project_id: Project identifier
            commit_hash: New git commit hash

        Returns:
            InvalidationResult with deletion count
        """
        import time
        start_time = time.time()

        # Invalidate patterns affected by git commit
        patterns = [
            f"project:{project_id}:vectors:*",
            f"project:{project_id}:fingerprint",
            f"project:{project_id}:embeddings:*"
        ]

        total_deleted = 0
        for pattern in patterns:
            result = await self.invalidate_pattern(pattern)
            total_deleted += result.keys_deleted

        duration_ms = int((time.time() - start_time) * 1000)

        # Record event
        event = InvalidationEvent(
            event_type="git_commit",
            affected_keys=[f"project:{project_id}"],
            metadata={"commit_hash": commit_hash},
            timestamp=time.time()
        )
        self.events.append(event)

        return InvalidationResult(
            keys_deleted=total_deleted,
            keys_scanned=total_deleted,
            strategy=InvalidationStrategy.EVENT_BASED,
            duration_ms=duration_ms
        )

    async def on_file_change(
        self,
        project_id: str,
        file_paths: List[str]
    ) -> InvalidationResult:
        """
        Invalidate caches when files change.

        Args:
            project_id: Project identifier
            file_paths: List of changed file paths

        Returns:
            InvalidationResult with deletion count
        """
        import time
        start_time = time.time()

        # Invalidate file-specific caches
        keys_to_delete = []
        for file_path in file_paths:
            # Normalize file path for cache key
            normalized = file_path.replace('/', ':')
            key = f"{self.namespace}:project:{project_id}:file:{normalized}"
            keys_to_delete.append(key)

        deleted_count = 0
        if keys_to_delete:
            deleted_count = await self.client.delete(*keys_to_delete)

        duration_ms = int((time.time() - start_time) * 1000)

        # Record event
        event = InvalidationEvent(
            event_type="file_change",
            affected_keys=file_paths,
            metadata={"project_id": project_id, "file_count": len(file_paths)},
            timestamp=time.time()
        )
        self.events.append(event)

        return InvalidationResult(
            keys_deleted=deleted_count,
            keys_scanned=len(keys_to_delete),
            strategy=InvalidationStrategy.EVENT_BASED,
            duration_ms=duration_ms
        )

    async def invalidate_dependencies(
        self,
        root_key: str,
        dependency_map: Dict[str, List[str]]
    ) -> InvalidationResult:
        """
        Cascade invalidation to dependent keys.

        Args:
            root_key: Root cache key that changed
            dependency_map: {key: [dependent_keys]} mapping

        Returns:
            InvalidationResult with deletion count
        """
        import time
        start_time = time.time()

        # BFS to find all dependent keys
        to_invalidate = {root_key}
        visited = set()

        while to_invalidate:
            current_key = to_invalidate.pop()
            if current_key in visited:
                continue

            visited.add(current_key)

            # Add dependencies
            if current_key in dependency_map:
                for dep in dependency_map[current_key]:
                    if dep not in visited:
                        to_invalidate.add(dep)

        # Delete all dependent keys
        namespaced_keys = [
            f"{self.namespace}:{k}" for k in visited
        ]

        deleted_count = 0
        if namespaced_keys:
            deleted_count = await self.client.delete(*namespaced_keys)

        duration_ms = int((time.time() - start_time) * 1000)

        return InvalidationResult(
            keys_deleted=deleted_count,
            keys_scanned=len(visited),
            strategy=InvalidationStrategy.DEPENDENCY,
            duration_ms=duration_ms
        )

    async def invalidate_by_tags(
        self,
        tags: List[str]
    ) -> InvalidationResult:
        """
        Invalidate all keys with matching tags.

        Args:
            tags: List of tags to invalidate

        Returns:
            InvalidationResult with deletion count
        """
        import time
        start_time = time.time()

        total_deleted = 0
        for tag in tags:
            pattern = f"tag:{tag}:*"
            result = await self.invalidate_pattern(pattern)
            total_deleted += result.keys_deleted

        duration_ms = int((time.time() - start_time) * 1000)

        return InvalidationResult(
            keys_deleted=total_deleted,
            keys_scanned=total_deleted,
            strategy=InvalidationStrategy.PATTERN_BASED,
            duration_ms=duration_ms
        )

    async def clear_namespace(self) -> InvalidationResult:
        """
        Clear all keys in namespace (dangerous!).

        Returns:
            InvalidationResult with deletion count
        """
        import time
        start_time = time.time()

        pattern = f"{self.namespace}:*"

        keys_to_delete = []
        async for key in self.client.scan_iter(match=pattern):
            keys_to_delete.append(key)

        deleted_count = 0
        if keys_to_delete:
            deleted_count = await self.client.delete(*keys_to_delete)

        duration_ms = int((time.time() - start_time) * 1000)

        return InvalidationResult(
            keys_deleted=deleted_count,
            keys_scanned=len(keys_to_delete),
            strategy=InvalidationStrategy.PATTERN_BASED,
            duration_ms=duration_ms
        )

    def get_recent_events(self, limit: int = 10) -> List[InvalidationEvent]:
        """Get recent invalidation events."""
        return self.events[-limit:]

    def clear_events(self) -> None:
        """Clear invalidation event history."""
        self.events.clear()


# ============================================================================
# Factory Functions
# ============================================================================

def create_invalidator(
    redis_client: aioredis.Redis,
    namespace: str = "spek"
) -> CacheInvalidator:
    """
    Factory function to create CacheInvalidator.

    Args:
        redis_client: Connected Redis client
        namespace: Cache key namespace

    Returns:
        CacheInvalidator instance
    """
    return CacheInvalidator(
        redis_client=redis_client,
        namespace=namespace
    )
