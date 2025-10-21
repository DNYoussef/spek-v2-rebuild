"""
DSPy Optimizer Configuration

Configuration for DSPy optimization of SPEK agents.
Defines P0 and P1 agent priorities and optimization parameters.

Week 6 Day 1
Version: 8.0.0
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class AgentPriority(Enum):
    """Agent optimization priority levels."""
    P0 = "p0"  # Critical agents (must optimize)
    P1 = "p1"  # Optional agents (optimize if ROI proven)
    P2 = "p2"  # Low priority (future optimization)


@dataclass
class OptimizerConfig:
    """Configuration for DSPy optimizer."""

    # Gemini free tier configuration
    gemini_model: str = "gemini-1.5-flash"
    gemini_api_key: str = ""  # Set via environment variable
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048

    # Optimization parameters
    training_iterations: int = 100
    validation_split: float = 0.2
    batch_size: int = 16
    learning_rate: float = 0.001

    # Quality targets
    min_quality_improvement_pct: float = 10.0  # Minimum 10% improvement
    target_quality_score: float = 85.0  # Target quality score (0-100)

    # Performance targets
    max_validation_time_ms: float = 5.0
    max_execution_time_ms: float = 100.0
    min_throughput_tasks_per_sec: float = 10.0

    # Cost tracking
    max_training_cost_usd: float = 0.0  # Gemini free tier
    max_inference_cost_per_task_usd: float = 0.0


@dataclass
class AgentOptimizationPlan:
    """Optimization plan for a specific agent."""
    agent_id: str
    priority: AgentPriority
    optimization_goals: List[str] = field(default_factory=list)
    training_dataset_size: int = 1000
    evaluation_metrics: List[str] = field(default_factory=list)

    # Baseline metrics (filled after baseline collection)
    baseline_quality_score: float = 0.0
    baseline_execution_time_ms: float = 0.0
    baseline_success_rate: float = 0.0

    # Target metrics
    target_quality_score: float = 0.0
    target_execution_time_ms: float = 0.0
    target_success_rate: float = 95.0


# P0 Agents (Critical - Must Optimize)
P0_AGENTS = {
    "queen": AgentOptimizationPlan(
        agent_id="queen",
        priority=AgentPriority.P0,
        optimization_goals=[
            "Improve task decomposition quality",
            "Optimize agent selection accuracy",
            "Enhance result aggregation",
            "Reduce coordination latency"
        ],
        evaluation_metrics=[
            "task_decomposition_accuracy",
            "agent_selection_precision",
            "result_aggregation_quality",
            "coordination_latency_ms"
        ]
    ),
    "tester": AgentOptimizationPlan(
        agent_id="tester",
        priority=AgentPriority.P0,
        optimization_goals=[
            "Increase test coverage quality",
            "Improve edge case detection",
            "Optimize test generation speed",
            "Enhance assertion quality"
        ],
        evaluation_metrics=[
            "test_coverage_percentage",
            "edge_case_detection_rate",
            "test_generation_time_ms",
            "assertion_relevance_score"
        ]
    ),
    "reviewer": AgentOptimizationPlan(
        agent_id="reviewer",
        priority=AgentPriority.P0,
        optimization_goals=[
            "Improve code quality assessment accuracy",
            "Enhance bug detection rate",
            "Optimize review thoroughness",
            "Reduce false positives"
        ],
        evaluation_metrics=[
            "code_quality_accuracy",
            "bug_detection_rate",
            "review_completeness_score",
            "false_positive_rate"
        ]
    ),
    "coder": AgentOptimizationPlan(
        agent_id="coder",
        priority=AgentPriority.P0,
        optimization_goals=[
            "Improve code generation quality",
            "Enhance pattern application accuracy",
            "Optimize type safety",
            "Reduce compilation errors"
        ],
        evaluation_metrics=[
            "code_generation_quality",
            "pattern_correctness",
            "type_safety_score",
            "compilation_success_rate"
        ]
    )
}

# P1 Agents (Optional - Optimize if ROI Proven)
P1_AGENTS = {
    "researcher": AgentOptimizationPlan(
        agent_id="researcher",
        priority=AgentPriority.P1,
        optimization_goals=[
            "Improve research relevance",
            "Enhance source credibility assessment",
            "Optimize search efficiency"
        ],
        evaluation_metrics=[
            "research_relevance_score",
            "source_credibility_rating",
            "search_efficiency"
        ]
    ),
    "architect": AgentOptimizationPlan(
        agent_id="architect",
        priority=AgentPriority.P1,
        optimization_goals=[
            "Improve architecture design quality",
            "Enhance scalability assessment",
            "Optimize pattern selection"
        ],
        evaluation_metrics=[
            "architecture_quality_score",
            "scalability_rating",
            "pattern_appropriateness"
        ]
    ),
    "spec-writer": AgentOptimizationPlan(
        agent_id="spec-writer",
        priority=AgentPriority.P1,
        optimization_goals=[
            "Improve specification completeness",
            "Enhance requirement clarity",
            "Optimize edge case coverage"
        ],
        evaluation_metrics=[
            "specification_completeness",
            "requirement_clarity_score",
            "edge_case_coverage"
        ]
    ),
    "debugger": AgentOptimizationPlan(
        agent_id="debugger",
        priority=AgentPriority.P1,
        optimization_goals=[
            "Improve root cause identification",
            "Enhance fix quality",
            "Optimize debugging speed"
        ],
        evaluation_metrics=[
            "root_cause_accuracy",
            "fix_effectiveness",
            "debugging_time_ms"
        ]
    )
}

# All optimization plans
ALL_OPTIMIZATION_PLANS = {**P0_AGENTS, **P1_AGENTS}


def get_optimizer_config() -> OptimizerConfig:
    """Get default optimizer configuration."""
    return OptimizerConfig()


def get_p0_agents() -> Dict[str, AgentOptimizationPlan]:
    """Get P0 agent optimization plans."""
    return P0_AGENTS.copy()


def get_p1_agents() -> Dict[str, AgentOptimizationPlan]:
    """Get P1 agent optimization plans."""
    return P1_AGENTS.copy()


def get_optimization_plan(agent_id: str) -> AgentOptimizationPlan:
    """Get optimization plan for specific agent."""
    return ALL_OPTIMIZATION_PLANS.get(agent_id)
