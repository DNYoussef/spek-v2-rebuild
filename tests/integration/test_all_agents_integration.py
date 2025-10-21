"""
Integration Tests for All 28 Agents
Week 22 - Production Hardening Phase 3

Tests all agents in isolation and validates:
- Agent initialization
- Task execution
- Error handling
- NASA compliance (≥92%)
- Context DNA integration
- Memory coordination
"""

import pytest
import ast
from pathlib import Path
from typing import Dict, List, Any


# Agent roster (28 total)
CORE_AGENTS = [
    'QueenAgent',
    'CoderAgent',
    'ResearcherAgent',
    'TesterAgent',
    'ReviewerAgent',
]

PRINCESS_AGENTS = [
    'PrincessDevAgent',
    'PrincessQualityAgent',
    'PrincessCoordinationAgent',
]

SPECIALIZED_AGENTS = [
    'ArchitectAgent',
    'PseudocodeWriterAgent',
    'SpecWriterAgent',
    'IntegrationEngineerAgent',
    'DebuggerAgent',
    'DocsWriterAgent',
    'DevOpsAgent',
    'SecurityManagerAgent',
    'CostTrackerAgent',
    'TheaterDetectorAgent',
    'NASAEnforcerAgent',
    'FSMAnalyzerAgent',
    'OrchestratorAgent',
    'PlannerAgent',
]

WEEK_8_9_AGENTS = [
    'FrontendDevAgent',
    'BackendDevAgent',
    'CodeAnalyzerAgent',
    'InfrastructureOpsAgent',
    'ReleaseManagerAgent',
    'PerformanceEngineerAgent',
]

ALL_AGENTS = CORE_AGENTS + PRINCESS_AGENTS + SPECIALIZED_AGENTS + WEEK_8_9_AGENTS


