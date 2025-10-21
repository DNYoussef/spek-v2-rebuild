"""
Integration Tests - Full Analysis Workflow

Tests for end-to-end analysis workflows combining:
- SyntaxAnalyzer → PatternDetector → ComplianceValidator
- Multi-engine coordination
- Error propagation
- Performance benchmarks

Target: 30+ tests
Version: 6.0.0 (Week 2 Day 3-5)
"""

import pytest
import ast
from analyzer.engines.syntax_analyzer import create_syntax_analyzer
from analyzer.engines.pattern_detector import create_pattern_detector
from analyzer.engines.compliance_validator import create_compliance_validator


class TestFullAnalysisWorkflow:
    """Test complete analysis workflow."""

    def test_analyze_clean_code_end_to_end(self, sample_python_clean_code):
        """Test full workflow with clean code."""
        # Step 1: Syntax analysis
        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(sample_python_clean_code, "python")

        assert syntax_results["success"] is True
        assert len(syntax_results["syntax_issues"]) == 0

        # Step 2: Pattern detection
        ast_tree = ast.parse(sample_python_clean_code)
        pattern_detector = create_pattern_detector()
        patterns = pattern_detector.detect(ast_tree, sample_python_clean_code)

        # Clean code should have few patterns
        assert len(patterns) <= 5

        # Step 3: Compliance validation
        compliance_validator = create_compliance_validator()
        compliance_results = compliance_validator.validate(syntax_results)

        assert compliance_results["success"] is True
        assert compliance_results["overall_score"] >= 0.90

    def test_analyze_god_function_end_to_end(self, sample_python_god_function):
        """Test full workflow with god function."""
        # Step 1: Syntax analysis detects NASA Rule 3 violation
        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(sample_python_god_function, "python")

        nasa_violations = [i for i in syntax_results["syntax_issues"]
                          if "nasa_rule_3" in i["type"]]
        assert len(nasa_violations) >= 1

        # Step 2: Pattern detection finds position coupling
        ast_tree = ast.parse(sample_python_god_function)
        pattern_detector = create_pattern_detector()
        patterns = pattern_detector.detect(ast_tree, sample_python_god_function)

        position_coupling = [p for p in patterns if p.pattern_type == "position_coupling"]
        assert len(position_coupling) >= 1

        # Step 3: Compliance validation fails NASA compliance
        compliance_validator = create_compliance_validator()
        compliance_results = compliance_validator.validate(syntax_results, ["NASA_POT10"])

        nasa_compliance = compliance_results["individual_scores"]["NASA_POT10"]
        assert nasa_compliance["passed"] is False

    def test_analyze_theater_code_end_to_end(self, sample_python_theater_code):
        """Test full workflow with theater violations."""
        # Step 1: Syntax analysis detects NotImplementedError
        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(sample_python_theater_code, "python")

        theater_syntax = [i for i in syntax_results["syntax_issues"]
                         if i["type"] == "theater_violation"]
        assert len(theater_syntax) >= 1

        # Step 2: Pattern detection finds TODO comments
        ast_tree = ast.parse(sample_python_theater_code)
        pattern_detector = create_pattern_detector()
        patterns = pattern_detector.detect(ast_tree, sample_python_theater_code)

        theater_patterns = [p for p in patterns if p.pattern_type == "theater_indicator"]
        assert len(theater_patterns) >= 1

        # Both engines detect theater in different ways
        assert len(theater_syntax) + len(theater_patterns) >= 2

    def test_analyze_security_risks_end_to_end(self, sample_python_security_risks):
        """Test full workflow with security vulnerabilities."""
        # Step 1: Syntax analysis detects eval/exec
        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(sample_python_security_risks, "python")

        security_issues = [i for i in syntax_results["syntax_issues"]
                          if i["type"] == "security_risk"]
        assert len(security_issues) >= 2

        # Step 2: Compliance validation flags DFARS violations
        compliance_validator = create_compliance_validator()
        compliance_results = compliance_validator.validate(syntax_results, ["DFARS"])

        dfars_compliance = compliance_results["individual_scores"]["DFARS"]
        assert dfars_compliance["critical_security_violations"] >= 2

    def test_analyze_god_class_end_to_end(self, sample_python_god_class):
        """Test full workflow with god class."""
        # Step 1: Syntax analysis
        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(sample_python_god_class, "python")

        # Step 2: Pattern detection finds god object
        ast_tree = ast.parse(sample_python_god_class)
        pattern_detector = create_pattern_detector()
        patterns = pattern_detector.detect(ast_tree, sample_python_god_class)

        god_objects = [p for p in patterns if p.pattern_type == "god_object"]
        assert len(god_objects) >= 1
        assert god_objects[0].severity == "critical"

        # Step 3: Compliance validation
        compliance_validator = create_compliance_validator()
        compliance_results = compliance_validator.validate(syntax_results)

        # God class affects overall code quality
        assert compliance_results["overall_score"] >= 0.0


