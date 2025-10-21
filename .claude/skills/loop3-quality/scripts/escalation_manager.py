#!/usr/bin/env python3
"""
Escalation Manager - Manages Loop 3 → Loop 1 escalations

Atomic skill helper for Loop 3 Quality phase.
Handles critical failures requiring Loop 1 re-planning.

VERSION: 1.0.0
USAGE: python escalation_manager.py --failure-data failures.json
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class EscalationManager:
    """Manages escalations from Loop 3 back to Loop 1."""

    # Escalation triggers
    ESCALATION_TRIGGERS = {
        "quality_gate_critical_failure": {
            "threshold": 50,  # <50% quality score
            "severity": "critical"
        },
        "security_vulnerabilities": {
            "threshold": 1,  # ≥1 critical vulnerability
            "severity": "critical"
        },
        "architecture_issues": {
            "threshold": 3,  # ≥3 major architecture issues
            "severity": "high"
        },
        "performance_failures": {
            "threshold": 5,  # ≥5 performance regressions
            "severity": "high"
        },
        "test_failures_persistent": {
            "threshold": 10,  # ≥10% tests failing after rewrites
            "severity": "medium"
        }
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize escalation manager.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.escalation_dir = self.project_root / ".claude" / "escalations"
        self.escalation_dir.mkdir(parents=True, exist_ok=True)

    def check_escalation_triggers(
        self, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if escalation triggers are met.

        Args:
            validation_data: Validation results

        Returns:
            Dict with trigger analysis
        """
        try:
            triggered = []

            # Check quality gate
            quality_score = validation_data.get("quality_gate", {}).get("percentage", 100)
            if quality_score < self.ESCALATION_TRIGGERS["quality_gate_critical_failure"]["threshold"]:
                triggered.append({
                    "trigger": "quality_gate_critical_failure",
                    "severity": "critical",
                    "value": quality_score,
                    "threshold": 50
                })

            # Check security
            security = validation_data.get("security", {})
            critical_vulns = security.get("critical_issues", 0)
            if critical_vulns >= self.ESCALATION_TRIGGERS["security_vulnerabilities"]["threshold"]:
                triggered.append({
                    "trigger": "security_vulnerabilities",
                    "severity": "critical",
                    "value": critical_vulns,
                    "threshold": 1
                })

            # Check test failures
            tests = validation_data.get("tests", {})
            failure_rate = tests.get("failure_rate", 0)
            if failure_rate >= self.ESCALATION_TRIGGERS["test_failures_persistent"]["threshold"]:
                triggered.append({
                    "trigger": "test_failures_persistent",
                    "severity": "medium",
                    "value": failure_rate,
                    "threshold": 10
                })

            requires_escalation = any(
                t["severity"] == "critical" for t in triggered
            )

            return {
                "success": True,
                "requires_escalation": requires_escalation,
                "triggers": triggered,
                "trigger_count": len(triggered)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_escalation_context(
        self, triggers: List[Dict[str, Any]], validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create escalation context for Loop 1.

        Args:
            triggers: Triggered escalations
            validation_data: Full validation data

        Returns:
            Dict with escalation context
        """
        try:
            context = {
                "escalation_id": self._generate_escalation_id(),
                "timestamp": datetime.now().isoformat(),
                "from_loop": 3,
                "to_loop": 1,
                "severity": self._assess_overall_severity(triggers),
                "triggers": triggers,
                "validation_data": validation_data,
                "required_actions": self._determine_required_actions(triggers),
                "estimated_rework": self._estimate_rework(triggers)
            }

            return {
                "success": True,
                "context": context
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_escalation(
        self, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete escalation workflow.

        Args:
            validation_data: Validation results

        Returns:
            Dict with escalation result
        """
        # Step 1: Check triggers
        trigger_check = self.check_escalation_triggers(validation_data)
        if not trigger_check["success"]:
            return trigger_check

        if not trigger_check["requires_escalation"]:
            return {
                "success": True,
                "requires_escalation": False,
                "message": "No critical triggers met"
            }

        # Step 2: Create context
        context_result = self.create_escalation_context(
            trigger_check["triggers"],
            validation_data
        )

        if not context_result["success"]:
            return context_result

        # Step 3: Save escalation
        escalation_file = self.escalation_dir / f"escalation_{context_result['context']['escalation_id']}.json"
        escalation_file.write_text(
            json.dumps(context_result["context"], indent=2),
            encoding="utf-8"
        )

        # Step 4: Generate Loop 1 instruction
        instruction = self._generate_loop1_instruction(context_result["context"])

        return {
            "success": True,
            "requires_escalation": True,
            "escalation": context_result["context"],
            "escalation_file": str(escalation_file),
            "loop1_instruction": instruction,
            "message": "Critical escalation created - requires Loop 1 re-planning"
        }

    def _generate_escalation_id(self) -> str:
        """Generate unique escalation ID."""
        return f"ESC{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _assess_overall_severity(self, triggers: List[Dict[str, Any]]) -> str:
        """Assess overall severity from triggers."""
        if any(t["severity"] == "critical" for t in triggers):
            return "critical"
        elif any(t["severity"] == "high" for t in triggers):
            return "high"
        else:
            return "medium"

    def _determine_required_actions(
        self, triggers: List[Dict[str, Any]]
    ) -> List[str]:
        """Determine required actions for Loop 1."""
        actions = []

        for trigger in triggers:
            trigger_type = trigger["trigger"]

            if trigger_type == "quality_gate_critical_failure":
                actions.append("Re-evaluate quality standards and requirements")
                actions.append("Revise implementation plan to improve quality")

            elif trigger_type == "security_vulnerabilities":
                actions.append("Security architecture review required")
                actions.append("Update security requirements in specification")

            elif trigger_type == "architecture_issues":
                actions.append("Architecture redesign required")
                actions.append("Re-run premortem with updated architecture")

            elif trigger_type == "test_failures_persistent":
                actions.append("Review test strategy and coverage")
                actions.append("Update quality acceptance criteria")

        return list(set(actions))  # Deduplicate

    def _estimate_rework(self, triggers: List[Dict[str, Any]]) -> str:
        """Estimate rework effort."""
        critical_count = sum(1 for t in triggers if t["severity"] == "critical")

        if critical_count >= 2:
            return "Major rework (4-8 weeks)"
        elif critical_count == 1:
            return "Moderate rework (2-4 weeks)"
        else:
            return "Minor rework (1-2 weeks)"

    def _generate_loop1_instruction(self, context: Dict[str, Any]) -> str:
        """Generate instruction for Loop 1 re-planning."""
        return f"""ESCALATION FROM LOOP 3 TO LOOP 1

**Escalation ID**: {context['escalation_id']}
**Severity**: {context['severity']}
**Timestamp**: {context['timestamp']}

## Critical Issues Detected

{self._format_triggers(context['triggers'])}

## Required Actions

{self._format_actions(context['required_actions'])}

## Estimated Rework

{context['estimated_rework']}

## Next Steps

1. Review escalation context in: {self.escalation_dir}
2. Re-evaluate specification and plan
3. Update premortem with lessons learned
4. Re-run Loop 1 planning with corrections
5. Return to Loop 2 implementation after approval

**IMPORTANT**: Do not proceed to production until all critical issues are resolved.
"""

    def _format_triggers(self, triggers: List[Dict[str, Any]]) -> str:
        """Format triggers for instruction."""
        lines = []
        for trigger in triggers:
            lines.append(
                f"- **{trigger['trigger']}** ({trigger['severity']}): "
                f"{trigger['value']} (threshold: {trigger['threshold']})"
            )
        return "\n".join(lines)

    def _format_actions(self, actions: List[str]) -> str:
        """Format actions for instruction."""
        return "\n".join([f"{i}. {action}" for i, action in enumerate(actions, 1)])


if __name__ == "__main__":
    # Example usage
    manager = EscalationManager()

    # Example validation data with failures
    validation_data = {
        "quality_gate": {"percentage": 45},
        "security": {"critical_issues": 2},
        "tests": {"failure_rate": 15}
    }

    result = manager.create_escalation(validation_data)
    print(json.dumps(result, indent=2))
