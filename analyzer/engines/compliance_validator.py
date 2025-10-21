"""
Compliance Validator - Multi-standard compliance validation

Validates code against NASA POT10, DFARS, ISO27001, and custom
standards. Calculates compliance scores and generates recommendations.

NASA Rule 3 Compliance: ≤213 LOC target
Version: 6.0.0 (Week 2 Day 2)
"""

import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ComplianceValidator:
    """
    Multi-standard compliance validation engine.

    Supports:
    - NASA POT10 (Power of Ten safety rules)
    - DFARS (Defense Federal Acquisition Regulation)
    - ISO27001 (Information security standard)
    - Custom standards
    """

    def __init__(self):
        """Initialize compliance validator with standards."""
        self.logger = logging.getLogger(__name__)
        self.standards_config = self._initialize_standards()

    def validate(self, analysis_results: Dict[str, Any],
                 standards: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate compliance against multiple standards.

        Args:
            analysis_results: Analysis results from SyntaxAnalyzer/PatternDetector
            standards: List of standards to validate (default: all)

        Returns:
            Dict with overall_score, individual_scores, recommendations
        """
        # Validation
        assert analysis_results, "analysis_results cannot be empty"
        standards = standards or ["NASA_POT10", "DFARS", "ISO27001"]

        start_time = time.time()
        compliance_results = {}

        try:
            # Validate each standard
            for standard in standards:
                if standard == "NASA_POT10":
                    compliance_results[standard] = self._validate_nasa_pot10(analysis_results)
                elif standard == "DFARS":
                    compliance_results[standard] = self._validate_dfars(analysis_results)
                elif standard == "ISO27001":
                    compliance_results[standard] = self._validate_iso27001(analysis_results)
                else:
                    compliance_results[standard] = self._validate_generic(analysis_results, standard)

            # Calculate overall compliance score
            scores = [result.get("score", 0.0) for result in compliance_results.values()]
            overall_score = sum(scores) / len(scores) if scores else 0.0

            execution_time = time.time() - start_time

            return {
                "success": True,
                "overall_score": overall_score,
                "standards": standards,
                "individual_scores": compliance_results,
                "execution_time": execution_time,
                "recommendations": self._generate_recommendations(compliance_results)
            }

        except Exception as e:
            self.logger.error(f"Compliance validation failed: {e}")
            return {
                "success": False,
                "overall_score": 0.0,
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    def _validate_nasa_pot10(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate NASA Power of Ten compliance.

        NASA POT10 Rules:
        - Rule 3: Functions ≤60 lines
        - Rule 4: ≥2 assertions per function
        - Rule 5: No recursion
        - Rule 6: ≤6 parameters
        - Rule 7: Fixed loop bounds
        """
        # Extract issue counts
        syntax_issues = results.get("syntax_issues", [])

        # Count critical violations
        nasa_violations = [
            issue for issue in syntax_issues
            if issue.get("type") in [
                "nasa_rule_3_violation",  # Function length
                "nasa_rule_4_violation",  # Assertions
                "nasa_rule_5_violation",  # Recursion
                "nasa_rule_6_violation",  # Parameters
                "nasa_rule_7_violation"   # Loop bounds
            ]
        ]

        critical_count = len([v for v in nasa_violations if v.get("severity") == "critical"])
        total_issues = len(syntax_issues)

        # Calculate compliance score (92% threshold)
        compliance_score = 1.0 - (critical_count / max(total_issues, 1))
        passed = compliance_score >= 0.92

        return {
            "score": compliance_score,
            "passed": passed,
            "critical_violations": critical_count,
            "total_violations": len(nasa_violations),
            "rules_checked": ["RULE_3", "RULE_4", "RULE_5", "RULE_6", "RULE_7"],
            "recommendations": [
                "Address all critical NASA POT10 violations",
                "Aim for ≥92% compliance score"
            ] if not passed else []
        }

    def _validate_dfars(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate DFARS 252.204-7012 compliance.

        DFARS Requirements:
        - Adequate security controls
        - Incident response procedures
        - Security assessments
        """
        # Extract security-related issues
        syntax_issues = results.get("syntax_issues", [])
        security_issues = [
            issue for issue in syntax_issues
            if issue.get("type") in ["security_risk", "vulnerability"]
        ]

        # Calculate security compliance score
        critical_security = len([i for i in security_issues if i.get("severity") == "critical"])
        compliance_score = 1.0 - (critical_security * 0.1)  # Each critical issue = -10%
        compliance_score = max(0.0, min(1.0, compliance_score))

        passed = compliance_score >= 0.95

        return {
            "score": compliance_score,
            "passed": passed,
            "security_violations": len(security_issues),
            "critical_security_violations": critical_security,
            "sections_checked": ["252.204-7012"],
            "recommendations": [
                "Address all critical security vulnerabilities",
                "Implement secure coding practices"
            ] if not passed else []
        }

    def _validate_iso27001(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ISO27001 A.14.2.1 compliance.

        ISO27001 Requirements:
        - Secure development lifecycle
        - Code review procedures
        - Security testing
        """
        # Extract quality and security issues
        syntax_issues = results.get("syntax_issues", [])

        quality_issues = [
            issue for issue in syntax_issues
            if issue.get("severity") in ["high", "critical"]
        ]

        # Calculate quality compliance score
        compliance_score = 1.0 - (len(quality_issues) * 0.05)  # Each issue = -5%
        compliance_score = max(0.0, min(1.0, compliance_score))

        passed = compliance_score >= 0.85

        return {
            "score": compliance_score,
            "passed": passed,
            "quality_violations": len(quality_issues),
            "controls_checked": ["A.14.2.1"],
            "recommendations": [
                "Implement secure development lifecycle",
                "Conduct regular code reviews"
            ] if not passed else []
        }

    def _validate_generic(self, results: Dict[str, Any], standard: str) -> Dict[str, Any]:
        """
        Generic compliance validation for custom standards.

        Provides basic compliance scoring based on issue severity.
        """
        syntax_issues = results.get("syntax_issues", [])

        # Simple scoring based on issue count
        compliance_score = max(0.0, 1.0 - (len(syntax_issues) * 0.02))

        return {
            "score": compliance_score,
            "passed": compliance_score >= 0.80,
            "total_issues": len(syntax_issues),
            "standard": standard,
            "recommendations": [
                f"Address issues to improve {standard} compliance"
            ] if compliance_score < 0.80 else []
        }

    def _generate_recommendations(self, compliance_results: Dict[str, Any]) -> List[str]:
        """
        Generate compliance recommendations based on results.

        Args:
            compliance_results: Individual compliance results

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        for standard, result in compliance_results.items():
            if not result.get("passed", True):
                recommendations.append(f"❌ {standard}: {result.get('score', 0.0):.1%} compliance - FAILED")
                recommendations.extend(result.get("recommendations", []))
            else:
                recommendations.append(f"✅ {standard}: {result.get('score', 0.0):.1%} compliance - PASSED")

        # Add overall recommendation if any failed
        if any(not r.get("passed", True) for r in compliance_results.values()):
            recommendations.insert(0, "⚠️  Address compliance violations before production deployment")

        return recommendations

    def _initialize_standards(self) -> Dict[str, Any]:
        """Initialize standards configuration."""
        return {
            "NASA_POT10": {
                "rules": ["RULE_3", "RULE_4", "RULE_5", "RULE_6", "RULE_7"],
                "threshold": 0.92
            },
            "DFARS": {
                "sections": ["252.204-7012"],
                "threshold": 0.95
            },
            "ISO27001": {
                "controls": ["A.14.2.1"],
                "threshold": 0.85
            }
        }


# Factory function
def create_compliance_validator() -> ComplianceValidator:
    """Create and return ComplianceValidator instance."""
    return ComplianceValidator()
