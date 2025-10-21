"""
QueenAgent - Top-Level Multi-Agent Coordinator

The Queen is the highest-level orchestrator in SPEK Platform's Princess Hive architecture.
Delegates high-level tasks to Princess agents (Dev, Quality, Coordination).
Aggregates and synthesizes results from multiple Princess agents.

Hierarchy:
    Queen (this agent)
      ├─ Princess-Dev (development tasks)
      ├─ Princess-Quality (testing/QA tasks)
      └─ Princess-Coordination (orchestration tasks)

Week 5 Day 1
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
from src.agents.instructions import QUEEN_SYSTEM_INSTRUCTIONS


# ============================================================================
# Queen-Specific Types
# ============================================================================

@dataclass
class PrincessAssignment:
    """Assignment to a Princess agent."""
    princess_id: str
    tasks: List[Task]
    priority: int


@dataclass
class AggregatedResult:
    """Aggregated result from multiple Princess agents."""
    task_id: str
    success: bool
    princess_results: Dict[str, Result]
    summary: str
    execution_time: float


# ============================================================================
# QueenAgent Class
# ============================================================================

class QueenAgent(AgentBase):
    """
    Queen Agent - Top-level multi-agent coordinator.

    Responsibilities:
    - Orchestrate complex multi-agent workflows
    - Delegate tasks to Princess agents
    - Monitor overall system health
    - Aggregate and synthesize results
    """

    def __init__(self):
        """Initialize Queen Agent."""
        metadata = create_agent_metadata(
            agent_id="queen",
            name="Queen Coordinator",
            agent_type=AgentType.CORE,
            supported_task_types=[
                "orchestrate",
                "coordinate",
                "delegate",
                "aggregate"
            ],
            capabilities=[
                AgentCapability(
                    name="Multi-Agent Orchestration",
                    description="Coordinate complex workflows across multiple agents",
                    level=10
                ),
                AgentCapability(
                    name="Task Decomposition",
                    description="Break down complex tasks into subtasks",
                    level=9
                ),
                AgentCapability(
                    name="Result Aggregation",
                    description="Synthesize results from multiple agents",
                    level=9
                ),
                AgentCapability(
                    name="System Health Monitoring",
                    description="Monitor overall agent swarm health",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=QUEEN_SYSTEM_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Princess agent registry
        self.princess_agents = {
            "princess-dev": ["code", "review", "debug", "integrate"],
            "princess-quality": ["test", "nasa-check", "theater-detect", "fsm-analyze"],
            "princess-coordination": ["orchestrate", "plan", "track-cost"]
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

        # Queen-specific validation
        if task.type == "orchestrate":
            errors.extend(self._validate_orchestrate_payload(task))
        elif task.type == "delegate":
            errors.extend(self._validate_delegate_payload(task))
        elif task.type == "aggregate":
            errors.extend(self._validate_aggregate_payload(task))

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
            if task.type == "orchestrate":
                result_data = await self._execute_orchestrate(task)
            elif task.type == "coordinate":
                result_data = await self._execute_coordinate(task)
            elif task.type == "delegate":
                result_data = await self._execute_delegate(task)
            elif task.type == "aggregate":
                result_data = await self._execute_aggregate(task)
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

    async def _execute_orchestrate(self, task: Task) -> Dict[str, Any]:
        """
        Orchestrate complex multi-agent workflow.

        Args:
            task: Orchestrate task

        Returns:
            Orchestration result
        """
        workflow = task.payload.get("workflow", {})
        phases = workflow.get("phases", [])

        self.log_info(f"Orchestrating workflow with {len(phases)} phases")

        # Execute phases sequentially
        phase_results = []

        for i, phase in enumerate(phases):
            self.log_info(f"Executing phase {i+1}/{len(phases)}: {phase.get('name')}")

            princess_id = self._select_princess(phase.get("task_type"))
            phase_task = self._create_phase_task(task.id, phase)

            # Delegate to Princess
            result = await self.delegate_task(princess_id, phase_task)
            phase_results.append({
                "phase": phase.get("name"),
                "success": result.success,
                "data": result.data
            })

            # Stop on failure if not configured to continue
            if not result.success and not phase.get("continue_on_failure", False):
                break

        return {
            "workflow_id": task.id,
            "phases_executed": len(phase_results),
            "phases_total": len(phases),
            "results": phase_results
        }

    async def _execute_coordinate(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate multiple Princess agents in parallel.

        Args:
            task: Coordinate task

        Returns:
            Coordination result
        """
        assignments = task.payload.get("assignments", [])

        self.log_info(f"Coordinating {len(assignments)} Princess assignments")

        # Execute assignments in parallel
        tasks_futures = []

        for assignment in assignments:
            princess_id = assignment.get("princess_id")
            subtasks = assignment.get("tasks", [])

            for subtask_data in subtasks:
                subtask = Task(**subtask_data)
                future = self.delegate_task(princess_id, subtask)
                tasks_futures.append(future)

        # Wait for all results
        results = await asyncio.gather(*tasks_futures, return_exceptions=True)

        # Aggregate results
        successful = sum(1 for r in results if isinstance(r, Result) and r.success)
        failed = len(results) - successful

        return {
            "total_tasks": len(results),
            "successful": successful,
            "failed": failed,
            "results": [r.__dict__ if isinstance(r, Result) else str(r) for r in results]
        }

    async def _execute_delegate(self, task: Task) -> Dict[str, Any]:
        """
        Delegate single task to appropriate Princess.

        Args:
            task: Delegate task

        Returns:
            Delegation result
        """
        subtask_data = task.payload.get("subtask")
        subtask = Task(**subtask_data)

        # Select Princess based on task type
        princess_id = self._select_princess(subtask.type)

        self.log_info(f"Delegating task {subtask.id} to {princess_id}")

        # Delegate
        result = await self.delegate_task(princess_id, subtask)

        return {
            "princess_id": princess_id,
            "task_id": subtask.id,
            "success": result.success,
            "result": result.__dict__
        }

    async def _execute_aggregate(self, task: Task) -> Dict[str, Any]:
        """
        Aggregate results from multiple Princess agents.

        Args:
            task: Aggregate task

        Returns:
            Aggregated result
        """
        results_data = task.payload.get("results", [])

        self.log_info(f"Aggregating {len(results_data)} results")

        # Convert to Result objects
        results = [Result(**r) for r in results_data]

        # Aggregate statistics
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        # Synthesize summary
        summary = self._synthesize_summary(results)

        return {
            "total_results": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "summary": summary
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _select_princess(self, task_type: str) -> str:
        """
        Select appropriate Princess for task type.

        Args:
            task_type: Task type

        Returns:
            Princess agent ID
        """
        for princess_id, supported_types in self.princess_agents.items():
            if task_type in supported_types:
                return princess_id

        # Default to coordination
        return "princess-coordination"

    def _create_phase_task(self, workflow_id: str, phase: Dict[str, Any]) -> Task:
        """Create task from workflow phase."""
        import uuid

        return Task(
            id=f"{workflow_id}-phase-{str(uuid.uuid4())[:8]}",
            type=phase.get("task_type", "generic"),
            description=phase.get("description", ""),
            payload=phase.get("payload", {}),
            priority=phase.get("priority", 5)
        )

    def _synthesize_summary(self, results: List[Result]) -> str:
        """
        Synthesize summary from multiple results.

        Args:
            results: List of results

        Returns:
            Summary string
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        summary_parts = []

        if successful:
            summary_parts.append(f"Completed {len(successful)} tasks successfully")

        if failed:
            summary_parts.append(f"{len(failed)} tasks failed")

        return ". ".join(summary_parts) if summary_parts else "No results to summarize"

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_orchestrate_payload(self, task: Task) -> List[ValidationError]:
        """Validate orchestrate task payload."""
        errors = []

        if "workflow" not in task.payload:
            errors.append(ValidationError(
                field="payload.workflow",
                message="Orchestrate task requires 'workflow' in payload",
                severity=10
            ))
        elif "phases" not in task.payload["workflow"]:
            errors.append(ValidationError(
                field="payload.workflow.phases",
                message="Workflow requires 'phases' list",
                severity=10
            ))

        return errors

    def _validate_delegate_payload(self, task: Task) -> List[ValidationError]:
        """Validate delegate task payload."""
        errors = []

        if "subtask" not in task.payload:
            errors.append(ValidationError(
                field="payload.subtask",
                message="Delegate task requires 'subtask' in payload",
                severity=10
            ))

        return errors

    def _validate_aggregate_payload(self, task: Task) -> List[ValidationError]:
        """Validate aggregate task payload."""
        errors = []

        if "results" not in task.payload:
            errors.append(ValidationError(
                field="payload.results",
                message="Aggregate task requires 'results' list in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_queen_agent() -> QueenAgent:
    """
    Create Queen Agent instance.

    Returns:
        QueenAgent
    """
    return QueenAgent()
