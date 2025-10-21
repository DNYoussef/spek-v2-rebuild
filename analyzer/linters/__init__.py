"""
Linter Bridge System - External linter integration for SPEK Analyzer

This module provides a pluggable architecture for integrating external linters
(pylint, flake8, mypy, radon) into the analyzer workflow.

Design Pattern: Bridge + Registry
- Bridge: Decouple linter logic from analyzer core
- Registry: Central management of all available linters

Usage:
    from analyzer.linters import linter_registry

    # Get available linters
    available = linter_registry.get_available_linters()

    # Run all linters on a file
    results = linter_registry.run_all_linters(Path("myfile.py"))

    # Run specific linter
    result = linter_registry.run_linter('pylint', Path("myfile.py"))

    # Aggregate violations from all linters
    all_violations = linter_registry.aggregate_violations(results)

NASA Rule 3 Compliance: ≤60 LOC per function
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .base_linter import LinterBridge
from analyzer.utils.types import ConnascenceViolation

logger = logging.getLogger(__name__)


class LinterRegistry:
    """
    Central registry for all linter bridges.

    Manages linter lifecycle:
    - Registration of linter bridges
    - Availability detection
    - Execution coordination
    - Result aggregation

    NASA Rule 4: Assertions for input validation
    """

    def __init__(self):
        """
        Initialize linter registry.

        Linters are registered lazily (only when first accessed)
        to avoid import errors if linter packages are missing.
        """
        self.linters: Dict[str, LinterBridge] = {}
        self._registered = False
        logger.debug("LinterRegistry initialized (lazy registration)")

    def _register_linters(self):
        """
        Register all available linter bridges.

        This is called lazily on first use to avoid import errors
        when linter packages are not installed.

        NASA Rule 3: ≤60 LOC
        """
        if self._registered:
            return

        # Try to register each linter, skip if import fails
        linters_to_register = [
            ('pylint', 'PylintBridge'),
            ('flake8', 'Flake8Bridge'),
            ('mypy', 'MypyBridge'),
            ('radon', 'RadonBridge'),
            ('connascence', 'ConnascenceBridge'),
            ('duplication', 'DuplicationBridge')
        ]

        for linter_name, class_name in linters_to_register:
            try:
                # Import linter bridge dynamically
                module = __import__(
                    f'analyzer.linters.{linter_name}_bridge',
                    fromlist=[class_name]
                )
                linter_class = getattr(module, class_name)

                # Instantiate and register
                self.linters[linter_name] = linter_class()
                logger.info(f"Registered {linter_name} bridge")

            except ImportError as e:
                logger.debug(
                    f"Could not register {linter_name} bridge "
                    f"(module not yet implemented): {e}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to register {linter_name} bridge: {e}"
                )

        self._registered = True
        logger.info(
            f"Linter registration complete: "
            f"{len(self.linters)}/{len(linters_to_register)} available"
        )

    def get_available_linters(self) -> List[str]:
        """
        Get list of available (installed and functional) linters.

        Returns:
            List of linter names that are available for use

        NASA Rule 3: ≤60 LOC
        """
        self._register_linters()

        available = [
            name for name, linter in self.linters.items()
            if linter.is_available()
        ]

        logger.debug(f"Available linters: {available}")
        return available

    def run_all_linters(self, file_path: Path) -> Dict[str, Any]:
        """
        Run all available linters on a file.

        Args:
            file_path: Path to file to analyze

        Returns:
            Dictionary mapping linter names to their results

        NASA Rule 4: Input validation
        """
        assert isinstance(file_path, Path), "file_path must be Path"
        assert file_path.exists(), f"File not found: {file_path}"

        self._register_linters()
        results = {}

        for name, linter in self.linters.items():
            if linter.is_available():
                logger.info(f"Running {name} on {file_path.name}")
                results[name] = linter.safe_run(file_path)
            else:
                logger.debug(f"Skipping {name} (not available)")

        logger.info(
            f"Linter execution complete: {len(results)} linters ran"
        )
        return results

    def run_linter(
        self,
        linter_name: str,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        Run specific linter on a file.

        Args:
            linter_name: Name of linter to run ('pylint', 'flake8', etc.)
            file_path: Path to file to analyze

        Returns:
            Linter execution result dictionary

        NASA Rule 4: Assertions
        """
        assert isinstance(linter_name, str), "linter_name must be string"
        assert isinstance(file_path, Path), "file_path must be Path"

        self._register_linters()

        if linter_name not in self.linters:
            return {
                'success': False,
                'error': f'Unknown linter: {linter_name}',
                'violations': []
            }

        linter = self.linters[linter_name]
        return linter.safe_run(file_path)

    def aggregate_violations(
        self,
        linter_results: Dict[str, Any]
    ) -> List[ConnascenceViolation]:
        """
        Aggregate violations from all linters into single list.

        Args:
            linter_results: Results from run_all_linters()

        Returns:
            Combined list of all violations from all linters

        NASA Rule 4: Assertions
        """
        assert isinstance(linter_results, dict), "results must be dict"

        all_violations = []

        for linter_name, result in linter_results.items():
            if result.get('success'):
                violations = result.get('violations', [])
                all_violations.extend(violations)
                logger.debug(
                    f"{linter_name}: {len(violations)} violations"
                )

        logger.info(
            f"Aggregated {len(all_violations)} total violations "
            f"from {len(linter_results)} linters"
        )
        return all_violations

    def get_linter_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered linters.

        Returns:
            Dictionary mapping linter names to their info

        NASA Rule 3: ≤60 LOC
        """
        self._register_linters()

        info = {}
        for name, linter in self.linters.items():
            info[name] = linter.get_info()

        return info


# Global registry instance
linter_registry = LinterRegistry()

__all__ = [
    'LinterBridge',
    'LinterRegistry',
    'linter_registry'
]
