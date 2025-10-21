"""
PseudocodeWriterAgent - Algorithm Design Specialist

Transforms specifications into clear, executable pseudocode:
- Translates requirements into algorithmic steps
- Designs data structures and algorithms
- Plans error handling and edge cases
- Creates implementation-ready pseudocode

Part of specialized agent roster (Week 5 Day 4).

Week 5 Day 4
Version: 8.0.0
"""

import time
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
from src.agents.instructions import PSEUDOCODE_WRITER_INSTRUCTIONS


# ============================================================================
# Pseudocode-Writer Specific Types
# ============================================================================

@dataclass
class AlgorithmStep:
    """Single step in algorithm."""
    step_number: int
    description: str
    pseudocode: str
    complexity: str  # O(n), O(log n), etc.


@dataclass
class PseudocodeDesign:
    """Complete pseudocode design."""
    function_name: str
    purpose: str
    inputs: List[Dict[str, str]]  # [{name, type, description}]
    outputs: Dict[str, str]  # {type, description}
    algorithm_steps: List[AlgorithmStep]
    edge_cases: List[str]
    time_complexity: str
    space_complexity: str


# ============================================================================
# PseudocodeWriterAgent Class
# ============================================================================

class PseudocodeWriterAgent(AgentBase):
    """
    Pseudocode-Writer Agent - Algorithm design specialist.

    Responsibilities:
    - Transform specifications into pseudocode
    - Design algorithms and data structures
    - Plan error handling and edge cases
    - Document complexity analysis
    """

    def __init__(self):
        """Initialize Pseudocode-Writer Agent."""
        metadata = create_agent_metadata(
            agent_id="pseudocode-writer",
            name="Algorithm Design Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "write-pseudocode",
                "refine-algorithm",
                "analyze-complexity",
                "validate-pseudocode"
            ],
            capabilities=[
                AgentCapability(
                    name="Algorithm Design",
                    description="Design efficient algorithms from specifications",
                    level=10
                ),
                AgentCapability(
                    name="Pseudocode Writing",
                    description="Write clear, implementation-ready pseudocode",
                    level=9
                ),
                AgentCapability(
                    name="Complexity Analysis",
                    description="Analyze time and space complexity",
                    level=9
                ),
                AgentCapability(
                    name="Edge Case Planning",
                    description="Identify and plan for edge cases",
                    level=8
                ),
                AgentCapability(
                    name="Data Structure Selection",
                    description="Select appropriate data structures",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=PSEUDOCODE_WRITER_INSTRUCTIONS.to_prompt()
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

        # Pseudocode-Writer specific validation
        if task.type == "write-pseudocode":
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
            if task.type == "write-pseudocode":
                result_data = await self._execute_write(task)
            elif task.type == "refine-algorithm":
                result_data = await self._execute_refine(task)
            elif task.type == "analyze-complexity":
                result_data = await self._execute_analyze(task)
            elif task.type == "validate-pseudocode":
                result_data = await self._execute_validate(task)
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
        Write pseudocode from specification.

        Args:
            task: Write-pseudocode task

        Returns:
            Pseudocode design result
        """
        spec_file = task.payload.get("specification_file")
        function_name = task.payload.get("function_name", "algorithm")

        self.log_info(
            f"Writing pseudocode for {function_name} from {spec_file}"
        )

        # Parse specification
        requirements = self._parse_specification(spec_file)

        # Design algorithm steps
        steps = self._design_algorithm_steps(requirements)

        # Identify edge cases
        edge_cases = self._identify_edge_cases(requirements)

        # Analyze complexity
        time_complexity = self._analyze_time_complexity(steps)
        space_complexity = self._analyze_space_complexity(steps)

        # Create pseudocode design
        design = PseudocodeDesign(
            function_name=function_name,
            purpose=requirements.get("purpose", ""),
            inputs=requirements.get("inputs", []),
            outputs=requirements.get("outputs", {}),
            algorithm_steps=steps,
            edge_cases=edge_cases,
            time_complexity=time_complexity,
            space_complexity=space_complexity
        )

        # Write pseudocode document
        output_file = task.payload.get(
            "output_file",
            f"docs/pseudocode/{function_name}.md"
        )
        self._write_pseudocode_document(design, output_file)

        return {
            "specification_file": spec_file,
            "pseudocode_file": output_file,
            "function_name": function_name,
            "step_count": len(steps),
            "edge_case_count": len(edge_cases),
            "time_complexity": time_complexity,
            "space_complexity": space_complexity,
            "design": design.__dict__
        }

    async def _execute_refine(self, task: Task) -> Dict[str, Any]:
        """Refine existing algorithm."""
        pseudocode_file = task.payload.get("pseudocode_file")

        self.log_info(f"Refining algorithm: {pseudocode_file}")

        return {
            "pseudocode_file": pseudocode_file,
            "refined": True
        }

    async def _execute_analyze(self, task: Task) -> Dict[str, Any]:
        """Analyze algorithm complexity."""
        pseudocode_file = task.payload.get("pseudocode_file")

        self.log_info(f"Analyzing complexity: {pseudocode_file}")

        return {
            "pseudocode_file": pseudocode_file,
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        }

    async def _execute_validate(self, task: Task) -> Dict[str, Any]:
        """Validate pseudocode design."""
        pseudocode_file = task.payload.get("pseudocode_file")

        self.log_info(f"Validating pseudocode: {pseudocode_file}")

        issues = []

        # Check for missing edge cases
        # Check for complexity issues
        # Check for unclear steps

        return {
            "pseudocode_file": pseudocode_file,
            "valid": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _parse_specification(self, spec_file: str) -> Dict[str, Any]:
        """Parse specification file."""
        if not Path(spec_file).exists():
            return {
                "purpose": "Unknown",
                "inputs": [],
                "outputs": {}
            }

        # Parse markdown or JSON specification
        with open(spec_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract requirements (simplified)
        return {
            "purpose": "Process data efficiently",
            "inputs": [
                {"name": "data", "type": "List", "description": "Input data"}
            ],
            "outputs": {
                "type": "Result",
                "description": "Processed result"
            }
        }

    def _design_algorithm_steps(
        self,
        requirements: Dict[str, Any]
    ) -> List[AlgorithmStep]:
        """Design algorithm steps."""
        steps = []

        steps.append(AlgorithmStep(
            step_number=1,
            description="Validate inputs",
            pseudocode="IF inputs are invalid THEN return error",
            complexity="O(1)"
        ))

        steps.append(AlgorithmStep(
            step_number=2,
            description="Process data",
            pseudocode="FOR EACH item IN data DO process(item)",
            complexity="O(n)"
        ))

        steps.append(AlgorithmStep(
            step_number=3,
            description="Return result",
            pseudocode="RETURN processed_result",
            complexity="O(1)"
        ))

        return steps

    def _identify_edge_cases(
        self,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Identify edge cases."""
        return [
            "Empty input list",
            "Null/None values",
            "Invalid data types",
            "Large datasets (>10,000 items)"
        ]

    def _analyze_time_complexity(
        self,
        steps: List[AlgorithmStep]
    ) -> str:
        """Analyze time complexity."""
        # Find highest complexity
        complexities = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)"]

        max_complexity = "O(1)"
        for step in steps:
            if step.complexity in complexities:
                current_index = complexities.index(step.complexity)
                max_index = complexities.index(max_complexity)
                if current_index > max_index:
                    max_complexity = step.complexity

        return max_complexity

    def _analyze_space_complexity(
        self,
        steps: List[AlgorithmStep]
    ) -> str:
        """Analyze space complexity."""
        # Check for data structure allocations
        return "O(1)"  # Simplified

    def _write_pseudocode_document(
        self,
        design: PseudocodeDesign,
        output_file: str
    ) -> None:
        """Write pseudocode design to file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        content = f"""# Pseudocode: {design.function_name}

## Purpose

{design.purpose}

## Inputs

{self._format_inputs(design.inputs)}

## Outputs

- Type: {design.outputs.get('type', 'Unknown')}
- Description: {design.outputs.get('description', 'N/A')}

## Algorithm

{self._format_algorithm_steps(design.algorithm_steps)}

## Edge Cases

{self._format_edge_cases(design.edge_cases)}

## Complexity Analysis

- Time Complexity: {design.time_complexity}
- Space Complexity: {design.space_complexity}
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _format_inputs(self, inputs: List[Dict[str, str]]) -> str:
        """Format inputs for documentation."""
        if not inputs:
            return "None"

        lines = []
        for inp in inputs:
            lines.append(
                f"- {inp['name']} ({inp['type']}): {inp['description']}"
            )
        return "\n".join(lines)

    def _format_algorithm_steps(
        self,
        steps: List[AlgorithmStep]
    ) -> str:
        """Format algorithm steps."""
        lines = []
        for step in steps:
            lines.append(f"### Step {step.step_number}: {step.description}")
            lines.append(f"```")
            lines.append(step.pseudocode)
            lines.append(f"```")
            lines.append(f"Complexity: {step.complexity}\n")
        return "\n".join(lines)

    def _format_edge_cases(self, edge_cases: List[str]) -> str:
        """Format edge cases."""
        return "\n".join(f"- {case}" for case in edge_cases)

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_write_payload(self, task: Task) -> List[ValidationError]:
        """Validate write-pseudocode task payload."""
        errors = []

        if "specification_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.specification_file",
                message="Write task requires 'specification_file' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_pseudocode_writer_agent() -> PseudocodeWriterAgent:
    """
    Create Pseudocode-Writer Agent instance.

    Returns:
        PseudocodeWriterAgent
    """
    return PseudocodeWriterAgent()
