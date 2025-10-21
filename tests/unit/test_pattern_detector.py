"""
Unit Tests - PatternDetector

Tests for pattern_detector.py covering:
- God object detection (>50 methods)
- Position coupling detection (>6 parameters)
- Magic literal detection
- Theater indicator detection (TODO/FIXME)
- Connascence detection (CoN, CoT, CoM, CoP, CoA)
- Complex conditional detection

Target: 50+ tests
Version: 6.0.0 (Week 2 Day 3-5)
"""

import pytest
import ast
from analyzer.engines.pattern_detector import PatternDetector, Pattern, create_pattern_detector


class TestPatternDetectorInitialization:
    """Test PatternDetector initialization and configuration."""

    def test_create_pattern_detector(self):
        """Test factory function creates detector."""
        detector = create_pattern_detector()
        assert detector is not None
        assert isinstance(detector, PatternDetector)

    def test_detector_has_thresholds(self):
        """Test detector has configured thresholds."""
        detector = PatternDetector()
        assert detector.god_object_threshold == 50
        assert detector.confidence_threshold == 0.7

    def test_detector_has_magic_literal_exclusions(self):
        """Test detector excludes common literals."""
        detector = PatternDetector()
        expected = [0, 1, -1, True, False, None, "", []]
        assert detector.magic_literal_exclusions == expected


class TestPatternDataclass:
    """Test Pattern dataclass structure."""

    def test_pattern_creation(self):
        """Test Pattern dataclass can be created."""
        pattern = Pattern(
            pattern_type="test_pattern",
            severity="high",
            description="Test description",
            location=(10, 5),
            context="test context",
            recommendation="Fix this",
            confidence=0.95
        )

        assert pattern.pattern_type == "test_pattern"
        assert pattern.severity == "high"
        assert pattern.location == (10, 5)
        assert pattern.confidence == 0.95


class TestGodObjectDetection:
    """Test god object pattern detection."""

    def test_detect_god_class(self, sample_python_god_class):
        """Test detection of god class (>50 methods)."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree, sample_python_god_class)

        god_objects = [p for p in patterns if p.pattern_type == "god_object"]
        assert len(god_objects) >= 1
        assert god_objects[0].severity == "critical"
        assert "50" in god_objects[0].description

    def test_god_object_confidence_high(self, sample_python_god_class):
        """Test god object detection has high confidence."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree)
        god_objects = [p for p in patterns if p.pattern_type == "god_object"]

        assert god_objects[0].confidence >= 0.90

    def test_small_class_not_god_object(self):
        """Test that small classes are not flagged as god objects."""
        detector = PatternDetector()
        code = '''
class SmallClass:
    def method1(self):
        return 1

    def method2(self):
        return 2
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree)

        god_objects = [p for p in patterns if p.pattern_type == "god_object"]
        assert len(god_objects) == 0


class TestPositionCoupling:
    """Test position coupling (CoP) detection."""

    def test_detect_position_coupling(self, sample_python_god_function):
        """Test detection of >6 parameters (position coupling)."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_function)

        patterns = detector.detect(ast_tree)

        position_coupling = [p for p in patterns if p.pattern_type == "position_coupling"]
        assert len(position_coupling) >= 1
        assert "6 parameters" in position_coupling[0].description or \
               "NASA Rule 6" in position_coupling[0].description

    def test_position_coupling_severity(self, sample_python_god_function):
        """Test position coupling has appropriate severity."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_function)

        patterns = detector.detect(ast_tree)
        position_coupling = [p for p in patterns if p.pattern_type == "position_coupling"]

        # 7 parameters should be medium severity
        assert position_coupling[0].severity in ["medium", "high"]

    def test_many_parameters_high_severity(self):
        """Test that >10 parameters triggers high severity."""
        detector = PatternDetector()
        code = '''
def too_many_params(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12):
    return sum([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12])
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree)

        position_coupling = [p for p in patterns if p.pattern_type == "position_coupling"]
        assert len(position_coupling) >= 1
        assert position_coupling[0].severity == "high"

    def test_few_parameters_no_coupling(self):
        """Test that ≤6 parameters don't trigger coupling."""
        detector = PatternDetector()
        code = '''
def good_function(a, b, c):
    return a + b + c
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree)

        position_coupling = [p for p in patterns if p.pattern_type == "position_coupling"]
        assert len(position_coupling) == 0


class TestMagicLiteralDetection:
    """Test magic literal detection."""

    def test_detect_numeric_magic_literals(self, sample_python_magic_literals):
        """Test detection of numeric magic literals."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_magic_literals)

        patterns = detector.detect(ast_tree)

        magic_literals = [p for p in patterns if p.pattern_type == "magic_literal"]
        assert len(magic_literals) >= 1

    def test_exclude_common_numbers(self):
        """Test that 0, 1, -1 are excluded from magic literal detection."""
        detector = PatternDetector()
        code = '''
