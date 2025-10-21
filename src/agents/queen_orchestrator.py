"""
Queen Orchestrator - CORRECTED VERSION

This Claude Code instance acts as the Queen agent.
When messages arrive from the UI, Queen:
1. Analyzes the request
2. Determines which Princess to spawn
3. Provides Princess with list of Drones to spawn (chosen from our 28 agents)
4. Princess uses Task tool to spawn those specific Drones
5. Drones work and report back

IMPORTANT: Princesses choose Drones from our agent registry, not arbitrary agents!

Version: 8.2.0 (Week 26 - Corrected)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.coordination.agent_registry import (
    find_drones_for_task,
    get_drone_description,
    get_princess_for_loop,
    get_default_drones_for_princess,
    AGENT_REGISTRY
)


class QueenOrchestrator:
    """
    Queen Agent - Top-level coordinator.

    This is Claude Code acting as Queen.
    It receives requests from UI and delegates to Princess agents.
    """

    def __init__(self, project_context: Dict[str, Any]):
        self.project_context = project_context
        self.flask_url = "http://localhost:5000"
        self.active_agents = []
        self.current_loop = None

        print(f"👑 Queen initialized")
        print(f"   Project: {project_context.get('name', 'None')}")
        print(f"   Type: {project_context.get('type', 'unknown')}")

    def process_request(self, user_message: str, task_id: str) -> Dict[str, Any]:
        """
        Main entry point - process user request.

        Steps:
        1. Analyze request (what does user want?)
        2. Determine which loop (1/2/3)
        3. Choose which Princess to spawn
        4. Find appropriate Drones from our agent registry
        5. Create detailed Princess prompt with Drone list
        6. Return Task tool instructions
        """
        print(f"\n👑 Queen analyzing request...")
        print(f"   Message: {user_message}")

        # Step 1: Analyze the request
        analysis = self.analyze_request(user_message)

        print(f"\n📊 Analysis complete:")
        print(f"   Loop: {analysis['loop']}")
        print(f"   Intent: {analysis['intent']}")
        print(f"   Princess needed: {analysis['princess']}")

        # Step 2: Find appropriate Drones from registry
        recommended_drones = find_drones_for_task(user_message, analysis['loop'])

        # If no drones found by keywords, use defaults for this Princess
        if not recommended_drones:
            recommended_drones = get_default_drones_for_princess(analysis['princess'])

        print(f"   Recommended Drones: {recommended_drones}")

        # Step 3: Create Princess prompt with Drone instructions
        princess_prompt = self.create_princess_prompt(
            princess_type=analysis['princess'],
            task_description=user_message,
            loop=analysis['loop'],
            recommended_drones=recommended_drones
        )

        # Step 4: Broadcast agent spawn to UI
        self.broadcast_agent_spawned(analysis['princess'], task_id, analysis['loop'])

        return {
            "response": self.generate_user_response(
                analysis['princess'],
                analysis['loop'],
                user_message,
                recommended_drones
            ),
            "agents_spawned": [analysis['princess']],
            "recommended_drones": recommended_drones,
            "loop": analysis['loop'],
            "princess_prompt": princess_prompt,
            "task_tool_instructions": self.generate_task_tool_instructions(
                analysis['princess'],
                princess_prompt
            )
        }

    def analyze_request(self, user_message: str) -> Dict[str, Any]:
        """
        Analyze user request to determine:
        - Which loop (1/2/3)?
        - Which Princess to delegate to?
        - What is the intent?
        """
        message_lower = user_message.lower()

        # Loop 1 keywords: research, plan, analyze, design, architecture
        if any(word in message_lower for word in ['research', 'plan', 'analyze', 'design', 'architecture', 'spec', 'requirements']):
            return {
                'loop': 'loop1',
                'princess': 'princess-coordination',
                'intent': 'Research & Planning'
            }

        # Loop 3 keywords: test, review, quality, audit, document
        elif any(word in message_lower for word in ['test', 'review', 'quality', 'audit', 'document', 'documentation', 'finalize']):
            return {
                'loop': 'loop3',
                'princess': 'princess-quality',
                'intent': 'Quality & Finalization'
            }

        # Default to Loop 2 (execution)
        else:
            return {
                'loop': 'loop2',
                'princess': 'princess-dev',
                'intent': 'Development & Implementation'
            }

    def delegate_to_princess(
        self,
        princess_type: str,
        loop: str,
        task_description: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Delegate task to a Princess agent.

        This is where we use the Task tool to spawn a new Claude Code instance.

        IMPORTANT: We don't call Task tool directly here - we document that
        THIS Claude Code instance (Queen) should use the Task tool UI feature
        to spawn the Princess agent.
        """
        # Broadcast agent spawn to UI
        self.broadcast_agent_spawned(princess_type, task_id, loop)

        # Prepare detailed instructions for the Princess
        princess_prompt = self.create_princess_prompt(
            princess_type=princess_type,
            task_description=task_description,
            loop=loop
        )

        print(f"\n🔮 Delegating to {princess_type}...")
        print(f"   Loop: {loop}")
        print(f"   Task: {task_description[:100]}...")

        # NOTE: At this point, Claude Code (Queen) should use the Task tool
        # to spawn a new Claude Code instance as the Princess.
        #
        # Since we can't programmatically invoke Task tool from Python,
        # we return instructions for the human operator or automation system.

        return {
            "response": self.generate_user_response(princess_type, loop, task_description),
            "agents_spawned": [princess_type],
            "loop": loop,
            "princess_prompt": princess_prompt,
            "instructions_for_claude": self.generate_task_tool_instructions(princess_type, princess_prompt)
        }

    def create_princess_prompt(
        self,
        princess_type: str,
        task_description: str,
        loop: str,
        recommended_drones: List[str] = None
    ) -> str:
        """
        Create detailed prompt for Princess agent.

        This prompt will be used when spawning the Princess via Task tool.
        """
        # Handle existing project with file list (no folder_path due to browser security)
        folder_info = self.project_context.get('folder_path')
        if not folder_info and self.project_context.get('type') == 'existing':
            folder_name = self.project_context.get('folder_name', 'Unknown')
            file_count = self.project_context.get('file_count', 0)
            folder_info = f"{folder_name} ({file_count} files - reading from original location)"

        project_info = f"""
Project Context:
- Name: {self.project_context.get('name', 'Unknown')}
- Type: {self.project_context.get('type', 'unknown')}
- Folder: {folder_info or 'N/A'}
- Note: For existing projects, we read from ORIGINAL location (no copying)
"""

        # Add recommended drones if provided
        drone_section = ""
        if recommended_drones:
            drone_list = "\n".join([f"  - {drone}: {get_drone_description(drone)}" for drone in recommended_drones])
            drone_section = f"""
Recommended Drone Agents (from our 28-agent registry):
{drone_list}

Use Task tool to spawn these specific Drones for this task.
"""

        if princess_type == "princess-dev":
            return f"""
You are Princess-Dev, a development coordination agent in the SPEK Platform.

{project_info}

Current Loop: {loop} (Development & Implementation)

User Request:
{task_description}

{drone_section}

Your Responsibilities:
1. Break down the task into concrete implementation steps
2. Spawn Drone agents from recommended list using Task tool
3. Coordinate their work
4. Ensure code quality (NASA Rule 10: ≤60 LOC per function)
5. Report progress back to Queen

Process:
1. Analyze the request
2. Spawn appropriate Drones from recommended list
3. Coordinate their work
4. Aggregate results
5. Report to Queen via Flask endpoint

Use Task tool to spawn each Drone agent with specific instructions.
"""

        elif princess_type == "princess-coordination":
            return f"""
You are Princess-Coordination, a research & planning coordination agent in the SPEK Platform.

{project_info}

Current Loop: {loop} (Research & Planning)

User Request:
{task_description}

{drone_section}

Your Responsibilities:
1. Research the problem domain
2. Spawn Drone agents from recommended list using Task tool
3. Gather artifacts
4. Create comprehensive plan
5. Report findings back to Queen

Process:
1. Analyze requirements
2. Spawn appropriate Drones from recommended list
3. Coordinate research and planning
4. Aggregate artifacts
5. Report to Queen via Flask endpoint

Use Task tool to spawn each Drone agent with specific instructions.
"""

        elif princess_type == "princess-quality":
            return f"""
You are Princess-Quality, a quality assurance coordination agent in the SPEK Platform.

{project_info}

Current Loop: {loop} (Quality & Finalization)

User Request:
{task_description}

{drone_section}

Your Responsibilities:
1. Audit all code and documentation
2. Spawn Drone agents from recommended list using Task tool
3. Ensure quality gates are met
4. Finalize deliverables
5. Report status back to Queen

Process:
1. Analyze quality requirements
2. Spawn appropriate Drones from recommended list
3. Coordinate quality assurance
4. Aggregate quality reports
5. Report to Queen via Flask endpoint

Use Task tool to spawn each Drone agent with specific instructions.
"""

        else:
            return f"Unknown princess type: {princess_type}"

    def generate_task_tool_instructions(self, princess_type: str, princess_prompt: str) -> str:
        """
        Generate instructions for using Task tool to spawn Princess.

        This is what the human operator (or automation) should do.
        """
        return f"""
CLAUDE CODE TASK TOOL INSTRUCTIONS:

Use the Task tool to spawn {princess_type}:

Tool: Task
Parameters:
  - subagent_type: "{princess_type}"
  - description: "Coordinate {princess_type} workflow"
  - prompt: '''
{princess_prompt}
'''

The spawned Princess will then use Task tool to spawn Drone agents.
"""

    def generate_user_response(
        self,
        princess_type: str,
        loop: str,
        task_description: str,
        recommended_drones: List[str] = None
    ) -> str:
        """Generate user-friendly response for the UI."""
        princess_names = {
            "princess-dev": "Princess Dev",
            "princess-coordination": "Princess Coordination",
            "princess-quality": "Princess Quality"
        }

        princess_name = princess_names.get(princess_type, princess_type)

        drone_info = ""
        if recommended_drones:
            drone_names = ", ".join(recommended_drones)
            drone_info = f"\n\n🐝 **Recommended Drones**: {drone_names}"

        return f"""
👑 **Queen here!** I've analyzed your request.

📋 **Task**: {task_description[:100]}{'...' if len(task_description) > 100 else ''}

🔮 **Action**: Delegating to **{princess_name}** for {loop} workflow.{drone_info}

The Princess will spawn specialized Drone agents from our 28-agent registry to handle this task. You'll see their activity in the sidebar!

⏳ Processing... (this may take a moment)
"""

    def broadcast_agent_spawned(self, agent_id: str, task_id: str, loop: str):
        """Broadcast agent spawn event to UI via WebSocket."""
        try:
            url = f"{self.flask_url}/api/claude/agent-spawned"
            data = {
                "agentId": agent_id,
                "taskId": task_id,
                "loop": loop,
                "timestamp": datetime.now().isoformat(),
                "status": "spawned"
            }

            requests.post(url, json=data, timeout=2)
            print(f"✅ Broadcasted: {agent_id} spawned")

        except Exception as e:
            print(f"⚠️  Could not broadcast spawn: {e}")


