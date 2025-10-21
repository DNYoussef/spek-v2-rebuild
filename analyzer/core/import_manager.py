"""
Simplified 2-Level Import Manager

Replaces the 5-level theater fallback system from v5 with honest fail-fast approach.

Architecture:
- Level 1: Primary import (production dependencies)
- Level 2: Fallback import (graceful degradation)
- NO Level 3-5: Emergency mock modes (REMOVED - was theater code)

NASA Rule 3 Compliance: ≤150 LOC target
Version: 6.0.0 (Week 1 Refactoring)
"""

import importlib
import logging
from typing import Optional, Any, Dict, List

logger = logging.getLogger(__name__)


class ImportManager:
    """Manages 2-level import fallback strategy with fail-fast error handling."""

    def __init__(self):
        self.failed_imports: List[tuple] = []
        self.import_stats: Dict[str, bool] = {}

    def import_with_fallback(
        self,
        primary: str,
        fallback: Optional[str] = None
    ) -> Any:
        """
        Import module with optional fallback.

        Args:
            primary: Primary module to import
            fallback: Optional fallback module

        Returns:
            Imported module

        Raises:
            ImportError: If both primary and fallback fail

        NASA Rule 4: 2 assertions (parameter validation)
        """
        assert primary, "Primary module name required"
        assert isinstance(primary, str), "Primary must be string"

        # Try primary import
        try:
            module = importlib.import_module(primary)
            logger.debug(f"Imported {primary} (primary)")
            self.import_stats[primary] = True
            return module
        except ImportError as e:
            logger.warning(f"Primary import failed: {primary} - {e}")
            self.failed_imports.append((primary, str(e)))
            self.import_stats[primary] = False

        # Try fallback if provided
        if fallback:
            try:
                module = importlib.import_module(fallback)
                logger.info(f"Imported {fallback} (fallback for {primary})")
                self.import_stats[fallback] = True
                return module
            except ImportError as e:
                logger.error(f"Fallback import failed: {fallback} - {e}")
                self.failed_imports.append((fallback, str(e)))
                self.import_stats[fallback] = False

        # Both failed - raise explicit error (FAIL-FAST, NO MOCK)
        error_msg = f"Failed to import {primary}"
        if fallback:
            error_msg += f" and fallback {fallback}"
        error_msg += ". Install required dependencies."

        raise ImportError(error_msg)

    def validate_dependencies(self, required: List[str]) -> Dict[str, bool]:
        """
        Validate all required dependencies can be imported.

        Args:
            required: List of required module names

        Returns:
            Dict of {module: status} where status is True/False

        NASA Rule 4: 2 assertions
        """
        assert required, "Required modules list cannot be empty"
        assert isinstance(required, list), "Required must be a list"

        results = {}
        for module in required:
            try:
                importlib.import_module(module)
                results[module] = True
            except ImportError:
                results[module] = False
                logger.error(f"Missing required dependency: {module}")

        return results

    def get_failed_imports(self) -> List[tuple]:
        """Return list of failed imports for diagnostics."""
        return self.failed_imports.copy()

    def get_import_stats(self) -> Dict[str, Any]:
        """Return import statistics."""
        total = len(self.import_stats)
        successful = sum(1 for v in self.import_stats.values() if v)

        return {
            "total_imports": total,
            "successful_imports": successful,
            "failed_imports": len(self.failed_imports),
            "success_rate": successful / total if total > 0 else 0.0,
            "failed_modules": [name for name, _ in self.failed_imports]
        }


# Global instance for module-level usage
import_manager = ImportManager()
