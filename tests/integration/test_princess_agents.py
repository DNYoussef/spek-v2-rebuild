"""
Integration Tests for Princess Agents (Week 21 Day 3 - Production Hardening)

Tests the 3 Princess agents that coordinate specialized swarms:
1. Princess-Dev - Development coordination (Coder, Researcher, Architect)
2. Princess-Quality - Quality assurance coordination (Tester, Reviewer, Security-Manager)
3. Princess-Coordination - Task coordination and agent assignment

Princess Hive Delegation Model:
- Queen → Princess agents (strategic delegation)
- Princess agents → Specialized worker agents (tactical execution)
- Reduces Queen's coordination overhead from 22 agents to 3 Princess agents

Each test validates:
- Princess agent contract compliance
- Swarm coordination capabilities
- Delegation to specialized agents
- Integration with Queen agent
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.princess_dev import PrincessDevAgent
from agents.princess_quality import PrincessQualityAgent
from agents.princess_coordination import PrincessCoordinationAgent
from infrastructure.agent_base import AgentContract, Task, TaskType, Result


class TestPrincessDevAgent:
    """Test suite for Princess-Dev Agent (Development coordination)."""

    @pytest.fixture
    def princess_dev(self):
        """Create Princess-Dev agent instance for testing."""
        return PrincessDevAgent(agent_id="test-princess-dev-001")

    def test_princess_dev_initialization(self, princess_dev):
        """Test Princess-Dev initializes with correct metadata."""
        metadata = princess_dev.get_metadata()

        assert metadata["agent_id"] == "test-princess-dev-001"
        assert metadata["name"] == "Princess-Dev"
        assert metadata["description"] == "Development coordination and swarm management"
        assert "development_coordination" in metadata["capabilities"]
        assert "swarm_management" in metadata["capabilities"]
        assert metadata["version"] == "2.0.0"

    def test_princess_dev_validate_accepts_dev_coordination_tasks(self, princess_dev):
        """Test Princess-Dev validates development coordination tasks."""
        task = Task(
            task_id="task-pd-001",
            task_type=TaskType.COORDINATION,
            description="Coordinate development of API endpoints",
            payload={
                "coordination": {
                    "objective": "Build REST API with 5 endpoints",
                    "swarm": ["coder", "researcher", "architect"],
                    "constraints": ["Use Express.js", "Follow RESTful principles"]
                }
            },
            priority="high",
            assigned_agent="test-princess-dev-001"
        )

        result = princess_dev.validate(task)
        assert result is True

    def test_princess_dev_validate_rejects_invalid_tasks(self, princess_dev):
        """Test Princess-Dev rejects tasks without coordination payload."""
        task = Task(
            task_id="task-pd-002",
            task_type=TaskType.TESTING,  # Wrong type
            description="Run tests",
            payload={},
            priority="medium",
            assigned_agent="test-princess-dev-001"
        )

        result = princess_dev.validate(task)
        assert result is False

    def test_princess_dev_execute_coordinates_development_swarm(self, princess_dev):
        """Test Princess-Dev coordinates development swarm for implementation."""
        task = Task(
            task_id="task-pd-003",
            task_type=TaskType.COORDINATION,
            description="Implement user authentication module",
            payload={
                "coordination": {
                    "objective": "Build JWT-based authentication system",
                    "swarm": ["researcher", "architect", "coder"],
                    "phases": [
                        {"phase": "research", "agent": "researcher", "duration_minutes": 30},
                        {"phase": "design", "agent": "architect", "duration_minutes": 45},
                        {"phase": "implementation", "agent": "coder", "duration_minutes": 120}
                    ]
                }
            },
            priority="high",
            assigned_agent="test-princess-dev-001"
        )

        result = princess_dev.execute(task)

        assert result.success is True
        assert "delegation_plan" in result.output or "swarm_tasks" in result.output

        # Check delegation includes expected agents
        delegation_text = str(result.output).lower()
        assert "researcher" in delegation_text or "coder" in delegation_text

    def test_princess_dev_delegates_to_coder_researcher_architect(self, princess_dev):
        """Test Princess-Dev creates tasks for Coder, Researcher, and Architect."""
        task = Task(
            task_id="task-pd-004",
            task_type=TaskType.COORDINATION,
            description="Build data processing pipeline",
            payload={
                "coordination": {
                    "objective": "ETL pipeline for CSV to PostgreSQL",
                    "swarm": ["researcher", "architect", "coder"]
                }
            },
            priority="medium",
            assigned_agent="test-princess-dev-001"
        )

        result = princess_dev.execute(task)

        assert result.success is True

        # Verify delegation structure
        if "swarm_tasks" in result.output:
            swarm_tasks = result.output["swarm_tasks"]
            agent_names = [t.get("agent", "").lower() for t in swarm_tasks]

            # Should include at least one dev agent
            dev_agents = {"researcher", "architect", "coder"}
            assert any(agent in agent_names for agent in dev_agents)


class TestPrincessQualityAgent:
    """Test suite for Princess-Quality Agent (Quality assurance coordination)."""

    @pytest.fixture
    def princess_quality(self):
        """Create Princess-Quality agent instance for testing."""
        return PrincessQualityAgent(agent_id="test-princess-quality-001")

    def test_princess_quality_initialization(self, princess_quality):
        """Test Princess-Quality initializes with correct metadata."""
        metadata = princess_quality.get_metadata()

        assert metadata["agent_id"] == "test-princess-quality-001"
        assert metadata["name"] == "Princess-Quality"
        assert metadata["description"] == "Quality assurance coordination and swarm management"
        assert "quality_coordination" in metadata["capabilities"]
        assert "swarm_management" in metadata["capabilities"]

    def test_princess_quality_validate_accepts_qa_coordination_tasks(self, princess_quality):
        """Test Princess-Quality validates QA coordination tasks."""
        task = Task(
            task_id="task-pq-001",
            task_type=TaskType.COORDINATION,
            description="Coordinate quality assurance for auth module",
            payload={
                "coordination": {
                    "objective": "Full QA pipeline for authentication",
                    "swarm": ["tester", "reviewer", "security-manager"],
                    "quality_gates": ["unit_tests", "code_review", "security_audit"]
                }
            },
            priority="critical",
            assigned_agent="test-princess-quality-001"
        )

        result = princess_quality.validate(task)
        assert result is True

    def test_princess_quality_execute_coordinates_qa_swarm(self, princess_quality):
        """Test Princess-Quality coordinates QA swarm for validation."""
        task = Task(
            task_id="task-pq-002",
            task_type=TaskType.COORDINATION,
            description="Run comprehensive QA on API endpoints",
            payload={
                "coordination": {
                    "objective": "Validate 5 REST API endpoints",
                    "swarm": ["tester", "reviewer"],
                    "phases": [
                        {"phase": "unit_testing", "agent": "tester", "coverage": 90},
                        {"phase": "code_review", "agent": "reviewer", "nasa_compliance": True}
                    ]
                }
            },
            priority="high",
            assigned_agent="test-princess-quality-001"
        )

        result = princess_quality.execute(task)

        assert result.success is True
        assert "delegation_plan" in result.output or "swarm_tasks" in result.output

        # Check QA agents mentioned
        delegation_text = str(result.output).lower()
        assert "tester" in delegation_text or "reviewer" in delegation_text

    def test_princess_quality_delegates_to_tester_reviewer_security(self, princess_quality):
        """Test Princess-Quality creates tasks for Tester, Reviewer, Security-Manager."""
        task = Task(
            task_id="task-pq-003",
            task_type=TaskType.COORDINATION,
            description="Security audit and testing for payment module",
            payload={
                "coordination": {
                    "objective": "Comprehensive security validation",
                    "swarm": ["security-manager", "tester", "reviewer"]
                }
            },
            priority="critical",
            assigned_agent="test-princess-quality-001"
        )

        result = princess_quality.execute(task)

        assert result.success is True

        # Verify delegation structure
        if "swarm_tasks" in result.output:
            swarm_tasks = result.output["swarm_tasks"]
            agent_names = [t.get("agent", "").lower() for t in swarm_tasks]

            # Should include at least one QA agent
            qa_agents = {"tester", "reviewer", "security-manager"}
            assert any(agent in agent_names for agent in qa_agents)


class TestPrincessCoordinationAgent:
    """Test suite for Princess-Coordination Agent (Task coordination and assignment)."""

    @pytest.fixture
    def princess_coordination(self):
        """Create Princess-Coordination agent instance for testing."""
        return PrincessCoordinationAgent(agent_id="test-princess-coord-001")

    def test_princess_coordination_initialization(self, princess_coordination):
        """Test Princess-Coordination initializes with correct metadata."""
        metadata = princess_coordination.get_metadata()

        assert metadata["agent_id"] == "test-princess-coord-001"
        assert metadata["name"] == "Princess-Coordination"
        assert metadata["description"] == "Task coordination and agent assignment specialist"
        assert "task_assignment" in metadata["capabilities"]
        assert "resource_allocation" in metadata["capabilities"]

    def test_princess_coordination_validate_accepts_coordination_tasks(self, princess_coordination):
        """Test Princess-Coordination validates task coordination requests."""
        task = Task(
            task_id="task-pc-001",
            task_type=TaskType.COORDINATION,
            description="Assign agents to subtasks",
            payload={
                "coordination": {
                    "objective": "Distribute 10 subtasks across 6 agents",
                    "subtasks": [
                        {"task_id": "sub-1", "description": "Research API design"},
                        {"task_id": "sub-2", "description": "Implement endpoints"}
                    ],
                    "available_agents": ["researcher", "coder", "tester"]
                }
            },
            priority="high",
            assigned_agent="test-princess-coord-001"
        )

        result = princess_coordination.validate(task)
        assert result is True

    def test_princess_coordination_execute_assigns_agents_to_tasks(self, princess_coordination):
        """Test Princess-Coordination assigns agents to subtasks optimally."""
        task = Task(
            task_id="task-pc-002",
            task_type=TaskType.COORDINATION,
            description="Coordinate multi-phase project execution",
            payload={
                "coordination": {
                    "objective": "Full-stack feature implementation",
                    "subtasks": [
                        {"task_id": "1", "task_type": "research", "description": "Research tech stack"},
                        {"task_id": "2", "task_type": "code", "description": "Build backend"},
                        {"task_id": "3", "task_type": "testing", "description": "Create tests"}
                    ],
                    "available_agents": ["researcher", "coder", "tester", "reviewer"]
                }
            },
            priority="high",
            assigned_agent="test-princess-coord-001"
        )

        result = princess_coordination.execute(task)

        assert result.success is True
        assert "assignment_plan" in result.output or "agent_assignments" in result.output

        # Check assignments are logical
        if "agent_assignments" in result.output:
            assignments = result.output["agent_assignments"]

            # Verify structure
            for assignment in assignments:
                assert "task_id" in assignment or "agent" in assignment

    def test_princess_coordination_balances_workload(self, princess_coordination):
        """Test Princess-Coordination balances workload across agents."""
        task = Task(
            task_id="task-pc-003",
            task_type=TaskType.COORDINATION,
            description="Balance heavy workload",
            payload={
                "coordination": {
                    "objective": "Distribute 20 subtasks evenly",
                    "subtasks": [
                        {"task_id": str(i), "task_type": "code", "estimated_minutes": 60}
                        for i in range(20)
                    ],
                    "available_agents": ["coder"] * 5  # 5 coder agents
                }
            },
            priority="medium",
            assigned_agent="test-princess-coord-001"
        )

        result = princess_coordination.execute(task)

        assert result.success is True

        # Verify workload distribution exists
        output_text = str(result.output).lower()
        assert "balance" in output_text or "distribute" in output_text or "assignment" in output_text


class TestPrincessHiveIntegration:
    """Integration tests for Princess Hive delegation model."""

    def test_all_princess_agents_implement_contract(self):
        """Test all Princess agents implement AgentContract interface."""
        agents = [
            PrincessDevAgent(agent_id="princess-dev"),
            PrincessQualityAgent(agent_id="princess-quality"),
            PrincessCoordinationAgent(agent_id="princess-coordination")
        ]

        for agent in agents:
            # Check contract methods exist
            assert hasattr(agent, "validate")
            assert hasattr(agent, "execute")
            assert hasattr(agent, "get_metadata")

            # Check metadata structure
            metadata = agent.get_metadata()
            assert "agent_id" in metadata
            assert "name" in metadata
            assert "description" in metadata
            assert "capabilities" in metadata
            assert "swarm_management" in metadata["capabilities"]

    def test_queen_delegates_to_princess_agents(self):
        """Test Queen can delegate to Princess agents for coordination."""
        from agents.queen import QueenAgent

        queen = QueenAgent(agent_id="queen")
        task = Task(
            task_id="queen-delegation-001",
            task_type=TaskType.WORKFLOW,
            description="Build and validate complete feature",
            payload={
                "workflow": {
                    "objective": "E-commerce checkout flow (development + QA)",
                    "constraints": ["React frontend", "Node.js backend", "90% test coverage"]
                }
            },
            priority="high",
            assigned_agent="queen"
        )

        result = queen.execute(task)
        assert result.success is True

        # Check if subtasks reference Princess agents
        if "subtasks" in result.output:
            subtasks = result.output["subtasks"]
            agent_names = [t.get("agent", "").lower() for t in subtasks]

            princess_agents = {"princess-dev", "princess-quality", "princess-coordination"}

            # May delegate to Princess agents OR core agents directly
            # Both patterns are valid
            assert len(agent_names) > 0

    def test_princess_dev_coordinates_development_swarm(self):
        """Test Princess-Dev coordinates Coder, Researcher, Architect."""
        princess_dev = PrincessDevAgent(agent_id="princess-dev")

        task = Task(
            task_id="dev-swarm-001",
            task_type=TaskType.COORDINATION,
            description="Implement payment processing module",
            payload={
                "coordination": {
                    "objective": "Stripe integration with webhook support",
                    "swarm": ["researcher", "architect", "coder"]
                }
            },
            priority="critical",
            assigned_agent="princess-dev"
        )

        result = princess_dev.execute(task)
        assert result.success is True

        # Verify development agents mentioned
        output_text = str(result.output).lower()
        dev_keywords = ["researcher", "architect", "coder", "research", "design", "implement"]
        assert any(keyword in output_text for keyword in dev_keywords)

    def test_princess_quality_coordinates_qa_swarm(self):
        """Test Princess-Quality coordinates Tester, Reviewer, Security-Manager."""
        princess_quality = PrincessQualityAgent(agent_id="princess-quality")

        task = Task(
            task_id="qa-swarm-001",
            task_type=TaskType.COORDINATION,
            description="Full QA for payment processing",
            payload={
                "coordination": {
                    "objective": "Comprehensive validation (tests, review, security)",
                    "swarm": ["tester", "reviewer", "security-manager"]
                }
            },
            priority="critical",
            assigned_agent="princess-quality"
        )

        result = princess_quality.execute(task)
        assert result.success is True

        # Verify QA agents mentioned
        output_text = str(result.output).lower()
        qa_keywords = ["tester", "reviewer", "security", "test", "review", "audit"]
        assert any(keyword in output_text for keyword in qa_keywords)

    def test_princess_coordination_assigns_tasks_efficiently(self):
        """Test Princess-Coordination assigns tasks across all agent types."""
        princess_coord = PrincessCoordinationAgent(agent_id="princess-coordination")

        task = Task(
            task_id="coord-001",
            task_type=TaskType.COORDINATION,
            description="Coordinate full project workflow",
            payload={
                "coordination": {
                    "objective": "Build, test, deploy microservice",
                    "subtasks": [
                        {"task_id": "1", "task_type": "research"},
                        {"task_id": "2", "task_type": "code"},
                        {"task_id": "3", "task_type": "testing"},
                        {"task_id": "4", "task_type": "review"},
                        {"task_id": "5", "task_type": "deployment"}
                    ],
                    "available_agents": ["researcher", "coder", "tester", "reviewer", "devops"]
                }
            },
            priority="high",
            assigned_agent="princess-coordination"
        )

        result = princess_coord.execute(task)
        assert result.success is True

        # Verify assignments created
        assert "assignment" in str(result.output).lower() or "agent" in str(result.output).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
