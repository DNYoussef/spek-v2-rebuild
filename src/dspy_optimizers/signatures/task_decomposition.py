"""
Task Decomposition Signature

Used for Queen → Princess communication where complex tasks
must be decomposed into princess-level subtasks.

Week 21 Day 3
Version: 1.0.0
"""

import dspy


class TaskDecompositionSignature(dspy.Signature):
    """
    Decompose complex task into princess-level subtasks.

    You are an expert Queen agent coordinating Princess agents.
    Your role is to break down complex objectives into actionable
    princess-level subtasks that can be executed by the three
    princess hives: Development, Quality, and Coordination.

    Each subtask must have:
    - Clear princess assignment (princess-dev, princess-quality, princess-coordination)
    - Specific task type matching princess capabilities
    - Realistic time estimate (15-60 minutes)
    - Valid dependencies (no circular references)
    - Concrete, measurable description

    Follow the 26 prompt engineering principles:
    - Clarity: Use precise, unambiguous language
    - Reasoning: Show step-by-step decomposition logic
    - Constraints: Respect NASA Rule 10 (≤60 LOC functions)
    - Structure: Output valid JSON format
    """

    task_description = dspy.InputField(
        desc="Complex task requiring decomposition into subtasks"
    )
    objective = dspy.InputField(
        desc="Success criteria and constraints for the overall task"
    )

    reasoning = dspy.OutputField(
        desc="Step-by-step decomposition reasoning explaining why each subtask is needed",
        prefix="Reasoning: Let's think step by step in order to"
    )

    subtasks = dspy.OutputField(
        desc=(
            "Ordered list of princess-level subtasks as JSON array. "
            "Each subtask must have: "
            "{'princess': str, 'task_type': str, 'description': str, "
            "'dependencies': list[str], 'estimated_minutes': int}"
        )
    )