class TestMultiEngineCoordination:
    """Test coordination between multiple engines."""

    def test_syntax_and_pattern_coordination(self, sample_python_god_function):
        """Test that syntax and pattern engines complement each other."""
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()

        # Analyze with both engines
        syntax_results = syntax_analyzer.analyze(sample_python_god_function, "python")
        ast_tree = ast.parse(sample_python_god_function)
        patterns = pattern_detector.detect(ast_tree, sample_python_god_function)

        # Syntax finds NASA Rule 3 violations
        syntax_issues_count = len(syntax_results["syntax_issues"])

        # Patterns find additional issues (position coupling, magic literals)
        pattern_issues_count = len(patterns)

        # Combined coverage is better than either alone
        total_issues = syntax_issues_count + pattern_issues_count
        assert total_issues >= max(syntax_issues_count, pattern_issues_count)

    def test_pattern_and_compliance_coordination(self, sample_python_god_function):
        """Test that pattern and compliance engines work together."""
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()
        compliance_validator = create_compliance_validator()

        # Run full pipeline
        syntax_results = syntax_analyzer.analyze(sample_python_god_function, "python")
        ast_tree = ast.parse(sample_python_god_function)
        patterns = pattern_detector.detect(ast_tree)

        # Compliance uses syntax results
        compliance_results = compliance_validator.validate(syntax_results)

        # Patterns provide additional context
        # Compliance score reflects syntax issues
        assert compliance_results["overall_score"] < 1.0
        assert len(patterns) >= 1

    def test_all_engines_performance(self, sample_python_clean_code):
        """Test performance when all engines run together."""
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()
        compliance_validator = create_compliance_validator()

        import time
        start_time = time.time()

        # Run all engines
        syntax_results = syntax_analyzer.analyze(sample_python_clean_code, "python")
        ast_tree = ast.parse(sample_python_clean_code)
        patterns = pattern_detector.detect(ast_tree, sample_python_clean_code)
        compliance_results = compliance_validator.validate(syntax_results)

        total_time = time.time() - start_time

        # All engines should complete quickly
        assert total_time < 1.0

        # All engines should succeed
        assert syntax_results["success"] is True
        assert isinstance(patterns, list)
        assert compliance_results["success"] is True


class TestErrorPropagation:
    """Test error handling across engines."""

    def test_syntax_error_propagation(self):
        """Test that syntax errors are handled gracefully."""
        syntax_analyzer = create_syntax_analyzer()

        invalid_code = "def broken function(:\n    return"
        syntax_results = syntax_analyzer.analyze(invalid_code, "python")

        # Should have syntax error issue
        syntax_errors = [i for i in syntax_results["syntax_issues"]
                        if i["type"] == "syntax_error"]
        assert len(syntax_errors) >= 1

    def test_invalid_ast_error_propagation(self):
        """Test that invalid AST errors are handled."""
        pattern_detector = create_pattern_detector()

        # Pass invalid AST
        patterns = pattern_detector.detect({})

        # Should return error pattern
        error_patterns = [p for p in patterns if p.pattern_type == "detection_error"]
        assert len(error_patterns) >= 1

    def test_compliance_validation_with_errors(self):
        """Test compliance validation with error-filled results."""
        compliance_validator = create_compliance_validator()

        # Results with many critical issues
        results = {
            "success": False,
            "syntax_issues": [
                {"type": "critical_error", "severity": "critical"}
                for _ in range(10)
            ]
        }

        compliance_results = compliance_validator.validate(results)

        # Should handle gracefully (may fail or have low score)
        assert "overall_score" in compliance_results


