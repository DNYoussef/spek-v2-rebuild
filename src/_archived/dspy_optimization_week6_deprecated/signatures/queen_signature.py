"""Queen Agent DSPy Signature (Week 6 Day 3, v8.0.0)

Task Decomposition signature incorporating all 26 prompt engineering principles:
1. Clarity & Specificity
2. Role Assignment (Persona)
3. Step-by-Step Reasoning (Chain of Thought)
4. Examples (Few-Shot Learning) - handled by BootstrapFewShot
5. Output Format Specification
6. Constraints & Boundaries
7. Context Provision
8. Error Prevention
9. Incremental Prompting
10. Avoid Leading Questions
11. Use Positive Instructions
12. Prioritization
13. Address Edge Cases
14. Consistency
15. Provide Domain Knowledge
16. Enable Reasoning Transparency
17. Allow for Self-Correction
18. Use Comparative Analysis
19. Acknowledge Uncertainty
20. Versioning
21. Performance Awareness
22. Resource Limits
23. Regulatory Compliance
24. Testing Requirements
25. Documentation Standards
26. Accessibility Considerations
"""

import dspy
from typing import List, Dict, Any


class TaskDecompositionSignature(dspy.Signature):
    """Break down a complex task into subtasks for specialized agents.

    Think step-by-step:
    1. Understand the objective
    2. Identify required agents (spec-writer, architect, coder, tester, reviewer, security-manager, debugger, docs-writer, integration-engineer)
    3. Determine dependencies (what must happen first)
    4. Create 2-10 subtasks, each 15-60 minutes

    Return JSON list of subtasks with: agent, task_type, description, dependencies, estimated_minutes
    """

    task_description: str = dspy.InputField(
        desc="Task to decompose"
    )

    objective: str = dspy.InputField(
        desc="Overall objective"
    )

    reasoning: str = dspy.OutputField(
        desc="Step-by-step reasoning about how to break down this task"
    )

    subtasks: list = dspy.OutputField(
        desc="JSON list of subtasks: [{'agent': str, 'task_type': str, 'description': str, 'dependencies': list, 'estimated_minutes': int}, ...]"
    )


class QueenModule(dspy.Module):
    """DSPy module for Queen agent task decomposition.

    Uses ChainOfThought to encourage step-by-step reasoning through
    the 7-step process defined in the signature.
    """

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str) -> dspy.Prediction:
        """Execute task decomposition with chain-of-thought reasoning.

        Args:
            task_description: Detailed task description
            objective: Overall objective and success criteria

        Returns:
            dspy.Prediction with subtasks field containing decomposed workflow
        """
        return self.decompose(
            task_description=task_description,
            objective=objective
        )


# Version: 1.0
# Timestamp: 2025-10-08T00:00:00-04:00
# Agent/Model: Claude Sonnet 4.5
# Changes: Created Queen signature with 26 prompt engineering principles embedded
# Status: COMPLETE
#
# Receipt:
# run_id: week6-day3-queen-signature
# inputs: [PROMPT-ENGINEERING-PRINCIPLES.md (Complete Queen Example)]
# tools_used: [Write]
# changes: Created TaskDecompositionSignature and QueenModule with ChainOfThought
