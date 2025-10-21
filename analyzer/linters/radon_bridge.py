"""
Radon Bridge - Real Cyclomatic Complexity & Maintainability Metrics

This module provides integration with Radon for genuine code metrics:
- Cyclomatic Complexity (CC): Measures code complexity via control flow paths
- Maintainability Index (MI): 0-100 score for code maintainability
- Raw Metrics: LOC, SLOC, comments, blank lines

Replaces mocked metrics with real calculations.

NASA Rule 10 Compliance:
- All functions ≤60 LOC
- Critical paths have ≥2 assertions
- No recursion
- Fixed loop bounds

Author: SPEK Platform Team
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import json
import time

from .base_linter import LinterBridge
from analyzer.utils.types import ConnascenceViolation


class RadonBridge(LinterBridge):
    """
    Radon integration for cyclomatic complexity and maintainability metrics.

    Radon Commands:
    - radon cc: Cyclomatic Complexity (A-F grades)
    - radon mi: Maintainability Index (0-100 score)
    - radon raw: Raw metrics (LOC, SLOC, comments)

    Thresholds (aligned with Radon's grading):
    - CC A (1-5): Low complexity, no violation
    - CC B (6-10): Medium complexity, low severity
    - CC C (11-20): High complexity, medium severity
    - CC D (21-50): Very high complexity, high severity
    - CC E/F (51+): Extreme complexity, critical severity

    - MI 20+: Maintainable (A/B grades)
    - MI 10-19: Needs work (C grade) → medium severity
    - MI 0-9: Unmaintainable (F grade) → high severity
    """

    # Cyclomatic Complexity thresholds (Radon grades)
    CC_THRESHOLDS = {
        'A': (1, 5, None),         # Low complexity, no violation
        'B': (6, 10, 'low'),       # Medium complexity
        'C': (11, 20, 'medium'),   # High complexity
        'D': (21, 50, 'high'),     # Very high complexity
        'E': (51, float('inf'), 'critical'),  # Extreme complexity
        'F': (51, float('inf'), 'critical')   # Extreme complexity (same as E)
    }

    # Maintainability Index thresholds
    MI_THRESHOLDS = [
        (20, float('inf'), None),      # A/B grade: Maintainable, no violation
        (10, 19, 'medium'),            # C grade: Needs work
        (0, 9, 'high')                 # F grade: Unmaintainable
    ]

    def __init__(self, timeout: int = 60):
        """
        Initialize Radon bridge.

        Args:
            timeout: Maximum execution time in seconds (default: 60)

        Raises:
            ValueError: If timeout is invalid
        """
        # NASA Rule 10: ≥2 assertions for validation
        assert isinstance(timeout, int), "Timeout must be an integer"
        assert timeout > 0, "Timeout must be positive"

        self.timeout = timeout
        self.name = "radon"

    def is_available(self) -> bool:
        """
        Check if Radon is installed and accessible.

        Returns:
            True if Radon is available, False otherwise
        """
        try:
            # Use 'python -m radon' for cross-platform compatibility
            import sys
            result = subprocess.run(
                [sys.executable, '-m', 'radon', '--version'],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            # Python executable not found (shouldn't happen)
            return False
        except subprocess.TimeoutExpired:
            # Version check shouldn't timeout, treat as unavailable
            return False
        except Exception:
            # Catch any other unexpected errors
            return False

    def run(self, file_path: Path) -> Dict[str, Any]:
        """
        Run Radon cyclomatic complexity analysis on a file.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Dictionary with structure:
            {
                'success': bool,
                'violations': List[ConnascenceViolation],
                'raw_output': Dict,  # Radon JSON output
                'execution_time': float,
                'linter': 'radon',
                'metrics': Dict  # Additional metrics (CC, MI, raw)
            }

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        # NASA Rule 10: ≥2 assertions for critical paths
        assert file_path is not None, "file_path cannot be None"
        assert isinstance(file_path, Path), "file_path must be a Path object"

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        start_time = time.time()

        try:
            # Run Radon CC (Cyclomatic Complexity) with JSON output
            cc_result = self._run_radon_cc(file_path)

            # Run Radon MI (Maintainability Index) with JSON output
            mi_result = self._run_radon_mi(file_path)

            # Combine raw outputs
            raw_output = {
                'cyclomatic_complexity': cc_result,
                'maintainability_index': mi_result
            }

            # Convert metrics to violations
            violations = self.convert_to_violations(raw_output)

            execution_time = time.time() - start_time

            return {
                'success': True,
                'violations': violations,
                'raw_output': raw_output,
                'execution_time': execution_time,
                'linter': 'radon',
                'metrics': self._extract_metrics(raw_output)
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'violations': [],
                'error': f"Radon execution timed out after {self.timeout}s",
                'execution_time': execution_time,
                'linter': 'radon'
            }
        except json.JSONDecodeError as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'violations': [],
                'error': f"Failed to parse Radon JSON output: {e}",
                'execution_time': execution_time,
                'linter': 'radon'
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'violations': [],
                'error': f"Radon execution failed: {e}",
                'execution_time': execution_time,
                'linter': 'radon'
            }

    def _run_radon_cc(self, file_path: Path) -> Dict[str, Any]:
        """
        Run Radon cyclomatic complexity command.

        Args:
            file_path: Path to analyze

        Returns:
            Parsed JSON output from radon cc -j
        """
        import sys
        result = subprocess.run(
            [sys.executable, '-m', 'radon', 'cc', str(file_path), '-j'],  # -j for JSON output
            capture_output=True,
            timeout=self.timeout,
            text=True
        )

        if result.stdout:
            return json.loads(result.stdout)
        return {}

    def _run_radon_mi(self, file_path: Path) -> Dict[str, Any]:
        """
        Run Radon maintainability index command.

        Args:
            file_path: Path to analyze

        Returns:
            Parsed JSON output from radon mi -j
        """
        import sys
        result = subprocess.run(
            [sys.executable, '-m', 'radon', 'mi', str(file_path), '-j'],  # -j for JSON output
            capture_output=True,
            timeout=self.timeout,
            text=True
        )

        if result.stdout:
            return json.loads(result.stdout)
        return {}

    def convert_to_violations(self, raw_output: Dict[str, Any]) -> List[ConnascenceViolation]:
        """
        Convert Radon metrics to ConnascenceViolation format.

        Radon CC JSON format:
        {
            "file.py": [
                {
                    "type": "method",
                    "name": "function_name",
                    "lineno": 10,
                    "complexity": 15,
                    "rank": "C"
                }
            ]
        }

        Radon MI JSON format:
        {
            "file.py": {
                "mi": 65.3,
                "rank": "A"
            }
        }

        Args:
            raw_output: Dict with 'cyclomatic_complexity' and 'maintainability_index'

        Returns:
            List of ConnascenceViolation objects
        """
        violations = []

        # Process cyclomatic complexity violations
        cc_data = raw_output.get('cyclomatic_complexity', {})
        for file_path, functions in cc_data.items():
            for func in functions:
                complexity = func.get('complexity', 0)
                rank = func.get('rank', 'A')
                severity = self._map_cc_severity(rank)

                if severity:  # Only create violation if threshold exceeded
                    violation = ConnascenceViolation(
                        type=f"radon_cyclomatic_complexity",
                        severity=severity,
                        description=f"High cyclomatic complexity (CC={complexity}, rank={rank}) in {func.get('type', 'function')} '{func.get('name', 'unknown')}'",
                        file_path=file_path,
                        line_number=func.get('lineno', 0),
                        column=0,
                        recommendation=self._get_cc_recommendation(complexity, rank)
                    )
                    violations.append(violation)

        # Process maintainability index violations
        mi_data = raw_output.get('maintainability_index', {})
        for file_path, mi_info in mi_data.items():
            mi_score = mi_info.get('mi', 100.0)
            mi_rank = mi_info.get('rank', 'A')
            severity = self._map_mi_severity(mi_score)

            if severity:  # Only create violation if threshold exceeded
                violation = ConnascenceViolation(
                    type=f"radon_maintainability_index",
                    severity=severity,
                    description=f"Low maintainability index (MI={mi_score:.1f}, rank={mi_rank})",
                    file_path=file_path,
                    line_number=1,  # File-level metric
                    column=0,
                    recommendation=self._get_mi_recommendation(mi_score, mi_rank)
                )
                violations.append(violation)

        return violations

    def _map_cc_severity(self, rank: str) -> Optional[str]:
        """
        Map Radon CC rank to severity level.

        Args:
            rank: Radon rank (A, B, C, D, E, F)

        Returns:
            Severity string or None if no violation
        """
        threshold = self.CC_THRESHOLDS.get(rank, (0, 0, None))
        return threshold[2]  # Return severity (3rd element)

    def _map_mi_severity(self, mi_score: float) -> Optional[str]:
        """
        Map maintainability index score to severity level.

        Args:
            mi_score: MI score (0-100)

        Returns:
            Severity string or None if no violation
        """
        # Use clearer threshold logic with >= comparisons
        if mi_score >= 20:
            return None  # Maintainable (A/B grade)
        elif mi_score >= 10:
            return 'medium'  # Needs work (C grade)
        else:
            return 'high'  # Unmaintainable (F grade)

    def _get_cc_recommendation(self, complexity: int, rank: str) -> str:
        """Generate recommendation for cyclomatic complexity violation."""
        if complexity > 50:
            return "Critical: Refactor into smaller functions (target CC ≤10). Consider extracting helper functions, reducing nesting, and simplifying control flow."
        elif complexity > 20:
            return "High complexity: Break down into smaller functions (target CC ≤10). Reduce branching and nesting depth."
        elif complexity > 10:
            return "Moderate complexity: Consider refactoring to improve readability (target CC ≤10)."
        else:
            return "Simplify control flow to reduce complexity."

    def _get_mi_recommendation(self, mi_score: float, rank: str) -> str:
        """Generate recommendation for maintainability index violation."""
        if mi_score < 10:
            return "Critical: Code is very difficult to maintain. Consider major refactoring, reducing complexity, improving naming, and adding documentation."
        elif mi_score < 20:
            return "Low maintainability: Improve code organization, reduce complexity, and enhance documentation."
        else:
            return "Enhance code maintainability through better structure and documentation."

    def _extract_metrics(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract summary metrics from Radon output.

        Args:
            raw_output: Combined Radon CC and MI output

        Returns:
            Dictionary with summary metrics
        """
        metrics = {
            'total_functions': 0,
            'average_complexity': 0.0,
            'max_complexity': 0,
            'average_mi': 0.0,
            'files_analyzed': 0
        }

        # Calculate CC metrics
        cc_data = raw_output.get('cyclomatic_complexity', {})
        total_complexity = 0
        total_functions = 0
        max_complexity = 0

        for functions in cc_data.values():
            for func in functions:
                complexity = func.get('complexity', 0)
                total_complexity += complexity
                total_functions += 1
                max_complexity = max(max_complexity, complexity)

        if total_functions > 0:
            metrics['total_functions'] = total_functions
            metrics['average_complexity'] = total_complexity / total_functions
            metrics['max_complexity'] = max_complexity

        # Calculate MI metrics
        mi_data = raw_output.get('maintainability_index', {})
        total_mi = sum(info.get('mi', 0) for info in mi_data.values())
        files_count = len(mi_data)

        if files_count > 0:
            metrics['average_mi'] = total_mi / files_count
            metrics['files_analyzed'] = files_count

        return metrics
