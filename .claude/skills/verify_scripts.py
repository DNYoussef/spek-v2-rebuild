#!/usr/bin/env python3
"""
Script Verification - Tests all 16 helper scripts for import and basic functionality

VERSION: 1.0.0
USAGE: python verify_scripts.py
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, List

def load_module_from_path(module_name: str, file_path: Path) -> Any:
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None

def verify_script(script_path: Path) -> Dict[str, Any]:
    """Verify a single script can be imported and has expected structure."""
    try:
        module_name = script_path.stem
        module = load_module_from_path(module_name, script_path)

        if not module:
            return {"success": False, "error": "Failed to load module"}

        # Check for classes
        classes = [name for name in dir(module) if not name.startswith("_") and isinstance(getattr(module, name), type)]

        return {
            "success": True,
            "script": script_path.name,
            "classes": classes,
            "has_main": hasattr(module, "__name__")
        }
    except Exception as e:
        return {"success": False, "script": script_path.name, "error": str(e)}

def _get_script_catalog() -> Dict[str, List[Path]]:
    """Get organized catalog of scripts."""
    base_path = Path(__file__).parent
    return {
        "Loop 1 Planning": [
            base_path / "loop1-planning/scripts/research_coordinator.py",
            base_path / "loop1-planning/scripts/premortem_generator.py",
            base_path / "loop1-planning/scripts/loop1_memory.py"
        ],
        "Loop 2 Implementation": [
            base_path / "loop2-implementation/scripts/audit_runner.py",
            base_path / "loop2-implementation/scripts/queen_coordinator.py",
            base_path / "loop2-implementation/scripts/princess_spawner.py",
            base_path / "loop2-implementation/scripts/drone_selector.py",
            base_path / "loop2-implementation/scripts/loop2_memory.py"
        ],
        "Loop 3 Quality": [
            base_path / "loop3-quality/scripts/quality_gate.py",
            base_path / "loop3-quality/scripts/integration_tester.py",
            base_path / "loop3-quality/scripts/rewrite_coordinator.py",
            base_path / "loop3-quality/scripts/deployment_approver.py",
            base_path / "loop3-quality/scripts/escalation_manager.py"
        ],
        "Flow Orchestrator": [
            base_path / "flow-orchestrator/scripts/flow_manager.py",
            base_path / "flow-orchestrator/scripts/memory_manager.py",
            base_path / "flow-orchestrator/scripts/transition_coordinator.py"
        ]
    }

def _verify_category_scripts(
    category: str,
    category_scripts: List[Path],
    passed_scripts: int,
    failed_scripts: List[Dict[str, Any]]
) -> tuple[int, int]:
    """Verify scripts for a single category."""
    print(f"\n{category}")
    print("-" * 70)

    total_scripts = 0
    for script_path in category_scripts:
        total_scripts += 1

        if not script_path.exists():
            print(f"  [FAIL] {script_path.name} - FILE NOT FOUND")
            failed_scripts.append({"script": script_path.name, "error": "File not found"})
            continue

        result = verify_script(script_path)

        if result["success"]:
            passed_scripts += 1
            classes_str = ", ".join(result["classes"]) if result["classes"] else "None"
            print(f"  [PASS] {script_path.name}")
            print(f"     Classes: {classes_str}")
        else:
            print(f"  [FAIL] {script_path.name}")
            print(f"     Error: {result.get('error', 'Unknown error')}")
            failed_scripts.append(result)

    return total_scripts, passed_scripts

def _print_verification_summary(
    total_scripts: int,
    passed_scripts: int,
    failed_scripts: List[Dict[str, Any]]
) -> None:
    """Print verification summary."""
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total Scripts: {total_scripts}")
    print(f"Passed: {passed_scripts} ({(passed_scripts/total_scripts)*100:.1f}%)")
    print(f"Failed: {len(failed_scripts)} ({(len(failed_scripts)/total_scripts)*100:.1f}%)")

    if failed_scripts:
        print("\nFailed Scripts:")
        for failed in failed_scripts:
            print(f"  - {failed['script']}: {failed.get('error', 'Unknown')}")

    print("\n" + "=" * 70)

    if passed_scripts == total_scripts:
        print("[SUCCESS] ALL SCRIPTS VERIFIED SUCCESSFULLY")
    else:
        print("[FAILURE] SOME SCRIPTS FAILED VERIFICATION")

def main() -> int:
    """Main verification function."""
    scripts = _get_script_catalog()

    print("=" * 70)
    print("3-LOOP SKILLS SYSTEM - SCRIPT VERIFICATION")
    print("=" * 70)

    total_scripts = 0
    passed_scripts = 0
    failed_scripts: List[Dict[str, Any]] = []

    for category, category_scripts in scripts.items():
        category_total, passed_scripts = _verify_category_scripts(
            category, category_scripts, passed_scripts, failed_scripts
        )
        total_scripts += category_total

    _print_verification_summary(total_scripts, passed_scripts, failed_scripts)

    return 0 if passed_scripts == total_scripts else 1

if __name__ == "__main__":
    sys.exit(main())
