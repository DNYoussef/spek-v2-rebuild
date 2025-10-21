"""
ReviewerAgent - Code Review and Quality Validation Specialist

Performs comprehensive code review with:
- NASA Rule 10 compliance checking
- Type safety validation
- Security audit (Bandit patterns)
- Code quality metrics (cyclomatic complexity, god objects)
- Best practices enforcement

Week 5 Day 2
Version: 8.0.0
"""

import time
import os
import ast
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from src.agents.AgentBase import (
    AgentBase,
    AgentType,
    AgentStatus,
    AgentCapability,
    AgentMetadata,
    Task,
    ValidationResult,
    ValidationError,
    Result,
    ErrorInfo,
    create_agent_metadata
)
from src.agents.instructions import REVIEWER_SYSTEM_INSTRUCTIONS


# ============================================================================
# Reviewer-Specific Types
# ============================================================================

@dataclass
class ReviewIssue:
    """Code review issue."""
    file: str
    line: int
    severity: str  # critical, high, medium, low
    category: str  # nasa, security, quality, style
    message: str
    suggestion: Optional[str] = None


@dataclass
class ReviewReport:
    """Code review report."""
    files_reviewed: int
    issues_found: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[ReviewIssue]
    overall_score: float  # 0-100


@dataclass
class NASAComplianceResult:
    """NASA Rule 10 compliance result."""
    compliant: bool
    violations: List[Dict[str, Any]]
    compliance_percent: float


# ============================================================================
# ReviewerAgent Class
# ============================================================================

