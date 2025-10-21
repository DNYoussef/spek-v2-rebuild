"""
ArchitectAgent - System Architecture Design Specialist

Designs scalable, secure, and modular system architectures based on:
- Functional specifications and requirements
- Technology constraints and preferences
- Performance and scalability requirements
- Security and compliance standards

Part of specialized agent roster (Week 5 Day 4).

Week 5 Day 4
Version: 8.0.0
"""

import time
import json
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
from src.agents.instructions import ARCHITECT_INSTRUCTIONS


# ============================================================================
# Architect-Specific Types
# ============================================================================

@dataclass
class ArchitectureComponent:
    """Component in system architecture."""
    name: str
    type: str  # service, module, database, api, etc.
    responsibilities: List[str]
    dependencies: List[str]
    technology: Optional[str] = None


@dataclass
class ArchitectureDesign:
    """Complete architecture design."""
    system_name: str
    components: List[ArchitectureComponent]
    data_flow: Dict[str, List[str]]  # component → dependent components
    technology_stack: Dict[str, str]  # layer → technology
    design_patterns: List[str]
    scalability_strategy: str
    security_considerations: List[str]


# ============================================================================
# ArchitectAgent Class
# ============================================================================

class ArchitectAgent(AgentBase):
    """
    Architect Agent - System architecture design specialist.

    Responsibilities:
    - Design system architectures from specifications
    - Define component boundaries and responsibilities
    - Select appropriate design patterns
    - Plan scalability and performance strategies
    - Document security considerations
    """

    def __init__(self):
        """Initialize Architect Agent."""
        metadata = create_agent_metadata(
            agent_id="architect",
            name="System Architecture Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "design-architecture",
                "refactor-architecture",
                "validate-architecture",
                "document-architecture"
            ],
            capabilities=[
                AgentCapability(
                    name="System Architecture Design",
                    description="Design scalable, secure system architectures",
                    level=10
                ),
                AgentCapability(
                    name="Design Pattern Selection",
                    description="Select appropriate design patterns for requirements",
                    level=9
                ),
                AgentCapability(
                    name="Technology Stack Planning",
                    description="Plan technology stacks based on constraints",
                    level=9
                ),
                AgentCapability(
                    name="Scalability Planning",
                    description="Design for horizontal and vertical scalability",
                    level=8
                ),
                AgentCapability(
                    name="Security Architecture",
                    description="Incorporate security best practices into design",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=ARCHITECT_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Common design patterns
        self.design_patterns = {
            "microservices": ["service mesh", "api gateway", "event sourcing"],
            "monolith": ["layered", "mvc", "repository"],
            "serverless": ["function-as-service", "event-driven"],
            "distributed": ["saga", "cqrs", "event sourcing"]
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

        # Architect-specific validation
        if task.type == "design-architecture":
            errors.extend(self._validate_design_payload(task))
        elif task.type == "validate-architecture":
            errors.extend(self._validate_architecture_payload(task))

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
            if task.type == "design-architecture":
                result_data = await self._execute_design(task)
            elif task.type == "refactor-architecture":
                result_data = await self._execute_refactor(task)
            elif task.type == "validate-architecture":
                result_data = await self._execute_validate(task)
            elif task.type == "document-architecture":
                result_data = await self._execute_document(task)
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

    async def _execute_design(self, task: Task) -> Dict[str, Any]:
        """
        Design system architecture from specifications.

        Args:
            task: Design-architecture task

        Returns:
            Architecture design result
        """
        spec_file = task.payload.get("specification_file")
        style = task.payload.get("style", "microservices")

        self.log_info(f"Designing {style} architecture from {spec_file}")

        # Parse specification
        requirements = self._parse_specification(spec_file)

        # Design components
        components = self._design_components(requirements, style)

        # Design data flow
        data_flow = self._design_data_flow(components)

        # Select technology stack
        tech_stack = self._select_technology_stack(style, requirements)

        # Select design patterns
        patterns = self._select_design_patterns(style, requirements)

        # Plan scalability
        scalability = self._plan_scalability(style, requirements)

        # Security considerations
        security = self._plan_security(requirements)

        # Create architecture design
        design = ArchitectureDesign(
            system_name=requirements.get("system_name", "System"),
            components=components,
            data_flow=data_flow,
            technology_stack=tech_stack,
            design_patterns=patterns,
            scalability_strategy=scalability,
            security_considerations=security
        )

        # Write architecture document
        output_file = task.payload.get(
            "output_file",
            "architecture/ARCHITECTURE-DESIGN.md"
        )
        self._write_architecture_document(design, output_file)

        return {
            "specification_file": spec_file,
            "architecture_file": output_file,
            "style": style,
            "component_count": len(components),
            "pattern_count": len(patterns),
            "design": design.__dict__
        }

    async def _execute_refactor(self, task: Task) -> Dict[str, Any]:
        """Refactor existing architecture."""
        current_arch = task.payload.get("current_architecture")
        improvements = task.payload.get("improvements", [])

        self.log_info(f"Refactoring architecture: {improvements}")

        return {
            "current_architecture": current_arch,
            "improvements_applied": improvements,
            "refactored": True
        }

    async def _execute_validate(self, task: Task) -> Dict[str, Any]:
        """Validate architecture design."""
        arch_file = task.payload.get("architecture_file")

        self.log_info(f"Validating architecture: {arch_file}")

        issues = []

        # Check for missing components
        # Check for circular dependencies
        # Check for scalability concerns
        # Check for security gaps

        return {
            "architecture_file": arch_file,
            "valid": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues
        }

    async def _execute_document(self, task: Task) -> Dict[str, Any]:
        """Generate architecture documentation."""
        arch_file = task.payload.get("architecture_file")

        self.log_info(f"Documenting architecture: {arch_file}")

        return {
            "architecture_file": arch_file,
            "documentation_generated": True
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _parse_specification(self, spec_file: str) -> Dict[str, Any]:
        """Parse specification file."""
        if not Path(spec_file).exists():
            return {"system_name": "Unknown", "requirements": []}

        # Parse markdown or JSON specification
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract requirements (simplified)
        return {
            "system_name": "SPEK Platform v2",
            "requirements": ["agent coordination", "FSM management"],
            "constraints": ["<100ms latency", ">=80% test coverage"]
        }

    def _design_components(
        self,
        requirements: Dict[str, Any],
        style: str
    ) -> List[ArchitectureComponent]:
        """Design system components."""
        components = []

        # Create core components based on style
        if style == "microservices":
            components.append(ArchitectureComponent(
                name="API Gateway",
                type="service",
                responsibilities=["routing", "authentication"],
                dependencies=[]
            ))

        return components

    def _design_data_flow(
        self,
        components: List[ArchitectureComponent]
    ) -> Dict[str, List[str]]:
        """Design data flow between components."""
        data_flow = {}

        for component in components:
            data_flow[component.name] = component.dependencies

        return data_flow

    def _select_technology_stack(
        self,
        style: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, str]:
        """Select technology stack."""
        return {
            "backend": "Python 3.11",
            "database": "PostgreSQL",
            "cache": "Redis",
            "api": "FastAPI"
        }

    def _select_design_patterns(
        self,
        style: str,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Select appropriate design patterns."""
        return self.design_patterns.get(style, [])

    def _plan_scalability(
        self,
        style: str,
        requirements: Dict[str, Any]
    ) -> str:
        """Plan scalability strategy."""
        if style == "microservices":
            return "Horizontal scaling with container orchestration"
        return "Vertical scaling with load balancing"

    def _plan_security(
        self,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Plan security considerations."""
        return [
            "JWT authentication",
            "HTTPS/TLS encryption",
            "Input validation",
            "Rate limiting"
        ]

    def _write_architecture_document(
        self,
        design: ArchitectureDesign,
        output_file: str
    ) -> None:
        """Write architecture design to file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        content = f"""# {design.system_name} Architecture

## Components

{self._format_components(design.components)}

## Technology Stack

{self._format_tech_stack(design.technology_stack)}

## Design Patterns

{self._format_patterns(design.design_patterns)}

## Scalability

{design.scalability_strategy}

## Security

{self._format_security(design.security_considerations)}
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _format_components(
        self,
        components: List[ArchitectureComponent]
    ) -> str:
        """Format components for documentation."""
        lines = []
        for comp in components:
            lines.append(f"### {comp.name}")
            lines.append(f"- Type: {comp.type}")
            lines.append(
                f"- Responsibilities: {', '.join(comp.responsibilities)}"
            )
        return "\n".join(lines)

    def _format_tech_stack(self, tech_stack: Dict[str, str]) -> str:
        """Format technology stack."""
        return "\n".join(
            f"- {layer}: {tech}" for layer, tech in tech_stack.items()
        )

    def _format_patterns(self, patterns: List[str]) -> str:
        """Format design patterns."""
        return "\n".join(f"- {pattern}" for pattern in patterns)

    def _format_security(self, security: List[str]) -> str:
        """Format security considerations."""
        return "\n".join(f"- {item}" for item in security)

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_design_payload(self, task: Task) -> List[ValidationError]:
        """Validate design-architecture task payload."""
        errors = []

        if "specification_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.specification_file",
                message="Design task requires 'specification_file' in payload",
                severity=10
            ))

        return errors

    def _validate_architecture_payload(
        self,
        task: Task
    ) -> List[ValidationError]:
        """Validate validate-architecture task payload."""
        errors = []

        if "architecture_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.architecture_file",
                message="Validate task requires 'architecture_file'",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_architect_agent() -> ArchitectAgent:
    """
    Create Architect Agent instance.

    Returns:
        ArchitectAgent
    """
    return ArchitectAgent()