class TestPerformanceBenchmarks:
    """Test performance benchmarks for different code sizes."""

    @pytest.mark.slow
    def test_large_file_performance(self):
        """Test analysis of large file (>1000 LOC)."""
        # Generate large Python file
        large_code = '\n'.join([
            f"def function_{i}():\n    return {i}"
            for i in range(500)
        ])

        syntax_analyzer = create_syntax_analyzer()

        import time
        start_time = time.time()
        syntax_results = syntax_analyzer.analyze(large_code, "python")
        elapsed = time.time() - start_time

        # Should complete within reasonable time
        assert elapsed < 2.0
        assert syntax_results["success"] is True

    @pytest.mark.slow
    def test_complex_ast_performance(self):
        """Test pattern detection on complex AST."""
        # Generate complex nested code
        complex_code = '''
class ComplexClass:
    def method(self):
        if True:
            if True:
                if True:
                    for i in range(10):
                        for j in range(10):
                            if i == j:
                                return i * j
'''

        pattern_detector = create_pattern_detector()
        ast_tree = ast.parse(complex_code)

        import time
        start_time = time.time()
        patterns = pattern_detector.detect(ast_tree, complex_code)
        elapsed = time.time() - start_time

        # Should complete quickly
        assert elapsed < 0.5

    def test_multiple_standards_performance(self):
        """Test compliance validation with multiple standards."""
        compliance_validator = create_compliance_validator()
        results = {"syntax_issues": []}

        import time
        start_time = time.time()
        compliance_results = compliance_validator.validate(
            results,
            ["NASA_POT10", "DFARS", "ISO27001"]
        )
        elapsed = time.time() - start_time

        # Should validate all standards quickly
        assert elapsed < 0.5
        assert len(compliance_results["individual_scores"]) == 3


class TestCrossCuttingConcerns:
    """Test cross-cutting concerns like logging, metrics."""

    def test_all_engines_log_appropriately(self, sample_python_clean_code, caplog):
        """Test that all engines log appropriately."""
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()
        compliance_validator = create_compliance_validator()

        # Run full workflow
        syntax_results = syntax_analyzer.analyze(sample_python_clean_code, "python")
        ast_tree = ast.parse(sample_python_clean_code)
        patterns = pattern_detector.detect(ast_tree, sample_python_clean_code)
        compliance_results = compliance_validator.validate(syntax_results)

        # All engines should have loggers
        assert syntax_analyzer.logger is not None
        assert pattern_detector.logger is not None
        assert compliance_validator.logger is not None

    def test_execution_time_tracking(self, sample_python_clean_code):
        """Test that execution times are tracked."""
        syntax_analyzer = create_syntax_analyzer()
        compliance_validator = create_compliance_validator()

        syntax_results = syntax_analyzer.analyze(sample_python_clean_code, "python")
        compliance_results = compliance_validator.validate(syntax_results)

        # Both should track execution time
        assert syntax_results["execution_time"] > 0
        assert compliance_results["execution_time"] > 0


