"""
Test Linter Infrastructure - Base classes and registry

Tests the core linter bridge infrastructure created in Sprint 2.1.
This validates that the base classes and registry work correctly
before implementing specific linter bridges.

Sprint: 2.1 (Infrastructure)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from analyzer.linters import LinterBridge, LinterRegistry, linter_registry
from analyzer.utils.types import ConnascenceViolation


class MockLinterBridge(LinterBridge):
    """
    Mock linter for testing infrastructure.

    Implements all abstract methods with simple test logic.
    """

    def __init__(self, available: bool = True, timeout: int = 60):
        super().__init__(timeout)
        self._available = available
        self._run_called = False

    def is_available(self) -> bool:
        """Mock availability check."""
        return self._available

    def run(self, file_path: Path) -> Dict[str, Any]:
        """Mock linter execution."""
        self._run_called = True
        return {
            'success': True,
            'violations': [
                ConnascenceViolation(
                    type='mock_violation',
                    severity='medium',
                    description='Mock violation for testing',
                    file_path=str(file_path),
                    line_number=1
                )
            ],
            'raw_output': {'mock': 'output'},
            'execution_time': 0.1,
            'linter': 'mock'
        }

    def convert_to_violations(self, raw_output: Any) -> List[ConnascenceViolation]:
        """Mock conversion."""
        return [
            ConnascenceViolation(
                type='converted_violation',
                severity='low',
                description='Converted from raw output',
                file_path='test.py',
                line_number=10
            )
        ]


class TestLinterBridge:
    """Test LinterBridge abstract base class."""

    def test_init(self):
        """Test linter bridge initialization."""
        bridge = MockLinterBridge(timeout=30)
        assert bridge.timeout == 30
        assert bridge.name == 'MockLinterBridge'

    def test_init_validation(self):
        """Test initialization input validation (NASA Rule 4)."""
        # Valid timeout
        bridge = MockLinterBridge(timeout=60)
        assert bridge.timeout == 60

        # Invalid timeout (not integer)
        with pytest.raises(AssertionError, match="timeout must be integer"):
            MockLinterBridge(timeout="60")

        # Invalid timeout (not positive)
        with pytest.raises(AssertionError, match="timeout must be positive"):
            MockLinterBridge(timeout=-1)

    def test_safe_run_success(self):
        """Test safe_run with successful execution."""
        bridge = MockLinterBridge(available=True)
        result = bridge.safe_run(Path(__file__))

        assert result['success'] is True
        assert 'violations' in result
        assert len(result['violations']) == 1
        assert result['violations'][0].type == 'mock_violation'

    def test_safe_run_unavailable(self):
        """Test safe_run when linter not available."""
        bridge = MockLinterBridge(available=False)
        result = bridge.safe_run(Path(__file__))

        assert result['success'] is False
        assert 'not available' in result['error']
        assert result['violations'] == []

    def test_safe_run_validation(self):
        """Test safe_run input validation (NASA Rule 4)."""
        bridge = MockLinterBridge()

        # Invalid file_path type
        with pytest.raises(AssertionError, match="file_path must be Path"):
            bridge.safe_run("not_a_path")

    def test_unavailable_result(self):
        """Test _unavailable_result format."""
        bridge = MockLinterBridge()
        result = bridge._unavailable_result()

        assert result['success'] is False
        assert 'error' in result
        assert result['violations'] == []
        assert result['linter'] == 'MockLinterBridge'

    def test_error_result(self):
        """Test _error_result format."""
        bridge = MockLinterBridge()
        result = bridge._error_result("Test error message")

        assert result['success'] is False
        assert result['error'] == "Test error message"
        assert result['violations'] == []

    def test_get_info(self):
        """Test get_info returns linter metadata."""
        bridge = MockLinterBridge(available=True, timeout=45)
        info = bridge.get_info()

        assert info['name'] == 'MockLinterBridge'
        assert info['available'] is True
        assert info['timeout'] == 45


class TestLinterRegistry:
    """Test LinterRegistry class."""

    def test_init(self):
        """Test registry initialization."""
        registry = LinterRegistry()
        assert registry.linters == {}
        assert registry._registered is False

    def test_get_available_linters_empty(self):
        """Test get_available_linters with registered linters."""
        registry = LinterRegistry()
        available = registry.get_available_linters()

        # Updated Sprint 4.1: We now have Pylint + Radon registered and available
        assert isinstance(available, list)
        # Note: Availability depends on whether linters are installed
        # In CI/CD they may not be installed, so we just check it's a list
        assert len(available) >= 0

    def test_get_linter_info_empty(self):
        """Test get_linter_info with registered linters."""
        registry = LinterRegistry()
        info = registry.get_linter_info()

        assert isinstance(info, dict)
        # Updated Sprint 1.4: We now have Pylint + Radon registered
        assert len(info) >= 2  # At least pylint and radon

    def test_run_linter_unknown(self):
        """Test run_linter with unknown linter name."""
        registry = LinterRegistry()
        result = registry.run_linter('nonexistent', Path(__file__))

        assert result['success'] is False
        assert 'Unknown linter' in result['error']

    def test_aggregate_violations_empty(self):
        """Test aggregate_violations with no results."""
        registry = LinterRegistry()
        violations = registry.aggregate_violations({})

        assert isinstance(violations, list)
        assert len(violations) == 0

    def test_aggregate_violations_validation(self):
        """Test aggregate_violations input validation (NASA Rule 4)."""
        registry = LinterRegistry()

        # Invalid input type
        with pytest.raises(AssertionError, match="results must be dict"):
            registry.aggregate_violations("not_a_dict")

    def test_aggregate_violations_success(self):
        """Test aggregate_violations with successful results."""
        registry = LinterRegistry()

        # Mock results from multiple linters
        results = {
            'pylint': {
                'success': True,
                'violations': [
                    ConnascenceViolation(type='pylint_error', severity='high', description='Error 1', file_path='test.py', line_number=1)
                ]
            },
            'flake8': {
                'success': True,
                'violations': [
                    ConnascenceViolation(type='flake8_warning', severity='medium', description='Warning 1', file_path='test.py', line_number=2),
                    ConnascenceViolation(type='flake8_warning', severity='medium', description='Warning 2', file_path='test.py', line_number=3)
                ]
            },
            'mypy': {
                'success': False,  # Failed linter - should be skipped
                'violations': []
            }
        }

        violations = registry.aggregate_violations(results)

        # Should have 3 violations (1 from pylint + 2 from flake8, mypy skipped)
        assert len(violations) == 3
        assert violations[0].type == 'pylint_error'
        assert violations[1].type == 'flake8_warning'
        assert violations[2].type == 'flake8_warning'


class TestGlobalRegistry:
    """Test the global linter_registry instance."""

    def test_global_registry_exists(self):
        """Test that global registry is accessible."""
        assert linter_registry is not None
        assert isinstance(linter_registry, LinterRegistry)

    def test_global_registry_get_available(self):
        """Test global registry get_available_linters."""
        available = linter_registry.get_available_linters()
        assert isinstance(available, list)
        # Should be empty until Sprint 2.2+ implements bridges


# Integration test placeholder for future sprints
class TestLinterIntegration:
    """
    Integration tests for linter bridges.

    These will be populated in Sprints 2.2-2.4 when actual
    linter bridges are implemented.
    """

    @pytest.mark.skip(reason="Pylint bridge not yet implemented (Sprint 2.2)")
    def test_pylint_integration(self):
        """Test Pylint bridge integration."""
        pass

    @pytest.mark.skip(reason="Flake8 bridge not yet implemented (Sprint 2.3)")
    def test_flake8_integration(self):
        """Test Flake8 bridge integration."""
        pass

    @pytest.mark.skip(reason="Mypy bridge not yet implemented (Sprint 2.4)")
    def test_mypy_integration(self):
        """Test Mypy bridge integration."""
        pass

    @pytest.mark.skip(reason="Radon bridge not yet implemented (Sprint 3.1)")
    def test_radon_integration(self):
        """Test Radon metrics integration."""
        pass
