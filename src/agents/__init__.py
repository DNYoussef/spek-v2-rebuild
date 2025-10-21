"""
SPEK Platform v8 - Agent System

22 agents implementing AgentContract interface:
- 5 core agents: queen, coder, researcher, tester, reviewer
- 3 swarm coordinators: princess-dev, princess-quality, princess-coordination
- 14 specialized agents: architect, debugger, docs-writer, etc.

Week 5
Version: 8.0.0
"""

from .AgentBase import (
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
    ResultMetadata,
    create_agent_metadata
)

__all__ = [
    "AgentBase",
    "AgentType",
    "AgentStatus",
    "AgentCapability",
    "AgentMetadata",
    "Task",
    "ValidationResult",
    "ValidationError",
    "Result",
    "ErrorInfo",
    "ResultMetadata",
    "create_agent_metadata"
]
