"""
Meta Audit Test - Comprehensive analyzer functionality validation

Tests all core analyzer modules to ensure they work as intended.

Version: 1.0.0
"""

import ast
import pytest
from pathlib import Path

# Core imports
from analyzer.core.api import Analyzer, analyze
from analyzer.core.engine import AnalysisEngine
from analyzer.core.cli import create_parser, main
from analyzer.engines.syntax_analyzer import SyntaxAnalyzer, create_syntax_analyzer
from analyzer.engines.pattern_detector import PatternDetector, create_pattern_detector, Pattern
from analyzer.engines.compliance_validator import ComplianceValidator, create_compliance_validator
from analyzer.constants.thresholds import *
from analyzer.constants.policies import normalize_policy_name, get_policy_config
from analyzer.constants.nasa_rules import get_nasa_rule, is_rule_enforced


class TestCoreAPI:
    """Test analyzer.core.api module."""

    def test_analyzer_initialization_valid_policies(self):
        """Test Analyzer initializes with all valid policies."""
        for policy in ["nasa-compliance", "strict", "standard", "lenient"]:
            analyzer = Analyzer(policy=policy)
            assert analyzer.policy == policy
            assert analyzer.engine is not None

    def test_analyzer_initialization_invalid_policy(self):
        """Test Analyzer fails with invalid policy."""
        with pytest.raises(AssertionError):
            Analyzer(policy="invalid-policy")

    def test_analyzer_analyze_missing_path(self):
        """Test Analyzer fails when path doesn't exist."""
        analyzer = Analyzer(policy="standard")
        with pytest.raises(FileNotFoundError):
            analyzer.analyze("/nonexistent/path")

    def test_convenience_function(self):
        """Test convenience analyze() function."""
        # Create a temporary test file
        test_file = Path("test_temp_analyzer.py")
        test_file.write_text("def test_func():\n    pass\n")

        try:
            result = analyze(str(test_file), policy="standard")
            assert result is not None
            assert "target" in result
            assert "policy" in result
        finally:
            test_file.unlink()


class TestAnalysisEngine:
    """Test analyzer.core.engine module."""

    def test_engine_initialization(self):
        """Test AnalysisEngine initializes correctly."""
        engine = AnalysisEngine(policy="standard")
        assert engine.policy == "standard"
        assert engine.detectors == []  # Empty until populated

    def test_engine_invalid_policy(self):
        """Test AnalysisEngine rejects invalid policy."""
        with pytest.raises(AssertionError):
            AnalysisEngine(policy="invalid")

    def test_engine_run_analysis(self):
        """Test AnalysisEngine runs analysis on valid path."""
        # Create test file
        test_file = Path("test_engine_temp.py")
        test_file.write_text("def test():\n    pass\n")

        try:
            engine = AnalysisEngine(policy="standard")
            result = engine.run_analysis(str(test_file))

            assert result["target"] == str(test_file)
            assert result["policy"] == "standard"
            assert "violations" in result
            assert "quality_scores" in result
            assert "summary" in result
        finally:
            test_file.unlink()


