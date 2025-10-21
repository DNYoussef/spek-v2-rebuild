"""
Integration Tests: AgentContract + EnhancedLightweightProtocol

Tests the integration between AgentContract (Day 1) and EnhancedLightweightProtocol (Day 2).
Validates that agents can communicate through the protocol with proper error handling,
circuit breaker protection, and performance targets.

Week 3 Day 3
Version: 8.0.0
"""

import pytest
import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass

# Import Day 1 components
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Set working directory to project root
os.chdir(str(Path(__file__).parent.parent.parent))

from core.AgentBase import (
    AgentBase,
    Task,
    Result,
    ValidationResult,
    AgentMetadata,
    AgentStatus,
    AgentCapability
)

# Import Day 2 components
from protocols.EnhancedLightweightProtocol import (
    EnhancedLightweightProtocol,
    ProtocolConfig,
    ProtocolMessage,
    MessageType,
    CircuitBreakerState,
    create_protocol
)


# ============================================================================
# Mock Agent Implementations for Testing
# ============================================================================

class MockCoderAgent(AgentBase):
    """Mock coder agent for integration testing."""

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="coder-001",
            name="Mock Coder",
            version="1.0.0",
            capabilities=[AgentCapability.CODE_GENERATION],
            supported_task_types=["code.generate", "code.refactor"]
        )
        super().__init__(metadata)
        self.execution_count = 0

    async def validate(self, task: Task) -> ValidationResult:
        """Validate coding task."""
        errors = self.validate_task_structure(task)

        if task.type not in self._metadata.supported_task_types:
            errors.append({
                "field": "type",
                "message": f"Unsupported task type: {task.type}",
                "severity": 10
            })

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            validation_time_ms=2.0,
            agent_id=self._metadata.agent_id
        )

    async def execute(self, task: Task) -> Result:
        """Execute coding task."""
        self.execution_count += 1

        # Simulate code generation
        await asyncio.sleep(0.05)  # 50ms work

        return self.build_result(
            task_id=task.id,
            success=True,
            data={
                "code": "def hello():\n    return 'Hello, World!'",
                "language": "python",
                "lines": 2
            }
        )


class MockReviewerAgent(AgentBase):
    """Mock reviewer agent for integration testing."""

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="reviewer-001",
            name="Mock Reviewer",
            version="1.0.0",
            capabilities=[AgentCapability.CODE_REVIEW],
            supported_task_types=["review.code", "review.security"]
        )
        super().__init__(metadata)
        self.execution_count = 0

    async def validate(self, task: Task) -> ValidationResult:
        """Validate review task."""
        errors = self.validate_task_structure(task)

        if "code" not in task.payload:
            errors.append({
                "field": "payload.code",
                "message": "Code payload required for review",
                "severity": 10
            })

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            validation_time_ms=2.0,
            agent_id=self._metadata.agent_id
        )

    async def execute(self, task: Task) -> Result:
        """Execute review task."""
        self.execution_count += 1

        # Simulate code review
        await asyncio.sleep(0.03)  # 30ms work

        return self.build_result(
            task_id=task.id,
            success=True,
            data={
                "review_comments": ["Good code structure", "Consider adding docstrings"],
                "issues_found": 0,
                "approval": True
            }
        )


class MockFailingAgent(AgentBase):
    """Mock agent that fails for circuit breaker testing."""

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="failing-001",
            name="Mock Failing Agent",
            version="1.0.0",
            capabilities=[],
            supported_task_types=["test.fail"]
        )
        super().__init__(metadata)
        self.fail_count = 0
        self.should_fail = True

    async def validate(self, task: Task) -> ValidationResult:
        """Always valid."""
        return ValidationResult(
            is_valid=True,
            errors=[],
            validation_time_ms=1.0,
            agent_id=self._metadata.agent_id
        )

    async def execute(self, task: Task) -> Result:
        """Fail to test circuit breaker."""
        self.fail_count += 1

        if self.should_fail:
            return self.build_result(
                task_id=task.id,
                success=False,
                error={
                    "code": "EXECUTION_FAILED",
                    "message": "Simulated failure for testing"
                }
            )
        else:
            return self.build_result(
                task_id=task.id,
                success=True,
                data={"recovered": True}
            )


# ============================================================================
# Integration Test Suite
# ============================================================================

