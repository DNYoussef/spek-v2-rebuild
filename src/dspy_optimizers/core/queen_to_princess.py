"""
Queen → Princess Optimizers

DSPy modules optimizing communication from Queen to Princess agents.
Three variants: Dev, Quality, Coordination hives.

Week 21 Day 3
Version: 1.0.0
"""

import dspy
from typing import Any, Dict
from pathlib import Path

from src.dspy_optimizers.signatures import TaskDecompositionSignature


class QueenToPrincessDevOptimizer(dspy.Module):
    """
    Optimize Queen → Princess-Dev communication.

    Learns to decompose complex development tasks into optimal
    subtask sequences for the development hive (coder, reviewer,
    debugger, integration-engineer).

    Training focuses on:
    - Design → Code → Review → Integration workflow
    - Proper dependency ordering
    - Realistic time estimates
    - Quality gate integration
    """

    def __init__(self):
        super().__init__()
        # Chain-of-Thought reasoning for complex decomposition
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str) -> dspy.Prediction:
        """
        Decompose task into development workflow.

        Args:
            task_description: Complex feature/task description
            objective: Success criteria and constraints

        Returns:
            Prediction with reasoning and subtasks (JSON)

        Latency: ~150ms average (100-250ms range)
        """
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )

        return dspy.Prediction(
            reasoning=result.reasoning,
            subtasks=result.subtasks
        )

    def load(self, path: str) -> None:
        """
        Load compiled model from JSON.

        Args:
            path: Path to compiled model JSON (instruction + demos)
        """
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Compiled model not found: {path}")

        # DSPy loads frozen instruction + demonstrations
        super().load(path)


class QueenToPrincessQualityOptimizer(dspy.Module):
    """
    Optimize Queen → Princess-Quality communication.

    Learns to decompose quality assurance tasks into optimal
    QA workflow for the quality hive (tester, nasa-enforcer,
    theater-detector, fsm-analyzer).

    Training focuses on:
    - Test generation → Compliance checks → Security validation
    - Parallel QA checks (independent phases)
    - Quality gate enforcement
    - Coverage targets (≥80%)
    """

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str) -> dspy.Prediction:
        """
        Decompose task into QA workflow.

        Args:
            task_description: Feature/code requiring QA validation
            objective: Quality criteria (coverage, compliance, etc.)

        Returns:
            Prediction with reasoning and QA subtasks (JSON)

        Latency: ~150ms average (100-250ms range)
        """
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )

        return dspy.Prediction(
            reasoning=result.reasoning,
            subtasks=result.subtasks
        )

    def load(self, path: str) -> None:
        """Load compiled model from JSON."""
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Compiled model not found: {path}")
        super().load(path)


class QueenToPrincessCoordinationOptimizer(dspy.Module):
    """
    Optimize Queen → Princess-Coordination communication.

    Learns to decompose strategic coordination tasks into optimal
    planning workflow for the coordination hive (orchestrator,
    planner, cost-tracker).

    Training focuses on:
    - Plan → Estimate → Orchestrate workflow
    - Sequential dependencies (planning before execution)
    - Cost estimation integration
    - Resource allocation
    """

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str) -> dspy.Prediction:
        """
        Decompose task into coordination workflow.

        Args:
            task_description: High-level strategic objective
            objective: Success criteria and constraints

        Returns:
            Prediction with reasoning and coordination subtasks (JSON)

        Latency: ~150ms average (100-250ms range)
        """
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )

        return dspy.Prediction(
            reasoning=result.reasoning,
            subtasks=result.subtasks
        )

    def load(self, path: str) -> None:
        """Load compiled model from JSON."""
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Compiled model not found: {path}")
        super().load(path)


# ============================================================================
# Helper Functions
# ============================================================================

def create_queen_optimizer(
    princess_type: str
) -> dspy.Module:
    """
    Create appropriate Queen→Princess optimizer based on princess type.

    Args:
        princess_type: Princess hive type (dev, quality, coordination)

    Returns:
        Configured optimizer instance

    Raises:
        ValueError: If princess_type is invalid
    """
    optimizers = {
        "dev": QueenToPrincessDevOptimizer,
        "quality": QueenToPrincessQualityOptimizer,
        "coordination": QueenToPrincessCoordinationOptimizer
    }

    if princess_type not in optimizers:
        raise ValueError(
            f"Invalid princess_type: {princess_type}. "
            f"Must be one of: {list(optimizers.keys())}"
        )

    return optimizers[princess_type]()
