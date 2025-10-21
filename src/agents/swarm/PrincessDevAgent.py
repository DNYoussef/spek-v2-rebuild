"""
PrincessDevAgent - Development Coordination Swarm

Coordinates development tasks across drone agents:
- Coder: Code implementation
- Reviewer: Code review and quality validation
- Debugger: Bug fixing and debugging
- Integration-Engineer: System integration

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
from src.agents.instructions import PRINCESS_DEV_INSTRUCTIONS


# ============================================================================
# Princess-Dev Specific Types
# ============================================================================

@dataclass
class DroneAssignment:
    """Assignment to a drone agent."""
    drone_id: str
    task: Task
    priority: int
    estimated_duration: float  # seconds


@dataclass
class DevelopmentWorkflow:
    """Development workflow phases."""
    phases: List[str]  # code → review → debug → integrate
    current_phase: str
    phase_results: Dict[str, Result]


# ============================================================================
# PrincessDevAgent Class
# ============================================================================

class PrincessDevAgent(AgentBase):
    """
    Princess-Dev Agent - Development coordination swarm.

    Responsibilities:
    - Coordinate development tasks
    - Delegate to drone agents (Coder, Reviewer, Debugger, Integration-Engineer)
    - Manage development workflow phases
    - Aggregate development results
    """

    def __init__(self):
        """Initialize Princess-Dev Agent."""
        metadata = create_agent_metadata(
            agent_id="princess-dev",
            name="Development Coordinator",
            agent_type=AgentType.SWARM,
            supported_task_types=[
                "coordinate-dev",
                "code",
                "review",
                "debug",
                "integrate"
            ],
            capabilities=[
                AgentCapability(
                    name="Development Coordination",
                    description="Coordinate development tasks across drone agents",
                    level=10
                ),
                AgentCapability(
                    name="Workflow Management",
                    description="Manage development workflow phases",
                    level=9
                ),
                AgentCapability(
                    name="Code Quality Enforcement",
                    description="Enforce code quality standards",
                    level=9
                ),
                AgentCapability(
                    name="Drone Delegation",
                    description="Delegate tasks to specialized drone agents",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=PRINCESS_DEV_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Drone agent registry (Week 8: Added frontend-dev, backend-dev)
        self.drone_agents = {
            "coder": ["code", "implement", "write"],
            "frontend-dev": ["implement-component", "implement-ui", "ui", "component", "react", "frontend"],
            "backend-dev": ["implement-api", "implement-database", "api", "database", "endpoint", "backend"],
            "reviewer": ["review", "validate", "check"],
            "debugger": ["debug", "fix", "troubleshoot"],
            "integration-engineer": ["integrate", "merge", "deploy"]
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

        # Princess-Dev specific validation
        if task.type == "coordinate-dev":
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
            if task.type == "coordinate-dev":
                result_data = await self._execute_coordinate_dev(task)
            elif task.type in ["code", "review", "debug", "integrate"]:
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

    async def _execute_coordinate_dev(self, task: Task) -> Dict[str, Any]:
        """
        Coordinate development workflow.

        Workflow phases:
        1. Code: Implement feature (Coder)
        2. Review: Code review (Reviewer)
        3. Debug: Fix issues if needed (Debugger)
        4. Integrate: Merge to main (Integration-Engineer)

        Args:
            task: Coordinate-dev task

        Returns:
            Coordination result
        """
        workflow = task.payload.get("workflow", {})
        phases = workflow.get("phases", ["code", "review"])

        self.log_info(f"Coordinating development workflow: {phases}")

        # Execute phases sequentially
        phase_results = {}

        for phase in phases:
            self.log_info(f"Executing phase: {phase}")

            # Create phase task
            phase_task = self._create_phase_task(task.id, phase, workflow)

            # Delegate to drone
            drone_id = self._select_drone(phase, phase_task)
            result = await self.delegate_task(drone_id, phase_task)

            phase_results[phase] = result.__dict__

            # Stop on failure unless configured to continue
            if not result.success and not workflow.get("continue_on_failure", False):
                break

        # Determine overall success
        all_success = all(
            r.get("success", False) for r in phase_results.values()
        )

        return {
            "workflow_id": task.id,
            "phases_executed": len(phase_results),
            "phases_total": len(phases),
            "all_success": all_success,
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
        drone_id = self._select_drone(task.type, task)

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

    def _select_drone(self, task_type: str, task: Optional[Task] = None) -> str:
        """
        Select appropriate drone agent for task type.

        Week 8: Enhanced with keyword-based routing for frontend-dev/backend-dev.

        Args:
            task_type: Task type
            task: Optional task object for description analysis

        Returns:
            Drone agent ID
        """
        # Check task description for frontend keywords
        if task and task.description:
            desc_lower = task.description.lower()
            if any(kw in desc_lower for kw in ["ui", "component", "react", "frontend", "view", "page"]):
                return "frontend-dev"
            if any(kw in desc_lower for kw in ["api", "database", "endpoint", "backend", "server", "query"]):
                return "backend-dev"

        # Check task type against registry
        for drone_id, supported_types in self.drone_agents.items():
            if task_type in supported_types:
                return drone_id

        # Default to coder
        return "coder"

    def _create_phase_task(
        self,
        workflow_id: str,
        phase: str,
        workflow: Dict[str, Any]
    ) -> Task:
        """Create task from workflow phase."""
        import uuid

        return Task(
            id=f"{workflow_id}-{phase}-{str(uuid.uuid4())[:8]}",
            type=phase,
            description=workflow.get("description", f"{phase} task"),
            payload=workflow.get("phase_payloads", {}).get(phase, {}),
            priority=workflow.get("priority", 5)
        )

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_coordinate_payload(self, task: Task) -> List[ValidationError]:
        """Validate coordinate-dev task payload."""
        errors = []

        if "workflow" not in task.payload:
            errors.append(ValidationError(
                field="payload.workflow",
                message="Coordinate-dev task requires 'workflow' in payload",
                severity=10
            ))
        elif "phases" not in task.payload["workflow"]:
            errors.append(ValidationError(
                field="payload.workflow.phases",
                message="Workflow requires 'phases' list",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_princess_dev_agent() -> PrincessDevAgent:
    """
    Create Princess-Dev Agent instance.

    Returns:
        PrincessDevAgent
    """
    return PrincessDevAgent()
