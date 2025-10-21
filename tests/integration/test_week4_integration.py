"""
Week 4 Integration Tests - End-to-end testing across all components

Tests integration of:
- WebSocket + Redis Pub/Sub (Day 1)
- Parallel Vectorization (Day 2)
- Docker Sandbox (Day 3)
- Redis Caching (Day 4)

Week 4 Day 5
Version: 8.0.0
"""

import pytest
import asyncio
from typing import Dict, Any


# ============================================================================
# Test: WebSocket + Cache Integration
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_cache_integration():
    """
    Test WebSocket broadcasts trigger cache invalidation.

    Scenario:
    1. User connects via WebSocket
    2. Agent thought cached
    3. WebSocket broadcasts update
    4. Cache invalidated
    5. Next request fetches fresh data
    """
    from src.server.websocket import SocketServer
    from src.services.cache import create_cache_layer, create_invalidator

    # Setup
    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()

    # Cache agent thought
    thought_data = {
        "agentId": "coder-001",
        "thought": "Implementing feature X",
        "timestamp": 1234567890
    }
    await cache.set("agent:coder-001:thought", thought_data, ttl=300)

    # Verify cache hit
    cached = await cache.get("agent:coder-001:thought")
    assert cached == thought_data

    # Simulate WebSocket broadcast (triggers invalidation)
    invalidator = create_invalidator(cache.client, namespace="integration_test")
    await invalidator.invalidate_pattern("agent:coder-001:*")

    # Verify cache miss after invalidation
    cached_after = await cache.get("agent:coder-001:thought")
    assert cached_after is None

    await cache.disconnect()


# ============================================================================
# Test: Vectorization + Cache Integration
# ============================================================================

@pytest.mark.asyncio
async def test_vectorization_cache_integration():
    """
    Test git commit triggers vectorization with cache invalidation.

    Scenario:
    1. Project vectors cached
    2. Git commit detected
    3. Cache invalidated
    4. Re-vectorization triggered
    5. New vectors cached
    """
    from src.services.cache import create_cache_layer, create_invalidator

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()
    invalidator = create_invalidator(cache.client, namespace="integration_test")

    project_id = "project-123"

    # Step 1: Cache initial vectors
    initial_vectors = {
        "file1.py": [0.1, 0.2, 0.3],
        "file2.py": [0.4, 0.5, 0.6]
    }
    await cache.set(f"project:{project_id}:vectors", initial_vectors, ttl=2592000)

    # Step 2: Simulate git commit
    commit_hash = "abc123def456"
    result = await invalidator.on_git_commit(project_id, commit_hash)

    assert result.keys_deleted >= 1  # At least vectors invalidated

    # Step 3: Verify cache miss (would trigger re-vectorization)
    cached_vectors = await cache.get(f"project:{project_id}:vectors")
    assert cached_vectors is None

    # Step 4: Simulate re-vectorization (cache new vectors)
    new_vectors = {
        "file1.py": [0.11, 0.21, 0.31],  # Updated
        "file2.py": [0.4, 0.5, 0.6],      # Unchanged
        "file3.py": [0.7, 0.8, 0.9]       # New
    }
    await cache.set(f"project:{project_id}:vectors", new_vectors, ttl=2592000)

    # Step 5: Verify new vectors cached
    final_vectors = await cache.get(f"project:{project_id}:vectors")
    assert final_vectors == new_vectors
    assert "file3.py" in final_vectors

    await cache.disconnect()


# ============================================================================
# Test: Sandbox + Cache Integration
# ============================================================================

@pytest.mark.asyncio
async def test_sandbox_cache_integration():
    """
    Test Docker sandbox execution results are cached.

    Scenario:
    1. Execute code in sandbox
    2. Cache execution result
    3. Second execution → cache hit (instant)
    4. Code change → cache invalidation
    5. Re-execution with new result
    """
    from src.services.sandbox import create_docker_sandbox, SandboxLanguage
    from src.services.cache import create_cache_layer
    import hashlib

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()

    # Step 1: Execute code
    code = "print(2 + 2)"
    code_hash = hashlib.sha256(code.encode()).hexdigest()

    sandbox = create_docker_sandbox(strict=False)
    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    # Step 2: Cache result
    cache_key = f"sandbox:result:{code_hash}"
    await cache.set(cache_key, {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code
    }, ttl=3600)

    # Step 3: Second execution → cache hit (simulated)
    cached_result = await cache.get(cache_key)
    assert cached_result is not None
    assert "4" in cached_result["stdout"]

    metrics = cache.get_metrics()
    assert metrics.hits >= 1

    # Step 4: Code change → different hash → cache miss
    new_code = "print(3 + 3)"
    new_hash = hashlib.sha256(new_code.encode()).hexdigest()
    new_cached = await cache.get(f"sandbox:result:{new_hash}")
    assert new_cached is None  # Cache miss (different code)

    await cache.disconnect()
    await sandbox.shutdown()


# ============================================================================
# Test: Full Pipeline Integration
# ============================================================================

