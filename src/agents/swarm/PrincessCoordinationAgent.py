"""
PrincessCoordinationAgent - Task Coordination Swarm

Coordinates high-level task orchestration across drone agents:
- Orchestrator: Workflow orchestration
- Planner: Task planning and decomposition
- Cost-Tracker: Budget and cost tracking

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
from src.agents.instructions import PRINCESS_COORDINATION_INSTRUCTIONS


# ============================================================================
# Princess-Coordination Specific Types
# ============================================================================

@dataclass
class TaskPlan:
    """Task plan with decomposition."""
    task_id: str
    subtasks: List[Task]
    dependencies: Dict[str, List[str]]  # task_id → dependency_ids
    estimated_duration: float  # seconds


@dataclass
class CostEstimate:
    """Cost estimate for task execution."""
    task_id: str
    api_calls: int
    token_count: int
    estimated_cost_usd: float


# ============================================================================
# PrincessCoordinationAgent Class
# ============================================================================

class PrincessCoordinationAgent(AgentBase):
    """
    Princess-Coordination Agent - Task coordination swarm.

    Responsibilities:
    - Coordinate high-level task orchestration
    - Delegate to drone agents (Orchestrator, Planner, Cost-Tracker)
    - Plan task execution strategies
    - Track costs and resource usage
    """

    def __init__(self):
        """Initialize Princess-Coordination Agent."""
        metadata = create_agent_metadata(
            agent_id="princess-coordination",
            name="Task Coordination Specialist",
            agent_type=AgentType.SWARM,
            supported_task_types=[
                "coordinate-tasks",
                "orchestrate",
                "plan",
                "track-cost"
            ],
            capabilities=[
                AgentCapability(
                    name="Task Coordination",
                    description="Coordinate high-level task orchestration",
                    level=10
                ),
                AgentCapability(
                    name="Strategic Planning",
                    description="Plan task execution strategies",
                    level=9
                ),
                AgentCapability(
                    name="Resource Optimization",
                    description="Optimize resource allocation and usage",
                    level=8
                ),
                AgentCapability(
                    name="Cost Tracking",
                    description="Track costs and budget compliance",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=PRINCESS_COORDINATION_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Drone agent registry (Week 9: Added infrastructure-ops, release-manager, performance-engineer)
        self.drone_agents = {
            "orchestrator": ["orchestrate", "workflow", "coordinate"],
            "planner": ["plan", "decompose", "strategy"],
            "cost-tracker": ["track-cost", "budget", "estimate"],
            "infrastructure-ops": ["deploy-infrastructure", "scale-infrastructure", "monitor-infrastructure", "configure-infrastructure", "kubernetes", "k8s", "docker", "cloud", "deploy"],
            "release-manager": ["prepare-release", "generate-changelog", "tag-release", "coordinate-deployment", "release", "version", "changelog"],
            "performance-engineer": ["profile-performance", "detect-bottlenecks", "optimize-performance", "benchmark-system", "performance", "profiling", "optimize", "benchmark"]
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

        # Princess-Coordination specific validation
        if task.type == "coordinate-tasks":
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
            if task.type == "coordinate-tasks":
                result_data = await self._execute_coordinate_tasks(task)
            elif task.type in ["orchestrate", "plan", "track-cost"]:
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

    async def _execute_coordinate_tasks(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate task execution strategy.

        Coordination phases:
        1. Plan: Decompose task and plan execution (Planner)
        2. Estimate: Estimate costs (Cost-Tracker)
        3. Orchestrate: Execute planned tasks (Orchestrator)

        Args:
            task: Coordinate-tasks task

        Returns:
            Coordination result
        """
        coordination_strategy = task.payload.get("strategy", {})
        phases = coordination_strategy.get("phases", ["plan", "orchestrate"])

        self.log_info(f"Coordinating tasks with strategy: {phases}")

        # Execute phases sequentially (planning must come first)
        phase_results = {}

        for phase in phases:
            self.log_info(f"Executing coordination phase: {phase}")

            # Create phase task
            phase_task = self._create_phase_task(task.id, phase, coordination_strategy)

            # Delegate to drone
            drone_id = self._select_drone(phase)
            result = await self.delegate_task(drone_id, phase_task)

            phase_results[phase] = result.__dict__

            # Pass planning result to orchestration phase
            if phase == "plan" and "orchestrate" in phases:
                # Extract task plan and pass to orchestration
                task_plan = result.data.get("task_plan", {}) if result.data else {}
                if task_plan:
                    coordination_strategy.setdefault("phase_payloads", {})
                    coordination_strategy["phase_payloads"]["orchestrate"] = {
                        "task_plan": task_plan
                    }

        # Calculate totals
        total_cost = self._calculate_total_cost(phase_results)
        total_tasks = self._count_total_tasks(phase_results)

        return {
            "coordination_id": task.id,
            "phases_executed": len(phase_results),
            "total_tasks": total_tasks,
            "total_cost_usd": total_cost,
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

        # Default to orchestrator
        return "orchestrator"

    def _create_phase_task(
        self,
        coordination_id: str,
        phase: str,
        strategy: Dict[str, Any]
    ) -> Task:
        """Create task from coordination phase."""
        import uuid

        return Task(
            id=f"{coordination_id}-{phase}-{str(uuid.uuid4())[:8]}",
            type=phase,
            description=strategy.get("description", f"{phase} task"),
            payload=strategy.get("phase_payloads", {}).get(phase, {}),
            priority=strategy.get("priority", 7)
        )

    def _calculate_total_cost(self, phase_results: Dict[str, Dict[str, Any]]) -> float:
        """Calculate total cost from phase results."""
        total_cost = 0.0

        for phase_result in phase_results.values():
            data = phase_result.get("data", {})
            if isinstance(data, dict):
                cost = data.get("estimated_cost_usd", 0.0)
                if isinstance(cost, (int, float)):
                    total_cost += cost

        return round(total_cost, 4)

    def _count_total_tasks(self, phase_results: Dict[str, Dict[str, Any]]) -> int:
        """Count total tasks from phase results."""
        total_tasks = 0

        for phase_result in phase_results.values():
            data = phase_result.get("data", {})
            if isinstance(data, dict):
                task_plan = data.get("task_plan", {})
                if task_plan and isinstance(task_plan, dict):
                    subtasks = task_plan.get("subtasks", [])
                    total_tasks += len(subtasks)

        return total_tasks

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_coordinate_payload(self, task: Task) -> List[ValidationError]:
        """Validate coordinate-tasks task payload."""
        errors = []

        if "strategy" not in task.payload:
            errors.append(ValidationError(
                field="payload.strategy",
                message="Coordinate-tasks task requires 'strategy' in payload",
                severity=10
            ))
        elif "phases" not in task.payload["strategy"]:
            errors.append(ValidationError(
                field="payload.strategy.phases",
                message="Strategy requires 'phases' list",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_princess_coordination_agent() -> PrincessCoordinationAgent:
    """
    Create Princess-Coordination Agent instance.

    Returns:
        PrincessCoordinationAgent
    """
    return PrincessCoordinationAgent()
