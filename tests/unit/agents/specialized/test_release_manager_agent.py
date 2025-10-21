"""
Unit tests for ReleaseManagerAgent.

Tests validate:
- Agent metadata and initialization
- Task validation for all 4 task types
- Semantic versioning
- Changelog generation
- Git tag management
"""

import pytest
from src.agents.specialized.ReleaseManagerAgent import (
    create_release_manager_agent,
    ReleaseManagerAgent
)
from src.core.types import Task, Result


class TestReleaseManagerAgentMetadata:
    """Test agent metadata."""

    def test_agent_creation(self):
        agent = create_release_manager_agent()
        assert agent is not None
        assert isinstance(agent, ReleaseManagerAgent)

    def test_agent_metadata(self):
        agent = create_release_manager_agent()
        metadata = agent.metadata

        assert metadata.agent_id == "release-manager"
        assert metadata.name == "Release Management Specialist"
        assert "release" in metadata.description.lower()

    def test_supported_task_types(self):
        agent = create_release_manager_agent()
        supported = agent.metadata.supported_task_types

        assert "prepare-release" in supported
        assert "generate-changelog" in supported
        assert "tag-release" in supported
        assert "coordinate-deployment" in supported
        assert len(supported) == 4


class TestReleaseManagerAgentValidation:
    """Test task validation."""

    @pytest.fixture
    def agent(self):
        return create_release_manager_agent()

    @pytest.mark.asyncio
    async def test_validate_prepare_release(self, agent):
        task = Task(
            task_id="test-001",
            task_type="prepare-release",
            description="Prepare v1.2.0 release",
            payload={"version": "1.2.0", "release_type": "minor"}
        )
        result = await agent.validate(task)
        assert result.is_valid

    @pytest.mark.asyncio
    async def test_validate_generate_changelog(self, agent):
        task = Task(
            task_id="test-002",
            task_type="generate-changelog",
            description="Generate changelog",
            payload={"from_version": "1.0.0", "to_version": "1.1.0"}
        )
        result = await agent.validate(task)
        assert result.is_valid


class TestReleaseManagerAgentVersioning:
    """Test semantic versioning."""

    @pytest.fixture
    def agent(self):
        return create_release_manager_agent()

    @pytest.mark.asyncio
    async def test_execute_prepare_major_release(self, agent):
        task = Task(
            task_id="test-003",
            task_type="prepare-release",
            description="Prepare major release",
            payload={
                "current_version": "1.5.3",
                "release_type": "major"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "new_version" in result.data
        assert result.data["new_version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_execute_prepare_minor_release(self, agent):
        task = Task(
            task_id="test-004",
            task_type="prepare-release",
            description="Prepare minor release",
            payload={
                "current_version": "1.5.3",
                "release_type": "minor"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert result.data["new_version"] == "1.6.0"

    @pytest.mark.asyncio
    async def test_execute_prepare_patch_release(self, agent):
        task = Task(
            task_id="test-005",
            task_type="prepare-release",
            description="Prepare patch release",
            payload={
                "current_version": "1.5.3",
                "release_type": "patch"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert result.data["new_version"] == "1.5.4"


class TestReleaseManagerAgentChangelog:
    """Test changelog generation."""

    @pytest.fixture
    def agent(self):
        return create_release_manager_agent()

    @pytest.mark.asyncio
    async def test_execute_generate_changelog(self, agent):
        task = Task(
            task_id="test-006",
            task_type="generate-changelog",
            description="Generate changelog from commits",
            payload={
                "commits": [
                    {"message": "feat: add new feature", "hash": "abc123"},
                    {"message": "fix: resolve bug", "hash": "def456"},
                    {"message": "docs: update README", "hash": "ghi789"}
                ]
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "changelog" in result.data

        changelog = result.data["changelog"]
        assert "Features" in changelog
        assert "Bug Fixes" in changelog
        assert "Documentation" in changelog

    @pytest.mark.asyncio
    async def test_changelog_conventional_commits(self, agent):
        """Test that changelog correctly categorizes conventional commits."""
        task = Task(
            task_id="test-007",
            task_type="generate-changelog",
            description="Categorize commits",
            payload={
                "commits": [
                    {"message": "feat: new API endpoint", "hash": "001"},
                    {"message": "fix: memory leak", "hash": "002"},
                    {"message": "refactor: cleanup code", "hash": "003"},
                    {"message": "perf: optimize query", "hash": "004"},
                    {"message": "test: add unit tests", "hash": "005"}
                ]
            }
        )
        result = await agent.execute(task)
        assert result.success
        changelog = result.data["changelog"]

        # Should have multiple categories
        assert "feat" in changelog.lower() or "feature" in changelog.lower()
        assert "fix" in changelog.lower()


class TestReleaseManagerAgentGitOperations:
    """Test Git tag operations."""

    @pytest.fixture
    def agent(self):
        return create_release_manager_agent()

    @pytest.mark.asyncio
    async def test_execute_tag_release(self, agent):
        task = Task(
            task_id="test-008",
            task_type="tag-release",
            description="Create git tag",
            payload={
                "version": "1.2.0",
                "message": "Release version 1.2.0"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "tag_command" in result.data or "commands" in result.data


class TestReleaseManagerAgentDeploymentCoordination:
    """Test deployment coordination."""

    @pytest.fixture
    def agent(self):
        return create_release_manager_agent()

    @pytest.mark.asyncio
    async def test_execute_coordinate_deployment(self, agent):
        task = Task(
            task_id="test-009",
            task_type="coordinate-deployment",
            description="Coordinate deployment",
            payload={
                "version": "1.2.0",
                "environments": ["staging", "production"],
                "strategy": "rolling"
            }
        )
        result = await agent.execute(task)
        assert result.success
        assert "deployment_plan" in result.data or "steps" in result.data


class TestReleaseManagerAgentEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def agent(self):
        return create_release_manager_agent()

    @pytest.mark.asyncio
    async def test_invalid_version_format(self, agent):
        """Test handling of invalid version format."""
        task = Task(
            task_id="test-010",
            task_type="prepare-release",
            description="Invalid version",
            payload={
                "current_version": "invalid",
                "release_type": "minor"
            }
        )
        result = await agent.execute(task)
        # Should handle gracefully
        assert not result.success or "error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_empty_commits_list(self, agent):
        """Test changelog generation with no commits."""
        task = Task(
            task_id="test-011",
            task_type="generate-changelog",
            description="No commits",
            payload={"commits": []}
        )
        result = await agent.execute(task)
        assert result.success
        assert result.data["changelog"] == "No changes"


# NASA Rule 10 Compliance Test
class TestReleaseManagerAgentNASACompliance:
    """Test NASA Rule 10 compliance."""

    def test_nasa_compliance(self):
        import ast
        from pathlib import Path

        agent_file = Path(__file__).parent.parent.parent.parent.parent / "src" / "agents" / "specialized" / "ReleaseManagerAgent.py"

        with open(agent_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > 60:
                    violations.append((node.name, length))

        assert len(violations) == 0, f"NASA Rule 10 violations: {violations}"
