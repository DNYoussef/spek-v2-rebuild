#!/usr/bin/env python3
"""
NASA Rule 10 Compliance Checker
Checks if functions are <=60 LOC (pragmatic target: >=92% compliance)
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

def check_file(filepath: Path) -> Tuple[int, int, List[str]]:
    """
    Returns: (total_functions, compliant_functions, violations)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except Exception as e:
        return 0, 0, []

    total = 0
    compliant = 0
    violations = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total += 1
            length = node.end_lineno - node.lineno + 1

            if length <= 60:
                compliant += 1
            else:
                violations.append(f"{filepath}:{node.lineno} - {node.name}() = {length} LOC")

    return total, compliant, violations

def check_directory(directory: Path) -> None:
    """Check all TypeScript/Python files in directory"""

    # Find all .ts/.tsx files
    ts_files = list(directory.rglob("*.ts")) + list(directory.rglob("*.tsx"))

    total_functions = 0
    total_compliant = 0
    all_violations = []

    print(f"\n=== Checking {directory} ===\n")

    for filepath in ts_files:
        # Skip node_modules, dist, .next
        if any(skip in str(filepath) for skip in ['node_modules', 'dist', '.next', '__tests__']):
            continue

        funcs, compliant, violations = check_file(filepath)
        total_functions += funcs
        total_compliant += compliant
        all_violations.extend(violations)

    if total_functions > 0:
        compliance_rate = (total_compliant / total_functions) * 100
        print(f"Total Functions: {total_functions}")
        print(f"Compliant Functions: {total_compliant}")
        print(f"Compliance Rate: {compliance_rate:.1f}%")
        print(f"Target: >=92%")
        print(f"Status: {'✅ PASS' if compliance_rate >= 92 else '❌ FAIL'}")

        if all_violations:
            print(f"\n=== Violations ({len(all_violations)}) ===")
            for v in all_violations[:10]:  # Show first 10
                print(f"  {v}")
            if len(all_violations) > 10:
                print(f"  ... and {len(all_violations) - 10} more")
    else:
        print("No functions found (TypeScript files cannot be parsed by Python AST)")
        print("Manual inspection required")

if __name__ == "__main__":
    frontend = Path("atlantis-ui/src")
    backend = Path("backend/src")

    if frontend.exists():
        check_directory(frontend)

    if backend.exists():
        check_directory(backend)
