#!/usr/bin/env python3
"""
Loop 2 Memory - Memory persistence helpers for Loop 2 Implementation

Atomic skill helper for Loop 2 Implementation phase.
Handles memory state persistence and Loop 3 handoff.

VERSION: 1.0.0
USAGE: python loop2_memory.py --action save --data state.json
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib


class Loop2Memory:
    """Manages Loop 2 implementation state persistence."""

    def __init__(self, memory_dir: Optional[Path] = None):
        """
        Initialize Loop 2 memory manager.

        Args:
            memory_dir: Directory for memory files
        """
        self.memory_dir = memory_dir or Path.cwd() / ".claude" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.memory_dir / "loop2_state.json"

    def load_loop1_context(self) -> Dict[str, Any]:
        """
        Load Loop 1 context for handoff.

        Returns:
            Dict with Loop 1 state
        """
        try:
            handoff_file = self.memory_dir / "loop1_to_loop2_handoff.json"

            if not handoff_file.exists():
                return {
                    "success": False,
                    "error": "No Loop 1 handoff found"
                }

            handoff = json.loads(handoff_file.read_text(encoding="utf-8"))

            return {
                "success": True,
                "loop1_context": handoff,
                "message": "Loop 1 context loaded"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_state(
        self,
        week: int,
        implementation: Dict[str, Any],
        audits: Dict[str, Any],
        agents_used: List[str]
    ) -> Dict[str, Any]:
        """
        Save Loop 2 state to memory.

        Args:
            week: Current week number
            implementation: Implementation details
            audits: Audit results
            agents_used: List of agent names used

        Returns:
            Dict with save result
        """
        try:
            # Load existing state or create new
            if self.state_file.exists():
                state = json.loads(self.state_file.read_text(encoding="utf-8"))
            else:
                state = {
                    "loop": 2,
                    "phase": "implementation",
                    "weeks": {},
                    "version": "1.0.0"
                }

            # Update state for current week
            state["weeks"][str(week)] = {
                "timestamp": datetime.now().isoformat(),
                "implementation": implementation,
                "audits": audits,
                "agents_used": agents_used
            }

            state["last_updated"] = datetime.now().isoformat()
            state["current_week"] = week

            # Add checksum
            state["checksum"] = self._calculate_checksum(state)

            self.state_file.write_text(
                json.dumps(state, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "file": str(self.state_file),
                "week": week,
                "checksum": state["checksum"],
                "message": f"Week {week} state saved"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_state(self) -> Dict[str, Any]:
        """
        Load Loop 2 state from memory.

        Returns:
            Dict with state data
        """
        try:
            if not self.state_file.exists():
                return {
                    "success": False,
                    "error": "No Loop 2 state found"
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
                "message": "Loop 2 state loaded"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def prepare_loop3_handoff(self) -> Dict[str, Any]:
        """
        Prepare handoff package for Loop 3.

        Returns:
            Dict with handoff data
        """
        load_result = self.load_state()
        if not load_result["success"]:
            return load_result

        state = load_result["state"]

        try:
            # Aggregate implementation data
            total_weeks = len(state.get("weeks", {}))
            all_audits = []
            all_agents = set()

            for week_data in state["weeks"].values():
                all_audits.append(week_data.get("audits", {}))
                all_agents.update(week_data.get("agents_used", []))

            handoff = {
                "loop2_complete": True,
                "timestamp": datetime.now().isoformat(),
                "weeks_completed": total_weeks,
                "agents_used": list(all_agents),
                "final_audits": all_audits[-1] if all_audits else {},
                "implementation_summary": self._summarize_implementation(state),
                "ready_for_loop3": self._check_readiness(all_audits)
            }

            handoff_file = self.memory_dir / "loop2_to_loop3_handoff.json"
            handoff_file.write_text(
                json.dumps(handoff, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "handoff": handoff,
                "handoff_file": str(handoff_file),
                "message": "Loop 3 handoff prepared"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_checksum(self, state: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum of state."""
        state_copy = {k: v for k, v in state.items() if k != "checksum"}
        state_str = json.dumps(state_copy, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]

    def _summarize_implementation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize implementation progress."""
        weeks = state.get("weeks", {})
        return {
            "total_weeks": len(weeks),
            "current_week": state.get("current_week", 0),
            "completion_percentage": (len(weeks) / 26) * 100
        }

    def _check_readiness(self, audits: List[Dict[str, Any]]) -> bool:
        """Check if implementation is ready for Loop 3."""
        if not audits:
            return False

        latest_audit = audits[-1]
        return latest_audit.get("all_passed", False)

    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get Loop 2 progress summary.

        Returns:
            Dict with progress data
        """
        load_result = self.load_state()
        if not load_result["success"]:
            return load_result

        state = load_result["state"]

        return {
            "success": True,
            "summary": {
                "phase": state.get("phase"),
                "current_week": state.get("current_week"),
                "total_weeks": len(state.get("weeks", {})),
                "last_updated": state.get("last_updated"),
                "completion": f"{(len(state.get('weeks', {})) / 26) * 100:.1f}%"
            }
        }


if __name__ == "__main__":
    # Example usage
    memory = Loop2Memory()

    # Load Loop 1 context
    context = memory.load_loop1_context()
    print("Loop 1 context:", json.dumps(context, indent=2))

    # Save Week 1 state
    result = memory.save_state(
        week=1,
        implementation={"modules": ["analyzer"], "loc": 2661},
        audits={"all_passed": True, "coverage": 85},
        agents_used=["coder", "tester", "reviewer"]
    )
    print("\nSave result:", json.dumps(result, indent=2))

    # Get progress
    progress = memory.get_progress_summary()
    print("\nProgress:", json.dumps(progress, indent=2))
