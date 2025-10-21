"""
Baseline Metrics Collection Script

Collects baseline performance metrics for P0 agents before DSPy optimization.
Creates benchmark data for A/B testing and ROI calculation.

Usage:
    python scripts/collect_baseline_metrics.py

Week 6 Day 1
Version: 8.0.0
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.AgentBase import Task
from src.agents.core import (
    create_queen_agent,
    create_coder_agent,
    create_tester_agent,
    create_reviewer_agent
)
from src.dspy_optimization.baseline_metrics import create_baseline_collector
from src.dspy_optimization.optimizer_config import get_p0_agents


def create_queen_tasks():
    """Generate test tasks for Queen agent."""
    return [
        Task(
            id="queen-001",
            type="orchestrate",
            description="Orchestrate feature implementation workflow",
            payload={
                "workflow": {
                    "steps": [
                        {"agent": "spec-writer", "task": "write-spec"},
                        {"agent": "architect", "task": "design"},
                        {"agent": "coder", "task": "implement"}
                    ]
                }
            },
            priority=7
        ),
        Task(
            id="queen-002",
            type="coordinate",
            description="Coordinate multi-agent code review",
            payload={
                "workflow": {
                    "steps": [
                        {"agent": "reviewer", "task": "review"},
                        {"agent": "tester", "task": "test"}
                    ]
                }
            },
            priority=8
        ),
        Task(
            id="queen-003",
            type="delegate",
            description="Delegate debugging task",
            payload={
                "workflow": {
                    "steps": [
                        {"agent": "debugger", "task": "debug"}
                    ]
                }
            },
            priority=9
        )
    ]


def create_tester_tasks():
    """Generate test tasks for Tester agent."""
    return [
        Task(
            id="tester-001",
            type="test",
            description="Create test suite for user authentication",
            payload={
                "source_file": "src/auth/login.py",
                "test_type": "unit"
            },
            priority=7
        ),
        Task(
            id="tester-002",
            type="generate-tests",
            description="Generate integration tests for API",
            payload={
                "source_file": "src/api/routes.py",
                "test_type": "integration"
            },
            priority=6
        ),
        Task(
            id="tester-003",
            type="test",
            description="Create edge case tests for validation",
            payload={
                "source_file": "src/validators/input.py",
                "test_type": "unit"
            },
            priority=8
        )
    ]


def create_reviewer_tasks():
    """Generate test tasks for Reviewer agent."""
    return [
        Task(
            id="reviewer-001",
            type="review",
            description="Review code quality for login module",
            payload={
                "file_path": "src/auth/login.py",
                "review_type": "quality"
            },
            priority=7
        ),
        Task(
            id="reviewer-002",
            type="security-review",
            description="Security review for API endpoints",
            payload={
                "file_path": "src/api/routes.py",
                "review_type": "security"
            },
            priority=9
        ),
        Task(
            id="reviewer-003",
            type="review",
            description="Performance review for database queries",
            payload={
                "file_path": "src/db/queries.py",
                "review_type": "performance"
            },
            priority=6
        )
    ]


def create_coder_tasks():
    """Generate test tasks for Coder agent."""
    return [
        Task(
            id="coder-001",
            type="code",
            description="Implement user authentication function",
            payload={
                "specification": "Create login function with email/password validation",
                "language": "python",
                "output_file": "src/auth/login.py"
            },
            priority=7
        ),
        Task(
            id="coder-002",
            type="refactor",
            description="Refactor API route handlers",
            payload={
                "source_file": "src/api/routes.py",
                "refactor_type": "simplify",
                "language": "python"
            },
            priority=6
        ),
        Task(
            id="coder-003",
            type="code",
            description="Implement data validation utilities",
            payload={
                "specification": "Create validation functions for user input",
                "language": "python",
                "output_file": "src/validators/input.py"
            },
            priority=8
        )
    ]


async def main():
    """Main execution function."""
    print("="*80)
    print("BASELINE METRICS COLLECTION - P0 AGENTS")
    print("Week 6 Day 1 - Pre-DSPy Optimization")
    print("="*80)
    print()

    # Create P0 agents
    print("Creating P0 agents...")
    agents = {
        "queen": create_queen_agent(),
        "tester": create_tester_agent(),
        "reviewer": create_reviewer_agent(),
        "coder": create_coder_agent()
    }
    print(f"[OK] Created {len(agents)} agents\n")

    # Create task generators
    task_generators = {
        "queen": create_queen_tasks,
        "tester": create_tester_tasks,
        "reviewer": create_reviewer_tasks,
        "coder": create_coder_tasks
    }

    # Create baseline collector
    collector = create_baseline_collector(output_dir="benchmarks/week6")

    # Collect baseline report
    print("Collecting baseline metrics (this may take a few minutes)...\n")
    report = await collector.collect_baseline_report(agents, task_generators)

    # Save report
    collector.save_report(report, filename="baseline_p0_agents.json")

    # Display summary
    print("\n" + "="*80)
    print("BASELINE METRICS SUMMARY")
    print("="*80)
    print(f"\nTotal agents tested: {report.total_agents_tested}")
    print(f"Test duration: {report.test_duration_sec:.2f}s")
    print(f"Timestamp: {report.timestamp}\n")

    print("Agent Performance:")
    print("-" * 80)
    print(f"{'Agent':<15} {'Success %':<12} {'Exec Time':<15} {'Throughput':<15} {'Quality':<10}")
    print("-" * 80)

    for agent_id, metrics in sorted(report.metrics.items()):
        print(f"{agent_id:<15} {metrics.success_rate:>10.1f}% "
              f"{metrics.execution_time_ms:>12.2f}ms "
              f"{metrics.throughput_tasks_per_sec:>12.2f}/s "
              f"{metrics.quality_score:>8.1f}")

    print("\n" + "="*80)
    print("Baseline collection complete!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review baseline metrics in benchmarks/week6/baseline_p0_agents.json")
    print("2. Set optimization targets based on baseline")
    print("3. Configure Gemini API for DSPy training")
    print("4. Begin DSPy optimization for P0 agents")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
