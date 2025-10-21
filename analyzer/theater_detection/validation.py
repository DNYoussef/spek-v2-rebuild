from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, Callable, Set

from analyzer.constants.thresholds import MAXIMUM_FUNCTION_LENGTH_LINES, MAXIMUM_GOD_OBJECTS_ALLOWED, MAXIMUM_NESTED_DEPTH

import os
import json
import subprocess
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .core import RealityValidationResult, TheaterPattern, TheaterType, SeverityLevel

@dataclass
class QualityMetric:
    """Represents a quality metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: str
    source: str

class RealityValidator:
    """Validates that claimed improvements are real."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def validate_test_claims(self, directory: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate test coverage and quality claims."""
        results = {
            "test_files_found": 0,
            "actual_tests_count": 0,
            "empty_tests": 0,
            "meaningful_tests": 0,
            "coverage_percentage": 0.0
        }

        # Count test files
        test_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if 'test' in file and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))

        results["test_files_found"] = len(test_files)

        # Analyze test quality
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Count test functions
                test_functions = re.findall(r'def\s+test_\w+', content)
                results["actual_tests_count"] += len(test_functions)

                # Check for empty tests
                empty_tests = re.findall(r'def\s+test_\w+[^:]*:\s*pass', content, re.MULTILINE)
                results["empty_tests"] += len(empty_tests)

                # Check for meaningful assertions
                assertions = re.findall(r'assert\s+(?!True\s*$)(?!False\s*$)(?!1\s*==\s*1)', content)
                results["meaningful_tests"] += len(assertions)

            except Exception:
                continue

        # Try to get actual coverage if pytest-cov is available
        try:
            cmd = ["python", "-m", "pytest", "--cov=.", "--cov-report=json", "--quiet"]
            result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Look for coverage report
                coverage_file = os.path.join(directory, "coverage.json")
                if path_exists(coverage_file):
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                        results["coverage_percentage"] = coverage_data.get("totals", {}).get("percent_covered", 0.0)
        except Exception:
            pass

        # Validate claims
        is_valid = True
        if results["empty_tests"] > results["meaningful_tests"]:
            is_valid = False

        if results["test_files_found"] > 0 and results["actual_tests_count"] == 0:
            is_valid = False

        return is_valid, results

    def validate_quality_metrics(self, metrics: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate quality metrics for suspicious values."""
        issues = []

        # Check for perfect scores
        suspicious_values = [100, 1.0, "perfect", "excellent", "A+"]
        for key, value in metrics.items():
            if value in suspicious_values:
                issues.append(f"Suspicious perfect value for {key}: {value}")

        # Check for impossible combinations
        if metrics.get("coverage", 0) == MAXIMUM_FUNCTION_LENGTH_LINES and metrics.get("test_count", 0) < MAXIMUM_NESTED_DEPTH:
            issues.append("100% coverage with very few tests is suspicious")

        if metrics.get("bug_count", -1) == 0 and metrics.get("complexity", 0) > 50:
            issues.append("Zero bugs with high complexity is suspicious")

        return len(issues) == 0, issues

    def validate_code_changes(self, directory: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate that code changes are meaningful."""
        results = {
            "total_files": 0,
            "changed_files": 0,
            "meaningful_changes": 0,
            "cosmetic_changes": 0,
            "lines_added": 0,
            "lines_removed": 0
        }

        try:
            # Get git diff stats
            cmd = ["git", "diff", "--stat", "HEAD~1", "HEAD"]
            result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True)

            if result.returncode == 0:
                diff_output = result.stdout

                # Parse diff stats
                for line in diff_output.split('\n'):
                    if '|' in line and ('+' in line or '-' in line):
                        results["changed_files"] += 1

                        # Count insertions and deletions
                        if '+' in line:
                            plus_count = line.count('+')
                            results["lines_added"] += plus_count

                        if '-' in line:
                            minus_count = line.count('-')
                            results["lines_removed"] += minus_count

            # Get detailed diff to analyze change quality
            cmd = ["git", "diff", "HEAD~1", "HEAD"]
            result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True)

            if result.returncode == 0:
                diff_content = result.stdout

                # Analyze changes
                cosmetic_patterns = [
                    r'^\+\s*#.*',  # Comments
                    r'^\+\s*""".*',  # Docstrings
                    r'^\+\s*\n',  # Blank lines
                    r'^\+\s*import\s+',  # Imports only
                ]

                meaningful_patterns = [
                    r'^\+.*def\s+',  # Function definitions
                    r'^\+.*class\s+',  # Class definitions
                    r'^\+.*if\s+',  # Logic
                    r'^\+.*for\s+',  # Loops
                    r'^\+.*while\s+',  # Loops
                    r'^\+.*try:',  # Error handling
                    r'^\+.*except',  # Error handling
                ]

                for line in diff_content.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        is_cosmetic = any(re.match(pattern, line) for pattern in cosmetic_patterns)
                        is_meaningful = any(re.match(pattern, line) for pattern in meaningful_patterns)

                        if is_cosmetic:
                            results["cosmetic_changes"] += 1
                        elif is_meaningful:
                            results["meaningful_changes"] += 1

        except Exception:
            pass

        # Validate changes
        is_valid = True
        if results["cosmetic_changes"] > results["meaningful_changes"] * 2:
            is_valid = False

        return is_valid, results

    def perform_reality_check(self, directory: str, claims: Dict[str, Any]) -> RealityValidationResult:
        """Perform comprehensive reality validation."""
        issues = []
        metrics = {}
        overall_score = 0.0

        # Validate test claims
        test_valid, test_metrics = self.validate_test_claims(directory)
        metrics["test_validation"] = test_metrics
        if not test_valid:
            issues.append(TheaterPattern(
                pattern_type=TheaterType.TEST_GAMING,
                severity=SeverityLevel.HIGH,
                file_path=directory,
                line_number=0,
                description="Test claims validation failed",
                evidence=test_metrics,
                recommendation="Improve test quality and coverage",
                confidence=0.9
            ))
        else:
            overall_score += 25

        # Validate quality metrics
        if "quality_metrics" in claims:
            metrics_valid, metric_issues = self.validate_quality_metrics(claims["quality_metrics"])
            if not metrics_valid:
                for issue in metric_issues:
                    issues.append(TheaterPattern(
                        pattern_type=TheaterType.METRICS_INFLATION,
                        severity=SeverityLevel.MEDIUM,
                        file_path=directory,
                        line_number=0,
                        description=issue,
                        evidence=claims["quality_metrics"],
                        recommendation="Provide realistic metrics",
                        confidence=0.8
                    ))
            else:
                overall_score += 25

        # Validate code changes
        changes_valid, change_metrics = self.validate_code_changes(directory)
        metrics["change_validation"] = change_metrics
        if not changes_valid:
            issues.append(TheaterPattern(
                pattern_type=TheaterType.QUALITY_FACADE,
                severity=SeverityLevel.MEDIUM,
                file_path=directory,
                line_number=0,
                description="Code changes appear mostly cosmetic",
                evidence=change_metrics,
                recommendation="Focus on meaningful functional improvements",
                confidence=0.7
            ))
        else:
            overall_score += MAXIMUM_GOD_OBJECTS_ALLOWED

        # Check for error masking
        error_patterns = self._check_error_masking(directory)
        if error_patterns:
            issues.extend(error_patterns)
        else:
            overall_score += 25

        return RealityValidationResult(
            is_valid=len(issues) == 0,
            score=overall_score,
            issues=issues,
            metrics=metrics,
            timestamp=datetime.now().isoformat()
        )

    def _check_error_masking(self, directory: str) -> List[TheaterPattern]:
        """Check for error masking patterns."""
        patterns = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Look for bare except clauses
                        bare_except_matches = re.finditer(r'except\s*:', content)
                        for match in bare_except_matches:
                            line_num = content[:match.start()].count('\n') + 1
                            patterns.append(TheaterPattern(
                                pattern_type=TheaterType.ERROR_MASKING,
                                severity=SeverityLevel.HIGH,
                                file_path=file_path,
                                line_number=line_num,
                                description="Bare except clause masks errors",
                                evidence={"pattern": "except:"},
                                recommendation="Catch specific exceptions",
                                confidence=0.95
                            ))

                    except Exception:
                        continue

        return patterns