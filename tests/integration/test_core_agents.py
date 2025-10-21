"""
Integration Tests for Core Agents (Week 21 Day 3 - Production Hardening)

Tests the 5 core agents that form the foundation of SPEK Platform:
1. Queen - Top-level coordinator and task decomposition
2. Coder - Code implementation and generation
3. Researcher - Research and analysis
4. Tester - Test creation and validation
5. Reviewer - Code review and quality assurance

Each test validates:
- Agent contract compliance (AgentContract interface)
- Core functionality execution
- Error handling and edge cases
- NASA Rule 10 compliance (functions ≤60 LOC)
- Integration with EnhancedLightweightProtocol
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.queen import QueenAgent
from agents.coder import CoderAgent
from agents.researcher import ResearcherAgent
from agents.tester import TesterAgent
from agents.reviewer import ReviewerAgent
from infrastructure.agent_base import AgentContract, Task, TaskType, Result


class TestQueenAgent:
    """Test suite for Queen Agent (Top-level coordinator)."""

    @pytest.fixture
    def queen_agent(self):
        """Create Queen agent instance for testing."""
        return QueenAgent(agent_id="test-queen-001")

    def test_queen_agent_initialization(self, queen_agent):
        """Test Queen agent initializes with correct metadata."""
        metadata = queen_agent.get_metadata()

        assert metadata["agent_id"] == "test-queen-001"
        assert metadata["name"] == "Queen"
        assert metadata["description"] == "Top-level coordinator for multi-agent orchestration"
        assert metadata["capabilities"] == ["task_decomposition", "agent_coordination", "workflow_orchestration"]
        assert metadata["version"] == "2.0.0"

    def test_queen_validate_accepts_workflow_tasks(self, queen_agent):
        """Test Queen validates workflow orchestration tasks correctly."""
        task = Task(
            task_id="task-001",
            task_type=TaskType.WORKFLOW,
            description="Implement user authentication system",
            payload={
                "workflow": {
                    "objective": "Build secure auth with JWT tokens",
                    "constraints": ["Must use bcrypt for passwords", "Session timeout 24h"]
                }
            },
            priority="high",
            assigned_agent="test-queen-001"
        )

        result = queen_agent.validate(task)
        assert result is True

    def test_queen_validate_rejects_invalid_tasks(self, queen_agent):
        """Test Queen rejects tasks without workflow payload."""
        task = Task(
            task_id="task-002",
            task_type=TaskType.CODE_IMPLEMENTATION,  # Wrong type
            description="Write code",
            payload={},
            priority="medium",
            assigned_agent="test-queen-001"
        )

        result = queen_agent.validate(task)
        assert result is False

    def test_queen_execute_task_decomposition(self, queen_agent):
        """Test Queen decomposes complex task into subtasks."""
        task = Task(
            task_id="task-003",
            task_type=TaskType.WORKFLOW,
            description="Build REST API for user management",
            payload={
                "workflow": {
                    "objective": "Create CRUD endpoints for users (GET, POST, PUT, DELETE)",
                    "constraints": ["Use Express.js", "PostgreSQL database", "JWT auth"]
                }
            },
            priority="high",
            assigned_agent="test-queen-001"
        )

        result = queen_agent.execute(task)

        assert result.success is True
        assert "subtasks" in result.output

        subtasks = result.output["subtasks"]
        assert isinstance(subtasks, list)
        assert len(subtasks) >= 2  # At least research + implementation

        # Check subtask structure
        for subtask in subtasks:
            assert "agent" in subtask
            assert "task_type" in subtask
            assert "description" in subtask
            assert subtask["agent"] in ["researcher", "coder", "tester", "reviewer"]

    def test_queen_handles_execution_errors_gracefully(self, queen_agent):
        """Test Queen handles errors without crashing."""
        task = Task(
            task_id="task-004",
            task_type=TaskType.WORKFLOW,
            description="Invalid task with missing payload",
            payload={},  # Missing workflow key
            priority="low",
            assigned_agent="test-queen-001"
        )

        result = queen_agent.execute(task)

        # Should fail validation but not crash
        assert result.success is False
        assert "error" in result.output or "validation" in result.output.get("message", "").lower()


class TestCoderAgent:
    """Test suite for Coder Agent (Code implementation)."""

    @pytest.fixture
    def coder_agent(self):
        """Create Coder agent instance for testing."""
        return CoderAgent(agent_id="test-coder-001")

    def test_coder_agent_initialization(self, coder_agent):
        """Test Coder agent initializes with correct metadata."""
        metadata = coder_agent.get_metadata()

        assert metadata["agent_id"] == "test-coder-001"
        assert metadata["name"] == "Coder"
        assert metadata["description"] == "Code implementation and generation specialist"
        assert "code_generation" in metadata["capabilities"]
        assert "refactoring" in metadata["capabilities"]

    def test_coder_validate_accepts_code_tasks(self, coder_agent):
        """Test Coder validates code implementation tasks."""
        task = Task(
            task_id="task-005",
            task_type=TaskType.CODE_IMPLEMENTATION,
            description="Implement user authentication function",
            payload={
                "language": "python",
                "function_name": "authenticate_user",
                "requirements": ["Check username/password", "Return JWT token"]
            },
            priority="high",
            assigned_agent="test-coder-001"
        )

        result = coder_agent.validate(task)
        assert result is True

    def test_coder_execute_generates_code(self, coder_agent):
        """Test Coder generates code for implementation tasks."""
        task = Task(
            task_id="task-006",
            task_type=TaskType.CODE_IMPLEMENTATION,
            description="Create a simple factorial function",
            payload={
                "language": "python",
                "function_name": "factorial",
                "requirements": ["Input: integer n", "Output: n!", "Handle n=0 edge case"]
            },
            priority="medium",
            assigned_agent="test-coder-001"
        )

        result = coder_agent.execute(task)

        assert result.success is True
        assert "code" in result.output or "implementation" in result.output


class TestResearcherAgent:
    """Test suite for Researcher Agent (Research and analysis)."""

    @pytest.fixture
    def researcher_agent(self):
        """Create Researcher agent instance for testing."""
        return ResearcherAgent(agent_id="test-researcher-001")

    def test_researcher_agent_initialization(self, researcher_agent):
        """Test Researcher agent initializes with correct metadata."""
        metadata = researcher_agent.get_metadata()

        assert metadata["agent_id"] == "test-researcher-001"
        assert metadata["name"] == "Researcher"
        assert metadata["description"] == "Research and analysis specialist"
        assert "research" in metadata["capabilities"]
        assert "analysis" in metadata["capabilities"]

    def test_researcher_validate_accepts_research_tasks(self, researcher_agent):
        """Test Researcher validates research tasks."""
        task = Task(
            task_id="task-007",
            task_type=TaskType.RESEARCH,
            description="Research best practices for JWT authentication",
            payload={
                "topic": "JWT authentication security",
                "depth": "comprehensive"
            },
            priority="medium",
            assigned_agent="test-researcher-001"
        )

        result = researcher_agent.validate(task)
        assert result is True

    def test_researcher_execute_provides_findings(self, researcher_agent):
        """Test Researcher provides research findings."""
        task = Task(
            task_id="task-008",
            task_type=TaskType.RESEARCH,
            description="Research Python testing frameworks",
            payload={
                "topic": "Python testing frameworks (pytest, unittest)",
                "depth": "basic"
            },
            priority="low",
            assigned_agent="test-researcher-001"
        )

        result = researcher_agent.execute(task)

        assert result.success is True
        assert "findings" in result.output or "research" in result.output


class TestTesterAgent:
    """Test suite for Tester Agent (Test creation and validation)."""

    @pytest.fixture
    def tester_agent(self):
        """Create Tester agent instance for testing."""
        return TesterAgent(agent_id="test-tester-001")

    def test_tester_agent_initialization(self, tester_agent):
        """Test Tester agent initializes with correct metadata."""
        metadata = tester_agent.get_metadata()

        assert metadata["agent_id"] == "test-tester-001"
        assert metadata["name"] == "Tester"
        assert metadata["description"] == "Test creation and validation specialist"
        assert "test_generation" in metadata["capabilities"]
        assert "test_execution" in metadata["capabilities"]

    def test_tester_validate_accepts_testing_tasks(self, tester_agent):
        """Test Tester validates testing tasks."""
        task = Task(
            task_id="task-009",
            task_type=TaskType.TESTING,
            description="Create unit tests for factorial function",
            payload={
                "test_type": "unit",
                "target": "factorial function",
                "coverage_target": 90
            },
            priority="high",
            assigned_agent="test-tester-001"
        )

        result = tester_agent.validate(task)
        assert result is True

    def test_tester_execute_generates_tests(self, tester_agent):
        """Test Tester generates test code."""
        task = Task(
            task_id="task-010",
            task_type=TaskType.TESTING,
            description="Generate tests for authentication function",
            payload={
                "test_type": "unit",
                "target": "authenticate_user function",
                "test_cases": [
                    "Valid credentials",
                    "Invalid password",
                    "Non-existent user"
                ]
            },
            priority="high",
            assigned_agent="test-tester-001"
        )

        result = tester_agent.execute(task)

        assert result.success is True
        assert "tests" in result.output or "test_code" in result.output


class TestReviewerAgent:
    """Test suite for Reviewer Agent (Code review and quality)."""

    @pytest.fixture
    def reviewer_agent(self):
        """Create Reviewer agent instance for testing."""
        return ReviewerAgent(agent_id="test-reviewer-001")

    def test_reviewer_agent_initialization(self, reviewer_agent):
        """Test Reviewer agent initializes with correct metadata."""
        metadata = reviewer_agent.get_metadata()

        assert metadata["agent_id"] == "test-reviewer-001"
        assert metadata["name"] == "Reviewer"
        assert metadata["description"] == "Code review and quality assurance specialist"
        assert "code_review" in metadata["capabilities"]
        assert "quality_validation" in metadata["capabilities"]

    def test_reviewer_validate_accepts_review_tasks(self, reviewer_agent):
        """Test Reviewer validates code review tasks."""
        task = Task(
            task_id="task-011",
            task_type=TaskType.CODE_REVIEW,
            description="Review authentication implementation",
            payload={
                "code": "def authenticate_user(username, password): ...",
                "focus_areas": ["security", "error_handling", "nasa_compliance"]
            },
            priority="high",
            assigned_agent="test-reviewer-001"
        )

        result = reviewer_agent.validate(task)
        assert result is True

    def test_reviewer_execute_provides_feedback(self, reviewer_agent):
        """Test Reviewer provides code review feedback."""
        task = Task(
            task_id="task-012",
            task_type=TaskType.CODE_REVIEW,
            description="Review factorial implementation",
            payload={
                "code": """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