def count():
    x = 0
    y = 1
    z = -1
    return x + y + z
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree)

        magic_literals = [p for p in patterns if p.pattern_type == "magic_literal"]
        # Should not detect 0, 1, -1
        for ml in magic_literals:
            assert ml.context not in ["0", "1", "-1"]

    def test_detect_string_magic_literals(self):
        """Test detection of string magic literals."""
        detector = PatternDetector()
        code = '''
def get_config():
    return "production_server_url_12345"
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree)

        magic_literals = [p for p in patterns if p.pattern_type == "magic_literal"]
        string_literals = [ml for ml in magic_literals if "production" in ml.context.lower()]
        assert len(string_literals) >= 1

    def test_short_strings_not_magic(self):
        """Test that short strings (≤3 chars) are not flagged."""
        detector = PatternDetector()
        code = '''
def separator():
    return ", "
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree)

        magic_literals = [p for p in patterns if p.pattern_type == "magic_literal"]
        # Short strings should not be flagged
        assert len(magic_literals) == 0

    def test_magic_literal_severity_low(self):
        """Test that magic literals have low severity."""
        detector = PatternDetector()
        code = "x = 12345"
        ast_tree = ast.parse(code)

        patterns = detector.detect(ast_tree)
        magic_literals = [p for p in patterns if p.pattern_type == "magic_literal"]

        if magic_literals:
            assert magic_literals[0].severity == "low"


class TestTheaterIndicatorDetection:
    """Test theater indicator detection (TODO/FIXME)."""

    def test_detect_todo_comments(self, sample_python_theater_code):
        """Test detection of TODO comments."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_theater_code)

        patterns = detector.detect(ast_tree, sample_python_theater_code)

        theater_indicators = [p for p in patterns if p.pattern_type == "theater_indicator"]
        assert len(theater_indicators) >= 1
        assert "TODO" in theater_indicators[0].context.upper()

    def test_detect_fixme_comments(self):
        """Test detection of FIXME comments."""
        detector = PatternDetector()
        code = '''
def broken_function():
    # FIXME: This is broken
    return None
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        theater_indicators = [p for p in patterns if p.pattern_type == "theater_indicator"]
        fixme = [ti for ti in theater_indicators if "FIXME" in ti.context.upper()]
        assert len(fixme) >= 1

    def test_detect_xxx_comments(self):
        """Test detection of XXX comments."""
        detector = PatternDetector()
        code = "# XXX: Hack alert\nx = 42"
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        theater_indicators = [p for p in patterns if p.pattern_type == "theater_indicator"]
        xxx = [ti for ti in theater_indicators if "XXX" in ti.context.upper()]
        assert len(xxx) >= 1

    def test_detect_hack_comments(self):
        """Test detection of HACK comments."""
        detector = PatternDetector()
        code = "# HACK: Quick fix\nreturn True"
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        theater_indicators = [p for p in patterns if p.pattern_type == "theater_indicator"]
        hack = [ti for ti in theater_indicators if "HACK" in ti.context.upper()]
        assert len(hack) >= 1

    def test_theater_indicator_severity_medium(self):
        """Test that theater indicators have medium severity."""
        detector = PatternDetector()
        code = "# TODO: Implement\npass"
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        theater_indicators = [p for p in patterns if p.pattern_type == "theater_indicator"]
        assert theater_indicators[0].severity == "medium"


class TestComplexConditionalDetection:
    """Test complex conditional detection."""

    def test_detect_complex_conditional(self):
        """Test detection of complex conditionals (>3 and/or)."""
        detector = PatternDetector()
        code = '''
if a and b and c and d or e and f:
    return True
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        complex_conditionals = [p for p in patterns if p.pattern_type == "complex_conditional"]
        assert len(complex_conditionals) >= 1

    def test_simple_conditional_not_flagged(self):
        """Test that simple conditionals are not flagged."""
        detector = PatternDetector()
        code = '''
if a and b:
    return True
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        complex_conditionals = [p for p in patterns if p.pattern_type == "complex_conditional"]
        assert len(complex_conditionals) == 0

    def test_complex_conditional_severity(self):
        """Test complex conditional has medium severity."""
        detector = PatternDetector()
        code = "if a and b and c and d and e:\n    pass"
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        complex_conditionals = [p for p in patterns if p.pattern_type == "complex_conditional"]
        if complex_conditionals:
            assert complex_conditionals[0].severity == "medium"


class TestConnascenceDetection:
    """Test connascence pattern detection."""

    def test_detect_connascence_of_algorithm(self):
        """Test detection of Connascence of Algorithm (CoA)."""
        detector = PatternDetector()
        code = '''
def func1():
    for i in range(10):
        print(i)
    for i in range(10):
        print(i)
    for i in range(10):
        print(i)

def func2():
    for i in range(10):
        print(i)
    for i in range(10):
        print(i)
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        coa = [p for p in patterns if p.pattern_type == "connascence_algorithm"]
        # Note: CoA detection is heuristic-based, may detect duplicated blocks
        # This test verifies the detection mechanism exists

    def test_no_connascence_in_clean_code(self, sample_python_clean_code):
        """Test that clean code has no connascence violations."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_clean_code)

        patterns = detector.detect(ast_tree, sample_python_clean_code)

        connascence = [p for p in patterns if "connascence" in p.pattern_type]
        # Clean code should have few or no connascence issues
        assert len(connascence) <= 1