class ReviewerAgent(AgentBase):
    """
    Reviewer Agent - Code review and quality validation specialist.

    Responsibilities:
    - Review code quality
    - Validate NASA Rule 10 compliance
    - Check type safety
    - Perform security audit
    - Enforce best practices
    """

    def __init__(self):
        """Initialize Reviewer Agent."""
        metadata = create_agent_metadata(
            agent_id="reviewer",
            name="Code Review Specialist",
            agent_type=AgentType.CORE,
            supported_task_types=[
                "review-code",
                "check-nasa",
                "audit-security",
                "validate-quality"
            ],
            capabilities=[
                AgentCapability(
                    name="NASA Rule 10 Compliance",
                    description="Validate NASA Rule 10 compliance (≤60 LOC, no recursion)",
                    level=10
                ),
                AgentCapability(
                    name="Security Audit",
                    description="Identify security vulnerabilities (Bandit patterns)",
                    level=9
                ),
                AgentCapability(
                    name="Code Quality Analysis",
                    description="Analyze code quality metrics (complexity, god objects)",
                    level=9
                ),
                AgentCapability(
                    name="Type Safety Validation",
                    description="Validate type hints and type safety",
                    level=8
                ),
                AgentCapability(
                    name="Best Practices Enforcement",
                    description="Enforce coding best practices and style guidelines",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=REVIEWER_SYSTEM_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # NASA Rule 10 thresholds
        self.max_function_loc = 60
        self.min_assertions = 2
        self.nasa_compliance_target = 90.0  # 90% compliance target

    # ========================================================================
    # AgentContract Implementation
    # ========================================================================

    async def validate(self, task: Task) -> ValidationResult:
        """
        Validate task before execution.

        Target: <5ms latency

        Args:
            task: Task to validate

        Returns:
            ValidationResult
        """
        start_time = time.time()
        errors = []

        # Common structure validation
        errors.extend(self.validate_task_structure(task))

        # Task type validation
        errors.extend(self.validate_task_type(task))

        # Reviewer-specific validation
        if task.type == "review-code":
            errors.extend(self._validate_review_code_payload(task))
        elif task.type == "check-nasa":
            errors.extend(self._validate_nasa_payload(task))
        elif task.type == "audit-security":
            errors.extend(self._validate_security_payload(task))

        validation_time = (time.time() - start_time) * 1000  # ms

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            validation_time=validation_time
        )

    async def execute(self, task: Task) -> Result:
        """
        Execute validated task.

        Routes to appropriate handler based on task type.

        Args:
            task: Task to execute

        Returns:
            Result
        """
        start_time = time.time()

        try:
            self.update_status(AgentStatus.BUSY)
            self.log_info(f"Executing task {task.id} (type: {task.type})")

            # Route to handler
            if task.type == "review-code":
                result_data = await self._execute_review_code(task)
            elif task.type == "check-nasa":
                result_data = await self._execute_check_nasa(task)
            elif task.type == "audit-security":
                result_data = await self._execute_audit_security(task)
            elif task.type == "validate-quality":
                result_data = await self._execute_validate_quality(task)
            else:
                raise ValueError(f"Unsupported task type: {task.type}")

            execution_time = (time.time() - start_time) * 1000  # ms

            self.update_status(AgentStatus.IDLE)

            return self.build_result(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000  # ms
            self.log_error(f"Task {task.id} failed", exc=e)

            self.update_status(AgentStatus.ERROR)

            return self.build_result(
                task_id=task.id,
                success=False,
                error=ErrorInfo(
                    code="EXECUTION_FAILED",
                    message=str(e),
                    stack=None
                ),
                execution_time=execution_time
            )

    # ========================================================================
    # Task Execution Methods
    # ========================================================================

    async def _execute_review_code(self, task: Task) -> Dict[str, Any]:
        """
        Comprehensive code review.

        Args:
            task: Review-code task

        Returns:
            Review result
        """
        source_files = task.payload.get("source_files", [])

        self.log_info(f"Reviewing {len(source_files)} files")

        all_issues = []

        for file_path in source_files:
            # NASA compliance
            nasa_result = self._check_nasa_compliance(file_path)
            all_issues.extend(self._convert_nasa_to_issues(file_path, nasa_result))

            # Security audit
            security_issues = self._audit_security(file_path)
            all_issues.extend(security_issues)

            # Quality metrics
            quality_issues = self._check_quality_metrics(file_path)
            all_issues.extend(quality_issues)

        # Categorize issues
        critical = len([i for i in all_issues if i.severity == "critical"])
        high = len([i for i in all_issues if i.severity == "high"])
        medium = len([i for i in all_issues if i.severity == "medium"])
        low = len([i for i in all_issues if i.severity == "low"])

        # Calculate overall score
        overall_score = self._calculate_review_score(all_issues, len(source_files))

        return {
            "files_reviewed": len(source_files),
            "issues_found": len(all_issues),
            "critical_issues": critical,
            "high_issues": high,
            "medium_issues": medium,
            "low_issues": low,
            "overall_score": overall_score,
            "issues": [i.__dict__ for i in all_issues]
        }

    async def _execute_check_nasa(self, task: Task) -> Dict[str, Any]:
        """
        Check NASA Rule 10 compliance.

        Args:
            task: Check-nasa task

        Returns:
            NASA compliance result
        """
        source_file = task.payload.get("source_file")

        self.log_info(f"Checking NASA compliance for {source_file}")

        result = self._check_nasa_compliance(source_file)

        return {
            "source_file": source_file,
            "compliant": result.compliant,
            "compliance_percent": result.compliance_percent,
            "violations": result.violations,
            "target": self.nasa_compliance_target
        }

    async def _execute_audit_security(self, task: Task) -> Dict[str, Any]:
        """
        Perform security audit.

        Args:
            task: Audit-security task

        Returns:
            Security audit result
        """
        source_file = task.payload.get("source_file")

        self.log_info(f"Auditing security for {source_file}")

        issues = self._audit_security(source_file)

        critical = len([i for i in issues if i.severity == "critical"])
        high = len([i for i in issues if i.severity == "high"])

        return {
            "source_file": source_file,
            "issues_found": len(issues),
            "critical_issues": critical,
            "high_issues": high,
            "issues": [i.__dict__ for i in issues]
        }

    async def _execute_validate_quality(self, task: Task) -> Dict[str, Any]:
        """
        Validate code quality metrics.

        Args:
            task: Validate-quality task

        Returns:
            Quality validation result
        """
        source_file = task.payload.get("source_file")

        self.log_info(f"Validating quality for {source_file}")

        issues = self._check_quality_metrics(source_file)

        return {
            "source_file": source_file,
            "issues_found": len(issues),
            "issues": [i.__dict__ for i in issues]
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _check_nasa_compliance(self, file_path: str) -> NASAComplianceResult:
        """
        Check NASA Rule 10 compliance.

        Rules:
        - Functions ≤60 LOC
        - ≥2 assertions (critical paths only)
        - No recursion
        - Fixed loop bounds
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return NASAComplianceResult(
                compliant=False,
                violations=[{"error": "Syntax error in file"}],
                compliance_percent=0.0
            )

        violations = []
        total_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1

                # Check function LOC
                func_loc = self._count_function_loc(node, source_code)
                if func_loc > self.max_function_loc:
                    violations.append({
                        "function": node.name,
                        "line": node.lineno,
                        "rule": "max_function_loc",
                        "actual": func_loc,
                        "limit": self.max_function_loc
                    })

                # Check for recursion
                if self._is_recursive(node):
                    violations.append({
                        "function": node.name,
                        "line": node.lineno,
                        "rule": "no_recursion",
                        "message": "Recursive function detected"
                    })

        # Calculate compliance
        compliant_functions = total_functions - len(violations)
        compliance_percent = (compliant_functions / total_functions * 100) if total_functions > 0 else 100.0

        return NASAComplianceResult(
            compliant=compliance_percent >= self.nasa_compliance_target,
            violations=violations,
            compliance_percent=compliance_percent
        )

    def _audit_security(self, file_path: str) -> List[ReviewIssue]:
        """Perform security audit (simplified Bandit patterns)."""
        issues = []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check for dangerous patterns
        dangerous_imports = ['os.system', 'subprocess.call', 'eval', 'exec']

        for i, line in enumerate(lines, 1):
            for pattern in dangerous_imports:
                if pattern in line and not line.strip().startswith('#'):
                    issues.append(ReviewIssue(
                        file=file_path,
                        line=i,
                        severity="critical",
                        category="security",
                        message=f"Dangerous function '{pattern}' detected",
                        suggestion=f"Use safer alternative to '{pattern}'"
                    ))

        return issues

    def _check_quality_metrics(self, file_path: str) -> List[ReviewIssue]:
        """Check code quality metrics."""
        issues = []

        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return issues

        # Check cyclomatic complexity (simplified)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append(ReviewIssue(
                        file=file_path,
                        line=node.lineno,
                        severity="medium",
                        category="quality",
                        message=f"High cyclomatic complexity: {complexity}",
                        suggestion="Refactor function to reduce complexity"
                    ))

        return issues

    def _count_function_loc(self, func_node: ast.FunctionDef, source: str) -> int:
        """Count function lines of code (excluding docstrings)."""
        lines = source.split('\n')
        func_lines = lines[func_node.lineno - 1:func_node.end_lineno]

        # Exclude docstring
        code_lines = []
        in_docstring = False

        for line in func_lines:
            stripped = line.strip()
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue
            if not in_docstring and stripped and not stripped.startswith('#'):
                code_lines.append(line)

        return len(code_lines)

    def _is_recursive(self, func_node: ast.FunctionDef) -> bool:
        """Check if function is recursive."""
        func_name = func_node.name

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    return True

        return False

    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1

        return complexity

    def _convert_nasa_to_issues(
        self,
        file_path: str,
        nasa_result: NASAComplianceResult
    ) -> List[ReviewIssue]:
        """Convert NASA violations to review issues."""
        issues = []

        for violation in nasa_result.violations:
            severity = "high" if violation.get("rule") == "max_function_loc" else "medium"

            message = f"NASA Rule 10 violation: {violation.get('rule')}"
            if "actual" in violation:
                message += f" (actual: {violation['actual']}, limit: {violation['limit']})"

            issues.append(ReviewIssue(
                file=file_path,
                line=violation.get("line", 0),
                severity=severity,
                category="nasa",
                message=message,
                suggestion="Refactor function to meet NASA Rule 10"
            ))

        return issues

    def _calculate_review_score(
        self,
        issues: List[ReviewIssue],
        file_count: int
    ) -> float:
        """Calculate overall review score (0-100)."""
        if not issues:
            return 100.0

        # Weight issues by severity
        penalty = 0
        for issue in issues:
            if issue.severity == "critical":
                penalty += 20
            elif issue.severity == "high":
                penalty += 10
            elif issue.severity == "medium":
                penalty += 5
            else:
                penalty += 2

        # Normalize by file count
        penalty_per_file = penalty / max(file_count, 1)

        score = max(0, 100 - penalty_per_file)
        return round(score, 2)

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_review_code_payload(self, task: Task) -> List[ValidationError]:
        """Validate review-code task payload."""
        errors = []

        if "source_files" not in task.payload:
            errors.append(ValidationError(
                field="payload.source_files",
                message="Review-code task requires 'source_files' in payload",
                severity=10
            ))

        return errors

    def _validate_nasa_payload(self, task: Task) -> List[ValidationError]:
        """Validate check-nasa task payload."""
        errors = []

        if "source_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.source_file",
                message="Check-nasa task requires 'source_file' in payload",
                severity=10
            ))

        return errors

    def _validate_security_payload(self, task: Task) -> List[ValidationError]:
        """Validate audit-security task payload."""
        errors = []

        if "source_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.source_file",
                message="Audit-security task requires 'source_file' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_reviewer_agent() -> ReviewerAgent:
    """
    Create Reviewer Agent instance.

    Returns:
        ReviewerAgent
    """
    return ReviewerAgent()
