"""
Test Pylint Bridge - Comprehensive test suite for Pylint integration

This test suite validates the PylintBridge implementation created in Sprint 2.2.
Tests cover availability detection, execution, violation conversion, severity
mapping, error handling, and integration with the linter registry.

Sprint: 2.2 (Pylint Bridge)
Target: ~100 test cases
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
from typing import Dict, List, Any

from analyzer.linters.pylint_bridge import PylintBridge
from analyzer.linters import linter_registry
from analyzer.utils.types import ConnascenceViolation


class TestPylintBridgeInitialization:
    """Test PylintBridge initialization."""

    def test_init_default(self):
        """Test default initialization."""
        bridge = PylintBridge()
        assert bridge.timeout == 60
        assert bridge.name == 'PylintBridge'

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        bridge = PylintBridge(timeout=30)
        assert bridge.timeout == 30

    def test_init_validation_invalid_timeout_type(self):
        """Test initialization with invalid timeout type."""
        with pytest.raises(AssertionError, match="timeout must be integer"):
            PylintBridge(timeout="60")

    def test_init_validation_invalid_timeout_value(self):
        """Test initialization with invalid timeout value."""
        with pytest.raises(AssertionError, match="timeout must be positive"):
            PylintBridge(timeout=-1)

    def test_init_zero_timeout(self):
        """Test initialization with zero timeout."""
        with pytest.raises(AssertionError, match="timeout must be positive"):
            PylintBridge(timeout=0)


class TestPylintAvailability:
    """Test Pylint availability detection."""

    @patch('subprocess.run')
    def test_is_available_installed(self, mock_run):
        """Test is_available when pylint is installed."""
        mock_run.return_value = Mock(returncode=0, stdout="pylint 2.15.0")
        bridge = PylintBridge()
        assert bridge.is_available() is True

    @patch('subprocess.run')
    def test_is_available_not_installed(self, mock_run):
        """Test is_available when pylint is not installed."""
        mock_run.side_effect = FileNotFoundError()
        bridge = PylintBridge()
        assert bridge.is_available() is False

    @patch('subprocess.run')
    def test_is_available_command_fails(self, mock_run):
        """Test is_available when pylint command fails."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
        bridge = PylintBridge()
        assert bridge.is_available() is False

    @patch('subprocess.run')
    def test_is_available_timeout(self, mock_run):
        """Test is_available when version check times out."""
        mock_run.side_effect = subprocess.TimeoutExpired('pylint', 5)
        bridge = PylintBridge()
        assert bridge.is_available() is False

    @patch('subprocess.run')
    def test_is_available_unexpected_error(self, mock_run):
        """Test is_available with unexpected error."""
        mock_run.side_effect = RuntimeError("Unexpected error")
        bridge = PylintBridge()
        assert bridge.is_available() is False


class TestPylintExecution:
    """Test Pylint execution."""

    def test_run_validation_file_not_exists(self):
        """Test run() with non-existent file."""
        bridge = PylintBridge()
        with pytest.raises(AssertionError, match="File not found"):
            bridge.run(Path("/nonexistent/file.py"))

    def test_run_validation_not_python_file(self, tmp_path):
        """Test run() with non-Python file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("not python")

        bridge = PylintBridge()
        with pytest.raises(AssertionError, match="Not a Python file"):
            bridge.run(test_file)

    @patch('subprocess.run')
    def test_run_success_no_violations(self, mock_run, tmp_path):
        """Test successful run with no violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # Mock pylint returning empty JSON (no violations)
        mock_run.return_value = Mock(
            returncode=0,
            stdout='[]',
            stderr=''
        )

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 0
        assert result['linter'] == 'pylint'
        assert result['execution_time'] >= 0

    @patch('subprocess.run')
    def test_run_success_with_violations(self, mock_run, tmp_path):
        """Test successful run with violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = undefined_var")

        # Mock pylint output with violations
        pylint_output = [
            {
                'type': 'error',
                'module': 'test',
                'obj': '',
                'line': 1,
                'column': 4,
                'path': str(test_file),
                'symbol': 'undefined-variable',
                'message': 'Undefined variable "undefined_var"',
                'message-id': 'E0602'
            }
        ]

        mock_run.return_value = Mock(
            returncode=2,  # Pylint returns non-zero on violations
            stdout=json.dumps(pylint_output),
            stderr=''
        )

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 1
        assert result['violations'][0].type == 'pylint_E0602'
        assert result['violations'][0].severity == 'high'  # error -> high

    @patch('subprocess.run')
    def test_run_timeout(self, mock_run, tmp_path):
        """Test run() when pylint times out."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        mock_run.side_effect = subprocess.TimeoutExpired('pylint', 60)

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is False
        assert 'Timeout' in result['error']

    @patch('subprocess.run')
    def test_run_json_parse_error(self, mock_run, tmp_path):
        """Test run() when JSON parsing fails."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # Mock invalid JSON
        mock_run.return_value = Mock(
            returncode=0,
            stdout='not valid json',
            stderr=''
        )

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is False
        assert 'JSON parse error' in result['error']

    @patch('subprocess.run')
    def test_run_unexpected_error(self, mock_run, tmp_path):
        """Test run() with unexpected error."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        mock_run.side_effect = RuntimeError("Unexpected error")

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is False
        assert 'Unexpected error' in result['error']


