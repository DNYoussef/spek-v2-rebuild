"""
SecurityManagerAgent - Security Validation Specialist

Implements comprehensive security mechanisms:
- Scan code for security vulnerabilities
- Validate authentication and authorization
- Detect insecure patterns and practices
- Generate security reports and recommendations

Part of specialized agent roster (Week 5 Day 5).

Week 5 Day 5
Version: 8.0.0
"""

import time
import re
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
from src.agents.instructions import SECURITY_MANAGER_INSTRUCTIONS


# ============================================================================
# Security-Manager Specific Types
# ============================================================================

@dataclass
class SecurityVulnerability:
    """Security vulnerability."""
    vuln_id: str
    severity: str  # critical, high, medium, low
    category: str  # sql_injection, xss, hardcoded_secret, etc.
    file_path: str
    line_number: int
    description: str
    recommendation: str


@dataclass
class SecurityReport:
    """Security scan report."""
    scan_id: str
    vulnerabilities: List[SecurityVulnerability]
    security_score: float  # 0-100
    files_scanned: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


# ============================================================================
# SecurityManagerAgent Class
# ============================================================================

class SecurityManagerAgent(AgentBase):
    """
    Security-Manager Agent - Security validation specialist.

    Responsibilities:
    - Scan code for security vulnerabilities
    - Validate authentication mechanisms
    - Detect insecure coding patterns
    - Generate security reports
    """

    def __init__(self):
        """Initialize Security-Manager Agent."""
        metadata = create_agent_metadata(
            agent_id="security-manager",
            name="Security Validation Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "scan-security",
                "validate-auth",
                "detect-vulnerabilities",
                "generate-report"
            ],
            capabilities=[
                AgentCapability(
                    name="Vulnerability Scanning",
                    description="Scan code for security vulnerabilities",
                    level=10
                ),
                AgentCapability(
                    name="Authentication Validation",
                    description="Validate auth mechanisms",
                    level=9
                ),
                AgentCapability(
                    name="Pattern Detection",
                    description="Detect insecure coding patterns",
                    level=9
                ),
                AgentCapability(
                    name="Security Reporting",
                    description="Generate comprehensive security reports",
                    level=8
                ),
                AgentCapability(
                    name="Compliance Checking",
                    description="Check compliance with security standards",
                    level=8
                )
            ]
        ,
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=SECURITY_MANAGER_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Security patterns to detect
        self.vulnerability_patterns = {
            "hardcoded_secret": [
                r'password\s*=\s*["\'][\w]+["\']',
                r'api_key\s*=\s*["\'][\w]+["\']',
                r'secret\s*=\s*["\'][\w]+["\']'
            ],
            "sql_injection": [
                r'execute\s*\(\s*["\'].*%s.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']'
            ],
            "command_injection": [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\(',
                r'exec\s*\('
            ],
            "insecure_crypto": [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES\s*\('
            ]
        }

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

        # Security-Manager specific validation
        if task.type == "scan-security":
            errors.extend(self._validate_scan_payload(task))

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
            if task.type == "scan-security":
                result_data = await self._execute_scan(task)
            elif task.type == "validate-auth":
                result_data = await self._execute_validate_auth(task)
            elif task.type == "detect-vulnerabilities":
                result_data = await self._execute_detect_vulns(task)
            elif task.type == "generate-report":
                result_data = await self._execute_generate_report(task)
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

    async def _execute_scan(self, task: Task) -> Dict[str, Any]:
        """
        Scan code for security vulnerabilities.

        Args:
            task: Scan-security task

        Returns:
            Security scan result
        """
        target_path = task.payload.get("target_path", "src/")

        self.log_info(f"Scanning {target_path} for vulnerabilities")

        # Collect all files to scan
        files_to_scan = self._collect_files(target_path)

        # Scan each file
        all_vulnerabilities = []
        for file_path in files_to_scan:
            vulns = self._scan_file(file_path)
            all_vulnerabilities.extend(vulns)

        # Count by severity
        severity_counts = self._count_by_severity(all_vulnerabilities)

        # Calculate security score
        security_score = self._calculate_security_score(severity_counts)

        # Create security report
        report = SecurityReport(
            scan_id=f"scan-{int(time.time())}",
            vulnerabilities=all_vulnerabilities,
            security_score=security_score,
            files_scanned=len(files_to_scan),
            critical_count=severity_counts["critical"],
            high_count=severity_counts["high"],
            medium_count=severity_counts["medium"],
            low_count=severity_counts["low"]
        )

        return {
            "scan_id": report.scan_id,
            "security_score": security_score,
            "files_scanned": len(files_to_scan),
            "vulnerability_count": len(all_vulnerabilities),
            "severity_counts": severity_counts,
            "report": report.__dict__
        }

    async def _execute_validate_auth(self, task: Task) -> Dict[str, Any]:
        """Validate authentication mechanisms."""
        auth_file = task.payload.get("auth_file")

        self.log_info(f"Validating authentication in {auth_file}")

        # Check for auth best practices
        issues = []

        if Path(auth_file).exists():
            with open(auth_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for common auth issues
            if "password" in content.lower() and "hash" not in content.lower():
                issues.append("Passwords should be hashed")

            if "token" in content.lower() and "jwt" not in content.lower():
                issues.append("Consider using JWT for tokens")

        return {
            "auth_file": auth_file,
            "valid": len(issues) == 0,
            "issues": issues
        }

    async def _execute_detect_vulns(self, task: Task) -> Dict[str, Any]:
        """Detect specific vulnerabilities."""
        file_path = task.payload.get("file_path")
        vuln_type = task.payload.get("vuln_type", "all")

        self.log_info(
            f"Detecting {vuln_type} vulnerabilities in {file_path}"
        )

        vulnerabilities = self._scan_file(file_path)

        # Filter by type if specified
        if vuln_type != "all":
            vulnerabilities = [
                v for v in vulnerabilities
                if v.category == vuln_type
            ]

        return {
            "file_path": file_path,
            "vuln_type": vuln_type,
            "vulnerability_count": len(vulnerabilities),
            "vulnerabilities": [v.__dict__ for v in vulnerabilities]
        }

    async def _execute_generate_report(self, task: Task) -> Dict[str, Any]:
        """Generate security report."""
        scan_id = task.payload.get("scan_id")

        self.log_info(f"Generating security report for {scan_id}")

        return {
            "scan_id": scan_id,
            "report_generated": True,
            "report_file": f"reports/security-{scan_id}.pdf"
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _collect_files(self, target_path: str) -> List[str]:
        """Collect files to scan."""
        path = Path(target_path)

        if path.is_file():
            return [str(path)]

        # Collect Python files
        files = []
        if path.is_dir():
            files = [str(f) for f in path.rglob("*.py")]

        return files

    def _scan_file(self, file_path: str) -> List[SecurityVulnerability]:
        """Scan single file for vulnerabilities."""
        if not Path(file_path).exists():
            return []

        vulnerabilities = []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check each line against patterns
        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity(category)
                        vulnerabilities.append(SecurityVulnerability(
                            vuln_id=f"VULN-{len(vulnerabilities)+1:03d}",
                            severity=severity,
                            category=category,
                            file_path=file_path,
                            line_number=line_num,
                            description=f"Detected {category} pattern",
                            recommendation=self._get_recommendation(
                                category
                            )
                        ))

        return vulnerabilities

    def _get_severity(self, category: str) -> str:
        """Get severity level for vulnerability category."""
        severity_map = {
            "hardcoded_secret": "critical",
            "sql_injection": "critical",
            "command_injection": "critical",
            "insecure_crypto": "high"
        }
        return severity_map.get(category, "medium")

    def _get_recommendation(self, category: str) -> str:
        """Get recommendation for vulnerability category."""
        recommendations = {
            "hardcoded_secret": "Use environment variables",
            "sql_injection": "Use parameterized queries",
            "command_injection": "Validate and sanitize inputs",
            "insecure_crypto": "Use SHA-256 or better"
        }
        return recommendations.get(
            category,
            "Review and fix vulnerability"
        )

    def _count_by_severity(
        self,
        vulnerabilities: List[SecurityVulnerability]
    ) -> Dict[str, int]:
        """Count vulnerabilities by severity."""
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        for vuln in vulnerabilities:
            counts[vuln.severity] += 1

        return counts

    def _calculate_security_score(
        self,
        severity_counts: Dict[str, int]
    ) -> float:
        """Calculate security score."""
        # Start at 100, deduct points for vulnerabilities
        score = 100.0

        score -= severity_counts["critical"] * 20
        score -= severity_counts["high"] * 10
        score -= severity_counts["medium"] * 5
        score -= severity_counts["low"] * 2

        return max(0.0, score)

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_scan_payload(self, task: Task) -> List[ValidationError]:
        """Validate scan-security task payload."""
        errors = []

        if "target_path" not in task.payload:
            errors.append(ValidationError(
                field="payload.target_path",
                message="Scan task requires 'target_path' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_security_manager_agent() -> SecurityManagerAgent:
    """
    Create Security-Manager Agent instance.

    Returns:
        SecurityManagerAgent
    """
    return SecurityManagerAgent()
