"""
TheaterDetectorAgent - Mock Code Detection Specialist

Detects theater code and genuine implementation:
- Identify TODO comments and placeholders
- Detect empty function bodies and pass statements
- Measure genuine implementation vs mock code
- Generate theater detection score

Part of specialized agent roster (Week 5 Day 6).

Week 5 Day 6
Version: 8.0.0
"""

import time
import re
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
from src.agents.instructions import THEATER_DETECTOR_INSTRUCTIONS


# ============================================================================
# Theater-Detector Specific Types
# ============================================================================

@dataclass
class TheaterEvidence:
    """Evidence of theater code."""
    file_path: str
    line_number: int
    evidence_type: str  # todo, pass, placeholder, etc.
    severity: int  # 1-10
    description: str


@dataclass
class TheaterReport:
    """Theater detection report."""
    total_files: int
    theater_score: float  # 0-100 (0=genuine, 100=all theater)
    evidence_count: int
    evidence_list: List[TheaterEvidence]
    genuine_loc: int
    theater_loc: int


# ============================================================================
# TheaterDetectorAgent Class
# ============================================================================

class TheaterDetectorAgent(AgentBase):
    """
    Theater-Detector Agent - Mock code detection specialist.

    Responsibilities:
    - Detect TODO comments and placeholders
    - Identify empty implementations
    - Calculate theater score
    - Recommend genuine implementation
    """

    def __init__(self):
        """Initialize Theater-Detector Agent."""
        metadata = create_agent_metadata(
            agent_id="theater-detector",
            name="Mock Code Detection Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "scan-theater",
                "calculate-score",
                "identify-placeholders",
                "validate-genuine"
            ],
            capabilities=[
                AgentCapability(
                    name="Theater Detection",
                    description="Detect mock and placeholder code",
                    level=10
                ),
                AgentCapability(
                    name="Score Calculation",
                    description="Calculate theater score",
                    level=9
                ),
                AgentCapability(
                    name="Pattern Recognition",
                    description="Recognize theater patterns",
                    level=9
                ),
                AgentCapability(
                    name="Genuine Validation",
                    description="Validate genuine implementation",
                    level=8
                ),
                AgentCapability(
                    name="Reporting",
                    description="Generate theater reports",
                    level=8
                )
            ]
        ,
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=THEATER_DETECTOR_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Theater patterns
        self.patterns = {
            "todo": r'#\s*TODO',
            "fixme": r'#\s*FIXME',
            "placeholder": r'#\s*placeholder',
            "not_implemented": r'raise\s+NotImplementedError',
            "pass_only": r'^\s*pass\s*$'
        }

    # ========================================================================
    # AgentContract Implementation
    # ========================================================================

    async def validate(self, task: Task) -> ValidationResult:
        """Validate task before execution."""
        start_time = time.time()
        errors = []

        errors.extend(self.validate_task_structure(task))
        errors.extend(self.validate_task_type(task))

        if task.type == "scan-theater":
            errors.extend(self._validate_scan_payload(task))

        validation_time = (time.time() - start_time) * 1000

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            validation_time=validation_time
        )

    async def execute(self, task: Task) -> Result:
        """Execute validated task."""
        start_time = time.time()

        try:
            self.update_status(AgentStatus.BUSY)
            self.log_info(f"Executing task {task.id} (type: {task.type})")

            if task.type == "scan-theater":
                result_data = await self._execute_scan(task)
            elif task.type == "calculate-score":
                result_data = await self._execute_calculate_score(task)
            elif task.type == "identify-placeholders":
                result_data = await self._execute_identify_placeholders(task)
            elif task.type == "validate-genuine":
                result_data = await self._execute_validate_genuine(task)
            else:
                raise ValueError(f"Unsupported task type: {task.type}")

            execution_time = (time.time() - start_time) * 1000

            self.update_status(AgentStatus.IDLE)

            return self.build_result(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
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
        """Scan for theater code."""
        target_path = task.payload.get("target_path", "src/")

        self.log_info(f"Scanning {target_path} for theater code")

        files = self._collect_files(target_path)
        all_evidence = []
        total_loc = 0
        theater_loc = 0

        for file_path in files:
            evidence = self._scan_file(file_path)
            all_evidence.extend(evidence)

            loc_data = self._count_loc(file_path)
            total_loc += loc_data["total"]
            theater_loc += loc_data["theater"]

        genuine_loc = total_loc - theater_loc
        theater_score = self._calculate_theater_score(
            theater_loc,
            total_loc
        )

        report = TheaterReport(
            total_files=len(files),
            theater_score=theater_score,
            evidence_count=len(all_evidence),
            evidence_list=all_evidence,
            genuine_loc=genuine_loc,
            theater_loc=theater_loc
        )

        return {
            "target_path": target_path,
            "file_count": len(files),
            "theater_score": theater_score,
            "evidence_count": len(all_evidence),
            "genuine_loc": genuine_loc,
            "theater_loc": theater_loc,
            "report": report.__dict__
        }

    async def _execute_calculate_score(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Calculate theater score."""
        file_path = task.payload.get("file_path")

        self.log_info(f"Calculating theater score for {file_path}")

        loc_data = self._count_loc(file_path)
        score = self._calculate_theater_score(
            loc_data["theater"],
            loc_data["total"]
        )

        return {
            "file_path": file_path,
            "theater_score": score,
            "genuine_loc": loc_data["total"] - loc_data["theater"],
            "theater_loc": loc_data["theater"]
        }

    async def _execute_identify_placeholders(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Identify placeholder code."""
        file_path = task.payload.get("file_path")

        self.log_info(f"Identifying placeholders in {file_path}")

        placeholders = self._find_placeholders(file_path)

        return {
            "file_path": file_path,
            "placeholder_count": len(placeholders),
            "placeholders": placeholders
        }

    async def _execute_validate_genuine(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Validate genuine implementation."""
        file_path = task.payload.get("file_path")

        self.log_info(f"Validating genuine code in {file_path}")

        is_genuine = self._is_genuine_implementation(file_path)

        return {
            "file_path": file_path,
            "is_genuine": is_genuine
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _collect_files(self, target_path: str) -> List[str]:
        """Collect Python files."""
        path = Path(target_path)

        if path.is_file():
            return [str(path)]

        files = []
        if path.is_dir():
            files = [str(f) for f in path.rglob("*.py")]

        return files

    def _scan_file(self, file_path: str) -> List[TheaterEvidence]:
        """Scan single file for theater evidence."""
        if not Path(file_path).exists():
            return []

        evidence = []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            for evidence_type, pattern in self.patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    evidence.append(TheaterEvidence(
                        file_path=file_path,
                        line_number=line_num,
                        evidence_type=evidence_type,
                        severity=self._get_severity(evidence_type),
                        description=f"Found {evidence_type} at line {line_num}"
                    ))

        return evidence

    def _count_loc(self, file_path: str) -> Dict[str, int]:
        """Count lines of code (genuine vs theater)."""
        if not Path(file_path).exists():
            return {"total": 0, "theater": 0}

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total = 0
        theater = 0

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                total += 1

                # Check if line is theater
                if any(re.search(p, line) for p in self.patterns.values()):
                    theater += 1
                elif stripped == "pass":
                    theater += 1

        return {"total": total, "theater": theater}

    def _calculate_theater_score(
        self,
        theater_loc: int,
        total_loc: int
    ) -> float:
        """Calculate theater score (0-100)."""
        if total_loc == 0:
            return 0.0

        return (theater_loc / total_loc) * 100

    def _get_severity(self, evidence_type: str) -> int:
        """Get severity for evidence type."""
        severity_map = {
            "todo": 5,
            "fixme": 7,
            "placeholder": 8,
            "not_implemented": 10,
            "pass_only": 6
        }
        return severity_map.get(evidence_type, 5)

    def _find_placeholders(self, file_path: str) -> List[str]:
        """Find placeholder code."""
        placeholders = []

        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern_name, pattern in self.patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                placeholders.extend(matches)

        return placeholders

    def _is_genuine_implementation(self, file_path: str) -> bool:
        """Check if file has genuine implementation."""
        loc_data = self._count_loc(file_path)

        if loc_data["total"] == 0:
            return False

        score = self._calculate_theater_score(
            loc_data["theater"],
            loc_data["total"]
        )

        return score < 20.0  # Less than 20% theater

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_scan_payload(self, task: Task) -> List[ValidationError]:
        """Validate scan-theater task payload."""
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

def create_theater_detector_agent() -> TheaterDetectorAgent:
    """
    Create Theater-Detector Agent instance.

    Returns:
        TheaterDetectorAgent
    """
    return TheaterDetectorAgent()
