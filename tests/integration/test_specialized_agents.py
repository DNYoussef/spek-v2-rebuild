"""
Integration Tests for Specialized Agents (Week 21 Day 3 - Production Hardening)

Tests the 14 specialized agents that provide domain-specific functionality:

SPARC Workflow (4 agents):
1. Architect - System architecture and design
2. Pseudocode-Writer - Algorithm design
3. Spec-Writer - Requirements documentation
4. Integration-Engineer - System integration

Development (5 agents):
5. Debugger - Bug fixing and debugging
6. Docs-Writer - Documentation generation
7. DevOps - Deployment automation
8. Security-Manager - Security validation
9. Cost-Tracker - Budget monitoring

Governance (5 agents):
10. Theater-Detector - Mock code detection
11. NASA-Enforcer - NASA Rule 10 compliance
12. FSM-Analyzer - FSM validation
13. Orchestrator - Workflow orchestration
14. Planner - Task planning

Each test validates agent contract compliance and core functionality.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from infrastructure.agent_base import AgentContract, Task, TaskType, Result

# SPARC Workflow Agents
from agents.architect import ArchitectAgent
from agents.pseudocode_writer import PseudocodeWriterAgent
from agents.spec_writer import SpecWriterAgent
from agents.integration_engineer import IntegrationEngineerAgent

# Development Agents
from agents.debugger import DebuggerAgent
from agents.docs_writer import DocsWriterAgent
from agents.devops import DevOpsAgent
from agents.security_manager import SecurityManagerAgent
from agents.cost_tracker import CostTrackerAgent

# Governance Agents
from agents.theater_detector import TheaterDetectorAgent
from agents.nasa_enforcer import NASAEnforcerAgent
from agents.fsm_analyzer import FSMAnalyzerAgent
from agents.orchestrator import OrchestratorAgent
from agents.planner import PlannerAgent


class TestSPARCWorkflowAgents:
    """Test suite for SPARC workflow agents."""

    def test_architect_agent(self):
        """Test Architect agent for system design."""
        agent = ArchitectAgent(agent_id="test-architect")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Architect"
        assert "architecture_design" in metadata["capabilities"]

        task = Task(
            task_id="arch-001",
            task_type=TaskType.ARCHITECTURE,
            description="Design microservices architecture",
            payload={"requirements": ["High availability", "Scalability"]},
            priority="high",
            assigned_agent="test-architect"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_pseudocode_writer_agent(self):
        """Test Pseudocode-Writer agent for algorithm design."""
        agent = PseudocodeWriterAgent(agent_id="test-pseudocode")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Pseudocode-Writer"
        assert "algorithm_design" in metadata["capabilities"]

        task = Task(
            task_id="pseudo-001",
            task_type=TaskType.PSEUDOCODE,
            description="Design sorting algorithm",
            payload={"algorithm": "quicksort", "language": "python"},
            priority="medium",
            assigned_agent="test-pseudocode"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_spec_writer_agent(self):
        """Test Spec-Writer agent for requirements documentation."""
        agent = SpecWriterAgent(agent_id="test-spec")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Spec-Writer"
        assert "specification_writing" in metadata["capabilities"]

        task = Task(
            task_id="spec-001",
            task_type=TaskType.SPECIFICATION,
            description="Write API specification",
            payload={"feature": "User authentication API"},
            priority="high",
            assigned_agent="test-spec"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_integration_engineer_agent(self):
        """Test Integration-Engineer agent for system integration."""
        agent = IntegrationEngineerAgent(agent_id="test-integration")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Integration-Engineer"
        assert "system_integration" in metadata["capabilities"]

        task = Task(
            task_id="integ-001",
            task_type=TaskType.INTEGRATION,
            description="Integrate payment gateway",
            payload={"systems": ["API", "Payment Gateway", "Database"]},
            priority="critical",
            assigned_agent="test-integration"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True


class TestDevelopmentAgents:
    """Test suite for development support agents."""

    def test_debugger_agent(self):
        """Test Debugger agent for bug fixing."""
        agent = DebuggerAgent(agent_id="test-debugger")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Debugger"
        assert "debugging" in metadata["capabilities"]

        task = Task(
            task_id="debug-001",
            task_type=TaskType.DEBUGGING,
            description="Fix null pointer exception",
            payload={
                "error": "NullPointerException at line 42",
                "code": "user.getName().toUpperCase()"
            },
            priority="critical",
            assigned_agent="test-debugger"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_docs_writer_agent(self):
        """Test Docs-Writer agent for documentation generation."""
        agent = DocsWriterAgent(agent_id="test-docs")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Docs-Writer"
        assert "documentation_generation" in metadata["capabilities"]

        task = Task(
            task_id="docs-001",
            task_type=TaskType.DOCUMENTATION,
            description="Generate API documentation",
            payload={"api": "User Management API", "format": "markdown"},
            priority="medium",
            assigned_agent="test-docs"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_devops_agent(self):
        """Test DevOps agent for deployment automation."""
        agent = DevOpsAgent(agent_id="test-devops")
        metadata = agent.get_metadata()

        assert metadata["name"] == "DevOps"
        assert "deployment_automation" in metadata["capabilities"]

        task = Task(
            task_id="devops-001",
            task_type=TaskType.DEPLOYMENT,
            description="Deploy to production",
            payload={
                "environment": "production",
                "services": ["api", "worker", "database"]
            },
            priority="critical",
            assigned_agent="test-devops"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_security_manager_agent(self):
        """Test Security-Manager agent for security validation."""
        agent = SecurityManagerAgent(agent_id="test-security")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Security-Manager"
        assert "security_validation" in metadata["capabilities"]

        task = Task(
            task_id="sec-001",
            task_type=TaskType.SECURITY_AUDIT,
            description="Security audit for authentication module",
            payload={
                "target": "authentication module",
                "checks": ["SQL injection", "XSS", "CSRF"]
            },
            priority="critical",
            assigned_agent="test-security"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_cost_tracker_agent(self):
        """Test Cost-Tracker agent for budget monitoring."""
        agent = CostTrackerAgent(agent_id="test-cost")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Cost-Tracker"
        assert "cost_monitoring" in metadata["capabilities"]

        task = Task(
            task_id="cost-001",
            task_type=TaskType.MONITORING,
            description="Track API costs",
            payload={
                "services": ["Claude API", "Gemini API"],
                "period": "monthly"
            },
            priority="low",
            assigned_agent="test-cost"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True


class TestGovernanceAgents:
    """Test suite for governance and quality agents."""

    def test_theater_detector_agent(self):
        """Test Theater-Detector agent for mock code detection."""
        agent = TheaterDetectorAgent(agent_id="test-theater")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Theater-Detector"
        assert "mock_detection" in metadata["capabilities"]

        task = Task(
            task_id="theater-001",
            task_type=TaskType.QUALITY_AUDIT,
            description="Scan codebase for theater code",
            payload={
                "target": "src/",
                "threshold": 60
            },
            priority="medium",
            assigned_agent="test-theater"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_nasa_enforcer_agent(self):
        """Test NASA-Enforcer agent for NASA Rule 10 compliance."""
        agent = NASAEnforcerAgent(agent_id="test-nasa")
        metadata = agent.get_metadata()

        assert metadata["name"] == "NASA-Enforcer"
        assert "nasa_compliance" in metadata["capabilities"]

        task = Task(
            task_id="nasa-001",
            task_type=TaskType.QUALITY_AUDIT,
            description="Check NASA Rule 10 compliance",
            payload={
                "target": "src/agents/",
                "rules": ["max_function_length", "no_recursion"]
            },
            priority="high",
            assigned_agent="test-nasa"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_fsm_analyzer_agent(self):
        """Test FSM-Analyzer agent for FSM validation."""
        agent = FSMAnalyzerAgent(agent_id="test-fsm")
        metadata = agent.get_metadata()

        assert metadata["name"] == "FSM-Analyzer"
        assert "fsm_validation" in metadata["capabilities"]

        task = Task(
            task_id="fsm-001",
            task_type=TaskType.QUALITY_AUDIT,
            description="Analyze FSM usage",
            payload={
                "target": "src/workflows/",
                "check_decision_matrix": True
            },
            priority="medium",
            assigned_agent="test-fsm"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_orchestrator_agent(self):
        """Test Orchestrator agent for workflow orchestration."""
        agent = OrchestratorAgent(agent_id="test-orchestrator")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Orchestrator"
        assert "workflow_orchestration" in metadata["capabilities"]

        task = Task(
            task_id="orch-001",
            task_type=TaskType.WORKFLOW,
            description="Orchestrate deployment workflow",
            payload={
                "workflow": "CI/CD pipeline",
                "stages": ["build", "test", "deploy"]
            },
            priority="high",
            assigned_agent="test-orchestrator"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True

    def test_planner_agent(self):
        """Test Planner agent for task planning."""
        agent = PlannerAgent(agent_id="test-planner")
        metadata = agent.get_metadata()

        assert metadata["name"] == "Planner"
        assert "task_planning" in metadata["capabilities"]

        task = Task(
            task_id="plan-001",
            task_type=TaskType.PLANNING,
            description="Plan sprint tasks",
            payload={
                "objective": "Implement user profile page",
                "duration": "2 weeks"
            },
            priority="medium",
            assigned_agent="test-planner"
        )

        assert agent.validate(task) is True
        result = agent.execute(task)
        assert result.success is True


class TestSpecializedAgentIntegration:
    """Integration tests for specialized agents."""

    def test_all_specialized_agents_implement_contract(self):
        """Test all 14 specialized agents implement AgentContract."""
        agents = [
            # SPARC Workflow
            ArchitectAgent(agent_id="architect"),
            PseudocodeWriterAgent(agent_id="pseudocode"),
            SpecWriterAgent(agent_id="spec"),
            IntegrationEngineerAgent(agent_id="integration"),
            # Development
            DebuggerAgent(agent_id="debugger"),
            DocsWriterAgent(agent_id="docs"),
            DevOpsAgent(agent_id="devops"),
            SecurityManagerAgent(agent_id="security"),
            CostTrackerAgent(agent_id="cost"),
            # Governance
            TheaterDetectorAgent(agent_id="theater"),
            NASAEnforcerAgent(agent_id="nasa"),
            FSMAnalyzerAgent(agent_id="fsm"),
            OrchestratorAgent(agent_id="orchestrator"),
            PlannerAgent(agent_id="planner")
        ]

        assert len(agents) == 14, "Should have exactly 14 specialized agents"

        for agent in agents:
            # Check contract methods
            assert hasattr(agent, "validate")
            assert hasattr(agent, "execute")
            assert hasattr(agent, "get_metadata")

            # Check metadata structure
            metadata = agent.get_metadata()
            assert "agent_id" in metadata
            assert "name" in metadata
            assert "description" in metadata
            assert "capabilities" in metadata
            assert "version" in metadata

    def test_sparc_workflow_integration(self):
        """Test SPARC workflow: Spec → Pseudocode → Architecture → Integration."""
        # Step 1: Spec-Writer creates specification
        spec_agent = SpecWriterAgent(agent_id="spec")
        spec_task = Task(
            task_id="sparc-1",
            task_type=TaskType.SPECIFICATION,
            description="Write spec for payment module",
            payload={"feature": "Stripe payment integration"},
            priority="high",
            assigned_agent="spec"
        )
        spec_result = spec_agent.execute(spec_task)
        assert spec_result.success is True

        # Step 2: Pseudocode-Writer designs algorithm
        pseudo_agent = PseudocodeWriterAgent(agent_id="pseudocode")
        pseudo_task = Task(
            task_id="sparc-2",
            task_type=TaskType.PSEUDOCODE,
            description="Design payment processing algorithm",
            payload={"spec": spec_result.output},
            priority="high",
            assigned_agent="pseudocode"
        )
        pseudo_result = pseudo_agent.execute(pseudo_task)
        assert pseudo_result.success is True

        # Step 3: Architect designs system
        arch_agent = ArchitectAgent(agent_id="architect")
        arch_task = Task(
            task_id="sparc-3",
            task_type=TaskType.ARCHITECTURE,
            description="Design payment system architecture",
            payload={"pseudocode": pseudo_result.output},
            priority="high",
            assigned_agent="architect"
        )
        arch_result = arch_agent.execute(arch_task)
        assert arch_result.success is True

        # Step 4: Integration-Engineer integrates
        integ_agent = IntegrationEngineerAgent(agent_id="integration")
        integ_task = Task(
            task_id="sparc-4",
            task_type=TaskType.INTEGRATION,
            description="Integrate payment system",
            payload={"architecture": arch_result.output},
            priority="high",
            assigned_agent="integration"
        )
        integ_result = integ_agent.execute(integ_task)
        assert integ_result.success is True

    def test_quality_gate_workflow(self):
        """Test quality gate workflow: Theater → NASA → Security."""
        # Step 1: Theater-Detector scans for mock code
        theater_agent = TheaterDetectorAgent(agent_id="theater")
        theater_task = Task(
            task_id="qa-1",
            task_type=TaskType.QUALITY_AUDIT,
            description="Scan for theater code",
            payload={"target": "src/"},
            priority="high",
            assigned_agent="theater"
        )
        theater_result = theater_agent.execute(theater_task)
        assert theater_result.success is True

        # Step 2: NASA-Enforcer checks compliance
        nasa_agent = NASAEnforcerAgent(agent_id="nasa")
        nasa_task = Task(
            task_id="qa-2",
            task_type=TaskType.QUALITY_AUDIT,
            description="Check NASA Rule 10",
            payload={"target": "src/"},
            priority="high",
            assigned_agent="nasa"
        )
        nasa_result = nasa_agent.execute(nasa_task)
        assert nasa_result.success is True

        # Step 3: Security-Manager audits security
        sec_agent = SecurityManagerAgent(agent_id="security")
        sec_task = Task(
            task_id="qa-3",
            task_type=TaskType.SECURITY_AUDIT,
            description="Security audit",
            payload={"target": "src/"},
            priority="critical",
            assigned_agent="security"
        )
        sec_result = sec_agent.execute(sec_task)
        assert sec_result.success is True

    def test_deployment_workflow(self):
        """Test deployment workflow: Planner → DevOps → Cost-Tracker."""
        # Step 1: Planner creates deployment plan
        planner_agent = PlannerAgent(agent_id="planner")
        plan_task = Task(
            task_id="deploy-1",
            task_type=TaskType.PLANNING,
            description="Plan production deployment",
            payload={"environment": "production"},
            priority="high",
            assigned_agent="planner"
        )
        plan_result = planner_agent.execute(plan_task)
        assert plan_result.success is True

        # Step 2: DevOps executes deployment
        devops_agent = DevOpsAgent(agent_id="devops")
        devops_task = Task(
            task_id="deploy-2",
            task_type=TaskType.DEPLOYMENT,
            description="Deploy to production",
            payload={"plan": plan_result.output},
            priority="critical",
            assigned_agent="devops"
        )
        devops_result = devops_agent.execute(devops_task)
        assert devops_result.success is True

        # Step 3: Cost-Tracker monitors costs
        cost_agent = CostTrackerAgent(agent_id="cost")
        cost_task = Task(
            task_id="deploy-3",
            task_type=TaskType.MONITORING,
            description="Track deployment costs",
            payload={"deployment": devops_result.output},
            priority="medium",
            assigned_agent="cost"
        )
        cost_result = cost_agent.execute(cost_task)
        assert cost_result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
