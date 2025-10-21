"""
DSPy Signature Definitions

Signatures define the input/output schema for DSPy modules.
Each signature represents a specific type of agent communication or task.

Week 21 Day 3
Version: 1.0.0
"""

from .task_decomposition import TaskDecompositionSignature
from .task_delegation import TaskDelegationSignature
from .result_aggregation import ResultAggregationSignature
from .mcp_tool_call import MCPToolCallSignature

__all__ = [
    "TaskDecompositionSignature",
    "TaskDelegationSignature",
    "ResultAggregationSignature",
    "MCPToolCallSignature"
]
