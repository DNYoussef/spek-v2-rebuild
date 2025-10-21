"""
Base Linter Bridge - Abstract base class for all linter integrations

This module provides the abstract interface that all linter bridges must implement.
Following the Bridge Pattern, each linter (pylint, flake8, mypy, radon) implements
this interface to integrate with the analyzer.

Design Principles:
- Bridge Pattern: Decouple linter-specific logic from analyzer core
- Fail-safe: All bridges check availability before running
- Consistent: All return ConnascenceViolation objects
- Error handling: Graceful fallbacks for missing/failed linters

NASA Rule 3 Compliance: ≤60 LOC per function
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import time

# Import canonical violation type
from analyzer.utils.types import ConnascenceViolation

logger = logging.getLogger(__name__)


class LinterBridge(ABC):
    """
    Abstract base class for all linter integrations.

    All linter bridges (Pylint, Flake8, Mypy, Radon) inherit from this class
    and implement the required methods for their specific linter.

    NASA Rule 4: 2 assertions per method enforced.
    """

    def __init__(self, timeout: int = 60):
        """
        Initialize linter bridge.

        Args:
            timeout: Maximum time (seconds) to wait for linter execution

        NASA Rule 4: Input validation
        """
        assert isinstance(timeout, int), "timeout must be integer"
        assert timeout > 0, "timeout must be positive"

        self.timeout = timeout
        self.name = self.__class__.__name__
        logger.debug(f"Initialized {self.name} with timeout={timeout}s")

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if linter is installed and available.

        Returns:
            True if linter can be used, False otherwise

        Implementation should try importing or executing the linter
        and return True only if it succeeds.

        NASA Rule 3: ≤60 LOC
        """
        pass

    @abstractmethod
    def run(self, file_path: Path) -> Dict[str, Any]:
        """
        Run linter on file and return structured results.

        Args:
            file_path: Path to file to analyze

        Returns:
            Dictionary containing:
            - 'success': bool - Whether linter ran successfully
            - 'violations': List[ConnascenceViolation] - Found violations
            - 'raw_output': Any - Linter-specific raw output
            - 'execution_time': float - Time taken in seconds
            - 'linter': str - Name of linter used
            - 'error': str (optional) - Error message if failed

        NASA Rule 4: File must exist before processing
        """
        pass

    @abstractmethod
    def convert_to_violations(self, raw_output: Any) -> List[ConnascenceViolation]:
        """
        Convert linter-specific output to ConnascenceViolation format.

        Args:
            raw_output: Linter-specific output format

        Returns:
            List of ConnascenceViolation objects

        This method handles the mapping from linter-specific violation
        formats (e.g., pylint messages, flake8 errors) to our canonical
        ConnascenceViolation type.

        NASA Rule 3: ≤60 LOC per implementation
        """
        pass

    def safe_run(self, file_path: Path) -> Dict[str, Any]:
        """
        Run linter with error handling and availability checks.

        Args:
            file_path: Path to file to analyze

        Returns:
            Result dictionary (same format as run())

        This is the primary entry point for executing linters.
        It wraps run() with availability checks and error handling.

        NASA Rule 4: Validation assertions
        """
        assert isinstance(file_path, Path), "file_path must be Path object"

        try:
            # Check if linter is available
            if not self.is_available():
                logger.warning(f"{self.name} not available")
                return self._unavailable_result()

            # Run the linter
            result = self.run(file_path)

            # Validate result structure
            assert 'success' in result, "run() must return 'success' key"
            assert 'violations' in result, "run() must return 'violations' key"

            return result

        except Exception as e:
            logger.error(f"{self.name} execution failed: {e}")
            return self._error_result(str(e))

    def _unavailable_result(self) -> Dict[str, Any]:
        """
        Generate result for unavailable linter.

        Returns:
            Standard error result indicating linter not available

        NASA Rule 3: ≤60 LOC
        """
        return {
            'success': False,
            'error': f'{self.name} not available (not installed or import failed)',
            'violations': [],
            'linter': self.name,
            'execution_time': 0.0
        }

    def _error_result(self, error: str) -> Dict[str, Any]:
        """
        Generate result for linter execution error.

        Args:
            error: Error message

        Returns:
            Standard error result with error message

        NASA Rule 3: ≤60 LOC
        """
        return {
            'success': False,
            'error': error,
            'violations': [],
            'linter': self.name,
            'execution_time': 0.0
        }

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this linter bridge.

        Returns:
            Dictionary with linter metadata

        NASA Rule 3: ≤60 LOC
        """
        return {
            'name': self.name,
            'available': self.is_available(),
            'timeout': self.timeout
        }


__all__ = ['LinterBridge']
