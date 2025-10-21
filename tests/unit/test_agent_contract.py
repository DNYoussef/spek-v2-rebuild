"""
Unit Tests - AgentContract and AgentBase

Tests for AgentContract TypeScript interface and AgentBase Python implementation.
Validates unified agent API, validation logic, metadata extensibility.

Target: 15 tests
Version: 8.0.0 (Week 3 Day 1)
"""

import pytest
import time
from src.core.AgentBase import (
    AgentBase,
    AgentType,
    AgentStatus,
    Task,
    TaskContext,
    Result,
    ErrorInfo,
    ValidationResult,
    ValidationError,
    AgentMetadata,
    AgentCapability,
)


# Mock agent for testing
class MockAgent(AgentBase):
    """Mock agent implementing AgentBase for testing."""

    async def validate(self, task: Task) -> ValidationResult:
        """Validate task structure and type."""
        start_time = time.time()

        errors = []
        errors.extend(self.validate_task_structure(task))
        errors.extend(self.validate_task_type(task))

        validation_time = (time.time() - start_time) * 1000  # ms

        return ValidationResult(
            valid=len(errors) == 0,
            validation_time=validation_time,
            errors=errors if errors else None
        )

    async def execute(self, task: Task) -> Result:
        """Execute task (mock implementation)."""
        start_time = time.time()

        # Simulate work
        await self._simulate_work(task)

        execution_time = (time.time() - start_time) * 1000  # ms

        return self.build_result(
            task_id=task.id,
            success=True,
            data={"message": "Task executed successfully"},
            execution_time=execution_time
        )

    async def _simulate_work(self, task: Task):
        """Simulate async work."""
        # Mock implementation
        pass


@pytest.fixture
def mock_metadata():
    """Create mock agent metadata."""
    return AgentMetadata(
        agent_id="mock-agent-001",
        name="Mock Agent",
        type=AgentType.CORE,
        version="8.0.0",
        supported_task_types=["test", "mock"],
        capabilities=[
            AgentCapability(
                name="testing",
                description="Testing capability",
                level=10
            )
        ],
        status=AgentStatus.IDLE
    )


@pytest.fixture
def mock_agent(mock_metadata):
    """Create mock agent instance."""
    return MockAgent(mock_metadata)


@pytest.fixture
def valid_task():
    """Create valid task."""
    return Task(
        id="task-001",
        type="test",
        description="Test task",
        payload={"data": "test"},
        priority=5
    )


class TestAgentInitialization:
    """Test agent initialization and metadata."""

    def test_agent_initialization(self, mock_agent, mock_metadata):
        """Test agent initializes with metadata."""
        assert mock_agent.metadata.agent_id == mock_metadata.agent_id
        assert mock_agent.metadata.name == mock_metadata.name
        assert mock_agent.metadata.type == AgentType.CORE

    def test_get_metadata(self, mock_agent, mock_metadata):
        """Test get_metadata returns correct metadata."""
        metadata = mock_agent.get_metadata()
        assert metadata.agent_id == mock_metadata.agent_id
        assert metadata.version == "8.0.0"

    def test_agent_status_update(self, mock_agent):
        """Test agent status can be updated."""
        assert mock_agent.metadata.status == AgentStatus.IDLE
        mock_agent.update_status(AgentStatus.BUSY)
        assert mock_agent.metadata.status == AgentStatus.BUSY


class TestTaskValidation:
    """Test task validation logic."""

    @pytest.mark.asyncio
    async def test_validate_valid_task(self, mock_agent, valid_task):
        """Test validation passes for valid task."""
        result = await mock_agent.validate(valid_task)

        assert result.valid is True
        assert result.errors is None
        assert result.validation_time < 5.0  # <5ms target

    @pytest.mark.asyncio
    async def test_validate_missing_id(self, mock_agent):
        """Test validation fails for missing task ID."""
        task = Task(
            id="",
            type="test",
            description="Test",
            payload={},
            priority=5
        )

        result = await mock_agent.validate(task)

        assert result.valid is False
        assert len(result.errors) >= 1
        assert any(e.field == "id" for e in result.errors)

    @pytest.mark.asyncio
    async def test_validate_invalid_type(self, mock_agent):
        """Test validation fails for unsupported task type."""
        task = Task(
            id="task-002",
            type="unsupported",
            description="Test",
            payload={},
            priority=5
        )

        result = await mock_agent.validate(task)

        assert result.valid is False
        assert any(e.field == "type" for e in result.errors)

    @pytest.mark.asyncio
    async def test_validate_invalid_priority(self, mock_agent):
        """Test validation fails for invalid priority."""
        task = Task(
            id="task-003",
            type="test",
            description="Test",
            payload={},
            priority=15  # out of range 0-10
        )

        result = await mock_agent.validate(task)

        assert result.valid is False
        assert any(e.field == "priority" for e in result.errors)

    @pytest.mark.asyncio
    async def test_validation_time_under_5ms(self, mock_agent, valid_task):
        """Test validation completes in <5ms."""
        result = await mock_agent.validate(valid_task)

        # p95 latency target
        assert result.validation_time < 5.0


class TestTaskExecution:
    """Test task execution logic."""

    @pytest.mark.asyncio
    async def test_execute_valid_task(self, mock_agent, valid_task):
        """Test task execution succeeds."""
        result = await mock_agent.execute(valid_task)

        assert result.success is True
        assert result.task_id == valid_task.id
        assert result.agent_id == mock_agent.metadata.agent_id
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_execute_returns_result(self, mock_agent, valid_task):
        """Test execute returns proper Result object."""
        result = await mock_agent.execute(valid_task)

        assert isinstance(result, Result)
        assert result.task_id == valid_task.id
        assert result.execution_time >= 0

    @pytest.mark.asyncio
    async def test_execute_includes_metadata(self, mock_agent, valid_task):
        """Test result includes metadata."""
        result = await mock_agent.execute(valid_task)

        assert result.metadata is not None
        assert result.metadata.timestamp is not None


class TestHealthCheck:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_default(self, mock_agent):
        """Test default health check returns true."""
        healthy = await mock_agent.health_check()
        assert healthy is True


class TestHelperMethods:
    """Test protected helper methods."""

    def test_validate_task_structure(self, mock_agent):
        """Test validate_task_structure helper."""
        task = Task(
            id="",  # invalid
            type="test",
            description="Test",
            payload={},
            priority=5
        )

        errors = mock_agent.validate_task_structure(task)
        assert len(errors) >= 1
        assert any(e.field == "id" for e in errors)

    def test_validate_task_type(self, mock_agent):
        """Test validate_task_type helper."""
        task = Task(
            id="task-004",
            type="unsupported",
            description="Test",
            payload={},
            priority=5
        )

        errors = mock_agent.validate_task_type(task)
        assert len(errors) >= 1
        assert errors[0].field == "type"

    def test_build_result(self, mock_agent):
        """Test build_result helper."""
        result = mock_agent.build_result(
            task_id="task-005",
            success=True,
            data={"key": "value"},
            execution_time=100.0
        )

        assert result.task_id == "task-005"
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.execution_time == 100.0
        assert result.agent_id == mock_agent.metadata.agent_id


class TestErrorHandling:
    """Test error handling."""

    def test_build_result_with_error(self, mock_agent):
        """Test building result with error."""
        error = ErrorInfo(
            code="TEST_ERROR",
            message="Test error message",
            context={"detail": "error detail"}
        )

        result = mock_agent.build_result(
            task_id="task-006",
            success=False,
            error=error,
            execution_time=50.0
        )

        assert result.success is False
        assert result.error is not None
        assert result.error.code == "TEST_ERROR"
