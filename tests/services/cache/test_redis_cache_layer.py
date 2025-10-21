"""
Test suite for RedisCacheLayer - Redis caching functionality

Tests:
- Connection management
- Get/Set operations
- Batch operations (get_many, set_many)
- TTL management
- Metrics tracking
- Serialization (JSON, pickle)

Week 4 Day 4
Version: 8.0.0
"""

import pytest
import asyncio
from src.services.cache.RedisCacheLayer import (
    RedisCacheLayer,
    CacheMetrics,
    create_cache_layer
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def cache():
    """Create and connect cache instance."""
    cache = create_cache_layer(
        redis_url="redis://localhost:6379",
        namespace="test_spek",
        ttl_days=1
    )
    await cache.connect()
    yield cache
    await cache.disconnect()


@pytest.fixture
async def cleanup_cache(cache):
    """Cleanup test keys after test."""
    yield cache

    # Clean up test namespace
    if cache.client:
        pattern = f"{cache.namespace}:*"
        async for key in cache.client.scan_iter(match=pattern):
            await cache.client.delete(key)


# ============================================================================
# Test: Connection Management
# ============================================================================

@pytest.mark.asyncio
async def test_connect_disconnect():
    """Test Redis connection lifecycle."""
    cache = create_cache_layer()

    assert cache.client is None

    await cache.connect()
    assert cache.client is not None

    await cache.disconnect()
    assert cache.client is None


# ============================================================================
# Test: Basic Get/Set Operations
# ============================================================================

@pytest.mark.asyncio
async def test_set_and_get_string(cleanup_cache):
    """Test caching string value."""
    cache = cleanup_cache

    await cache.set("test_key", "hello world")
    result = await cache.get("test_key")

    assert result == "hello world"
    assert cache.metrics.sets == 1
    assert cache.metrics.hits == 1
    assert cache.metrics.misses == 0


@pytest.mark.asyncio
async def test_set_and_get_dict(cleanup_cache):
    """Test caching dictionary value."""
    cache = cleanup_cache

    data = {"name": "Alice", "age": 30, "roles": ["admin", "user"]}
    await cache.set("user:123", data)
    result = await cache.get("user:123")

    assert result == data
    assert result["name"] == "Alice"
    assert result["roles"] == ["admin", "user"]


@pytest.mark.asyncio
async def test_get_nonexistent_key(cleanup_cache):
    """Test getting non-existent key returns None."""
    cache = cleanup_cache

    result = await cache.get("nonexistent")

    assert result is None
    assert cache.metrics.misses == 1
    assert cache.metrics.hits == 0


@pytest.mark.asyncio
async def test_set_and_get_complex_object(cleanup_cache):
    """Test caching complex Python object."""
    cache = cleanup_cache

    class CustomObject:
        def __init__(self, value):
            self.value = value

    obj = CustomObject(42)
    await cache.set("complex", obj)
    result = await cache.get("complex")

    assert isinstance(result, CustomObject)
    assert result.value == 42


# ============================================================================
# Test: Batch Operations
# ============================================================================

@pytest.mark.asyncio
async def test_set_many(cleanup_cache):
    """Test batch set operation."""
    cache = cleanup_cache

    items = {
        "user:1": {"name": "Alice"},
        "user:2": {"name": "Bob"},
        "user:3": {"name": "Charlie"}
    }

    count = await cache.set_many(items)

    assert count == 3
    assert cache.metrics.sets == 3


@pytest.mark.asyncio
async def test_get_many(cleanup_cache):
    """Test batch get operation."""
    cache = cleanup_cache

    # Set up data
    await cache.set("user:1", {"name": "Alice"})
    await cache.set("user:2", {"name": "Bob"})

    # Get many
    result = await cache.get_many(["user:1", "user:2", "user:3"])

    assert len(result) == 2
    assert result["user:1"]["name"] == "Alice"
    assert result["user:2"]["name"] == "Bob"
    assert "user:3" not in result

    assert cache.metrics.hits == 2
    assert cache.metrics.misses == 1


# ============================================================================
# Test: TTL Management
# ============================================================================

@pytest.mark.asyncio
async def test_ttl_expiration(cleanup_cache):
    """Test TTL expiration (short TTL)."""
    cache = cleanup_cache

    # Set with 1 second TTL
    await cache.set("expire_test", "value", ttl=1)

    # Should exist immediately
    result = await cache.get("expire_test")
    assert result == "value"

    # Wait for expiration
    await asyncio.sleep(1.5)

    # Should be expired
    result = await cache.get("expire_test")
    assert result is None


@pytest.mark.asyncio
async def test_get_ttl(cleanup_cache):
    """Test getting remaining TTL."""
    cache = cleanup_cache

    await cache.set("ttl_test", "value", ttl=60)

    ttl = await cache.get_ttl("ttl_test")

    assert ttl is not None
    assert 55 <= ttl <= 60  # Account for execution time


@pytest.mark.asyncio
async def test_exists(cleanup_cache):
    """Test key existence check."""
    cache = cleanup_cache

    await cache.set("exists_test", "value")

    assert await cache.exists("exists_test") is True
    assert await cache.exists("nonexistent") is False


# ============================================================================
# Test: Delete Operations
# ============================================================================

@pytest.mark.asyncio
async def test_delete(cleanup_cache):
    """Test key deletion."""
    cache = cleanup_cache

    await cache.set("delete_test", "value")

    # Verify exists
    assert await cache.exists("delete_test") is True

    # Delete
    deleted = await cache.delete("delete_test")
    assert deleted is True

    # Verify deleted
    assert await cache.exists("delete_test") is False

    assert cache.metrics.deletes == 1


@pytest.mark.asyncio
async def test_delete_nonexistent(cleanup_cache):
    """Test deleting non-existent key."""
    cache = cleanup_cache

    deleted = await cache.delete("nonexistent")
    assert deleted is False


# ============================================================================
# Test: Metrics
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_tracking(cleanup_cache):
    """Test cache metrics tracking."""
    cache = cleanup_cache

    # Perform operations
    await cache.set("key1", "value1")
    await cache.get("key1")  # Hit
    await cache.get("key2")  # Miss
    await cache.delete("key1")

    metrics = cache.get_metrics()

    assert metrics.sets == 1
    assert metrics.hits == 1
    assert metrics.misses == 1
    assert metrics.deletes == 1
    assert metrics.hit_rate == 50.0  # 1 hit / (1 hit + 1 miss)


@pytest.mark.asyncio
async def test_reset_metrics(cleanup_cache):
    """Test resetting metrics."""
    cache = cleanup_cache

    await cache.set("key", "value")
    await cache.get("key")

    cache.reset_metrics()
    metrics = cache.get_metrics()

    assert metrics.sets == 0
    assert metrics.hits == 0
    assert metrics.misses == 0


# ============================================================================
# Test: Namespace Isolation
# ============================================================================

@pytest.mark.asyncio
async def test_namespace_isolation():
    """Test namespace isolation between caches."""
    cache1 = create_cache_layer(namespace="app1")
    cache2 = create_cache_layer(namespace="app2")

    await cache1.connect()
    await cache2.connect()

    # Set same key in different namespaces
    await cache1.set("shared_key", "value1")
    await cache2.set("shared_key", "value2")

    # Verify isolation
    result1 = await cache1.get("shared_key")
    result2 = await cache2.get("shared_key")

    assert result1 == "value1"
    assert result2 == "value2"

    await cache1.disconnect()
    await cache2.disconnect()


# ============================================================================
# Test: Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_operation_without_connection():
    """Test operations fail gracefully without connection."""
    cache = create_cache_layer()

    # Don't connect

    with pytest.raises(RuntimeError, match="Cache not connected"):
        await cache.get("key")

    with pytest.raises(RuntimeError, match="Cache not connected"):
        await cache.set("key", "value")
