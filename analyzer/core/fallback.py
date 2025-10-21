"""
Minimal Fallback Handler - Emergency modes WITHOUT theater

Provides minimal graceful degradation WITHOUT mock results.

REMOVED from v5: 250 LOC of mock theater code
ADDED in v6: Honest fail-fast error handling

NASA Rule 3 Compliance: ≤100 LOC target
Version: 6.0.0 (Week 1 Refactoring)
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class FallbackHandler:
    """
    Minimal fallback handler with honest error reporting.

    NO MOCK RESULTS. NO THEATER. FAIL-FAST ONLY.
    """

    def __init__(self):
        self.fallback_count = 0
        self.errors = []

    def handle_analysis_failure(
        self,
        error: Exception,
        context: str = ""
    ) -> None:
        """
        Handle analysis failure with proper error reporting.

        Args:
            error: The exception that occurred
            context: Additional context for debugging

        Raises:
            The original exception (fail-fast)

        NASA Rule 4: 2 assertions
        """
        assert error is not None, "Error cannot be None"
        assert isinstance(error, Exception), "Error must be an Exception"

        self.fallback_count += 1
        error_msg = f"Analysis failed: {error}"
        if context:
            error_msg += f" (context: {context})"

        logger.error(error_msg)
        self.errors.append((error, context))

        # FAIL-FAST: Re-raise the original exception
        # NO MOCK RESULTS, NO FAKE ANALYSIS
        raise error

    def get_error_summary(self) -> dict:
        """Return error summary for diagnostics."""
        return {
            "fallback_count": self.fallback_count,
            "total_errors": len(self.errors),
            "errors": [
                {
                    "type": type(err).__name__,
                    "message": str(err),
                    "context": ctx
                }
                for err, ctx in self.errors
            ]
        }


# Global instance
fallback_handler = FallbackHandler()
