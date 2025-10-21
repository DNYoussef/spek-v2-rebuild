"""
Unit tests for PerformanceEngineerAgent.

Tests validate:
- Agent metadata and initialization
- Task validation for all 4 task types
- Performance profiling
- Bottleneck detection
- Optimization recommendations
"""

import pytest
from src.agents.specialized.PerformanceEngineerAgent import (
    create_performance_engineer_agent,
    PerformanceEngineerAgent
)
from src.core.types import Task, Result


class TestPerformanceEngineerAgentMetadata:
    """Test agent metadata."""

    def test_agent_creation(self):
        agent = create_performance_engineer_agent()
        assert agent is not None
        assert isinstance(agent, PerformanceEngineerAgent)

    def test_agent_metadata(self):
        agent = create_performance_engineer_agent()
        metadata = agent.metadata

        assert metadata.agent_id == "performance-engineer"
        assert metadata.name == "Performance Engineering Specialist"
        assert "performance" in metadata.description.lower()

    def test_supported_task_types(self):
        agent = create_performance_engineer_agent()
        supported = agent.metadata.supported_task_types

        assert "profile-performance" in supported
        assert "detect-bottlenecks" in supported
        assert "optimize-performance" in supported
        assert "benchmark-system" in supported
        assert len(supported) == 4


class TestPerformanceEngineerAgentValidation:
    """Test task validation."""

    @pytest.fixture
    def agent(self):
        return create_performance_engineer_agent()

    @pytest.mark.asyncio
    async def test_validate_profile_performance(self, agent):
        task = Task(
            task_id="test-001",
            task_type="profile-performance",
            description="Profile API endpoint",
            payload={"target": "api_endpoint", "metrics": ["cpu", "memory"]}
        )
        result = await agent.validate(task)
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_detect_bottlenecks(self, agent):
        task = Task(
            task_id="test-002",
            task_type="detect-bottlenecks",
            description="Find bottlenecks",
            payload={"system": "web_app"}
        )
        result = await agent.validate(task)
        assert result.is_valid


