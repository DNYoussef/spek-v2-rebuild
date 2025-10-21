"""
Syntax Analyzer - AST-based syntax analysis engine

Performs language-specific syntax analysis using AST parsing
and pattern matching. Detects syntax errors, god functions,
theater violations, and code quality issues.

NASA Rule 3 Compliance: ≤200 LOC target
Version: 6.0.0 (Week 2 Day 2)
"""

import ast
import re
import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SyntaxAnalyzer:
    """
    Language-specific syntax analysis engine.

    Supports Python (AST), JavaScript, C/C++ (regex-based).
    Detects syntax errors, god functions, theater code.
    """

    def __init__(self):
        """Initialize syntax analyzer with language support."""
        self.logger = logging.getLogger(__name__)
        self.supported_languages = ["python", "javascript", "js", "c", "cpp", "c++"]

    def analyze(self, source_code: str, language: str = "python") -> Dict[str, Any]:
        """
        Perform comprehensive syntax analysis.

        Args:
            source_code: Source code to analyze
            language: Programming language

        Returns:
            Dict with syntax_issues, execution_time, success
        """
        # Validation
        assert source_code, "source_code cannot be empty"
        assert language, "language cannot be empty"

        start_time = time.time()
        syntax_issues = []

        try:
            # Route to language-specific analyzer
            if language.lower() == "python":
                syntax_issues = self._analyze_python(source_code)
            elif language.lower() in ["javascript", "js"]:
                syntax_issues = self._analyze_javascript(source_code)
            elif language.lower() in ["c", "cpp", "c++"]:
                syntax_issues = self._analyze_c_cpp(source_code)
            else:
                syntax_issues = self._analyze_generic(source_code)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "syntax_issues": syntax_issues,
                "execution_time": execution_time,
                "language": language,
                "engine_version": "6.0.0"
            }

        except Exception as e:
            self.logger.error(f"Syntax analysis failed: {e}")
            return {
                "success": False,
                "syntax_issues": [],
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    def _analyze_python(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Analyze Python syntax using AST parsing.

        Detects:
        - Syntax errors
        - God functions (>60 LOC)
        - Theater violations (NotImplementedError)
        - Security risks (eval/exec)
        - Style issues
        """
        issues = []

        try:
            # Parse with AST
            tree = ast.parse(source_code)

            # Walk AST nodes
            for node in ast.walk(tree):
                # God function detection (NASA Rule 3)
                if isinstance(node, ast.FunctionDef):
                    # Count source lines, not AST statements
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 60:
                        issues.append({
                            "type": "nasa_rule_3_violation",
                            "severity": "high",
                            "line": node.lineno,
                            "column": node.col_offset,
                            "message": f"Function '{node.name}' exceeds 60 lines ({func_lines} lines)",
                            "recommendation": "Break function into smaller, focused functions"
                        })

                # Theater detection - NotImplementedError
                if isinstance(node, ast.Raise):
                    if isinstance(node.exc, ast.Call):
                        if (hasattr(node.exc.func, 'id') and
                            node.exc.func.id == 'NotImplementedError'):
                            issues.append({
                                "type": "theater_violation",
                                "severity": "critical",
                                "line": node.lineno,
                                "column": node.col_offset,
                                "message": "NotImplementedError theater detected",
                                "recommendation": "Implement actual functionality"
                            })

                # Security risk - eval/exec usage
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id in ['eval', 'exec']:
                        issues.append({
                            "type": "security_risk",
                            "severity": "critical",
                            "line": node.lineno,
                            "column": node.col_offset,
                            "message": f"Dangerous {node.func.id}() usage detected",
                            "recommendation": "Replace with safe alternatives like ast.literal_eval"
                        })

                # Wildcard import detection
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == '*':
                            issues.append({
                                "type": "import_quality",
                                "severity": "medium",
                                "line": node.lineno,
                                "column": node.col_offset,
                                "message": "Wildcard import detected",
                                "recommendation": "Use explicit imports for better code clarity"
                            })

        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "severity": "critical",
                "line": e.lineno,
                "column": e.offset,
                "message": f"Python syntax error: {e.msg}",
                "recommendation": "Fix syntax error before proceeding"
            })

        return issues

    def _analyze_javascript(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Analyze JavaScript syntax using regex patterns.

        Detects:
        - Theater violations (throw new Error("Not implemented"))
        - Function definitions
        - Basic style issues
        """
        issues = []
        lines = source_code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Theater detection
            if 'throw new Error("Not implemented")' in line or \
               'throw new Error(\'Not implemented\')' in line:
                issues.append({
                    "type": "theater_violation",
                    "severity": "critical",
                    "line": line_num,
                    "column": 0,
                    "message": "JavaScript implementation theater detected",
                    "recommendation": "Implement actual functionality"
                })

            # Function definition tracking
            if re.match(r'^\s*(function\s+\w+|const\s+\w+\s*=\s*\(.*\)\s*=>)', line):
                issues.append({
                    "type": "function_detected",
                    "severity": "info",
                    "line": line_num,
                    "column": 0,
                    "message": "Function definition found",
                    "recommendation": "Verify function length and complexity"
                })

        return issues

    def _analyze_c_cpp(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Analyze C/C++ syntax using regex patterns.

        Detects:
        - Buffer overflow risks (strcpy, sprintf)
        - Memory management issues
        - Basic style issues
        """
        issues = []
        lines = source_code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Unsafe C functions
            if re.search(r'\b(strcpy|sprintf|gets)\s*\(', line):
                issues.append({
                    "type": "security_risk",
                    "severity": "high",
                    "line": line_num,
                    "column": 0,
                    "message": "Unsafe C function detected",
                    "recommendation": "Use safe alternatives (strncpy, snprintf, fgets)"
                })

        return issues

    def _analyze_generic(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Generic syntax analysis for unsupported languages.

        Detects:
        - Long lines (>200 chars)
        - Basic formatting issues
        """
        issues = []
        lines = source_code.split('\n')

        for line_num, line in enumerate(lines, 1):
            if len(line) > 200:
                issues.append({
                    "type": "long_line",
                    "severity": "low",
                    "line": line_num,
                    "column": 0,
                    "message": f"Line too long ({len(line)} characters)",
                    "recommendation": "Break long lines for readability"
                })

        return issues


# Factory function
def create_syntax_analyzer() -> SyntaxAnalyzer:
    """Create and return SyntaxAnalyzer instance."""
    return SyntaxAnalyzer()
