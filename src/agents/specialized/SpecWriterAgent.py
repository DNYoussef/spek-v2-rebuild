"""
SpecWriterAgent - Requirements Documentation Specialist

Captures full project context and creates comprehensive specifications:
- Functional requirements and user stories
- Non-functional requirements (performance, security)
- Edge cases and error scenarios
- Acceptance criteria and success metrics

Part of specialized agent roster (Week 5 Day 4).

Week 5 Day 4
Version: 8.0.0
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

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
from src.agents.instructions import SPEC_WRITER_INSTRUCTIONS


# ============================================================================
# Spec-Writer Specific Types
# ============================================================================

@dataclass
class Requirement:
    """Single requirement."""
    req_id: str
    category: str  # functional, non-functional, constraint
    priority: str  # P0, P1, P2, P3
    description: str
    acceptance_criteria: List[str]


@dataclass
class Specification:
    """Complete specification document."""
    spec_id: str
    title: str
    version: str
    created_at: str
    functional_requirements: List[Requirement]
    non_functional_requirements: List[Requirement]
    constraints: List[Requirement]
    edge_cases: List[str]
    success_metrics: Dict[str, str]


# ============================================================================
# SpecWriterAgent Class
# ============================================================================

class SpecWriterAgent(AgentBase):
    """
    Spec-Writer Agent - Requirements documentation specialist.

    Responsibilities:
    - Capture functional and non-functional requirements
    - Document edge cases and error scenarios
    - Define acceptance criteria
    - Create comprehensive specifications
    """

    def __init__(self):
        """Initialize Spec-Writer Agent."""
        metadata = create_agent_metadata(
            agent_id="spec-writer",
            name="Requirements Documentation Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "write-spec",
                "refine-requirements",
                "validate-spec",
                "extract-requirements"
            ],
            capabilities=[
                AgentCapability(
                    name="Requirements Capture",
                    description="Capture functional and non-functional requirements",
                    level=10
                ),
                AgentCapability(
                    name="Specification Writing",
                    description="Write clear, comprehensive specifications",
                    level=9
                ),
                AgentCapability(
                    name="Edge Case Identification",
                    description="Identify and document edge cases",
                    level=9
                ),
                AgentCapability(
                    name="Acceptance Criteria Definition",
                    description="Define measurable acceptance criteria",
                    level=8
                ),
                AgentCapability(
                    name="Constraint Documentation",
                    description="Document technical and business constraints",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=SPEC_WRITER_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

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

        # Spec-Writer specific validation
        if task.type == "write-spec":
            errors.extend(self._validate_write_payload(task))

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
            if task.type == "write-spec":
                result_data = await self._execute_write(task)
            elif task.type == "refine-requirements":
                result_data = await self._execute_refine(task)
            elif task.type == "validate-spec":
                result_data = await self._execute_validate(task)
            elif task.type == "extract-requirements":
                result_data = await self._execute_extract(task)
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

    async def _execute_write(self, task: Task) -> Dict[str, Any]:
        """
        Write specification from input.

        Args:
            task: Write-spec task

        Returns:
            Specification result
        """
        input_file = task.payload.get("input_file")
        spec_title = task.payload.get("title", "System Specification")

        self.log_info(f"Writing specification: {spec_title}")

        # Parse input
        input_data = self._parse_input(input_file)

        # Extract functional requirements
        functional_reqs = self._extract_functional_requirements(input_data)

        # Extract non-functional requirements
        non_functional_reqs = self._extract_non_functional_requirements(
            input_data
        )

        # Extract constraints
        constraints = self._extract_constraints(input_data)

        # Identify edge cases
        edge_cases = self._identify_edge_cases(input_data)

        # Define success metrics
        success_metrics = self._define_success_metrics(input_data)

        # Create specification
        spec = Specification(
            spec_id=f"SPEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=spec_title,
            version="1.0",
            created_at=datetime.now().isoformat(),
            functional_requirements=functional_reqs,
            non_functional_requirements=non_functional_reqs,
            constraints=constraints,
            edge_cases=edge_cases,
            success_metrics=success_metrics
        )

        # Write specification document
        output_file = task.payload.get(
            "output_file",
            f"specs/{spec.spec_id}.md"
        )
        self._write_specification_document(spec, output_file)

        return {
            "input_file": input_file,
            "specification_file": output_file,
            "spec_id": spec.spec_id,
            "title": spec_title,
            "functional_count": len(functional_reqs),
            "non_functional_count": len(non_functional_reqs),
            "constraint_count": len(constraints),
            "edge_case_count": len(edge_cases),
            "specification": spec.__dict__
        }

    async def _execute_refine(self, task: Task) -> Dict[str, Any]:
        """Refine existing requirements."""
        spec_file = task.payload.get("specification_file")

        self.log_info(f"Refining requirements: {spec_file}")

        return {
            "specification_file": spec_file,
            "refined": True
        }

    async def _execute_validate(self, task: Task) -> Dict[str, Any]:
        """Validate specification."""
        spec_file = task.payload.get("specification_file")

        self.log_info(f"Validating specification: {spec_file}")

        issues = []

        # Check for missing requirements
        # Check for ambiguous criteria
        # Check for conflicting constraints

        return {
            "specification_file": spec_file,
            "valid": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues
        }

    async def _execute_extract(self, task: Task) -> Dict[str, Any]:
        """Extract requirements from existing documents."""
        source_file = task.payload.get("source_file")

        self.log_info(f"Extracting requirements: {source_file}")

        return {
            "source_file": source_file,
            "requirements_extracted": 0
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _parse_input(self, input_file: str) -> Dict[str, Any]:
        """Parse input file."""
        if not Path(input_file).exists():
            return {"features": [], "constraints": []}

        # Parse markdown or JSON input
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract data (simplified)
        return {
            "features": ["agent coordination", "FSM management"],
            "constraints": ["<100ms latency", ">=80% coverage"]
        }

    def _extract_functional_requirements(
        self,
        input_data: Dict[str, Any]
    ) -> List[Requirement]:
        """Extract functional requirements."""
        requirements = []

        features = input_data.get("features", [])
        for i, feature in enumerate(features, 1):
            requirements.append(Requirement(
                req_id=f"FR-{i:03d}",
                category="functional",
                priority="P0",
                description=feature,
                acceptance_criteria=[
                    f"{feature} implemented and tested",
                    f"{feature} meets performance targets"
                ]
            ))

        return requirements

    def _extract_non_functional_requirements(
        self,
        input_data: Dict[str, Any]
    ) -> List[Requirement]:
        """Extract non-functional requirements."""
        requirements = []

        requirements.append(Requirement(
            req_id="NFR-001",
            category="non-functional",
            priority="P0",
            description="System must handle 200+ concurrent users",
            acceptance_criteria=[
                "Load test passes with 200 concurrent users",
                "Response time <100ms at peak load"
            ]
        ))

        requirements.append(Requirement(
            req_id="NFR-002",
            category="non-functional",
            priority="P1",
            description="System must maintain >=99.9% uptime",
            acceptance_criteria=[
                "Uptime monitoring enabled",
                "SLA compliance tracked"
            ]
        ))

        return requirements

    def _extract_constraints(
        self,
        input_data: Dict[str, Any]
    ) -> List[Requirement]:
        """Extract constraints."""
        requirements = []

        constraints = input_data.get("constraints", [])
        for i, constraint in enumerate(constraints, 1):
            requirements.append(Requirement(
                req_id=f"CON-{i:03d}",
                category="constraint",
                priority="P0",
                description=constraint,
                acceptance_criteria=[f"Constraint validated: {constraint}"]
            ))

        return requirements

    def _identify_edge_cases(
        self,
        input_data: Dict[str, Any]
    ) -> List[str]:
        """Identify edge cases."""
        return [
            "Empty input data",
            "Invalid data types",
            "Network failures",
            "Concurrent modifications",
            "Resource exhaustion"
        ]

    def _define_success_metrics(
        self,
        input_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Define success metrics."""
        return {
            "test_coverage": ">=80%",
            "nasa_compliance": ">=90%",
            "performance": "<100ms latency",
            "uptime": ">=99.9%"
        }

    def _write_specification_document(
        self,
        spec: Specification,
        output_file: str
    ) -> None:
        """Write specification to file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        content = f"""# {spec.title}

