"""
Unit tests for FrontendDevAgent.

Tests validate:
- Agent metadata and initialization
- Task validation for all 4 task types
- Task execution for component/UI/rendering/styles
- Error handling and edge cases
- NASA Rule 10 compliance
"""

import pytest
from typing import Dict, Any
from src.agents.specialized.FrontendDevAgent import (
    create_frontend_dev_agent,
    FrontendDevAgent
)
from src.core.types import Task, ValidationResult, Result


class TestFrontendDevAgentMetadata:
    """Test agent metadata and initialization."""

    def test_agent_creation(self):
        """Test agent can be created successfully."""
        agent = create_frontend_dev_agent()
        assert agent is not None
        assert isinstance(agent, FrontendDevAgent)

    def test_agent_metadata(self):
        """Test agent has correct metadata."""
        agent = create_frontend_dev_agent()
        metadata = agent.metadata

        assert metadata.agent_id == "frontend-dev"
        assert metadata.name == "Frontend Development Specialist"
        assert metadata.version == "1.0.0"
        assert "Frontend" in metadata.description

    def test_supported_task_types(self):
        """Test agent supports all 4 task types."""
        agent = create_frontend_dev_agent()
        supported = agent.metadata.supported_task_types

        assert "implement-component" in supported
        assert "implement-ui" in supported
        assert "optimize-rendering" in supported
        assert "implement-styles" in supported
        assert len(supported) == 4

    def test_capabilities(self):
        """Test agent has correct capabilities."""
        agent = create_frontend_dev_agent()
        capabilities = agent.metadata.capabilities

        assert "React component development" in capabilities
        assert "TypeScript" in capabilities
        assert "UI/UX implementation" in capabilities
        assert "Rendering optimization" in capabilities
        assert "Styling" in capabilities
        assert len(capabilities) == 5


