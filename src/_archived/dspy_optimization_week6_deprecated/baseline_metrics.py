"""
Baseline Performance Metrics Collection

Collects baseline performance metrics for agents before DSPy optimization.
Used for A/B testing and ROI calculation.

Week 6 Day 1
Version: 8.0.0
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json

from src.agents.AgentBase import Task, AgentBase


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single agent."""
    agent_id: str
    validation_time_ms: float
    execution_time_ms: float
    success_rate: float
    quality_score: float  # 0-100
    throughput_tasks_per_sec: float
    timestamp: str


@dataclass
class BaselineReport:
    """Baseline performance report for all agents."""
    metrics: Dict[str, PerformanceMetrics]
    total_agents_tested: int
    test_duration_sec: float
    timestamp: str


class BaselineCollector:
    """Collects baseline performance metrics for agents."""

    def __init__(self, output_dir: str = "benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_agent_baseline(
        self,
        agent: AgentBase,
        test_tasks: List[Task],
        iterations: int = 10
    ) -> PerformanceMetrics:
        """
        Collect baseline metrics for a single agent.

        Args:
            agent: Agent to benchmark
            test_tasks: List of test tasks to execute
            iterations: Number of iterations per task

        Returns:
            PerformanceMetrics for the agent
        """
        validation_times = []
        execution_times = []
        successes = 0
        total_runs = 0

        start_time = time.time()

        for task in test_tasks:
            for _ in range(iterations):
                total_runs += 1

                # Measure validation time
                val_start = time.time()
                validation = await agent.validate(task)
                val_time = (time.time() - val_start) * 1000
                validation_times.append(val_time)

                # Measure execution time
                exec_start = time.time()
                result = await agent.execute(task)
                exec_time = (time.time() - exec_start) * 1000
                execution_times.append(exec_time)

                if result.success:
                    successes += 1

        end_time = time.time()
        duration = end_time - start_time

        # Calculate metrics
        avg_validation = sum(validation_times) / len(validation_times)
        avg_execution = sum(execution_times) / len(execution_times)
        success_rate = (successes / total_runs) * 100
        throughput = total_runs / duration

        # Quality score (placeholder - will be enhanced with DSPy)
        quality_score = success_rate  # Initial: quality = success rate

        return PerformanceMetrics(
            agent_id=agent.metadata.agent_id,
            validation_time_ms=avg_validation,
            execution_time_ms=avg_execution,
            success_rate=success_rate,
            quality_score=quality_score,
            throughput_tasks_per_sec=throughput,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    async def collect_baseline_report(
        self,
        agents: Dict[str, AgentBase],
        task_generators: Dict[str, callable]
    ) -> BaselineReport:
        """
        Collect baseline report for multiple agents.

        Args:
            agents: Dict of agent_id -> agent instance
            task_generators: Dict of agent_id -> task generator function

        Returns:
            BaselineReport with all agent metrics
        """
        metrics = {}
        start_time = time.time()

        for agent_id, agent in agents.items():
            print(f"Collecting baseline for {agent_id}...")

            # Generate test tasks
            task_gen = task_generators.get(agent_id)
            if not task_gen:
                print(f"  Warning: No task generator for {agent_id}, skipping")
                continue

            test_tasks = task_gen()

            # Collect metrics
            agent_metrics = await self.collect_agent_baseline(
                agent, test_tasks, iterations=5
            )
            metrics[agent_id] = agent_metrics

            print(f"  [OK] {agent_id}: {agent_metrics.success_rate:.1f}% success, "
                  f"{agent_metrics.execution_time_ms:.2f}ms avg execution")

        duration = time.time() - start_time

        report = BaselineReport(
            metrics=metrics,
            total_agents_tested=len(metrics),
            test_duration_sec=duration,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        return report

    def save_report(self, report: BaselineReport, filename: str = "baseline_report.json"):
        """Save baseline report to JSON file."""
        output_path = self.output_dir / filename

        report_dict = {
            "total_agents_tested": report.total_agents_tested,
            "test_duration_sec": report.test_duration_sec,
            "timestamp": report.timestamp,
            "metrics": {
                agent_id: {
                    "agent_id": m.agent_id,
                    "validation_time_ms": m.validation_time_ms,
                    "execution_time_ms": m.execution_time_ms,
                    "success_rate": m.success_rate,
                    "quality_score": m.quality_score,
                    "throughput_tasks_per_sec": m.throughput_tasks_per_sec,
                    "timestamp": m.timestamp
                }
                for agent_id, m in report.metrics.items()
            }
        }

        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)

        print(f"\nBaseline report saved to: {output_path}")

    def load_report(self, filename: str = "baseline_report.json") -> Optional[BaselineReport]:
        """Load baseline report from JSON file."""
        file_path = self.output_dir / filename

        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)

        metrics = {
            agent_id: PerformanceMetrics(**m)
            for agent_id, m in data["metrics"].items()
        }

        return BaselineReport(
            metrics=metrics,
            total_agents_tested=data["total_agents_tested"],
            test_duration_sec=data["test_duration_sec"],
            timestamp=data["timestamp"]
        )


def create_baseline_collector(output_dir: str = "benchmarks") -> BaselineCollector:
    """Factory function to create BaselineCollector."""
    return BaselineCollector(output_dir=output_dir)