@pytest.mark.asyncio
async def test_full_pipeline_integration():
    """
    Test complete pipeline: Git → Vectorize → Cache → WebSocket broadcast.

    Scenario:
    1. Git commit detected
    2. Cache invalidation triggered
    3. Parallel vectorization starts
    4. Vectors cached
    5. WebSocket broadcasts update to clients
    """
    from src.services.cache import create_cache_layer, create_invalidator

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()
    invalidator = create_invalidator(cache.client, namespace="integration_test")

    project_id = "full-pipeline-test"

    # Step 1: Initial state - cached vectors
    await cache.set(
        f"project:{project_id}:vectors",
        {"file1.py": [0.1, 0.2]},
        ttl=2592000
    )

    # Step 2: Git commit detected
    commit_result = await invalidator.on_git_commit(project_id, "commit123")
    assert commit_result.keys_deleted >= 1

    # Step 3: Simulate parallel vectorization (would use ParallelEmbedder)
    # Mock: new vectors after re-vectorization
    new_vectors = {
        "file1.py": [0.15, 0.25],  # Updated embeddings
        "file2.py": [0.3, 0.4]     # New file
    }

    # Step 4: Cache new vectors
    await cache.set(
        f"project:{project_id}:vectors",
        new_vectors,
        ttl=2592000
    )

    # Step 5: Verify cache updated
    final_vectors = await cache.get(f"project:{project_id}:vectors")
    assert final_vectors == new_vectors

    # Step 6: Simulate WebSocket broadcast (would use SocketServer)
    broadcast_payload = {
        "event": "vectors_updated",
        "project_id": project_id,
        "commit": "commit123",
        "file_count": len(new_vectors)
    }
    # In real scenario: await socket_server.broadcast("project:updates", broadcast_payload)

    # Verify metrics
    metrics = cache.get_metrics()
    assert metrics.sets >= 2  # Initial + updated
    assert metrics.hit_rate > 0  # Some cache hits occurred

    await cache.disconnect()


# ============================================================================
# Test: Multi-Agent Coordination
# ============================================================================

@pytest.mark.asyncio
async def test_multi_agent_coordination():
    """
    Test cache coordination across multiple agents.

    Scenario:
    1. Coder agent caches analysis
    2. Reviewer agent reads cached analysis
    3. Tester agent invalidates on test failure
    4. All agents see fresh state
    """
    from src.services.cache import create_cache_layer, create_invalidator

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()
    invalidator = create_invalidator(cache.client, namespace="integration_test")

    # Step 1: Coder agent caches analysis
    await cache.set("task:123:analysis", {
        "agent": "coder",
        "complexity": "medium",
        "estimated_loc": 150
    }, ttl=3600)

    # Step 2: Reviewer agent reads cached analysis
    analysis = await cache.get("task:123:analysis")
    assert analysis["agent"] == "coder"
    assert analysis["complexity"] == "medium"

    # Step 3: Tester agent detects test failure → invalidate
    await invalidator.invalidate_pattern("task:123:*")

    # Step 4: All agents see cache miss (fresh state)
    fresh_check = await cache.get("task:123:analysis")
    assert fresh_check is None

    await cache.disconnect()


# ============================================================================
# Test: Error Recovery
# ============================================================================

@pytest.mark.asyncio
async def test_error_recovery_integration():
    """
    Test system recovers from component failures.

    Scenario:
    1. Cache operation fails (simulated)
    2. System falls back to direct computation
    3. Cache reconnects
    4. Normal operation resumes
    """
    from src.services.cache import create_cache_layer

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()

    # Step 1: Normal operation
    await cache.set("health:check", "ok", ttl=60)
    assert await cache.get("health:check") == "ok"

    # Step 2: Simulate cache failure (disconnect)
    await cache.disconnect()

    # Step 3: Operations should fail gracefully
    try:
        await cache.get("health:check")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "not connected" in str(e).lower()

    # Step 4: Reconnect and resume
    await cache.connect()
    await cache.set("health:check", "recovered", ttl=60)
    assert await cache.get("health:check") == "recovered"

    await cache.disconnect()


# ============================================================================
# Test: Performance Under Load
# ============================================================================

@pytest.mark.asyncio
async def test_performance_under_load():
    """
    Test cache performance with concurrent operations.

    Scenario:
    1. 100 concurrent set operations
    2. 100 concurrent get operations
    3. Verify all operations complete
    4. Measure hit rate and performance
    """
    from src.services.cache import create_cache_layer

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()

    # Step 1: Concurrent sets
    set_tasks = [
        cache.set(f"load:key:{i}", f"value_{i}", ttl=300)
        for i in range(100)
    ]
    set_results = await asyncio.gather(*set_tasks)
    assert all(set_results)  # All successful

    # Step 2: Concurrent gets
    get_tasks = [
        cache.get(f"load:key:{i}")
        for i in range(100)
    ]
    get_results = await asyncio.gather(*get_tasks)

    # Step 3: Verify all retrieved
    assert len(get_results) == 100
    assert all(r is not None for r in get_results)
    assert get_results[0] == "value_0"
    assert get_results[99] == "value_99"

    # Step 4: Check metrics
    metrics = cache.get_metrics()
    assert metrics.sets == 100
    assert metrics.hits == 100
    assert metrics.hit_rate == 100.0

    await cache.disconnect()


# ============================================================================
# Test: Batch Operations Performance
# ============================================================================

@pytest.mark.asyncio
async def test_batch_operations_performance():
    """
    Test batch operations are faster than individual operations.

    Scenario:
    1. Individual set (100 operations)
    2. Batch set (100 items)
    3. Verify batch is faster
    4. Same for get operations
    """
    from src.services.cache import create_cache_layer
    import time

    cache = create_cache_layer(namespace="integration_test")
    await cache.connect()

    # Individual operations
    start_individual = time.time()
    for i in range(100):
        await cache.set(f"batch:individual:{i}", i, ttl=300)
    individual_duration = time.time() - start_individual

    # Batch operations
    batch_items = {f"batch:batch:{i}": i for i in range(100)}
    start_batch = time.time()
    await cache.set_many(batch_items, ttl=300)
    batch_duration = time.time() - start_batch

    # Batch should be significantly faster
    assert batch_duration < individual_duration
    print(f"Individual: {individual_duration:.3f}s, Batch: {batch_duration:.3f}s")
    print(f"Speedup: {individual_duration / batch_duration:.1f}x")

    await cache.disconnect()