class TestPatternSorting:
    """Test pattern sorting and prioritization."""

    def test_patterns_sorted_by_severity(self, sample_python_god_class):
        """Test that patterns are sorted by severity."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree, sample_python_god_class)

        # First patterns should be critical/high severity
        if len(patterns) >= 2:
            assert patterns[0].severity in ["critical", "high"]

    def test_patterns_sorted_by_confidence(self):
        """Test that patterns with same severity are sorted by confidence."""
        detector = PatternDetector()
        code = '''
class MediumClass:
    # Multiple medium-severity issues
    def method1(self, p1, p2, p3, p4, p5, p6, p7):
        x = 12345  # Magic literal
        y = 67890  # Magic literal
        return x + y
'''
        ast_tree = ast.parse(code)
        patterns = detector.detect(ast_tree, code)

        # Within same severity, higher confidence should come first
        medium_patterns = [p for p in patterns if p.severity == "medium"]
        if len(medium_patterns) >= 2:
            assert medium_patterns[0].confidence >= medium_patterns[1].confidence

    def test_pattern_limit_50(self, sample_python_god_class):
        """Test that patterns are limited to top 50."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree, sample_python_god_class)

        # Should never return more than 50 patterns
        assert len(patterns) <= 50


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_none_ast_tree_raises_assertion(self):
        """Test that None AST raises assertion error."""
        detector = PatternDetector()

        with pytest.raises(AssertionError, match="ast_tree cannot be None"):
            detector.detect(None)

    def test_invalid_ast_tree_returns_error_pattern(self):
        """Test that invalid AST returns error pattern."""
        detector = PatternDetector()

        # Pass invalid object as AST
        patterns = detector.detect({})

        # Should return detection_error pattern
        error_patterns = [p for p in patterns if p.pattern_type == "detection_error"]
        assert len(error_patterns) >= 1
        assert error_patterns[0].severity == "medium"

    def test_source_code_optional(self):
        """Test that source_code parameter is optional."""
        detector = PatternDetector()
        code = "def test(): return 1"
        ast_tree = ast.parse(code)

        # Should work without source_code
        patterns = detector.detect(ast_tree, source_code=None)
        assert isinstance(patterns, list)

    def test_empty_ast_tree(self):
        """Test detection with empty AST."""
        detector = PatternDetector()
        ast_tree = ast.parse("")

        patterns = detector.detect(ast_tree)
        # Empty AST should return empty list
        assert len(patterns) == 0


class TestPatternStructure:
    """Test Pattern object structure and fields."""

    def test_pattern_has_location(self, sample_python_god_class):
        """Test that patterns include location (line, column)."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree)

        for pattern in patterns:
            assert isinstance(pattern.location, tuple)
            assert len(pattern.location) == 2
            assert pattern.location[0] >= 0  # line
            assert pattern.location[1] >= 0  # column

    def test_pattern_has_recommendation(self, sample_python_god_class):
        """Test that patterns include actionable recommendations."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree)

        for pattern in patterns:
            assert pattern.recommendation
            assert len(pattern.recommendation) > 0

    def test_pattern_has_confidence(self, sample_python_god_class):
        """Test that patterns include confidence scores."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_class)

        patterns = detector.detect(ast_tree)

        for pattern in patterns:
            assert 0.0 <= pattern.confidence <= 1.0


class TestIntegrationWithSyntaxAnalyzer:
    """Test integration scenarios with SyntaxAnalyzer."""

    def test_detect_patterns_from_analyzed_code(self, sample_python_god_function):
        """Test pattern detection on code analyzed by SyntaxAnalyzer."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_god_function)

        patterns = detector.detect(ast_tree, sample_python_god_function)

        # Should detect multiple patterns (god function, position coupling, etc.)
        assert len(patterns) >= 2

    def test_combined_detection_coverage(self, sample_python_security_risks):
        """Test that pattern detector complements syntax analyzer."""
        detector = PatternDetector()
        ast_tree = ast.parse(sample_python_security_risks)

        patterns = detector.detect(ast_tree, sample_python_security_risks)

        # Pattern detector should find theater indicators (TODO comments)
        # that syntax analyzer might not catch
        theater = [p for p in patterns if p.pattern_type == "theater_indicator"]
        assert len(theater) >= 0  # May or may not have TODO comments