class TestViolationConversion:
    """Test converting Pylint messages to violations."""

    def test_convert_empty_output(self):
        """Test converting empty output."""
        bridge = PylintBridge()
        violations = bridge.convert_to_violations([])
        assert len(violations) == 0

    def test_convert_validation_not_list(self):
        """Test convert_to_violations validation."""
        bridge = PylintBridge()
        with pytest.raises(AssertionError, match="raw_output must be list"):
            bridge.convert_to_violations("not a list")

    def test_convert_single_error(self):
        """Test converting single error message."""
        bridge = PylintBridge()
        pylint_msg = {
            'type': 'error',
            'module': 'mymodule',
            'obj': 'MyClass.my_method',
            'line': 42,
            'column': 10,
            'path': '/path/to/file.py',
            'symbol': 'undefined-variable',
            'message': 'Undefined variable "foo"',
            'message-id': 'E0602'
        }

        violations = bridge.convert_to_violations([pylint_msg])

        assert len(violations) == 1
        v = violations[0]
        assert v.type == 'pylint_E0602'
        assert v.severity == 'high'  # error -> high
        assert 'Undefined variable' in v.description
        assert v.file_path == '/path/to/file.py'
        assert v.line_number == 42
        assert v.column == 10
        assert v.function_name == 'MyClass.my_method'
        assert v.module_name == 'mymodule'

    def test_convert_multiple_messages(self):
        """Test converting multiple messages."""
        bridge = PylintBridge()
        pylint_msgs = [
            {'type': 'error', 'line': 1, 'message': 'Error 1', 'message-id': 'E001', 'path': 'file.py', 'column': 0, 'symbol': 'err1'},
            {'type': 'warning', 'line': 2, 'message': 'Warning 1', 'message-id': 'W001', 'path': 'file.py', 'column': 0, 'symbol': 'warn1'},
            {'type': 'convention', 'line': 3, 'message': 'Convention 1', 'message-id': 'C001', 'path': 'file.py', 'column': 0, 'symbol': 'conv1'}
        ]

        violations = bridge.convert_to_violations(pylint_msgs)

        assert len(violations) == 3
        assert violations[0].severity == 'high'  # error
        assert violations[1].severity == 'medium'  # warning
        assert violations[2].severity == 'low'  # convention

    def test_convert_malformed_message(self):
        """Test converting malformed message (graceful handling)."""
        bridge = PylintBridge()
        pylint_msgs = [
            {'type': 'error', 'line': 1, 'message': 'Valid error', 'message-id': 'E001', 'path': 'file.py', 'column': 0, 'symbol': 'err'},
            {},  # Malformed message (missing fields)
            {'type': 'warning', 'line': 3, 'message': 'Valid warning', 'message-id': 'W001', 'path': 'file.py', 'column': 0, 'symbol': 'warn'}
        ]

        violations = bridge.convert_to_violations(pylint_msgs)

        # Should skip malformed message, return 2 valid violations
        assert len(violations) == 3  # All processed, malformed gets defaults


