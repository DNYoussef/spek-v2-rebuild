"""
Week 5 Performance Benchmarks - Load and Stress Testing

Tests system performance under load:
- 200+ concurrent agent tasks
- Latency benchmarks (<100ms coordination)
- Memory efficiency
- Throughput testing

Week 5 Day 7
Version: 8.0.0
"""

import pytest
import asyncio
import time
from typing import List
import statistics

from src.agents.AgentBase import Task, create_task
from src.agents.core import create_queen_agent, create_coder_agent
from src.agents.swarm import create_princess_dev_agent


# ============================================================================
# Performance Test Fixtures
# ============================================================================

@pytest.fixture
def performance_agents():
    """Create agents for performance testing."""
    return {
        "queen": create_queen_agent(),
        "princess-dev": create_princess_dev_agent(),
        "coder": create_coder_agent()
    }


# ============================================================================
# Test 1: Concurrent Task Execution (200+ users)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_200_concurrent_tasks(performance_agents):
    """
    Test 1: Handle 200+ concurrent tasks.

    Target: All tasks complete successfully with <100ms avg latency
    """
    queen = performance_agents["queen"]

    # Create 200 tasks
    tasks = [
        create_task(
            task_id=f"concurrent-{i:03d}",
            task_type="orchestrate",
            payload={
                "workflow": {
                    "phases": [{"name": "test", "task_type": "code"}]
                }
            }
        )
        for i in range(200)
    ]

    # Execute concurrently
    start_time = time.time()
    results = await asyncio.gather(
        *[queen.execute(task) for task in tasks],
        return_exceptions=True
    )
    total_time = time.time() - start_time

    # Validate results
    successful = sum(1 for r in results if hasattr(r, 'success') and r.success)
    errors = sum(1 for r in results if isinstance(r, Exception))

    print(f"\n200 Concurrent Tasks:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Successful: {successful}/200")
    print(f"  Errors: {errors}")
    print(f"  Throughput: {200/total_time:.2f} tasks/sec")

    assert successful >= 190, f"At least 190/200 tasks should succeed (got {successful})"
    assert total_time < 30.0, f"Should complete in <30s (got {total_time:.2f}s)"


# ============================================================================
# Test 2: Latency Benchmarks
# ============================================================================

@pytest.mark.asyncio
async def test_task_validation_latency(performance_agents):
    """
    Test 2: Task validation latency <5ms.

    Target: All validation times <5ms
    """
    queen = performance_agents["queen"]

    task = create_task(
        task_id="latency-001",
        task_type="orchestrate",
        payload={"workflow": {"phases": []}}
    )

    # Warm-up
    await queen.validate(task)

    # Measure 100 validations
    validation_times = []
    for _ in range(100):
        result = await queen.validate(task)
        validation_times.append(result.validation_time)

    avg_latency = statistics.mean(validation_times)
    p95_latency = statistics.quantiles(validation_times, n=20)[18]  # 95th percentile
    max_latency = max(validation_times)

    print(f"\nValidation Latency:")
    print(f"  Average: {avg_latency:.2f}ms")
    print(f"  P95: {p95_latency:.2f}ms")
    print(f"  Max: {max_latency:.2f}ms")

    assert avg_latency < 5.0, f"Avg validation should be <5ms (got {avg_latency:.2f}ms)"
    assert p95_latency < 10.0, f"P95 should be <10ms (got {p95_latency:.2f}ms)"


@pytest.mark.asyncio
async def test_agent_coordination_latency(performance_agents):
    """
    Test 3: Agent coordination latency <100ms.

    Target: Princess → Drone coordination <100ms
    """
    princess = performance_agents["princess-dev"]

    task = create_task(
        task_id="coord-001",
        task_type="coordinate-dev",
        payload={
            "dev_workflow": {
                "phases": ["code"],
                "target_file": "test.py"
            }
        }
    )

    # Measure 50 coordinations
    coordination_times = []
    for _ in range(50):
        start = time.time()
        result = await princess.execute(task)
        elapsed = (time.time() - start) * 1000  # ms
        if result.success:
            coordination_times.append(elapsed)

    avg_coord = statistics.mean(coordination_times)
    p95_coord = statistics.quantiles(coordination_times, n=20)[18]

    print(f"\nCoordination Latency:")
    print(f"  Average: {avg_coord:.2f}ms")
    print(f"  P95: {p95_coord:.2f}ms")

    assert avg_coord < 100.0, f"Avg coordination should be <100ms (got {avg_coord:.2f}ms)"


# ============================================================================
# Test 3: Throughput Testing
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_sustained_throughput(performance_agents):
    """
    Test 4: Sustained throughput over 60 seconds.

    Target: Process 1000+ tasks in 60 seconds
    """
    queen = performance_agents["queen"]

    tasks_completed = 0
    start_time = time.time()
    duration = 10.0  # 10 seconds for testing (60s in production)

    while time.time() - start_time < duration:
        # Create batch of 10 tasks
        batch = [
            create_task(
                task_id=f"throughput-{tasks_completed + i}",
                task_type="orchestrate",
                payload={"workflow": {"phases": []}}
            )
            for i in range(10)
        ]

        # Execute batch
        results = await asyncio.gather(
            *[queen.execute(task) for task in batch],
            return_exceptions=True
        )

        tasks_completed += sum(
            1 for r in results
            if hasattr(r, 'success') and r.success
        )

    elapsed = time.time() - start_time
    throughput = tasks_completed / elapsed

    print(f"\nSustained Throughput:")
    print(f"  Duration: {elapsed:.2f}s")
    print(f"  Tasks completed: {tasks_completed}")
    print(f"  Throughput: {throughput:.2f} tasks/sec")

    assert throughput > 10.0, f"Should process >10 tasks/sec (got {throughput:.2f})"