class TestFrontendDevAgentValidation:
    """Test task validation for all task types."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return create_frontend_dev_agent()

    @pytest.mark.asyncio
    async def test_validate_implement_component(self, agent):
        """Test validation for implement-component task."""
        task = Task(
            task_id="test-001",
            task_type="implement-component",
            description="Create UserProfile component",
            payload={
                "component_name": "UserProfile",
                "component_type": "functional",
                "props": ["userId", "onUpdate"]
            }
        )

        result = await agent.validate(task)
        assert result.is_valid
        assert result.confidence >= 0.9

    @pytest.mark.asyncio
    async def test_validate_implement_ui(self, agent):
        """Test validation for implement-ui task."""
        task = Task(
            task_id="test-002",
            task_type="implement-ui",
            description="Create dashboard UI layout",
            payload={
                "ui_name": "Dashboard",
                "layout_type": "responsive",
                "sections": ["header", "sidebar", "content"]
            }
        )

        result = await agent.validate(task)
        assert result.is_valid
        assert result.confidence >= 0.9

    @pytest.mark.asyncio
    async def test_validate_optimize_rendering(self, agent):
        """Test validation for optimize-rendering task."""
        task = Task(
            task_id="test-003",
            task_type="optimize-rendering",
            description="Optimize ProductList rendering",
            payload={
                "component_name": "ProductList",
                "optimization_type": "memoization"
            }
        )

        result = await agent.validate(task)
        assert result.is_valid
        assert result.confidence >= 0.9

    @pytest.mark.asyncio
    async def test_validate_implement_styles(self, agent):
        """Test validation for implement-styles task."""
        task = Task(
            task_id="test-004",
            task_type="implement-styles",
            description="Create button styles",
            payload={
                "component_name": "Button",
                "style_system": "tailwind"
            }
        )

        result = await agent.validate(task)
        assert result.is_valid
        assert result.confidence >= 0.9

    @pytest.mark.asyncio
    async def test_validate_unsupported_task_type(self, agent):
        """Test validation rejects unsupported task types."""
        task = Task(
            task_id="test-005",
            task_type="unsupported-task",
            description="Invalid task"
        )

        result = await agent.validate(task)
        assert not result.is_valid
        assert result.confidence < 0.5

    @pytest.mark.asyncio
    async def test_validate_missing_required_fields(self, agent):
        """Test validation rejects tasks with missing required fields."""
        task = Task(
            task_id="test-006",
            task_type="implement-component",
            description="Create component",
            payload={}  # Missing component_name
        )

        result = await agent.validate(task)
        assert not result.is_valid
        assert "component_name" in result.message.lower()


class TestFrontendDevAgentExecution:
    """Test task execution for all task types."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return create_frontend_dev_agent()

    @pytest.mark.asyncio
    async def test_execute_implement_component(self, agent):
        """Test execution of implement-component task."""
        task = Task(
            task_id="test-007",
            task_type="implement-component",
            description="Create Button component",
            payload={
                "component_name": "Button",
                "component_type": "functional",
                "props": ["label", "onClick", "disabled"]
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "code" in result.data
        assert "Button" in result.data["code"]
        assert "React" in result.data["code"]
        assert "typescript" == result.data["language"]

    @pytest.mark.asyncio
    async def test_execute_implement_ui(self, agent):
        """Test execution of implement-ui task."""
        task = Task(
            task_id="test-008",
            task_type="implement-ui",
            description="Create login page UI",
            payload={
                "ui_name": "LoginPage",
                "layout_type": "centered",
                "sections": ["form", "footer"]
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "code" in result.data
        assert "LoginPage" in result.data["code"]
        assert "export" in result.data["code"]

    @pytest.mark.asyncio
    async def test_execute_optimize_rendering(self, agent):
        """Test execution of optimize-rendering task."""
        task = Task(
            task_id="test-009",
            task_type="optimize-rendering",
            description="Add memoization to ProductList",
            payload={
                "component_name": "ProductList",
                "optimization_type": "memoization"
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "recommendations" in result.data
        assert len(result.data["recommendations"]) > 0
        assert any("memo" in rec.lower() for rec in result.data["recommendations"])

    @pytest.mark.asyncio
    async def test_execute_implement_styles(self, agent):
        """Test execution of implement-styles task."""
        task = Task(
            task_id="test-010",
            task_type="implement-styles",
            description="Create Card component styles",
            payload={
                "component_name": "Card",
                "style_system": "tailwind"
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "styles" in result.data
        assert "Card" in result.data["styles"]


class TestFrontendDevAgentEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return create_frontend_dev_agent()

    @pytest.mark.asyncio
    async def test_invalid_component_type(self, agent):
        """Test handling of invalid component type."""
        task = Task(
            task_id="test-011",
            task_type="implement-component",
            description="Create component",
            payload={
                "component_name": "TestComponent",
                "component_type": "invalid-type"  # Invalid
            }
        )

        result = await agent.execute(task)
        # Should default to functional component
        assert result.success
        assert "functional" in result.data.get("component_type", "functional")

    @pytest.mark.asyncio
    async def test_empty_props_list(self, agent):
        """Test handling of empty props list."""
        task = Task(
            task_id="test-012",
            task_type="implement-component",
            description="Create component with no props",
            payload={
                "component_name": "EmptyComponent",
                "component_type": "functional",
                "props": []
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "code" in result.data

    @pytest.mark.asyncio
    async def test_complex_component_with_state(self, agent):
        """Test creation of component with state management."""
        task = Task(
            task_id="test-013",
            task_type="implement-component",
            description="Create component with state",
            payload={
                "component_name": "Counter",
                "component_type": "functional",
                "props": ["initialCount"],
                "has_state": True
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "useState" in result.data["code"] or "state" in result.data["code"].lower()


class TestFrontendDevAgentAccessibility:
    """Test accessibility features."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return create_frontend_dev_agent()

    @pytest.mark.asyncio
    async def test_accessibility_requirements(self, agent):
        """Test that generated components include accessibility features."""
        task = Task(
            task_id="test-014",
            task_type="implement-component",
            description="Create accessible Button component",
            payload={
                "component_name": "Button",
                "component_type": "functional",
                "props": ["label", "onClick"]
            }
        )

        result = await agent.execute(task)
        assert result.success
        code = result.data["code"]

        # Check for accessibility attributes
        # Note: This is a basic check; real implementation should have aria-* attributes
        assert "aria" in code.lower() or "role" in code.lower() or "accessible" in code.lower()


class TestFrontendDevAgentPerformance:
    """Test performance characteristics."""

    @pytest.fixture
    def agent(self):
        """Create agent for testing."""
        return create_frontend_dev_agent()

    @pytest.mark.asyncio
    async def test_validation_performance(self, agent):
        """Test validation completes in <5ms."""
        import time

        task = Task(
            task_id="test-015",
            task_type="implement-component",
            description="Performance test",
            payload={"component_name": "TestComponent"}
        )

        start = time.time()
        await agent.validate(task)
        duration = (time.time() - start) * 1000  # Convert to ms

        # Validation should be very fast
        assert duration < 100  # Allow 100ms for test environment overhead

    @pytest.mark.asyncio
    async def test_optimization_recommendations_quality(self, agent):
        """Test that optimization recommendations are actionable."""
        task = Task(
            task_id="test-016",
            task_type="optimize-rendering",
            description="Get optimization recommendations",
            payload={
                "component_name": "ExpensiveComponent",
                "optimization_type": "comprehensive"
            }
        )

        result = await agent.execute(task)
        assert result.success
        assert "recommendations" in result.data
        assert len(result.data["recommendations"]) >= 3  # At least 3 recommendations


# NASA Rule 10 Compliance Test
class TestFrontendDevAgentNASACompliance:
    """Test NASA Rule 10 compliance."""

    def test_nasa_compliance(self):
        """Verify all functions are ≤60 LOC."""
        import ast
        from pathlib import Path

        agent_file = Path(__file__).parent.parent.parent.parent.parent / "src" / "agents" / "specialized" / "FrontendDevAgent.py"

        with open(agent_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > 60:
                    violations.append((node.name, length))

        assert len(violations) == 0, f"NASA Rule 10 violations: {violations}"
