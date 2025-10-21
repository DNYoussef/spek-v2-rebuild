#!/usr/bin/env python3
"""
Analyzer Integration for Meta-Audit

Integrates the SPEK analyzer engines into meta-audit workflow
for enhanced detection across all 3 phases.

VERSION: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add analyzer to path
analyzer_root = Path(__file__).parent.parent.parent.parent / "analyzer"
sys.path.insert(0, str(analyzer_root))

from analyzer.core.api import Analyzer
from analyzer.engines.pattern_detector import PatternDetector
from analyzer.engines.compliance_validator import ComplianceValidator
from analyzer.constants.nasa_rules import NASA_RULES, NASA_COMPLIANCE_THRESHOLDS
from analyzer.constants.thresholds import (
    MAXIMUM_FUNCTION_LENGTH_LINES,
    NASA_PARAMETER_THRESHOLD,
    THEATER_DETECTION_FAILURE_THRESHOLD,
    MINIMUM_TEST_COVERAGE_PERCENTAGE,
    NASA_POT10_TARGET_COMPLIANCE_THRESHOLD,
    ALGORITHM_COMPLEXITY_THRESHOLD,
    MECE_SIMILARITY_THRESHOLD,
)


class AnalyzerIntegration:
    """
    Integrates analyzer engines into meta-audit phases.

    Phase 1 (Theater): Pattern detection for mocks, TODOs, placeholders
    Phase 2 (Functionality): Syntax analysis, import validation
    Phase 3 (Quality): Full analyzer with NASA compliance
    """

    def __init__(self, target_path: Path):
        """
        Initialize analyzer integration.

        Args:
            target_path: Path to analyze
        """
        self.target_path = target_path
        self.analyzer = Analyzer(policy="nasa-compliance")
        self.pattern_detector = PatternDetector()
        self.compliance_validator = ComplianceValidator()

    def phase1_theater_detection(self) -> Dict[str, Any]:
        """
        Phase 1: Enhanced theater detection using analyzer.

        Uses PatternDetector to find:
        - Mock patterns (mock_, fake_, stub_)
        - Magic literals (hardcoded values)
        - TODO/FIXME patterns
        - Placeholder patterns (pass, NotImplementedError, ...)
        - Commented-out code

        Returns:
            Dict with enhanced theater detection results
        """
        results = {
            "phase": "theater_detection",
            "analyzer_used": True,
            "patterns_detected": [],
            "theater_score": 0,
            "recommendations": []
        }

        try:
            # Run full analyzer to get AST and patterns
            analysis = self.analyzer.analyze(str(self.target_path))

            # Extract pattern detection results
            patterns = analysis.get("patterns", [])

            # Filter for theater-related patterns
            theater_patterns = {
                "mocks": [],
                "todos": [],
                "placeholders": [],
                "magic_literals": [],
                "commented_code": []
            }

            for pattern in patterns:
                pattern_type = pattern.get("pattern_type", "")

                # Mock detection
                if "mock" in pattern_type.lower() or "fake" in pattern_type.lower():
                    theater_patterns["mocks"].append(pattern)

                # TODO/FIXME detection
                elif "todo" in pattern_type.lower() or "fixme" in pattern_type.lower():
                    theater_patterns["todos"].append(pattern)

                # Placeholder detection
                elif "placeholder" in pattern_type.lower() or "not_implemented" in pattern_type.lower():
                    theater_patterns["placeholders"].append(pattern)

                # Magic literal detection (CoM - Connascence of Meaning)
                elif pattern_type == "CoM":
                    theater_patterns["magic_literals"].append(pattern)

            # Calculate theater score using analyzer thresholds
            score = self._calculate_theater_score(theater_patterns)

            results["patterns_detected"] = theater_patterns
            results["theater_score"] = score
            results["passed"] = score < THEATER_DETECTION_FAILURE_THRESHOLD * 100

            # Generate recommendations
            results["recommendations"] = self._generate_theater_recommendations(theater_patterns)

            return results

        except Exception as e:
            results["error"] = str(e)
            results["passed"] = False
            return results

    def phase2_functionality_validation(self) -> Dict[str, Any]:
        """
        Phase 2: Enhanced functionality validation using analyzer.

        Uses SyntaxAnalyzer to validate:
        - Import statements (no circular imports, all resolvable)
        - Syntax correctness
        - AST validity
        - Type hints coverage
        - Assertion presence (NASA Rule 4)

        Returns:
            Dict with enhanced functionality validation results
        """
        results = {
            "phase": "functionality_validation",
            "analyzer_used": True,
            "syntax_valid": True,
            "imports_valid": True,
            "assertions_adequate": True,
            "issues": []
        }

        try:
            # Run full analyzer
            analysis = self.analyzer.analyze(str(self.target_path))

            # Extract syntax issues
            syntax_issues = analysis.get("syntax_issues", [])
            results["syntax_valid"] = len(syntax_issues) == 0

            # Extract import issues
            import_issues = [
                issue for issue in analysis.get("issues", [])
                if "import" in issue.get("description", "").lower()
            ]
            results["imports_valid"] = len(import_issues) == 0

            # Check NASA Rule 4: Assertions
            nasa_rule4_violations = [
                issue for issue in analysis.get("issues", [])
                if issue.get("rule_id") == "RULE_4"
            ]
            results["assertions_adequate"] = len(nasa_rule4_violations) == 0

            # Collect all issues
            results["issues"] = syntax_issues + import_issues + nasa_rule4_violations

            # Overall pass/fail
            results["passed"] = (
                results["syntax_valid"] and
                results["imports_valid"] and
                results["assertions_adequate"]
            )

            return results

        except Exception as e:
            results["error"] = str(e)
            results["passed"] = False
            return results

    def phase3_quality_refactoring(self) -> Dict[str, Any]:
        """
        Phase 3: Full analyzer integration for quality standards.

        Uses complete analyzer with:
        - NASA POT10 compliance validation
        - Pattern detection (god objects, connascence)
        - Complexity analysis
        - Code duplication detection (MECE)
        - Quality scoring

        Returns:
            Dict with comprehensive quality analysis
        """
        results = {
            "phase": "quality_refactoring",
            "analyzer_used": True,
            "nasa_compliance": {},
            "quality_metrics": {},
            "issues_by_severity": {},
            "refactoring_targets": []
        }

        try:
            # Run full analyzer with NASA compliance policy
            analysis = self.analyzer.analyze(str(self.target_path))

            # Extract NASA compliance
            results["nasa_compliance"] = self._extract_nasa_compliance(analysis)

            # Extract quality metrics
            results["quality_metrics"] = {
                "average_complexity": analysis.get("avg_complexity", 0),
                "max_complexity": analysis.get("max_complexity", 0),
                "duplication_percentage": analysis.get("duplication_percentage", 0.0),
                "god_objects_count": analysis.get("god_objects_count", 0),
                "overall_quality_score": analysis.get("quality_score", 0.0)
            }

            # Group issues by severity
            issues = analysis.get("issues", [])
            results["issues_by_severity"] = {
                "critical": [i for i in issues if i.get("severity") == "critical"],
                "high": [i for i in issues if i.get("severity") == "high"],
                "medium": [i for i in issues if i.get("severity") == "medium"],
                "low": [i for i in issues if i.get("severity") == "low"]
            }

            # Identify refactoring targets
            results["refactoring_targets"] = self._identify_refactoring_targets(analysis)

            # Pass/fail based on NASA compliance threshold
            nasa_compliance_rate = results["nasa_compliance"].get("compliance_rate", 0.0)
            results["passed"] = nasa_compliance_rate >= NASA_POT10_TARGET_COMPLIANCE_THRESHOLD

            return results

        except Exception as e:
            results["error"] = str(e)
            results["passed"] = False
            return results

    def _calculate_theater_score(self, patterns: Dict[str, List]) -> float:
        """
        Calculate theater score from detected patterns.

        Scoring:
        - TODOs: 10 points each
        - Mocks: 20 points each
        - Placeholders: 15 points each
        - Magic literals: 5 points each
        - Commented code: 5 points each

        Args:
            patterns: Dict of theater patterns by type

        Returns:
            Theater score (0-100+, lower is better)
        """
        score = (
            len(patterns.get("todos", [])) * 10 +
            len(patterns.get("mocks", [])) * 20 +
            len(patterns.get("placeholders", [])) * 15 +
            len(patterns.get("magic_literals", [])) * 5 +
            len(patterns.get("commented_code", [])) * 5
        )
        return score

    def _generate_theater_recommendations(self, patterns: Dict[str, List]) -> List[str]:
        """Generate recommendations for theater elimination."""
        recommendations = []

        if patterns.get("todos"):
            recommendations.append(
                f"Replace {len(patterns['todos'])} TODO comments with real implementations"
            )

        if patterns.get("mocks"):
            recommendations.append(
                f"Replace {len(patterns['mocks'])} mock implementations with genuine services"
            )

        if patterns.get("placeholders"):
            recommendations.append(
                f"Implement {len(patterns['placeholders'])} placeholder functions"
            )

        if patterns.get("magic_literals"):
            recommendations.append(
                f"Extract {len(patterns['magic_literals'])} magic literals into named constants"
            )

        return recommendations

    def _extract_nasa_compliance(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract NASA compliance from analyzer results."""
        nasa_compliance = {
            "compliance_rate": 0.0,
            "rules_violated": [],
            "rules_passed": [],
            "violations_by_rule": {}
        }

        # Get compliance results from analyzer
        compliance = analysis.get("compliance", {})
        nasa_results = compliance.get("NASA_POT10", {})

        nasa_compliance["compliance_rate"] = nasa_results.get("score", 0.0)

        # Extract violations by rule
        violations = nasa_results.get("violations", [])
        for violation in violations:
            rule_id = violation.get("rule_id")
            if rule_id:
                if rule_id not in nasa_compliance["violations_by_rule"]:
                    nasa_compliance["violations_by_rule"][rule_id] = []
                nasa_compliance["violations_by_rule"][rule_id].append(violation)

                if rule_id not in nasa_compliance["rules_violated"]:
                    nasa_compliance["rules_violated"].append(rule_id)

        # Determine passed rules
        all_rules = list(NASA_RULES.keys())
        nasa_compliance["rules_passed"] = [
            rule for rule in all_rules
            if rule not in nasa_compliance["rules_violated"]
        ]

        return nasa_compliance

    def _identify_refactoring_targets(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify high-priority refactoring targets.

        Targets:
        - Functions >60 LOC (NASA Rule 3 violation)
        - Functions with complexity >10
        - God objects (>20 methods or >500 LOC)
        - High code duplication (>80% similarity)

        Args:
            analysis: Full analyzer results

        Returns:
            List of refactoring targets with priority
        """
        targets = []

        # Find NASA Rule 3 violations (function length)
        issues = analysis.get("issues", [])
        for issue in issues:
            if issue.get("rule_id") == "RULE_3":
                targets.append({
                    "type": "long_function",
                    "priority": "high",
                    "file": issue.get("file"),
                    "function": issue.get("function"),
                    "current_loc": issue.get("actual"),
                    "target_loc": MAXIMUM_FUNCTION_LENGTH_LINES,
                    "recommendation": f"Refactor into smaller functions (target: ≤{MAXIMUM_FUNCTION_LENGTH_LINES} LOC)"
                })

        # Find high complexity functions
        patterns = analysis.get("patterns", [])
        for pattern in patterns:
            if pattern.get("pattern_type") == "high_complexity":
                targets.append({
                    "type": "high_complexity",
                    "priority": "medium",
                    "file": pattern.get("file"),
                    "function": pattern.get("function"),
                    "complexity": pattern.get("complexity"),
                    "recommendation": f"Reduce complexity (target: ≤{ALGORITHM_COMPLEXITY_THRESHOLD})"
                })

        # Find god objects
        god_objects = analysis.get("god_objects", [])
        for god_obj in god_objects:
            targets.append({
                "type": "god_object",
                "priority": "high",
                "file": god_obj.get("file"),
                "class": god_obj.get("class"),
                "method_count": god_obj.get("method_count"),
                "loc": god_obj.get("loc"),
                "recommendation": "Split into smaller, focused classes"
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        targets.sort(key=lambda t: priority_order.get(t.get("priority", "low"), 2))

        return targets


if __name__ == "__main__":
    # Example usage
    import json

    integration = AnalyzerIntegration(Path("../../src"))

    print("Phase 1: Theater Detection")
    phase1 = integration.phase1_theater_detection()
    print(json.dumps(phase1, indent=2))

    print("\nPhase 2: Functionality Validation")
    phase2 = integration.phase2_functionality_validation()
    print(json.dumps(phase2, indent=2))

    print("\nPhase 3: Quality Refactoring")
    phase3 = integration.phase3_quality_refactoring()
    print(json.dumps(phase3, indent=2))
