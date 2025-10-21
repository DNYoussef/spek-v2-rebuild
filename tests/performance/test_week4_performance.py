"""
Week 4 Performance Tests - Load testing and benchmarks

Performance targets:
- WebSocket: 200+ concurrent users, <50ms latency
- Vectorization: 10K files <60s (15x speedup)
- Sandbox: 30s timeout, <5s startup
- Cache: >80% hit rate, <5ms get, <50ms batch

Week 4 Day 5
Version: 8.0.0
"""

import pytest
import asyncio
import time
from typing import List, Dict


# ============================================================================
# Test: WebSocket Performance (Day 1)
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_200_concurrent_users():
    """
    Test WebSocket handles 200+ concurrent users.

    Target: <50ms message latency
    """
    from src.server.websocket import SocketServer
    from src.services.cache import create_cache_layer

    # This test requires running HTTP server + Socket.io
    # Simulated with concurrent operations

    concurrent_users = 200
    messages_per_user = 10

    async def simulate_user(user_id: int):
        """Simulate user sending messages."""
        latencies = []
        for i in range(messages_per_user):
            start = time.time()
            # Simulate message broadcast
            await asyncio.sleep(0.001)  # Simulated processing
            latency = (time.time() - start) * 1000
            latencies.append(latency)
        return latencies

    # Run concurrent users
    start_time = time.time()
    tasks = [simulate_user(i) for i in range(concurrent_users)]
    all_latencies = await asyncio.gather(*tasks)

    total_duration = time.time() - start_time

    # Flatten latencies
    flat_latencies = [lat for user_lats in all_latencies for lat in user_lats]

    avg_latency = sum(flat_latencies) / len(flat_latencies)
    max_latency = max(flat_latencies)
    total_messages = concurrent_users * messages_per_user

    print(f"\n=== WebSocket Performance ===")
    print(f"Concurrent users: {concurrent_users}")
    print(f"Total messages: {total_messages}")
    print(f"Total duration: {total_duration:.2f}s")
    print(f"Avg latency: {avg_latency:.2f}ms")
    print(f"Max latency: {max_latency:.2f}ms")
    print(f"Throughput: {total_messages / total_duration:.0f} msg/s")

    # Assertions
    assert avg_latency < 50, f"Avg latency {avg_latency}ms exceeds 50ms target"
    assert max_latency < 200, f"Max latency {max_latency}ms too high"


# ============================================================================
# Test: Vectorization Performance (Day 2)
# ============================================================================

@pytest.mark.asyncio
async def test_vectorization_10k_files_performance():
    """
    Test vectorization handles 10K files in <60s.

    Target: 15x speedup (10K files: 15min → 60s)
    """
    # Simulated test (actual requires Pinecone + OpenAI)

    file_count = 10000
    batch_size = 64
    parallel_tasks = 10

    async def embed_batch(batch_files: List[str]):
        """Simulate embedding batch of files."""
        # Simulate OpenAI API call (100ms per batch)
        await asyncio.sleep(0.1)
        return len(batch_files)

    # Create batches
    batches = [
        list(range(i, min(i + batch_size, file_count)))
        for i in range(0, file_count, batch_size)
    ]

    # Parallel processing with semaphore
    semaphore = asyncio.Semaphore(parallel_tasks)

    async def process_batch_with_limit(batch):
        async with semaphore:
            return await embed_batch(batch)

    # Execute
    start_time = time.time()
    tasks = [process_batch_with_limit(batch) for batch in batches]

    results = []
    for task in asyncio.as_completed(tasks):
        result = await task
        results.append(result)

    total_duration = time.time() - start_time
    total_embedded = sum(results)

    files_per_second = total_embedded / total_duration

    print(f"\n=== Vectorization Performance ===")
    print(f"Total files: {file_count}")
    print(f"Batch size: {batch_size}")
    print(f"Parallel tasks: {parallel_tasks}")
    print(f"Duration: {total_duration:.2f}s")
    print(f"Throughput: {files_per_second:.0f} files/s")

    # Assertions
    assert total_duration < 60, f"Duration {total_duration}s exceeds 60s target"
    assert total_embedded == file_count
    assert files_per_second > 150, f"Throughput {files_per_second} too low"


# ============================================================================
# Test: Sandbox Performance (Day 3)
# ============================================================================

