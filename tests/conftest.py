"""
Pytest Configuration and Shared Fixtures

Provides shared fixtures for all tests including:
- Sample code files (god functions, theater code, etc.)
- Mock analyzers and engines
- Temporary directories
- Test data builders

Version: 6.0.0 (Week 2 Day 3-5)
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any


# Sample code fixtures for testing
@pytest.fixture
def sample_python_god_function():
    """Sample Python code with god function (>60 LOC)."""
    return '''
def god_function(param1, param2, param3, param4, param5, param6, param7):
    """This function violates NASA Rule 3 (>60 LOC) and Rule 6 (>6 params)."""
    result = 0
    # Line 5
    for i in range(100):
        result += i
    # Line 8
    if param1:
        result *= 2
    # Line 11
    if param2:
        result *= 3
    # Line 14
    if param3:
        result *= 4
    # Line 17
    if param4:
        result *= 5
    # Line 20
    if param5:
        result *= 6
    # Line 23
    if param6:
        result *= 7
    # Line 26
    if param7:
        result *= 8
    # Lines 29-70 to exceed 60 LOC limit
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = 5
    x6 = 6
    x7 = 7
    x8 = 8
    x9 = 9
    x10 = 10
    x11 = 11
    x12 = 12
    x13 = 13
    x14 = 14
    x15 = 15
    x16 = 16
    x17 = 17
    x18 = 18
    x19 = 19
    x20 = 20
    x21 = 21
    x22 = 22
    x23 = 23
    x24 = 24
    x25 = 25
    x26 = 26
    x27 = 27
    x28 = 28
    x29 = 29
    x30 = 30
    x31 = 31
    x32 = 32
    return result
'''


@pytest.fixture
def sample_python_theater_code():
    """Sample Python code with theater violations."""
    return '''
def not_implemented_function():
    """This is theater code - raises NotImplementedError."""
    raise NotImplementedError("This should be implemented")

def fake_analysis():
    # TODO: Implement real analysis
    return {"status": "success", "theater": True}
'''


@pytest.fixture
def sample_python_security_risks():
    """Sample Python code with security vulnerabilities."""
    return '''
import os

def dangerous_eval(user_input):
    """Security risk - uses eval()."""
    return eval(user_input)

def dangerous_exec(code):
    """Security risk - uses exec()."""
    exec(code)

def wildcard_import():
    """Code quality issue - wildcard import."""
    from os import *
    return listdir('.')
'''


@pytest.fixture
def sample_python_magic_literals():
    """Sample Python code with magic literals."""
    return '''
def calculate_price(quantity):
    """Contains magic literals."""
    base_price = 19.99  # Magic literal
    tax_rate = 0.085    # Magic literal
    discount_threshold = 100  # Magic literal

    total = quantity * base_price
    if quantity > discount_threshold:
        total *= 0.9  # Magic literal

    tax = total * tax_rate
    return total + tax
'''


@pytest.fixture
def sample_python_god_class():
    """Sample Python code with god class (>50 methods)."""
    methods = '\n'.join([
        f'    def method_{i}(self):\n        """Method {i}"""\n        return {i}'
        for i in range(60)
    ])

    return f'''
class GodClass:
    """This class violates god object pattern (>50 methods)."""
{methods}
'''


@pytest.fixture
def sample_python_clean_code():
    """Sample clean Python code with no violations."""
    return '''
def calculate_sum(numbers):
    """Calculate sum of numbers - clean implementation."""
    assert numbers, "numbers cannot be empty"
    assert isinstance(numbers, list), "numbers must be a list"

    total = sum(numbers)
    return total

def format_output(value):
    """Format output string."""
    assert value is not None, "value cannot be None"
    return f"Result: {value}"
'''


@pytest.fixture
def sample_javascript_theater():
    """Sample JavaScript code with theater violations."""
    return '''
function notImplemented() {
    throw new Error("Not implemented");
}

function fakeValidation() {
    // TODO: Implement real validation
    return true;
}
'''


@pytest.fixture
def sample_c_unsafe_functions():
    """Sample C code with unsafe functions."""
    return '''
#include <string.h>
#include <stdio.h>

void unsafe_copy(char *dest, char *src) {
    strcpy(dest, src);  // Buffer overflow risk
}

void unsafe_format(char *buffer, char *input) {
    sprintf(buffer, "Input: %s", input);  // Buffer overflow risk
}
'''


@pytest.fixture
def temp_test_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_analysis_results():
    """Mock analysis results for testing."""
    return {
        "success": True,
        "syntax_issues": [
            {
                "type": "nasa_rule_3_violation",
                "severity": "critical",
                "line": 10,
                "column": 0,
                "message": "Function exceeds 60 lines",
                "recommendation": "Break into smaller functions"
            },
            {
                "type": "security_risk",
                "severity": "high",
                "line": 25,
                "column": 4,
                "message": "Dangerous eval() usage",
                "recommendation": "Use ast.literal_eval"
            }
        ],
        "execution_time": 0.125,
        "language": "python"
    }


@pytest.fixture
def mock_compliance_standards():
    """Mock compliance standards list."""
    return ["NASA_POT10", "DFARS", "ISO27001"]


# Test data builders
class AnalysisResultBuilder:
    """Builder for creating test analysis results."""

    def __init__(self):
        self.result = {
            "success": True,
            "syntax_issues": [],
            "execution_time": 0.0,
            "language": "python"
        }

    def with_issue(self, issue_type: str, severity: str = "medium") -> 'AnalysisResultBuilder':
        """Add an issue to the result."""
        self.result["syntax_issues"].append({
            "type": issue_type,
            "severity": severity,
            "line": 1,
            "column": 0,
            "message": f"{issue_type} detected",
            "recommendation": "Fix this issue"
        })
        return self

    def with_nasa_violation(self, rule: int) -> 'AnalysisResultBuilder':
        """Add a NASA rule violation."""
        return self.with_issue(f"nasa_rule_{rule}_violation", "critical")

    def with_execution_time(self, time: float) -> 'AnalysisResultBuilder':
        """Set execution time."""
        self.result["execution_time"] = time
        return self

    def build(self) -> Dict[str, Any]:
        """Build the analysis result."""
        return self.result


@pytest.fixture
def analysis_result_builder():
    """Provide AnalysisResultBuilder fixture."""
    return AnalysisResultBuilder
