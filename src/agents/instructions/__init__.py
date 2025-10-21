"""
Agent Instructions Package

Complete system instructions for all 22 SPEK Platform agents.
Each instruction embeds all 26 prompt engineering principles.

Week 21 (Post-DSPy Decision)
Version: 8.0.0

Usage:
    from src.agents.instructions import QUEEN_SYSTEM_INSTRUCTIONS
    prompt = QUEEN_SYSTEM_INSTRUCTIONS.to_prompt()
"""

# Base framework
from src.agents.instructions.AgentInstructionBase import (
    AgentInstruction,
    create_instruction
)

# Core agents (5)
from src.agents.instructions.QueenInstructions import QUEEN_SYSTEM_INSTRUCTIONS
from src.agents.instructions.CoderInstructions import CODER_SYSTEM_INSTRUCTIONS
from src.agents.instructions.TesterInstructions import TESTER_SYSTEM_INSTRUCTIONS
from src.agents.instructions.ReviewerInstructions import REVIEWER_SYSTEM_INSTRUCTIONS
from src.agents.instructions.ResearcherInstructions import RESEARCHER_SYSTEM_INSTRUCTIONS

# Princess agents (3)
from src.agents.instructions.PrincessInstructions import (
    PRINCESS_DEV_INSTRUCTIONS,
    PRINCESS_QUALITY_INSTRUCTIONS,
    PRINCESS_COORDINATION_INSTRUCTIONS
)

# Specialized agents (20)
from src.agents.instructions.SpecializedInstructions import (
    ARCHITECT_INSTRUCTIONS,
    PSEUDOCODE_WRITER_INSTRUCTIONS,
    SPEC_WRITER_INSTRUCTIONS,
    INTEGRATION_ENGINEER_INSTRUCTIONS,
    DEBUGGER_INSTRUCTIONS,
    DOCS_WRITER_INSTRUCTIONS,
    DEVOPS_INSTRUCTIONS,
    SECURITY_MANAGER_INSTRUCTIONS,
    COST_TRACKER_INSTRUCTIONS,
    THEATER_DETECTOR_INSTRUCTIONS,
    NASA_ENFORCER_INSTRUCTIONS,
    FSM_ANALYZER_INSTRUCTIONS,
    ORCHESTRATOR_INSTRUCTIONS,
    PLANNER_INSTRUCTIONS,
    FRONTEND_DEV_INSTRUCTIONS,
    BACKEND_DEV_INSTRUCTIONS,
    CODE_ANALYZER_INSTRUCTIONS,
    INFRASTRUCTURE_OPS_INSTRUCTIONS,
    RELEASE_MANAGER_INSTRUCTIONS,
    PERFORMANCE_ENGINEER_INSTRUCTIONS
)


# Instruction registry (agent_id -> instruction)
AGENT_INSTRUCTIONS = {
    # Core agents
    "queen": QUEEN_SYSTEM_INSTRUCTIONS,
    "coder": CODER_SYSTEM_INSTRUCTIONS,
    "tester": TESTER_SYSTEM_INSTRUCTIONS,
    "reviewer": REVIEWER_SYSTEM_INSTRUCTIONS,
    "researcher": RESEARCHER_SYSTEM_INSTRUCTIONS,

    # Princess agents
    "princess-dev": PRINCESS_DEV_INSTRUCTIONS,
    "princess-quality": PRINCESS_QUALITY_INSTRUCTIONS,
    "princess-coordination": PRINCESS_COORDINATION_INSTRUCTIONS,

    # Specialized agents
    "architect": ARCHITECT_INSTRUCTIONS,
    "pseudocode-writer": PSEUDOCODE_WRITER_INSTRUCTIONS,
    "spec-writer": SPEC_WRITER_INSTRUCTIONS,
    "integration-engineer": INTEGRATION_ENGINEER_INSTRUCTIONS,
    "debugger": DEBUGGER_INSTRUCTIONS,
    "docs-writer": DOCS_WRITER_INSTRUCTIONS,
    "devops": DEVOPS_INSTRUCTIONS,
    "security-manager": SECURITY_MANAGER_INSTRUCTIONS,
    "cost-tracker": COST_TRACKER_INSTRUCTIONS,
    "theater-detector": THEATER_DETECTOR_INSTRUCTIONS,
    "nasa-enforcer": NASA_ENFORCER_INSTRUCTIONS,
    "fsm-analyzer": FSM_ANALYZER_INSTRUCTIONS,
    "orchestrator": ORCHESTRATOR_INSTRUCTIONS,
    "planner": PLANNER_INSTRUCTIONS,
    "frontend-dev": FRONTEND_DEV_INSTRUCTIONS,
    "backend-dev": BACKEND_DEV_INSTRUCTIONS,
    "code-analyzer": CODE_ANALYZER_INSTRUCTIONS,
    "infrastructure-ops": INFRASTRUCTURE_OPS_INSTRUCTIONS,
    "release-manager": RELEASE_MANAGER_INSTRUCTIONS,
    "performance-engineer": PERFORMANCE_ENGINEER_INSTRUCTIONS
}


