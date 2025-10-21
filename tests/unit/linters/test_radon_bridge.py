"""
Tests for Radon Bridge - Real Cyclomatic Complexity & Maintainability Metrics

Test Coverage:
- Initialization and validation
- Availability detection
- Cyclomatic complexity execution
- Maintainability index execution
- Violation conversion
- Severity mapping
- Safe run wrapper
- Registry integration
- Edge cases
- Performance
- Real-world scenarios

Author: SPEK Platform Team
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json
from typing import Dict, Any

from analyzer.linters.radon_bridge import RadonBridge
from analyzer.utils.types import ConnascenceViolation


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def radon_bridge():
    """Create RadonBridge instance for testing."""
    return RadonBridge(timeout=60)


@pytest.fixture
def sample_cc_output():
    """Sample Radon CC JSON output."""
    return {
        "test_file.py": [
            {
                "type": "method",
                "name": "complex_function",
                "lineno": 10,
                "complexity": 15,
                "rank": "C"
            },
            {
                "type": "function",
                "name": "simple_function",
                "lineno": 30,
                "complexity": 3,
                "rank": "A"
            },
            {
                "type": "method",
                "name": "very_complex_function",
                "lineno": 50,
                "complexity": 55,
                "rank": "F"
            }
        ]
    }


@pytest.fixture
def sample_mi_output():
    """Sample Radon MI JSON output."""
    return {
        "test_file.py": {
            "mi": 45.3,
            "rank": "B"
        }
    }


@pytest.fixture
def low_mi_output():
    """Sample Radon MI output with low maintainability."""
    return {
        "bad_file.py": {
            "mi": 8.5,
            "rank": "F"
        }
    }


# ============================================================================
# 1. Initialization & Validation Tests (5 tests)
# ============================================================================

class TestInitialization:
    """Test RadonBridge initialization and validation."""

    def test_default_initialization(self):
        """Test default timeout initialization."""
        bridge = RadonBridge()
        assert bridge.timeout == 60
        assert bridge.name == "radon"

    def test_custom_timeout(self):
        """Test custom timeout configuration."""
        bridge = RadonBridge(timeout=120)
        assert bridge.timeout == 120

    def test_invalid_timeout_type(self):
        """Test that non-integer timeout raises assertion."""
        with pytest.raises(AssertionError, match="Timeout must be an integer"):
            RadonBridge(timeout="60")  # String instead of int

    def test_invalid_timeout_value(self):
        """Test that non-positive timeout raises assertion."""
        with pytest.raises(AssertionError, match="Timeout must be positive"):
            RadonBridge(timeout=-10)

    def test_zero_timeout(self):
        """Test that zero timeout raises assertion."""
        with pytest.raises(AssertionError, match="Timeout must be positive"):
            RadonBridge(timeout=0)


# ============================================================================
# 2. Availability Detection Tests (5 tests)
# ============================================================================

class TestAvailability:
    """Test Radon availability detection."""

    @patch('subprocess.run')
    def test_radon_available(self, mock_run, radon_bridge):
        """Test when Radon is installed and available."""
        import sys
        mock_run.return_value = Mock(returncode=0, stdout="Radon 5.1.0")
        assert radon_bridge.is_available() is True
        mock_run.assert_called_once_with(
            [sys.executable, '-m', 'radon', '--version'],
            capture_output=True,
            timeout=5,
            text=True
        )

    @patch('subprocess.run')
    def test_radon_not_installed(self, mock_run, radon_bridge):
        """Test when Radon is not installed."""
        mock_run.side_effect = FileNotFoundError()
        assert radon_bridge.is_available() is False

    @patch('subprocess.run')
    def test_radon_command_fails(self, mock_run, radon_bridge):
        """Test when Radon command fails."""
        mock_run.return_value = Mock(returncode=1)
        assert radon_bridge.is_available() is False

    @patch('subprocess.run')
    def test_radon_timeout(self, mock_run, radon_bridge):
        """Test when Radon version check times out."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=['radon'], timeout=5)
        assert radon_bridge.is_available() is False

    @patch('subprocess.run')
    def test_radon_unexpected_error(self, mock_run, radon_bridge):
        """Test when unexpected error occurs."""
        mock_run.side_effect = RuntimeError("Unexpected error")
        assert radon_bridge.is_available() is False


