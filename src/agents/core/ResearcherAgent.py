"""
ResearcherAgent - Research and Analysis Specialist

Conducts research and gathers information:
- Search and analyze documentation
- Gather requirements and specifications
- Research best practices and patterns
- Provide recommendations based on findings

Part of core agent roster (Week 5 Day 6).

Week 5 Day 6
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
from src.agents.instructions import RESEARCHER_SYSTEM_INSTRUCTIONS


# ============================================================================
# Researcher-Specific Types
# ============================================================================

@dataclass
class ResearchFinding:
    """Single research finding."""
    source: str
    summary: str
    relevance_score: float
    key_points: List[str]


@dataclass
class ResearchReport:
    """Complete research report."""
    topic: str
    findings: List[ResearchFinding]
    recommendations: List[str]
    confidence_score: float


# ============================================================================
# ResearcherAgent Class
# ============================================================================

class ResearcherAgent(AgentBase):
    """
    Researcher Agent - Research and analysis specialist.

    Responsibilities:
    - Conduct research on topics
    - Analyze documentation and code
    - Gather requirements
    - Provide recommendations
    """

    def __init__(self):
        """Initialize Researcher Agent."""
        metadata = create_agent_metadata(
            agent_id="researcher",
            name="Research and Analysis Specialist",
            agent_type=AgentType.CORE,
            supported_task_types=[
                "research-topic",
                "analyze-codebase",
                "gather-requirements",
                "find-best-practices"
            ],
            capabilities=[
                AgentCapability(
                    name="Research and Investigation",
                    description="Research topics and gather information",
                    level=10
                ),
                AgentCapability(
                    name="Code Analysis",
                    description="Analyze codebase structure and patterns",
                    level=9
                ),
                AgentCapability(
                    name="Requirements Gathering",
                    description="Gather and document requirements",
                    level=9
                ),
                AgentCapability(
                    name="Best Practices",
                    description="Research industry best practices",
                    level=8
                ),
                AgentCapability(
                    name="Recommendations",
                    description="Provide actionable recommendations",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=RESEARCHER_SYSTEM_INSTRUCTIONS.to_prompt()
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

        # Researcher-specific validation
        if task.type == "research-topic":
            errors.extend(self._validate_research_payload(task))

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
            if task.type == "research-topic":
                result_data = await self._execute_research(task)
            elif task.type == "analyze-codebase":
                result_data = await self._execute_analyze_codebase(task)
            elif task.type == "gather-requirements":
                result_data = await self._execute_gather_requirements(task)
            elif task.type == "find-best-practices":
                result_data = await self._execute_find_best_practices(task)
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

    async def _execute_research(self, task: Task) -> Dict[str, Any]:
        """
        Research topic and gather information.

        Args:
            task: Research-topic task

        Returns:
            Research result
        """
        topic = task.payload.get("topic")
        depth = task.payload.get("depth", "medium")

        self.log_info(f"Researching topic: {topic} (depth: {depth})")

        # Gather findings from various sources
        findings = self._gather_findings(topic, depth)

        # Generate recommendations
        recommendations = self._generate_recommendations(findings)

        # Calculate confidence score
        confidence = self._calculate_confidence(findings)

        # Create research report
        report = ResearchReport(
            topic=topic,
            findings=findings,
            recommendations=recommendations,
            confidence_score=confidence
        )

        return {
            "topic": topic,
            "finding_count": len(findings),
            "recommendation_count": len(recommendations),
            "confidence_score": confidence,
            "report": report.__dict__
        }

    async def _execute_analyze_codebase(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Analyze codebase structure."""
        codebase_path = task.payload.get("codebase_path", "src/")

        self.log_info(f"Analyzing codebase: {codebase_path}")

        # Collect files
        files = self._collect_python_files(codebase_path)

        # Analyze structure
        structure = self._analyze_structure(files)

        return {
            "codebase_path": codebase_path,
            "file_count": len(files),
            "total_loc": structure["total_loc"],
            "structure": structure
        }

    async def _execute_gather_requirements(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Gather requirements from stakeholders."""
        stakeholder = task.payload.get("stakeholder", "user")

        self.log_info(f"Gathering requirements from {stakeholder}")

        requirements = [
            "System must handle 200+ concurrent users",
            "Response time <100ms for critical operations",
            "Test coverage >=80%",
            "NASA Rule 10 compliance >=92%"
        ]

        return {
            "stakeholder": stakeholder,
            "requirement_count": len(requirements),
            "requirements": requirements
        }

    async def _execute_find_best_practices(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Find best practices for topic."""
        topic = task.payload.get("topic", "python")

        self.log_info(f"Finding best practices for {topic}")

        best_practices = [
            "Use type hints for all function signatures",
            "Follow PEP 8 style guide",
            "Write comprehensive docstrings",
            "Maintain functions <=60 LOC (NASA Rule 10)",
            "Use dataclasses for DTOs"
        ]

        return {
            "topic": topic,
            "practice_count": len(best_practices),
            "best_practices": best_practices
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _gather_findings(
        self,
        topic: str,
        depth: str
    ) -> List[ResearchFinding]:
        """Gather research findings."""
        findings = []

        # Simulate research findings
        if depth in ["medium", "deep"]:
            findings.append(ResearchFinding(
                source="Documentation",
                summary=f"Official documentation for {topic}",
                relevance_score=0.9,
                key_points=[
                    f"{topic} supports async operations",
                    f"{topic} has built-in type checking",
                    f"{topic} follows industry standards"
                ]
            ))

        if depth == "deep":
            findings.append(ResearchFinding(
                source="Best Practices",
                summary=f"Industry best practices for {topic}",
                relevance_score=0.8,
                key_points=[
                    "Use design patterns appropriately",
                    "Follow SOLID principles",
                    "Implement comprehensive testing"
                ]
            ))

        return findings

    def _generate_recommendations(
        self,
        findings: List[ResearchFinding]
    ) -> List[str]:
        """Generate recommendations from findings."""
        recommendations = []

        for finding in findings:
            if finding.relevance_score > 0.7:
                recommendations.extend(finding.key_points)

        return recommendations[:5]  # Top 5 recommendations

    def _calculate_confidence(
        self,
        findings: List[ResearchFinding]
    ) -> float:
        """Calculate confidence score."""
        if not findings:
            return 0.0

        avg_relevance = sum(
            f.relevance_score for f in findings
        ) / len(findings)

        return avg_relevance * 100  # Convert to percentage

    def _collect_python_files(self, path: str) -> List[str]:
        """Collect Python files in directory."""
        path_obj = Path(path)

        if not path_obj.exists():
            return []

        if path_obj.is_file():
            return [str(path_obj)]

        return [str(f) for f in path_obj.rglob("*.py")]

    def _analyze_structure(self, files: List[str]) -> Dict[str, Any]:
        """Analyze codebase structure."""
        total_loc = 0
        total_functions = 0
        total_classes = 0

        for file_path in files:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_loc += len([
                        l for l in lines
                        if l.strip() and not l.strip().startswith('#')
                    ])

        return {
            "total_loc": total_loc,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "file_count": len(files)
        }

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_research_payload(
        self,
        task: Task
    ) -> List[ValidationError]:
        """Validate research-topic task payload."""
        errors = []

        if "topic" not in task.payload:
            errors.append(ValidationError(
                field="payload.topic",
                message="Research task requires 'topic' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_researcher_agent() -> ResearcherAgent:
    """
    Create Researcher Agent instance.

    Returns:
        ResearcherAgent
    """
    return ResearcherAgent()
