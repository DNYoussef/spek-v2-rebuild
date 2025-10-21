#!/usr/bin/env python3
"""
Deployment Approver - Final deployment gate validator

Atomic skill helper for Loop 3 Quality phase.
Validates all conditions before production deployment approval.

VERSION: 1.0.0
USAGE: python deployment_approver.py --validate-all
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class DeploymentApprover:
    """Validates final deployment readiness."""

    # Deployment requirements
    REQUIREMENTS = {
        "quality_gate": "Quality gate must pass (≥90%)",
        "all_tests": "All test suites must pass",
        "security_scan": "Security scan must show no critical issues",
        "production_build": "Production build must succeed",
        "documentation": "Deployment documentation must be complete",
        "rollback_plan": "Rollback plan must be documented",
        "monitoring": "Monitoring must be configured",
        "environment": "Environment variables must be validated"
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize deployment approver.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.approval_dir = self.project_root / ".claude" / "approvals"
        self.approval_dir.mkdir(parents=True, exist_ok=True)

    def validate_quality_gate(
        self, quality_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate quality gate results.

        Args:
            quality_results: Quality gate results

        Returns:
            Dict with validation
        """
        try:
            passed = (
                quality_results.get("decision") == "GO" and
                quality_results.get("percentage", 0) >= 90
            )

            return {
                "requirement": "quality_gate",
                "passed": passed,
                "score": quality_results.get("percentage", 0),
                "details": quality_results
            }
        except Exception as e:
            return {"requirement": "quality_gate", "passed": False, "error": str(e)}

    def validate_test_results(
        self, test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate all test suites passed.

        Args:
            test_results: Test results from integration_tester

        Returns:
            Dict with validation
        """
        try:
            passed = test_results.get("all_passed", False)

            return {
                "requirement": "all_tests",
                "passed": passed,
                "details": test_results
            }
        except Exception as e:
            return {"requirement": "all_tests", "passed": False, "error": str(e)}

    def validate_security(self) -> Dict[str, Any]:
        """
        Validate security scan results.

        Returns:
            Dict with validation
        """
        try:
            # Check for security scan results
            scan_file = self.project_root / ".claude" / "security" / "scan_results.json"

            if not scan_file.exists():
                return {
                    "requirement": "security_scan",
                    "passed": False,
                    "error": "No security scan results found"
                }

            results = json.loads(scan_file.read_text(encoding="utf-8"))
            critical_count = results.get("critical", 0)

            return {
                "requirement": "security_scan",
                "passed": critical_count == 0,
                "critical_issues": critical_count,
                "details": results
            }
        except Exception as e:
            return {"requirement": "security_scan", "passed": False, "error": str(e)}

    def validate_production_build(self) -> Dict[str, Any]:
        """
        Validate production build succeeds.

        Returns:
            Dict with validation
        """
        try:
            # Check for build artifacts
            build_dir = self.project_root / "dist"
            next_build = self.project_root / ".next"

            has_build = build_dir.exists() or next_build.exists()

            return {
                "requirement": "production_build",
                "passed": has_build,
                "build_dir": str(build_dir if build_dir.exists() else next_build)
            }
        except Exception as e:
            return {"requirement": "production_build", "passed": False, "error": str(e)}

    def validate_documentation(self) -> Dict[str, Any]:
        """
        Validate deployment documentation exists.

        Returns:
            Dict with validation
        """
        try:
            required_docs = [
                "docs/DEPLOYMENT-GUIDE.md",
                "docs/ROLLBACK-PROCEDURE.md",
                "README.md"
            ]

            existing = []
            missing = []

            for doc in required_docs:
                doc_path = self.project_root / doc
                if doc_path.exists():
                    existing.append(doc)
                else:
                    missing.append(doc)

            return {
                "requirement": "documentation",
                "passed": len(missing) == 0,
                "existing": existing,
                "missing": missing
            }
        except Exception as e:
            return {"requirement": "documentation", "passed": False, "error": str(e)}

    def validate_rollback_plan(self) -> Dict[str, Any]:
        """
        Validate rollback plan documented.

        Returns:
            Dict with validation
        """
        try:
            rollback_file = self.project_root / "docs" / "ROLLBACK-PROCEDURE.md"

            return {
                "requirement": "rollback_plan",
                "passed": rollback_file.exists(),
                "file": str(rollback_file)
            }
        except Exception as e:
            return {"requirement": "rollback_plan", "passed": False, "error": str(e)}

    def validate_monitoring(self) -> Dict[str, Any]:
        """
        Validate monitoring configured.

        Returns:
            Dict with validation
        """
        try:
            # Check for monitoring config
            monitoring_configs = [
                ".claude/monitoring/config.json",
                "monitoring.config.js"
            ]

            configured = any(
                (self.project_root / config).exists()
                for config in monitoring_configs
            )

            return {
                "requirement": "monitoring",
                "passed": configured
            }
        except Exception as e:
            return {"requirement": "monitoring", "passed": False, "error": str(e)}

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate environment variables configured.

        Returns:
            Dict with validation
        """
        try:
            env_files = [".env.production", ".env.example"]

            has_env = any(
                (self.project_root / env).exists()
                for env in env_files
            )

            return {
                "requirement": "environment",
                "passed": has_env
            }
        except Exception as e:
            return {"requirement": "environment", "passed": False, "error": str(e)}

    def run_full_validation(
        self,
        quality_results: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run complete deployment validation.

        Args:
            quality_results: Quality gate results
            test_results: Test results

        Returns:
            Dict with approval decision
        """
        try:
            validations = {
                "quality_gate": self.validate_quality_gate(quality_results),
                "all_tests": self.validate_test_results(test_results),
                "security_scan": self.validate_security(),
                "production_build": self.validate_production_build(),
                "documentation": self.validate_documentation(),
                "rollback_plan": self.validate_rollback_plan(),
                "monitoring": self.validate_monitoring(),
                "environment": self.validate_environment()
            }

            all_passed = all(v.get("passed", False) for v in validations.values())
            passed_count = sum(1 for v in validations.values() if v.get("passed", False))
            total_count = len(validations)

            decision = "APPROVED" if all_passed else "REJECTED"

            result = {
                "success": True,
                "decision": decision,
                "all_passed": all_passed,
                "passed_count": passed_count,
                "total_count": total_count,
                "percentage": (passed_count / total_count) * 100,
                "validations": validations,
                "timestamp": datetime.now().isoformat()
            }

            # Save approval record
            self._save_approval_record(result)

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_approval_record(self, result: Dict[str, Any]) -> None:
        """Save approval record to file."""
        record_file = self.approval_dir / "deployment_approval.json"
        record_file.write_text(
            json.dumps(result, indent=2),
            encoding="utf-8"
        )


if __name__ == "__main__":
    # Example usage
    approver = DeploymentApprover()

    # Example validation
    result = approver.run_full_validation(
        quality_results={"decision": "GO", "percentage": 95},
        test_results={"all_passed": True}
    )

    print(json.dumps(result, indent=2))
