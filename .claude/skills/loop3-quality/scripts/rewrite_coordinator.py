#!/usr/bin/env python3
"""
Rewrite Coordinator - Coordinates rewrites based on audit failures

Atomic skill helper for Loop 3 Quality phase.
Analyzes failures and spawns appropriate Drones for fixes.

VERSION: 1.0.0
USAGE: python rewrite_coordinator.py --audit-results results.json
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class RewriteCoordinator:
    """Coordinates code rewrites based on audit failures."""

    # Failure to Drone mappings
    FAILURE_DRONE_MAP = {
        "functionality": ["debugger", "coder", "tester"],
        "style": ["reviewer", "coder"],
        "theater": ["coder", "reviewer"],
        "security": ["security-manager", "coder"],
        "performance": ["performance-engineer", "coder"]
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize rewrite coordinator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.rewrite_dir = self.project_root / ".claude" / "rewrites"
        self.rewrite_dir.mkdir(parents=True, exist_ok=True)

    def analyze_failures(
        self, audit_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze audit failures.

        Args:
            audit_results: Audit results from audit_runner

        Returns:
            Dict with failure analysis
        """
        try:
            failures = []

            for audit_type, audit_data in audit_results.get("audits", {}).items():
                if not audit_data.get("passed", False):
                    failures.append({
                        "type": audit_type,
                        "data": audit_data,
                        "severity": self._assess_severity(audit_type, audit_data)
                    })

            return {
                "success": True,
                "failures": failures,
                "failure_count": len(failures),
                "requires_rewrites": len(failures) > 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def select_drones_for_fixes(
        self, failures: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select appropriate Drones for fixes.

        Args:
            failures: List of failure dictionaries

        Returns:
            Dict with Drone selections
        """
        try:
            drone_assignments = []

            for failure in failures:
                failure_type = failure.get("type")
                drones = self.FAILURE_DRONE_MAP.get(failure_type, ["coder"])

                assignment = {
                    "failure_type": failure_type,
                    "severity": failure.get("severity"),
                    "primary_drone": drones[0],
                    "backup_drones": drones[1:] if len(drones) > 1 else [],
                    "estimated_hours": self._estimate_fix_time(failure)
                }

                drone_assignments.append(assignment)

            return {
                "success": True,
                "assignments": drone_assignments,
                "total_assignments": len(drone_assignments)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_rewrite_tasks(
        self, assignments: List[Dict[str, Any]], failures: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create rewrite task instructions.

        Args:
            assignments: Drone assignments
            failures: Failure details

        Returns:
            Dict with task instructions
        """
        try:
            tasks = []

            for i, (assignment, failure) in enumerate(zip(assignments, failures), 1):
                task = {
                    "task_id": f"rewrite_{i}",
                    "drone": assignment["primary_drone"],
                    "failure_type": assignment["failure_type"],
                    "severity": assignment["severity"],
                    "instruction": self._generate_instruction(assignment, failure),
                    "estimated_hours": assignment["estimated_hours"]
                }

                tasks.append(task)

            # Save tasks
            tasks_file = self.rewrite_dir / "rewrite_tasks.json"
            tasks_file.write_text(
                json.dumps({"tasks": tasks, "timestamp": datetime.now().isoformat()}, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "tasks": tasks,
                "tasks_file": str(tasks_file),
                "total_tasks": len(tasks)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def coordinate_rewrites(
        self, audit_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete rewrite coordination workflow.

        Args:
            audit_results: Audit results

        Returns:
            Dict with coordination results
        """
        # Step 1: Analyze failures
        analysis = self.analyze_failures(audit_results)
        if not analysis["success"]:
            return analysis

        if not analysis["requires_rewrites"]:
            return {
                "success": True,
                "message": "No rewrites needed - all audits passed",
                "requires_action": False
            }

        # Step 2: Select Drones
        selection = self.select_drones_for_fixes(analysis["failures"])
        if not selection["success"]:
            return selection

        # Step 3: Create tasks
        tasks = self.create_rewrite_tasks(
            selection["assignments"],
            analysis["failures"]
        )

        return {
            "success": True,
            "coordination": {
                "failure_analysis": analysis,
                "drone_selection": selection,
                "rewrite_tasks": tasks
            },
            "requires_action": True,
            "message": f"{len(tasks['tasks'])} rewrite tasks created"
        }

    def _assess_severity(
        self, audit_type: str, audit_data: Dict[str, Any]
    ) -> str:
        """Assess failure severity."""
        if audit_type == "functionality":
            return "critical"
        elif audit_type == "security":
            return "high"
        elif audit_type in ["style", "theater"]:
            return "medium"
        else:
            return "low"

    def _estimate_fix_time(self, failure: Dict[str, Any]) -> int:
        """Estimate time to fix (hours)."""
        severity = failure.get("severity")

        if severity == "critical":
            return 8
        elif severity == "high":
            return 4
        elif severity == "medium":
            return 2
        else:
            return 1

    def _generate_instruction(
        self, assignment: Dict[str, Any], failure: Dict[str, Any]
    ) -> str:
        """Generate Drone instruction for rewrite."""
        return f"""You are {assignment['primary_drone'].upper()} for SPEK Platform Loop 3 Rewrites.

TASK: Fix {assignment['failure_type']} audit failure

SEVERITY: {assignment['severity']}

FAILURE DETAILS:
{json.dumps(failure.get('data'), indent=2)}

YOUR ACTIONS:
1. Analyze the failure root cause
2. Implement fixes following SPEK standards
3. Run local validation (tests, linting)
4. Document changes made
5. Report completion with validation results

STANDARDS:
- NASA Rule 10 compliance (≤60 LOC per function)
- 100% type hints coverage
- Comprehensive error handling
- Unit tests for all changes

ESTIMATED TIME: {assignment['estimated_hours']} hours

Begin rewrite now."""


if __name__ == "__main__":
    # Example usage
    coordinator = RewriteCoordinator()

    # Example audit results with failures
    audit_results = {
        "all_passed": False,
        "audits": {
            "functionality": {
                "passed": False,
                "results": {"test_results": {"success": False}}
            },
            "style": {
                "passed": False,
                "results": {"nasa_compliance": {"passed": False, "violations": 3}}
            },
            "theater": {
                "passed": True,
                "score": 20
            }
        }
    }

    result = coordinator.coordinate_rewrites(audit_results)
    print(json.dumps(result, indent=2))
