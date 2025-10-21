"""
Test suite for CacheInvalidator - Smart invalidation strategies

Tests:
- Pattern-based invalidation
- Event-based invalidation (git commit, file change)
- Dependency-based invalidation
- Tag-based invalidation
- Event tracking

Week 4 Day 4
Version: 8.0.0
"""

import pytest
import asyncio
import redis.asyncio as aioredis
from src.services.cache.CacheInvalidator import (
    CacheInvalidator,
    InvalidationStrategy,
    create_invalidator
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def redis_client():
    """Create Redis client."""
    client = await aioredis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=False
    )
    yield client
    await client.close()


@pytest.fixture
async def invalidator(redis_client):
    """Create invalidator instance."""
    inv = create_invalidator(redis_client, namespace="test_spek")
    yield inv
    # Cleanup
    await inv.clear_namespace()
    inv.clear_events()


@pytest.fixture
async def setup_test_data(redis_client):
    """Setup test cache data."""
    # Create test keys
    test_keys = {
        "test_spek:project:123:vectors:file1": b"vector1",
        "test_spek:project:123:vectors:file2": b"vector2",
        "test_spek:project:123:fingerprint": b"abc123",
        "test_spek:project:456:vectors:file1": b"vector3",
        "test_spek:tag:python:key1": b"data1",
        "test_spek:tag:python:key2": b"data2",
        "test_spek:tag:javascript:key1": b"data3"
    }

    for key, value in test_keys.items():
        await redis_client.set(key, value)

    yield

    # Cleanup
    pattern = "test_spek:*"
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)


# ============================================================================
# Test: Pattern-Based Invalidation
# ============================================================================

@pytest.mark.asyncio
async def test_invalidate_pattern(invalidator, setup_test_data):
    """Test pattern-based invalidation."""
    result = await invalidator.invalidate_pattern("project:123:vectors:*")

    assert result.strategy == InvalidationStrategy.PATTERN_BASED
    assert result.keys_deleted == 2  # file1 and file2
    assert result.keys_scanned == 2


@pytest.mark.asyncio
async def test_invalidate_pattern_no_matches(invalidator):
    """Test pattern with no matches."""
    result = await invalidator.invalidate_pattern("nonexistent:*")

    assert result.keys_deleted == 0
    assert result.keys_scanned == 0


@pytest.mark.asyncio
async def test_invalidate_all_projects(invalidator, setup_test_data):
    """Test invalidating all projects."""
    result = await invalidator.invalidate_pattern("project:*")

    assert result.keys_deleted >= 3  # At least 3 project keys


# ============================================================================
# Test: Event-Based Invalidation
# ============================================================================

@pytest.mark.asyncio
async def test_on_git_commit(invalidator, setup_test_data):
    """Test git commit event invalidation."""
    result = await invalidator.on_git_commit(
        project_id="123",
        commit_hash="def456"
    )

    assert result.strategy == InvalidationStrategy.EVENT_BASED
    assert result.keys_deleted >= 2  # vectors + fingerprint

    # Verify event recorded
    events = invalidator.get_recent_events()
    assert len(events) == 1
    assert events[0].event_type == "git_commit"
    assert events[0].metadata["commit_hash"] == "def456"


@pytest.mark.asyncio
async def test_on_file_change(invalidator, redis_client):
    """Test file change event invalidation."""
    # Setup file-specific cache
    await redis_client.set(
        "test_spek:project:123:file:src:main.py",
        b"file_data"
    )

    result = await invalidator.on_file_change(
        project_id="123",
        file_paths=["src/main.py"]
    )

    assert result.strategy == InvalidationStrategy.EVENT_BASED
    assert result.keys_deleted == 1

    # Verify event recorded
    events = invalidator.get_recent_events()
    assert len(events) == 1
    assert events[0].event_type == "file_change"


@pytest.mark.asyncio
async def test_on_file_change_multiple_files(invalidator, redis_client):
    """Test file change with multiple files."""
    # Setup multiple file caches
    await redis_client.set(
        "test_spek:project:123:file:src:main.py",
        b"data1"
    )
    await redis_client.set(
        "test_spek:project:123:file:src:utils.py",
        b"data2"
    )

    result = await invalidator.on_file_change(
        project_id="123",
        file_paths=["src/main.py", "src/utils.py"]
    )

    assert result.keys_deleted == 2


