"""
Task Delegation Signature

Used for Princess → Drone communication where princess agents
delegate specific tasks to their drone agents.

Week 21 Day 3
Version: 1.0.0
"""

import dspy


class TaskDelegationSignature(dspy.Signature):
    """
    Delegate task to drone agent with clear instructions.

    You are a Princess agent coordinating your specialized drone hive.
    Your role is to take high-level workflow phases and convert them
    into specific, actionable tasks for your drone agents.

    Princess-Dev drones: coder, reviewer, debugger, integration-engineer
    Princess-Quality drones: tester, nasa-enforcer, theater-detector, fsm-analyzer
    Princess-Coordination drones: orchestrator, planner, cost-tracker

    Each drone task must have:
    - Specific drone agent assignment
    - Task type matching drone capabilities
    - Clear context from previous phases
    - Concrete deliverables
    - Quality gates/acceptance criteria

    Follow the 26 prompt engineering principles:
    - Clarity: Unambiguous instructions
    - Context: Include relevant phase results
    - Constraints: Respect drone capabilities
    - Structure: Output valid JSON format
    """

    phase = dspy.InputField(
        desc="Development phase to execute (design, code, test, review, etc.)"
    )
    context = dspy.InputField(
        desc="Context and results from previous phases that this phase depends on"
    )

    reasoning = dspy.OutputField(
        desc="Delegation reasoning explaining drone selection and task structure",
        prefix="Reasoning: Let's think step by step in order to"
    )

    drone_task = dspy.OutputField(
        desc=(
            "Structured task for drone agent as JSON object. "
            "Must have: "
            "{'drone_id': str, 'task_type': str, 'description': str, "
            "'payload': dict, 'acceptance_criteria': list[str]}"
        )
    )
