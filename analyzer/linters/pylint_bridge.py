"""
Pylint Bridge - Integration with Pylint linter

This module provides integration between the SPEK analyzer and Pylint,
a comprehensive Python static analysis tool that checks for errors,
enforces coding standards, and detects code smells.

Pylint Message Types:
- fatal (F): Critical errors that prevent analysis
- error (E): Definite problems
- warning (W): Stylistic problems, minor issues
- refactor (R): Code quality improvements
- convention (C): Coding standard violations
- info (I): Informational messages

Severity Mapping:
- fatal → critical
- error → high
- warning → medium
- refactor → low
- convention → low
- info → info

NASA Rule 3 Compliance: ≤60 LOC per function
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import logging

from .base_linter import LinterBridge
from analyzer.utils.types import ConnascenceViolation

logger = logging.getLogger(__name__)


class PylintBridge(LinterBridge):
    """
    Pylint integration bridge.

    Executes Pylint on Python files and converts results to
    ConnascenceViolation format for unified reporting.
    """

    # Severity mapping from Pylint message types to our levels
    SEVERITY_MAP = {
        'fatal': 'critical',
        'error': 'high',
        'warning': 'medium',
        'refactor': 'low',
        'convention': 'low',
        'info': 'low'  # Map info to low (ConnascenceViolation accepts: critical, high, medium, low)
    }

    def __init__(self, timeout: int = 60):
        """
        Initialize Pylint bridge.

        Args:
            timeout: Maximum execution time in seconds

        NASA Rule 4: Assertions for input validation
        """
        super().__init__(timeout)
        logger.debug("PylintBridge initialized")

    def is_available(self) -> bool:
        """
        Check if Pylint is installed and available.

        Returns:
            True if pylint command can be executed, False otherwise

        This method tries to run 'pylint --version' to verify installation.
        If the command succeeds, Pylint is available.

        NASA Rule 3: ≤60 LOC
        """
        try:
            # Use 'python -m pylint' for cross-platform compatibility
            import sys
            result = subprocess.run(
                [sys.executable, '-m', 'pylint', '--version'],
                capture_output=True,
                timeout=5,
                text=True
            )
            available = result.returncode == 0
            logger.debug(f"Pylint availability: {available}")
            return available

        except FileNotFoundError:
            logger.debug("Python executable not found (shouldn't happen)")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("Pylint version check timed out")
            return False
        except Exception as e:
            logger.warning(f"Pylint availability check failed: {e}")
            return False

    def run(self, file_path: Path) -> Dict[str, Any]:
        """
        Run Pylint on a file and return structured results.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Dictionary with keys:
            - 'success': bool
            - 'violations': List[ConnascenceViolation]
            - 'raw_output': List[Dict] (JSON from pylint)
            - 'execution_time': float
            - 'linter': str ('pylint')

        NASA Rule 4: Assertions for input validation
        """
        assert file_path.exists(), f"File not found: {file_path}"
        assert file_path.suffix == '.py', f"Not a Python file: {file_path}"

        start_time = time.time()
        logger.info(f"Running Pylint on {file_path.name}")

        try:
            # Run pylint with JSON output format using 'python -m pylint'
            import sys
            result = subprocess.run(
                [sys.executable, '-m', 'pylint', str(file_path), '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            execution_time = time.time() - start_time

            # Parse JSON output
            # Note: Pylint returns non-zero if violations found
            # so we don't check returncode for success
            try:
                raw_output = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Pylint JSON: {e}")
                return self._error_result(f"JSON parse error: {e}")

            # Convert to violations
            violations = self.convert_to_violations(raw_output)

            logger.info(
                f"Pylint found {len(violations)} violations "
                f"in {execution_time:.2f}s"
            )

            return {
                'success': True,
                'violations': violations,
                'raw_output': raw_output,
                'execution_time': execution_time,
                'linter': 'pylint'
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Pylint timed out after {execution_time:.1f}s")
            return self._error_result(
                f"Timeout after {self.timeout}s"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Pylint execution failed: {e}")
            return self._error_result(str(e))

    def convert_to_violations(
        self,
        raw_output: List[Dict[str, Any]]
    ) -> List[ConnascenceViolation]:
        """
        Convert Pylint messages to ConnascenceViolation format.

        Args:
            raw_output: List of Pylint message dictionaries

        Returns:
            List of ConnascenceViolation objects

        Pylint message format:
        {
            'type': 'error',  # or 'warning', 'convention', etc.
            'module': 'mymodule',
            'obj': 'MyClass.my_method',
            'line': 42,
            'column': 0,
            'endLine': 42,
            'endColumn': 10,
            'path': '/path/to/file.py',
            'symbol': 'undefined-variable',
            'message': 'Undefined variable "foo"',
            'message-id': 'E0602'
        }

        NASA Rule 3: ≤60 LOC
        """
        assert isinstance(raw_output, list), "raw_output must be list"

        violations = []

        for msg in raw_output:
            try:
                # Map Pylint severity to our severity levels
                pylint_type = msg.get('type', 'warning')
                severity = self.SEVERITY_MAP.get(pylint_type, 'medium')

                # Create violation
                violation = ConnascenceViolation(
                    type=f"pylint_{msg.get('message-id', 'unknown')}",
                    severity=severity,
                    description=f"{msg.get('message', 'Unknown issue')} ({msg.get('symbol', 'unknown')})",
                    file_path=msg.get('path', 'unknown'),
                    line_number=msg.get('line', 0),
                    column=msg.get('column', 0),
                    recommendation=f"Pylint {msg.get('message-id', '')}: {msg.get('message', '')}",
                    rule_id=msg.get('message-id'),
                    function_name=msg.get('obj', None),
                    module_name=msg.get('module', None)
                )

                violations.append(violation)

            except Exception as e:
                logger.warning(f"Failed to convert Pylint message: {e}")
                continue

        logger.debug(f"Converted {len(violations)} Pylint messages")
        return violations


__all__ = ['PylintBridge']
