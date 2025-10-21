#!/usr/bin/env python3
"""
Memory Manager - Memory state persistence for flow orchestrator

Atomic skill helper for Flow Orchestrator.
Manages cross-loop memory persistence and integrity.

VERSION: 1.0.0
USAGE: python memory_manager.py --action save --data state.json
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import hashlib


class MemoryManager:
    """Manages flow orchestrator memory state."""

    def __init__(self, memory_dir: Optional[Path] = None):
        """
        Initialize memory manager.

        Args:
            memory_dir: Directory for memory files
        """
        self.memory_dir = memory_dir or Path.cwd() / ".claude" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def save_loop_state(
        self, loop: int, state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save loop state to memory.

        Args:
            loop: Loop number (1, 2, or 3)
            state: State data to save

        Returns:
            Dict with save result
        """
        try:
            state_with_meta = {
                "loop": loop,
                "timestamp": datetime.now().isoformat(),
                "state": state,
                "version": "1.0.0"
            }

            # Add checksum
            state_with_meta["checksum"] = self._calculate_checksum(state_with_meta)

            state_file = self.memory_dir / f"loop{loop}_state.json"
            state_file.write_text(
                json.dumps(state_with_meta, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "loop": loop,
                "file": str(state_file),
                "checksum": state_with_meta["checksum"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_loop_state(self, loop: int) -> Dict[str, Any]:
        """
        Load loop state from memory.

        Args:
            loop: Loop number to load

        Returns:
            Dict with state data
        """
        try:
            state_file = self.memory_dir / f"loop{loop}_state.json"

            if not state_file.exists():
                return {
                    "success": False,
                    "error": f"No state found for loop {loop}"
                }

            data = json.loads(state_file.read_text(encoding="utf-8"))

            # Verify checksum
            stored_checksum = data.pop("checksum", None)
            calculated_checksum = self._calculate_checksum(data)

            if stored_checksum != calculated_checksum:
                return {
                    "success": False,
                    "error": "State integrity check failed"
                }

            return {
                "success": True,
                "loop": loop,
                "state": data["state"],
                "timestamp": data.get("timestamp")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_handoff(
        self, from_loop: int, to_loop: int, handoff_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save loop handoff data.

        Args:
            from_loop: Source loop
            to_loop: Target loop
            handoff_data: Handoff data

        Returns:
            Dict with save result
        """
        try:
            handoff = {
                "from_loop": from_loop,
                "to_loop": to_loop,
                "timestamp": datetime.now().isoformat(),
                "data": handoff_data
            }

            handoff_file = self.memory_dir / f"loop{from_loop}_to_loop{to_loop}_handoff.json"
            handoff_file.write_text(
                json.dumps(handoff, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "handoff_file": str(handoff_file)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_handoff(
        self, from_loop: int, to_loop: int
    ) -> Dict[str, Any]:
        """
        Load loop handoff data.

        Args:
            from_loop: Source loop
            to_loop: Target loop

        Returns:
            Dict with handoff data
        """
        try:
            handoff_file = self.memory_dir / f"loop{from_loop}_to_loop{to_loop}_handoff.json"

            if not handoff_file.exists():
                return {
                    "success": False,
                    "error": f"No handoff found from loop {from_loop} to {to_loop}"
                }

            handoff = json.loads(handoff_file.read_text(encoding="utf-8"))

            return {
                "success": True,
                "handoff": handoff
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_loop_states(self) -> Dict[str, Any]:
        """
        Get all loop states.

        Returns:
            Dict with all states
        """
        try:
            states = {}

            for loop in [1, 2, 3]:
                result = self.load_loop_state(loop)
                if result["success"]:
                    states[f"loop{loop}"] = result["state"]

            return {
                "success": True,
                "states": states,
                "loops_found": len(states)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of all memory files.

        Returns:
            Dict with integrity check results
        """
        try:
            results = []

            for loop in [1, 2, 3]:
                state_file = self.memory_dir / f"loop{loop}_state.json"

                if state_file.exists():
                    data = json.loads(state_file.read_text(encoding="utf-8"))
                    stored_checksum = data.get("checksum")
                    data_copy = {k: v for k, v in data.items() if k != "checksum"}
                    calculated_checksum = self._calculate_checksum(data_copy)

                    results.append({
                        "file": str(state_file),
                        "valid": stored_checksum == calculated_checksum
                    })

            all_valid = all(r["valid"] for r in results)

            return {
                "success": True,
                "all_valid": all_valid,
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup_old_states(self, keep_latest: int = 5) -> Dict[str, Any]:
        """
        Clean up old state backups.

        Args:
            keep_latest: Number of latest states to keep

        Returns:
            Dict with cleanup result
        """
        try:
            backup_pattern = "loop*_state_backup_*.json"
            backups = sorted(
                self.memory_dir.glob(backup_pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            removed = []
            for backup in backups[keep_latest:]:
                backup.unlink()
                removed.append(str(backup))

            return {
                "success": True,
                "removed_count": len(removed),
                "removed_files": removed
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_memory_snapshot(self) -> Dict[str, Any]:
        """
        Export complete memory snapshot.

        Returns:
            Dict with snapshot data
        """
        try:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "loops": {},
                "handoffs": {}
            }

            # Load all loop states
            for loop in [1, 2, 3]:
                result = self.load_loop_state(loop)
                if result["success"]:
                    snapshot["loops"][f"loop{loop}"] = result["state"]

            # Load all handoffs
            for from_loop, to_loop in [(1, 2), (2, 3)]:
                result = self.load_handoff(from_loop, to_loop)
                if result["success"]:
                    snapshot["handoffs"][f"loop{from_loop}_to_loop{to_loop}"] = result["handoff"]

            snapshot_file = self.memory_dir / f"memory_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            snapshot_file.write_text(
                json.dumps(snapshot, indent=2),
                encoding="utf-8"
            )

            return {
                "success": True,
                "snapshot_file": str(snapshot_file),
                "snapshot": snapshot
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Example usage
    manager = MemoryManager()

    # Save loop state
    result1 = manager.save_loop_state(
        loop=1,
        state={"spec": "v1.0", "decision": "GO", "risk_score": 1500}
    )
    print("Save result:", json.dumps(result1, indent=2))

    # Load loop state
    result2 = manager.load_loop_state(loop=1)
    print("\nLoad result:", json.dumps(result2, indent=2))

    # Save handoff
    result3 = manager.save_handoff(
        from_loop=1,
        to_loop=2,
        handoff_data={"approved": True, "next_actions": ["Start Week 1"]}
    )
    print("\nHandoff result:", json.dumps(result3, indent=2))

    # Verify integrity
    result4 = manager.verify_integrity()
    print("\nIntegrity check:", json.dumps(result4, indent=2))
