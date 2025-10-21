#!/usr/bin/env python3
"""
Transition Coordinator - Loop transition logic

Atomic skill helper for Flow Orchestrator.
Manages transitions between loops (1→2, 2→3, 3→production, 3→1).

VERSION: 1.0.0
USAGE: python transition_coordinator.py --from-loop 1 --to-loop 2
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class TransitionCoordinator:
    """Coordinates transitions between loops."""

    # Transition requirements
    TRANSITION_REQUIREMENTS = {
        "1_to_2": {
            "required_artifacts": ["spec", "plan", "premortem"],
            "required_decision": "GO",
            "max_risk_score": 2000
        },
        "2_to_3": {
            "required_artifacts": ["implementation", "audits"],
            "all_audits_passed": True,
            "min_weeks_complete": 1
        },
        "3_to_production": {
            "required_artifacts": ["quality_gate", "deployment_approval"],
            "quality_gate_passed": True,
            "deployment_approved": True
        },
        "3_to_1": {
            "required_artifacts": ["escalation"],
            "escalation_severity": "critical"
        }
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize transition coordinator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.transition_dir = self.project_root / ".claude" / "transitions"
        self.transition_dir.mkdir(parents=True, exist_ok=True)

    def _check_artifacts(
        self, requirements: Dict[str, Any], context: Dict[str, Any]
    ) -> list:
        """Check required artifacts are present."""
        results = []
        for artifact in requirements.get("required_artifacts", []):
            has_artifact = artifact in context
            results.append({
                "check": f"Has {artifact} artifact",
                "passed": has_artifact
            })
        return results

    def _check_conditions(
        self, requirements: Dict[str, Any], context: Dict[str, Any]
    ) -> list:
        """Check specific conditions for transition."""
        results = []

        if "required_decision" in requirements:
            decision_ok = context.get("decision") == requirements["required_decision"]
            results.append({"check": "Decision is GO", "passed": decision_ok})

        if "max_risk_score" in requirements:
            score_ok = context.get("risk_score", 9999) <= requirements["max_risk_score"]
            results.append({
                "check": f"Risk score ≤ {requirements['max_risk_score']}",
                "passed": score_ok
            })

        if "all_audits_passed" in requirements:
            audits_ok = context.get("all_audits_passed", False)
            results.append({"check": "All audits passed", "passed": audits_ok})

        if "quality_gate_passed" in requirements:
            quality_ok = context.get("quality_gate_passed", False)
            results.append({"check": "Quality gate passed", "passed": quality_ok})

        if "deployment_approved" in requirements:
            deploy_ok = context.get("deployment_approved", False)
            results.append({"check": "Deployment approved", "passed": deploy_ok})

        return results

    def validate_transition(
        self, from_loop: int, to_loop: int, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate if transition is allowed.

        Args:
            from_loop: Source loop
            to_loop: Target loop
            context: Transition context data

        Returns:
            Dict with validation result
        """
        try:
            transition_key = f"{from_loop}_to_{to_loop}"

            if transition_key not in self.TRANSITION_REQUIREMENTS:
                return {
                    "success": False,
                    "error": f"Invalid transition: {transition_key}"
                }

            requirements = self.TRANSITION_REQUIREMENTS[transition_key]

            # Check artifacts and conditions
            artifact_results = self._check_artifacts(requirements, context)
            condition_results = self._check_conditions(requirements, context)
            validation_results = artifact_results + condition_results

            all_passed = all(r["passed"] for r in validation_results)

            return {
                "success": True,
                "transition_allowed": all_passed,
                "validation_results": validation_results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_transition(
        self, from_loop: int, to_loop: int, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute transition between loops.

        Args:
            from_loop: Source loop
            to_loop: Target loop
            context: Transition context

        Returns:
            Dict with transition result
        """
        # Step 1: Validate transition
        validation = self.validate_transition(from_loop, to_loop, context)

        if not validation["success"]:
            return validation

        if not validation["transition_allowed"]:
            return {
                "success": False,
                "error": "Transition validation failed",
                "validation_results": validation["validation_results"]
            }

        # Step 2: Prepare handoff
        handoff = self._prepare_handoff(from_loop, to_loop, context)

        # Step 3: Generate next loop instruction
        instruction = self._generate_next_loop_instruction(to_loop, handoff)

        # Step 4: Record transition
        transition_record = {
            "timestamp": datetime.now().isoformat(),
            "from_loop": from_loop,
            "to_loop": to_loop,
            "context": context,
            "handoff": handoff,
            "validation": validation
        }

        record_file = self.transition_dir / f"transition_{from_loop}_to_{to_loop}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        record_file.write_text(
            json.dumps(transition_record, indent=2),
            encoding="utf-8"
        )

        return {
            "success": True,
            "from_loop": from_loop,
            "to_loop": to_loop,
            "handoff": handoff,
            "instruction": instruction,
            "record_file": str(record_file),
            "message": f"Transition from Loop {from_loop} to Loop {to_loop} successful"
        }

    def _prepare_handoff(
        self, from_loop: int, to_loop: int, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare handoff data for next loop."""
        handoff = {
            "from_loop": from_loop,
            "to_loop": to_loop,
            "timestamp": datetime.now().isoformat(),
            "context": context
        }

        if from_loop == 1 and to_loop == 2:
            handoff["artifacts"] = {
                "spec": context.get("spec"),
                "plan": context.get("plan"),
                "premortem": context.get("premortem")
            }
            handoff["next_actions"] = [
                "Begin Week 1 implementation",
                "Set up development environment",
                "Initialize project structure"
            ]

        elif from_loop == 2 and to_loop == 3:
            handoff["artifacts"] = {
                "implementation": context.get("implementation"),
                "audits": context.get("audits")
            }
            handoff["next_actions"] = [
                "Run quality gate validation",
                "Execute E2E test suite",
                "Validate deployment readiness"
            ]

        elif from_loop == 3 and to_loop == 1:
            handoff["artifacts"] = {
                "escalation": context.get("escalation")
            }
            handoff["next_actions"] = [
                "Review escalation context",
                "Revise specification",
                "Update premortem",
                "Re-run Loop 1 planning"
            ]

        return handoff

    def _generate_loop1_instruction(self, handoff: Dict[str, Any]) -> str:
        """Generate Loop 1 instruction."""
        return f"""TRANSITION TO LOOP 1: Planning

**Previous Loop**: {handoff['from_loop']}
**Handoff Timestamp**: {handoff['timestamp']}

## Context
{json.dumps(handoff.get('context', {}), indent=2)}

## Next Actions
{self._format_actions(handoff.get('next_actions', []))}

Begin Loop 1 planning now."""

    def _generate_loop2_instruction(self, handoff: Dict[str, Any]) -> str:
        """Generate Loop 2 instruction."""
        return f"""TRANSITION TO LOOP 2: Implementation

**Previous Loop**: {handoff['from_loop']}
**Handoff Timestamp**: {handoff['timestamp']}

## Available Artifacts
{self._format_artifacts(handoff.get('artifacts', {}))}

## Next Actions
{self._format_actions(handoff.get('next_actions', []))}

Begin Loop 2 implementation now."""

    def _generate_loop3_instruction(self, handoff: Dict[str, Any]) -> str:
        """Generate Loop 3 instruction."""
        return f"""TRANSITION TO LOOP 3: Quality Validation

**Previous Loop**: {handoff['from_loop']}
**Handoff Timestamp**: {handoff['timestamp']}

## Implementation Summary
{self._format_artifacts(handoff.get('artifacts', {}))}

## Next Actions
{self._format_actions(handoff.get('next_actions', []))}

Begin Loop 3 quality validation now."""

    def _generate_production_instruction(self, handoff: Dict[str, Any]) -> str:
        """Generate production instruction."""
        return f"""TRANSITION TO PRODUCTION

**Previous Loop**: {handoff['from_loop']}
**Handoff Timestamp**: {handoff['timestamp']}

All quality gates passed. Ready for production deployment.

## Deployment Checklist
1. Verify environment configuration
2. Execute database migrations
3. Deploy to production
4. Run post-deployment validation
5. Monitor for issues

Begin production deployment now."""

    def _generate_next_loop_instruction(
        self, to_loop: int, handoff: Dict[str, Any]
    ) -> str:
        """Generate instruction for next loop."""
        if to_loop == 1:
            return self._generate_loop1_instruction(handoff)
        elif to_loop == 2:
            return self._generate_loop2_instruction(handoff)
        elif to_loop == 3:
            return self._generate_loop3_instruction(handoff)
        else:
            return self._generate_production_instruction(handoff)

    def _format_actions(self, actions: list) -> str:
        """Format actions list."""
        return "\n".join([f"{i}. {action}" for i, action in enumerate(actions, 1)])

    def _format_artifacts(self, artifacts: Dict[str, Any]) -> str:
        """Format artifacts dict."""
        lines = []
        for key, value in artifacts.items():
            lines.append(f"- **{key}**: {type(value).__name__}")
        return "\n".join(lines) if lines else "No artifacts"


if __name__ == "__main__":
    # Example usage
    coordinator = TransitionCoordinator()

    # Example: Loop 1 → Loop 2 transition
    result = coordinator.execute_transition(
        from_loop=1,
        to_loop=2,
        context={
            "spec": {"version": "1.0"},
            "plan": {"weeks": 26},
            "premortem": {"decision": "GO", "risk_score": 1500},
            "decision": "GO",
            "risk_score": 1500
        }
    )

    print(json.dumps(result, indent=2))