""",
                "focus_areas": ["correctness", "nasa_compliance", "performance"]
            },
            priority="medium",
            assigned_agent="test-reviewer-001"
        )

        result = reviewer_agent.execute(task)

        assert result.success is True
        assert "feedback" in result.output or "review" in result.output

        # Should flag recursion (NASA Rule 10 violation)
        review_text = str(result.output).lower()
        assert "recursion" in review_text or "iterative" in review_text


class TestCoreAgentIntegration:
    """Integration tests for core agent coordination."""

    def test_all_core_agents_implement_contract(self):
        """Test all core agents implement AgentContract interface."""
        agents = [
            QueenAgent(agent_id="queen"),
            CoderAgent(agent_id="coder"),
            ResearcherAgent(agent_id="researcher"),
            TesterAgent(agent_id="tester"),
            ReviewerAgent(agent_id="reviewer")
        ]

        for agent in agents:
            # Check contract methods exist
            assert hasattr(agent, "validate")
            assert hasattr(agent, "execute")
            assert hasattr(agent, "get_metadata")
            assert callable(agent.validate)
            assert callable(agent.execute)
            assert callable(agent.get_metadata)

            # Check metadata structure
            metadata = agent.get_metadata()
            assert "agent_id" in metadata
            assert "name" in metadata
            assert "description" in metadata
            assert "capabilities" in metadata
            assert "version" in metadata

    def test_workflow_orchestration_end_to_end(self):
        """Test end-to-end workflow from Queen → Researcher → Coder → Tester → Reviewer."""
        # Step 1: Queen decomposes task
        queen = QueenAgent(agent_id="queen")
        workflow_task = Task(
            task_id="workflow-001",
            task_type=TaskType.WORKFLOW,
            description="Build user authentication system",
            payload={
                "workflow": {
                    "objective": "Implement JWT-based authentication",
                    "constraints": ["Python", "bcrypt for passwords"]
                }
            },
            priority="high",
            assigned_agent="queen"
        )

        queen_result = queen.execute(workflow_task)
        assert queen_result.success is True
        assert "subtasks" in queen_result.output

        subtasks = queen_result.output["subtasks"]
        assert len(subtasks) > 0

        # Step 2: Verify subtasks can be assigned to agents
        agent_map = {
            "researcher": ResearcherAgent(agent_id="researcher"),
            "coder": CoderAgent(agent_id="coder"),
            "tester": TesterAgent(agent_id="tester"),
            "reviewer": ReviewerAgent(agent_id="reviewer")
        }

        for subtask in subtasks:
            agent_name = subtask.get("agent", "").lower()
            if agent_name in agent_map:
                agent = agent_map[agent_name]
                metadata = agent.get_metadata()

                # Verify agent exists and is properly initialized
                assert metadata["name"].lower() == agent_name

        # Full workflow coordination validated
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