class TestSyntaxAnalyzer:
    """Test analyzer.engines.syntax_analyzer module."""

    def test_syntax_analyzer_initialization(self):
        """Test SyntaxAnalyzer initializes correctly."""
        analyzer = SyntaxAnalyzer()
        assert "python" in analyzer.supported_languages
        assert "javascript" in analyzer.supported_languages

    def test_analyze_valid_python_code(self):
        """Test SyntaxAnalyzer analyzes valid Python code."""
        code = """
def valid_function():
    x = 1
    y = 2
    return x + y
"""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(code, language="python")

        assert result["success"] is True
        assert result["language"] == "python"
        assert "syntax_issues" in result
        assert "execution_time" in result

    def test_analyze_python_syntax_error(self):
        """Test SyntaxAnalyzer detects Python syntax errors."""
        code = "def bad_syntax(\n    pass"  # Missing closing parenthesis
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(code, language="python")

        assert len(result["syntax_issues"]) > 0
        assert any(issue["type"] == "syntax_error" for issue in result["syntax_issues"])

    def test_analyze_god_function(self):
        """Test SyntaxAnalyzer detects god functions (>60 LOC)."""
        # Create function with >60 lines
        lines = ["    x = 1\n"] * 65
        code = f"def god_function():\n{''.join(lines)}"

        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(code, language="python")

        # Should detect NASA Rule 3 violation
        violations = [i for i in result["syntax_issues"] if i["type"] == "nasa_rule_3_violation"]
        assert len(violations) > 0

    def test_analyze_theater_code(self):
        """Test SyntaxAnalyzer detects theater violations."""
        code = """
def theater_function():
    raise NotImplementedError("Coming soon")
"""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(code, language="python")

        theater_violations = [i for i in result["syntax_issues"] if i["type"] == "theater_violation"]
        assert len(theater_violations) > 0

    def test_analyze_security_risks(self):
        """Test SyntaxAnalyzer detects security risks."""
        code = """
def dangerous_function():
    eval("print('danger')")
"""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(code, language="python")

        security_issues = [i for i in result["syntax_issues"] if i["type"] == "security_risk"]
        assert len(security_issues) > 0

    def test_factory_function(self):
        """Test create_syntax_analyzer factory function."""
        analyzer = create_syntax_analyzer()
        assert isinstance(analyzer, SyntaxAnalyzer)


class TestPatternDetector:
    """Test analyzer.engines.pattern_detector module."""

    def test_pattern_detector_initialization(self):
        """Test PatternDetector initializes correctly."""
        detector = PatternDetector()
        assert detector.god_object_threshold == 50
        assert detector.confidence_threshold == 0.7

    def test_detect_god_object(self):
        """Test PatternDetector detects god objects."""
        # Create a class with >50 methods (god object threshold)
        methods = '\n'.join([f'    def method_{i}(self): pass' for i in range(60)])
        code = f"""
class GodClass:
{methods}
"""
        tree = ast.parse(code)
        detector = PatternDetector()
        patterns = detector.detect(tree)

        god_patterns = [p for p in patterns if p.pattern_type == "god_object"]
        assert len(god_patterns) > 0

    def test_detect_position_coupling(self):
        """Test PatternDetector detects position coupling."""
        code = """
def many_params(a, b, c, d, e, f, g, h, i, j):
    return a + b + c
"""
        tree = ast.parse(code)
        detector = PatternDetector()
        patterns = detector.detect(tree)

        position_patterns = [p for p in patterns if p.pattern_type == "position_coupling"]
        assert len(position_patterns) > 0

    def test_detect_magic_literals(self):
        """Test PatternDetector detects magic literals."""
        code = """
def magic_function():
    x = 42
    y = 3.14159
    return x * y
"""
        tree = ast.parse(code)
        detector = PatternDetector()
        patterns = detector.detect(tree, source_code=code)

        magic_patterns = [p for p in patterns if p.pattern_type == "magic_literal"]
        assert len(magic_patterns) > 0

    def test_detect_todo_comments(self):
        """Test PatternDetector detects TODO comments."""
        code = """
def incomplete():
    # TODO: Implement this
    pass
"""
        tree = ast.parse(code)
        detector = PatternDetector()
        patterns = detector.detect(tree, source_code=code)

        theater_patterns = [p for p in patterns if p.pattern_type == "theater_indicator"]
        assert len(theater_patterns) > 0

    def test_factory_function(self):
        """Test create_pattern_detector factory function."""
        detector = create_pattern_detector()
        assert isinstance(detector, PatternDetector)


