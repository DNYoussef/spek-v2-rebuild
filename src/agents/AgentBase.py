"""
AgentBase - Base class for all SPEK Platform agents

Provides common functionality for all agents implementing AgentContract.
Uses EnhancedLightweightProtocol for coordination.

All 22 agents extend this base class.

Week 5 Day 1
Version: 8.0.0
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from src.protocols.EnhancedLightweightProtocol import EnhancedLightweightProtocol, ProtocolConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Types (Python equivalents of TypeScript AgentContract types)
# ============================================================================

class AgentType(str, Enum):
    """Agent type categorization."""
    CORE = "core"
    SWARM = "swarm"
    SPECIALIZED = "specialized"


class AgentStatus(str, Enum):
    """Agent status."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentCapability:
    """Agent capability description."""
    name: str
    description: str
    level: int  # 1-10, 10=expert


@dataclass
class AgentMetadata:
    """Agent metadata."""
    agent_id: str
    name: str
    type: AgentType
    version: str
    supported_task_types: List[str]
    capabilities: List[AgentCapability]
    status: AgentStatus
    config: Dict[str, Any] = field(default_factory=dict)
    mcp_tools: List[str] = field(default_factory=list)
    system_instructions: Optional[str] = None  # Week 21: Prompt engineering principles


@dataclass
class Task:
    """Task to be performed by an agent."""
    id: str
    type: str
    description: str
    payload: Dict[str, Any]
    priority: int  # 0-10
    timeout: Optional[int] = 300000  # 5 minutes default
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationError:
    """Validation error."""
    field: str
    message: str
    severity: int  # 1-10


@dataclass
class ValidationResult:
    """Task validation result."""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    validation_time: float = 0.0


@dataclass
class ErrorInfo:
    """Error information."""
    code: str
    message: str
    stack: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultMetadata:
    """Result metadata."""
    timestamp: str
    retry_count: int = 0
    resource_usage: Optional[Dict[str, Any]] = None
    artifacts: List[str] = field(default_factory=list)


@dataclass
class Result:
    """Task execution result."""
    task_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[ErrorInfo] = None
    execution_time: float = 0.0
    agent_id: str = ""
    metadata: Optional[ResultMetadata] = None


# ============================================================================
# AgentBase Class
# ============================================================================

class AgentBase(ABC):
    """
    Base class for all SPEK Platform agents.

    Implements AgentContract interface with common functionality.
    """

    def __init__(
        self,
        metadata: AgentMetadata,
        protocol: Optional[EnhancedLightweightProtocol] = None
    ):
        """
        Initialize agent.

        Args:
            metadata: Agent metadata
            protocol: Optional protocol instance (creates default if not provided)
        """
        self.metadata = metadata
        self.protocol = protocol or EnhancedLightweightProtocol(ProtocolConfig())
        self.start_time = time.time()

    # ========================================================================
    # Abstract Methods (Must be implemented by subclasses)
    # ========================================================================

    @abstractmethod
    async def validate(self, task: Task) -> ValidationResult:
        """
        Validate task before execution.

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
        Execute validated task.

        Args:
            task: Task to execute (assumed valid)

        Returns:
            Result with success indicator and data/error
        """
        pass

    # ========================================================================
    # Implemented Methods (Common functionality)
    # ========================================================================

    def get_metadata(self) -> AgentMetadata:
        """
        Get agent metadata.

        Returns:
            AgentMetadata
        """
        return self.metadata

    async def health_check(self) -> bool:
        """
        Health check (optional, <10ms target).

        Returns:
            bool: True if healthy
        """
        return self.metadata.status != AgentStatus.OFFLINE

    def update_status(self, status: AgentStatus) -> None:
        """
        Update agent status.

        Args:
            status: New agent status
        """
        self.metadata.status = status
        logger.info(f"Agent {self.metadata.agent_id} status: {status}")

    # ========================================================================
    # Protected Helper Methods
    # ========================================================================

    def validate_task_structure(self, task: Task) -> List[ValidationError]:
        """
        Validate task structure (common validation logic).

        Args:
            task: Task to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

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

        if not task.payload or not isinstance(task.payload, dict):
            errors.append(ValidationError(
                field="payload",
                message="Task payload must be a dict",
                severity=10
            ))

        if not isinstance(task.priority, int) or task.priority < 0 or task.priority > 10:
            errors.append(ValidationError(
                field="priority",
                message="Task priority must be an integer between 0 and 10",
                severity=6
            ))

        if task.timeout is not None and (not isinstance(task.timeout, int) or task.timeout <= 0):
            errors.append(ValidationError(
                field="timeout",
                message="Task timeout must be a positive integer",
                severity=6
            ))

        return errors

    def validate_task_type(self, task: Task) -> List[ValidationError]:
        """
        Validate task type (agent-specific).

        Args:
            task: Task to validate

        Returns:
            List of validation errors (empty if type supported)
        """
        errors = []

        if task.type not in self.metadata.supported_task_types:
            errors.append(ValidationError(
                field="type",
                message=f"Task type '{task.type}' not supported by agent '{self.metadata.agent_id}'",
                severity=10
            ))

        return errors

    def build_result(
        self,
        task_id: str,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[ErrorInfo] = None,
        execution_time: float = 0.0
    ) -> Result:
        """
        Build result object (common result construction).

        Args:
            task_id: Task ID
            success: Success indicator
            data: Result data (optional)
            error: Error info (optional)
            execution_time: Execution time in ms

        Returns:
            Result object
        """
        from datetime import datetime

        return Result(
            task_id=task_id,
            success=success,
            data=data,
            error=error,
            execution_time=execution_time,
            agent_id=self.metadata.agent_id,
            metadata=ResultMetadata(
                timestamp=datetime.utcnow().isoformat()
            )
        )

    async def delegate_task(
        self,
        target_agent_id: str,
        task: Task
    ) -> Result:
        """
        Delegate task to another agent via protocol.

        Uses EnhancedLightweightProtocol for <100ms coordination.

        Args:
            target_agent_id: Target agent ID
            task: Task to delegate

        Returns:
            Result from target agent
        """
        result_data = await self.protocol.send_task(
            sender_id=self.metadata.agent_id,
            receiver_id=target_agent_id,
            task=task.__dict__
        )

        # Convert dict to Result
        return Result(**result_data)

    def log_info(self, message: str) -> None:
        """Log info message."""
        logger.info(f"[{self.metadata.agent_id}] {message}")

    def log_error(self, message: str, exc: Optional[Exception] = None) -> None:
        """Log error message."""
        logger.error(f"[{self.metadata.agent_id}] {message}", exc_info=exc)

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        logger.debug(f"[{self.metadata.agent_id}] {message}")


# ============================================================================
# Factory Functions
# ============================================================================

def create_agent_metadata(
    agent_id: str,
    name: str,
    agent_type: AgentType,
    supported_task_types: List[str],
    capabilities: List[AgentCapability],
    version: str = "8.0.0",
    system_instructions: Optional[str] = None
) -> AgentMetadata:
    """
    Create agent metadata.

    Args:
        agent_id: Unique agent identifier
        name: Agent name
        agent_type: Agent type (core/swarm/specialized)
        supported_task_types: Task types this agent supports
        capabilities: Agent capabilities
        version: Agent version
        system_instructions: System prompt with 26 prompt engineering principles (Week 21)

    Returns:
        AgentMetadata instance
    """
    return AgentMetadata(
        agent_id=agent_id,
        name=name,
        type=agent_type,
        version=version,
        supported_task_types=supported_task_types,
        capabilities=capabilities,
        status=AgentStatus.IDLE,
        system_instructions=system_instructions
    )
