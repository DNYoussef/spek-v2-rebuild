"""
CodeAnalyzerAgent - Code Analysis Specialist

Automated static analysis, complexity metrics, and code quality:
- Perform static code analysis (AST parsing)
- Calculate cyclomatic complexity
- Detect code duplicates and smells
- Analyze dependency relationships

Part of specialized agent roster (Week 8 Day 3).

Week 8 Day 3
Version: 8.0.0
"""

import time
import ast
import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

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
from src.agents.instructions import CODE_ANALYZER_INSTRUCTIONS


# ============================================================================
# Code Analysis Types
# ============================================================================

@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    comment_ratio: float
    function_count: int
    class_count: int


@dataclass
class CodeSmell:
    """Code smell detection result."""
    smell_type: str
    severity: int  # 1-10
    location: str
    description: str
    suggestion: str


@dataclass
class DuplicationResult:
    """Code duplication detection result."""
    file1: str
    file2: str
    duplicate_lines: int
    similarity_score: float


# ============================================================================
# CodeAnalyzerAgent Class
# ============================================================================

class CodeAnalyzerAgent(AgentBase):
    """
    Code-Analyzer Agent - Code analysis specialist.

    Responsibilities:
    - Static code analysis
    - Complexity metrics
    - Code smell detection
    - Duplication detection
    """

    def __init__(self):
        """Initialize Code-Analyzer Agent."""
        metadata = create_agent_metadata(
            agent_id="code-analyzer",
            name="Code Analysis Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "analyze-code",
                "detect-complexity",
                "detect-duplicates",
                "analyze-dependencies"
            ],
            capabilities=[
                AgentCapability(
                    name="Static Code Analysis",
                    description="Perform AST-based code analysis",
                    level=10
                ),
                AgentCapability(
                    name="Complexity Analysis",
                    description="Calculate complexity metrics",
                    level=9
                ),
                AgentCapability(
                    name="Code Smell Detection",
                    description="Identify anti-patterns",
                    level=9
                ),
                AgentCapability(
                    name="Dependency Analysis",
                    description="Map dependency graphs",
                    level=8
                ),
                AgentCapability(
                    name="Performance Analysis",
                    description="Identify performance issues",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 principles
            system_instructions=CODE_ANALYZER_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Code smell patterns
        self.code_smells = {
            "long_function": {"threshold": 60, "severity": 8},
            "too_many_params": {"threshold": 5, "severity": 6},
            "deep_nesting": {"threshold": 4, "severity": 7},
            "magic_numbers": {"pattern": r'\b\d{2,}\b', "severity": 5},
            "TODO_comments": {"pattern": r'#\s*TODO', "severity": 4}
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

        # Code-analyzer specific validation
        if task.type == "analyze-code":
            errors.extend(self._validate_analyze_payload(task))

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
            if task.type == "analyze-code":
                result_data = await self._execute_analyze_code(task)
            elif task.type == "detect-complexity":
                result_data = await self._execute_detect_complexity(task)
            elif task.type == "detect-duplicates":
                result_data = await self._execute_detect_duplicates(task)
            elif task.type == "analyze-dependencies":
                result_data = await self._execute_analyze_dependencies(task)
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

    async def _execute_analyze_code(self, task: Task) -> Dict[str, Any]:
        """
        Perform full code analysis.

        Args:
            task: Analyze-code task

        Returns:
            Analysis result
        """
        target_path = task.payload.get("path")

        self.log_info(f"Analyzing code at: {target_path}")

        # Parse code
        ast_tree, code_content = self._parse_ast(target_path)

        if ast_tree is None:
            return {
                "path": target_path,
                "analyzed": False,
                "error": "Failed to parse code"
            }

        # Calculate complexity
        complexity = self._calculate_complexity(ast_tree, code_content)

        # Detect code smells
        smells = self._detect_code_smells(ast_tree, code_content)

        # Generate metrics
        metrics = ComplexityMetrics(
            cyclomatic_complexity=complexity["cyclomatic"],
            cognitive_complexity=complexity["cognitive"],
            lines_of_code=complexity["loc"],
            comment_ratio=complexity["comment_ratio"],
            function_count=complexity["function_count"],
            class_count=complexity["class_count"]
        )

        return {
            "path": target_path,
            "analyzed": True,
            "metrics": metrics.__dict__,
            "smells_detected": len(smells),
            "smells": [smell.__dict__ for smell in smells],
            "quality_score": self._calculate_quality_score(
                metrics,
                smells
            )
        }

    async def _execute_detect_complexity(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Detect cyclomatic complexity.

        Args:
            task: Detect-complexity task

        Returns:
            Complexity result
        """
        file_path = task.payload.get("file_path")

        self.log_info(f"Detecting complexity: {file_path}")

        ast_tree, code_content = self._parse_ast(file_path)

        if ast_tree is None:
            return {
                "file_path": file_path,
                "error": "Failed to parse file"
            }

        # Calculate per-function complexity
        function_complexity = {}

        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                function_complexity[node.name] = complexity

        return {
            "file_path": file_path,
            "function_count": len(function_complexity),
            "average_complexity": sum(function_complexity.values()) / len(
                function_complexity
            ) if function_complexity else 0,
            "max_complexity": max(
                function_complexity.values()
            ) if function_complexity else 0,
            "function_complexity": function_complexity
        }

    async def _execute_detect_duplicates(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Detect code duplicates.

        Args:
            task: Detect-duplicates task

        Returns:
            Duplication result
        """
        target_dir = task.payload.get("directory")

        self.log_info(f"Detecting duplicates in: {target_dir}")

        # Find Python files
        py_files = list(Path(target_dir).rglob("*.py"))

        duplicates = []

        # Compare files (simplified)
        for i, file1 in enumerate(py_files):
            for file2 in py_files[i + 1:]:
                similarity = self._calculate_similarity(file1, file2)
                if similarity > 0.7:  # 70% similar
                    duplicates.append(DuplicationResult(
                        file1=str(file1),
                        file2=str(file2),
                        duplicate_lines=0,  # Would calculate actual lines
                        similarity_score=similarity
                    ))

        return {
            "directory": target_dir,
            "files_analyzed": len(py_files),
            "duplicates_found": len(duplicates),
            "duplicates": [dup.__dict__ for dup in duplicates]
        }

    async def _execute_analyze_dependencies(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Analyze code dependencies.

        Args:
            task: Analyze-dependencies task

        Returns:
            Dependency analysis result
        """
        file_path = task.payload.get("file_path")

        self.log_info(f"Analyzing dependencies: {file_path}")

        imports = self._extract_imports(file_path)

        # Categorize imports
        stdlib_imports = []
        third_party_imports = []
        local_imports = []

        for imp in imports:
            if self._is_stdlib(imp):
                stdlib_imports.append(imp)
            elif imp.startswith('.') or imp.startswith('src'):
                local_imports.append(imp)
            else:
                third_party_imports.append(imp)

        return {
            "file_path": file_path,
            "total_imports": len(imports),
            "stdlib_count": len(stdlib_imports),
            "third_party_count": len(third_party_imports),
            "local_count": len(local_imports),
            "imports": {
                "stdlib": stdlib_imports,
                "third_party": third_party_imports,
                "local": local_imports
            }
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _parse_ast(self, file_path: str) -> tuple[Optional[ast.AST], str]:
        """Parse file into AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            return tree, content

        except Exception as e:
            self.log_error(f"Failed to parse {file_path}", exc=e)
            return None, ""

    def _calculate_complexity(
        self,
        tree: ast.AST,
        content: str
    ) -> Dict[str, Any]:
        """Calculate complexity metrics."""
        lines = content.split('\n')
        code_lines = [
            l for l in lines
            if l.strip() and not l.strip().startswith('#')
        ]
        comment_lines = [l for l in lines if l.strip().startswith('#')]

        function_count = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        )
        class_count = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        )

        # Calculate cyclomatic complexity
        cyclomatic = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                cyclomatic += 1
            elif isinstance(node, ast.BoolOp):
                cyclomatic += len(node.values) - 1

        return {
            "cyclomatic": cyclomatic,
            "cognitive": cyclomatic,  # Simplified
            "loc": len(code_lines),
            "comment_ratio": len(comment_lines) / len(lines) if lines else 0,
            "function_count": function_count,
            "class_count": class_count
        }

    def _calculate_cyclomatic_complexity(
        self,
        func_node: ast.FunctionDef
    ) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _detect_code_smells(
        self,
        tree: ast.AST,
        content: str
    ) -> List[CodeSmell]:
        """Detect code smells."""
        smells = []

        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno + 1
                if length > self.code_smells["long_function"]["threshold"]:
                    smells.append(CodeSmell(
                        smell_type="long_function",
                        severity=self.code_smells["long_function"]["severity"],
                        location=f"{node.name}:{node.lineno}",
                        description=f"Function too long ({length} lines)",
                        suggestion="Refactor into smaller functions"
                    ))

        # Check for TODO comments
        if re.search(self.code_smells["TODO_comments"]["pattern"], content):
            smells.append(CodeSmell(
                smell_type="TODO_comment",
                severity=self.code_smells["TODO_comments"]["severity"],
                location="various",
                description="TODO comments found",
                suggestion="Complete or remove TODO items"
            ))

        return smells

    def _calculate_quality_score(
        self,
        metrics: ComplexityMetrics,
        smells: List[CodeSmell]
    ) -> float:
        """Calculate overall quality score."""
        score = 100.0

        # Deduct for complexity
        if metrics.cyclomatic_complexity > 20:
            score -= 20
        elif metrics.cyclomatic_complexity > 10:
            score -= 10

        # Deduct for smells
        for smell in smells:
            score -= smell.severity

        # Bonus for good comment ratio
        if metrics.comment_ratio > 0.1:
            score += 5

        return max(0.0, min(100.0, score))

    def _calculate_similarity(
        self,
        file1: Path,
        file2: Path
    ) -> float:
        """Calculate code similarity between two files."""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                content1 = set(f.read().split())

            with open(file2, 'r', encoding='utf-8') as f:
                content2 = set(f.read().split())

            intersection = len(content1 & content2)
            union = len(content1 | content2)

            return intersection / union if union > 0 else 0.0

        except Exception:
            return 0.0

    def _extract_imports(self, file_path: str) -> List[str]:
        """Extract import statements."""
        imports = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception as e:
            self.log_error(f"Failed to extract imports from {file_path}", exc=e)

        return imports

    def _is_stdlib(self, module_name: str) -> bool:
        """Check if module is from standard library."""
        stdlib_modules = {
            'os', 'sys', 'time', 'datetime', 'json', 'math', 're',
            'typing', 'pathlib', 'logging', 'collections', 'dataclasses'
        }
        return module_name.split('.')[0] in stdlib_modules

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_analyze_payload(self, task: Task) -> List[ValidationError]:
        """Validate analyze-code task payload."""
        errors = []

        if "path" not in task.payload:
            errors.append(ValidationError(
                field="payload.path",
                message="Analyze task requires 'path' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_code_analyzer_agent() -> CodeAnalyzerAgent:
    """
    Create Code-Analyzer Agent instance.

    Returns:
        CodeAnalyzerAgent
    """
    return CodeAnalyzerAgent()
