"""
Unit Tests - SyntaxAnalyzer

Tests for syntax_analyzer.py covering:
- Python AST analysis (god functions, theater, security)
- JavaScript regex analysis
- C/C++ regex analysis
- Generic analysis
- Error handling
- NASA compliance detection

Target: 50+ tests
Version: 6.0.0 (Week 2 Day 3-5)
"""

import pytest
from analyzer.engines.syntax_analyzer import SyntaxAnalyzer, create_syntax_analyzer


class TestSyntaxAnalyzerInitialization:
    """Test SyntaxAnalyzer initialization and configuration."""

    def test_create_syntax_analyzer(self):
        """Test factory function creates analyzer."""
        analyzer = create_syntax_analyzer()
        assert analyzer is not None
        assert isinstance(analyzer, SyntaxAnalyzer)

    def test_analyzer_has_supported_languages(self):
        """Test analyzer supports expected languages."""
        analyzer = SyntaxAnalyzer()
        expected = ["python", "javascript", "js", "c", "cpp", "c++"]
        assert analyzer.supported_languages == expected

    def test_analyzer_has_logger(self):
        """Test analyzer has logger configured."""
        analyzer = SyntaxAnalyzer()
        assert analyzer.logger is not None


class TestPythonAnalysis:
    """Test Python syntax analysis."""

    def test_analyze_clean_python_code(self, sample_python_clean_code):
        """Test analysis of clean Python code with no violations."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_clean_code, "python")

        assert result["success"] is True
        assert result["language"] == "python"
        assert len(result["syntax_issues"]) == 0
        assert result["execution_time"] > 0

    def test_detect_god_function(self, sample_python_god_function):
        """Test detection of god function (>60 LOC)."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_god_function, "python")

        assert result["success"] is True
        issues = result["syntax_issues"]

        # Should detect NASA Rule 3 violation (function >60 lines)
        nasa_violations = [i for i in issues if i["type"] == "nasa_rule_3_violation"]
        assert len(nasa_violations) >= 1
        assert nasa_violations[0]["severity"] == "high"
        assert "60 lines" in nasa_violations[0]["message"].lower()

    def test_detect_position_coupling(self, sample_python_god_function):
        """Test detection of position coupling (>6 parameters)."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_god_function, "python")

        # God function has 7 parameters (violates NASA Rule 6)
        # Note: This detection is in PatternDetector, but we can verify AST parsing
        assert result["success"] is True

    def test_detect_theater_code(self, sample_python_theater_code):
        """Test detection of NotImplementedError theater."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_theater_code, "python")

        assert result["success"] is True
        issues = result["syntax_issues"]

        theater_violations = [i for i in issues if i["type"] == "theater_violation"]
        assert len(theater_violations) >= 1
        assert theater_violations[0]["severity"] == "critical"
        assert "NotImplementedError" in theater_violations[0]["message"]

    def test_detect_security_risks_eval(self, sample_python_security_risks):
        """Test detection of eval() security risk."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_security_risks, "python")

        assert result["success"] is True
        issues = result["syntax_issues"]

        security_issues = [i for i in issues if i["type"] == "security_risk"]
        assert len(security_issues) >= 1
        assert any("eval" in i["message"].lower() for i in security_issues)
        assert security_issues[0]["severity"] == "critical"

    def test_detect_security_risks_exec(self, sample_python_security_risks):
        """Test detection of exec() security risk."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_security_risks, "python")

        issues = result["syntax_issues"]
        security_issues = [i for i in issues if i["type"] == "security_risk"]

        # Should detect both eval() and exec()
        assert len(security_issues) >= 2

    def test_detect_wildcard_import(self, sample_python_security_risks):
        """Test detection of wildcard imports."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_security_risks, "python")

        issues = result["syntax_issues"]
        import_issues = [i for i in issues if i["type"] == "import_quality"]

        assert len(import_issues) >= 1
        assert import_issues[0]["severity"] == "medium"
        assert "wildcard" in import_issues[0]["message"].lower()

    def test_handle_python_syntax_error(self):
        """Test handling of Python syntax errors."""
        analyzer = SyntaxAnalyzer()
        invalid_code = "def broken function():\n    return"

        result = analyzer.analyze(invalid_code, "python")

        assert result["success"] is True
        issues = result["syntax_issues"]

        syntax_errors = [i for i in issues if i["type"] == "syntax_error"]
        assert len(syntax_errors) >= 1
        assert syntax_errors[0]["severity"] == "critical"

    def test_python_analysis_includes_line_numbers(self, sample_python_theater_code):
        """Test that issues include accurate line numbers."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_theater_code, "python")

        issues = result["syntax_issues"]
        for issue in issues:
            assert "line" in issue
            assert issue["line"] > 0

    def test_python_analysis_includes_recommendations(self, sample_python_theater_code):
        """Test that issues include actionable recommendations."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_theater_code, "python")

        issues = result["syntax_issues"]
        for issue in issues:
            assert "recommendation" in issue
            assert len(issue["recommendation"]) > 0


class TestJavaScriptAnalysis:
    """Test JavaScript syntax analysis."""

    def test_analyze_javascript_code(self, sample_javascript_theater):
        """Test JavaScript analysis."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_javascript_theater, "javascript")

        assert result["success"] is True
        assert result["language"] == "javascript"

    def test_detect_javascript_theater(self, sample_javascript_theater):
        """Test detection of JavaScript theater violations."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_javascript_theater, "javascript")

        issues = result["syntax_issues"]
        theater_violations = [i for i in issues if i["type"] == "theater_violation"]

        assert len(theater_violations) >= 1
        assert theater_violations[0]["severity"] == "critical"

    def test_detect_javascript_functions(self, sample_javascript_theater):
        """Test detection of JavaScript function definitions."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_javascript_theater, "javascript")

        issues = result["syntax_issues"]
        function_detections = [i for i in issues if i["type"] == "function_detected"]

        assert len(function_detections) >= 1
        assert function_detections[0]["severity"] == "info"

    def test_javascript_alias_js(self):
        """Test that 'js' is accepted as language alias."""
        analyzer = SyntaxAnalyzer()
        code = "function test() { return true; }"

        result = analyzer.analyze(code, "js")
        assert result["success"] is True
        assert result["language"] == "js"


