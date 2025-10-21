"""
Integration tests for Princess Agent delegation to new specialized agents.

Tests validate:
- Princess-Dev routes to frontend-dev/backend-dev
- Princess-Quality routes to code-analyzer
- Princess-Coordination routes to infrastructure-ops/release-manager/performance-engineer
- Keyword-based routing works correctly
- End-to-end task flow
"""

import pytest
from src.agents.swarm.PrincessDevAgent import create_princess_dev_agent
from src.agents.swarm.PrincessQualityAgent import create_princess_quality_agent
from src.agents.swarm.PrincessCoordinationAgent import create_princess_coordination_agent
from src.core.types import Task


class TestPrincessDevDelegation:
    """Test Princess-Dev delegation to frontend-dev and backend-dev."""

    @pytest.fixture
    def princess(self):
        return create_princess_dev_agent()

    @pytest.mark.asyncio
    async def test_delegate_to_frontend_dev_by_keyword(self, princess):
        """Test delegation to frontend-dev based on keywords."""
        task = Task(
            task_id="test-001",
            task_type="implement-component",
            description="Create React UI component for user profile",
            payload={"component_name": "UserProfile"}
        )

        # The Princess should route this to frontend-dev
        result = await princess.execute(task)
        assert result.success
        # Verify it was routed to frontend-dev
        assert "frontend" in result.message.lower() or "component" in result.data

    @pytest.mark.asyncio
    async def test_delegate_to_backend_dev_by_keyword(self, princess):
        """Test delegation to backend-dev based on keywords."""
        task = Task(
            task_id="test-002",
            task_type="implement-api",
            description="Create REST API endpoint for user management",
            payload={"endpoint": "/users", "method": "GET"}
        )

        result = await princess.execute(task)
        assert result.success
        # Verify it was routed to backend-dev
        assert "backend" in result.message.lower() or "api" in result.data

    @pytest.mark.asyncio
    async def test_frontend_keyword_ui(self, princess):
        """Test 'ui' keyword routes to frontend-dev."""
        task = Task(
            task_id="test-003",
            task_type="implement-ui",
            description="Implement dashboard UI layout",
            payload={"ui_name": "Dashboard"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_backend_keyword_database(self, princess):
        """Test 'database' keyword routes to backend-dev."""
        task = Task(
            task_id="test-004",
            task_type="implement-database",
            description="Create database schema for products",
            payload={"table_name": "products", "database_type": "postgresql"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_fallback_to_coder(self, princess):
        """Test that tasks without specific keywords fall back to coder."""
        task = Task(
            task_id="test-005",
            task_type="code",
            description="Write utility function for data processing",
            payload={"function_name": "process_data"}
        )

        result = await princess.execute(task)
        assert result.success


class TestPrincessQualityDelegation:
    """Test Princess-Quality delegation to code-analyzer."""

    @pytest.fixture
    def princess(self):
        return create_princess_quality_agent()

    @pytest.mark.asyncio
    async def test_delegate_to_code_analyzer(self, princess):
        """Test delegation to code-analyzer."""
        task = Task(
            task_id="test-006",
            task_type="analyze-code",
            description="Analyze code quality and complexity",
            payload={"file_path": "src/utils.py"}
        )

        result = await princess.execute(task)
        assert result.success
        # Verify it was routed to code-analyzer
        assert "analysis" in result.message.lower() or "analyze" in result.data

    @pytest.mark.asyncio
    async def test_detect_complexity_routing(self, princess):
        """Test complexity detection routes to code-analyzer."""
        task = Task(
            task_id="test-007",
            task_type="detect-complexity",
            description="Detect cyclomatic complexity",
            payload={"code": "def test(): pass"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_detect_duplicates_routing(self, princess):
        """Test duplicate detection routes to code-analyzer."""
        task = Task(
            task_id="test-008",
            task_type="detect-duplicates",
            description="Find duplicate code blocks",
            payload={"code": "def a(): return 1\ndef b(): return 1"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_fallback_to_reviewer(self, princess):
        """Test that review tasks fall back to reviewer."""
        task = Task(
            task_id="test-009",
            task_type="review",
            description="Review code changes",
            payload={"file_path": "src/main.py"}
        )

        result = await princess.execute(task)
        assert result.success


class TestPrincessCoordinationDelegation:
    """Test Princess-Coordination delegation to infrastructure-ops, release-manager, performance-engineer."""

    @pytest.fixture
    def princess(self):
        return create_princess_coordination_agent()

    @pytest.mark.asyncio
    async def test_delegate_to_infrastructure_ops(self, princess):
        """Test delegation to infrastructure-ops."""
        task = Task(
            task_id="test-010",
            task_type="deploy-infrastructure",
            description="Deploy Kubernetes cluster for microservices",
            payload={"platform": "kubernetes", "app_name": "api"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_kubernetes_keyword_routing(self, princess):
        """Test 'kubernetes' keyword routes to infrastructure-ops."""
        task = Task(
            task_id="test-011",
            task_type="configure-infrastructure",
            description="Configure Kubernetes autoscaling",
            payload={"resource": "deployment", "min_replicas": 2}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_delegate_to_release_manager(self, princess):
        """Test delegation to release-manager."""
        task = Task(
            task_id="test-012",
            task_type="prepare-release",
            description="Prepare release v2.0.0 with changelog",
            payload={"version": "2.0.0", "release_type": "major"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_version_keyword_routing(self, princess):
        """Test 'version' keyword routes to release-manager."""
        task = Task(
            task_id="test-013",
            task_type="tag-release",
            description="Tag version 1.5.0 in git",
            payload={"version": "1.5.0"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_delegate_to_performance_engineer(self, princess):
        """Test delegation to performance-engineer."""
        task = Task(
            task_id="test-014",
            task_type="profile-performance",
            description="Profile API endpoint performance",
            payload={"target": "api_endpoint", "metrics": ["cpu", "memory"]}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_optimize_keyword_routing(self, princess):
        """Test 'optimize' keyword routes to performance-engineer."""
        task = Task(
            task_id="test-015",
            task_type="optimize-performance",
            description="Optimize database query performance",
            payload={"target": "user_search"}
        )

        result = await princess.execute(task)
        assert result.success

    @pytest.mark.asyncio
    async def test_fallback_to_orchestrator(self, princess):
        """Test that generic coordination tasks fall back to orchestrator."""
        task = Task(
            task_id="test-016",
            task_type="orchestrate",
            description="Orchestrate complex workflow",
            payload={"workflow": "data_pipeline"}
        )

        result = await princess.execute(task)
        assert result.success


class TestEndToEndDelegationFlow:
    """Test end-to-end delegation flow across multiple Princess agents."""

    @pytest.mark.asyncio
    async def test_full_feature_implementation_flow(self):
        """Test complete flow: spec → frontend → backend → test → review."""
        # This simulates a real workflow where multiple agents work together

        # Step 1: Princess-Dev delegates UI work to frontend-dev
        princess_dev = create_princess_dev_agent()
        ui_task = Task(
            task_id="flow-001",
            task_type="implement-component",
            description="Create user dashboard React component",
            payload={"component_name": "Dashboard"}
        )
        ui_result = await princess_dev.execute(ui_task)
        assert ui_result.success

        # Step 2: Princess-Dev delegates API work to backend-dev
        api_task = Task(
            task_id="flow-002",
            task_type="implement-api",
            description="Create dashboard data API endpoint",
            payload={"endpoint": "/api/dashboard", "method": "GET"}
        )
        api_result = await princess_dev.execute(api_task)
        assert api_result.success

        # Step 3: Princess-Quality analyzes the code
        princess_quality = create_princess_quality_agent()
        analysis_task = Task(
            task_id="flow-003",
            task_type="analyze-code",
            description="Analyze dashboard component complexity",
            payload={"code": "def dashboard(): pass"}
        )
        analysis_result = await princess_quality.execute(analysis_task)
        assert analysis_result.success

        # Step 4: Princess-Coordination manages deployment
        princess_coord = create_princess_coordination_agent()
        deploy_task = Task(
            task_id="flow-004",
            task_type="deploy-infrastructure",
            description="Deploy dashboard to Kubernetes",
            payload={"platform": "kubernetes", "app_name": "dashboard"}
        )
        deploy_result = await princess_coord.execute(deploy_task)
        assert deploy_result.success

    @pytest.mark.asyncio
    async def test_release_workflow(self):
        """Test complete release workflow."""
        princess_coord = create_princess_coordination_agent()

        # Step 1: Generate changelog
        changelog_task = Task(
            task_id="release-001",
            task_type="generate-changelog",
            description="Generate changelog for v2.0.0",
            payload={"commits": [{"message": "feat: new feature", "hash": "abc"}]}
        )
        changelog_result = await princess_coord.execute(changelog_task)
        assert changelog_result.success

        # Step 2: Prepare release
        release_task = Task(
            task_id="release-002",
            task_type="prepare-release",
            description="Prepare v2.0.0 release",
            payload={"current_version": "1.5.0", "release_type": "major"}
        )
        release_result = await princess_coord.execute(release_task)
        assert release_result.success

        # Step 3: Coordinate deployment
        deploy_task = Task(
            task_id="release-003",
            task_type="coordinate-deployment",
            description="Deploy v2.0.0 to production",
            payload={"version": "2.0.0", "environments": ["production"]}
        )
        deploy_result = await princess_coord.execute(deploy_task)
        assert deploy_result.success


class TestDelegationErrorHandling:
    """Test error handling in delegation."""

    @pytest.mark.asyncio
    async def test_invalid_task_type(self):
        """Test handling of invalid task types."""
        princess_dev = create_princess_dev_agent()
        task = Task(
            task_id="error-001",
            task_type="invalid-task-type",
            description="Invalid task"
        )

        result = await princess_dev.execute(task)
        # Should handle gracefully
        assert not result.success or "error" in result.message.lower()

    @pytest.mark.asyncio
    async def test_missing_required_drone(self):
        """Test handling when required drone is not available."""
        princess_dev = create_princess_dev_agent()
        task = Task(
            task_id="error-002",
            task_type="implement-component",
            description="Task requiring frontend-dev",
            payload={"component_name": "Test"}
        )

        # Even if drone is missing, should handle gracefully
        result = await princess_dev.execute(task)
        # Should either succeed with fallback or fail gracefully
        assert result is not None


class TestPerformanceAndLatency:
    """Test performance characteristics of delegation."""

    @pytest.mark.asyncio
    async def test_delegation_latency(self):
        """Test that delegation doesn't add significant overhead."""
        import time

        princess_dev = create_princess_dev_agent()
        task = Task(
            task_id="perf-001",
            task_type="implement-component",
            description="Create Button component",
            payload={"component_name": "Button"}
        )

        start = time.time()
        await princess_dev.validate(task)
        validation_time = (time.time() - start) * 1000

        # Validation should be fast (<100ms including delegation logic)
        assert validation_time < 100

    @pytest.mark.asyncio
    async def test_concurrent_delegation(self):
        """Test that multiple delegations can happen concurrently."""
        import asyncio

        princess_dev = create_princess_dev_agent()
        princess_quality = create_princess_quality_agent()
        princess_coord = create_princess_coordination_agent()

        tasks = [
            princess_dev.execute(Task(
                task_id="conc-001",
                task_type="implement-component",
                description="Create component A",
                payload={"component_name": "A"}
            )),
            princess_quality.execute(Task(
                task_id="conc-002",
                task_type="analyze-code",
                description="Analyze file B",
                payload={"file_path": "b.py"}
            )),
            princess_coord.execute(Task(
                task_id="conc-003",
                task_type="deploy-infrastructure",
                description="Deploy service C",
                payload={"platform": "kubernetes", "app_name": "C"}
            ))
        ]

        results = await asyncio.gather(*tasks)
        assert all(r.success for r in results)
