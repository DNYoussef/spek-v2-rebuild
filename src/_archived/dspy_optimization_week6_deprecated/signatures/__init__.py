"""DSPy Signature Modules for SPEK Platform Agent Optimization (Week 6 Day 3, v8.0.0)

This module contains DSPy signatures for all P0 agents:
- Queen: Task decomposition and workflow orchestration
- Tester: Test generation and validation
- Reviewer: Code review and quality assessment
- Coder: Code implementation

Each signature incorporates 26 prompt engineering principles for optimal quality.
"""

from src.dspy_optimization.signatures.queen_signature import (
    TaskDecompositionSignature,
    QueenModule
)
from src.dspy_optimization.signatures.tester_signature import (
    TestGenerationSignature,
    TesterModule
)
from src.dspy_optimization.signatures.reviewer_signature import (
    CodeReviewSignature,
    ReviewerModule
)
from src.dspy_optimization.signatures.coder_signature import (
    CodeImplementationSignature,
    CoderModule
)

__all__ = [
    "TaskDecompositionSignature",
    "QueenModule",
    "TestGenerationSignature",
    "TesterModule",
    "CodeReviewSignature",
    "ReviewerModule",
    "CodeImplementationSignature",
    "CoderModule"
]

# Version: 1.0
# Timestamp: 2025-10-08T00:00:00-04:00
# Agent/Model: Claude Sonnet 4.5
# Changes: Initial creation with DSPy signature imports for 4 P0 agents
# Status: COMPLETE
#
# Receipt:
# run_id: week6-day3-signatures-init
# inputs: [DSPY-INTEGRATION-STRATEGY.md, PROMPT-ENGINEERING-PRINCIPLES.md]
# tools_used: [Write]
# changes: Created __init__.py with signature module exports