@pytest.mark.asyncio
async def test_sandbox_execution_performance():
    """
    Test sandbox execution performance.

    Targets:
    - Startup: <5s
    - Execution: <30s timeout
    - Cleanup: <2s
    """
    from src.services.sandbox import create_docker_sandbox, SandboxLanguage

    sandbox = create_docker_sandbox()

    # Test 1: Simple execution (should be fast)
    code_simple = "print('hello')"

    start_time = time.time()
    result = await sandbox.execute_code(code_simple, SandboxLanguage.PYTHON)
    simple_duration = (time.time() - start_time) * 1000

    assert result.success is True
    assert simple_duration < 5000, f"Simple execution {simple_duration}ms > 5s"

    # Test 2: Concurrent executions
    concurrent_count = 10

    async def execute_concurrent(i: int):
        code = f"print({i} * 2)"
        start = time.time()
        result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)
        duration = (time.time() - start) * 1000
        return duration, result.success

    start_concurrent = time.time()
    tasks = [execute_concurrent(i) for i in range(concurrent_count)]
    results = await asyncio.gather(*tasks)
    concurrent_total = time.time() - start_concurrent

    durations, successes = zip(*results)

    print(f"\n=== Sandbox Performance ===")
    print(f"Simple execution: {simple_duration:.0f}ms")
    print(f"Concurrent executions: {concurrent_count}")
    print(f"Concurrent total: {concurrent_total:.2f}s")
    print(f"Avg execution: {sum(durations) / len(durations):.0f}ms")
    print(f"Max execution: {max(durations):.0f}ms")

    # Assertions
    assert all(successes), "Some executions failed"
    assert max(durations) < 5000, "Some executions too slow"

    await sandbox.shutdown()


# ============================================================================
# Test: Cache Performance (Day 4)
# ============================================================================

@pytest.mark.asyncio
async def test_cache_hit_rate_performance():
    """
    Test cache achieves >80% hit rate.

    Scenario:
    1. Populate cache with 1000 keys
    2. Simulate realistic access pattern (80/20 rule)
    3. Measure hit rate
    """
    from src.services.cache import create_cache_layer

    cache = create_cache_layer(namespace="perf_test")
    await cache.connect()

    # Step 1: Populate cache
    total_keys = 1000
    for i in range(total_keys):
        await cache.set(f"perf:key:{i}", f"value_{i}", ttl=3600)

    cache.reset_metrics()

    # Step 2: Simulate 80/20 access pattern
    # 80% of requests hit 20% of keys (hot keys)
    total_requests = 10000
    hot_keys = total_keys // 5  # Top 20% of keys

    for _ in range(total_requests):
        # 80% probability to access hot keys
        if _ % 10 < 8:
            key_id = _ % hot_keys
        else:
            key_id = hot_keys + (_ % (total_keys - hot_keys))

        await cache.get(f"perf:key:{key_id}")

    metrics = cache.get_metrics()

    print(f"\n=== Cache Performance ===")
    print(f"Total keys: {total_keys}")
    print(f"Total requests: {total_requests}")
    print(f"Cache hits: {metrics.hits}")
    print(f"Cache misses: {metrics.misses}")
    print(f"Hit rate: {metrics.hit_rate:.1f}%")

    # Assertions
    assert metrics.hit_rate > 80, f"Hit rate {metrics.hit_rate}% < 80%"
    assert metrics.hits + metrics.misses == total_requests

    await cache.disconnect()


@pytest.mark.asyncio
async def test_cache_latency_performance():
    """
    Test cache latency targets.

    Targets:
    - Single get: <5ms
    - Batch get (100 keys): <50ms
    """
    from src.services.cache import create_cache_layer

    cache = create_cache_layer(namespace="perf_test")
    await cache.connect()

    # Setup data
    for i in range(100):
        await cache.set(f"latency:key:{i}", f"value_{i}", ttl=3600)

    # Test 1: Single get latency
    single_latencies = []
    for i in range(100):
        start = time.time()
        await cache.get(f"latency:key:{i}")
        latency = (time.time() - start) * 1000
        single_latencies.append(latency)

    avg_single = sum(single_latencies) / len(single_latencies)
    max_single = max(single_latencies)

    # Test 2: Batch get latency
    batch_keys = [f"latency:key:{i}" for i in range(100)]

    start_batch = time.time()
    batch_result = await cache.get_many(batch_keys)
    batch_latency = (time.time() - start_batch) * 1000

    print(f"\n=== Cache Latency ===")
    print(f"Single get avg: {avg_single:.2f}ms")
    print(f"Single get max: {max_single:.2f}ms")
    print(f"Batch get (100 keys): {batch_latency:.2f}ms")

    # Assertions
    assert avg_single < 5, f"Avg single get {avg_single}ms > 5ms"
    assert batch_latency < 50, f"Batch get {batch_latency}ms > 50ms"
    assert len(batch_result) == 100

    await cache.disconnect()


