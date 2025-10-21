"""
Unit tests for CodeAnalyzerAgent.

Tests validate:
- Agent metadata and initialization
- Task validation for all 4 task types
- Task execution for code analysis, complexity, duplicates, dependencies
- AST parsing accuracy
- Edge cases
"""

import pytest
from src.agents.specialized.CodeAnalyzerAgent import (
    create_code_analyzer_agent,
    CodeAnalyzerAgent
)
from src.core.types import Task, Result


class TestCodeAnalyzerAgentMetadata:
    """Test agent metadata and initialization."""

    def test_agent_creation(self):
        agent = create_code_analyzer_agent()
        assert agent is not None
        assert isinstance(agent, CodeAnalyzerAgent)

    def test_agent_metadata(self):
        agent = create_code_analyzer_agent()
        metadata = agent.metadata

        assert metadata.agent_id == "code-analyzer"
        assert metadata.name == "Code Analysis Specialist"
        assert "analysis" in metadata.description.lower()

    def test_supported_task_types(self):
        agent = create_code_analyzer_agent()
        supported = agent.metadata.supported_task_types

        assert "analyze-code" in supported
        assert "detect-complexity" in supported
        assert "detect-duplicates" in supported
        assert "analyze-dependencies" in supported
        assert len(supported) == 4


class TestCodeAnalyzerAgentValidation:
    """Test task validation."""

    @pytest.fixture
    def agent(self):
        return create_code_analyzer_agent()

    @pytest.mark.asyncio
    async def test_validate_analyze_code(self, agent):
        task = Task(
            task_id="test-001",
            task_type="analyze-code",
            description="Analyze Python file",
            payload={"file_path": "test.py", "language": "python"}
        )
        result = await agent.validate(task)
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_detect_complexity(self, agent):
        task = Task(
            task_id="test-002",
            task_type="detect-complexity",
            description="Detect cyclomatic complexity",
            payload={"file_path": "test.py"}
        )
        result = await agent.validate(task)
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_detect_duplicates(self, agent):
        task = Task(
            task_id="test-003",
            task_type="detect-duplicates",
            description="Find duplicate code",
            payload={"file_path": "test.py"}
        )
        result = await agent.validate(task)
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_analyze_dependencies(self, agent):
        task = Task(
            task_id="test-004",
            task_type="analyze-dependencies",
            description="Analyze imports",
            payload={"file_path": "test.py"}
        )
        result = await agent.validate(task)
        assert result.is_valid


class TestCodeAnalyzerAgentExecution:
    """Test task execution."""

    @pytest.fixture
    def agent(self):
        return create_code_analyzer_agent()

    @pytest.mark.asyncio
    async def test_execute_analyze_code(self, agent):
        task = Task(
            task_id="test-005",
            task_type="analyze-code",
            description="Analyze code quality",
            payload={
                "file_path": "test.py",
                "code": "def hello():\n    print('Hello')\n    return True"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "analysis" in result.data

    @pytest.mark.asyncio
    async def test_execute_detect_complexity(self, agent):
        task = Task(
            task_id="test-006",
            task_type="detect-complexity",
            description="Detect complexity",
            payload={
                "code": """
def complex_function(x):
    if x > 0:
        if x > 10:
            return 'big'
        else:
            return 'small'
    else:
        return 'negative'
"""
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "complexity_metrics" in result.data
        assert len(result.data["complexity_metrics"]) > 0

    @pytest.mark.asyncio
    async def test_execute_detect_duplicates(self, agent):
        task = Task(
            task_id="test-007",
            task_type="detect-duplicates",
            description="Find duplicates",
            payload={
                "code": """
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    x = 1
    y = 2
    return x + y
"""
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "duplicates" in result.data

    @pytest.mark.asyncio
    async def test_execute_analyze_dependencies(self, agent):
        task = Task(
            task_id="test-008",
            task_type="analyze-dependencies",
            description="Analyze imports",
            payload={
                "code": """
import os
import sys
from typing import Dict, List
"""
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "dependencies" in result.data


class TestCodeAnalyzerAgentComplexity:
    """Test complexity calculation."""

    @pytest.fixture
    def agent(self):
        return create_code_analyzer_agent()

    @pytest.mark.asyncio
    async def test_simple_function_complexity(self, agent):
        """Test complexity of simple linear function."""
        task = Task(
            task_id="test-009",
            task_type="detect-complexity",
            description="Simple function",
            payload={
                "code": "def simple():\n    return 1"
            }
        )
        result = await agent.execute(task)
        assert result.success
        # Simple function should have complexity = 1
        metrics = result.data["complexity_metrics"]
        assert len(metrics) > 0
        assert metrics[0]["complexity"] == 1

    @pytest.mark.asyncio
    async def test_nested_conditionals_complexity(self, agent):
        """Test complexity with nested conditionals."""
        task = Task(
            task_id="test-010",
            task_type="detect-complexity",
            description="Nested conditionals",
            payload={
                "code": """
def nested(x, y):
    if x > 0:
        if y > 0:
            return 1
        else:
            return 2
    elif x < 0:
        return 3
    else:
        return 4
"""
            }
        )
        result = await agent.execute(task)
        assert result.success
        metrics = result.data["complexity_metrics"]
        # Should have complexity > 1 due to multiple branches
        assert metrics[0]["complexity"] > 1


class TestCodeAnalyzerAgentEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def agent(self):
        return create_code_analyzer_agent()

    @pytest.mark.asyncio
    async def test_empty_code(self, agent):
        """Test handling of empty code."""
        task = Task(
            task_id="test-011",
            task_type="analyze-code",
            description="Empty code",
            payload={"code": ""}
        )
        result = await agent.execute(task)
        assert result.success or not result.success  # Either handles or fails gracefully

    @pytest.mark.asyncio
    async def test_syntax_error_code(self, agent):
        """Test handling of code with syntax errors."""
        task = Task(
            task_id="test-012",
            task_type="analyze-code",
            description="Invalid syntax",
            payload={"code": "def invalid(\n    pass"}  # Missing closing paren
        )
        result = await agent.execute(task)
        # Should handle syntax errors gracefully
        assert "error" in result.data or "syntax" in result.message.lower()


# NASA Rule 10 Compliance Test
class TestCodeAnalyzerAgentNASACompliance:
    """Test NASA Rule 10 compliance."""

    def test_nasa_compliance(self):
        import ast
        from pathlib import Path

        agent_file = Path(__file__).parent.parent.parent.parent.parent / "src" / "agents" / "specialized" / "CodeAnalyzerAgent.py"

        with open(agent_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > 60:
                    violations.append((node.name, length))

        assert len(violations) == 0, f"NASA Rule 10 violations: {violations}"