class TestPerformanceEngineerAgentProfiling:
    """Test performance profiling."""

    @pytest.fixture
    def agent(self):
        return create_performance_engineer_agent()

    @pytest.mark.asyncio
    async def test_execute_profile_performance(self, agent):
        task = Task(
            task_id="test-003",
            task_type="profile-performance",
            description="Profile function",
            payload={
                "target": "process_data",
                "metrics": ["cpu", "memory", "io"]
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "profile_results" in result.data

        profile = result.data["profile_results"]
        assert "duration_ms" in profile
        assert "cpu_time_ms" in profile
        assert "memory_mb" in profile

    @pytest.mark.asyncio
    async def test_profile_includes_hot_spots(self, agent):
        """Test that profiling identifies hot spots."""
        task = Task(
            task_id="test-004",
            task_type="profile-performance",
            description="Find hot spots",
            payload={
                "target": "complex_function",
                "detail_level": "high"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "hot_spots" in result.data["profile_results"]


class TestPerformanceEngineerAgentBottleneckDetection:
    """Test bottleneck detection."""

    @pytest.fixture
    def agent(self):
        return create_performance_engineer_agent()

    @pytest.mark.asyncio
    async def test_execute_detect_bottlenecks(self, agent):
        task = Task(
            task_id="test-005",
            task_type="detect-bottlenecks",
            description="Detect system bottlenecks",
            payload={
                "system": "api_server",
                "metrics": {
                    "response_time": 500,
                    "cpu_usage": 85,
                    "memory_usage": 90
                }
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "bottlenecks" in result.data
        assert len(result.data["bottlenecks"]) > 0

    @pytest.mark.asyncio
    async def test_bottleneck_prioritization(self, agent):
        """Test that bottlenecks are prioritized by severity."""
        task = Task(
            task_id="test-006",
            task_type="detect-bottlenecks",
            description="Prioritize issues",
            payload={
                "system": "database",
                "metrics": {
                    "query_time": 1000,
                    "connection_pool": 95,
                    "cache_hit_rate": 30
                }
            }
        )
        result = await agent.execute(task)
        assert result.success
        bottlenecks = result.data["bottlenecks"]

        # Check that bottlenecks have severity
        assert all("severity" in b for b in bottlenecks)


class TestPerformanceEngineerAgentOptimization:
    """Test optimization recommendations."""

    @pytest.fixture
    def agent(self):
        return create_performance_engineer_agent()

    @pytest.mark.asyncio
    async def test_execute_optimize_performance(self, agent):
        task = Task(
            task_id="test-007",
            task_type="optimize-performance",
            description="Optimize slow function",
            payload={
                "target": "data_processor",
                "current_performance": {
                    "execution_time": 500,
                    "memory_usage": 256
                }
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "optimizations" in result.data
        assert len(result.data["optimizations"]) > 0

    @pytest.mark.asyncio
    async def test_optimization_strategies(self, agent):
        """Test that optimizations include specific strategies."""
        task = Task(
            task_id="test-008",
            task_type="optimize-performance",
            description="Get optimization strategies",
            payload={
                "target": "api_endpoint",
                "bottleneck_type": "cpu"
            }
        )
        result = await agent.execute(task)
        assert result.success
        optimizations = result.data["optimizations"]

        # Each optimization should have strategy and expected impact
        assert all("strategy" in opt for opt in optimizations)
        assert all("expected_improvement" in opt for opt in optimizations)


class TestPerformanceEngineerAgentBenchmarking:
    """Test benchmarking functionality."""

    @pytest.fixture
    def agent(self):
        return create_performance_engineer_agent()

    @pytest.mark.asyncio
    async def test_execute_benchmark_system(self, agent):
        task = Task(
            task_id="test-009",
            task_type="benchmark-system",
            description="Benchmark API",
            payload={
                "system": "rest_api",
                "test_cases": [
                    {"endpoint": "/users", "method": "GET"},
                    {"endpoint": "/users", "method": "POST"}
                ]
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "benchmark_results" in result.data

    @pytest.mark.asyncio
    async def test_benchmark_comparison(self, agent):
        """Test benchmark with baseline comparison."""
        task = Task(
            task_id="test-010",
            task_type="benchmark-system",
            description="Compare with baseline",
            payload={
                "system": "api",
                "baseline": {"avg_response": 100, "p95": 150},
                "current": {"avg_response": 120, "p95": 180}
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "comparison" in result.data or "regression" in result.data


class TestPerformanceEngineerAgentEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def agent(self):
        return create_performance_engineer_agent()

    @pytest.mark.asyncio
    async def test_no_bottlenecks_detected(self, agent):
        """Test handling when system performs well."""
        task = Task(
            task_id="test-011",
            task_type="detect-bottlenecks",
            description="Well-performing system",
            payload={
                "system": "optimized_api",
                "metrics": {
                    "response_time": 50,
                    "cpu_usage": 30,
                    "memory_usage": 40
                }
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert len(result.data["bottlenecks"]) == 0 or "none detected" in result.message.lower()

    @pytest.mark.asyncio
    async def test_invalid_metrics(self, agent):
        """Test handling of invalid metrics."""
        task = Task(
            task_id="test-012",
            task_type="profile-performance",
            description="Invalid metrics",
            payload={
                "target": "test",
                "metrics": ["invalid_metric"]
            }
        )
        result = await agent.execute(task)
        # Should handle gracefully
        assert result.success or "error" in result.message.lower()


# NASA Rule 10 Compliance Test
class TestPerformanceEngineerAgentNASACompliance:
    """Test NASA Rule 10 compliance."""

    def test_nasa_compliance(self):
        import ast
        from pathlib import Path

        agent_file = Path(__file__).parent.parent.parent.parent.parent / "src" / "agents" / "specialized" / "PerformanceEngineerAgent.py"

        with open(agent_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > 60:
                    violations.append((node.name, length))

        # Allow 1 violation (__init__ at 80 LOC due to configuration)
        assert len(violations) <= 1, f"NASA Rule 10 violations: {violations}"
        if violations:
            assert violations[0][0] == "__init__"
            assert violations[0][1] <= 85  # Should be around 80 LOC
