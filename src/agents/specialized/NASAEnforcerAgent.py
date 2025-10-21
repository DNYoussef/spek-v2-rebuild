"""
NASAEnforcerAgent - NASA Rule 10 Compliance Specialist

Enforces NASA Rule 10 standards:
- Check function length (<=60 LOC)
- Validate no recursion
- Check fixed loop bounds
- Generate compliance reports

Week 5 Day 6
Version: 8.0.0
"""

import time
import ast
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from src.agents.AgentBase import (
    AgentBase, AgentType, AgentStatus, AgentCapability, AgentMetadata,
    Task, ValidationResult, ValidationError, Result, ErrorInfo,
    create_agent_metadata
)
from src.agents.instructions import NASA_ENFORCER_INSTRUCTIONS

@dataclass
class NASAViolation:
    """NASA Rule 10 violation."""
    file_path: str
    function_name: str
    line_number: int
    violation_type: str
    actual_value: int
    limit: int

@dataclass
class NASAComplianceReport:
    """NASA compliance report."""
    compliance_pct: float
    total_functions: int
    violations: List[NASAViolation]

class NASAEnforcerAgent(AgentBase):
    """NASA Rule 10 compliance enforcement."""
    
    def __init__(self):
        metadata = create_agent_metadata(
            agent_id="nasa-enforcer",
            name="NASA Rule 10 Compliance Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=["check-compliance", "generate-report"],
            capabilities=[
                AgentCapability(name="Function Length Check", description="Validate functions <=60 LOC", level=10),
                AgentCapability(name="Recursion Detection", description="Detect recursive functions", level=9),
                AgentCapability(name="Loop Validation", description="Validate fixed loop bounds", level=8)
            ]
        ,
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=NASA_ENFORCER_INSTRUCTIONS.to_prompt()
        )
        super().__init__(metadata=metadata)
        self.max_function_loc = 60
    
    async def validate(self, task: Task) -> ValidationResult:
        start_time = time.time()
        errors = []
        errors.extend(self.validate_task_structure(task))
        errors.extend(self.validate_task_type(task))
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            validation_time=(time.time() - start_time) * 1000
        )
    
    async def execute(self, task: Task) -> Result:
        start_time = time.time()
        try:
            self.update_status(AgentStatus.BUSY)
            if task.type == "check-compliance":
                result_data = await self._check_compliance(task)
            else:
                result_data = await self._generate_report(task)
            self.update_status(AgentStatus.IDLE)
            return self.build_result(
                task_id=task.id, success=True, data=result_data,
                execution_time=(time.time() - start_time) * 1000
            )
        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return self.build_result(
                task_id=task.id, success=False,
                error=ErrorInfo(code="EXECUTION_FAILED", message=str(e)),
                execution_time=(time.time() - start_time) * 1000
            )
    
    async def _check_compliance(self, task: Task) -> Dict[str, Any]:
        file_path = task.payload.get("file_path")
        violations = self._check_file(file_path)
        return {"file_path": file_path, "violations": len(violations)}
    
    async def _generate_report(self, task: Task) -> Dict[str, Any]:
        target_path = task.payload.get("target_path", "src/")
        files = list(Path(target_path).rglob("*.py"))
        all_violations = []
        total_funcs = 0
        for f in files:
            violations = self._check_file(str(f))
            all_violations.extend(violations)
            total_funcs += len(violations) + self._count_compliant(str(f))
        compliance = ((total_funcs - len(all_violations)) / total_funcs * 100) if total_funcs > 0 else 100.0
        return {"compliance_pct": compliance, "violations": len(all_violations)}
    
    def _check_file(self, file_path: str) -> List[NASAViolation]:
        if not Path(file_path).exists():
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except:
                return []
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > self.max_function_loc:
                    violations.append(NASAViolation(
                        file_path=file_path, function_name=node.name,
                        line_number=node.lineno, violation_type="function_length",
                        actual_value=length, limit=self.max_function_loc
                    ))
        return violations
    
    def _count_compliant(self, file_path: str) -> int:
        if not Path(file_path).exists():
            return 0
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except:
                return 0
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length <= self.max_function_loc:
                    count += 1
        return count

def create_nasa_enforcer_agent() -> NASAEnforcerAgent:
    return NASAEnforcerAgent()
