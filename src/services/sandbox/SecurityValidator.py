"""
SecurityValidator - Pre/post execution security validation

Validates code before execution and verifies security constraints after.

Pre-execution:
- AST-based security checks
- Block dangerous imports (os.system, subprocess, etc.)
- Block file system access attempts
- Block network access attempts

Post-execution:
- Verify network isolation (no connections)
- Verify filesystem unchanged (read-only enforced)
- Verify resource limits respected

Week 4 Day 3
Version: 8.0.0
"""

import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Types
# ============================================================================

class SecurityLevel(str, Enum):
    """Security check severity levels."""
    CRITICAL = "critical"  # Blocks execution
    HIGH = "high"          # Warns but allows
    MEDIUM = "medium"      # Logged only
    LOW = "low"           # Informational


@dataclass
class SecurityIssue:
    """Security validation issue."""
    level: SecurityLevel
    code: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class SecurityCheckResult:
    """Result of security validation."""
    passed: bool
    issues: List[SecurityIssue]
    blocked: bool  # True if execution should be blocked


# ============================================================================
# SecurityValidator Class
# ============================================================================

class SecurityValidator:
    """
    Validates code for security issues before/after execution.

    Defense-in-depth approach:
    1. Static analysis (AST)
    2. Pattern matching (regex)
    3. Runtime validation (Docker constraints)
    4. Post-execution verification
    """

    # Dangerous imports that should be blocked
    DANGEROUS_IMPORTS = {
        'os',           # File system access
        'sys',          # System access
        'subprocess',   # Shell execution
        'shutil',       # File operations
        'pathlib',      # File system access
        'socket',       # Network access
        'urllib',       # Network access
        'requests',     # Network access
        'http',         # Network access
        'ftplib',       # Network access
        'telnetlib',    # Network access
        'eval',         # Code execution
        'exec',         # Code execution
        'compile',      # Code execution
        '__import__',   # Dynamic imports
    }

    # Dangerous function calls
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file',  # File access
        'input', 'raw_input',  # User input (can hang)
    }

    # Dangerous attribute access patterns
    DANGEROUS_ATTRIBUTES = {
        '__code__', '__globals__', '__builtins__',
        '__dict__', '__class__', '__bases__'
    }

    def __init__(self):
        """Initialize security validator."""
        pass

    async def validate_pre_execution(
        self,
        code: str,
        language: str = "python"
    ) -> SecurityCheckResult:
        """
        Validate code before execution.

        Performs static analysis to detect security issues.

        Args:
            code: Source code to validate
            language: Programming language

        Returns:
            SecurityCheckResult with issues found
        """
        issues: List[SecurityIssue] = []

        if language == "python":
            issues.extend(self._check_python_code(code))
        elif language in ["typescript", "javascript"]:
            issues.extend(self._check_javascript_code(code))

        # Check for critical issues
        critical_issues = [i for i in issues if i.level == SecurityLevel.CRITICAL]
        blocked = len(critical_issues) > 0

        return SecurityCheckResult(
            passed=len(critical_issues) == 0,
            issues=issues,
            blocked=blocked
        )

    def _check_python_code(self, code: str) -> List[SecurityIssue]:
        """
        Check Python code for security issues using AST.

        Args:
            code: Python source code

        Returns:
            List of security issues found
        """
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(SecurityIssue(
                level=SecurityLevel.HIGH,
                code="SYNTAX_ERROR",
                message=f"Syntax error: {e}",
                line_number=e.lineno
            ))
            return issues

        # Walk AST and check for dangerous patterns
        for node in ast.walk(tree):
            self._check_imports(node, issues)
            self._check_function_calls(node, issues)
            self._check_attributes(node, issues)

        return issues

    def _check_imports(self, node, issues: List[SecurityIssue]) -> None:
        """Check for dangerous imports in AST node."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.DANGEROUS_IMPORTS:
                    issues.append(SecurityIssue(
                        level=SecurityLevel.CRITICAL,
                        code="DANGEROUS_IMPORT",
                        message=f"Dangerous import blocked: {alias.name}",
                        line_number=node.lineno,
                        suggestion=f"Remove 'import {alias.name}'"
                    ))

        if isinstance(node, ast.ImportFrom):
            if node.module in self.DANGEROUS_IMPORTS:
                issues.append(SecurityIssue(
                    level=SecurityLevel.CRITICAL,
                    code="DANGEROUS_IMPORT",
                    message=f"Dangerous import blocked: {node.module}",
                    line_number=node.lineno,
                    suggestion=f"Remove 'from {node.module} import ...'"
                ))

    def _check_function_calls(self, node, issues: List[SecurityIssue]) -> None:
        """Check for dangerous function calls in AST node."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.DANGEROUS_FUNCTIONS:
                    issues.append(SecurityIssue(
                        level=SecurityLevel.CRITICAL,
                        code="DANGEROUS_FUNCTION",
                        message=f"Dangerous function blocked: {node.func.id}()",
                        line_number=node.lineno,
                        suggestion=f"Remove call to {node.func.id}()"
                    ))

    def _check_attributes(self, node, issues: List[SecurityIssue]) -> None:
        """Check for dangerous attribute access in AST node."""
        if isinstance(node, ast.Attribute):
            if node.attr in self.DANGEROUS_ATTRIBUTES:
                issues.append(SecurityIssue(
                    level=SecurityLevel.HIGH,
                    code="DANGEROUS_ATTRIBUTE",
                    message=f"Suspicious attribute access: {node.attr}",
                    line_number=node.lineno,
                    suggestion="Avoid accessing internal attributes"
                ))

    def _check_javascript_code(self, code: str) -> List[SecurityIssue]:
        """
        Check JavaScript/TypeScript code for security issues.

        Uses regex patterns (no AST parser for JS in Python).

        Args:
            code: JavaScript source code

        Returns:
            List of security issues found
        """
        issues = []

        # Check for dangerous patterns
        patterns = {
            r'\beval\s*\(': ("DANGEROUS_FUNCTION", "eval() is dangerous"),
            r'\bFunction\s*\(': ("DANGEROUS_FUNCTION", "Function() constructor is dangerous"),
            r'\brequire\s*\(\s*[\'"]child_process[\'"]\s*\)': ("DANGEROUS_IMPORT", "child_process blocked"),
            r'\brequire\s*\(\s*[\'"]fs[\'"]\s*\)': ("DANGEROUS_IMPORT", "fs (filesystem) blocked"),
            r'\brequire\s*\(\s*[\'"]net[\'"]\s*\)': ("DANGEROUS_IMPORT", "net (network) blocked"),
            r'\bprocess\.exit': ("DANGEROUS_FUNCTION", "process.exit() not allowed"),
        }

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, (code_name, message) in patterns.items():
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        level=SecurityLevel.CRITICAL,
                        code=code_name,
                        message=message,
                        line_number=line_num,
                        suggestion="Remove dangerous code"
                    ))

        return issues

    async def validate_post_execution(
        self,
        container_stats: Dict[str, Any]
    ) -> SecurityCheckResult:
        """
        Validate after execution to verify security constraints.

        Args:
            container_stats: Docker container statistics

        Returns:
            SecurityCheckResult with violations found
        """
        issues = []

        self._check_network_isolation(container_stats, issues)
        self._check_resource_limits(container_stats, issues)
        self._check_filesystem_security(container_stats, issues)
        self._check_user_security(container_stats, issues)

        critical_issues = [i for i in issues if i.level == SecurityLevel.CRITICAL]

        return SecurityCheckResult(
            passed=len(critical_issues) == 0,
            issues=issues,
            blocked=False  # Post-execution, can't block
        )

    def _check_network_isolation(
        self,
        container_stats: Dict[str, Any],
        issues: List[SecurityIssue]
    ) -> None:
        """Check network isolation constraints."""
        if 'NetworkSettings' in container_stats:
            networks = container_stats['NetworkSettings'].get('Networks', {})
            if networks and any(net != 'none' for net in networks.keys()):
                issues.append(SecurityIssue(
                    level=SecurityLevel.CRITICAL,
                    code="NETWORK_VIOLATION",
                    message="Network isolation violated",
                    suggestion="Ensure NetworkMode='none'"
                ))

    def _check_resource_limits(
        self,
        container_stats: Dict[str, Any],
        issues: List[SecurityIssue]
    ) -> None:
        """Check resource limit constraints."""
        if 'HostConfig' in container_stats:
            host_config = container_stats['HostConfig']

            if not host_config.get('Memory'):
                issues.append(SecurityIssue(
                    level=SecurityLevel.HIGH,
                    code="NO_MEMORY_LIMIT",
                    message="Memory limit not enforced",
                    suggestion="Set Memory limit in HostConfig"
                ))

            if not host_config.get('CpuQuota'):
                issues.append(SecurityIssue(
                    level=SecurityLevel.MEDIUM,
                    code="NO_CPU_LIMIT",
                    message="CPU limit not enforced",
                    suggestion="Set CpuQuota in HostConfig"
                ))

    def _check_filesystem_security(
        self,
        container_stats: Dict[str, Any],
        issues: List[SecurityIssue]
    ) -> None:
        """Check filesystem security constraints."""
        config = container_stats.get('Config', {})
        if not config.get('ReadonlyRootfs'):
            issues.append(SecurityIssue(
                level=SecurityLevel.HIGH,
                code="WRITABLE_ROOTFS",
                message="Root filesystem is writable",
                suggestion="Set ReadonlyRootfs=True"
            ))

    def _check_user_security(
        self,
        container_stats: Dict[str, Any],
        issues: List[SecurityIssue]
    ) -> None:
        """Check user security constraints."""
        config = container_stats.get('Config', {})
        if config.get('User') in ['root', '', None]:
            issues.append(SecurityIssue(
                level=SecurityLevel.CRITICAL,
                code="ROOT_USER",
                message="Container running as root",
                suggestion="Set User to non-root (e.g., 'node', 'nobody')"
            ))

    def get_safe_subset_suggestions(self, language: str) -> List[str]:
        """
        Get suggestions for safe subset of language features.

        Args:
            language: Programming language

        Returns:
            List of safe practices
        """
        if language == "python":
            return [
                "✅ Use built-in math functions (abs, min, max, sum)",
                "✅ Use string operations (str.upper, str.lower, str.split)",
                "✅ Use list/dict operations (append, extend, update)",
                "✅ Use comprehensions ([x for x in range(10)])",
                "✅ Import: math, json, datetime, itertools, functools",
                "❌ Avoid: os, sys, subprocess, socket, file operations",
                "❌ Avoid: eval(), exec(), __import__()",
                "❌ Avoid: network access (urllib, requests)",
            ]
        elif language in ["javascript", "typescript"]:
            return [
                "✅ Use Array methods (map, filter, reduce)",
                "✅ Use String methods (toUpperCase, toLowerCase, split)",
                "✅ Use Math operations (Math.max, Math.min)",
                "✅ Use JSON operations (JSON.parse, JSON.stringify)",
                "❌ Avoid: fs, child_process, net, http modules",
                "❌ Avoid: eval(), Function() constructor",
                "❌ Avoid: process.exit(), process.env",
            ]
        else:
            return ["No specific guidance for this language"]


def create_security_validator() -> SecurityValidator:
    """
    Factory function to create SecurityValidator.

    Returns:
        SecurityValidator instance
    """
    return SecurityValidator()
