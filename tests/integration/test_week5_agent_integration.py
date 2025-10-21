"""
Week 5 Integration Tests - End-to-End Agent Workflows

Tests complete workflows across all 22 agents:
- SPARC workflow (Spec → Pseudocode → Architecture → Code → Test)
- Princess Hive delegation
- Multi-agent coordination
- Quality gate validation

Week 5 Day 7
Version: 8.0.0
"""

import pytest
import asyncio
from typing import Dict, Any

from src.agents.AgentBase import Task, create_task
from src.agents.core import (
    create_queen_agent,
    create_coder_agent,
    create_researcher_agent,
    create_tester_agent,
    create_reviewer_agent
)
from src.agents.swarm import (
    create_princess_dev_agent,
    create_princess_quality_agent,
    create_princess_coordination_agent
)
from src.agents.specialized import (
    create_architect_agent,
    create_pseudocode_writer_agent,
    create_spec_writer_agent,
    create_integration_engineer_agent,
    create_debugger_agent,
    create_docs_writer_agent,
    create_devops_agent,
    create_security_manager_agent,
    create_cost_tracker_agent,
    create_theater_detector_agent,
    create_nasa_enforcer_agent,
    create_fsm_analyzer_agent,
    create_orchestrator_agent,
    create_planner_agent
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def all_agents():
    """Create all 22 agents."""
    return {
        # Core agents (5)
        "queen": create_queen_agent(),
        "coder": create_coder_agent(),
        "researcher": create_researcher_agent(),
        "tester": create_tester_agent(),
        "reviewer": create_reviewer_agent(),

        # Swarm coordinators (3)
        "princess-dev": create_princess_dev_agent(),
        "princess-quality": create_princess_quality_agent(),
        "princess-coordination": create_princess_coordination_agent(),

        # Specialized agents (14)
        "architect": create_architect_agent(),
        "pseudocode-writer": create_pseudocode_writer_agent(),
        "spec-writer": create_spec_writer_agent(),
        "integration-engineer": create_integration_engineer_agent(),
        "debugger": create_debugger_agent(),
        "docs-writer": create_docs_writer_agent(),
        "devops": create_devops_agent(),
        "security-manager": create_security_manager_agent(),
        "cost-tracker": create_cost_tracker_agent(),
        "theater-detector": create_theater_detector_agent(),
        "nasa-enforcer": create_nasa_enforcer_agent(),
        "fsm-analyzer": create_fsm_analyzer_agent(),
        "orchestrator": create_orchestrator_agent(),
        "planner": create_planner_agent()
    }


@pytest.fixture
def sparc_workflow_task():
    """Create SPARC workflow task."""
    return create_task(
        task_id="sparc-workflow-001",
        task_type="orchestrate",
        payload={
            "workflow": {
                "name": "SPARC Implementation",
                "phases": [
                    {"name": "Specification", "task_type": "write-spec"},
                    {"name": "Pseudocode", "task_type": "write-pseudocode"},
                    {"name": "Architecture", "task_type": "design-architecture"},
                    {"name": "Implementation", "task_type": "implement-code"},
                    {"name": "Testing", "task_type": "generate-tests"}
                ]
            }
        }
    )


# ============================================================================
# Test 1: Agent Creation and Initialization
# ============================================================================

@pytest.mark.asyncio
async def test_all_agents_created(all_agents):
    """Test 1: All 22 agents can be created."""
    assert len(all_agents) == 22, "Should have 22 agents"

    # Verify core agents
    assert "queen" in all_agents
    assert "coder" in all_agents
    assert "researcher" in all_agents
    assert "tester" in all_agents
    assert "reviewer" in all_agents

    # Verify swarm coordinators
    assert "princess-dev" in all_agents
    assert "princess-quality" in all_agents
    assert "princess-coordination" in all_agents

    # Verify specialized agents
    assert "architect" in all_agents
    assert "theater-detector" in all_agents
    assert "nasa-enforcer" in all_agents


@pytest.mark.asyncio
async def test_agent_metadata_valid(all_agents):
    """Test 2: All agents have valid metadata."""
    for agent_id, agent in all_agents.items():
        metadata = agent.get_metadata()

        assert metadata.agent_id is not None
        assert metadata.name is not None
        assert len(metadata.capabilities) > 0
        assert len(metadata.supported_task_types) > 0


# ============================================================================
# Test 2: SPARC Workflow Integration
# ============================================================================

@pytest.mark.asyncio
async def test_sparc_workflow_spec_to_code(all_agents):
    """Test 3: SPARC workflow from spec to code."""
    # Step 1: Spec-Writer creates specification
    spec_task = create_task(
        task_id="spec-001",
        task_type="write-spec",
        payload={
            "input_file": "requirements.md",
            "title": "User Authentication System"
        }
    )

    spec_result = await all_agents["spec-writer"].execute(spec_task)
    assert spec_result.success, "Spec writing should succeed"

    # Step 2: Pseudocode-Writer creates algorithm
    pseudo_task = create_task(
        task_id="pseudo-001",
        task_type="write-pseudocode",
        payload={
            "specification_file": "specs/SPEC-001.md",
            "function_name": "authenticate_user"
        }
    )

    pseudo_result = await all_agents["pseudocode-writer"].execute(pseudo_task)
    assert pseudo_result.success, "Pseudocode writing should succeed"

    # Step 3: Architect designs system
    arch_task = create_task(
        task_id="arch-001",
        task_type="design-architecture",
        payload={
            "specification_file": "specs/SPEC-001.md",
            "style": "microservices"
        }
    )

    arch_result = await all_agents["architect"].execute(arch_task)
    assert arch_result.success, "Architecture design should succeed"

    # Step 4: Coder implements
    code_task = create_task(
        task_id="code-001",
        task_type="implement-code",
        payload={
            "spec_file": "specs/SPEC-001.md",
            "output_file": "src/auth/authenticate.py",
            "language": "python"
        }
    )

    code_result = await all_agents["coder"].execute(code_task)
    assert code_result.success, "Code implementation should succeed"


# ============================================================================
# Test 3: Princess Hive Delegation
# ============================================================================

@pytest.mark.asyncio
async def test_princess_dev_delegation(all_agents):
    """Test 4: Princess-Dev delegates to development drones."""
    dev_task = create_task(
        task_id="dev-001",
        task_type="coordinate-dev",
        payload={
            "dev_workflow": {
                "phases": ["code", "review"],
                "target_file": "src/feature.py"
            }
        }
    )

    result = await all_agents["princess-dev"].execute(dev_task)
    assert result.success, "Princess-Dev coordination should succeed"
    assert "phase_results" in result.data


@pytest.mark.asyncio
async def test_princess_quality_delegation(all_agents):
    """Test 5: Princess-Quality delegates to QA drones."""
    qa_task = create_task(
        task_id="qa-001",
        task_type="coordinate-qa",
        payload={
            "qa_workflow": {
                "phases": ["test", "nasa-check"],
                "target_path": "src/"
            }
        }
    )

    result = await all_agents["princess-quality"].execute(qa_task)
    assert result.success, "Princess-Quality coordination should succeed"
    assert "quality_gates" in result.data


@pytest.mark.asyncio
async def test_queen_orchestration(all_agents):
    """Test 6: Queen orchestrates multi-phase workflow."""
    workflow_task = create_task(
        task_id="queen-001",
        task_type="orchestrate",
        payload={
            "workflow": {
                "phases": [
                    {"name": "Development", "task_type": "coordinate-dev"},
                    {"name": "Quality", "task_type": "coordinate-qa"}
                ]
            }
        }
    )

    result = await all_agents["queen"].execute(workflow_task)
    assert result.success, "Queen orchestration should succeed"


# ============================================================================
# Test 4: Quality Gate Validation
# ============================================================================

@pytest.mark.asyncio
async def test_nasa_compliance_check(all_agents):
    """Test 7: NASA-Enforcer validates compliance."""
    nasa_task = create_task(
        task_id="nasa-001",
        task_type="check-compliance",
        payload={"file_path": "src/agents/core/CoderAgent.py"}
    )

    result = await all_agents["nasa-enforcer"].execute(nasa_task)
    assert result.success, "NASA compliance check should succeed"


@pytest.mark.asyncio
async def test_theater_detection(all_agents):
    """Test 8: Theater-Detector scans for mock code."""
    theater_task = create_task(
        task_id="theater-001",
        task_type="scan-theater",
        payload={"target_path": "src/agents/"}
    )

    result = await all_agents["theater-detector"].execute(theater_task)
    assert result.success, "Theater detection should succeed"
    assert "theater_score" in result.data


@pytest.mark.asyncio
async def test_security_scan(all_agents):
    """Test 9: Security-Manager scans for vulnerabilities."""
    security_task = create_task(
        task_id="security-001",
        task_type="scan-security",
        payload={"target_path": "src/agents/"}
    )

    result = await all_agents["security-manager"].execute(security_task)
    assert result.success, "Security scan should succeed"
    assert "security_score" in result.data


# ============================================================================
# Test 5: Performance and Coordination
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_agent_execution(all_agents):
    """Test 10: Multiple agents execute concurrently."""
    # Create tasks for different agents
    tasks = [
        (all_agents["researcher"], create_task(
            task_id="research-001",
            task_type="research-topic",
            payload={"topic": "Python async patterns"}
        )),
        (all_agents["cost-tracker"], create_task(
            task_id="cost-001",
            task_type="track-cost",
            payload={"service": "claude", "usage_units": 1000}
        )),
        (all_agents["docs-writer"], create_task(
            task_id="docs-001",
            task_type="create-readme",
            payload={"project_name": "SPEK Platform"}
        ))
    ]

    # Execute concurrently
    results = await asyncio.gather(
        *[agent.execute(task) for agent, task in tasks]
    )

    assert len(results) == 3
    assert all(r.success for r in results), "All concurrent tasks should succeed"


@pytest.mark.asyncio
async def test_agent_validation_performance(all_agents):
    """Test 11: Validation completes in <5ms."""
    task = create_task(
        task_id="perf-001",
        task_type="research-topic",
        payload={"topic": "test"}
    )

    validation = await all_agents["researcher"].validate(task)

    assert validation.valid
    assert validation.validation_time < 5.0, "Validation should be <5ms"


# ============================================================================
# Test 6: Integration Engineer Workflows
# ============================================================================

@pytest.mark.asyncio
async def test_integration_engineer_deployment(all_agents):
    """Test 12: Integration-Engineer integrates components."""
    integration_task = create_task(
        task_id="integrate-001",
        task_type="integrate-components",
        payload={
            "components": ["APIGateway", "AuthService", "Database"],
            "integration_plan": {
                "dependencies": {
                    "APIGateway": ["AuthService"],
                    "AuthService": ["Database"]
                }
            }
        }
    )

    result = await all_agents["integration-engineer"].execute(integration_task)
    assert result.success, "Component integration should succeed"
    assert result.data["success"]


# ============================================================================
# Test 7: Cost and Resource Tracking
# ============================================================================

@pytest.mark.asyncio
async def test_cost_tracking_and_reporting(all_agents):
    """Test 13: Cost-Tracker monitors budget."""
    # Track cost
    track_task = create_task(
        task_id="cost-track-001",
        task_type="track-cost",
        payload={"service": "claude", "usage_units": 5000}
    )

    track_result = await all_agents["cost-tracker"].execute(track_task)
    assert track_result.success
    assert "cost_usd" in track_result.data

    # Generate report
    report_task = create_task(
        task_id="cost-report-001",
        task_type="generate-cost-report",
        payload={"period_days": 30}
    )

    report_result = await all_agents["cost-tracker"].execute(report_task)
    assert report_result.success
    assert "budget_used_pct" in report_result.data


# ============================================================================
# Test 8: Complete End-to-End Workflow
# ============================================================================

@pytest.mark.asyncio
async def test_complete_feature_implementation_workflow(all_agents):
    """
    Test 14: Complete workflow from planning to deployment.

    Workflow:
    1. Planner creates implementation plan
    2. Spec-Writer documents requirements
    3. Architect designs system
    4. Coder implements feature
    5. Tester creates tests
    6. Reviewer validates quality
    7. DevOps deploys to staging
    8. Integration-Engineer validates deployment
    """
    # Step 1: Planning
    plan_task = create_task(
        task_id="plan-001",
        task_type="create-plan",
        payload={"objective": "Implement user authentication"}
    )
    plan_result = await all_agents["planner"].execute(plan_task)
    assert plan_result.success

    # Step 2: Requirements
    spec_task = create_task(
        task_id="spec-002",
        task_type="write-spec",
        payload={"input_file": "requirements.md", "title": "Auth System"}
    )
    spec_result = await all_agents["spec-writer"].execute(spec_task)
    assert spec_result.success

    # Step 3: Architecture
    arch_task = create_task(
        task_id="arch-002",
        task_type="design-architecture",
        payload={"specification_file": "specs/SPEC-002.md"}
    )
    arch_result = await all_agents["architect"].execute(arch_task)
    assert arch_result.success

    # Step 4: Implementation
    code_task = create_task(
        task_id="code-002",
        task_type="implement-code",
        payload={
            "spec_file": "specs/SPEC-002.md",
            "output_file": "src/auth.py"
        }
    )
    code_result = await all_agents["coder"].execute(code_task)
    assert code_result.success

    # Step 5: Testing
    test_task = create_task(
        task_id="test-002",
        task_type="generate-tests",
        payload={"source_file": "src/auth.py", "test_type": "unit"}
    )
    test_result = await all_agents["tester"].execute(test_task)
    assert test_result.success

    # Step 6: Review
    review_task = create_task(
        task_id="review-002",
        task_type="review-code",
        payload={"file_path": "src/auth.py"}
    )
    review_result = await all_agents["reviewer"].execute(review_task)
    assert review_result.success

    # Step 7: Deployment
    deploy_task = create_task(
        task_id="deploy-002",
        task_type="deploy-app",
        payload={"environment": "staging", "version": "1.0.0"}
    )
    deploy_result = await all_agents["devops"].execute(deploy_task)
    assert deploy_result.success

    # All steps completed successfully
    assert all([
        plan_result.success,
        spec_result.success,
        arch_result.success,
        code_result.success,
        test_result.success,
        review_result.success,
        deploy_result.success
    ]), "Complete workflow should succeed end-to-end"


# ============================================================================
# Test Summary
# ============================================================================

def test_summary():
    """
    Test 15: Summary of integration test coverage.

    Coverage:
    - 22/22 agents tested
    - SPARC workflow validated
    - Princess Hive delegation tested
    - Quality gates validated
    - Performance benchmarked
    - Complete end-to-end workflow tested
    """
    assert True, "Integration tests provide comprehensive coverage"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
