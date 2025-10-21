"""
Agent Registry

Complete registry of all 28 SPEK Platform agents:
- 1 Queen (top coordinator)
- 3 Princesses (coordination layer)
- 24 Drones (specialized workers)

This registry is used by Princesses to choose which Drones to spawn.

Version: 8.2.0 (Week 26)
"""

from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class AgentCapabilities:
    """What an agent can do."""
    keywords: List[str]  # Keywords that trigger this agent
    task_types: List[str]  # Types of tasks this agent handles
    loop: str  # Which loop (loop1, loop2, loop3)
    description: str  # What this agent does


# ============================================================================
# AGENT REGISTRY - All 28 Agents
# ============================================================================

AGENT_REGISTRY: Dict[str, AgentCapabilities] = {

    # ========================================================================
    # QUEEN (1 agent) - Top-level coordinator
    # ========================================================================

    "queen": AgentCapabilities(
        keywords=["coordinate", "orchestrate", "manage"],
        task_types=["coordination", "delegation"],
        loop="all",
        description="Top-level coordinator that delegates to Princesses"
    ),

    # ========================================================================
    # PRINCESSES (3 agents) - Coordination layer
    # ========================================================================

    "princess-dev": AgentCapabilities(
        keywords=["implement", "code", "build", "develop", "create", "write"],
        task_types=["development", "implementation", "coding"],
        loop="loop2",
        description="Development coordinator - spawns Coder, Tester, Reviewer"
    ),

    "princess-coordination": AgentCapabilities(
        keywords=["research", "plan", "analyze", "design", "spec", "architecture"],
        task_types=["research", "planning", "analysis", "design"],
        loop="loop1",
        description="Research coordinator - spawns Researcher, Spec-Writer, Architect"
    ),

    "princess-quality": AgentCapabilities(
        keywords=["test", "review", "audit", "quality", "validate", "document"],
        task_types=["testing", "quality", "audit", "documentation"],
        loop="loop3",
        description="Quality coordinator - spawns Theater-Detector, NASA-Enforcer, Docs-Writer"
    ),

    # ========================================================================
    # CORE DRONES (5 agents) - Basic development
    # ========================================================================

    "coder": AgentCapabilities(
        keywords=["code", "implement", "write", "function", "class", "module"],
        task_types=["coding", "implementation"],
        loop="loop2",
        description="Writes clean, tested code following NASA Rule 10 (≤60 LOC per function)"
    ),

    "tester": AgentCapabilities(
        keywords=["test", "pytest", "unittest", "coverage", "assertion"],
        task_types=["testing", "validation"],
        loop="loop2",
        description="Writes comprehensive test suites with ≥80% coverage"
    ),

    "reviewer": AgentCapabilities(
        keywords=["review", "critique", "feedback", "improve", "refactor"],
        task_types=["review", "quality"],
        loop="loop2",
        description="Reviews code for quality, security, and best practices"
    ),

    "researcher": AgentCapabilities(
        keywords=["research", "investigate", "study", "analyze", "explore"],
        task_types=["research", "investigation"],
        loop="loop1",
        description="Researches problem domains and gathers information"
    ),

    "planner": AgentCapabilities(
        keywords=["plan", "strategy", "roadmap", "schedule", "timeline"],
        task_types=["planning", "strategy"],
        loop="loop1",
        description="Creates project plans and schedules"
    ),

    # ========================================================================
    # SPARC DRONES (4 agents) - SPARC methodology
    # ========================================================================

    "spec-writer": AgentCapabilities(
        keywords=["specification", "requirements", "spec", "document"],
        task_types=["specification", "documentation"],
        loop="loop1",
        description="Writes technical specifications and requirements documents"
    ),

    "architect": AgentCapabilities(
        keywords=["architecture", "design", "system", "structure", "pattern"],
        task_types=["architecture", "design"],
        loop="loop1",
        description="Designs system architecture and component interactions"
    ),

    "pseudocode-writer": AgentCapabilities(
        keywords=["pseudocode", "algorithm", "logic", "flow"],
        task_types=["algorithm", "design"],
        loop="loop1",
        description="Writes pseudocode and algorithm designs"
    ),

    "integration-engineer": AgentCapabilities(
        keywords=["integrate", "merge", "combine", "connect"],
        task_types=["integration", "connection"],
        loop="loop2",
        description="Integrates components and ensures they work together"
    ),

    # ========================================================================
    # SPECIALIZED DRONES (10 agents) - Specific tasks
    # ========================================================================

    "debugger": AgentCapabilities(
        keywords=["debug", "fix", "bug", "error", "issue"],
        task_types=["debugging", "troubleshooting"],
        loop="loop2",
        description="Debugs issues and fixes bugs"
    ),

    "docs-writer": AgentCapabilities(
        keywords=["documentation", "readme", "guide", "tutorial", "docs"],
        task_types=["documentation", "writing"],
        loop="loop3",
        description="Generates comprehensive documentation"
    ),

    "devops": AgentCapabilities(
        keywords=["deploy", "ci/cd", "docker", "kubernetes", "pipeline"],
        task_types=["deployment", "devops"],
        loop="loop3",
        description="Handles deployment and CI/CD pipeline setup"
    ),

    "security-manager": AgentCapabilities(
        keywords=["security", "vulnerability", "audit", "penetration", "threat"],
        task_types=["security", "audit"],
        loop="loop3",
        description="Performs security audits and vulnerability assessments"
    ),

    "cost-tracker": AgentCapabilities(
        keywords=["cost", "budget", "pricing", "expense", "billing"],
        task_types=["cost", "budget"],
        loop="loop3",
        description="Tracks costs and manages budgets"
    ),

    "theater-detector": AgentCapabilities(
        keywords=["mock", "fake", "placeholder", "todo", "fixme"],
        task_types=["detection", "audit"],
        loop="loop3",
        description="Detects mock code, TODOs, and placeholder implementations"
    ),

    "nasa-enforcer": AgentCapabilities(
        keywords=["nasa", "compliance", "rule10", "lint", "standard"],
        task_types=["compliance", "validation"],
        loop="loop3",
        description="Enforces NASA Rule 10 (≤60 LOC per function, ≥2 assertions)"
    ),

    "fsm-analyzer": AgentCapabilities(
        keywords=["fsm", "state", "machine", "xstate", "transition"],
        task_types=["fsm", "analysis"],
        loop="loop3",
        description="Analyzes and validates finite state machines"
    ),

    "orchestrator": AgentCapabilities(
        keywords=["orchestrate", "workflow", "coordinate", "manage"],
        task_types=["orchestration", "coordination"],
        loop="loop2",
        description="Orchestrates complex multi-agent workflows"
    ),

    # ========================================================================
    # FRONTEND/BACKEND DRONES (3 agents) - Week 8-9
    # ========================================================================

    "frontend-dev": AgentCapabilities(
        keywords=["frontend", "ui", "react", "component", "interface"],
        task_types=["frontend", "ui"],
        loop="loop2",
        description="Develops frontend UI components (React, Next.js, etc.)"
    ),

    "backend-dev": AgentCapabilities(
        keywords=["backend", "api", "server", "endpoint", "database"],
        task_types=["backend", "api"],
        loop="loop2",
        description="Develops backend APIs and server logic"
    ),

    "code-analyzer": AgentCapabilities(
        keywords=["analyze", "static", "ast", "parse", "inspect"],
        task_types=["analysis", "inspection"],
        loop="loop3",
        description="Performs static code analysis and AST inspection"
    ),

    # ========================================================================
    # INFRASTRUCTURE DRONES (3 agents) - Week 9
    # ========================================================================

    "infrastructure-ops": AgentCapabilities(
        keywords=["infrastructure", "k8s", "terraform", "cloud", "provision"],
        task_types=["infrastructure", "provisioning"],
        loop="loop3",
        description="Manages infrastructure and cloud provisioning"
    ),

    "release-manager": AgentCapabilities(
        keywords=["release", "version", "changelog", "tag", "publish"],
        task_types=["release", "publishing"],
        loop="loop3",
        description="Coordinates releases and versioning"
    ),

    "performance-engineer": AgentCapabilities(
        keywords=["performance", "optimize", "profile", "benchmark", "speed"],
        task_types=["performance", "optimization"],
        loop="loop3",
        description="Optimizes performance and conducts benchmarks"
    ),
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_drones() -> List[str]:
    """Get list of all Drone agent IDs (excludes Queen and Princesses)."""
    return [
        agent_id for agent_id in AGENT_REGISTRY.keys()
        if not agent_id.startswith("queen") and not agent_id.startswith("princess")
    ]


def get_drones_for_loop(loop: str) -> List[str]:
    """Get all Drones available for a specific loop."""
    return [
        agent_id for agent_id, caps in AGENT_REGISTRY.items()
        if (caps.loop == loop or caps.loop == "all")
        and not agent_id.startswith("queen")
        and not agent_id.startswith("princess")
    ]


def find_drones_for_task(task_description: str, loop: str) -> List[str]:
    """
    Find the best Drone agents for a given task.

    This is the core logic Princesses use to choose Drones.

    Args:
        task_description: User's task description
        loop: Current loop (loop1/loop2/loop3)

    Returns:
        List of Drone agent IDs that match the task
    """
    task_lower = task_description.lower()
    matching_drones = []

    # Get all drones available for this loop
    available_drones = get_drones_for_loop(loop)

    # Score each drone based on keyword matches
    drone_scores = {}
    for drone_id in available_drones:
        caps = AGENT_REGISTRY[drone_id]
        score = 0

        # Check keyword matches
        for keyword in caps.keywords:
            if keyword in task_lower:
                score += 2  # High priority for keyword match

        # Check task type matches
        for task_type in caps.task_types:
            if task_type in task_lower:
                score += 1  # Medium priority for task type match

        if score > 0:
            drone_scores[drone_id] = score

    # Sort by score and return top matches
    sorted_drones = sorted(drone_scores.items(), key=lambda x: x[1], reverse=True)

    # Return top 5 matches (or fewer if not enough)
    return [drone_id for drone_id, score in sorted_drones[:5]]


def get_drone_description(agent_id: str) -> str:
    """Get human-readable description of a Drone agent."""
    if agent_id in AGENT_REGISTRY:
        return AGENT_REGISTRY[agent_id].description
    return f"Unknown agent: {agent_id}"


def get_princess_for_loop(loop: str) -> str:
    """Get the Princess agent ID for a given loop."""
    if loop == "loop1":
        return "princess-coordination"
    elif loop == "loop2":
        return "princess-dev"
    elif loop == "loop3":
        return "princess-quality"
    else:
        return "princess-dev"  # Default


def get_default_drones_for_princess(princess_id: str) -> List[str]:
    """Get default Drones that a Princess typically spawns."""
    defaults = {
        "princess-dev": ["coder", "tester", "reviewer"],
        "princess-coordination": ["researcher", "spec-writer", "architect"],
        "princess-quality": ["theater-detector", "nasa-enforcer", "docs-writer"]
    }
    return defaults.get(princess_id, [])


# ============================================================================
# AGENT SUMMARY
# ============================================================================

def print_agent_summary():
    """Print summary of all agents (for debugging)."""
    print("\n" + "="*60)
    print("SPEK PLATFORM - AGENT REGISTRY")
    print("="*60)

    print(f"\nTotal Agents: {len(AGENT_REGISTRY)}")

    queen = [a for a in AGENT_REGISTRY if a.startswith("queen")]
    princesses = [a for a in AGENT_REGISTRY if a.startswith("princess")]
    drones = get_all_drones()

    print(f"  Queen: {len(queen)}")
    print(f"  Princesses: {len(princesses)}")
    print(f"  Drones: {len(drones)}")

    print("\n" + "-"*60)
    print("LOOP 1 (Research & Planning) - Drones:")
    print("-"*60)
    for drone in get_drones_for_loop("loop1"):
        print(f"  • {drone}: {AGENT_REGISTRY[drone].description}")

    print("\n" + "-"*60)
    print("LOOP 2 (Development & Implementation) - Drones:")
    print("-"*60)
    for drone in get_drones_for_loop("loop2"):
        print(f"  • {drone}: {AGENT_REGISTRY[drone].description}")

    print("\n" + "-"*60)
    print("LOOP 3 (Quality & Finalization) - Drones:")
    print("-"*60)
    for drone in get_drones_for_loop("loop3"):
        print(f"  • {drone}: {AGENT_REGISTRY[drone].description}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Test the agent registry
    print_agent_summary()

    # Test drone selection
    print("\n" + "="*60)
    print("TESTING DRONE SELECTION")
    print("="*60)

    test_tasks = [
        ("Create a Python web app", "loop2"),
        ("Research best practices for REST APIs", "loop1"),
        ("Audit the code for security issues", "loop3"),
        ("Fix the bug in the authentication module", "loop2"),
        ("Write documentation for the API", "loop3")
    ]

    for task_desc, loop in test_tasks:
        print(f"\nTask: '{task_desc}' (in {loop})")
        drones = find_drones_for_task(task_desc, loop)
        print(f"  Recommended Drones:")
        for drone in drones:
            print(f"    - {drone}: {get_drone_description(drone)}")

    print("\n" + "="*60 + "\n")
