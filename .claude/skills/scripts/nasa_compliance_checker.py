#!/usr/bin/env python3
"""
NASA Compliance Checker - Atomic Skill Helper Script

Enforces NASA Rule 10 for code quality:
- ≤60 lines of code per function
- Type hints present (Python)
- No recursion
- Fixed loop bounds (no while True)

VERSION: 1.0.0
USAGE: python nasa_compliance_checker.py [--path src/] [--max-loc 60]
"""

import ast
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


class NASAComplianceChecker:
    """Atomic skill helper for NASA Rule 10 compliance."""

    def __init__(self, path: str = "src", max_loc: int = 60):
        self.path = Path(path)
        self.max_loc = max_loc
        self.violations = []
        self.functions_checked = 0
        self.compliant_functions = 0

    def check_function_length(self, node: ast.FunctionDef, filename: str) -> Optional[Dict]:
        """Check if function exceeds max LOC."""
        length = node.end_lineno - node.lineno + 1

        if length > self.max_loc:
            return {
                "type": "length",
                "function": node.name,
                "file": str(filename),
                "line": node.lineno,
                "loc": length,
                "max_loc": self.max_loc,
                "severity": "high" if length > self.max_loc * 1.5 else "medium",
                "message": f"Function '{node.name}' has {length} LOC (max {self.max_loc})"
            }
        return None

    def check_type_hints(self, node: ast.FunctionDef, filename: str) -> List[Dict]:
        """Check if function has type hints for args and return."""
        issues = []

        # Check return type
        if node.returns is None and node.name != "__init__":
            issues.append({
                "type": "type_hint",
                "function": node.name,
                "file": str(filename),
                "line": node.lineno,
                "severity": "low",
                "message": f"Function '{node.name}' missing return type hint"
            })

        # Check argument type hints
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self":
                issues.append({
                    "type": "type_hint",
                    "function": node.name,
                    "file": str(filename),
                    "line": node.lineno,
                    "severity": "low",
                    "message": f"Argument '{arg.arg}' in '{node.name}' missing type hint"
                })

        return issues

    def check_recursion(self, node: ast.FunctionDef, filename: str) -> Optional[Dict]:
        """Check if function contains recursion."""
        function_name = node.name

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id == function_name:
                    return {
                        "type": "recursion",
                        "function": function_name,
                        "file": str(filename),
                        "line": child.lineno,
                        "severity": "high",
                        "message": f"Function '{function_name}' contains recursion (NASA Rule 10 violation)"
                    }
        return None

    def check_unbounded_loops(self, node: ast.FunctionDef, filename: str) -> List[Dict]:
        """Check for unbounded while loops (while True)."""
        issues = []

        for child in ast.walk(node):
            if isinstance(child, ast.While):
                # Check if condition is True (unbounded)
                if isinstance(child.test, ast.Constant) and child.test.value is True:
                    issues.append({
                        "type": "unbounded_loop",
                        "function": node.name,
                        "file": str(filename),
                        "line": child.lineno,
                        "severity": "medium",
                        "message": f"Unbounded loop 'while True' in '{node.name}' (use fixed iterations)"
                    })

        return issues

    def analyze_file(self, filepath: Path) -> List[Dict]:
        """Analyze a single Python file for NASA compliance."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))

            file_violations = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.functions_checked += 1

                    # Check function length
                    length_violation = self.check_function_length(node, filepath)
                    if length_violation:
                        file_violations.append(length_violation)

                    # Check type hints
                    type_violations = self.check_type_hints(node, filepath)
                    file_violations.extend(type_violations)

                    # Check recursion
                    recursion_violation = self.check_recursion(node, filepath)
                    if recursion_violation:
                        file_violations.append(recursion_violation)

                    # Check unbounded loops
                    loop_violations = self.check_unbounded_loops(node, filepath)
                    file_violations.extend(loop_violations)

                    # If no violations, count as compliant
                    if not length_violation and not type_violations and not recursion_violation and not loop_violations:
                        self.compliant_functions += 1

            return file_violations

        except SyntaxError as e:
            return [{
                "type": "syntax_error",
                "file": str(filepath),
                "line": e.lineno,
                "severity": "critical",
                "message": f"Syntax error: {e.msg}"
            }]
        except Exception as e:
            return [{
                "type": "analysis_error",
                "file": str(filepath),
                "severity": "critical",
                "message": f"Error analyzing file: {str(e)}"
            }]

    def _analyze_all_files(self) -> None:
        """Analyze all Python files and collect violations."""
        python_files = list(self.path.rglob("*.py"))

        for filepath in python_files:
            file_violations = self.analyze_file(filepath)
            self.violations.extend(file_violations)

    def _build_response(
        self,
        compliant: bool,
        compliance_rate: float,
        critical: List[Dict],
        high: List[Dict],
        medium: List[Dict],
        low: List[Dict]
    ) -> Dict[str, Any]:
        """Build response dictionary with recommendation."""
        response = {
            "skill": "nasa-compliance-checker",
            "compliant": compliant,
            "compliance_rate": round(compliance_rate, 1),
            "functions_checked": self.functions_checked,
            "compliant_functions": self.compliant_functions,
            "total_violations": len(self.violations),
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
            "violations": self.violations[:20],
            "max_loc": self.max_loc
        }

        # Add recommendation
        if compliant:
            response["recommendation"] = f"NASA compliance: {compliance_rate:.1f}% ✅ Meets target (≥96%)"
        elif len(critical) > 0:
            response["recommendation"] = f"CRITICAL: {len(critical)} syntax/analysis errors must be fixed"
        elif len(high) > 0:
            response["recommendation"] = f"HIGH: {len(high)} functions exceed {self.max_loc} LOC or use recursion. Refactor required."
        else:
            response["recommendation"] = f"Compliance: {compliance_rate:.1f}% (target: ≥96%). Add type hints and fix medium issues."

        return response

    def run(self) -> Dict[str, Any]:
        """Analyze all Python files in path."""
        if not self.path.exists():
            return {
                "skill": "nasa-compliance-checker",
                "compliant": False,
                "error": f"Path not found: {self.path}",
                "recommendation": "Check path and try again"
            }

        # Find all Python files
        python_files = list(self.path.rglob("*.py"))

        if not python_files:
            return {
                "skill": "nasa-compliance-checker",
                "compliant": True,
                "message": "No Python files found in path",
                "recommendation": "No action needed"
            }

        # Analyze all files
        self._analyze_all_files()

        # Calculate compliance percentage
        compliance_rate = (self.compliant_functions / self.functions_checked * 100) if self.functions_checked > 0 else 100.0

        # Group violations by severity
        critical = [v for v in self.violations if v.get("severity") == "critical"]
        high = [v for v in self.violations if v.get("severity") == "high"]
        medium = [v for v in self.violations if v.get("severity") == "medium"]
        low = [v for v in self.violations if v.get("severity") == "low"]

        # Determine compliance
        compliant = compliance_rate >= 96.0 and len(critical) == 0 and len(high) == 0

        return self._build_response(
            compliant, compliance_rate, critical, high, medium, low
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="NASA Compliance Checker - Atomic Skill Helper")
    parser.add_argument("--path", default="src", help="Path to analyze (default: src)")
    parser.add_argument("--max-loc", type=int, default=60, help="Max lines per function (default: 60)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    checker = NASAComplianceChecker(path=args.path, max_loc=args.max_loc)
    result = checker.run()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"NASA COMPLIANCE CHECKER")
        print(f"{'='*60}\n")

        if result.get("compliant"):
            print(f"✅ Status: NASA COMPLIANT")
            print(f"📊 Compliance Rate: {result['compliance_rate']:.1f}% (target: ≥96%)")
            print(f"✅ Functions Checked: {result['functions_checked']}")
            print(f"✅ Compliant Functions: {result['compliant_functions']}")
        else:
            print(f"❌ Status: NASA VIOLATIONS FOUND")
            print(f"📊 Compliance Rate: {result['compliance_rate']:.1f}% (target: ≥96%)")
            print(f"📊 Functions Checked: {result['functions_checked']}")
            print(f"⚠️  Total Violations: {result['total_violations']}")
            print(f"\n❌ Violations by Severity:")
            print(f"   Critical: {result['critical']}")
            print(f"   High: {result['high']}")
            print(f"   Medium: {result['medium']}")
            print(f"   Low: {result['low']}")

            if result.get('violations'):
                print(f"\n❌ Top Violations (showing first 10):")
                for v in result['violations'][:10]:
                    print(f"   [{v['severity'].upper()}] {v['message']}")
                    print(f"      File: {v['file']}:{v['line']}")

        print(f"\n🔧 Recommendation: {result['recommendation']}\n")

    return 0 if result.get("compliant") else 1


if __name__ == "__main__":
    sys.exit(main())