# ============================================================================
# Helper Functions for Princess Agents
# ============================================================================

def princess_dev_workflow(task_description: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Princess-Dev workflow implementation.

    This function would be used by a Princess-Dev Claude Code instance.
    """
    print(f"\n💎 Princess-Dev activated")
    print(f"   Task: {task_description}")

    # Step 1: Analyze task
    steps = [
        "Understand requirements",
        "Design solution",
        "Write code",
        "Write tests",
        "Review code"
    ]

    # Step 2: Spawn Drones (using Task tool)
    drones_to_spawn = [
        ("coder", "Write implementation code"),
        ("tester", "Write comprehensive tests"),
        ("reviewer", "Review code quality")
    ]

    print(f"\n💎 Princess-Dev will spawn {len(drones_to_spawn)} Drones:")
    for drone_type, drone_task in drones_to_spawn:
        print(f"   - {drone_type}: {drone_task}")

    return {
        "success": True,
        "princess": "princess-dev",
        "drones_spawned": [d[0] for d in drones_to_spawn],
        "status": "in_progress"
    }


def princess_coordination_workflow(task_description: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Princess-Coordination workflow implementation.

    This function would be used by a Princess-Coordination Claude Code instance.
    """
    print(f"\n🔮 Princess-Coordination activated")
    print(f"   Task: {task_description}")

    drones_to_spawn = [
        ("researcher", "Research problem domain"),
        ("spec-writer", "Write technical specification"),
        ("architect", "Design system architecture")
    ]

    print(f"\n🔮 Princess-Coordination will spawn {len(drones_to_spawn)} Drones:")
    for drone_type, drone_task in drones_to_spawn:
        print(f"   - {drone_type}: {drone_task}")

    return {
        "success": True,
        "princess": "princess-coordination",
        "drones_spawned": [d[0] for d in drones_to_spawn],
        "status": "in_progress"
    }


def princess_quality_workflow(task_description: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Princess-Quality workflow implementation.

    This function would be used by a Princess-Quality Claude Code instance.
    """
    print(f"\n✨ Princess-Quality activated")
    print(f"   Task: {task_description}")

    drones_to_spawn = [
        ("theater-detector", "Scan for mock code"),
        ("nasa-enforcer", "Validate NASA Rule 10"),
        ("docs-writer", "Generate documentation")
    ]

    print(f"\n✨ Princess-Quality will spawn {len(drones_to_spawn)} Drones:")
    for drone_type, drone_task in drones_to_spawn:
        print(f"   - {drone_type}: {drone_task}")

    return {
        "success": True,
        "princess": "princess-quality",
        "drones_spawned": [d[0] for d in drones_to_spawn],
        "status": "in_progress"
    }