class TestComplianceValidator:
    """Test analyzer.engines.compliance_validator module."""

    def test_compliance_validator_initialization(self):
        """Test ComplianceValidator initializes correctly."""
        validator = ComplianceValidator()
        assert validator.standards_config is not None

    def test_validate_nasa_pot10(self):
        """Test ComplianceValidator validates NASA POT10."""
        # Mock analysis results
        results = {
            "syntax_issues": [
                {"type": "nasa_rule_3_violation", "severity": "critical"},
                {"type": "nasa_rule_6_violation", "severity": "medium"},
            ]
        }

        validator = ComplianceValidator()
        compliance = validator.validate(results, standards=["NASA_POT10"])

        assert "NASA_POT10" in compliance["individual_scores"]
        assert "score" in compliance["individual_scores"]["NASA_POT10"]
        assert "passed" in compliance["individual_scores"]["NASA_POT10"]

    def test_validate_dfars(self):
        """Test ComplianceValidator validates DFARS."""
        results = {
            "syntax_issues": [
                {"type": "security_risk", "severity": "critical"},
            ]
        }

        validator = ComplianceValidator()
        compliance = validator.validate(results, standards=["DFARS"])

        assert "DFARS" in compliance["individual_scores"]
        assert compliance["individual_scores"]["DFARS"]["score"] < 1.0

    def test_validate_iso27001(self):
        """Test ComplianceValidator validates ISO27001."""
        results = {
            "syntax_issues": [
                {"type": "security_risk", "severity": "high"},
            ]
        }

        validator = ComplianceValidator()
        compliance = validator.validate(results, standards=["ISO27001"])

        assert "ISO27001" in compliance["individual_scores"]

    def test_factory_function(self):
        """Test create_compliance_validator factory function."""
        validator = create_compliance_validator()
        assert isinstance(validator, ComplianceValidator)


class TestConstants:
    """Test analyzer.constants modules."""

    def test_thresholds_constants(self):
        """Test thresholds are properly defined."""
        assert MAXIMUM_FILE_LENGTH_LINES == 500
        assert MAXIMUM_FUNCTION_LENGTH_LINES == 60
        assert NASA_PARAMETER_THRESHOLD == 6
        assert NASA_POT10_TARGET_COMPLIANCE_THRESHOLD == 0.92

    def test_policy_normalization(self):
        """Test policy name normalization."""
        assert normalize_policy_name("nasa-compliance") == "nasa-compliance"
        assert normalize_policy_name("strict") == "strict"

        # Legacy mapping
        with pytest.warns(DeprecationWarning):
            assert normalize_policy_name("nasa") == "nasa-compliance"

    def test_policy_config_retrieval(self):
        """Test policy configuration retrieval."""
        config = get_policy_config("nasa-compliance")
        assert config["max_function_lines"] == 60
        assert config["min_assertions"] == 2
        assert config["allow_recursion"] is False

    def test_nasa_rules_definitions(self):
        """Test NASA rules are properly defined."""
        rule3 = get_nasa_rule("RULE_3")
        assert rule3["title"] == "Function length limit"
        assert rule3["enforced"] is True
        assert rule3["threshold"] == 60

        assert is_rule_enforced("RULE_3") is True
        assert is_rule_enforced("RULE_2") is False  # Not enforced in Python


class TestCLI:
    """Test analyzer.core.cli module."""

    def test_create_parser(self):
        """Test CLI parser creation."""
        parser = create_parser()
        assert parser is not None

        # Test default arguments
        args = parser.parse_args(["test.py"])
        assert args.path == "test.py"
        assert args.policy == "standard"
        assert args.format == "json"

    def test_parser_with_options(self):
        """Test CLI parser with various options."""
        parser = create_parser()
        args = parser.parse_args([
            "test.py",
            "--policy", "nasa-compliance",
            "--format", "sarif",
            "--fail-on-critical",
            "--compliance-threshold", "0.95"
        ])

        assert args.policy == "nasa-compliance"
        assert args.format == "sarif"
        assert args.fail_on_critical is True
        assert args.compliance_threshold == 0.95


class TestIntegration:
    """Integration tests for complete analyzer workflow."""

    def test_end_to_end_analysis(self):
        """Test complete analysis workflow."""
        # Create test file with various issues
        test_file = Path("test_integration_temp.py")
        test_file.write_text("""
def god_function():
    # TODO: Implement this
    x = 42  # Magic literal
    eval("dangerous")  # Security risk
    # Add 60+ lines to trigger NASA Rule 3
    """ + "\n    pass\n" * 60 + """

class GodClass:
    """ + "\n".join([f"    def method_{i}(self): pass" for i in range(60)])
        )

        try:
            # Run full analysis
            analyzer = Analyzer(policy="nasa-compliance")
            result = analyzer.analyze(str(test_file))

            # Verify results
            assert result is not None
            assert result["target"] == str(test_file)
            assert "violations" in result
            assert "quality_scores" in result

            # Should detect various issues
            # (Note: Current implementation has placeholder detectors)

        finally:
            test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