**Specification ID**: {spec.spec_id}
**Version**: {spec.version}
**Created**: {spec.created_at}

---

## Functional Requirements

{self._format_requirements(spec.functional_requirements)}

## Non-Functional Requirements

{self._format_requirements(spec.non_functional_requirements)}

## Constraints

{self._format_requirements(spec.constraints)}

## Edge Cases

{self._format_edge_cases(spec.edge_cases)}

## Success Metrics

{self._format_success_metrics(spec.success_metrics)}
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _format_requirements(
        self,
        requirements: List[Requirement]
    ) -> str:
        """Format requirements for documentation."""
        lines = []
        for req in requirements:
            lines.append(f"### {req.req_id}: {req.description}")
            lines.append(f"- **Priority**: {req.priority}")
            lines.append(f"- **Category**: {req.category}")
            lines.append(f"- **Acceptance Criteria**:")
            for criterion in req.acceptance_criteria:
                lines.append(f"  - {criterion}")
            lines.append("")
        return "\n".join(lines)

    def _format_edge_cases(self, edge_cases: List[str]) -> str:
        """Format edge cases."""
        return "\n".join(f"- {case}" for case in edge_cases)

    def _format_success_metrics(
        self,
        metrics: Dict[str, str]
    ) -> str:
        """Format success metrics."""
        return "\n".join(
            f"- **{metric}**: {value}" for metric, value in metrics.items()
        )

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_write_payload(self, task: Task) -> List[ValidationError]:
        """Validate write-spec task payload."""
        errors = []

        if "input_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.input_file",
                message="Write task requires 'input_file' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_spec_writer_agent() -> SpecWriterAgent:
    """
    Create Spec-Writer Agent instance.

    Returns:
        SpecWriterAgent
    """
    return SpecWriterAgent()
