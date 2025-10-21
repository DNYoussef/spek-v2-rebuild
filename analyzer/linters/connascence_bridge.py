"""
Connascence Bridge - Integration with linter registry system

Bridges the connascence detector into the unified linter interface.
Detects 7 types of connascence violations (CoM, CoV, CoP, CoT, CoA, CoE, CoI).

NASA Rule 3 Compliance: ≤60 LOC per function
"""
import ast
import logging
from pathlib import Path
from typing import Dict, List, Any

from .base_linter import LinterBridge
from analyzer.utils.types import ConnascenceViolation

logger = logging.getLogger(__name__)


class ConnascenceBridge(LinterBridge):
    """
    Bridge for connascence detection via unified linter interface.

    Detects architectural coupling issues:
    - CoM (Connascence of Meaning): Magic literals, hardcoded values
    - CoV (Connascence of Value): Shared configuration
    - CoP (Connascence of Position): Parameter order dependencies
    - CoT (Connascence of Timing): Race conditions
    - CoA (Connascence of Algorithm): Duplicate algorithms
    - CoE (Connascence of Execution): Execution order
    - CoI (Connascence of Identity): Shared mutable state

    NASA Rule 3: All methods ≤60 LOC
    """

    def __init__(self):
        """Initialize connascence bridge."""
        self.detector = None  # Lazy loaded
        self.detector_name = "connascence"
        logger.debug("ConnascenceBridge initialized (lazy loading)")

    def is_available(self) -> bool:
        """
        Check if connascence detector is available.

        Returns:
            True if detector can be imported and used

        NASA Rule 3: ≤60 LOC
        """
        try:
            from analyzer.architecture.connascence_detector import ConnascenceDetector

            # Test instantiation
            test_detector = ConnascenceDetector()

            # Verify supported types
            supported = test_detector.get_supported_connascence_types()
            if len(supported) >= 7:  # Should support at least 7 types
                logger.info(f"Connascence detector available: {supported}")
                return True
            else:
                logger.warning(f"Connascence detector incomplete: {supported}")
                return False

        except ImportError as e:
            logger.debug(f"Connascence detector not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Connascence detector check failed: {e}")
            return False

    def convert_to_violations(self, raw_output: Any) -> List[ConnascenceViolation]:
        """
        Convert detector output to ConnascenceViolation format.

        For connascence detector, raw_output is already a list of
        ConnascenceViolation objects, so we just return it directly.

        Args:
            raw_output: List of ConnascenceViolation objects from detector

        Returns:
            List of ConnascenceViolation objects

        NASA Rule 3: <=60 LOC
        """
        if isinstance(raw_output, list):
            return raw_output
        return []

    def run(self, file_path: Path) -> Dict[str, Any]:
        """
        Run connascence detection on a Python file.

        Args:
            file_path: Path to file to analyze

        Returns:
            Result dictionary with violations and metrics

        NASA Rule 4: Assertions for input validation
        """
        assert isinstance(file_path, Path), "file_path must be Path"
        assert file_path.exists(), f"File not found: {file_path}"
        assert file_path.suffix == '.py', f"Not a Python file: {file_path}"

        try:
            # Lazy load detector
            if self.detector is None:
                from analyzer.architecture.connascence_detector import ConnascenceDetector
                self.detector = ConnascenceDetector()

            # Read source
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                source_lines = source.splitlines()

            # Parse AST
            tree = ast.parse(source, filename=str(file_path))

            # Run detection
            raw_violations = self.detector.detect_violations(
                tree,
                str(file_path),
                source_lines
            )

            # Convert to standard format
            violations = self.convert_to_violations(raw_violations)

            logger.info(
                f"Connascence detection complete: "
                f"{len(violations)} violations in {file_path.name}"
            )

            return {
                'success': True,
                'violations': violations,
                'linter': self.detector_name,
                'raw_output': raw_violations,
                'metrics': self._extract_metrics(violations)
            }

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return {
                'success': False,
                'error': f'Syntax error: {e}',
                'violations': [],
                'linter': self.detector_name
            }
        except Exception as e:
            logger.error(f"Connascence detection failed for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'violations': [],
                'linter': self.detector_name
            }

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the connascence detector.

        Returns:
            Dictionary with detector metadata

        NASA Rule 3: ≤60 LOC
        """
        info = {
            'name': self.detector_name,
            'description': 'Detects architectural coupling (connascence)',
            'types_detected': [
                'CoM (Meaning)', 'CoV (Value)', 'CoP (Position)',
                'CoT (Timing)', 'CoA (Algorithm)', 'CoE (Execution)',
                'CoI (Identity)'
            ],
            'severity_levels': ['critical', 'high', 'medium', 'low'],
            'performance': '~2-3s per file',
            'requires': 'Python AST parsing'
        }

        # Add runtime info if available
        if self.is_available():
            try:
                from analyzer.architecture.connascence_detector import ConnascenceDetector
                test_detector = ConnascenceDetector()
                info['detector_name'] = test_detector.get_detector_name()
                info['supported_types'] = test_detector.get_supported_connascence_types()
            except Exception:
                pass

        return info

    def _extract_metrics(self, violations: List[ConnascenceViolation]) -> Dict[str, Any]:
        """
        Extract metrics from connascence violations.

        Args:
            violations: List of detected violations

        Returns:
            Metrics dictionary

        NASA Rule 3: ≤60 LOC
        """
        if not violations:
            return {
                'total_violations': 0,
                'by_severity': {},
                'by_type': {},
                'overall_health': 'excellent'
            }

        # Count by severity
        by_severity = {}
        for v in violations:
            severity = v.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Count by connascence type
        by_type = {}
        for v in violations:
            c_type = v.connascence_type
            by_type[c_type] = by_type.get(c_type, 0) + 1

        # Determine overall health
        critical_count = by_severity.get('critical', 0)
        high_count = by_severity.get('high', 0)

        if critical_count > 0:
            health = 'poor'
        elif high_count > 5:
            health = 'fair'
        elif high_count > 0:
            health = 'good'
        else:
            health = 'excellent'

        return {
            'total_violations': len(violations),
            'by_severity': by_severity,
            'by_type': by_type,
            'overall_health': health
        }


__all__ = ['ConnascenceBridge']
