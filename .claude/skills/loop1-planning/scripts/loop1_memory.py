#!/usr/bin/env python3
"""
Loop 1 Memory - Memory persistence helpers for Loop 1 Planning

Atomic skill helper for Loop 1 Planning phase.
Handles memory state persistence and Loop 2 handoff.

VERSION: 1.0.0
USAGE: python loop1_memory.py --action save --data state.json
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib


class Loop1Memory:
    """Manages Loop 1 planning state persistence."""

    def __init__(self, memory_dir: Optional[Path] = None):
        """
        Initialize Loop 1 memory manager.

        Args:
            memory_dir: Directory for memory files
        """
        self.memory_dir = memory_dir or Path.cwd() / ".claude" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.memory_dir / "loop1_state.json"

    def save_state(
        self,
        spec: Dict[str, Any],
        plan: Dict[str, Any],
        premortem: Dict[str, Any],
        research: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save Loop 1 state to memory.

        Args:
            spec: Specification document data
            plan: Implementation plan data
            premortem: Risk analysis data
            research: Optional research data

        Returns:
            Dict with save result
        """
        try:
            state = {
                "loop": 1,
                "phase": "planning",
                "timestamp": datetime.now().isoformat(),
                "spec": spec,
                "plan": plan,
                "premortem": premortem,
                "research": research or {},
                "version": "1.0.0"
            }

            # Add checksum for integrity
            state["checksum"] = self._calculate_checksum(state)

            self.state_file.write_text(
                json.dumps(state, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "file": str(self.state_file),
                "checksum": state["checksum"],
                "message": "Loop 1 state saved successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_state(self) -> Dict[str, Any]:
        """
        Load Loop 1 state from memory.

        Returns:
            Dict with state data or error
        """
        try:
            if not self.state_file.exists():
                return {
                    "success": False,
                    "error": "No Loop 1 state found"
                }

            state = json.loads(self.state_file.read_text(encoding="utf-8"))

            # Verify checksum
            stored_checksum = state.pop("checksum", None)
            calculated_checksum = self._calculate_checksum(state)

            if stored_checksum != calculated_checksum:
                return {
                    "success": False,
                    "error": "State integrity check failed"
                }

            return {
                "success": True,
                "state": state,
                "message": "Loop 1 state loaded successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def prepare_loop2_handoff(self) -> Dict[str, Any]:
        """
        Prepare handoff package for Loop 2.

        Returns:
            Dict with handoff data
        """
        load_result = self.load_state()
        if not load_result["success"]:
            return load_result

        state = load_result["state"]

        try:
            handoff = {
                "loop1_complete": True,
                "timestamp": datetime.now().isoformat(),
                "decision": state["premortem"].get("decision", "UNKNOWN"),
                "risk_score": state["premortem"].get("score", 0),
                "spec_version": state["spec"].get("version", "1.0"),
                "plan_weeks": state["plan"].get("total_weeks", 26),
                "artifacts": {
                    "spec": state.get("spec", {}),
                    "plan": state.get("plan", {}),
                    "research": state.get("research", {})
                },
                "next_actions": self._generate_next_actions(state)
            }

            handoff_file = self.memory_dir / "loop1_to_loop2_handoff.json"
            handoff_file.write_text(
                json.dumps(handoff, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "handoff": handoff,
                "handoff_file": str(handoff_file),
                "message": "Loop 2 handoff prepared"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_checksum(self, state: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum of state."""
        # Remove checksum field if present
        state_copy = {k: v for k, v in state.items() if k != "checksum"}
        state_str = json.dumps(state_copy, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]

    def _generate_next_actions(self, state: Dict[str, Any]) -> list:
        """Generate next actions for Loop 2."""
        decision = state["premortem"].get("decision", "UNKNOWN")

        if decision == "GO":
            return [
                "Begin Week 1 implementation",
                "Set up development environment",
                "Initialize project structure"
            ]
        elif decision == "CAUTION":
            return [
                "Review and mitigate P1/P2 risks",
                "Update premortem with mitigations",
                "Re-evaluate decision score"
            ]
        else:
            return [
                "Revise specification based on risks",
                "Re-run premortem analysis",
                "Do not proceed to Loop 2"
            ]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get Loop 1 state summary.

        Returns:
            Dict with summary data
        """
        load_result = self.load_state()
        if not load_result["success"]:
            return load_result

        state = load_result["state"]

        return {
            "success": True,
            "summary": {
                "phase": state.get("phase"),
                "timestamp": state.get("timestamp"),
                "decision": state["premortem"].get("decision"),
                "risk_score": state["premortem"].get("score"),
                "spec_version": state["spec"].get("version"),
                "ready_for_loop2": state["premortem"].get("decision") == "GO"
            }
        }


if __name__ == "__main__":
    # Example usage
    memory = Loop1Memory()

    # Save example state
    result = memory.save_state(
        spec={"version": "1.0", "title": "Test Feature"},
        plan={"total_weeks": 4, "phases": ["Week 1", "Week 2"]},
        premortem={"decision": "GO", "score": 1500}
    )
    print("Save result:", json.dumps(result, indent=2))

    # Load state
    load_result = memory.load_state()
    print("\nLoad result:", json.dumps(load_result, indent=2))

    # Prepare handoff
    handoff_result = memory.prepare_loop2_handoff()
    print("\nHandoff result:", json.dumps(handoff_result, indent=2))
