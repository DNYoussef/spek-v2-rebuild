"""
Public API Facade - Simplified analyzer interface

Provides the primary entry point for analyzer functionality.

NASA Rule 3 Compliance: ≤100 LOC target
Version: 6.0.0 (Week 1 Refactoring)
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .engine import AnalysisEngine

logger = logging.getLogger(__name__)


class Analyzer:
    """
    Main analyzer class providing simplified API.

    This is the recommended entry point for all analyzer operations.

    Example:
        analyzer = Analyzer(policy="nasa-compliance")
        result = analyzer.analyze("./src")
    """

    def __init__(
        self,
        policy: str = "standard",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize analyzer with policy and configuration.

        Args:
            policy: Analysis policy (nasa-compliance, strict, standard, lenient)
            config: Optional configuration overrides

        NASA Rule 4: 2 assertions
        """
        assert policy in ["nasa-compliance", "strict", "standard", "lenient"], \
            f"Invalid policy: {policy}"
        assert config is None or isinstance(config, dict), \
            "Config must be dict or None"

        self.policy = policy
        self.config = config or {}
        self.engine = AnalysisEngine(policy=policy, config=self.config)

    def analyze(
        self,
        path: str,
        format: str = "dict"
    ) -> Dict[str, Any]:
        """
        Analyze code at given path.

        Args:
            path: Path to analyze (file or directory)
            format: Output format (dict, json, sarif)

        Returns:
            Analysis results

        NASA Rule 4: 2 assertions
        """
        assert path, "Path cannot be empty"
        assert format in ["dict", "json", "sarif"], \
            f"Invalid format: {format}"

        target_path = Path(path)
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        # Delegate to engine
        result = self.engine.run_analysis(str(target_path))

        # Format result
        if format == "dict":
            return result
        elif format == "json":
            import json
            return json.dumps(result, indent=2)
        elif format == "sarif":
            from ..reporting import sarif
            return sarif.to_sarif(result)

        return result


# Convenience function for one-liner usage
def analyze(path: str, policy: str = "standard") -> Dict[str, Any]:
    """
    Convenience function for quick analysis.

    Example:
        from analyzer.core.api import analyze
        result = analyze("./src", policy="nasa-compliance")
    """
    analyzer = Analyzer(policy=policy)
    return analyzer.analyze(path)