def get_instruction(agent_id: str) -> AgentInstruction:
    """
    Get system instruction for an agent.

    Args:
        agent_id: Agent identifier (e.g., 'queen', 'coder', 'tester')

    Returns:
        AgentInstruction object

    Raises:
        KeyError: If agent_id not found

    Example:
        >>> instruction = get_instruction('queen')
        >>> prompt = instruction.to_prompt()
        >>> print(prompt)
    """
    if agent_id not in AGENT_INSTRUCTIONS:
        available = ', '.join(sorted(AGENT_INSTRUCTIONS.keys()))
        raise KeyError(
            f"No instruction found for agent '{agent_id}'. "
            f"Available agents: {available}"
        )
    return AGENT_INSTRUCTIONS[agent_id]


def get_all_instructions() -> dict[str, AgentInstruction]:
    """Get all agent instructions."""
    return AGENT_INSTRUCTIONS.copy()


__all__ = [
    # Base
    'AgentInstruction',
    'create_instruction',

    # Helper functions
    'get_instruction',
    'get_all_instructions',
    'AGENT_INSTRUCTIONS',

    # Individual instructions
    'QUEEN_SYSTEM_INSTRUCTIONS',
    'CODER_SYSTEM_INSTRUCTIONS',
    'TESTER_SYSTEM_INSTRUCTIONS',
    'REVIEWER_SYSTEM_INSTRUCTIONS',
    'RESEARCHER_SYSTEM_INSTRUCTIONS',
    'PRINCESS_DEV_INSTRUCTIONS',
    'PRINCESS_QUALITY_INSTRUCTIONS',
    'PRINCESS_COORDINATION_INSTRUCTIONS',
    'ARCHITECT_INSTRUCTIONS',
    'PSEUDOCODE_WRITER_INSTRUCTIONS',
    'SPEC_WRITER_INSTRUCTIONS',
    'INTEGRATION_ENGINEER_INSTRUCTIONS',
    'DEBUGGER_INSTRUCTIONS',
    'DOCS_WRITER_INSTRUCTIONS',
    'DEVOPS_INSTRUCTIONS',
    'SECURITY_MANAGER_INSTRUCTIONS',
    'COST_TRACKER_INSTRUCTIONS',
    'THEATER_DETECTOR_INSTRUCTIONS',
    'NASA_ENFORCER_INSTRUCTIONS',
    'FSM_ANALYZER_INSTRUCTIONS',
    'ORCHESTRATOR_INSTRUCTIONS',
    'PLANNER_INSTRUCTIONS',
    'FRONTEND_DEV_INSTRUCTIONS',
    'BACKEND_DEV_INSTRUCTIONS',
    'CODE_ANALYZER_INSTRUCTIONS',
    'INFRASTRUCTURE_OPS_INSTRUCTIONS',
    'RELEASE_MANAGER_INSTRUCTIONS',
    'PERFORMANCE_ENGINEER_INSTRUCTIONS'
]