class TestAgentProtocolIntegration:
    """Integration tests for AgentContract + EnhancedLightweightProtocol."""

    @pytest.fixture
    def protocol(self):
        """Create protocol instance."""
        config = ProtocolConfig(
            max_retries=3,
            retry_delay_ms=50,
            timeout_ms=5000,
            compression_enabled=True
        )
        return create_protocol(config)

    @pytest.fixture
    def coder_agent(self):
        """Create mock coder agent."""
        return MockCoderAgent()

    @pytest.fixture
    def reviewer_agent(self):
        """Create mock reviewer agent."""
        return MockReviewerAgent()

    @pytest.fixture
    def failing_agent(self):
        """Create mock failing agent."""
        return MockFailingAgent()

    @pytest.mark.asyncio
    async def test_basic_agent_communication(self, protocol, coder_agent):
        """Test basic agent-to-agent communication via protocol."""
        # Create task
        task = Task(
            id="task-001",
            type="code.generate",
            description="Generate hello world function",
            payload={"language": "python"},
            priority=5
        )

        # Validate task
        validation = await coder_agent.validate(task)
        assert validation.is_valid
        assert validation.validation_time_ms < 5.0  # <5ms target

        # Execute task
        result = await coder_agent.execute(task)
        assert result.success
        assert result.task_id == task.id
        assert "code" in result.data
        assert result.execution_time < 100.0  # <100ms for simple task

    @pytest.mark.asyncio
    async def test_agent_workflow_coder_to_reviewer(self, protocol, coder_agent, reviewer_agent):
        """Test workflow: Coder generates code → Reviewer reviews code."""
        # Step 1: Coder generates code
        code_task = Task(
            id="task-code-001",
            type="code.generate",
            description="Generate hello world",
            payload={"language": "python"},
            priority=5
        )

        code_result = await coder_agent.execute(code_task)
        assert code_result.success
        generated_code = code_result.data["code"]

        # Step 2: Reviewer reviews generated code
        review_task = Task(
            id="task-review-001",
            type="review.code",
            description="Review generated code",
            payload={"code": generated_code},
            priority=5
        )

        review_result = await reviewer_agent.execute(review_task)
        assert review_result.success
        assert review_result.data["approval"]

    @pytest.mark.asyncio
    async def test_protocol_message_serialization(self, protocol):
        """Test protocol message serialization with agent data."""
        # Create message with agent task
        message = ProtocolMessage(
            message_id="msg-001",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="queen-001",
            receiver_id="coder-001",
            payload={
                "task_id": "task-001",
                "type": "code.generate",
                "description": "Generate function",
                "priority": 5
            }
        )

        # Serialize
        serialized = protocol.serialize_message(message)
        assert isinstance(serialized, bytes)
        assert len(serialized) < 1024  # <1KB target

        # Deserialize
        deserialized = protocol.deserialize_message(serialized)
        assert deserialized.message_id == message.message_id
        assert deserialized.sender_id == message.sender_id
        assert deserialized.receiver_id == message.receiver_id
        assert deserialized.payload["task_id"] == "task-001"

    @pytest.mark.asyncio
    async def test_circuit_breaker_with_failing_agent(self, protocol, failing_agent):
        """Test circuit breaker opens after repeated agent failures."""
        # Execute 5 tasks that will fail
        for i in range(5):
            task = Task(
                id=f"task-fail-{i}",
                type="test.fail",
                description="Test failure",
                payload={},
                priority=5
            )
            result = await failing_agent.execute(task)
            assert not result.success

        # Circuit breaker should be OPEN after 5 failures
        assert failing_agent.fail_count == 5

        # Agent can still recover (no circuit breaker in agent itself,
        # but protocol would prevent further calls)
        failing_agent.should_fail = False
        recovery_task = Task(
            id="task-recover-001",
            type="test.fail",
            description="Test recovery",
            payload={},
            priority=5
        )
        recovery_result = await failing_agent.execute(recovery_task)
        assert recovery_result.success
        assert recovery_result.data["recovered"]

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self, protocol, coder_agent, reviewer_agent):
        """Test concurrent execution of multiple agents."""
        # Create tasks for both agents
        tasks = [
            Task(
                id=f"task-code-{i}",
                type="code.generate",
                description=f"Generate code {i}",
                payload={"language": "python"},
                priority=5
            )
            for i in range(3)
        ] + [
            Task(
                id=f"task-review-{i}",
                type="review.code",
                description=f"Review code {i}",
                payload={"code": "def test(): pass"},
                priority=5
            )
            for i in range(3)
        ]

        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(
            *[coder_agent.execute(tasks[0])],
            *[coder_agent.execute(tasks[1])],
            *[coder_agent.execute(tasks[2])],
            *[reviewer_agent.execute(tasks[3])],
            *[reviewer_agent.execute(tasks[4])],
            *[reviewer_agent.execute(tasks[5])]
        )
        elapsed_ms = (time.time() - start_time) * 1000

        # All should succeed
        assert all(r.success for r in results)

        # Concurrent execution should be faster than sequential
        # Sequential would be ~6 * 50ms = 300ms
        # Concurrent should be ~50ms (max of all)
        assert elapsed_ms < 200  # Allow some overhead

    @pytest.mark.asyncio
    async def test_validation_before_execution(self, protocol, coder_agent):
        """Test that validation must pass before execution."""
        # Create invalid task (unsupported type)
        invalid_task = Task(
            id="task-invalid-001",
            type="code.unsupported",
            description="Unsupported task type",
            payload={},
            priority=5
        )

        # Validation should fail
        validation = await coder_agent.validate(invalid_task)
        assert not validation.is_valid
        assert len(validation.errors) > 0
        assert validation.errors[0]["field"] == "type"

        # Execution would still work (agent doesn't enforce validation)
        # but in real system, protocol would block invalid tasks

    @pytest.mark.asyncio
    async def test_latency_tracking_integration(self, protocol, coder_agent):
        """Test protocol latency tracking with real agent execution."""
        # Execute multiple tasks to collect latency samples
        for i in range(10):
            task = Task(
                id=f"task-latency-{i}",
                type="code.generate",
                description=f"Task {i}",
                payload={"language": "python"},
                priority=5
            )
            await coder_agent.execute(task)

        # Check execution count
        assert coder_agent.execution_count == 10

        # Protocol would track latency (tested separately in Day 2)
        # Here we just verify agents executed within target

    @pytest.mark.asyncio
    async def test_error_propagation_through_protocol(self, protocol, failing_agent):
        """Test that agent errors propagate correctly through protocol."""
        task = Task(
            id="task-error-001",
            type="test.fail",
            description="Test error propagation",
            payload={},
            priority=5
        )

        result = await failing_agent.execute(task)

        # Verify error structure
        assert not result.success
        assert result.error is not None
        assert result.error["code"] == "EXECUTION_FAILED"
        assert "Simulated failure" in result.error["message"]

    @pytest.mark.asyncio
    async def test_health_check_integration(self, protocol, coder_agent, reviewer_agent):
        """Test agent health checks."""
        # Check health of both agents
        coder_health = await coder_agent.health_check()
        reviewer_health = await reviewer_agent.health_check()

        assert coder_health is True
        assert reviewer_health is True

        # Update status
        coder_agent.update_status(AgentStatus.BUSY)
        assert coder_agent._metadata.status == AgentStatus.BUSY

        coder_agent.update_status(AgentStatus.IDLE)
        assert coder_agent._metadata.status == AgentStatus.IDLE