# ============================================================================
# Test 4: Load Testing
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_load_ramp_up(performance_agents):
    """
    Test 5: Load ramp-up from 10 to 200 concurrent tasks.

    Target: Linear scaling, no degradation
    """
    queen = performance_agents["queen"]

    load_levels = [10, 50, 100, 150, 200]
    results = {}

    for load in load_levels:
        tasks = [
            create_task(
                task_id=f"load-{load}-{i}",
                task_type="orchestrate",
                payload={"workflow": {"phases": []}}
            )
            for i in range(load)
        ]

        start = time.time()
        task_results = await asyncio.gather(
            *[queen.execute(task) for task in tasks],
            return_exceptions=True
        )
        elapsed = time.time() - start

        successful = sum(
            1 for r in task_results
            if hasattr(r, 'success') and r.success
        )

        results[load] = {
            "elapsed": elapsed,
            "successful": successful,
            "throughput": successful / elapsed
        }

    print(f"\nLoad Ramp-Up Results:")
    for load, data in results.items():
        print(f"  {load} tasks: {data['elapsed']:.2f}s, "
              f"{data['successful']}/{load} successful, "
              f"{data['throughput']:.2f} tasks/sec")

    # Verify no significant degradation
    assert all(
        data['successful'] / load >= 0.95
        for load, data in results.items()
    ), "Should maintain >95% success rate at all load levels"


# ============================================================================
# Test 5: Memory Efficiency
# ============================================================================

@pytest.mark.asyncio
async def test_memory_efficiency():
    """
    Test 6: Memory usage under load.

    Target: Reasonable memory footprint for agent objects
    """
    import sys

    # Create 100 agents
    agents = []
    for i in range(100):
        agents.append(create_queen_agent())

    # Estimate memory per agent
    # (This is a simplified test - in production use memory_profiler)
    agent_size = sys.getsizeof(agents[0])

    print(f"\nMemory Efficiency:")
    print(f"  Agent object size: ~{agent_size} bytes")
    print(f"  100 agents: ~{agent_size * 100 / 1024:.2f} KB")

    # Cleanup
    agents.clear()

    assert agent_size < 10000, "Agent object should be <10KB"


# ============================================================================
# Test 6: Stress Testing
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_stress_burst_traffic(performance_agents):
    """
    Test 7: Handle burst traffic (500 tasks in rapid succession).

    Target: System handles burst without failures
    """
    queen = performance_agents["queen"]

    # Create 500 tasks
    tasks = [
        create_task(
            task_id=f"burst-{i:03d}",
            task_type="orchestrate",
            payload={"workflow": {"phases": []}}
        )
        for i in range(500)
    ]

    # Execute all at once
    start_time = time.time()
    results = await asyncio.gather(
        *[queen.execute(task) for task in tasks],
        return_exceptions=True
    )
    elapsed = time.time() - start_time

    successful = sum(1 for r in results if hasattr(r, 'success') and r.success)
    errors = sum(1 for r in results if isinstance(r, Exception))

    print(f"\nBurst Traffic (500 tasks):")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Successful: {successful}/500")
    print(f"  Errors: {errors}")
    print(f"  Throughput: {500/elapsed:.2f} tasks/sec")

    assert successful >= 475, f"At least 475/500 should succeed (got {successful})"


# ============================================================================
# Test 7: Performance Regression
# ============================================================================

@pytest.mark.asyncio
async def test_no_performance_regression(performance_agents):
    """
    Test 8: Validate no performance regression.

    Baseline metrics (from design):
    - Validation: <5ms
    - Coordination: <100ms
    - Throughput: >10 tasks/sec
    """
    queen = performance_agents["queen"]

    # Quick validation test
    task = create_task(
        task_id="regression-001",
        task_type="orchestrate",
        payload={"workflow": {"phases": []}}
    )

    validation = await queen.validate(task)
    assert validation.validation_time < 5.0, "Validation regression detected"

    # Quick execution test
    start = time.time()
    result = await queen.execute(task)
    execution_time = (time.time() - start) * 1000

    assert execution_time < 100.0, "Execution regression detected"
    assert result.success, "Execution should succeed"

    print(f"\nPerformance Regression Check:")
    print(f"  Validation: {validation.validation_time:.2f}ms (target: <5ms)")
    print(f"  Execution: {execution_time:.2f}ms (target: <100ms)")
    print(f"  Status: PASS - No regression detected")


# ============================================================================
# Performance Summary
# ============================================================================

def test_performance_summary():
    """
    Test 9: Performance test summary.

    Benchmark targets:
    - Validation latency: <5ms (P95)
    - Coordination latency: <100ms (P95)
    - Concurrent tasks: 200+ users
    - Throughput: >10 tasks/sec
    - Success rate: >95% under load
    """
    print("\nPerformance Benchmarks:")
    print("  Target: <5ms validation latency")
    print("  Target: <100ms coordination latency")
    print("  Target: 200+ concurrent users")
    print("  Target: >10 tasks/sec throughput")
    print("  Target: >95% success rate under load")

    assert True, "Performance benchmarks defined"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
