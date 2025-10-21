"""
CLI Entry Point - Command-line interface

Provides command-line access to analyzer functionality.

NASA Rule 3 Compliance: ≤150 LOC target
Version: 6.0.0 (Week 1 Refactoring)
"""

import argparse
import sys
import logging
from typing import List, Optional

from .api import Analyzer

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="SPEK Analyzer v6.0 - Code Quality Analysis"
    )

    parser.add_argument(
        "path",
        help="Path to analyze (file or directory)"
    )

    parser.add_argument(
        "--policy",
        choices=["nasa-compliance", "strict", "standard", "lenient"],
        default="standard",
        help="Analysis policy (default: standard)"
    )

    parser.add_argument(
        "--format",
        choices=["dict", "json", "sarif"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with error code if critical violations found"
    )

    parser.add_argument(
        "--compliance-threshold",
        type=float,
        default=0.92,
        help="Minimum NASA compliance threshold (default: 0.92)"
    )

    parser.add_argument(
        "--theater-threshold",
        type=int,
        default=60,
        help="Maximum theater detection score (default: 60)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (for testing)

    Returns:
        Exit code (0 = success, 1 = failure)

    NASA Rule 4: 2 assertions
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    try:
        # Run analysis
        analyzer = Analyzer(policy=args.policy)
        result = analyzer.analyze(args.path, format=args.format)

        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(str(result))
            logger.info(f"Results written to {args.output}")
        else:
            print(result)

        # Check quality gates
        if args.fail_on_critical:
            quality = result.get("quality_scores", {})
            nasa_compliance = quality.get("nasa_compliance", 0.0)
            theater_score = quality.get("theater_score", 100.0)

            if nasa_compliance < args.compliance_threshold:
                logger.error(
                    f"NASA compliance {nasa_compliance:.2%} below threshold "
                    f"{args.compliance_threshold:.2%}"
                )
                return 1

            if theater_score > args.theater_threshold:
                logger.error(
                    f"Theater score {theater_score} above threshold "
                    f"{args.theater_threshold}"
                )
                return 1

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