# ============================================================================
# Test: Dependency-Based Invalidation
# ============================================================================

@pytest.mark.asyncio
async def test_invalidate_dependencies(invalidator, redis_client):
    """Test cascade invalidation with dependencies."""
    # Setup cache keys with dependencies
    await redis_client.set("test_spek:root", b"root_data")
    await redis_client.set("test_spek:child1", b"child1_data")
    await redis_client.set("test_spek:child2", b"child2_data")
    await redis_client.set("test_spek:grandchild", b"grandchild_data")

    # Define dependency tree
    dependency_map = {
        "root": ["child1", "child2"],
        "child1": ["grandchild"],
        "child2": []
    }

    result = await invalidator.invalidate_dependencies(
        root_key="root",
        dependency_map=dependency_map
    )

    assert result.strategy == InvalidationStrategy.DEPENDENCY
    assert result.keys_deleted == 4  # root + child1 + child2 + grandchild
    assert result.keys_scanned == 4


@pytest.mark.asyncio
async def test_invalidate_dependencies_circular(invalidator, redis_client):
    """Test dependency invalidation handles circular references."""
    # Setup circular dependency
    await redis_client.set("test_spek:a", b"data_a")
    await redis_client.set("test_spek:b", b"data_b")

    dependency_map = {
        "a": ["b"],
        "b": ["a"]  # Circular!
    }

    result = await invalidator.invalidate_dependencies(
        root_key="a",
        dependency_map=dependency_map
    )

    # Should handle circular reference gracefully
    assert result.keys_deleted == 2
    assert result.keys_scanned == 2


# ============================================================================
# Test: Tag-Based Invalidation
# ============================================================================

@pytest.mark.asyncio
async def test_invalidate_by_tags(invalidator, setup_test_data):
    """Test tag-based invalidation."""
    result = await invalidator.invalidate_by_tags(["python"])

    assert result.strategy == InvalidationStrategy.PATTERN_BASED
    assert result.keys_deleted == 2  # python:key1 and python:key2


@pytest.mark.asyncio
async def test_invalidate_multiple_tags(invalidator, setup_test_data):
    """Test invalidating multiple tags."""
    result = await invalidator.invalidate_by_tags(["python", "javascript"])

    assert result.keys_deleted == 3  # python:key1, python:key2, javascript:key1


# ============================================================================
# Test: Namespace Operations
# ============================================================================

@pytest.mark.asyncio
async def test_clear_namespace(invalidator, setup_test_data):
    """Test clearing entire namespace."""
    result = await invalidator.clear_namespace()

    assert result.strategy == InvalidationStrategy.PATTERN_BASED
    assert result.keys_deleted >= 7  # All test keys


# ============================================================================
# Test: Event Tracking
# ============================================================================

@pytest.mark.asyncio
async def test_event_tracking(invalidator, setup_test_data):
    """Test invalidation event tracking."""
    # Trigger multiple events
    await invalidator.on_git_commit("123", "abc123")
    await invalidator.on_file_change("456", ["file1.py"])

    events = invalidator.get_recent_events()

    assert len(events) == 2
    assert events[0].event_type == "git_commit"
    assert events[1].event_type == "file_change"


@pytest.mark.asyncio
async def test_clear_events(invalidator, setup_test_data):
    """Test clearing event history."""
    await invalidator.on_git_commit("123", "abc123")

    invalidator.clear_events()
    events = invalidator.get_recent_events()

    assert len(events) == 0


@pytest.mark.asyncio
async def test_recent_events_limit(invalidator, setup_test_data):
    """Test recent events respects limit."""
    # Trigger many events
    for i in range(20):
        await invalidator.on_git_commit(f"project:{i}", f"hash{i}")

    events = invalidator.get_recent_events(limit=5)

    assert len(events) == 5


# ============================================================================
# Test: Performance
# ============================================================================

@pytest.mark.asyncio
async def test_invalidation_performance(invalidator, redis_client):
    """Test invalidation completes quickly."""
    # Create many keys
    for i in range(100):
        await redis_client.set(f"test_spek:perf:key{i}", b"data")

    result = await invalidator.invalidate_pattern("perf:*")

    assert result.keys_deleted == 100
    assert result.duration_ms < 1000  # Should complete in <1s
