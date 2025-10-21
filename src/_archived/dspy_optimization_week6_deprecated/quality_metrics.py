"""
Quality Metrics Definitions for Agent Optimization

Defines specific quality metrics for each P0 agent type to measure
optimization effectiveness and calculate ROI.

Week 6 Day 2
Version: 8.0.0
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class MetricType(Enum):
    """Types of quality metrics."""
    ACCURACY = "accuracy"  # Correctness (0-100%)
    COMPLETENESS = "completeness"  # Coverage (0-100%)
    EFFICIENCY = "efficiency"  # Speed/resource usage
    RELEVANCE = "relevance"  # Appropriateness (0-100%)


@dataclass
class QualityMetric:
    """Definition of a quality metric."""
    name: str
    metric_type: MetricType
    description: str
    weight: float  # 0-1 (importance for overall quality score)
    target_value: float  # Target to achieve
    baseline_value: float = 0.0  # Baseline before optimization

    def calculate_improvement_pct(self, current_value: float) -> float:
        """Calculate improvement percentage over baseline."""
        if self.baseline_value == 0:
            return 0.0
        return ((current_value - self.baseline_value) / self.baseline_value) * 100


# Queen Agent Quality Metrics
QUEEN_METRICS = [
    QualityMetric(
        name="task_decomposition_accuracy",
        metric_type=MetricType.ACCURACY,
        description="Accuracy of breaking down complex tasks into subtasks",
        weight=0.3,
        target_value=90.0
    ),
    QualityMetric(
        name="agent_selection_precision",
        metric_type=MetricType.ACCURACY,
        description="Precision in selecting appropriate agents for subtasks",
        weight=0.25,
        target_value=95.0
    ),
    QualityMetric(
        name="workflow_completeness",
        metric_type=MetricType.COMPLETENESS,
        description="Completeness of workflow coverage (no missing steps)",
        weight=0.25,
        target_value=95.0
    ),
    QualityMetric(
        name="coordination_efficiency",
        metric_type=MetricType.EFFICIENCY,
        description="Efficiency of agent coordination (minimize overhead)",
        weight=0.2,
        target_value=85.0
    )
]

# Tester Agent Quality Metrics
TESTER_METRICS = [
    QualityMetric(
        name="test_coverage_quality",
        metric_type=MetricType.COMPLETENESS,
        description="Quality of test coverage (happy path + edge cases + errors)",
        weight=0.3,
        target_value=90.0
    ),
    QualityMetric(
        name="edge_case_detection_rate",
        metric_type=MetricType.ACCURACY,
        description="Percentage of edge cases identified and tested",
        weight=0.25,
        target_value=85.0
    ),
    QualityMetric(
        name="assertion_relevance",
        metric_type=MetricType.RELEVANCE,
        description="Relevance and effectiveness of test assertions",
        weight=0.25,
        target_value=90.0
    ),
    QualityMetric(
        name="test_generation_efficiency",
        metric_type=MetricType.EFFICIENCY,
        description="Speed and resource efficiency of test generation",
        weight=0.2,
        target_value=85.0
    )
]

# Reviewer Agent Quality Metrics
REVIEWER_METRICS = [
    QualityMetric(
        name="bug_detection_rate",
        metric_type=MetricType.ACCURACY,
        description="Percentage of bugs/issues detected in code",
        weight=0.3,
        target_value=90.0
    ),
    QualityMetric(
        name="code_quality_assessment_accuracy",
        metric_type=MetricType.ACCURACY,
        description="Accuracy of code quality assessment",
        weight=0.25,
        target_value=85.0
    ),
    QualityMetric(
        name="review_completeness",
        metric_type=MetricType.COMPLETENESS,
        description="Thoroughness of code review (all aspects covered)",
        weight=0.25,
        target_value=90.0
    ),
    QualityMetric(
        name="false_positive_rate",
        metric_type=MetricType.ACCURACY,
        description="Rate of false positive issues (lower is better, inverted)",
        weight=0.2,
        target_value=95.0  # 95% means only 5% false positives
    )
]

# Coder Agent Quality Metrics
CODER_METRICS = [
    QualityMetric(
        name="code_generation_quality",
        metric_type=MetricType.ACCURACY,
        description="Overall quality of generated code (correctness + style)",
        weight=0.3,
        target_value=90.0
    ),
    QualityMetric(
        name="pattern_application_correctness",
        metric_type=MetricType.ACCURACY,
        description="Correctness of design pattern application",
        weight=0.25,
        target_value=90.0
    ),
    QualityMetric(
        name="type_safety_score",
        metric_type=MetricType.ACCURACY,
        description="Type safety and hint completeness",
        weight=0.25,
        target_value=95.0
    ),
    QualityMetric(
        name="compilation_success_rate",
        metric_type=MetricType.ACCURACY,
        description="Percentage of generated code that compiles/runs without errors",
        weight=0.2,
        target_value=95.0
    )
]

# All metrics mapped by agent
ALL_METRICS: Dict[str, List[QualityMetric]] = {
    "queen": QUEEN_METRICS,
    "tester": TESTER_METRICS,
    "reviewer": REVIEWER_METRICS,
    "coder": CODER_METRICS
}


@dataclass
class QualityScore:
    """Overall quality score for an agent."""
    agent_id: str
    overall_score: float  # 0-100
    metric_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""

    def calculate_improvement(self, baseline_score: float) -> float:
        """Calculate improvement over baseline."""
        if baseline_score == 0:
            return 0.0
        return ((self.overall_score - baseline_score) / baseline_score) * 100


class QualityCalculator:
    """Calculates quality scores for agents."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.metrics = ALL_METRICS.get(agent_id, [])

    def calculate_overall_score(self, metric_values: Dict[str, float]) -> QualityScore:
        """
        Calculate overall quality score from individual metrics.

        Args:
            metric_values: Dict of metric_name -> value (0-100)

        Returns:
            QualityScore with overall and individual scores
        """
        if not self.metrics:
            return QualityScore(agent_id=self.agent_id, overall_score=0.0)

        # Calculate weighted average
        total_weight = sum(m.weight for m in self.metrics)
        weighted_sum = 0.0

        for metric in self.metrics:
            value = metric_values.get(metric.name, 0.0)
            weighted_sum += value * metric.weight

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0

        return QualityScore(
            agent_id=self.agent_id,
            overall_score=overall,
            metric_scores=metric_values.copy()
        )

    def get_metric_targets(self) -> Dict[str, float]:
        """Get target values for all metrics."""
        return {m.name: m.target_value for m in self.metrics}

    def get_metric_weights(self) -> Dict[str, float]:
        """Get weights for all metrics."""
        return {m.name: m.weight for m in self.metrics}


