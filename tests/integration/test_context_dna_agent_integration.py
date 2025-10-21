"""
Context DNA Agent Integration Tests

Tests Context DNA integration with AgentBase.
Validates context persistence, session management, and retrieval.

Week 20 Day 1
Version: 8.0.0
"""

import pytest
import uuid
from datetime import datetime
from src.services.context_dna_bridge import (
    ContextDNABridge,
    AgentExecutionContext,
)


@pytest.fixture
def context_bridge():
    """Create Context DNA bridge for testing."""
    return ContextDNABridge()


@pytest.fixture
def sample_context():
    """Create sample agent execution context."""
    return AgentExecutionContext(
        agent_id="test-agent",
        project_id="test-project",
        task_id="test-task",
        session_id=str(uuid.uuid4()),
        start_time=datetime.now(),
        metadata={"test": True},
    )


class TestContextDNAAgentIntegration:
    """Test Context DNA agent integration."""

    @pytest.mark.asyncio
    async def test_initialize_context(self, context_bridge, sample_context):
        """Test context initialization."""
        # Should not raise exception
        await context_bridge.initialize_context(sample_context)

    @pytest.mark.asyncio
    async def test_store_agent_thought(self, context_bridge, sample_context):
        """Test storing agent thoughts."""
        await context_bridge.initialize_context(sample_context)

        # Store thought
        await context_bridge.store_agent_thought(
            sample_context, "Test thought", {"step": 1}
        )

        # Should not raise exception

    @pytest.mark.asyncio
    async def test_store_agent_result(self, context_bridge, sample_context):
        """Test storing agent result."""
        await context_bridge.initialize_context(sample_context)

        # Store result
        result = await context_bridge.store_agent_result(
            sample_context,
            {
                "success": True,
                "output": "Test output",
                "metrics": {"duration_ms": 100},
            },
        )

        assert result.success is True
        assert result.context_id == sample_context.session_id
        assert result.performance_ms >= 0

    @pytest.mark.asyncio
    async def test_retrieve_context(self, context_bridge, sample_context):
        """Test retrieving context."""
        # Initialize and store some context
        await context_bridge.initialize_context(sample_context)
        await context_bridge.store_agent_thought(sample_context, "Test thought")

        # Retrieve context
        result = await context_bridge.retrieve_context(
            project_id=sample_context.project_id,
            agent_id=sample_context.agent_id,
            query="test",
            limit=10,
        )

        assert isinstance(result, dict)
        assert "conversations" in result
        assert "memories" in result
        assert "tasks" in result
        assert "performance_ms" in result
        assert result["performance_ms"] >= 0

    @pytest.mark.asyncio
    async def test_finalize_context(self, context_bridge, sample_context):
        """Test finalizing context."""
        await context_bridge.initialize_context(sample_context)

        # Should not raise exception
        await context_bridge.finalize_context(sample_context)

    @pytest.mark.asyncio
    async def test_full_workflow(self, context_bridge):
        """Test full context workflow."""
        # Create context
        context = AgentExecutionContext(
            agent_id="workflow-test-agent",
            project_id="workflow-test-project",
            task_id="workflow-test-task",
            session_id=str(uuid.uuid4()),
            start_time=datetime.now(),
        )

        # 1. Initialize
        await context_bridge.initialize_context(context)

        # 2. Store thoughts
        await context_bridge.store_agent_thought(context, "Thought 1")
        await context_bridge.store_agent_thought(context, "Thought 2")
        await context_bridge.store_agent_thought(context, "Thought 3")

        # 3. Store result
        result = await context_bridge.store_agent_result(
            context, {"success": True, "output": "Workflow complete"}
        )
        assert result.success is True

        # 4. Retrieve context
        retrieved = await context_bridge.retrieve_context(
            project_id=context.project_id,
            agent_id=context.agent_id,
            query="workflow",
            limit=10,
        )
        assert isinstance(retrieved, dict)

        # 5. Finalize
        await context_bridge.finalize_context(context)

    @pytest.mark.asyncio
    async def test_error_handling(self, context_bridge, sample_context):
        """Test error handling in context operations."""
        await context_bridge.initialize_context(sample_context)

        # Store error result
        result = await context_bridge.store_agent_result(
            sample_context,
            {"success": False, "error": "Test error"},
        )

        # Should still succeed in storing the error
        assert result.success is True
        assert result.context_id == sample_context.session_id


class TestQueenAgentWithContext:
    """Test Queen agent with Context DNA integration."""

    @pytest.mark.asyncio
    async def test_queen_agent_execute_with_context(self):
        """Test Queen agent execution with context persistence."""
        from src.agents.core.QueenAgentWithContext import QueenAgentWithContext
        from src.agents.AgentBase import Task

        # Create Queen agent
        queen = QueenAgentWithContext()

        # Create task
        task = Task(
            id="test-task-001",
            type="coordinate",
            description="Test coordination task",
            payload={"project_id": "test-project", "phase": "test"},
            priority=5,
        )

        # Execute (should auto-persist context)
        result = await queen.execute(task)

        assert result.success is True
        assert result.task_id == task.id
        assert result.execution_time > 0
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_queen_agent_delegation(self):
        """Test Queen agent delegation with context."""
        from src.agents.core.QueenAgentWithContext import QueenAgentWithContext
        from src.agents.AgentBase import Task

        queen = QueenAgentWithContext()

        task = Task(
            id="test-delegate-001",
            type="delegate",
            description="Test delegation",
            payload={
                "project_id": "test-project",
                "target_agent": "princess-dev",
            },
            priority=7,
        )

        result = await queen.execute(task)

        assert result.success is True
        assert result.data.get("status") == "delegated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