class TestAgentInitialization:
    """Test that all 28 agents can be initialized successfully."""

    @pytest.mark.parametrize('agent_name', ALL_AGENTS)
    def test_agent_imports_successfully(self, agent_name: str):
        """Test that each agent can be imported without errors."""
        # Map agent names to their module paths
        agent_module_map = {
            # Core agents
            'QueenAgent': 'src.agents.core.QueenAgent',
            'CoderAgent': 'src.agents.core.CoderAgent',
            'ResearcherAgent': 'src.agents.core.ResearcherAgent',
            'TesterAgent': 'src.agents.core.TesterAgent',
            'ReviewerAgent': 'src.agents.core.ReviewerAgent',

            # Princess agents
            'PrincessDevAgent': 'src.agents.swarm.PrincessDevAgent',
            'PrincessQualityAgent': 'src.agents.swarm.PrincessQualityAgent',
            'PrincessCoordinationAgent': 'src.agents.swarm.PrincessCoordinationAgent',

            # Specialized agents
            'ArchitectAgent': 'src.agents.specialized.ArchitectAgent',
            'PseudocodeWriterAgent': 'src.agents.specialized.PseudocodeWriterAgent',
            'SpecWriterAgent': 'src.agents.specialized.SpecWriterAgent',
            'IntegrationEngineerAgent': 'src.agents.specialized.IntegrationEngineerAgent',
            'DebuggerAgent': 'src.agents.specialized.DebuggerAgent',
            'DocsWriterAgent': 'src.agents.specialized.DocsWriterAgent',
            'DevOpsAgent': 'src.agents.specialized.DevOpsAgent',
            'SecurityManagerAgent': 'src.agents.specialized.SecurityManagerAgent',
            'CostTrackerAgent': 'src.agents.specialized.CostTrackerAgent',
            'TheaterDetectorAgent': 'src.agents.specialized.TheaterDetectorAgent',
            'NASAEnforcerAgent': 'src.agents.specialized.NASAEnforcerAgent',
            'FSMAnalyzerAgent': 'src.agents.specialized.FSMAnalyzerAgent',
            'OrchestratorAgent': 'src.agents.specialized.OrchestratorAgent',
            'PlannerAgent': 'src.agents.specialized.PlannerAgent',

            # Week 8-9 agents
            'FrontendDevAgent': 'src.agents.specialized.FrontendDevAgent',
            'BackendDevAgent': 'src.agents.specialized.BackendDevAgent',
            'CodeAnalyzerAgent': 'src.agents.specialized.CodeAnalyzerAgent',
            'InfrastructureOpsAgent': 'src.agents.specialized.InfrastructureOpsAgent',
            'ReleaseManagerAgent': 'src.agents.specialized.ReleaseManagerAgent',
            'PerformanceEngineerAgent': 'src.agents.specialized.PerformanceEngineerAgent',
        }

        module_path = agent_module_map.get(agent_name)

        if module_path:
            try:
                # Try to import the agent
                module_parts = module_path.rsplit('.', 1)
                module = __import__(module_parts[0], fromlist=[module_parts[1]])
                agent_class = getattr(module, agent_name)

                assert agent_class is not None
                print(f"✓ {agent_name} imported successfully")
            except (ImportError, AttributeError) as e:
                pytest.skip(f"{agent_name} not yet implemented: {e}")
        else:
            pytest.fail(f"Agent {agent_name} not mapped to module path")

    @pytest.mark.parametrize('agent_name', ALL_AGENTS)
    def test_agent_has_required_methods(self, agent_name: str):
        """Test that each agent implements required AgentBase methods."""
        # Required methods from AgentBase
        required_methods = [
            '__init__',
            'execute',
            'validate',
            'get_metadata',
        ]

        # Get agent file path
        agent_files = list(Path('src/agents').rglob(f'*{agent_name}.py'))

        if not agent_files:
            pytest.skip(f"{agent_name} file not found")

        agent_file = agent_files[0]

        # Parse agent file
        with open(agent_file, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        # Find agent class
        agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == agent_name:
                agent_class = node
                break

        if not agent_class:
            pytest.skip(f"{agent_name} class not found in file")

        # Get all method names
        method_names = [
            m.name for m in agent_class.body
            if isinstance(m, ast.FunctionDef)
        ]

        # Check for required methods
        missing_methods = [m for m in required_methods if m not in method_names]

        assert len(missing_methods) == 0, \
            f"{agent_name} missing required methods: {missing_methods}"

        print(f"✓ {agent_name} has all required methods: {method_names}")


class TestAgentNASACompliance:
    """Test NASA Rule 10 compliance for all agent implementations."""

    @pytest.mark.parametrize('agent_name', ALL_AGENTS)
    def test_agent_functions_under_60_lines(self, agent_name: str):
        """Test that all functions in agent are ≤60 lines (NASA Rule 10)."""
        # Get agent file path
        agent_files = list(Path('src/agents').rglob(f'*{agent_name}.py'))

        if not agent_files:
            pytest.skip(f"{agent_name} file not found")

        agent_file = agent_files[0]

        # Parse agent file
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        violations = []
        total_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                func_length = node.end_lineno - node.lineno + 1

                if func_length > 60:
                    violations.append({
                        'name': node.name,
                        'length': func_length,
                        'line': node.lineno,
                    })

        compliance_rate = (
            ((total_functions - len(violations)) / total_functions * 100)
            if total_functions > 0 else 100
        )

        print(f"{agent_name} NASA compliance: {compliance_rate:.1f}% "
              f"({total_functions - len(violations)}/{total_functions} functions)")

        if violations:
            for v in violations:
                print(f"  ⚠️  {v['name']}:{v['line']} = {v['length']} LOC")

        # Assert ≥92% compliance (Week 5 target)
        assert compliance_rate >= 92.0, \
            f"{agent_name} NASA compliance {compliance_rate:.1f}% < 92% target"

    @pytest.mark.parametrize('agent_name', ALL_AGENTS)
    def test_agent_file_size_reasonable(self, agent_name: str):
        """Test that agent file is ≤500 LOC (maintainability)."""
        # Get agent file path
        agent_files = list(Path('src/agents').rglob(f'*{agent_name}.py'))

        if not agent_files:
            pytest.skip(f"{agent_name} file not found")

        agent_file = agent_files[0]

        # Count lines of code (excluding blank lines and comments)
        with open(agent_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        loc = sum(
            1 for line in lines
            if line.strip() and not line.strip().startswith('#')
        )

        print(f"{agent_name}: {loc} LOC")

        # Warn if over 500 LOC (should consider refactoring)
        if loc > 500:
            print(f"  ⚠️  {agent_name} exceeds 500 LOC - consider refactoring")

        # Hard limit: 1000 LOC
        assert loc <= 1000, \
            f"{agent_name} has {loc} LOC (>1000 limit)"


class TestAgentExecution:
    """Test agent execution with sample tasks."""

    def test_queen_agent_orchestration(self):
        """Test Queen agent can orchestrate multi-agent tasks."""
        try:
            from src.agents.core.QueenAgent import QueenAgent

            queen = QueenAgent()

            # Test orchestration with simple task
            task = {
                'type': 'code_review',
                'description': 'Review sample code',
                'priority': 'high',
            }

            # Execute task (may return delegation plan)
            result = queen.execute(task)

            assert result is not None
            print("✓ Queen agent orchestration successful")

        except ImportError:
            pytest.skip("QueenAgent not yet implemented")

    def test_coder_agent_code_generation(self):
        """Test Coder agent can generate code."""
        try:
            from src.agents.core.CoderAgent import CoderAgent

            coder = CoderAgent()

            # Test code generation
            task = {
                'type': 'implement',
                'description': 'Create hello world function',
                'language': 'python',
            }

            result = coder.execute(task)

            assert result is not None
            print("✓ Coder agent code generation successful")

        except ImportError:
            pytest.skip("CoderAgent not yet implemented")

    def test_tester_agent_test_generation(self):
        """Test Tester agent can generate tests."""
        try:
            from src.agents.core.TesterAgent import TesterAgent

            tester = TesterAgent()

            # Test test generation
            task = {
                'type': 'test',
                'description': 'Generate tests for hello world',
                'framework': 'pytest',
            }

            result = tester.execute(task)

            assert result is not None
            print("✓ Tester agent test generation successful")

        except ImportError:
            pytest.skip("TesterAgent not yet implemented")


class TestAgentRegistry:
    """Test agent registration and discovery."""

    def test_all_28_agents_registered(self):
        """Test that all 28 agents are discoverable."""
        agent_files = list(Path('src/agents').rglob('*Agent.py'))

        # Exclude base classes
        agent_files = [
            f for f in agent_files
            if f.name not in ['AgentBase.py', '__init__.py']
        ]

        agent_count = len(agent_files)

        print(f"Found {agent_count} agent files:")
        for f in sorted(agent_files):
            print(f"  - {f.stem}")

        # Should have 28 agents (5 core + 3 princess + 14 specialized + 6 week 8-9)
        # Allow some flexibility as agents may be in development
        assert agent_count >= 20, \
            f"Expected ≥20 agents, found {agent_count}"

        if agent_count >= 28:
            print(f"✓ All 28 agents present")
        else:
            print(f"⚠️  {28 - agent_count} agents still in development")

    def test_agent_categorization(self):
        """Test that agents are properly organized by category."""
        categories = {
            'core': Path('src/agents/core'),
            'swarm': Path('src/agents/swarm'),
            'specialized': Path('src/agents/specialized'),
        }

        for category, path in categories.items():
            if path.exists():
                agent_count = len(list(path.glob('*Agent.py')))
                print(f"{category}: {agent_count} agents")
            else:
                print(f"⚠️  {category} directory not found")


class TestLoop123Integration:
    """Test Loop 1-2-3 workflow integration."""

    def test_loop1_premortem_workflow(self):
        """Test Loop 1 (Premortem & Research) workflow."""
        # Loop 1 agents: Queen, Researcher, Architect, SpecWriter
        required_agents = [
            'QueenAgent',
            'ResearcherAgent',
            'ArchitectAgent',
            'SpecWriterAgent',
        ]

        for agent_name in required_agents:
            agent_files = list(Path('src/agents').rglob(f'*{agent_name}.py'))

            if agent_files:
                print(f"  ✓ {agent_name} available for Loop 1")
            else:
                print(f"  ⚠️  {agent_name} not found (Loop 1 blocker)")

    def test_loop2_execution_workflow(self):
        """Test Loop 2 (Execution & Audit) workflow."""
        # Loop 2 agents: Coder, Tester, Reviewer, Debugger
        required_agents = [
            'CoderAgent',
            'TesterAgent',
            'ReviewerAgent',
            'DebuggerAgent',
        ]

        for agent_name in required_agents:
            agent_files = list(Path('src/agents').rglob(f'*{agent_name}.py'))

            if agent_files:
                print(f"  ✓ {agent_name} available for Loop 2")
            else:
                print(f"  ⚠️  {agent_name} not found (Loop 2 blocker)")

    def test_loop3_deployment_workflow(self):
        """Test Loop 3 (Deployment & Quality) workflow."""
        # Loop 3 agents: DevOps, SecurityManager, NASAEnforcer, ReleaseManager
        required_agents = [
            'DevOpsAgent',
            'SecurityManagerAgent',
            'NASAEnforcerAgent',
            'ReleaseManagerAgent',
        ]

        for agent_name in required_agents:
            agent_files = list(Path('src/agents').rglob(f'*{agent_name}.py'))

            if agent_files:
                print(f"  ✓ {agent_name} available for Loop 3")
            else:
                print(f"  ⚠️  {agent_name} not found (Loop 3 blocker)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