def get_agent_metrics(agent_id: str) -> List[QualityMetric]:
    """Get quality metrics for a specific agent."""
    return ALL_METRICS.get(agent_id, [])


def create_quality_calculator(agent_id: str) -> QualityCalculator:
    """Factory function to create quality calculator."""
    return QualityCalculator(agent_id=agent_id)


# Metric definitions summary
METRICS_SUMMARY = """
Quality Metrics Summary
=======================

Queen Agent (4 metrics):
1. task_decomposition_accuracy (30%): Accuracy of task breakdown -> 90% target
2. agent_selection_precision (25%): Precision in agent selection -> 95% target
3. workflow_completeness (25%): Workflow coverage -> 95% target
4. coordination_efficiency (20%): Coordination efficiency -> 85% target

Tester Agent (4 metrics):
1. test_coverage_quality (30%): Test coverage quality -> 90% target
2. edge_case_detection_rate (25%): Edge case detection -> 85% target
3. assertion_relevance (25%): Assertion effectiveness -> 90% target
4. test_generation_efficiency (20%): Generation efficiency -> 85% target

Reviewer Agent (4 metrics):
1. bug_detection_rate (30%): Bug detection percentage -> 90% target
2. code_quality_assessment_accuracy (25%): Assessment accuracy -> 85% target
3. review_completeness (25%): Review thoroughness -> 90% target
4. false_positive_rate (20%): False positives (inverted) -> 95% target

Coder Agent (4 metrics):
1. code_generation_quality (30%): Overall code quality -> 90% target
2. pattern_application_correctness (25%): Pattern correctness -> 90% target
3. type_safety_score (25%): Type safety -> 95% target
4. compilation_success_rate (20%): Compilation success -> 95% target
"""


if __name__ == "__main__":
    print(METRICS_SUMMARY)

    # Test quality calculator
    print("\nQuality Calculator Test:")
    print("="*80)

    calc = create_quality_calculator("queen")

    # Example metric values
    test_values = {
        "task_decomposition_accuracy": 85.0,
        "agent_selection_precision": 90.0,
        "workflow_completeness": 88.0,
        "coordination_efficiency": 80.0
    }

    score = calc.calculate_overall_score(test_values)

    print(f"\nAgent: {score.agent_id}")
    print(f"Overall Score: {score.overall_score:.1f}/100")
    print("\nIndividual Metrics:")
    for name, value in score.metric_scores.items():
        print(f"  {name}: {value:.1f}")

    # Calculate improvement
    baseline = 70.0
    improvement = score.calculate_improvement(baseline)
    print(f"\nImprovement over baseline ({baseline}): {improvement:+.1f}%")
