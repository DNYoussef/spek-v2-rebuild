#!/usr/bin/env python3
"""
Test Runner - Atomic Skill Helper Script

Executes test suite and returns structured results.
Supports: npm (Jest/Vitest), pytest, Playwright

VERSION: 1.0.0
USAGE: python test_runner.py [--framework auto|npm|pytest|playwright] [--target path/to/tests]
"""

import subprocess
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional


class TestRunner:
    """Atomic skill helper for running tests."""

    TEST_COMMANDS = {
        "npm": "npm test",
        "pytest": "pytest --cov=src --cov-report=term-missing -v",
        "playwright": "npx playwright test",
        "jest": "npx jest --coverage",
        "vitest": "npx vitest run"
    }

    def __init__(self, framework: str = "auto", target: Optional[str] = None, timeout: int = 300):
        self.framework = framework if framework != "auto" else self.detect_framework()
        self.target = target
        self.timeout = timeout

    def detect_framework(self) -> str:
        """Auto-detect test framework from project files."""
        if Path("package.json").exists():
            with open("package.json") as f:
                content = f.read()
                if "jest" in content:
                    return "jest"
                elif "vitest" in content:
                    return "vitest"
                elif "playwright" in content:
                    return "playwright"
                else:
                    return "npm"  # Default to npm test

        if Path("pytest.ini").exists() or Path("setup.py").exists():
            return "pytest"

        return "npm"  # Fallback

    def build_command(self) -> str:
        """Build test command with optional target."""
        command = self.TEST_COMMANDS.get(self.framework, "npm test")

        if self.target:
            command += f" {self.target}"

        return command

    def parse_npm_output(self, stdout: str, stderr: str, exit_code: int) -> Dict[str, Any]:
        """Parse npm test (Jest/Vitest) output."""
        # Extract test counts
        total_match = re.search(r'Tests:\s+(\d+)\s+total', stdout)
        passed_match = re.search(r'(\d+)\s+passed', stdout)
        failed_match = re.search(r'(\d+)\s+failed', stdout)

        # Extract coverage
        coverage_match = re.search(r'All files\s+\|\s+([\d.]+)', stdout)

        # Extract failed test names
        failed_tests = re.findall(r'●\s+(.+?)(?:\n|$)', stdout)

        return {
            "passed": exit_code == 0,
            "total": int(total_match.group(1)) if total_match else 0,
            "passed_count": int(passed_match.group(1)) if passed_match else 0,
            "failed_count": int(failed_match.group(1)) if failed_match else 0,
            "coverage": float(coverage_match.group(1)) if coverage_match else 0.0,
            "failed_tests": failed_tests,
            "framework": self.framework
        }

    def parse_pytest_output(self, stdout: str, stderr: str, exit_code: int) -> Dict[str, Any]:
        """Parse pytest output."""
        # Extract test counts
        summary_match = re.search(r'=+\s+(\d+)\s+passed.*?in\s+([\d.]+)s', stdout)
        failed_match = re.search(r'(\d+)\s+failed', stdout)

        # Extract coverage from coverage report
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', stdout)

        # Extract failed test names
        failed_tests = re.findall(r'FAILED\s+(.+?)\s+-', stdout)

        passed_count = int(summary_match.group(1)) if summary_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0

        return {
            "passed": exit_code == 0,
            "total": passed_count + failed_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "coverage": float(coverage_match.group(1)) if coverage_match else 0.0,
            "failed_tests": failed_tests,
            "framework": self.framework
        }

    def parse_playwright_output(self, stdout: str, stderr: str, exit_code: int) -> Dict[str, Any]:
        """Parse Playwright output."""
        # Extract test counts
        passed_match = re.search(r'(\d+)\s+passed', stdout)
        failed_match = re.search(r'(\d+)\s+failed', stdout)

        # Extract failed test names
        failed_tests = re.findall(r'✘\s+\[.+?\]\s+›\s+(.+)', stdout)

        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0

        return {
            "passed": exit_code == 0,
            "total": passed_count + failed_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "coverage": 0.0,  # Playwright doesn't provide coverage by default
            "failed_tests": failed_tests,
            "framework": self.framework
        }

    def _parse_test_output(
        self, stdout: str, stderr: str, exit_code: int
    ) -> Dict[str, Any]:
        """Parse test output based on framework."""
        if self.framework in ["npm", "jest", "vitest"]:
            return self.parse_npm_output(stdout, stderr, exit_code)
        elif self.framework == "pytest":
            return self.parse_pytest_output(stdout, stderr, exit_code)
        elif self.framework == "playwright":
            return self.parse_playwright_output(stdout, stderr, exit_code)
        else:
            return {
                "passed": exit_code == 0,
                "total": 0,
                "passed_count": 0,
                "failed_count": 0,
                "coverage": 0.0,
                "failed_tests": [],
                "framework": self.framework
            }

    def _add_metadata(
        self, parsed: Dict[str, Any], command: str, exit_code: int, stdout: str, stderr: str
    ) -> Dict[str, Any]:
        """Add metadata and recommendation to parsed results."""
        parsed["skill"] = "test-runner"
        parsed["command"] = command
        parsed["exit_code"] = exit_code
        parsed["stdout"] = stdout[:500]
        parsed["stderr"] = stderr[:500] if stderr else ""

        if parsed["passed"]:
            parsed["recommendation"] = "All tests passed ✅ Proceed to next gate"
        else:
            parsed["recommendation"] = f"Fix {parsed['failed_count']} failing tests before proceeding"

        return parsed

    def run(self) -> Dict[str, Any]:
        """Execute tests and return structured results."""
        command = self.build_command()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode

            # Parse output
            parsed = self._parse_test_output(stdout, stderr, exit_code)

            # Add metadata
            return self._add_metadata(parsed, command, exit_code, stdout, stderr)

        except subprocess.TimeoutExpired:
            return {
                "skill": "test-runner",
                "passed": False,
                "error": f"Tests exceeded {self.timeout}s timeout",
                "recommendation": "Optimize slow tests or increase timeout",
                "framework": self.framework
            }
        except Exception as e:
            return {
                "skill": "test-runner",
                "passed": False,
                "error": str(e),
                "recommendation": f"Fix test execution error: {str(e)}",
                "framework": self.framework
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Runner - Atomic Skill Helper")
    parser.add_argument("--framework", default="auto", choices=["auto", "npm", "pytest", "playwright", "jest", "vitest"],
                       help="Test framework (default: auto-detect)")
    parser.add_argument("--target", help="Specific test file or pattern")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds (default: 300)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    runner = TestRunner(framework=args.framework, target=args.target, timeout=args.timeout)
    result = runner.run()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"\n{'='*60}")
        print(f"TEST RUNNER - {result['framework'].upper()}")
        print(f"{'='*60}\n")

        if result["passed"]:
            print(f"✅ Status: ALL TESTS PASSED")
            print(f"📊 Total: {result.get('total', 0)} tests")
            print(f"✅ Passed: {result.get('passed_count', 0)}")
            print(f"📈 Coverage: {result.get('coverage', 0):.1f}%")
        else:
            print(f"❌ Status: TESTS FAILED")
            print(f"📊 Total: {result.get('total', 0)} tests")
            print(f"✅ Passed: {result.get('passed_count', 0)}")
            print(f"❌ Failed: {result.get('failed_count', 0)}")
            if result.get('failed_tests'):
                print(f"\n❌ Failed Tests:")
                for test in result['failed_tests'][:10]:  # Show first 10
                    print(f"   - {test}")

        print(f"\n🔧 Recommendation: {result['recommendation']}\n")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
