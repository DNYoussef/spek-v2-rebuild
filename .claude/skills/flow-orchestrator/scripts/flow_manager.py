#!/usr/bin/env python3
"""
Flow Manager - Core FSM implementation for 3-loop workflow

Atomic skill helper for Flow Orchestrator.
Implements state machine with transitions and event handling.

VERSION: 1.0.0
USAGE: python flow_manager.py --event start_loop1
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from enum import Enum


class State(Enum):
    """Flow states."""
    IDLE = "idle"
    LOOP1_PLANNING = "loop1_planning"
    LOOP1_REVIEW = "loop1_review"
    LOOP2_IMPLEMENTATION = "loop2_implementation"
    LOOP2_AUDIT = "loop2_audit"
    LOOP3_QUALITY = "loop3_quality"
    LOOP3_DEPLOYMENT = "loop3_deployment"
    PRODUCTION = "production"
    ESCALATED = "escalated"


class Event(Enum):
    """Flow events."""
    START_LOOP1 = "start_loop1"
    LOOP1_COMPLETE = "loop1_complete"
    LOOP1_APPROVED = "loop1_approved"
    START_LOOP2 = "start_loop2"
    LOOP2_WEEK_COMPLETE = "loop2_week_complete"
    LOOP2_COMPLETE = "loop2_complete"
    START_LOOP3 = "start_loop3"
    AUDITS_PASSED = "audits_passed"
    AUDITS_FAILED = "audits_failed"
    DEPLOYMENT_APPROVED = "deployment_approved"
    DEPLOYMENT_REJECTED = "deployment_rejected"
    ESCALATE = "escalate"


class FlowManager:
    """Manages 3-loop workflow state machine."""

    # State transition rules
    TRANSITIONS = {
        (State.IDLE, Event.START_LOOP1): State.LOOP1_PLANNING,
        (State.LOOP1_PLANNING, Event.LOOP1_COMPLETE): State.LOOP1_REVIEW,
        (State.LOOP1_REVIEW, Event.LOOP1_APPROVED): State.LOOP2_IMPLEMENTATION,
        (State.LOOP2_IMPLEMENTATION, Event.LOOP2_WEEK_COMPLETE): State.LOOP2_AUDIT,
        (State.LOOP2_AUDIT, Event.AUDITS_PASSED): State.LOOP2_IMPLEMENTATION,
        (State.LOOP2_AUDIT, Event.AUDITS_FAILED): State.LOOP2_IMPLEMENTATION,
        (State.LOOP2_IMPLEMENTATION, Event.LOOP2_COMPLETE): State.LOOP3_QUALITY,
        (State.LOOP3_QUALITY, Event.AUDITS_PASSED): State.LOOP3_DEPLOYMENT,
        (State.LOOP3_QUALITY, Event.AUDITS_FAILED): State.LOOP2_IMPLEMENTATION,
        (State.LOOP3_DEPLOYMENT, Event.DEPLOYMENT_APPROVED): State.PRODUCTION,
        (State.LOOP3_DEPLOYMENT, Event.DEPLOYMENT_REJECTED): State.LOOP2_IMPLEMENTATION,
        (State.LOOP3_QUALITY, Event.ESCALATE): State.ESCALATED,
        (State.ESCALATED, Event.START_LOOP1): State.LOOP1_PLANNING,
    }

    def __init__(self, state_dir: Optional[Path] = None):
        """
        Initialize flow manager.

        Args:
            state_dir: Directory for state files
        """
        self.state_dir = state_dir or Path.cwd() / ".claude" / "flow"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "flow_state.json"
        self.current_state = State.IDLE
        self.history: List[Dict[str, Any]] = []
        self._load_state()

    def get_current_state(self) -> str:
        """Get current state."""
        return self.current_state.value

    def can_transition(self, event: Event) -> bool:
        """
        Check if transition is valid.

        Args:
            event: Event to check

        Returns:
            True if transition is valid
        """
        return (self.current_state, event) in self.TRANSITIONS

    def transition(self, event: Event, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute state transition.

        Args:
            event: Event to trigger
            context: Optional transition context

        Returns:
            Dict with transition result
        """
        try:
            if not self.can_transition(event):
                return {
                    "success": False,
                    "error": f"Invalid transition: {self.current_state.value} + {event.value}"
                }

            old_state = self.current_state
            new_state = self.TRANSITIONS[(self.current_state, event)]

            # Record transition
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "from_state": old_state.value,
                "event": event.value,
                "to_state": new_state.value,
                "context": context or {}
            })

            self.current_state = new_state
            self._save_state()

            return {
                "success": True,
                "from_state": old_state.value,
                "event": event.value,
                "to_state": new_state.value,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_valid_events(self) -> List[str]:
        """
        Get valid events for current state.

        Returns:
            List of valid event names
        """
        return [
            event.value
            for (state, event), _ in self.TRANSITIONS.items()
            if state == self.current_state
        ]

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get transition history.

        Args:
            limit: Optional limit on results

        Returns:
            List of historical transitions
        """
        if limit:
            return self.history[-limit:]
        return self.history

    def reset(self) -> Dict[str, Any]:
        """
        Reset flow to idle state.

        Returns:
            Dict with reset result
        """
        try:
            self.current_state = State.IDLE
            self.history = []
            self._save_state()

            return {
                "success": True,
                "message": "Flow reset to idle state"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_flow_status(self) -> Dict[str, Any]:
        """
        Get complete flow status.

        Returns:
            Dict with status information
        """
        return {
            "current_state": self.current_state.value,
            "valid_events": self.get_valid_events(),
            "history_count": len(self.history),
            "recent_transitions": self.get_history(limit=5)
        }

    def _save_state(self) -> None:
        """Save state to file."""
        state_data = {
            "current_state": self.current_state.value,
            "history": self.history,
            "last_updated": datetime.now().isoformat()
        }

        self.state_file.write_text(
            json.dumps(state_data, indent=2),
            encoding="utf-8"
        )

    def _load_state(self) -> None:
        """Load state from file."""
        if not self.state_file.exists():
            return

        try:
            state_data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.current_state = State(state_data.get("current_state", "idle"))
            self.history = state_data.get("history", [])
        except Exception:
            # If load fails, start fresh
            pass


if __name__ == "__main__":
    # Example usage
    manager = FlowManager()

    print("Initial state:", manager.get_current_state())
    print("Valid events:", manager.get_valid_events())

    # Transition through workflow
    result1 = manager.transition(Event.START_LOOP1, {"user": "test"})
    print("\nTransition 1:", json.dumps(result1, indent=2))

    result2 = manager.transition(Event.LOOP1_COMPLETE, {"spec_version": "1.0"})
    print("\nTransition 2:", json.dumps(result2, indent=2))

    # Get status
    status = manager.get_flow_status()
    print("\nFlow status:", json.dumps(status, indent=2))
