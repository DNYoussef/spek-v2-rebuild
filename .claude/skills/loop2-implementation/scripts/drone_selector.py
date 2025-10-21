#!/usr/bin/env python3
"""
Drone Selector - Wraps agent registry drone selection logic

Atomic skill helper for Loop 2 Implementation phase.
Interfaces with agent_registry.py for intelligent Drone selection.

VERSION: 1.0.0
USAGE: python drone_selector.py --task "implement feature" --count 3
"""

import json
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))


class DroneSelector:
    """Selects appropriate Drone agents for tasks."""

    # Drone capability mappings (mirrors agent_registry.py)
    DRONE_CAPABILITIES = {
        "coder": {"keywords": ["implement", "code", "write", "build"], "priority": 1},
        "tester": {"keywords": ["test", "verify", "validate", "check"], "priority": 2},
        "reviewer": {"keywords": ["review", "audit", "inspect", "analyze"], "priority": 2},
        "architect": {"keywords": ["design", "architecture", "structure", "plan"], "priority": 1},
        "debugger": {"keywords": ["debug", "fix", "error", "bug"], "priority": 1},
        "frontend-dev": {"keywords": ["ui", "frontend", "component", "react"], "priority": 2},
        "backend-dev": {"keywords": ["api", "backend", "server", "database"], "priority": 2},
        "devops": {"keywords": ["deploy", "docker", "kubernetes", "ci/cd"], "priority": 3},
        "security-manager": {"keywords": ["security", "auth", "encrypt", "vulnerability"], "priority": 2},
        "docs-writer": {"keywords": ["document", "docs", "readme", "guide"], "priority": 3},
        "integration-engineer": {"keywords": ["integrate", "merge", "combine", "connect"], "priority": 2}
    }

    def __init__(self):
        """Initialize Drone selector."""
        self.project_root = project_root

    def find_drones_for_task(
        self, task: str, max_drones: int = 3
    ) -> Dict[str, Any]:
        """
        Find appropriate Drones for task.

        Args:
            task: Task description
            max_drones: Maximum number of Drones to return

        Returns:
            Dict with selected Drones
        """
        try:
            # Score drones based on keyword matching
            scores = {}
            keywords = task.lower().split()

            for drone, info in self.DRONE_CAPABILITIES.items():
                score = 0
                for keyword in keywords:
                    if any(cap in keyword for cap in info["keywords"]):
                        score += 10
                # Apply priority boost
                score += (4 - info["priority"]) * 2
                scores[drone] = score

            # Sort by score and return top N
            sorted_drones = sorted(
                scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            selected = [
                {
                    "drone": drone,
                    "score": score,
                    "capabilities": self.DRONE_CAPABILITIES[drone]["keywords"]
                }
                for drone, score in sorted_drones[:max_drones]
                if score > 0
            ]

            return {
                "success": True,
                "task": task,
                "drones": selected,
                "count": len(selected)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_drone_info(self, drone_name: str) -> Dict[str, Any]:
        """
        Get information about specific Drone.

        Args:
            drone_name: Drone agent name

        Returns:
            Dict with Drone information
        """
        try:
            if drone_name not in self.DRONE_CAPABILITIES:
                return {
                    "success": False,
                    "error": f"Drone {drone_name} not found"
                }

            info = self.DRONE_CAPABILITIES[drone_name]

            return {
                "success": True,
                "drone": drone_name,
                "capabilities": info["keywords"],
                "priority": info["priority"],
                "description": self._get_drone_description(drone_name)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def recommend_drones_for_subtasks(
        self, subtasks: List[str]
    ) -> Dict[str, Any]:
        """
        Recommend Drones for multiple subtasks.

        Args:
            subtasks: List of subtask descriptions

        Returns:
            Dict with recommendations
        """
        try:
            recommendations = []

            for subtask in subtasks:
                result = self.find_drones_for_task(subtask, max_drones=2)
                if result["success"] and result["drones"]:
                    recommendations.append({
                        "subtask": subtask,
                        "recommended_drone": result["drones"][0]["drone"],
                        "alternatives": [d["drone"] for d in result["drones"][1:]]
                    })

            return {
                "success": True,
                "recommendations": recommendations,
                "total_subtasks": len(subtasks)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_drone_description(self, drone_name: str) -> str:
        """Get human-readable Drone description."""
        descriptions = {
            "coder": "Implements code and features",
            "tester": "Creates and runs tests",
            "reviewer": "Reviews code quality",
            "architect": "Designs system architecture",
            "debugger": "Debugs and fixes issues",
            "frontend-dev": "Develops frontend/UI",
            "backend-dev": "Develops backend/API",
            "devops": "Handles deployment and infrastructure",
            "security-manager": "Manages security concerns",
            "docs-writer": "Writes documentation",
            "integration-engineer": "Integrates system components"
        }
        return descriptions.get(drone_name, "Specialized agent")


if __name__ == "__main__":
    # Example usage
    selector = DroneSelector()

    # Example 1: Find drones for single task
    result1 = selector.find_drones_for_task(
        "Implement REST API with authentication",
        max_drones=3
    )
    print("Single task:")
    print(json.dumps(result1, indent=2))

    # Example 2: Get specific drone info
    result2 = selector.get_drone_info("backend-dev")
    print("\nDrone info:")
    print(json.dumps(result2, indent=2))

    # Example 3: Recommend for multiple subtasks
    result3 = selector.recommend_drones_for_subtasks([
        "Design database schema",
        "Implement API endpoints",
        "Write integration tests",
        "Deploy to staging"
    ])
    print("\nSubtask recommendations:")
    print(json.dumps(result3, indent=2))
