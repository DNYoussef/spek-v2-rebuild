"""
Duplication Bridge - Integration with linter registry system

Bridges the duplication analyzer into the unified linter interface.
Detects code duplication via MECE similarity clustering and algorithm matching.

NASA Rule 3 Compliance: ≤60 LOC per function
"""
import logging
from pathlib import Path
from typing import Dict, List, Any

from .base_linter import LinterBridge
from analyzer.utils.types import ConnascenceViolation

logger = logging.getLogger(__name__)


class DuplicationBridge(LinterBridge):
    """
    Bridge for duplication detection via unified linter interface.

    Detects code duplication:
    - Function-level similarity (MECE clustering)
    - Algorithm duplication (CoA - Connascence of Algorithm)
    - Cross-file and intra-file duplicates
    - Structural code clones

    Returns duplication violations with similarity scores and recommendations.

    NASA Rule 3: All methods ≤60 LOC
    """

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize duplication bridge.

        Args:
            similarity_threshold: Minimum similarity for duplication (0.0-1.0)
        """
        self.analyzer = None  # Lazy loaded
        self.detector_name = "duplication"
        self.similarity_threshold = similarity_threshold
        logger.debug(
            f"DuplicationBridge initialized "
            f"(threshold={similarity_threshold}, lazy loading)"
        )

    def is_available(self) -> bool:
        """
        Check if duplication analyzer is available.

        Returns:
            True if analyzer can be imported and used

        NASA Rule 3: ≤60 LOC
        """
        try:
            from analyzer.duplication_unified import UnifiedDuplicationAnalyzer

            # Test instantiation
            test_analyzer = UnifiedDuplicationAnalyzer(
                similarity_threshold=self.similarity_threshold
            )

            # Verify it has required methods
            if hasattr(test_analyzer, 'analyze_path'):
                logger.info("Duplication analyzer available")
                return True
            else:
                logger.warning("Duplication analyzer missing analyze_path method")
                return False

        except ImportError as e:
            logger.debug(f"Duplication analyzer not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Duplication analyzer check failed: {e}")
            return False

    def convert_to_violations(self, raw_output: Any) -> List[ConnascenceViolation]:
        """
        Convert duplication analyzer output to ConnascenceViolation format.

        Args:
            raw_output: Tuple of (duplication_violations, file_path)

        Returns:
            List of ConnascenceViolation objects

        NASA Rule 3: ≤60 LOC
        """
        if not isinstance(raw_output, tuple) or len(raw_output) != 2:
            return []

        dup_violations, file_path = raw_output
        return self._convert_violations(dup_violations, file_path)

    def run(self, file_path: Path) -> Dict[str, Any]:
        """
        Run duplication analysis on a Python file.

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
            # Lazy load analyzer
            if self.analyzer is None:
                from analyzer.duplication_unified import UnifiedDuplicationAnalyzer
                self.analyzer = UnifiedDuplicationAnalyzer(
                    similarity_threshold=self.similarity_threshold
                )

            # Run analysis
            result = self.analyzer.analyze_path(file_path)

            if not result.success:
                logger.error(f"Duplication analysis failed: {result.error}")
                return {
                    'success': False,
                    'error': result.error,
                    'violations': [],
                    'linter': self.detector_name
                }

            # Convert duplication violations to ConnascenceViolation format
            raw_output = (
                result.similarity_violations + result.algorithm_violations,
                file_path
            )
            violations = self.convert_to_violations(raw_output)

            logger.info(
                f"Duplication analysis complete: "
                f"{len(violations)} violations in {file_path.name}"
            )

            return {
                'success': True,
                'violations': violations,
                'linter': self.detector_name,
                'raw_output': raw_output,
                'metrics': {
                    'total_violations': result.total_violations,
                    'similarity_duplications': len(result.similarity_violations),
                    'algorithm_duplications': len(result.algorithm_violations),
                    'duplication_score': result.overall_duplication_score,
                    'summary': result.summary
                }
            }

        except Exception as e:
            logger.error(f"Duplication analysis failed for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'violations': [],
                'linter': self.detector_name
            }

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the duplication analyzer.

        Returns:
            Dictionary with analyzer metadata

        NASA Rule 3: ≤60 LOC
        """
        return {
            'name': self.detector_name,
            'description': 'Detects code duplication and redundancy',
            'methods': [
                'MECE similarity clustering',
                'Algorithm pattern matching (CoA)',
                'Cross-file duplication',
                'Intra-file duplication'
            ],
            'similarity_threshold': self.similarity_threshold,
            'severity_levels': ['critical', 'high', 'medium', 'low'],
            'performance': '~2-4s per file',
            'requires': 'Python AST parsing'
        }

    def _convert_violations(
        self,
        dup_violations: List[Any],
        file_path: Path
    ) -> List[ConnascenceViolation]:
        """
        Convert duplication violations to ConnascenceViolation format.

        Args:
            dup_violations: List of DuplicationViolation objects
            file_path: Path to analyzed file

        Returns:
            List of ConnascenceViolation objects

        NASA Rule 3: ≤60 LOC
        """
        violations = []

        for dup_v in dup_violations:
            # Extract line number (use first range if available)
            line_num = 1
            if dup_v.line_ranges:
                line_num = dup_v.line_ranges[0].get('start', 1)

            # Map duplication severity to connascence severity
            severity = dup_v.severity  # Already in correct format

            # Create ConnascenceViolation
            violation = ConnascenceViolation(
                connascence_type='CoA',  # Duplication is Connascence of Algorithm
                severity=severity,
                line_number=line_num,
                description=f"{dup_v.description} (similarity: {dup_v.similarity_score:.2f})",
                recommendation=dup_v.recommendation,
                file_path=str(file_path),
                context={
                    'duplication_type': dup_v.type,
                    'similarity_score': dup_v.similarity_score,
                    'files_involved': dup_v.files_involved,
                    'line_ranges': dup_v.line_ranges
                }
            )

            violations.append(violation)

        return violations


__all__ = ['DuplicationBridge']
