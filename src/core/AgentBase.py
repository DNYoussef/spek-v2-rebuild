"""
AgentBase - Python implementation of AgentContract

Provides abstract base class for Python agents to implement AgentContract.
TypeScript definitions are in AgentContract.ts, this provides Python runtime.

Design Principles:
- Unified API matching TypeScript AgentContract
- <5ms validation latency target
- Extensible metadata system
- NASA POT10 compliance (functions ≤60 lines)

Version: 8.0.0 (Week 3 Day 1)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import time


class AgentType(str, Enum):
    """Agent type categorization."""
    CORE = "core"
    SWARM = "swarm"
    SPECIALIZED = "specialized"


class AgentStatus(str, Enum):
    """Agent health and availability status."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class TaskContext:
    """Task execution context."""
    working_directory: str
    project_root: str
    project_name: Optional[str] = None
    git_commit_hash: Optional[str] = None
    previous_results: Optional[List[Dict[str, Any]]] = None


@dataclass
class Task:
    """Task to be performed by an agent."""
    id: str
    type: str
    description: str
    payload: Dict[str, Any]
    priority: int  # 0-10, 10=highest
    timeout: int = 300000  # milliseconds (5 minutes default)
    context: Optional[TaskContext] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ErrorInfo:
    """Structured error information."""
    code: str
    message: str
    stack: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ResourceUsage:
    """Resource consumption tracking."""
    cpu_time: Optional[float] = None  # milliseconds
    memory_peak: Optional[int] = None  # bytes
    disk_io: Optional[int] = None  # bytes
    network_io: Optional[int] = None  # bytes


@dataclass
class ResultMetadata:
    """Additional result information."""
    timestamp: str
    retry_count: Optional[int] = None
    resource_usage: Optional[ResourceUsage] = None
    artifacts: Optional[List[str]] = None


@dataclass
class Result:
    """Task execution result."""
    task_id: str
    success: bool
    agent_id: str
    execution_time: float  # milliseconds
    data: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    metadata: Optional[ResultMetadata] = None


@dataclass
class ValidationError:
    """Validation failure details."""
    field: str
    message: str
    severity: int  # 1-10, 10=critical


@dataclass
class ValidationResult:
    """Task validation outcome."""
    valid: bool
    validation_time: float  # milliseconds
    errors: Optional[List[ValidationError]] = None


@dataclass
class AgentCapability:
    """Agent capability description."""
    name: str
    description: str
    level: int  # 1-10, 10=expert


@dataclass
class AgentMetadata:
    """Agent metadata and configuration."""
    agent_id: str
    name: str
    type: AgentType
    version: str
    supported_task_types: List[str]
    capabilities: List[AgentCapability]
    status: AgentStatus
    config: Optional[Dict[str, Any]] = None
    mcp_tools: Optional[List[str]] = None


class AgentBase(ABC):
    """
    Abstract base class implementing AgentContract.

    All 22 agents inherit from this class and implement:
    - validate(task) -> ValidationResult
    - execute(task) -> Result
    """

    def __init__(self, metadata: AgentMetadata):
        """
        Initialize agent with metadata.

        Args:
            metadata: Agent metadata and configuration
        """
        assert metadata, "metadata cannot be None"
        assert metadata.agent_id, "agent_id cannot be empty"
        self._metadata = metadata

    @property
    def metadata(self) -> AgentMetadata:
        """Get agent metadata."""
        return self._metadata

    @abstractmethod
    async def validate(self, task: Task) -> ValidationResult:
        """
        Validate a task before execution.

        Must complete in <5ms (p95 latency target).

        Args:
            task: Task to validate

        Returns:
            ValidationResult with errors if invalid
        """
        pass

    @abstractmethod
    async def execute(self, task: Task) -> Result:
        """
        Execute a validated task.

        Performs the actual work and returns a result.
        Must handle timeouts gracefully.

        Args:
            task: Task to execute (assumed valid)

        Returns:
            Result with success indicator and data/error
        """
        pass

    def get_metadata(self) -> AgentMetadata:
        """
        Get agent metadata.

        Returns:
            AgentMetadata
        """
        return self._metadata

    async def health_check(self) -> bool:
        """
        Health check (optional, <10ms target).

        Verifies agent is responsive and healthy.

        Returns:
            bool: True if healthy
        """
        return True

    def update_status(self, status: AgentStatus) -> None:
        """
        Update agent status.

        Called by protocol to track agent availability.

        Args:
            status: New agent status
        """
        self._metadata.status = status

    def validate_task_structure(self, task: Task) -> List[ValidationError]:
        """
        Validate task structure (common validation logic).

        Protected helper for implementing classes.

        Args:
            task: Task to validate

        Returns:
            List[ValidationError]: Empty if valid
        """
        errors: List[ValidationError] = []

        if not task.id or not isinstance(task.id, str):
            errors.append(ValidationError(
                field="id",
                message="Task ID must be a non-empty string",
                severity=10
            ))

        if not task.type or not isinstance(task.type, str):
            errors.append(ValidationError(
                field="type",
                message="Task type must be a non-empty string",
                severity=10
            ))

        if not task.description or not isinstance(task.description, str):
            errors.append(ValidationError(
                field="description",
                message="Task description must be a non-empty string",
                severity=8
            ))

        if not isinstance(task.payload, dict):
            errors.append(ValidationError(
                field="payload",
                message="Task payload must be a dictionary",
                severity=10
            ))

        if not isinstance(task.priority, int) or task.priority < 0 or task.priority > 10:
            errors.append(ValidationError(
                field="priority",
                message="Task priority must be an integer between 0 and 10",
                severity=6
            ))

        if task.timeout and (not isinstance(task.timeout, int) or task.timeout <= 0):
            errors.append(ValidationError(
                field="timeout",
                message="Task timeout must be a positive integer",
                severity=6
            ))

        return errors

    def validate_task_type(self, task: Task) -> List[ValidationError]:
        """
        Validate task type (agent-specific).

        Protected helper for implementing classes.

        Args:
            task: Task to validate

        Returns:
            List[ValidationError]: Empty if type supported
        """
        errors: List[ValidationError] = []

        if task.type not in self._metadata.supported_task_types:
            errors.append(ValidationError(
                field="type",
                message=f"Task type '{task.type}' not supported by agent '{self._metadata.agent_id}'",
                severity=10
            ))

        return errors

    def build_result(
        self,
        task_id: str,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[ErrorInfo] = None,
        execution_time: Optional[float] = None
    ) -> Result:
        """
        Build result object (common result construction).

        Protected helper for implementing classes.

        Args:
            task_id: Task ID
            success: Success indicator
            data: Result data (optional)
            error: Error info (optional)
            execution_time: Execution time in ms (optional)

        Returns:
            Result object
        """
        return Result(
            task_id=task_id,
            success=success,
            agent_id=self._metadata.agent_id,
            execution_time=execution_time or 0.0,
            data=data,
            error=error,
            metadata=ResultMetadata(
                timestamp=datetime.now().isoformat()
            )
        )


# Export all types
__all__ = [
    "AgentBase",
    "AgentType",
    "AgentStatus",
    "Task",
    "TaskContext",
    "Result",
    "ErrorInfo",
    "ResultMetadata",
    "ResourceUsage",
    "ValidationResult",
    "ValidationError",
    "AgentMetadata",
    "AgentCapability",
]