# ============================================================================
# 3. Execution Tests (10 tests)
# ============================================================================

class TestExecution:
    """Test Radon execution."""

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_successful_execution(self, mock_mi, mock_cc, radon_bridge, sample_cc_output, sample_mi_output, tmp_path):
        """Test successful Radon execution."""
        mock_cc.return_value = sample_cc_output
        mock_mi.return_value = sample_mi_output

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert result['success'] is True
        assert 'violations' in result
        assert 'raw_output' in result
        assert 'execution_time' in result
        assert result['linter'] == 'radon'
        assert 'metrics' in result

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_execution_with_no_violations(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test execution with clean code (no violations)."""
        # All functions have low complexity (A rank)
        mock_cc.return_value = {
            "clean_file.py": [
                {"type": "function", "name": "simple", "lineno": 1, "complexity": 2, "rank": "A"}
            ]
        }
        # High maintainability index
        mock_mi.return_value = {
            "clean_file.py": {"mi": 85.0, "rank": "A"}
        }

        test_file = tmp_path / "clean.py"
        test_file.write_text("def simple(): return 1")

        result = radon_bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 0  # No violations for clean code

    @patch.object(RadonBridge, '_run_radon_cc')
    def test_execution_timeout(self, mock_cc, radon_bridge, tmp_path):
        """Test execution timeout handling."""
        mock_cc.side_effect = subprocess.TimeoutExpired(cmd=['radon'], timeout=60)

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert result['success'] is False
        assert 'error' in result
        assert 'timed out' in result['error']
        assert len(result['violations']) == 0

    @patch.object(RadonBridge, '_run_radon_cc')
    def test_execution_json_parse_error(self, mock_cc, radon_bridge, tmp_path):
        """Test handling of malformed JSON output."""
        mock_cc.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert result['success'] is False
        assert 'error' in result
        assert 'Failed to parse' in result['error']

    def test_execution_file_not_found(self, radon_bridge):
        """Test execution with non-existent file."""
        with pytest.raises(FileNotFoundError):
            radon_bridge.run(Path("/nonexistent/file.py"))

    def test_execution_none_file_path(self, radon_bridge):
        """Test execution with None file_path."""
        with pytest.raises(AssertionError, match="file_path cannot be None"):
            radon_bridge.run(None)

    def test_execution_invalid_file_path_type(self, radon_bridge):
        """Test execution with invalid file_path type."""
        with pytest.raises(AssertionError, match="file_path must be a Path object"):
            radon_bridge.run("not_a_path_object")

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_execution_time_measurement(self, mock_mi, mock_cc, radon_bridge, sample_cc_output, sample_mi_output, tmp_path):
        """Test that execution time is measured."""
        mock_cc.return_value = sample_cc_output
        mock_mi.return_value = sample_mi_output

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert 'execution_time' in result
        assert isinstance(result['execution_time'], float)
        assert result['execution_time'] >= 0

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_raw_output_structure(self, mock_mi, mock_cc, radon_bridge, sample_cc_output, sample_mi_output, tmp_path):
        """Test raw output includes both CC and MI data."""
        mock_cc.return_value = sample_cc_output
        mock_mi.return_value = sample_mi_output

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert 'raw_output' in result
        assert 'cyclomatic_complexity' in result['raw_output']
        assert 'maintainability_index' in result['raw_output']
        assert result['raw_output']['cyclomatic_complexity'] == sample_cc_output
        assert result['raw_output']['maintainability_index'] == sample_mi_output

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_metrics_extraction(self, mock_mi, mock_cc, radon_bridge, sample_cc_output, sample_mi_output, tmp_path):
        """Test metrics are extracted from raw output."""
        mock_cc.return_value = sample_cc_output
        mock_mi.return_value = sample_mi_output

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert 'metrics' in result
        metrics = result['metrics']
        assert 'total_functions' in metrics
        assert 'average_complexity' in metrics
        assert 'max_complexity' in metrics
        assert 'average_mi' in metrics
        assert 'files_analyzed' in metrics


# ============================================================================
# 4. Violation Conversion Tests (8 tests)
# ============================================================================

class TestViolationConversion:
    """Test conversion of Radon metrics to violations."""

    def test_convert_cc_violations(self, radon_bridge, sample_cc_output):
        """Test cyclomatic complexity violation conversion."""
        raw_output = {
            'cyclomatic_complexity': sample_cc_output,
            'maintainability_index': {}
        }

        violations = radon_bridge.convert_to_violations(raw_output)

        # Should have 2 violations: rank C (medium) and rank F (critical)
        # Rank A (complexity 3) should not create violation
        cc_violations = [v for v in violations if v.type == 'radon_cyclomatic_complexity']
        assert len(cc_violations) == 2

        # Check rank C violation (complexity 15)
        c_violation = [v for v in cc_violations if 'CC=15' in v.description][0]
        assert c_violation.severity == 'medium'
        assert c_violation.line_number == 10
        assert 'complex_function' in c_violation.description

        # Check rank F violation (complexity 55)
        f_violation = [v for v in cc_violations if 'CC=55' in v.description][0]
        assert f_violation.severity == 'critical'
        assert f_violation.line_number == 50
        assert 'very_complex_function' in f_violation.description

    def test_convert_mi_violations(self, radon_bridge, low_mi_output):
        """Test maintainability index violation conversion."""
        raw_output = {
            'cyclomatic_complexity': {},
            'maintainability_index': low_mi_output
        }

        violations = radon_bridge.convert_to_violations(raw_output)

        assert len(violations) == 1
        mi_violation = violations[0]
        assert mi_violation.type == 'radon_maintainability_index'
        assert mi_violation.severity == 'high'  # MI=8.5 is in 0-9 range
        assert 'MI=8.5' in mi_violation.description
        assert mi_violation.line_number == 1  # File-level metric

    def test_convert_no_violations(self, radon_bridge):
        """Test conversion with clean code (no violations)."""
        raw_output = {
            'cyclomatic_complexity': {
                "clean.py": [
                    {"type": "function", "name": "simple", "lineno": 1, "complexity": 2, "rank": "A"}
                ]
            },
            'maintainability_index': {
                "clean.py": {"mi": 85.0, "rank": "A"}
            }
        }

        violations = radon_bridge.convert_to_violations(raw_output)
        assert len(violations) == 0

    def test_convert_empty_output(self, radon_bridge):
        """Test conversion with empty output."""
        raw_output = {
            'cyclomatic_complexity': {},
            'maintainability_index': {}
        }

        violations = radon_bridge.convert_to_violations(raw_output)
        assert len(violations) == 0

    def test_violation_field_mapping(self, radon_bridge):
        """Test that all required fields are mapped correctly."""
        raw_output = {
            'cyclomatic_complexity': {
                "test.py": [
                    {"type": "method", "name": "func", "lineno": 42, "complexity": 25, "rank": "D"}
                ]
            },
            'maintainability_index': {}
        }

        violations = radon_bridge.convert_to_violations(raw_output)
        v = violations[0]

        assert v.type == 'radon_cyclomatic_complexity'
        assert v.severity == 'high'  # Rank D
        assert v.file_path == 'test.py'
        assert v.line_number == 42
        assert v.column == 0
        assert 'func' in v.description
        assert v.recommendation is not None

    def test_cc_recommendations(self, radon_bridge):
        """Test cyclomatic complexity recommendations."""
        test_cases = [
            (55, "F", "Critical"),  # Extreme complexity
            (25, "D", "High complexity"),  # Very high
            (15, "C", "Moderate complexity"),  # High
            (8, "B", "Simplify control flow")  # Medium (but creates violation)
        ]

        for complexity, rank, expected_keyword in test_cases:
            raw_output = {
                'cyclomatic_complexity': {
                    "test.py": [
                        {"type": "function", "name": "f", "lineno": 1, "complexity": complexity, "rank": rank}
                    ]
                },
                'maintainability_index': {}
            }

            violations = radon_bridge.convert_to_violations(raw_output)
            if violations:  # Only check if violation created
                rec = violations[0].recommendation
                assert expected_keyword in rec

    def test_mi_recommendations(self, radon_bridge):
        """Test maintainability index recommendations."""
        test_cases = [
            (5.0, "F", "Critical"),  # Very low MI
            (15.0, "C", "Low maintainability")  # Medium MI
        ]

        for mi_score, rank, expected_keyword in test_cases:
            raw_output = {
                'cyclomatic_complexity': {},
                'maintainability_index': {
                    "test.py": {"mi": mi_score, "rank": rank}
                }
            }

            violations = radon_bridge.convert_to_violations(raw_output)
            if violations:
                rec = violations[0].recommendation
                assert expected_keyword in rec

    def test_combined_cc_and_mi_violations(self, radon_bridge, sample_cc_output, low_mi_output):
        """Test conversion with both CC and MI violations."""
        raw_output = {
            'cyclomatic_complexity': sample_cc_output,
            'maintainability_index': low_mi_output
        }

        violations = radon_bridge.convert_to_violations(raw_output)

        cc_violations = [v for v in violations if v.type == 'radon_cyclomatic_complexity']
        mi_violations = [v for v in violations if v.type == 'radon_maintainability_index']

        assert len(cc_violations) == 2  # Ranks C and F
        assert len(mi_violations) == 1  # Low MI
        assert len(violations) == 3  # Total


# ============================================================================
# 5. Severity Mapping Tests (10 tests)
# ============================================================================

class TestSeverityMapping:
    """Test severity mapping for CC ranks and MI scores."""

    @pytest.mark.parametrize("rank,expected_severity", [
        ('A', None),       # No violation
        ('B', 'low'),      # Medium complexity
        ('C', 'medium'),   # High complexity
        ('D', 'high'),     # Very high complexity
        ('E', 'critical'), # Extreme complexity
        ('F', 'critical')  # Extreme complexity
    ])
    def test_cc_rank_mapping(self, radon_bridge, rank, expected_severity):
        """Test all CC rank mappings."""
        severity = radon_bridge._map_cc_severity(rank)
        assert severity == expected_severity

    @pytest.mark.parametrize("mi_score,expected_severity", [
        (100.0, None),    # Perfect maintainability
        (50.0, None),     # Good maintainability
        (20.0, None),     # Acceptable (threshold)
        (19.9, 'medium'), # Needs work
        (15.0, 'medium'), # Needs work
        (10.0, 'medium'), # Needs work (threshold)
        (9.9, 'high'),    # Unmaintainable
        (5.0, 'high'),    # Very unmaintainable
        (0.0, 'high')     # Worst case
    ])
    def test_mi_score_mapping(self, radon_bridge, mi_score, expected_severity):
        """Test all MI score mappings."""
        severity = radon_bridge._map_mi_severity(mi_score)
        assert severity == expected_severity

    def test_unknown_cc_rank(self, radon_bridge):
        """Test unknown CC rank defaults correctly."""
        severity = radon_bridge._map_cc_severity('Z')  # Invalid rank
        assert severity is None  # Should use default (A equivalent)


# ============================================================================
# 6. Safe Run Wrapper Tests (3 tests)
# ============================================================================

class TestSafeRun:
    """Test safe_run wrapper functionality."""

    @patch.object(RadonBridge, 'is_available')
    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_safe_run_success(self, mock_mi, mock_cc, mock_available, radon_bridge, sample_cc_output, sample_mi_output, tmp_path):
        """Test safe_run with successful execution."""
        mock_available.return_value = True
        mock_cc.return_value = sample_cc_output
        mock_mi.return_value = sample_mi_output

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.safe_run(test_file)

        assert result['success'] is True
        assert 'violations' in result

    @patch.object(RadonBridge, 'is_available')
    def test_safe_run_unavailable(self, mock_available, radon_bridge, tmp_path):
        """Test safe_run when Radon is unavailable."""
        mock_available.return_value = False

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.safe_run(test_file)

        assert result['success'] is False
        assert 'error' in result
        assert 'not available' in result['error']

    @patch.object(RadonBridge, 'is_available')
    @patch.object(RadonBridge, '_run_radon_cc')
    def test_safe_run_exception_handling(self, mock_cc, mock_available, radon_bridge, tmp_path):
        """Test safe_run catches exceptions."""
        mock_available.return_value = True
        mock_cc.side_effect = RuntimeError("Unexpected error")

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = radon_bridge.safe_run(test_file)

        assert result['success'] is False
        assert 'error' in result


# ============================================================================
# 7. Registry Integration Tests (2 tests)
# ============================================================================

class TestRegistryIntegration:
    """Test integration with LinterRegistry."""

    @patch.object(RadonBridge, 'is_available')
    def test_registry_lazy_registration(self, mock_available):
        """Test that Radon bridge registers with registry."""
        from analyzer.linters import linter_registry

        mock_available.return_value = True

        # Force registration
        available = linter_registry.get_available_linters()

        assert 'radon' in linter_registry.linters

    @patch.object(RadonBridge, 'is_available')
    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_registry_run_radon(self, mock_mi, mock_cc, mock_available, sample_cc_output, sample_mi_output, tmp_path):
        """Test running Radon via registry."""
        from analyzer.linters import linter_registry

        mock_available.return_value = True
        mock_cc.return_value = sample_cc_output
        mock_mi.return_value = sample_mi_output

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")

        result = linter_registry.run_linter('radon', test_file)

        assert result['success'] is True
        assert result['linter'] == 'radon'


# ============================================================================
# 8. Edge Cases Tests (5 tests)
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_large_number_of_functions(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test with 100 functions (performance test)."""
        # Generate 100 functions with varying complexity
        functions = [
            {
                "type": "function",
                "name": f"func_{i}",
                "lineno": i * 10,
                "complexity": (i % 60) + 1,  # 1-60 range
                "rank": ["A", "B", "C", "D", "E", "F"][min((i % 60) // 10, 5)]
            }
            for i in range(100)
        ]

        mock_cc.return_value = {"large_file.py": functions}
        mock_mi.return_value = {"large_file.py": {"mi": 50.0, "rank": "B"}}

        test_file = tmp_path / "large.py"
        test_file.write_text("# Large file")

        result = radon_bridge.run(test_file)

        assert result['success'] is True
        assert result['metrics']['total_functions'] == 100

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_unicode_in_function_names(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test handling of unicode characters in function names."""
        mock_cc.return_value = {
            "unicode_file.py": [
                {"type": "function", "name": "函数_test", "lineno": 1, "complexity": 25, "rank": "D"}
            ]
        }
        mock_mi.return_value = {}

        test_file = tmp_path / "unicode.py"
        test_file.write_text("def 函数_test(): pass", encoding='utf-8')

        result = radon_bridge.run(test_file)

        assert result['success'] is True
        violations = result['violations']
        assert len(violations) == 1
        assert '函数_test' in violations[0].description

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_very_long_file_path(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test handling of very long file paths."""
        long_name = "a" * 200 + ".py"
        mock_cc.return_value = {}
        mock_mi.return_value = {}

        test_file = tmp_path / long_name
        test_file.write_text("def foo(): pass")

        result = radon_bridge.run(test_file)

        assert result['success'] is True

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_empty_file(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test handling of empty Python file."""
        mock_cc.return_value = {}
        mock_mi.return_value = {}

        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = radon_bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 0

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_metrics_calculation_edge_cases(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test metrics calculation with edge cases."""
        # Test with zero functions
        mock_cc.return_value = {}
        mock_mi.return_value = {}

        test_file = tmp_path / "test.py"
        test_file.write_text("# No functions")

        result = radon_bridge.run(test_file)

        metrics = result['metrics']
        assert metrics['total_functions'] == 0
        assert metrics['average_complexity'] == 0.0
        assert metrics['max_complexity'] == 0


# ============================================================================
# 9. Real-World Scenario Tests (2 tests)
# ============================================================================

class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_typical_project_file(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test analysis of typical project file."""
        # Realistic mix: some clean functions, some complex ones
        mock_cc.return_value = {
            "project_file.py": [
                {"type": "function", "name": "simple_getter", "lineno": 5, "complexity": 1, "rank": "A"},
                {"type": "function", "name": "simple_setter", "lineno": 10, "complexity": 2, "rank": "A"},
                {"type": "method", "name": "validate_input", "lineno": 20, "complexity": 12, "rank": "C"},
                {"type": "method", "name": "process_data", "lineno": 50, "complexity": 8, "rank": "B"},
                {"type": "function", "name": "legacy_monster", "lineno": 100, "complexity": 45, "rank": "E"}
            ]
        }
        mock_mi.return_value = {
            "project_file.py": {"mi": 55.2, "rank": "B"}
        }

        test_file = tmp_path / "project.py"
        test_file.write_text("# Typical project file")

        result = radon_bridge.run(test_file)

        assert result['success'] is True

        # Should have violations for ranks B, C, E (not A)
        violations = result['violations']
        cc_violations = [v for v in violations if v.type == 'radon_cyclomatic_complexity']
        assert len(cc_violations) == 3  # B, C, E

        # Check metrics
        metrics = result['metrics']
        assert metrics['total_functions'] == 5
        assert metrics['average_complexity'] > 0
        assert metrics['max_complexity'] == 45

    @patch.object(RadonBridge, '_run_radon_cc')
    @patch.object(RadonBridge, '_run_radon_mi')
    def test_legacy_code_analysis(self, mock_mi, mock_cc, radon_bridge, tmp_path):
        """Test analysis of legacy code with many issues."""
        # Simulate legacy code: high complexity, low maintainability
        mock_cc.return_value = {
            "legacy.py": [
                {"type": "method", "name": "god_method_1", "lineno": 10, "complexity": 75, "rank": "F"},
                {"type": "method", "name": "god_method_2", "lineno": 200, "complexity": 82, "rank": "F"},
                {"type": "function", "name": "complex_logic", "lineno": 400, "complexity": 35, "rank": "D"}
            ]
        }
        mock_mi.return_value = {
            "legacy.py": {"mi": 6.2, "rank": "F"}
        }

        test_file = tmp_path / "legacy.py"
        test_file.write_text("# Legacy code")

        result = radon_bridge.run(test_file)

        assert result['success'] is True

        # Should have many violations
        violations = result['violations']
        cc_violations = [v for v in violations if v.type == 'radon_cyclomatic_complexity']
        mi_violations = [v for v in violations if v.type == 'radon_maintainability_index']

        assert len(cc_violations) == 3  # All functions have issues
        assert len(mi_violations) == 1  # Low MI
        assert len(violations) == 4  # Total

        # All CC violations should be high or critical
        for v in cc_violations:
            assert v.severity in ['high', 'critical']

        # MI violation should be high (MI < 10)
        assert mi_violations[0].severity == 'high'