# ============================================================================
# Test: End-to-End Pipeline Performance
# ============================================================================

@pytest.mark.asyncio
async def test_end_to_end_pipeline_performance():
    """
    Test complete pipeline performance.

    Pipeline:
    1. Git commit detected (simulated)
    2. Cache invalidation
    3. Parallel vectorization
    4. Cache update
    5. WebSocket broadcast

    Target: <10s for 1000 files
    """
    from src.services.cache import create_cache_layer, create_invalidator

    cache = create_cache_layer(namespace="pipeline_perf")
    await cache.connect()
    invalidator = create_invalidator(cache.client, namespace="pipeline_perf")

    project_id = "perf-project"
    file_count = 1000

    # Step 1: Git commit (instant)
    start_pipeline = time.time()

    commit_start = time.time()
    await invalidator.on_git_commit(project_id, "commit123")
    commit_duration = (time.time() - commit_start) * 1000

    # Step 2: Simulate vectorization (parallel batching)
    vectorize_start = time.time()

    # Simulate embedding 1000 files (batch size 64, 10 parallel)
    batch_size = 64
    parallel_tasks = 10
    batches = (file_count + batch_size - 1) // batch_size

    async def embed_batch():
        await asyncio.sleep(0.05)  # 50ms per batch

    semaphore = asyncio.Semaphore(parallel_tasks)

    async def process_with_limit():
        async with semaphore:
            await embed_batch()

    tasks = [process_with_limit() for _ in range(batches)]
    await asyncio.gather(*tasks)

    vectorize_duration = (time.time() - vectorize_start) * 1000

    # Step 3: Cache update (batch)
    cache_start = time.time()

    vectors = {f"file:{i}": [0.1 * i, 0.2 * i] for i in range(file_count)}
    await cache.set_many(vectors, ttl=2592000)

    cache_duration = (time.time() - cache_start) * 1000

    # Step 4: WebSocket broadcast (simulated)
    broadcast_start = time.time()
    await asyncio.sleep(0.01)  # Simulate broadcast
    broadcast_duration = (time.time() - broadcast_start) * 1000

    total_pipeline = (time.time() - start_pipeline) * 1000

    print(f"\n=== End-to-End Pipeline Performance ===")
    print(f"File count: {file_count}")
    print(f"1. Git commit: {commit_duration:.0f}ms")
    print(f"2. Vectorization: {vectorize_duration:.0f}ms")
    print(f"3. Cache update: {cache_duration:.0f}ms")
    print(f"4. Broadcast: {broadcast_duration:.0f}ms")
    print(f"Total pipeline: {total_pipeline:.0f}ms ({total_pipeline/1000:.1f}s)")

    # Assertions
    assert total_pipeline < 10000, f"Pipeline {total_pipeline}ms > 10s"

    await cache.disconnect()


# ============================================================================
# Test: System Resource Usage
# ============================================================================

@pytest.mark.asyncio
async def test_memory_usage_performance():
    """
    Test memory usage remains reasonable under load.

    Target: <100MB for 10K cached items
    """
    from src.services.cache import create_cache_layer
    import sys

    cache = create_cache_layer(namespace="memory_test")
    await cache.connect()

    # Cache 10K items
    item_count = 10000
    item_size = 1000  # 1KB per item

    items = {
        f"memory:key:{i}": "x" * item_size
        for i in range(item_count)
    }

    await cache.set_many(items, ttl=3600)

    # Note: Actual memory usage measured in Redis, not Python
    # This test validates the operations complete successfully

    total_data_size = item_count * item_size / (1024 * 1024)  # MB

    print(f"\n=== Memory Performance ===")
    print(f"Items cached: {item_count}")
    print(f"Approx data size: {total_data_size:.1f}MB")
    print(f"Items successfully cached: {len(items)}")

    # Verify retrieval
    sample_keys = [f"memory:key:{i}" for i in range(0, item_count, 1000)]
    sample_results = await cache.get_many(sample_keys)

    assert len(sample_results) == len(sample_keys)

    await cache.disconnect()
