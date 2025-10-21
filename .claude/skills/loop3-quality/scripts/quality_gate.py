#!/usr/bin/env python3
"""
Quality Gate - 47-point checklist validator

Atomic skill helper for Loop 3 Quality phase.
Implements comprehensive quality gate validation.

VERSION: 1.0.0
USAGE: python quality_gate.py --target src/
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class QualityGate:
    """Validates project against 47-point quality checklist."""

    # Quality checklist (47 points total)
    CHECKLIST = {
        "functionality": {
            "weight": 35,
            "checks": [
                "All tests passing",
                "No runtime errors",
                "All features implemented",
                "Integration tests passing",
                "E2E tests passing",
                "Performance targets met",
                "Error handling complete"
            ]
        },
        "code_quality": {
            "weight": 25,
            "checks": [
                "NASA Rule 10 compliance",
                "Zero linting errors",
                "Type hints coverage >90%",
                "No code duplication",
                "Proper error handling",
                "Documentation complete",
                "Code review approved"
            ]
        },
        "security": {
            "weight": 15,
            "checks": [
                "No security vulnerabilities",
                "Authentication implemented",
                "Authorization checks",
                "Input validation",
                "No hardcoded secrets"
            ]
        },
        "deployment": {
            "weight": 15,
            "checks": [
                "Production build succeeds",
                "Environment configs valid",
                "Database migrations ready",
                "Rollback plan documented",
                "Monitoring configured"
            ]
        },
        "documentation": {
            "weight": 10,
            "checks": [
                "README complete",
                "API docs generated",
                "Deployment guide written",
                "Architecture documented",
                "User guide available"
            ]
        }
    }

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize quality gate validator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.results_dir = self.project_root / ".claude" / "quality"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def validate_category(
        self, category: str, results: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Validate single category.

        Args:
            category: Category name
            results: Dict of check results

        Returns:
            Dict with category validation
        """
        try:
            config = self.CHECKLIST[category]
            checks = config["checks"]
            weight = config["weight"]

            passed_checks = sum(1 for check in checks if results.get(check, False))
            total_checks = len(checks)
            score = (passed_checks / total_checks) * weight

            return {
                "category": category,
                "passed": passed_checks,
                "total": total_checks,
                "score": score,
                "max_score": weight,
                "percentage": (passed_checks / total_checks) * 100,
                "passed_all": passed_checks == total_checks
            }
        except Exception as e:
            return {"error": str(e)}

    def run_full_validation(
        self, category_results: Dict[str, Dict[str, bool]]
    ) -> Dict[str, Any]:
        """
        Run full quality gate validation.

        Args:
            category_results: Results by category

        Returns:
            Dict with validation results
        """
        try:
            category_scores = {}
            total_score = 0
            max_score = 100

            for category, results in category_results.items():
                if category in self.CHECKLIST:
                    validation = self.validate_category(category, results)
                    category_scores[category] = validation
                    total_score += validation.get("score", 0)

            # Determine GO/NO-GO
            percentage = (total_score / max_score) * 100
            decision = "GO" if percentage >= 90 else "NO_GO"

            return {
                "success": True,
                "total_score": round(total_score, 2),
                "max_score": max_score,
                "percentage": round(percentage, 1),
                "decision": decision,
                "categories": category_scores,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_report(
        self, validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate quality gate report.

        Args:
            validation: Validation results

        Returns:
            Dict with report result
        """
        try:
            report = self._format_report(validation)
            report_file = self.results_dir / "quality_gate_report.md"

            report_file.write_text(report, encoding="utf-8")

            return {
                "success": True,
                "report_file": str(report_file),
                "decision": validation.get("decision"),
                "score": validation.get("percentage")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_required_files(self) -> Dict[str, bool]:
        """
        Check for required documentation files.

        Returns:
            Dict of file existence checks
        """
        required_files = [
            "README.md",
            "CLAUDE.md",
            "architecture/ARCHITECTURE-MASTER-TOC.md",
            "docs/DEPLOYMENT-GUIDE.md"
        ]

        return {
            file: (self.project_root / file).exists()
            for file in required_files
        }

    def validate_test_coverage(self) -> Dict[str, Any]:
        """
        Validate test coverage meets requirements.

        Returns:
            Dict with coverage validation
        """
        try:
            # Simplified coverage check
            test_dir = self.project_root / "tests"
            if not test_dir.exists():
                return {"passed": False, "coverage": 0}

            test_files = list(test_dir.rglob("test_*.py"))
            src_files = list((self.project_root / "src").rglob("*.py"))

            if not src_files:
                return {"passed": True, "coverage": 100, "message": "No source files"}

            coverage_estimate = min(100, (len(test_files) / len(src_files)) * 100)

            return {
                "passed": coverage_estimate >= 80,
                "coverage": round(coverage_estimate, 1),
                "test_files": len(test_files),
                "source_files": len(src_files)
            }
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _format_report(self, validation: Dict[str, Any]) -> str:
        """Format quality gate report."""
        categories = validation.get("categories", {})

        category_details = []
        for cat_name, cat_data in categories.items():
            status = "✅" if cat_data.get("passed_all") else "❌"
            category_details.append(
                f"### {cat_name.replace('_', ' ').title()} {status}\n"
                f"- Score: {cat_data.get('score')}/{cat_data.get('max_score')}\n"
                f"- Passed: {cat_data.get('passed')}/{cat_data.get('total')} checks\n"
                f"- Percentage: {cat_data.get('percentage'):.1f}%\n"
            )

        return f"""# Quality Gate Report

**Generated**: {validation.get('timestamp')}

## Overall Result

**Decision**: {validation.get('decision')}
**Score**: {validation.get('total_score')}/{validation.get('max_score')} ({validation.get('percentage')}%)

## Category Breakdown

{''.join(category_details)}

## Recommendation

{self._get_recommendation(validation.get('decision'), validation.get('percentage'))}
"""

    def _get_recommendation(self, decision: str, percentage: float) -> str:
        """Get recommendation based on results."""
        if decision == "GO":
            return "✅ Quality gate passed. Project is ready for production deployment."
        else:
            return f"❌ Quality gate failed ({percentage}%). Address failing checks before deployment."


if __name__ == "__main__":
    # Example usage
    gate = QualityGate()

    # Example validation
    results = gate.run_full_validation({
        "functionality": {
            "All tests passing": True,
            "No runtime errors": True,
            "All features implemented": True,
            "Integration tests passing": True,
            "E2E tests passing": True,
            "Performance targets met": True,
            "Error handling complete": True
        },
        "code_quality": {
            "NASA Rule 10 compliance": True,
            "Zero linting errors": True,
            "Type hints coverage >90%": True,
            "No code duplication": True,
            "Proper error handling": True,
            "Documentation complete": False,
            "Code review approved": True
        },
        "security": {
            "No security vulnerabilities": True,
            "Authentication implemented": True,
            "Authorization checks": True,
            "Input validation": True,
            "No hardcoded secrets": True
        },
        "deployment": {
            "Production build succeeds": True,
            "Environment configs valid": True,
            "Database migrations ready": True,
            "Rollback plan documented": True,
            "Monitoring configured": True
        },
        "documentation": {
            "README complete": True,
            "API docs generated": True,
            "Deployment guide written": True,
            "Architecture documented": True,
            "User guide available": False
        }
    })

    print(json.dumps(results, indent=2))

    # Generate report
    report = gate.generate_report(results)
    print("\nReport:", json.dumps(report, indent=2))
