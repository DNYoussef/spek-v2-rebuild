"""PlannerAgent - Task Planning Specialist (Week 5 Day 6, v8.0.0)"""
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from src.agents.AgentBase import (AgentBase, AgentType, AgentStatus, AgentCapability, Task, ValidationResult, Result, ErrorInfo, create_agent_metadata)
from src.agents.instructions import PLANNER_INSTRUCTIONS

@dataclass
class TaskPlan:
    plan_id: str
    tasks: List[Dict[str, Any]]
    estimated_duration_min: int

class PlannerAgent(AgentBase):
    def __init__(self):
        metadata = create_agent_metadata(agent_id="planner", name="Task Planning Specialist", agent_type=AgentType.SPECIALIZED, supported_task_types=["create-plan", "decompose-task"], capabilities=[AgentCapability(name="Task Decomposition", description="Break down complex tasks", level=10), AgentCapability(name="Planning", description="Create execution plans", level=9)],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=PLANNER_INSTRUCTIONS.to_prompt()
        )
        super().__init__(metadata=metadata)
    async def validate(self, task: Task) -> ValidationResult:
        errors = []
        errors.extend(self.validate_task_structure(task))
        errors.extend(self.validate_task_type(task))
        return ValidationResult(valid=len(errors) == 0, errors=errors, validation_time=2.0)
    async def execute(self, task: Task) -> Result:
        start_time = time.time()
        try:
            self.update_status(AgentStatus.BUSY)
            objective = task.payload.get("objective", "")
            tasks = [{"task": f"Step {i+1}", "agent": "coder"} for i in range(3)]
            self.update_status(AgentStatus.IDLE)
            return self.build_result(task_id=task.id, success=True, data={"plan_id": task.id, "task_count": len(tasks), "tasks": tasks}, execution_time=(time.time() - start_time) * 1000)
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return self.build_result(task_id=task.id, success=False, error=ErrorInfo(code="EXECUTION_FAILED", message=str(e)), execution_time=(time.time() - start_time) * 1000)

def create_planner_agent() -> PlannerAgent:
    return PlannerAgent()
