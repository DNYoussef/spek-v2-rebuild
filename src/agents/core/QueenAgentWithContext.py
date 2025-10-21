"""
Queen Agent with Context DNA Integration

Enhanced Queen agent demonstrating Context DNA integration.
Shows how to use context persistence in agent execution.

Week 20 Day 1 - Example Integration
Version: 8.0.0
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from src.agents.AgentBase import (
    AgentBase,
    AgentMetadata,
    AgentType,
    AgentStatus,
    AgentCapability,
    Task,
    ValidationResult,
    Result,
    ErrorInfo,
    create_agent_metadata,
)
from src.services.context_dna_bridge import (
    get_context_dna_bridge,
    AgentExecutionContext,
)


class QueenAgentWithContext(AgentBase):
    """
    Queen Agent with Context DNA integration.

    Demonstrates automatic context persistence for agent operations.
    """

    def __init__(self):
        """Initialize Queen agent with Context DNA."""
        # Create agent metadata
        metadata = create_agent_metadata(
            agent_id="queen",
            name="Queen Agent",
            agent_type=AgentType.CORE,
            supported_task_types=[
                "coordinate",
                "delegate",
                "monitor",
                "decide",
            ],
            capabilities=[
                AgentCapability(
                    name="coordination",
                    description="Multi-agent coordination",
                    level=10,
                ),
                AgentCapability(
                    name="delegation",
                    description="Task delegation to Princess agents",
                    level=10,
                ),
                AgentCapability(
                    name="monitoring",
                    description="System health monitoring",
                    level=9,
                ),
            ],
        )

        super().__init__(metadata)

        # Context DNA bridge
        self.context_bridge = get_context_dna_bridge()

    async def validate(self, task: Task) -> ValidationResult:
        """
        Validate task before execution.

        Args:
            task: Task to validate

        Returns:
            ValidationResult
        """
        start_time = datetime.now()

        # Common validation
        errors = self.validate_task_structure(task)
        errors.extend(self.validate_task_type(task))

        # Queen-specific validation
        if task.type == "delegate" and not task.payload.get("target_agent"):
            from src.agents.AgentBase import ValidationError
            errors.append(
                ValidationError(
                    field="payload.target_agent",
                    message="Delegation requires target_agent",
                    severity=10,
                )
            )

        validation_time = (datetime.now() - start_time).total_seconds() * 1000

        return ValidationResult(
            valid=len(errors) == 0, errors=errors, validation_time=validation_time
        )

    async def execute(self, task: Task) -> Result:
        """
        Execute validated task with Context DNA persistence.

        Args:
            task: Task to execute

        Returns:
            Result
        """
        start_time = datetime.now()

        # Create execution context
        context = AgentExecutionContext(
            agent_id=self.metadata.agent_id,
            project_id=task.payload.get("project_id", "default"),
            task_id=task.id,
            session_id=str(uuid.uuid4()),
            start_time=start_time,
            metadata={"task_type": task.type},
        )

        try:
            # Initialize context (auto-creates session)
            await self.context_bridge.initialize_context(context)

            self.log_info(f"Executing task: {task.id}")

            # Store initial thought
            await self.context_bridge.store_agent_thought(
                context, f"Starting task: {task.description}"
            )

            # Execute based on task type
            result_data = await self._execute_task(task, context)

            # Store success result
            await self.context_bridge.store_agent_result(
                context,
                {
                    "success": True,
                    "output": result_data.get("output"),
                    "metrics": {
                        "duration_ms": (datetime.now() - start_time).total_seconds()
                        * 1000
                    },
                },
            )

            # Finalize context
            await self.context_bridge.finalize_context(context)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return self.build_result(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time=execution_time,
            )

        except Exception as e:
            self.log_error(f"Task execution failed: {e}", exc=e)

            # Store error result
            await self.context_bridge.store_agent_result(
                context, {"success": False, "error": str(e)}
            )

            # Finalize context with failure
            await self.context_bridge.finalize_context(context)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return self.build_result(
                task_id=task.id,
                success=False,
                error=ErrorInfo(code="EXECUTION_ERROR", message=str(e)),
                execution_time=execution_time,
            )

    async def _execute_task(
        self, task: Task, context: AgentExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute task logic with context tracking.

        Args:
            task: Task to execute
            context: Execution context

        Returns:
            Result data
        """
        # Store thought: analyzing task
        await self.context_bridge.store_agent_thought(
            context, f"Analyzing task type: {task.type}"
        )

        if task.type == "coordinate":
            return await self._coordinate(task, context)
        elif task.type == "delegate":
            return await self._delegate(task, context)
        elif task.type == "monitor":
            return await self._monitor(task, context)
        elif task.type == "decide":
            return await self._decide(task, context)
        else:
            raise ValueError(f"Unsupported task type: {task.type}")

    async def _coordinate(
        self, task: Task, context: AgentExecutionContext
    ) -> Dict[str, Any]:
        """Coordinate multi-agent activity."""
        await self.context_bridge.store_agent_thought(
            context, "Coordinating multi-agent activity"
        )

        # Retrieve relevant context from previous sessions
        previous_context = await self.context_bridge.retrieve_context(
            project_id=context.project_id,
            agent_id=self.metadata.agent_id,
            query="coordination",
            limit=5,
        )

        await self.context_bridge.store_agent_thought(
            context,
            f"Retrieved {len(previous_context['conversations'])} previous conversations",
        )

        # Coordination logic here...
        return {"output": "Coordination complete", "agents_coordinated": 3}

    async def _delegate(
        self, task: Task, context: AgentExecutionContext
    ) -> Dict[str, Any]:
        """Delegate task to Princess agent."""
        target_agent = task.payload.get("target_agent")

        await self.context_bridge.store_agent_thought(
            context, f"Delegating to {target_agent}"
        )

        # Delegation logic here...
        # Would call: await self.delegate_task(target_agent, task)

        return {"output": f"Delegated to {target_agent}", "status": "delegated"}

    async def _monitor(
        self, task: Task, context: AgentExecutionContext
    ) -> Dict[str, Any]:
        """Monitor system health."""
        await self.context_bridge.store_agent_thought(
            context, "Monitoring system health"
        )

        # Monitoring logic here...
        health = await self.health_check()

        return {"output": "Health check complete", "healthy": health}

    async def _decide(
        self, task: Task, context: AgentExecutionContext
    ) -> Dict[str, Any]:
        """Make strategic decision."""
        await self.context_bridge.store_agent_thought(
            context, "Making strategic decision"
        )

        # Decision logic here...
        decision = task.payload.get("options", [None])[0]

        return {"output": f"Decision: {decision}", "decision": decision}


# ============================================================================
# Example Usage
# ============================================================================


async def example_usage():
    """Example of using Queen agent with Context DNA."""
    # Create Queen agent
    queen = QueenAgentWithContext()

    # Create task
    task = Task(
        id="task-001",
        type="coordinate",
        description="Coordinate agents for project setup",
        payload={"project_id": "project-001", "phase": "setup"},
        priority=8,
    )

    # Validate task
    validation = await queen.validate(task)
    print(f"Validation: {validation.valid}")

    if validation.valid:
        # Execute task (auto-persists context)
        result = await queen.execute(task)
        print(f"Result: {result.success}")
        print(f"Data: {result.data}")
        print(f"Execution time: {result.execution_time}ms")


if __name__ == "__main__":
    asyncio.run(example_usage())