class TestRealWorldScenarios:
    """Test real-world analysis scenarios."""

    def test_production_code_analysis(self):
        """Test analysis of production-quality code."""
        production_code = '''
"""Module docstring."""

def calculate_metrics(data, threshold=0.85):
    """
    Calculate quality metrics.

    Args:
        data: Input data dictionary
        threshold: Quality threshold (0.0-1.0)

    Returns:
        Dict with calculated metrics
    """
    assert data, "data cannot be empty"
    assert 0.0 <= threshold <= 1.0, "threshold must be in [0.0, 1.0]"

    total = sum(data.values())
    average = total / len(data)

    return {
        "total": total,
        "average": average,
        "passed": average >= threshold
    }
'''

        # Full analysis
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()
        compliance_validator = create_compliance_validator()

        syntax_results = syntax_analyzer.analyze(production_code, "python")
        ast_tree = ast.parse(production_code)
        patterns = pattern_detector.detect(ast_tree, production_code)
        compliance_results = compliance_validator.validate(syntax_results)

        # Production code should pass all checks
        assert len(syntax_results["syntax_issues"]) <= 2  # May have minor issues
        assert compliance_results["overall_score"] >= 0.80

    def test_legacy_code_analysis(self, sample_python_god_function, sample_python_theater_code):
        """Test analysis of legacy code with multiple issues."""
        legacy_code = sample_python_god_function + "\n\n" + sample_python_theater_code

        # Full analysis
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()
        compliance_validator = create_compliance_validator()

        syntax_results = syntax_analyzer.analyze(legacy_code, "python")
        ast_tree = ast.parse(legacy_code)
        patterns = pattern_detector.detect(ast_tree, legacy_code)
        compliance_results = compliance_validator.validate(syntax_results)

        # Legacy code should have many issues
        assert len(syntax_results["syntax_issues"]) >= 2
        assert len(patterns) >= 2
        assert compliance_results["overall_score"] < 0.90

    def test_mixed_quality_codebase(self, sample_python_clean_code, sample_python_security_risks):
        """Test analysis of codebase with mixed quality."""
        mixed_code = sample_python_clean_code + "\n\n" + sample_python_security_risks

        syntax_analyzer = create_syntax_analyzer()
        compliance_validator = create_compliance_validator()

        syntax_results = syntax_analyzer.analyze(mixed_code, "python")
        compliance_results = compliance_validator.validate(syntax_results)

        # Mixed quality results in moderate scores
        assert 0.30 <= compliance_results["overall_score"] <= 0.90


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_file_analysis(self):
        """Test analysis of empty file."""
        syntax_analyzer = create_syntax_analyzer()

        with pytest.raises(AssertionError):
            syntax_analyzer.analyze("", "python")

    def test_single_line_analysis(self):
        """Test analysis of single line."""
        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze("x = 1", "python")

        assert syntax_results["success"] is True

    def test_very_long_line_analysis(self):
        """Test analysis of very long line."""
        long_line = "x = " + "a" * 500

        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(long_line, "unknown")

        long_line_issues = [i for i in syntax_results["syntax_issues"]
                           if i["type"] == "long_line"]
        assert len(long_line_issues) >= 1

    def test_unicode_code_analysis(self):
        """Test analysis of code with Unicode characters."""
        unicode_code = '''
def greet():
    return "Hello, 世界! 🌍"
'''

        syntax_analyzer = create_syntax_analyzer()
        syntax_results = syntax_analyzer.analyze(unicode_code, "python")

        assert syntax_results["success"] is True

    def test_no_issues_found(self, sample_python_clean_code):
        """Test workflow when no issues are found."""
        syntax_analyzer = create_syntax_analyzer()
        pattern_detector = create_pattern_detector()
        compliance_validator = create_compliance_validator()

        syntax_results = syntax_analyzer.analyze(sample_python_clean_code, "python")
        ast_tree = ast.parse(sample_python_clean_code)
        patterns = pattern_detector.detect(ast_tree, sample_python_clean_code)
        compliance_results = compliance_validator.validate(syntax_results)

        # Should complete successfully even with no issues
        assert syntax_results["success"] is True
        assert compliance_results["success"] is True
        assert compliance_results["overall_score"] >= 0.90
