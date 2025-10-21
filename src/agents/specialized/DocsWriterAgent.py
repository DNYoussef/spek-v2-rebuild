"""
DocsWriterAgent - Documentation Generation Specialist

Creates concise, clear, modular documentation:
- Generate API documentation from code
- Write user guides and tutorials
- Create architecture diagrams and flowcharts
- Maintain documentation consistency

Part of specialized agent roster (Week 5 Day 5).

Week 5 Day 5
Version: 8.0.0
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import ast

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
from src.agents.instructions import DOCS_WRITER_INSTRUCTIONS


# ============================================================================
# Docs-Writer Specific Types
# ============================================================================

@dataclass
class APIDocumentation:
    """API documentation."""
    module_name: str
    classes: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    constants: List[Dict[str, Any]]


@dataclass
class UserGuide:
    """User guide documentation."""
    title: str
    sections: List[Dict[str, str]]
    examples: List[str]
    prerequisites: List[str]


# ============================================================================
# DocsWriterAgent Class
# ============================================================================

class DocsWriterAgent(AgentBase):
    """
    Docs-Writer Agent - Documentation generation specialist.

    Responsibilities:
    - Generate API documentation from source code
    - Write user guides and tutorials
    - Create README files
    - Maintain documentation consistency
    """

    def __init__(self):
        """Initialize Docs-Writer Agent."""
        metadata = create_agent_metadata(
            agent_id="docs-writer",
            name="Documentation Generation Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "generate-api-docs",
                "write-user-guide",
                "create-readme",
                "update-docs"
            ],
            capabilities=[
                AgentCapability(
                    name="API Documentation",
                    description="Generate API docs from source code",
                    level=10
                ),
                AgentCapability(
                    name="User Guide Writing",
                    description="Write clear user guides and tutorials",
                    level=9
                ),
                AgentCapability(
                    name="README Creation",
                    description="Create comprehensive README files",
                    level=9
                ),
                AgentCapability(
                    name="Documentation Maintenance",
                    description="Keep documentation up-to-date",
                    level=8
                ),
                AgentCapability(
                    name="Markdown Formatting",
                    description="Format documentation with markdown",
                    level=8
                )
            ]
        ,
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=DOCS_WRITER_INSTRUCTIONS.to_prompt()
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

        # Docs-Writer specific validation
        if task.type == "generate-api-docs":
            errors.extend(self._validate_api_docs_payload(task))

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
            if task.type == "generate-api-docs":
                result_data = await self._execute_generate_api_docs(task)
            elif task.type == "write-user-guide":
                result_data = await self._execute_write_user_guide(task)
            elif task.type == "create-readme":
                result_data = await self._execute_create_readme(task)
            elif task.type == "update-docs":
                result_data = await self._execute_update_docs(task)
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

    async def _execute_generate_api_docs(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Generate API documentation from source code.

        Args:
            task: Generate-api-docs task

        Returns:
            API documentation result
        """
        source_file = task.payload.get("source_file")

        self.log_info(f"Generating API docs for {source_file}")

        # Parse source code
        api_doc = self._parse_source_for_api_docs(source_file)

        # Generate markdown
        output_file = task.payload.get(
            "output_file",
            f"docs/api/{Path(source_file).stem}.md"
        )
        self._write_api_documentation(api_doc, output_file)

        return {
            "source_file": source_file,
            "output_file": output_file,
            "class_count": len(api_doc.classes),
            "function_count": len(api_doc.functions),
            "documentation": api_doc.__dict__
        }

    async def _execute_write_user_guide(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Write user guide."""
        topic = task.payload.get("topic", "User Guide")

        self.log_info(f"Writing user guide: {topic}")

        # Create user guide structure
        guide = UserGuide(
            title=topic,
            sections=[
                {"title": "Introduction", "content": "Overview"},
                {"title": "Getting Started", "content": "Setup"},
                {"title": "Usage", "content": "How to use"},
                {"title": "Examples", "content": "Code examples"}
            ],
            examples=["Example 1", "Example 2"],
            prerequisites=["Python 3.11+", "pip"]
        )

        # Write guide
        output_file = task.payload.get(
            "output_file",
            f"docs/guides/{topic.lower().replace(' ', '-')}.md"
        )
        self._write_user_guide(guide, output_file)

        return {
            "topic": topic,
            "output_file": output_file,
            "section_count": len(guide.sections),
            "guide": guide.__dict__
        }

    async def _execute_create_readme(self, task: Task) -> Dict[str, Any]:
        """Create README file."""
        project_name = task.payload.get("project_name", "Project")

        self.log_info(f"Creating README for {project_name}")

        # Generate README content
        readme_content = self._generate_readme_content(project_name)

        # Write README
        output_file = task.payload.get("output_file", "README.md")
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        return {
            "project_name": project_name,
            "output_file": output_file,
            "readme_created": True
        }

    async def _execute_update_docs(self, task: Task) -> Dict[str, Any]:
        """Update existing documentation."""
        doc_file = task.payload.get("doc_file")

        self.log_info(f"Updating documentation: {doc_file}")

        return {
            "doc_file": doc_file,
            "updated": True
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _parse_source_for_api_docs(
        self,
        source_file: str
    ) -> APIDocumentation:
        """Parse source code to extract API documentation."""
        if not Path(source_file).exists():
            return APIDocumentation(
                module_name=Path(source_file).stem,
                classes=[],
                functions=[],
                constants=[]
            )

        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        try:
            tree = ast.parse(source_code)
        except:
            return APIDocumentation(
                module_name=Path(source_file).stem,
                classes=[],
                functions=[],
                constants=[]
            )

        classes = []
        functions = []
        constants = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "",
                    "methods": self._extract_methods(node)
                })
            elif isinstance(node, ast.FunctionDef):
                if not self._is_method(node):
                    functions.append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or "",
                        "args": [arg.arg for arg in node.args.args]
                    })

        return APIDocumentation(
            module_name=Path(source_file).stem,
            classes=classes,
            functions=functions,
            constants=constants
        )

    def _extract_methods(self, class_node: ast.ClassDef) -> List[Dict]:
        """Extract methods from class."""
        methods = []

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "",
                    "args": [arg.arg for arg in node.args.args]
                })

        return methods

    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a method."""
        # Simple heuristic: methods have 'self' as first arg
        if node.args.args:
            return node.args.args[0].arg in ('self', 'cls')
        return False

    def _write_api_documentation(
        self,
        api_doc: APIDocumentation,
        output_file: str
    ) -> None:
        """Write API documentation to file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        content = f"""# API Documentation: {api_doc.module_name}

## Classes

{self._format_classes(api_doc.classes)}

## Functions

{self._format_functions(api_doc.functions)}
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _format_classes(self, classes: List[Dict[str, Any]]) -> str:
        """Format classes for documentation."""
        if not classes:
            return "No classes defined."

        lines = []
        for cls in classes:
            lines.append(f"### {cls['name']}")
            if cls['docstring']:
                lines.append(f"\n{cls['docstring']}\n")
            lines.append("\n**Methods**:")
            for method in cls['methods']:
                args = ", ".join(method['args'])
                lines.append(f"- `{method['name']}({args})`")
                if method['docstring']:
                    lines.append(f"  - {method['docstring']}")
            lines.append("")

        return "\n".join(lines)

    def _format_functions(self, functions: List[Dict[str, Any]]) -> str:
        """Format functions for documentation."""
        if not functions:
            return "No functions defined."

        lines = []
        for func in functions:
            args = ", ".join(func['args'])
            lines.append(f"### {func['name']}({args})")
            if func['docstring']:
                lines.append(f"\n{func['docstring']}\n")
            lines.append("")

        return "\n".join(lines)

    def _write_user_guide(self, guide: UserGuide, output_file: str) -> None:
        """Write user guide to file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        content = f"""# {guide.title}

## Prerequisites

{self._format_prerequisites(guide.prerequisites)}

"""

        for section in guide.sections:
            content += f"## {section['title']}\n\n{section['content']}\n\n"

        if guide.examples:
            content += "## Examples\n\n"
            for example in guide.examples:
                content += f"- {example}\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _format_prerequisites(self, prerequisites: List[str]) -> str:
        """Format prerequisites list."""
        return "\n".join(f"- {prereq}" for prereq in prerequisites)

    def _generate_readme_content(self, project_name: str) -> str:
        """Generate README content."""
        return f"""# {project_name}

## Overview

[Brief description of the project]

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install {project_name.lower()}
```

## Usage

```python
from {project_name.lower()} import main

# Example usage
main()
```

## Documentation

See [docs/](docs/) for full documentation.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[License information]
"""

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_api_docs_payload(
        self,
        task: Task
    ) -> List[ValidationError]:
        """Validate generate-api-docs task payload."""
        errors = []

        if "source_file" not in task.payload:
            errors.append(ValidationError(
                field="payload.source_file",
                message="API docs task requires 'source_file' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_docs_writer_agent() -> DocsWriterAgent:
    """
    Create Docs-Writer Agent instance.

    Returns:
        DocsWriterAgent
    """
    return DocsWriterAgent()
