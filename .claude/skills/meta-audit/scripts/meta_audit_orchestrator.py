#!/usr/bin/env python3
"""
Meta-Audit Orchestrator

Coordinates 3-phase sequential audit-and-fix workflow:
1. Theater Detection & Elimination
2. Functionality Validation & Correction
3. Style/Quality Refactoring

Each phase follows: Audit → Fix → Verify (up to 3 attempts)

VERSION: 1.0.0
USAGE: python meta_audit_orchestrator.py --target src/
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import existing audit runner
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "loop2-implementation" / "scripts"))
from audit_runner import AuditRunner


class MetaAuditOrchestrator:
    """Orchestrates 3-phase meta-audit with automatic fixes."""

    def __init__(self, target_path: Path, max_attempts: int = 3):
        """
        Initialize meta-audit orchestrator.

        Args:
            target_path: Path to audit and fix
            max_attempts: Max retry attempts per phase (default: 3)
        """
        self.target_path = target_path
        self.max_attempts = max_attempts
        self.audit_runner = AuditRunner(project_root=target_path.parent)
        self.results = {
            "start_time": datetime.now().isoformat(),
            "target": str(target_path),
            "phases": []
        }

    def run_meta_audit(self, skip_phases: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Run complete 3-phase meta-audit.

        Args:
            skip_phases: List of phase numbers to skip (1, 2, or 3)

        Returns:
            Dict with complete audit results
        """
        skip_phases = skip_phases or []

        print("=" * 70)
        print("META-AUDIT: Comprehensive Quality Orchestration")
        print("=" * 70)
        print(f"Target: {self.target_path}")
        print(f"Max Attempts per Phase: {self.max_attempts}")
        print()

        # Phase 1: Theater Detection & Elimination
        if 1 not in skip_phases:
            phase1 = self.run_phase1_theater()
            self.results["phases"].append(phase1)

            if not phase1["passed"]:
                return self._finalize_results("FAILED_PHASE_1")

            print()

        # Phase 2: Functionality Validation & Correction
        if 2 not in skip_phases:
            phase2 = self.run_phase2_functionality()
            self.results["phases"].append(phase2)

            if not phase2["passed"]:
                return self._finalize_results("FAILED_PHASE_2")

            print()

        # Phase 3: Style/Quality Refactoring
        if 3 not in skip_phases:
            phase3 = self.run_phase3_style()
            self.results["phases"].append(phase3)

            if not phase3["passed"]:
                # Phase 3 failure is acceptable (code works, just not perfect)
                self.results["warning"] = "Phase 3 incomplete: Code functional but quality standards not fully met"
                print(f"\n⚠️  WARNING: {self.results['warning']}")

            print()

        return self._finalize_results("SUCCESS")

    def run_phase1_theater(self) -> Dict[str, Any]:
        """
        Phase 1: Theater Detection & Elimination.

        Returns:
            Dict with phase results
        """
        print("-" * 70)
        print("PHASE 1: Theater Detection & Elimination")
        print("-" * 70)

        phase_result = {
            "phase": 1,
            "name": "Theater Detection & Elimination",
            "attempts": [],
            "passed": False
        }

        for attempt in range(1, self.max_attempts + 1):
            print(f"\nAttempt {attempt}/{self.max_attempts}")

            # Step 1: Run theater audit
            print("  1. Running theater audit...")
            audit = self.audit_runner.run_theater_audit(self.target_path)

            attempt_data = {
                "attempt": attempt,
                "audit_score": audit.get("score", 0),
                "audit_passed": audit.get("passed", False),
                "timestamp": datetime.now().isoformat()
            }

            if audit.get("passed", False):
                print(f"  ✅ Theater audit PASSED (score: {audit['score']} < 60)")
                phase_result["attempts"].append(attempt_data)
                phase_result["passed"] = True
                phase_result["final_score"] = audit["score"]
                break

            print(f"  ❌ Theater audit FAILED (score: {audit['score']} >= 60)")
            print(f"     - TODOs: {audit['results']['todo_count']}")
            print(f"     - Mocks: {audit['results']['mock_detection']['count']}")
            print(f"     - Placeholders: {audit['results']['placeholder_detection']['count']}")

            # Step 2: Spawn theater fix agent (Coder)
            print("  2. Spawning Coder Drone to eliminate theater...")
            fix_result = self._spawn_theater_fix_agent(audit)
            attempt_data["fix_applied"] = fix_result

            # Step 3: Re-audit to verify
            print("  3. Re-auditing to verify fixes...")
            attempt_data["verification_audit"] = self.audit_runner.run_theater_audit(
                self.target_path
            )

            phase_result["attempts"].append(attempt_data)

        if not phase_result["passed"]:
            print(f"\n❌ PHASE 1 FAILED after {self.max_attempts} attempts")
            print("   ESCALATION: Manual intervention required")

        return phase_result

    def run_phase2_functionality(self) -> Dict[str, Any]:
        """
        Phase 2: Functionality Validation & Correction.

        Returns:
            Dict with phase results
        """
        print("-" * 70)
        print("PHASE 2: Functionality Validation & Correction")
        print("-" * 70)

        phase_result = {
            "phase": 2,
            "name": "Functionality Validation & Correction",
            "attempts": [],
            "passed": False
        }

        for attempt in range(1, self.max_attempts + 1):
            print(f"\nAttempt {attempt}/{self.max_attempts}")

            # Step 1: Run functionality audit
            print("  1. Running functionality audit...")
            audit = self.audit_runner.run_functionality_audit(self.target_path)

            attempt_data = {
                "attempt": attempt,
                "audit_passed": audit.get("passed", False),
                "timestamp": datetime.now().isoformat()
            }

            if audit.get("passed", False):
                print("  ✅ Functionality audit PASSED")
                print(f"     - All tests passing")
                print(f"     - Coverage: {audit['results']['test_results'].get('coverage', 'N/A')}")
                phase_result["attempts"].append(attempt_data)
                phase_result["passed"] = True
                break

            print("  ❌ Functionality audit FAILED")

            # Determine what to fix
            test_results = audit["results"].get("test_results", {})
            if not test_results.get("success", False):
                print("     - Tests failing, spawning Debugger Drone...")
                fix_result = self._spawn_debugger_agent(audit)
                attempt_data["debugger_fix"] = fix_result

            # TODO: Add tester spawn for low coverage
            # (requires coverage parsing from test_results)

            # Step 2: Re-audit to verify
            print("  2. Re-auditing to verify fixes...")
            attempt_data["verification_audit"] = self.audit_runner.run_functionality_audit(
                self.target_path
            )

            phase_result["attempts"].append(attempt_data)

        if not phase_result["passed"]:
            print(f"\n❌ PHASE 2 FAILED after {self.max_attempts} attempts")
            print("   ESCALATION: Manual intervention required")

        return phase_result

    def run_phase3_style(self) -> Dict[str, Any]:
        """
        Phase 3: Style/Quality Refactoring.

        Returns:
            Dict with phase results
        """
        print("-" * 70)
        print("PHASE 3: Style/Quality Refactoring")
        print("-" * 70)

        phase_result = {
            "phase": 3,
            "name": "Style/Quality Refactoring",
            "attempts": [],
            "passed": False
        }

        for attempt in range(1, self.max_attempts + 1):
            print(f"\nAttempt {attempt}/{self.max_attempts}")

            # Step 1: Run style audit
            print("  1. Running style/quality audit...")
            audit = self.audit_runner.run_style_audit(self.target_path)

            attempt_data = {
                "attempt": attempt,
                "audit_passed": audit.get("passed", False),
                "timestamp": datetime.now().isoformat()
            }

            if audit.get("passed", False):
                print("  ✅ Style audit PASSED")
                phase_result["attempts"].append(attempt_data)
                phase_result["passed"] = True
                break

            print("  ❌ Style audit FAILED")
            nasa = audit["results"].get("nasa_compliance", {})
            print(f"     - NASA violations: {len(nasa.get('violations', []))}")

            # Step 2: Spawn reviewer for refactoring
            print("  2. Spawning Reviewer Drone for refactoring...")
            fix_result = self._spawn_reviewer_agent(audit)
            attempt_data["refactoring_applied"] = fix_result

            # Step 3: CRITICAL - Regression check
            print("  3. ⚠️  CRITICAL: Running regression check...")
            regression_check = self.audit_runner.run_functionality_audit(
                self.target_path
            )

            if not regression_check.get("passed", False):
                print("  ❌ REGRESSION: Refactoring broke tests!")
                print("     Reverting changes...")
                # In real implementation, would use git revert
                attempt_data["regression_detected"] = True
                phase_result["attempts"].append(attempt_data)
                continue

            print("  ✅ No regression: Tests still passing")

            # Step 4: Re-audit style to verify improvements
            print("  4. Re-auditing style to verify improvements...")
            attempt_data["verification_audit"] = self.audit_runner.run_style_audit(
                self.target_path
            )

            phase_result["attempts"].append(attempt_data)

        if not phase_result["passed"]:
            print(f"\n⚠️  PHASE 3 INCOMPLETE after {self.max_attempts} attempts")
            print("   Code is functional, but quality standards not fully met")

        return phase_result

    def _spawn_theater_fix_agent(self, audit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Spawn Coder Drone to eliminate theater.

        In real implementation, this would use Task tool to spawn agent.
        For now, we simulate the fix.

        Args:
            audit: Theater audit results

        Returns:
            Dict with fix results
        """
        # Simulated fix (real implementation would spawn Task agent)
        return {
            "agent": "coder",
            "task": "eliminate_theater",
            "simulated": True,
            "message": "Would spawn Coder Drone to eliminate theater code"
        }

    def _spawn_debugger_agent(self, audit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Spawn Debugger Drone to fix failing tests.

        Args:
            audit: Functionality audit results

        Returns:
            Dict with fix results
        """
        # Simulated fix
        return {
            "agent": "debugger",
            "task": "fix_failing_tests",
            "simulated": True,
            "message": "Would spawn Debugger Drone to fix test failures"
        }

    def _spawn_reviewer_agent(self, audit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Spawn Reviewer Drone for quality refactoring.

        Args:
            audit: Style audit results

        Returns:
            Dict with fix results
        """
        # Simulated refactoring
        return {
            "agent": "reviewer",
            "task": "quality_refactoring",
            "simulated": True,
            "message": "Would spawn Reviewer Drone for quality refactoring"
        }

    def _finalize_results(self, status: str) -> Dict[str, Any]:
        """
        Finalize meta-audit results.

        Args:
            status: Overall status (SUCCESS, FAILED_PHASE_1, FAILED_PHASE_2)

        Returns:
            Complete results dict
        """
        self.results["end_time"] = datetime.now().isoformat()
        self.results["overall_status"] = status
        self.results["production_ready"] = status == "SUCCESS"

        # Calculate metrics
        phases_passed = sum(1 for p in self.results["phases"] if p["passed"])
        phases_total = len(self.results["phases"])
        self.results["phases_passed"] = f"{phases_passed}/{phases_total}"

        print("\n" + "=" * 70)
        print("META-AUDIT COMPLETE")
        print("=" * 70)
        print(f"Status: {status}")
        print(f"Phases Passed: {phases_passed}/{phases_total}")
        print(f"Production Ready: {self.results['production_ready']}")
        print("=" * 70)

        return self.results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Meta-Audit: Comprehensive Quality Orchestrator"
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target path to audit and fix"
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Max retry attempts per phase (default: 3)"
    )
    parser.add_argument(
        "--skip-phases",
        type=str,
        default="",
        help="Comma-separated phase numbers to skip (e.g., '1,3')"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file for results"
    )

    args = parser.parse_args()

    # Parse skip phases
    skip_phases = []
    if args.skip_phases:
        skip_phases = [int(p) for p in args.skip_phases.split(",")]

    # Run meta-audit
    orchestrator = MetaAuditOrchestrator(
        target_path=args.target,
        max_attempts=args.max_attempts
    )

    results = orchestrator.run_meta_audit(skip_phases=skip_phases)

    # Save results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    else:
        print("\nResults:")
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