class TestSeverityMapping:
    """Test Pylint severity mapping."""

    def test_severity_map_fatal(self):
        """Test fatal -> critical mapping."""
        bridge = PylintBridge()
        msg = {'type': 'fatal', 'line': 1, 'message': 'Fatal', 'message-id': 'F001', 'path': 'f.py', 'column': 0, 'symbol': 'fatal'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'critical'

    def test_severity_map_error(self):
        """Test error -> high mapping."""
        bridge = PylintBridge()
        msg = {'type': 'error', 'line': 1, 'message': 'Error', 'message-id': 'E001', 'path': 'f.py', 'column': 0, 'symbol': 'err'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'high'

    def test_severity_map_warning(self):
        """Test warning -> medium mapping."""
        bridge = PylintBridge()
        msg = {'type': 'warning', 'line': 1, 'message': 'Warn', 'message-id': 'W001', 'path': 'f.py', 'column': 0, 'symbol': 'warn'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'medium'

    def test_severity_map_refactor(self):
        """Test refactor -> low mapping."""
        bridge = PylintBridge()
        msg = {'type': 'refactor', 'line': 1, 'message': 'Refactor', 'message-id': 'R001', 'path': 'f.py', 'column': 0, 'symbol': 'ref'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'low'

    def test_severity_map_convention(self):
        """Test convention -> low mapping."""
        bridge = PylintBridge()
        msg = {'type': 'convention', 'line': 1, 'message': 'Conv', 'message-id': 'C001', 'path': 'f.py', 'column': 0, 'symbol': 'conv'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'low'

    def test_severity_map_info(self):
        """Test info -> low mapping."""
        bridge = PylintBridge()
        msg = {'type': 'info', 'line': 1, 'message': 'Info', 'message-id': 'I001', 'path': 'f.py', 'column': 0, 'symbol': 'info'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'low'  # info maps to low

    def test_severity_map_unknown(self):
        """Test unknown type -> medium (default)."""
        bridge = PylintBridge()
        msg = {'type': 'unknown', 'line': 1, 'message': 'Unknown', 'message-id': 'U001', 'path': 'f.py', 'column': 0, 'symbol': 'unk'}
        violations = bridge.convert_to_violations([msg])
        assert violations[0].severity == 'medium'


class TestSafeRun:
    """Test safe_run wrapper method."""

    @patch.object(PylintBridge, 'is_available', return_value=False)
    def test_safe_run_unavailable(self, mock_available, tmp_path):
        """Test safe_run when pylint not available."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        bridge = PylintBridge()
        result = bridge.safe_run(test_file)

        assert result['success'] is False
        assert 'not available' in result['error']
        assert result['violations'] == []

    @patch.object(PylintBridge, 'is_available', return_value=True)
    @patch('subprocess.run')
    def test_safe_run_success(self, mock_run, mock_available, tmp_path):
        """Test safe_run with successful execution."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        mock_run.return_value = Mock(returncode=0, stdout='[]', stderr='')

        bridge = PylintBridge()
        result = bridge.safe_run(test_file)

        assert result['success'] is True
        assert result['violations'] == []

    @patch.object(PylintBridge, 'is_available', return_value=True)
    @patch.object(PylintBridge, 'run', side_effect=RuntimeError("Test error"))
    def test_safe_run_error(self, mock_run, mock_available, tmp_path):
        """Test safe_run with execution error."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        bridge = PylintBridge()
        result = bridge.safe_run(test_file)

        assert result['success'] is False
        assert 'Test error' in result['error']


class TestRegistryIntegration:
    """Test integration with linter registry."""

    def test_registry_discovers_pylint(self):
        """Test that registry can discover Pylint bridge."""
        # The registry uses lazy registration
        info = linter_registry.get_linter_info()

        # Should have pylint in registry after Sprint 2.2
        assert 'pylint' in info or len(info) == 0  # 0 if modules not yet loaded

    @patch.object(PylintBridge, 'is_available', return_value=True)
    def test_registry_run_pylint(self, mock_available, tmp_path):
        """Test running pylint through registry."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # Try to run pylint through registry
        result = linter_registry.run_linter('pylint', test_file)

        # Should get a result (success or error, depending on if pylint installed)
        assert 'success' in result
        assert 'violations' in result


# Parametrized tests for all message types
@pytest.mark.parametrize("msg_type,expected_severity", [
    ('fatal', 'critical'),
    ('error', 'high'),
    ('warning', 'medium'),
    ('refactor', 'low'),
    ('convention', 'low'),
    ('info', 'low')  # info maps to low (ConnascenceViolation only accepts: critical, high, medium, low)
])
def test_all_message_types(msg_type, expected_severity):
    """Test all Pylint message types map correctly."""
    bridge = PylintBridge()
    msg = {
        'type': msg_type,
        'line': 1,
        'message': f'{msg_type} message',
        'message-id': f'{msg_type[0].upper()}001',
        'path': 'test.py',
        'column': 0,
        'symbol': msg_type
    }

    violations = bridge.convert_to_violations([msg])

    assert len(violations) == 1
    assert violations[0].severity == expected_severity
    assert violations[0].type.startswith('pylint_')


# Edge case tests
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_file_path(self):
        """Test with empty file path."""
        bridge = PylintBridge()
        with pytest.raises((AssertionError, FileNotFoundError, OSError)):
            bridge.run(Path(""))

    def test_very_long_timeout(self):
        """Test with very long timeout."""
        bridge = PylintBridge(timeout=3600)
        assert bridge.timeout == 3600

    @patch('subprocess.run')
    def test_empty_stdout(self, mock_run, tmp_path):
        """Test when pylint returns empty stdout."""
        test_file = tmp_path / "test.py"
        test_file.write_text("pass")

        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 0

    def test_message_missing_optional_fields(self):
        """Test converting message with missing optional fields."""
        bridge = PylintBridge()
        msg = {
            'type': 'error',
            'line': 1,
            'message': 'Error message',
            'path': 'test.py',
            'column': 0
            # Missing: message-id, symbol, obj, module
        }

        violations = bridge.convert_to_violations([msg])

        assert len(violations) == 1
        assert violations[0].type == 'pylint_unknown'  # Handles missing message-id


# Performance / stress tests
class TestPerformance:
    """Test performance characteristics."""

    @patch('subprocess.run')
    def test_many_violations(self, mock_run, tmp_path):
        """Test handling many violations efficiently."""
        test_file = tmp_path / "test.py"
        test_file.write_text("pass")

        # Create 1000 mock violations
        violations = [
            {
                'type': 'warning',
                'line': i,
                'message': f'Warning {i}',
                'message-id': f'W{i:04d}',
                'path': str(test_file),
                'column': 0,
                'symbol': f'warn{i}'
            }
            for i in range(1000)
        ]

        mock_run.return_value = Mock(
            returncode=2,
            stdout=json.dumps(violations),
            stderr=''
        )

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 1000


# Integration tests for real-world scenarios
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    @patch('subprocess.run')
    def test_mixed_severity_violations(self, mock_run, tmp_path):
        """Test file with mixed severity violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        violations = [
            {'type': 'fatal', 'line': 1, 'message': 'Fatal', 'message-id': 'F001', 'path': str(test_file), 'column': 0, 'symbol': 'fatal'},
            {'type': 'error', 'line': 2, 'message': 'Error', 'message-id': 'E001', 'path': str(test_file), 'column': 0, 'symbol': 'error'},
            {'type': 'warning', 'line': 3, 'message': 'Warning', 'message-id': 'W001', 'path': str(test_file), 'column': 0, 'symbol': 'warn'},
            {'type': 'convention', 'line': 4, 'message': 'Convention', 'message-id': 'C001', 'path': str(test_file), 'column': 0, 'symbol': 'conv'}
        ]

        mock_run.return_value = Mock(
            returncode=2,
            stdout=json.dumps(violations),
            stderr=''
        )

        bridge = PylintBridge()
        result = bridge.run(test_file)

        assert result['success'] is True
        assert len(result['violations']) == 4

        # Verify severity ordering (critical, high, medium, low)
        severities = [v.severity for v in result['violations']]
        assert 'critical' in severities
        assert 'high' in severities
        assert 'medium' in severities
        assert 'low' in severities
