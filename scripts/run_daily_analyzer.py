#!/usr/bin/env python3
"""
Daily Analyzer Runner - Week 3+ Integration

Runs the refactored Week 2 analyzer (syntax_analyzer, pattern_detector, compliance_validator)
on daily work outputs to ensure enterprise quality and low connascence.

Usage:
    python scripts/run_daily_analyzer.py <file_path> [--format json|text]

Version: 8.0.0 (Week 3 Day 2+)
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from analyzer.engines.syntax_analyzer import create_syntax_analyzer
    from analyzer.engines.pattern_detector import create_pattern_detector
    from analyzer.engines.compliance_validator import create_compliance_validator
except ImportError as e:
    print(f"ERROR: Failed to import analyzer engines: {e}")
    print(f"Project root: {project_root}")
    print("Please ensure Week 2 analyzer refactoring is complete.")
    sys.exit(1)


class DailyAnalyzerRunner:
    """
    Runs all 3 analyzer engines on a target file for daily audit.

    Outputs:
    - Enterprise quality score
    - Connascence levels (static, dynamic, inheritance)
    - NASA Rule 10 compliance (functions ≤60 LOC, files ≤300 LOC)
    - Security vulnerabilities
    - Code smells and anti-patterns
    """

    def __init__(self, file_path: str):
        """
        Initialize analyzer runner.

        Args:
            file_path: Path to file to analyze
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.syntax_analyzer = create_syntax_analyzer()
        self.pattern_detector = create_pattern_detector()
        self.compliance_validator = create_compliance_validator()

        self.results: Dict[str, Any] = {}

    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run all 3 analyzer engines.

        Returns:
            Dict with results from all engines
        """
        print(f"Analyzing: {self.file_path}")
        print("=" * 80)

        # Read file content
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Syntax Analysis
        print("\n[1/3] Running Syntax Analyzer...")
        syntax_results = self.syntax_analyzer.analyze(str(self.file_path), content)
        self.results['syntax'] = syntax_results

        # 2. Pattern Detection
        print("[2/3] Running Pattern Detector...")
        pattern_results = self.pattern_detector.detect(str(self.file_path), content)
        self.results['patterns'] = pattern_results

        # 3. Compliance Validation
        print("[3/3] Running Compliance Validator...")
        compliance_results = self.compliance_validator.validate(str(self.file_path), content)
        self.results['compliance'] = compliance_results

        # Calculate aggregate metrics
        self.results['aggregate'] = self._calculate_aggregate_metrics()

        print("✅ Analysis complete")
        return self.results

    def _calculate_aggregate_metrics(self) -> Dict[str, Any]:
        """
        Calculate aggregate enterprise quality metrics.

        Returns:
            Dict with aggregate scores
        """
        aggregate = {
            'file': str(self.file_path),
            'total_lines': 0,
            'enterprise_quality_score': 0.0,
            'nasa_compliance_score': 0.0,
            'connascence_level': 'UNKNOWN',
            'critical_issues': 0,
            'warnings': 0,
            'recommendations': []
        }

        # Extract syntax metrics
        syntax = self.results.get('syntax', {})
        aggregate['total_lines'] = syntax.get('total_lines', 0)
        aggregate['functions_count'] = syntax.get('functions_count', 0)
        aggregate['classes_count'] = syntax.get('classes_count', 0)

        # Extract compliance metrics
        compliance = self.results.get('compliance', {})
        aggregate['nasa_compliance_score'] = compliance.get('nasa_compliance_percentage', 0.0)
        aggregate['file_size_compliant'] = compliance.get('file_size_compliant', False)
        aggregate['avg_function_size'] = compliance.get('avg_function_size', 0)

        # Extract pattern metrics
        patterns = self.results.get('patterns', {})
        aggregate['code_smells'] = patterns.get('code_smells', [])
        aggregate['security_issues'] = patterns.get('security_issues', [])
        aggregate['connascence_violations'] = patterns.get('connascence_violations', [])

        # Calculate enterprise quality score (0-100)
        quality_score = 100.0

        # Deduct for NASA non-compliance
        nasa_penalty = (100.0 - aggregate['nasa_compliance_score']) * 0.4
        quality_score -= nasa_penalty

        # Deduct for code smells (5 points each, max 25)
        smell_penalty = min(len(aggregate['code_smells']) * 5, 25)
        quality_score -= smell_penalty

        # Deduct for security issues (10 points each, max 30)
        security_penalty = min(len(aggregate['security_issues']) * 10, 30)
        quality_score -= security_penalty

        # Deduct for connascence violations (7 points each, max 20)
        connascence_penalty = min(len(aggregate['connascence_violations']) * 7, 20)
        quality_score -= connascence_penalty

        aggregate['enterprise_quality_score'] = max(0.0, quality_score)

        # Determine connascence level
        connascence_count = len(aggregate['connascence_violations'])
        if connascence_count == 0:
            aggregate['connascence_level'] = 'LOW (Excellent)'
        elif connascence_count <= 2:
            aggregate['connascence_level'] = 'MODERATE (Good)'
        elif connascence_count <= 5:
            aggregate['connascence_level'] = 'HIGH (Needs Improvement)'
        else:
            aggregate['connascence_level'] = 'CRITICAL (Refactor Required)'

        # Count critical issues
        aggregate['critical_issues'] = (
            len(aggregate['security_issues']) +
            len([s for s in aggregate['code_smells'] if 'CRITICAL' in s])
        )
        aggregate['warnings'] = len(aggregate['code_smells']) + connascence_count

        # Generate recommendations
        if aggregate['nasa_compliance_score'] < 92.0:
            aggregate['recommendations'].append(
                f"NASA compliance at {aggregate['nasa_compliance_score']:.1f}% - "
                "target ≥92%. Review function sizes (≤60 LOC)."
            )

        if not aggregate['file_size_compliant']:
            aggregate['recommendations'].append(
                f"File size {aggregate['total_lines']} LOC exceeds 300 LOC limit. "
                "Consider splitting into multiple modules."
            )

        if aggregate['critical_issues'] > 0:
            aggregate['recommendations'].append(
                f"{aggregate['critical_issues']} critical security/smell issues found. "
                "Address before production deployment."
            )

        if connascence_count > 2:
            aggregate['recommendations'].append(
                f"Connascence level {aggregate['connascence_level']} - "
                "reduce coupling between modules."
            )

        if aggregate['enterprise_quality_score'] < 80.0:
            aggregate['recommendations'].append(
                f"Enterprise quality score {aggregate['enterprise_quality_score']:.1f}/100 "
                "below 80.0 threshold. Review all issues."
            )

        return aggregate

    def print_report(self, format: str = 'text') -> None:
        """
        Print analysis report.

        Args:
            format: 'text' or 'json'
        """
        if format == 'json':
            print(json.dumps(self.results, indent=2))
            return

        # Text format
        aggregate = self.results['aggregate']

        print("\n" + "=" * 80)
        print("DAILY ANALYZER REPORT - ENTERPRISE QUALITY SCAN")
        print("=" * 80)

        print(f"\n📄 File: {aggregate['file']}")
        print(f"📏 Total Lines: {aggregate['total_lines']} LOC")
        print(f"🔢 Functions: {aggregate.get('functions_count', 0)}")
        print(f"🏛️  Classes: {aggregate.get('classes_count', 0)}")

        print(f"\n🎯 Enterprise Quality Score: {aggregate['enterprise_quality_score']:.1f}/100")

        # Score interpretation
        score = aggregate['enterprise_quality_score']
        if score >= 95:
            status = "EXCELLENT ✅"
        elif score >= 85:
            status = "GOOD ✅"
        elif score >= 75:
            status = "ACCEPTABLE ⚠️"
        else:
            status = "NEEDS IMPROVEMENT ❌"
        print(f"   Status: {status}")

        print(f"\n📋 NASA Rule 10 Compliance: {aggregate['nasa_compliance_score']:.1f}%")
        if aggregate['file_size_compliant']:
            print("   File Size: ✅ Compliant (≤300 LOC)")
        else:
            print(f"   File Size: ❌ Non-compliant ({aggregate['total_lines']} LOC > 300)")
        print(f"   Avg Function Size: {aggregate.get('avg_function_size', 0)} LOC")

        print(f"\n🔗 Connascence Level: {aggregate['connascence_level']}")

        print(f"\n⚠️  Issues Summary:")
        print(f"   Critical Issues: {aggregate['critical_issues']}")
        print(f"   Warnings: {aggregate['warnings']}")
        print(f"   Code Smells: {len(aggregate['code_smells'])}")
        print(f"   Security Issues: {len(aggregate['security_issues'])}")
        print(f"   Connascence Violations: {len(aggregate['connascence_violations'])}")

        # Detailed issues
        if aggregate['security_issues']:
            print(f"\n🔒 Security Issues ({len(aggregate['security_issues'])}):")
            for issue in aggregate['security_issues'][:5]:  # Top 5
                print(f"   - {issue}")

        if aggregate['code_smells']:
            print(f"\n👃 Code Smells ({len(aggregate['code_smells'])}):")
            for smell in aggregate['code_smells'][:5]:  # Top 5
                print(f"   - {smell}")

        if aggregate['connascence_violations']:
            print(f"\n🔗 Connascence Violations ({len(aggregate['connascence_violations'])}):")
            for violation in aggregate['connascence_violations'][:5]:  # Top 5
                print(f"   - {violation}")

        # Recommendations
        if aggregate['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(aggregate['recommendations'], 1):
                print(f"   {i}. {rec}")

        print("\n" + "=" * 80)
        print("END OF REPORT")
        print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_daily_analyzer.py <file_path> [--format json|text]")
        print("\nExample:")
        print("  python scripts/run_daily_analyzer.py src/protocols/EnhancedLightweightProtocol.py")
        sys.exit(1)

    file_path = sys.argv[1]
    format_type = 'text'

    if len(sys.argv) >= 3 and sys.argv[2] == '--format':
        format_type = sys.argv[3] if len(sys.argv) > 3 else 'text'

    try:
        runner = DailyAnalyzerRunner(file_path)
        runner.run_full_analysis()
        runner.print_report(format=format_type)

        # Exit code based on quality score
        score = runner.results['aggregate']['enterprise_quality_score']
        if score < 75.0:
            sys.exit(1)  # Fail if quality too low

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
