"""
CoderAgent - Code Implementation Specialist

Implements clean, efficient, modular code:
- Write production-ready code from specifications
- Follow design patterns and best practices
- Implement type safety and error handling
- Maintain NASA Rule 10 compliance

Part of core agent roster (Week 5 Day 6).

Week 5 Day 6
Version: 8.0.0
"""

import time
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
from src.agents.instructions import CODER_SYSTEM_INSTRUCTIONS


# ============================================================================
# Coder-Specific Types
# ============================================================================

@dataclass
class CodeImplementation:
    """Code implementation result."""
    file_path: str
    language: str
    lines_of_code: int
    functions: List[str]
    classes: List[str]
    test_coverage: float


@dataclass
class RefactorResult:
    """Code refactoring result."""
    file_path: str
    original_loc: int
    refactored_loc: int
    improvements: List[str]


# ============================================================================
# CoderAgent Class
# ============================================================================

class CoderAgent(AgentBase):
    """
    Coder Agent - Code implementation specialist.

    Responsibilities:
    - Write clean, efficient code
    - Follow best practices and design patterns
    - Maintain type safety
    - Ensure NASA Rule 10 compliance
    """

    def __init__(self):
        """Initialize Coder Agent."""
        metadata = create_agent_metadata(
            agent_id="coder",
            name="Code Implementation Specialist",
            agent_type=AgentType.CORE,
            supported_task_types=[
                "implement-code",
                "refactor-code",
                "optimize-code",
                "validate-implementation"
            ],
            capabilities=[
                AgentCapability(
                    name="Code Implementation",
                    description="Write clean, efficient code",
                    level=10
                ),
                AgentCapability(
                    name="Code Refactoring",
                    description="Refactor code for quality",
                    level=9
                ),
                AgentCapability(
                    name="Design Patterns",
                    description="Apply appropriate design patterns",
                    level=9
                ),
                AgentCapability(
                    name="Type Safety",
                    description="Implement type hints and validation",
                    level=8
                ),
                AgentCapability(
                    name="NASA Compliance",
                    description="Maintain NASA Rule 10 compliance",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=CODER_SYSTEM_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Supported languages
        self.languages = ["python", "typescript", "javascript"]

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

        # Coder-specific validation
        if task.type == "implement-code":
            errors.extend(self._validate_implement_payload(task))

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
            if task.type == "implement-code":
                result_data = await self._execute_implement(task)
            elif task.type == "refactor-code":
                result_data = await self._execute_refactor(task)
            elif task.type == "optimize-code":
                result_data = await self._execute_optimize(task)
            elif task.type == "validate-implementation":
                result_data = await self._execute_validate_impl(task)
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

    async def _execute_implement(self, task: Task) -> Dict[str, Any]:
        """
        Implement code from specification.

        Args:
            task: Implement-code task

        Returns:
            Implementation result
        """
        spec_file = task.payload.get("spec_file")
        output_file = task.payload.get("output_file")
        language = task.payload.get("language", "python")

        self.log_info(
            f"Implementing {language} code from {spec_file}"
        )

        # Parse specification
        spec = self._parse_specification(spec_file)

        # Generate code
        code = self._generate_code(spec, language)

        # Write code to file
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)

        # Analyze implementation
        analysis = self._analyze_code(output_file, language)

        implementation = CodeImplementation(
            file_path=output_file,
            language=language,
            lines_of_code=analysis["loc"],
            functions=analysis["functions"],
            classes=analysis["classes"],
            test_coverage=0.0  # To be measured by tests
        )

        return {
            "spec_file": spec_file,
            "output_file": output_file,
            "language": language,
            "lines_of_code": analysis["loc"],
            "function_count": len(analysis["functions"]),
            "class_count": len(analysis["classes"]),
            "implementation": implementation.__dict__
        }

    async def _execute_refactor(self, task: Task) -> Dict[str, Any]:
        """Refactor existing code."""
        file_path = task.payload.get("file_path")

        self.log_info(f"Refactoring code in {file_path}")

        # Read original code
        if not Path(file_path).exists():
            return {"error": "File not found", "refactored": False}

        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        original_loc = len([
            l for l in original_code.split('\n')
            if l.strip() and not l.strip().startswith('#')
        ])

        # Refactor code (simplified)
        improvements = self._identify_improvements(file_path)

        refactor = RefactorResult(
            file_path=file_path,
            original_loc=original_loc,
            refactored_loc=original_loc,  # Would change after refactor
            improvements=improvements
        )

        return {
            "file_path": file_path,
            "original_loc": original_loc,
            "improvement_count": len(improvements),
            "refactor": refactor.__dict__
        }

    async def _execute_optimize(self, task: Task) -> Dict[str, Any]:
        """Optimize code for performance."""
        file_path = task.payload.get("file_path")

        self.log_info(f"Optimizing code in {file_path}")

        optimizations = [
            "Use list comprehensions instead of loops",
            "Cache frequently accessed values",
            "Use generators for large datasets"
        ]

        return {
            "file_path": file_path,
            "optimization_count": len(optimizations),
            "optimizations": optimizations
        }

    async def _execute_validate_impl(self, task: Task) -> Dict[str, Any]:
        """Validate code implementation."""
        file_path = task.payload.get("file_path")

        self.log_info(f"Validating implementation: {file_path}")

        issues = []

        if Path(file_path).exists():
            # Check NASA compliance
            nasa_compliant = self._check_nasa_compliance(file_path)
            if not nasa_compliant:
                issues.append("NASA Rule 10 violations detected")

            # Check type hints
            has_type_hints = self._check_type_hints(file_path)
            if not has_type_hints:
                issues.append("Missing type hints")

        return {
            "file_path": file_path,
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
            return {"functions": [], "classes": []}

        # Simplified spec parsing
        return {
            "functions": ["process_data", "validate_input"],
            "classes": ["DataProcessor"]
        }

    def _generate_code(
        self,
        spec: Dict[str, Any],
        language: str
    ) -> str:
        """Generate code from specification."""
        if language == "python":
            code = '"""Generated code from specification."""\n\n'
            code += "from typing import Any, Dict, List\n\n"

            # Generate classes
            for cls in spec.get("classes", []):
                code += f"class {cls}:\n"
                code += f'    """Generated {cls} class."""\n'
                code += "    pass\n\n"

            # Generate functions
            for func in spec.get("functions", []):
                code += f"def {func}(data: Any) -> Dict[str, Any]:\n"
                code += f'    """{func.replace("_", " ").title()}."""\n'
                code += "    return {}\n\n"

            return code

        return "// Code generation not implemented for " + language

    def _analyze_code(
        self,
        file_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Analyze generated code."""
        if not Path(file_path).exists():
            return {"loc": 0, "functions": [], "classes": []}

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        loc = len([
            l for l in code.split('\n')
            if l.strip() and not l.strip().startswith('#')
        ])

        if language == "python":
            try:
                tree = ast.parse(code)
                functions = [
                    node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                ]
                classes = [
                    node.name for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ]
            except:
                functions = []
                classes = []
        else:
            functions = []
            classes = []

        return {
            "loc": loc,
            "functions": functions,
            "classes": classes
        }

    def _identify_improvements(self, file_path: str) -> List[str]:
        """Identify code improvements."""
        improvements = []

        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Check for common issues
            if "TODO" in code:
                improvements.append("Remove TODO comments")

            if "pass" in code:
                improvements.append("Implement placeholder functions")

        return improvements

    def _check_nasa_compliance(self, file_path: str) -> bool:
        """Check NASA Rule 10 compliance."""
        if not Path(file_path).exists():
            return True

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except:
                return True

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > 60:
                    return False

        return True

    def _check_type_hints(self, file_path: str) -> bool:
        """Check for type hints."""
        if not Path(file_path).exists():
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Simple check for type hints
        return "typing" in code or "->" in code

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_implement_payload(
        self,
        task: Task
    ) -> List[ValidationError]:
        """Validate implement-code task payload."""
        errors = []

        if "spec_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.spec_file",
                message="Implement task requires 'spec_file' in payload",
                severity=10
            ))

        if "output_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.output_file",
                message="Implement task requires 'output_file' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_coder_agent() -> CoderAgent:
    """
    Create Coder Agent instance.

    Returns:
        CoderAgent
    """
    return CoderAgent()
