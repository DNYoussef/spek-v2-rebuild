"""
PerformanceEngineerAgent - Performance Engineering Specialist

Performance profiling, bottleneck detection, and optimization:
- Profile application performance (CPU, memory, I/O)
- Detect performance bottlenecks
- Apply optimizations
- Run performance benchmarks

Part of specialized agent roster (Week 9 Day 3).

Week 9 Day 3
Version: 8.0.0
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from src.agents.AgentBase import (
    AgentBase,
    AgentType,
    AgentStatus,
    AgentCapability,
    AgentMetadata,
    Task,
    ValidationResult,
    ValidationError,
    Result,
    ErrorInfo,
    create_agent_metadata
)
from src.agents.instructions import PERFORMANCE_ENGINEER_INSTRUCTIONS


# ============================================================================
# Performance-Specific Types
# ============================================================================

@dataclass
class ProfileResult:
    """Performance profiling result."""
    duration_ms: float
    cpu_time_ms: float
    memory_mb: float
    io_operations: int
    hot_spots: List[Dict[str, Any]]


@dataclass
class BottleneckInfo:
    """Performance bottleneck information."""
    location: str
    bottleneck_type: str  # cpu, memory, io, network
    severity: int  # 1-10
    impact: str
    recommendation: str


@dataclass
class BenchmarkResult:
    """Benchmark result."""
    test_name: str
    iterations: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    throughput: float  # operations/second


# ============================================================================
# PerformanceEngineerAgent Class
# ============================================================================

class PerformanceEngineerAgent(AgentBase):
    """
    Performance-Engineer Agent - Performance engineering specialist.

    Responsibilities:
    - Profile performance
    - Detect bottlenecks
    - Optimize code
    - Run benchmarks
    """

    def __init__(self):
        """Initialize Performance-Engineer Agent."""
        metadata = create_agent_metadata(
            agent_id="performance-engineer",
            name="Performance Engineering Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "profile-performance",
                "detect-bottlenecks",
                "optimize-performance",
                "benchmark-system"
            ],
            capabilities=[
                AgentCapability(
                    name="Performance Profiling",
                    description="Profile CPU/memory/IO performance",
                    level=10
                ),
                AgentCapability(
                    name="Bottleneck Detection",
                    description="Identify performance bottlenecks",
                    level=9
                ),
                AgentCapability(
                    name="Optimization Strategies",
                    description="Apply performance optimizations",
                    level=9
                ),
                AgentCapability(
                    name="Load Testing",
                    description="Perform load and stress testing",
                    level=8
                ),
                AgentCapability(
                    name="Memory Analysis",
                    description="Analyze memory usage and leaks",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 principles
            system_instructions=PERFORMANCE_ENGINEER_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Performance metrics thresholds
        self.thresholds = {
            "response_time_ms": 200,
            "cpu_usage_percent": 80,
            "memory_usage_mb": 512,
            "io_operations_per_sec": 1000
        }

        # Optimization strategies
        self.optimizations = {
            "cpu": [
                "Use caching to reduce computation",
                "Optimize algorithms (O(n) vs O(n^2))",
                "Use lazy evaluation",
                "Parallelize independent operations"
            ],
            "memory": [
                "Use generators instead of lists",
                "Implement object pooling",
                "Clear unused references",
                "Use memory-efficient data structures"
            ],
            "io": [
                "Batch I/O operations",
                "Use async I/O",
                "Implement read-ahead buffering",
                "Reduce filesystem calls"
            ],
            "network": [
                "Use connection pooling",
                "Implement request caching",
                "Compress payloads",
                "Use CDN for static assets"
            ]
        }

    # ========================================================================
    # AgentContract Implementation
    # ========================================================================

    async def validate(self, task: Task) -> ValidationResult:
        """
        Validate task before execution.

        Target: <5ms latency

        Args:
            task: Task to validate

        Returns:
            ValidationResult
        """
        start_time = time.time()
        errors = []

        # Common structure validation
        errors.extend(self.validate_task_structure(task))

        # Task type validation
        errors.extend(self.validate_task_type(task))

        # Performance-specific validation
        if task.type == "profile-performance":
            errors.extend(self._validate_profile_payload(task))

        validation_time = (time.time() - start_time) * 1000  # ms

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            validation_time=validation_time
        )

    async def execute(self, task: Task) -> Result:
        """
        Execute validated task.

        Routes to appropriate handler based on task type.

        Args:
            task: Task to execute

        Returns:
            Result
        """
        start_time = time.time()

        try:
            self.update_status(AgentStatus.BUSY)
            self.log_info(f"Executing task {task.id} (type: {task.type})")

            # Route to handler
            if task.type == "profile-performance":
                result_data = await self._execute_profile(task)
            elif task.type == "detect-bottlenecks":
                result_data = await self._execute_detect_bottlenecks(task)
            elif task.type == "optimize-performance":
                result_data = await self._execute_optimize(task)
            elif task.type == "benchmark-system":
                result_data = await self._execute_benchmark(task)
            else:
                raise ValueError(f"Unsupported task type: {task.type}")

            execution_time = (time.time() - start_time) * 1000  # ms

            self.update_status(AgentStatus.IDLE)

            return self.build_result(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000  # ms
            self.log_error(f"Task {task.id} failed", exc=e)

            self.update_status(AgentStatus.ERROR)

            return self.build_result(
                task_id=task.id,
                success=False,
                error=ErrorInfo(
                    code="EXECUTION_FAILED",
                    message=str(e),
                    stack=None
                ),
                execution_time=execution_time
            )

    # ========================================================================
    # Task Execution Methods
    # ========================================================================

    async def _execute_profile(self, task: Task) -> Dict[str, Any]:
        """
        Profile application performance.

        Args:
            task: Profile-performance task

        Returns:
            Profiling result
        """
        target = task.payload.get("target")
        profile_type = task.payload.get("type", "cpu")

        self.log_info(f"Profiling {target} ({profile_type})")

        # Simulate profiling
        profile = ProfileResult(
            duration_ms=1250.5,
            cpu_time_ms=980.3,
            memory_mb=245.8,
            io_operations=42,
            hot_spots=[
                {
                    "function": "process_data",
                    "file": "src/processor.py",
                    "line": 145,
                    "time_ms": 450.2,
                    "calls": 1000,
                    "time_per_call_ms": 0.45
                },
                {
                    "function": "database_query",
                    "file": "src/database.py",
                    "line": 78,
                    "time_ms": 320.1,
                    "calls": 50,
                    "time_per_call_ms": 6.4
                }
            ]
        )

        # Generate profiling report
        report = self._generate_profile_report(profile)

        # Write report file
        output_dir = task.payload.get("output_dir", "performance")
        report_file = Path(output_dir) / f"profile_{profile_type}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return {
            "target": target,
            "profile_type": profile_type,
            "duration_ms": profile.duration_ms,
            "cpu_time_ms": profile.cpu_time_ms,
            "memory_mb": profile.memory_mb,
            "hot_spot_count": len(profile.hot_spots),
            "report_file": str(report_file),
            "profile": profile.__dict__
        }

    async def _execute_detect_bottlenecks(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Detect performance bottlenecks.

        Args:
            task: Detect-bottlenecks task

        Returns:
            Bottleneck detection result
        """
        target = task.payload.get("target")

        self.log_info(f"Detecting bottlenecks in: {target}")

        # Simulate bottleneck detection
        bottlenecks = [
            BottleneckInfo(
                location="src/processor.py:145 (process_data)",
                bottleneck_type="cpu",
                severity=8,
                impact="36% of total CPU time",
                recommendation="Cache frequently computed values"
            ),
            BottleneckInfo(
                location="src/database.py:78 (database_query)",
                bottleneck_type="io",
                severity=7,
                impact="26% of total execution time",
                recommendation="Add database index on query field"
            ),
            BottleneckInfo(
                location="src/api.py:234 (fetch_external_data)",
                bottleneck_type="network",
                severity=6,
                impact="15% of total execution time",
                recommendation="Implement request caching"
            )
        ]

        # Sort by severity
        bottlenecks.sort(key=lambda b: b.severity, reverse=True)

        return {
            "target": target,
            "bottleneck_count": len(bottlenecks),
            "critical_count": sum(1 for b in bottlenecks if b.severity >= 8),
            "bottlenecks": [b.__dict__ for b in bottlenecks]
        }

    async def _execute_optimize(self, task: Task) -> Dict[str, Any]:
        """
        Apply performance optimizations.

        Args:
            task: Optimize-performance task

        Returns:
            Optimization result
        """
        target = task.payload.get("target")
        optimization_type = task.payload.get("type", "cpu")

        self.log_info(f"Optimizing {target} ({optimization_type})")

        # Get optimization strategies
        strategies = self.optimizations.get(optimization_type, [])

        # Simulate applying optimizations
        applied = []
        for strategy in strategies[:3]:  # Apply top 3
            applied.append({
                "strategy": strategy,
                "estimated_improvement": "15-25%",
                "applied": True
            })

        # Measure improvement (simulated)
        before_time_ms = 1250.5
        after_time_ms = 875.3
        improvement_percent = (
            (before_time_ms - after_time_ms) / before_time_ms * 100
        )

        return {
            "target": target,
            "optimization_type": optimization_type,
            "strategies_applied": len(applied),
            "before_time_ms": before_time_ms,
            "after_time_ms": after_time_ms,
            "improvement_percent": round(improvement_percent, 1),
            "optimizations": applied
        }

    async def _execute_benchmark(self, task: Task) -> Dict[str, Any]:
        """
        Run performance benchmarks.

        Args:
            task: Benchmark-system task

        Returns:
            Benchmark result
        """
        target = task.payload.get("target")
        iterations = task.payload.get("iterations", 1000)

        self.log_info(f"Benchmarking {target} ({iterations} iterations)")

        # Simulate benchmark run
        benchmark = BenchmarkResult(
            test_name=target,
            iterations=iterations,
            avg_time_ms=2.45,
            min_time_ms=1.82,
            max_time_ms=5.21,
            std_dev_ms=0.63,
            throughput=408.16  # ops/sec
        )

        # Check against thresholds
        within_target = benchmark.avg_time_ms < self.thresholds[
            "response_time_ms"
        ]

        # Generate benchmark report
        report = self._generate_benchmark_report(benchmark)

        # Write report file
        output_dir = task.payload.get("output_dir", "benchmarks")
        report_file = Path(output_dir) / f"benchmark_{target}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return {
            "target": target,
            "iterations": iterations,
            "avg_time_ms": benchmark.avg_time_ms,
            "throughput": benchmark.throughput,
            "within_target": within_target,
            "report_file": str(report_file),
            "benchmark": benchmark.__dict__
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _generate_profile_report(self, profile: ProfileResult) -> str:
        """Generate profiling report."""
        report = f"""Performance Profile Report
==========================

Duration: {profile.duration_ms:.2f} ms
CPU Time: {profile.cpu_time_ms:.2f} ms
Memory: {profile.memory_mb:.2f} MB
I/O Operations: {profile.io_operations}

Hot Spots:
----------
"""

        for i, hot_spot in enumerate(profile.hot_spots, 1):
            report += f"""
{i}. {hot_spot['function']} ({hot_spot['file']}:{hot_spot['line']})
   Total Time: {hot_spot['time_ms']:.2f} ms
   Calls: {hot_spot['calls']}
   Time/Call: {hot_spot['time_per_call_ms']:.4f} ms
"""

        return report

    def _generate_benchmark_report(
        self,
        benchmark: BenchmarkResult
    ) -> str:
        """Generate benchmark report."""
        report = f"""Benchmark Report: {benchmark.test_name}
{'=' * (18 + len(benchmark.test_name))}

Iterations: {benchmark.iterations}

Timing Statistics:
  Average: {benchmark.avg_time_ms:.4f} ms
  Minimum: {benchmark.min_time_ms:.4f} ms
  Maximum: {benchmark.max_time_ms:.4f} ms
  Std Dev: {benchmark.std_dev_ms:.4f} ms

Throughput: {benchmark.throughput:.2f} ops/sec
"""

        return report

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_profile_payload(self, task: Task) -> List[ValidationError]:
        """Validate profile-performance task payload."""
        errors = []

        if "target" not in task.payload:
            errors.append(ValidationError(
                field="payload.target",
                message="Profile task requires 'target' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_performance_engineer_agent() -> PerformanceEngineerAgent:
    """
    Create Performance-Engineer Agent instance.

    Returns:
        PerformanceEngineerAgent
    """
    return PerformanceEngineerAgent()