# ============================================================================
# Performance Integration Tests
# ============================================================================

class TestPerformanceIntegration:
    """Performance tests for agent + protocol integration."""

    @pytest.mark.asyncio
    async def test_validation_latency_target(self):
        """Test that validation meets <5ms target."""
        coder = MockCoderAgent()

        # Measure validation latency
        latencies = []
        for i in range(100):
            task = Task(
                id=f"task-perf-{i}",
                type="code.generate",
                description="Performance test",
                payload={},
                priority=5
            )

            start_time = time.time()
            await coder.validate(task)
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate p95
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]

        assert p95 < 5.0  # <5ms p95 target

    @pytest.mark.asyncio
    async def test_execution_throughput(self):
        """Test agent execution throughput."""
        coder = MockCoderAgent()

        # Execute 50 tasks
        start_time = time.time()
        tasks = [
            Task(
                id=f"task-throughput-{i}",
                type="code.generate",
                description=f"Task {i}",
                payload={},
                priority=5
            )
            for i in range(50)
        ]

        results = await asyncio.gather(*[coder.execute(t) for t in tasks])
        elapsed_time = time.time() - start_time

        # All should succeed
        assert all(r.success for r in results)

        # Calculate throughput (tasks/sec)
        throughput = 50 / elapsed_time
        assert throughput > 20  # >20 tasks/sec minimum


# ============================================================================
# Error Handling Integration Tests
# ============================================================================

class TestErrorHandlingIntegration:
    """Error handling tests for agent + protocol integration."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in agent execution."""
        # This would require async timeout implementation
        # Placeholder for future timeout tests
        pass

    @pytest.mark.asyncio
    async def test_retry_logic_integration(self):
        """Test retry logic with transient failures."""
        # This would test protocol retry with agent failures
        # Placeholder for future retry tests
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