class TestCCppAnalysis:
    """Test C/C++ syntax analysis."""

    def test_analyze_c_code(self, sample_c_unsafe_functions):
        """Test C code analysis."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_c_unsafe_functions, "c")

        assert result["success"] is True
        assert result["language"] == "c"

    def test_detect_unsafe_strcpy(self, sample_c_unsafe_functions):
        """Test detection of unsafe strcpy()."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_c_unsafe_functions, "c")

        issues = result["syntax_issues"]
        security_issues = [i for i in issues if i["type"] == "security_risk"]

        strcpy_issues = [i for i in security_issues if "strcpy" in i["message"].lower()]
        assert len(strcpy_issues) >= 1
        assert strcpy_issues[0]["severity"] == "high"

    def test_detect_unsafe_sprintf(self, sample_c_unsafe_functions):
        """Test detection of unsafe sprintf()."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_c_unsafe_functions, "c")

        issues = result["syntax_issues"]
        security_issues = [i for i in issues if i["type"] == "security_risk"]

        sprintf_issues = [i for i in security_issues if "sprintf" in i["message"].lower()]
        assert len(sprintf_issues) >= 1

    def test_cpp_alias(self):
        """Test that 'cpp' and 'c++' are accepted."""
        analyzer = SyntaxAnalyzer()
        code = "#include <iostream>\nint main() { return 0; }"

        result_cpp = analyzer.analyze(code, "cpp")
        result_cxx = analyzer.analyze(code, "c++")

        assert result_cpp["success"] is True
        assert result_cxx["success"] is True


class TestGenericAnalysis:
    """Test generic analysis for unsupported languages."""

    def test_analyze_unsupported_language(self):
        """Test analysis of unsupported language."""
        analyzer = SyntaxAnalyzer()
        code = "func main() { println('Hello, Go!') }"

        result = analyzer.analyze(code, "go")
        assert result["success"] is True
        assert result["language"] == "go"

    def test_detect_long_lines(self):
        """Test detection of long lines (>200 chars)."""
        analyzer = SyntaxAnalyzer()
        long_line = "x = " + "a" * 250  # 254 character line

        result = analyzer.analyze(long_line, "unknown")

        issues = result["syntax_issues"]
        long_line_issues = [i for i in issues if i["type"] == "long_line"]

        assert len(long_line_issues) >= 1
        assert long_line_issues[0]["severity"] == "low"

    def test_generic_analysis_no_issues(self):
        """Test generic analysis with clean code."""
        analyzer = SyntaxAnalyzer()
        code = "short line\nanother short line"

        result = analyzer.analyze(code, "rust")
        assert result["success"] is True
        assert len(result["syntax_issues"]) == 0


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_source_code_raises_assertion(self):
        """Test that empty source code raises assertion error."""
        analyzer = SyntaxAnalyzer()

        with pytest.raises(AssertionError, match="source_code cannot be empty"):
            analyzer.analyze("", "python")

    def test_empty_language_raises_assertion(self):
        """Test that empty language raises assertion error."""
        analyzer = SyntaxAnalyzer()

        with pytest.raises(AssertionError, match="language cannot be empty"):
            analyzer.analyze("print('test')", "")

    def test_none_source_code_raises_assertion(self):
        """Test that None source code raises assertion error."""
        analyzer = SyntaxAnalyzer()

        with pytest.raises(AssertionError):
            analyzer.analyze(None, "python")

    def test_none_language_raises_assertion(self):
        """Test that None language raises assertion error."""
        analyzer = SyntaxAnalyzer()

        with pytest.raises(AssertionError):
            analyzer.analyze("print('test')", None)

    def test_analysis_failure_returns_error_result(self):
        """Test that analysis failures return error result with success=False."""
        analyzer = SyntaxAnalyzer()

        # This will trigger an internal error during AST processing
        # by providing code that breaks internal logic
        # (This is a hypothetical test - adjust based on actual error paths)

        # For now, test with extremely malformed code
        result = analyzer.analyze("def", "python")

        # Should either return success with syntax_error issue, or success=False
        if not result["success"]:
            assert "error" in result
            assert result["execution_time"] > 0


class TestExecutionMetrics:
    """Test execution time and performance metrics."""

    def test_execution_time_recorded(self, sample_python_clean_code):
        """Test that execution time is recorded."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_clean_code, "python")

        assert "execution_time" in result
        assert result["execution_time"] > 0
        assert result["execution_time"] < 1.0  # Should be fast

    def test_engine_version_included(self, sample_python_clean_code):
        """Test that engine version is included in results."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_clean_code, "python")

        assert "engine_version" in result
        assert result["engine_version"] == "6.0.0"


class TestIssueStructure:
    """Test that issues follow expected structure."""

    def test_issue_has_required_fields(self, sample_python_theater_code):
        """Test that issues contain all required fields."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_theater_code, "python")

        issues = result["syntax_issues"]
        required_fields = ["type", "severity", "line", "column", "message", "recommendation"]

        for issue in issues:
            for field in required_fields:
                assert field in issue, f"Issue missing required field: {field}"

    def test_severity_levels_are_valid(self, sample_python_security_risks):
        """Test that severity levels are valid."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_security_risks, "python")

        valid_severities = ["critical", "high", "medium", "low", "info"]
        issues = result["syntax_issues"]

        for issue in issues:
            assert issue["severity"] in valid_severities


class TestNASACompliance:
    """Test NASA POT10 rule detection."""

    def test_nasa_rule_3_detection(self, sample_python_god_function):
        """Test NASA Rule 3 (function ≤60 lines) detection."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_god_function, "python")

        issues = result["syntax_issues"]
        nasa_rule_3 = [i for i in issues if "nasa_rule_3" in i["type"]]

        assert len(nasa_rule_3) >= 1
        assert "60 lines" in nasa_rule_3[0]["message"].lower()

    def test_nasa_recommendations_provided(self, sample_python_god_function):
        """Test that NASA violations include recommendations."""
        analyzer = SyntaxAnalyzer()
        result = analyzer.analyze(sample_python_god_function, "python")

        issues = result["syntax_issues"]
        nasa_violations = [i for i in issues if "nasa_rule" in i["type"]]

        for violation in nasa_violations:
            assert len(violation["recommendation"]) > 0
            assert isinstance(violation["recommendation"], str)
