#!/usr/bin/env python3
"""
Princess Spawner - Princess selection and spawning logic

Atomic skill helper for Loop 2 Implementation phase.
Handles Princess agent selection and Task tool spawning.

VERSION: 1.0.0
USAGE: python princess_spawner.py --task "coordinate development"
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class PrincessSpawner:
    """Handles Princess agent selection and spawning."""

    PRINCESS_CAPABILITIES = {
        "princess-dev": {
            "domains": ["coding", "implementation", "development", "feature"],
            "drones": ["coder", "frontend-dev", "backend-dev", "architect"],
            "description": "Coordinates development work"
        },
        "princess-quality": {
            "domains": ["testing", "review", "quality", "validation"],
            "drones": ["tester", "reviewer", "debugger", "security-manager"],
            "description": "Coordinates quality assurance"
        },
        "princess-coordination": {
            "domains": ["planning", "coordination", "integration", "deployment"],
            "drones": ["integration-engineer", "devops", "planner", "orchestrator"],
            "description": "Coordinates system integration"
        }
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Princess spawner.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.spawn_dir = self.project_root / ".claude" / "spawns"
        self.spawn_dir.mkdir(parents=True, exist_ok=True)

    def select_princess(
        self, task: str, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select appropriate Princess for task.

        Args:
            task: Task description
            domain: Optional domain hint

        Returns:
            Dict with Princess selection
        """
        try:
            keywords = task.lower().split()

            # Score each Princess
            scores = {}
            for princess, info in self.PRINCESS_CAPABILITIES.items():
                score = 0
                for keyword in keywords:
                    if any(d in keyword for d in info["domains"]):
                        score += 1
                scores[princess] = score

            # Select highest scoring Princess
            selected = max(scores, key=scores.get)

            if scores[selected] == 0:
                selected = "princess-dev"  # Default

            return {
                "success": True,
                "princess": selected,
                "capabilities": self.PRINCESS_CAPABILITIES[selected],
                "selection_score": scores[selected],
                "rationale": f"Best match for task domain"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_spawn_instruction(
        self, princess: str, task: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create spawn instruction for Princess.

        Args:
            princess: Princess name
            task: Task description
            context: Additional context

        Returns:
            Dict with spawn instruction
        """
        try:
            capabilities = self.PRINCESS_CAPABILITIES.get(princess, {})

            instruction = f"""You are {princess.upper()} for SPEK Platform.

TASK: {task}

YOUR CAPABILITIES:
- Domains: {', '.join(capabilities.get('domains', []))}
- Available Drones: {', '.join(capabilities.get('drones', []))}
- Role: {capabilities.get('description', 'Coordinate work')}

CONTEXT:
{json.dumps(context, indent=2)}

YOUR WORKFLOW:
1. Analyze the task and break into subtasks
2. Select appropriate Drones using drone_selector.py
3. Spawn Drones using Task tool with specific instructions
4. Monitor progress and coordinate between Drones
5. Aggregate results and report back to Queen

COORDINATION RULES:
- Write progress to: {self.spawn_dir}/{princess}_progress.json
- Update status every 15 minutes
- Escalate blockers immediately
- Complete all subtasks before reporting done

Begin coordination now."""

            return {
                "success": True,
                "instruction": instruction,
                "princess": princess,
                "capabilities": capabilities
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def spawn_princess(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete Princess spawning workflow.

        Args:
            task: Task description
            context: Optional additional context

        Returns:
            Dict with spawn result
        """
        # Step 1: Select Princess
        selection = self.select_princess(task)
        if not selection["success"]:
            return selection

        # Step 2: Create spawn instruction
        instruction_result = self.create_spawn_instruction(
            selection["princess"],
            task,
            context or {}
        )

        if not instruction_result["success"]:
            return instruction_result

        # Step 3: Record spawn
        spawn_record = {
            "timestamp": datetime.now().isoformat(),
            "princess": selection["princess"],
            "task": task,
            "context": context or {},
            "status": "spawned"
        }

        record_file = self.spawn_dir / f"{selection['princess']}_spawn.json"
        record_file.write_text(
            json.dumps(spawn_record, indent=2),
            encoding="utf-8"
        )

        return {
            "success": True,
            "princess": selection["princess"],
            "instruction": instruction_result["instruction"],
            "capabilities": selection["capabilities"],
            "record_file": str(record_file),
            "message": f"Princess {selection['princess']} spawned for task"
        }

    def get_princess_status(self, princess: str) -> Dict[str, Any]:
        """
        Get Princess status from progress file.

        Args:
            princess: Princess name

        Returns:
            Dict with status
        """
        try:
            progress_file = self.spawn_dir / f"{princess}_progress.json"

            if not progress_file.exists():
                return {
                    "success": True,
                    "princess": princess,
                    "status": "not_found",
                    "message": "No progress file found"
                }

            progress = json.loads(progress_file.read_text(encoding="utf-8"))

            return {
                "success": True,
                "princess": princess,
                "status": "active",
                "progress": progress
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Example usage
    spawner = PrincessSpawner()

    result = spawner.spawn_princess(
        task="Implement authentication system",
        context={
            "requirements": ["JWT tokens", "OAuth2", "Role-based access"],
            "priority": "high"
        }
    )

    print(json.dumps(result, indent=2))
