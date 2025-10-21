"""
PrincessQualityAgent - Quality Assurance Coordination Swarm

Coordinates quality assurance tasks across drone agents:
- Tester: Test creation and validation
- NASA-Enforcer: NASA Rule 10 compliance
- Theater-Detector: Mock code detection
- FSM-Analyzer: FSM validation

Part of Princess Hive delegation model (Queen → Princess → Drone).

Week 5 Day 3
Version: 8.0.0
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

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
from src.agents.instructions import PRINCESS_QUALITY_INSTRUCTIONS


# ============================================================================
# Princess-Quality Specific Types
# ============================================================================

@dataclass
class QualityGate:
    """Quality gate configuration."""
    name: str
    threshold: float
    current_value: float
    passed: bool


@dataclass
class QualityReport:
    """Quality assurance report."""
    gates_passed: int
    gates_failed: int
    overall_score: float
    gates: List[QualityGate]


# ============================================================================
# PrincessQualityAgent Class
# ============================================================================

class PrincessQualityAgent(AgentBase):
    """
    Princess-Quality Agent - Quality assurance coordination swarm.

    Responsibilities:
    - Coordinate quality assurance tasks
    - Delegate to drone agents (Tester, NASA-Enforcer, Theater-Detector, FSM-Analyzer)
    - Enforce quality gates
    - Aggregate quality metrics
    """

    def __init__(self):
        """Initialize Princess-Quality Agent."""
        metadata = create_agent_metadata(
            agent_id="princess-quality",
            name="Quality Assurance Coordinator",
            agent_type=AgentType.SWARM,
            supported_task_types=[
                "coordinate-qa",
                "test",
                "nasa-check",
                "theater-detect",
                "fsm-analyze"
            ],
            capabilities=[
                AgentCapability(
                    name="Quality Assurance Coordination",
                    description="Coordinate QA tasks across drone agents",
                    level=10
                ),
                AgentCapability(
                    name="Quality Gate Enforcement",
                    description="Enforce quality gates and standards",
                    level=9
                ),
                AgentCapability(
                    name="Test Orchestration",
                    description="Orchestrate test creation and execution",
                    level=9
                ),
                AgentCapability(
                    name="Compliance Validation",
                    description="Validate NASA Rule 10 and other standards",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=PRINCESS_QUALITY_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Drone agent registry (Week 8: Added code-analyzer)
        self.drone_agents = {
            "tester": ["test", "validate-coverage", "run-tests"],
            "code-analyzer": ["analyze-code", "detect-complexity", "detect-duplicates", "analyze-dependencies", "analyze", "metrics", "complexity"],
            "nasa-enforcer": ["nasa-check", "compliance"],
            "theater-detector": ["theater-detect", "mock-scan"],
            "fsm-analyzer": ["fsm-analyze", "fsm-validate"]
        }

        # Quality gates configuration
        self.quality_gates = {
            "test_coverage": 80.0,
            "nasa_compliance": 90.0,
            "theater_score": 10.0,  # max allowed
            "fsm_complexity": 10.0   # max allowed
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

        # Princess-Quality specific validation
        if task.type == "coordinate-qa":
            errors.extend(self._validate_coordinate_payload(task))

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
            if task.type == "coordinate-qa":
                result_data = await self._execute_coordinate_qa(task)
            elif task.type in ["test", "nasa-check", "theater-detect", "fsm-analyze"]:
                result_data = await self._execute_delegate_to_drone(task)
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

    async def _execute_coordinate_qa(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate quality assurance workflow.

        QA phases:
        1. Test: Generate and run tests (Tester)
        2. NASA: Check NASA Rule 10 compliance (NASA-Enforcer)
        3. Theater: Detect mock code (Theater-Detector)
        4. FSM: Validate FSM usage (FSM-Analyzer)

        Args:
            task: Coordinate-qa task

        Returns:
            QA coordination result
        """
        qa_workflow = task.payload.get("qa_workflow", {})
        phases = qa_workflow.get("phases", ["test", "nasa-check"])

        self.log_info(f"Coordinating QA workflow: {phases}")

        # Execute phases in parallel (QA checks are independent)
        phase_tasks = []

        for phase in phases:
            phase_task = self._create_phase_task(task.id, phase, qa_workflow)
            drone_id = self._select_drone(phase)
            phase_tasks.append(self.delegate_task(drone_id, phase_task))

        # Wait for all phases
        phase_results_list = await asyncio.gather(*phase_tasks, return_exceptions=True)

        # Build phase results dict
        phase_results = {}
        for i, phase in enumerate(phases):
            result = phase_results_list[i]
            if isinstance(result, Result):
                phase_results[phase] = result.__dict__
            else:
                phase_results[phase] = {"success": False, "error": str(result)}

        # Evaluate quality gates
        quality_gates = self._evaluate_quality_gates(phase_results)

        # Calculate overall score
        overall_score = self._calculate_quality_score(quality_gates)

        return {
            "qa_workflow_id": task.id,
            "phases_executed": len(phase_results),
            "quality_gates": [g.__dict__ for g in quality_gates],
            "gates_passed": sum(1 for g in quality_gates if g.passed),
            "gates_failed": sum(1 for g in quality_gates if not g.passed),
            "overall_score": overall_score,
            "phase_results": phase_results
        }

    async def _execute_delegate_to_drone(self, task: Task) -> Dict[str, Any]:
        """
        Delegate single task to drone agent.

        Args:
            task: Task to delegate

        Returns:
            Delegation result
        """
        drone_id = self._select_drone(task.type)

        self.log_info(f"Delegating {task.type} task to {drone_id}")

        # Delegate to drone
        result = await self.delegate_task(drone_id, task)

        return {
            "drone_id": drone_id,
            "task_id": task.id,
            "task_type": task.type,
            "success": result.success,
            "result": result.__dict__
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _select_drone(self, task_type: str) -> str:
        """
        Select appropriate drone agent for task type.

        Args:
            task_type: Task type

        Returns:
            Drone agent ID
        """
        for drone_id, supported_types in self.drone_agents.items():
            if task_type in supported_types:
                return drone_id

        # Default to tester
        return "tester"

    def _create_phase_task(
        self,
        workflow_id: str,
        phase: str,
        qa_workflow: Dict[str, Any]
    ) -> Task:
        """Create task from QA workflow phase."""
        import uuid

        return Task(
            id=f"{workflow_id}-{phase}-{str(uuid.uuid4())[:8]}",
            type=phase,
            description=qa_workflow.get("description", f"{phase} task"),
            payload=qa_workflow.get("phase_payloads", {}).get(phase, {}),
            priority=qa_workflow.get("priority", 8)  # QA is high priority
        )

    def _evaluate_quality_gates(
        self,
        phase_results: Dict[str, Dict[str, Any]]
    ) -> List[QualityGate]:
        """
        Evaluate quality gates from phase results.

        Args:
            phase_results: Results from each QA phase

        Returns:
            List of evaluated quality gates
        """
        gates = []

        # Test coverage gate
        if "test" in phase_results:
            test_result = phase_results["test"]
            coverage = test_result.get("data", {}).get("coverage_percent", 0.0)
            gates.append(QualityGate(
                name="test_coverage",
                threshold=self.quality_gates["test_coverage"],
                current_value=coverage,
                passed=coverage >= self.quality_gates["test_coverage"]
            ))

        # NASA compliance gate
        if "nasa-check" in phase_results:
            nasa_result = phase_results["nasa-check"]
            compliance = nasa_result.get("data", {}).get("compliance_percent", 0.0)
            gates.append(QualityGate(
                name="nasa_compliance",
                threshold=self.quality_gates["nasa_compliance"],
                current_value=compliance,
                passed=compliance >= self.quality_gates["nasa_compliance"]
            ))

        # Theater detection gate (lower is better)
        if "theater-detect" in phase_results:
            theater_result = phase_results["theater-detect"]
            theater_score = theater_result.get("data", {}).get("theater_score", 100.0)
            gates.append(QualityGate(
                name="theater_score",
                threshold=self.quality_gates["theater_score"],
                current_value=theater_score,
                passed=theater_score <= self.quality_gates["theater_score"]
            ))

        # FSM complexity gate (lower is better)
        if "fsm-analyze" in phase_results:
            fsm_result = phase_results["fsm-analyze"]
            fsm_complexity = fsm_result.get("data", {}).get("complexity", 0.0)
            gates.append(QualityGate(
                name="fsm_complexity",
                threshold=self.quality_gates["fsm_complexity"],
                current_value=fsm_complexity,
                passed=fsm_complexity <= self.quality_gates["fsm_complexity"]
            ))

        return gates

    def _calculate_quality_score(self, quality_gates: List[QualityGate]) -> float:
        """
        Calculate overall quality score (0-100).

        Args:
            quality_gates: Evaluated quality gates

        Returns:
            Overall quality score
        """
        if not quality_gates:
            return 0.0

        passed = sum(1 for g in quality_gates if g.passed)
        total = len(quality_gates)

        return round((passed / total) * 100, 2)

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_coordinate_payload(self, task: Task) -> List[ValidationError]:
        """Validate coordinate-qa task payload."""
        errors = []

        if "qa_workflow" not in task.payload:
            errors.append(ValidationError(
                field="payload.qa_workflow",
                message="Coordinate-qa task requires 'qa_workflow' in payload",
                severity=10
            ))
        elif "phases" not in task.payload["qa_workflow"]:
            errors.append(ValidationError(
                field="payload.qa_workflow.phases",
                message="QA workflow requires 'phases' list",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_princess_quality_agent() -> PrincessQualityAgent:
    """
    Create Princess-Quality Agent instance.

    Returns:
        PrincessQualityAgent
    """
    return PrincessQualityAgent()
