"""
Unit tests for AgentBase

Tests common agent functionality:
- Metadata creation
- Status updates
- Health checks
- Task structure validation
- Result building
- Delegation
- Logging

Week 5 Day 2
Version: 8.0.0
"""

import pytest
import asyncio
from typing import Dict, Any

from src.agents.AgentBase import (
    AgentBase,
    AgentType,
    AgentStatus,
    AgentCapability,
    AgentMetadata,
    Task,
    ValidationResult,
    ValidationError,
    Result,
    ErrorInfo,
    create_agent_metadata
)
from src.protocols.EnhancedLightweightProtocol import EnhancedLightweightProtocol


# ============================================================================
# Test Agent (Concrete implementation for testing)
# ============================================================================

class TestAgent(AgentBase):
    """Test agent for AgentBase testing."""

    def __init__(self, metadata: AgentMetadata):
        super().__init__(metadata=metadata)

    async def validate(self, task: Task) -> ValidationResult:
        """Validate task."""
        errors = []
        errors.extend(self.validate_task_structure(task))
        errors.extend(self.validate_task_type(task))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            validation_time=1.0
        )

    async def execute(self, task: Task) -> Result:
        """Execute task."""
        return self.build_result(
            task_id=task.id,
            success=True,
            data={"result": "test execution"},
            execution_time=10.0
        )


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_metadata():
    """Create sample agent metadata."""
    return create_agent_metadata(
        agent_id="test-agent",
        name="Test Agent",
        agent_type=AgentType.CORE,
        supported_task_types=["test-task"],
        capabilities=[
            AgentCapability(
                name="Test Capability",
                description="Test capability description",
                level=10
            )
        ]
    )


@pytest.fixture
def test_agent(sample_metadata):
    """Create test agent instance."""
    return TestAgent(metadata=sample_metadata)


@pytest.fixture
def valid_task():
    """Create valid task."""
    return Task(
        id="task-123",
        type="test-task",
        description="Test task description",
        payload={"key": "value"},
        priority=5
    )


@pytest.fixture
def invalid_task():
    """Create invalid task (missing required fields)."""
    return Task(
        id="",  # Invalid: empty ID
        type="",  # Invalid: empty type
        description="Test",
        payload={"key": "value"},
        priority=5
    )


# ============================================================================
# Test Cases
# ============================================================================

def test_agent_metadata_creation(sample_metadata):
    """Test 1: Agent metadata creation."""
    assert sample_metadata.agent_id == "test-agent"
    assert sample_metadata.name == "Test Agent"
    assert sample_metadata.type == AgentType.CORE
    assert sample_metadata.status == AgentStatus.IDLE
    assert len(sample_metadata.capabilities) == 1
    assert sample_metadata.capabilities[0].name == "Test Capability"


def test_agent_initialization(test_agent, sample_metadata):
    """Test 2: Agent initialization with metadata."""
    assert test_agent.metadata == sample_metadata
    assert test_agent.protocol is not None
    assert isinstance(test_agent.protocol, EnhancedLightweightProtocol)


def test_get_metadata(test_agent, sample_metadata):
    """Test 3: Get agent metadata."""
    retrieved_metadata = test_agent.get_metadata()
    assert retrieved_metadata == sample_metadata
    assert retrieved_metadata.agent_id == "test-agent"


@pytest.mark.asyncio
async def test_health_check_healthy(test_agent):
    """Test 4: Health check returns True when agent is healthy."""
    is_healthy = await test_agent.health_check()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_offline(test_agent):
    """Test 5: Health check returns False when agent is offline."""
    test_agent.update_status(AgentStatus.OFFLINE)
    is_healthy = await test_agent.health_check()
    assert is_healthy is False


def test_update_status(test_agent):
    """Test 6: Update agent status."""
    assert test_agent.metadata.status == AgentStatus.IDLE

    test_agent.update_status(AgentStatus.BUSY)
    assert test_agent.metadata.status == AgentStatus.BUSY

    test_agent.update_status(AgentStatus.ERROR)
    assert test_agent.metadata.status == AgentStatus.ERROR


def test_validate_task_structure_valid(test_agent, valid_task):
    """Test 7: Validate valid task structure (no errors)."""
    errors = test_agent.validate_task_structure(valid_task)
    assert len(errors) == 0


def test_validate_task_structure_invalid(test_agent, invalid_task):
    """Test 8: Validate invalid task structure (multiple errors)."""
    errors = test_agent.validate_task_structure(invalid_task)
    assert len(errors) > 0
    assert any(e.field == "id" for e in errors)
    assert any(e.field == "type" for e in errors)


def test_validate_task_type_supported(test_agent, valid_task):
    """Test 9: Validate supported task type (no errors)."""
    errors = test_agent.validate_task_type(valid_task)
    assert len(errors) == 0


def test_validate_task_type_unsupported(test_agent):
    """Test 10: Validate unsupported task type (error)."""
    unsupported_task = Task(
        id="task-456",
        type="unsupported-type",
        description="Test",
        payload={},
        priority=5
    )

    errors = test_agent.validate_task_type(unsupported_task)
    assert len(errors) == 1
    assert errors[0].field == "type"
    assert "not supported" in errors[0].message


def test_build_result_success(test_agent):
    """Test 11: Build successful result."""
    result = test_agent.build_result(
        task_id="task-789",
        success=True,
        data={"output": "success"},
        execution_time=15.5
    )

    assert result.task_id == "task-789"
    assert result.success is True
    assert result.data == {"output": "success"}
    assert result.error is None
    assert result.execution_time == 15.5
    assert result.agent_id == "test-agent"
    assert result.metadata is not None
    assert result.metadata.timestamp is not None


def test_build_result_failure(test_agent):
    """Test 12: Build failed result with error."""
    error = ErrorInfo(
        code="TEST_ERROR",
        message="Test error message",
        stack="test stack trace"
    )

    result = test_agent.build_result(
        task_id="task-999",
        success=False,
        error=error,
        execution_time=5.0
    )

    assert result.task_id == "task-999"
    assert result.success is False
    assert result.data is None
    assert result.error == error
    assert result.error.code == "TEST_ERROR"
    assert result.execution_time == 5.0


@pytest.mark.asyncio
async def test_validate_implementation(test_agent, valid_task):
    """Test 13: Validate method implementation."""
    validation_result = await test_agent.validate(valid_task)

    assert isinstance(validation_result, ValidationResult)
    assert validation_result.valid is True
    assert len(validation_result.errors) == 0
    assert validation_result.validation_time > 0


@pytest.mark.asyncio
async def test_execute_implementation(test_agent, valid_task):
    """Test 14: Execute method implementation."""
    result = await test_agent.execute(valid_task)

    assert isinstance(result, Result)
    assert result.task_id == valid_task.id
    assert result.success is True
    assert result.data == {"result": "test execution"}
    assert result.execution_time == 10.0


def test_logging_methods(test_agent, caplog):
    """Test 15: Logging methods (info, error, debug)."""
    import logging
    caplog.set_level(logging.DEBUG)

    test_agent.log_info("Test info message")
    test_agent.log_error("Test error message")
    test_agent.log_debug("Test debug message")

    # Verify logs contain agent ID and messages
    assert any("test-agent" in record.message for record in caplog.records)
