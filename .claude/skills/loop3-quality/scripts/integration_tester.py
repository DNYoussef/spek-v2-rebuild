#!/usr/bin/env python3
"""
Integration Tester - E2E test orchestration

Atomic skill helper for Loop 3 Quality phase.
Handles Playwright/Cypress detection and test execution.

VERSION: 1.0.0
USAGE: python integration_tester.py --suite e2e
"""

import json
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class IntegrationTester:
    """Orchestrates E2E and integration testing."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize integration tester.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.test_results_dir = self.project_root / "test-results"
        self.test_results_dir.mkdir(exist_ok=True)

    def detect_test_framework(self) -> Dict[str, Any]:
        """
        Detect E2E test framework.

        Returns:
            Dict with framework detection
        """
        try:
            frameworks = {
                "playwright": self._check_playwright(),
                "cypress": self._check_cypress(),
                "pytest": self._check_pytest()
            }

            detected = [name for name, exists in frameworks.items() if exists]

            return {
                "success": True,
                "frameworks": detected,
                "primary": detected[0] if detected else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_e2e_tests(
        self, framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run E2E tests.

        Args:
            framework: Test framework to use (auto-detect if None)

        Returns:
            Dict with test results
        """
        if not framework:
            detection = self.detect_test_framework()
            if not detection["success"] or not detection["primary"]:
                return {
                    "success": False,
                    "error": "No E2E framework detected"
                }
            framework = detection["primary"]

        try:
            if framework == "playwright":
                return self._run_playwright_tests()
            elif framework == "cypress":
                return self._run_cypress_tests()
            elif framework == "pytest":
                return self._run_pytest_tests()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported framework: {framework}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_integration_tests(self) -> Dict[str, Any]:
        """
        Run integration tests.

        Returns:
            Dict with test results
        """
        try:
            test_dir = self.project_root / "tests" / "integration"

            if not test_dir.exists():
                return {
                    "success": False,
                    "error": "No integration tests found"
                }

            result = subprocess.run(
                ["pytest", str(test_dir), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=600
            )

            return self._parse_pytest_output(result)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test suites.

        Returns:
            Dict with combined results
        """
        e2e_result = self.run_e2e_tests()
        integration_result = self.run_integration_tests()

        all_passed = (
            e2e_result.get("passed", False) and
            integration_result.get("passed", False)
        )

        return {
            "success": True,
            "all_passed": all_passed,
            "e2e": e2e_result,
            "integration": integration_result,
            "timestamp": datetime.now().isoformat()
        }

    def _check_playwright(self) -> bool:
        """Check if Playwright is available."""
        return (
            (self.project_root / "playwright.config.ts").exists() or
            (self.project_root / "playwright.config.js").exists()
        )

    def _check_cypress(self) -> bool:
        """Check if Cypress is available."""
        return (self.project_root / "cypress.config.ts").exists()

    def _check_pytest(self) -> bool:
        """Check if pytest is available."""
        return (self.project_root / "pytest.ini").exists()

    def _run_playwright_tests(self) -> Dict[str, Any]:
        """Run Playwright tests."""
        try:
            result = subprocess.run(
                ["npx", "playwright", "test"],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self.project_root)
            )

            return self._parse_playwright_output(result)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_cypress_tests(self) -> Dict[str, Any]:
        """Run Cypress tests."""
        try:
            result = subprocess.run(
                ["npx", "cypress", "run"],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self.project_root)
            )

            return self._parse_cypress_output(result)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_pytest_tests(self) -> Dict[str, Any]:
        """Run pytest tests."""
        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self.project_root)
            )

            return self._parse_pytest_output(result)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_playwright_output(
        self, result: subprocess.CompletedProcess
    ) -> Dict[str, Any]:
        """Parse Playwright test output."""
        output = result.stdout

        # Simple parsing (can be enhanced)
        passed = result.returncode == 0

        return {
            "success": True,
            "framework": "playwright",
            "passed": passed,
            "output": output,
            "return_code": result.returncode
        }

    def _parse_cypress_output(
        self, result: subprocess.CompletedProcess
    ) -> Dict[str, Any]:
        """Parse Cypress test output."""
        output = result.stdout

        passed = result.returncode == 0

        return {
            "success": True,
            "framework": "cypress",
            "passed": passed,
            "output": output,
            "return_code": result.returncode
        }

    def _parse_pytest_output(
        self, result: subprocess.CompletedProcess
    ) -> Dict[str, Any]:
        """Parse pytest output."""
        output = result.stdout

        # Extract test counts from output
        passed_count = output.count(" PASSED")
        failed_count = output.count(" FAILED")

        return {
            "success": True,
            "framework": "pytest",
            "passed": result.returncode == 0,
            "tests_passed": passed_count,
            "tests_failed": failed_count,
            "output": output,
            "return_code": result.returncode
        }


if __name__ == "__main__":
    # Example usage
    tester = IntegrationTester()

    # Detect frameworks
    detection = tester.detect_test_framework()
    print("Framework detection:")
    print(json.dumps(detection, indent=2))

    # Run all tests
    results = tester.run_all_tests()
    print("\nTest results:")
    print(json.dumps(results, indent=2))
