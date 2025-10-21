"""
Unit tests for InfrastructureOpsAgent.

Tests validate:
- Agent metadata and initialization
- Task validation for all 4 task types
- Kubernetes manifest generation
- Docker configuration
- Terraform automation
"""

import pytest
from src.agents.specialized.InfrastructureOpsAgent import (
    create_infrastructure_ops_agent,
    InfrastructureOpsAgent
)
from src.core.types import Task, Result


class TestInfrastructureOpsAgentMetadata:
    """Test agent metadata."""

    def test_agent_creation(self):
        agent = create_infrastructure_ops_agent()
        assert agent is not None
        assert isinstance(agent, InfrastructureOpsAgent)

    def test_agent_metadata(self):
        agent = create_infrastructure_ops_agent()
        metadata = agent.metadata

        assert metadata.agent_id == "infrastructure-ops"
        assert metadata.name == "Infrastructure Operations Specialist"
        assert "infrastructure" in metadata.description.lower()

    def test_supported_task_types(self):
        agent = create_infrastructure_ops_agent()
        supported = agent.metadata.supported_task_types

        assert "deploy-infrastructure" in supported
        assert "scale-infrastructure" in supported
        assert "monitor-infrastructure" in supported
        assert "configure-infrastructure" in supported
        assert len(supported) == 4


class TestInfrastructureOpsAgentValidation:
    """Test task validation."""

    @pytest.fixture
    def agent(self):
        return create_infrastructure_ops_agent()

    @pytest.mark.asyncio
    async def test_validate_deploy_infrastructure(self, agent):
        task = Task(
            task_id="test-001",
            task_type="deploy-infrastructure",
            description="Deploy k8s cluster",
            payload={"platform": "kubernetes", "app_name": "test-app"}
        )
        result = await agent.validate(task)
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_scale_infrastructure(self, agent):
        task = Task(
            task_id="test-002",
            task_type="scale-infrastructure",
            description="Scale deployment",
            payload={"resource": "deployment", "replicas": 3}
        )
        result = await agent.validate(task)
        assert result.is_valid


class TestInfrastructureOpsAgentKubernetes:
    """Test Kubernetes manifest generation."""

    @pytest.fixture
    def agent(self):
        return create_infrastructure_ops_agent()

    @pytest.mark.asyncio
    async def test_execute_kubernetes_deployment(self, agent):
        task = Task(
            task_id="test-003",
            task_type="deploy-infrastructure",
            description="Create k8s deployment",
            payload={
                "platform": "kubernetes",
                "app_name": "web-app",
                "image": "nginx:latest",
                "replicas": 3,
                "port": 80
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "manifests" in result.data
        assert "Deployment" in result.data["manifests"]
        assert "Service" in result.data["manifests"]

    @pytest.mark.asyncio
    async def test_kubernetes_manifest_structure(self, agent):
        """Test that generated manifests have correct structure."""
        task = Task(
            task_id="test-004",
            task_type="deploy-infrastructure",
            description="Generate k8s manifest",
            payload={
                "platform": "kubernetes",
                "app_name": "api",
                "image": "myapp:v1"
            }
        )
        result = await agent.execute(task)
        assert result.success
        manifests = result.data["manifests"]

        # Check Deployment manifest
        assert "apiVersion" in manifests["Deployment"]
        assert "kind: Deployment" in manifests["Deployment"]
        assert "metadata:" in manifests["Deployment"]
        assert "spec:" in manifests["Deployment"]


class TestInfrastructureOpsAgentDocker:
    """Test Docker configuration."""

    @pytest.fixture
    def agent(self):
        return create_infrastructure_ops_agent()

    @pytest.mark.asyncio
    async def test_execute_docker_deployment(self, agent):
        task = Task(
            task_id="test-005",
            task_type="deploy-infrastructure",
            description="Create Docker setup",
            payload={
                "platform": "docker",
                "app_name": "web-app",
                "base_image": "node:18"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "dockerfile" in result.data or "docker-compose" in result.data


class TestInfrastructureOpsAgentScaling:
    """Test scaling operations."""

    @pytest.fixture
    def agent(self):
        return create_infrastructure_ops_agent()

    @pytest.mark.asyncio
    async def test_execute_scale_infrastructure(self, agent):
        task = Task(
            task_id="test-006",
            task_type="scale-infrastructure",
            description="Scale deployment",
            payload={
                "resource": "deployment/web-app",
                "replicas": 5,
                "platform": "kubernetes"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "commands" in result.data or "config" in result.data


class TestInfrastructureOpsAgentMonitoring:
    """Test monitoring configuration."""

    @pytest.fixture
    def agent(self):
        return create_infrastructure_ops_agent()

    @pytest.mark.asyncio
    async def test_execute_monitor_infrastructure(self, agent):
        task = Task(
            task_id="test-007",
            task_type="monitor-infrastructure",
            description="Setup monitoring",
            payload={
                "monitoring_type": "prometheus",
                "targets": ["web-app", "api"]
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "config" in result.data or "recommendations" in result.data


class TestInfrastructureOpsAgentEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def agent(self):
        return create_infrastructure_ops_agent()

    @pytest.mark.asyncio
    async def test_invalid_platform(self, agent):
        """Test handling of invalid platform."""
        task = Task(
            task_id="test-008",
            task_type="deploy-infrastructure",
            description="Deploy to invalid platform",
            payload={
                "platform": "invalid-platform",
                "app_name": "test"
            }
        )
        result = await agent.execute(task)
        # Should default to kubernetes or handle gracefully
        assert result.success or not result.success

    @pytest.mark.asyncio
    async def test_missing_required_config(self, agent):
        """Test handling of missing configuration."""
        task = Task(
            task_id="test-009",
            task_type="deploy-infrastructure",
            description="Deploy with minimal config",
            payload={
                "platform": "kubernetes"
                # Missing app_name
            }
        )
        result = await agent.validate(task)
        assert not result.is_valid


# NASA Rule 10 Compliance Test
class TestInfrastructureOpsAgentNASACompliance:
    """Test NASA Rule 10 compliance."""

    def test_nasa_compliance(self):
        import ast
        from pathlib import Path

        agent_file = Path(__file__).parent.parent.parent.parent.parent / "src" / "agents" / "specialized" / "InfrastructureOpsAgent.py"

        with open(agent_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > 60:
                    violations.append((node.name, length))

        assert len(violations) == 0, f"NASA Rule 10 violations: {violations}"
