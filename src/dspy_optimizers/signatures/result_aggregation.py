"""
Result Aggregation Signature

Used for Drone → Princess communication where multiple drone results
must be aggregated into a coherent princess-level result.

Week 21 Day 3
Version: 1.0.0
"""

import dspy


class ResultAggregationSignature(dspy.Signature):
    """
    Aggregate drone results into coherent princess-level output.

    You are a Princess agent receiving results from multiple drone agents
    that executed tasks in parallel or sequence. Your role is to combine
    their individual results into a unified, comprehensive result that
    can be reported to the Queen.

    Aggregation must include:
    - Success/failure status of overall workflow
    - Quality metrics from all drones
    - Validation against quality gates
    - Artifacts produced by drones
    - Recommendations or next steps

    Follow the 26 prompt engineering principles:
    - Completeness: Include all relevant drone outputs
    - Quality: Validate against gates (test coverage, NASA compliance, etc.)
    - Clarity: Summarize complex results clearly
    - Structure: Output valid JSON format
    """

    drone_results = dspy.InputField(
        desc="List of results from drone agents (each with success, data, metrics)"
    )
    quality_gates = dspy.InputField(
        desc="Quality gates to validate against (e.g., test_coverage >= 80%)"
    )

    reasoning = dspy.OutputField(
        desc="Aggregation reasoning explaining how results were combined and validated",
        prefix="Reasoning: Let's think step by step in order to"
    )

    aggregated_result = dspy.OutputField(
        desc=(
            "Aggregated result as JSON object. "
            "Must have: "
            "{'success': bool, 'overall_score': float, 'gates_passed': int, "
            "'gates_failed': int, 'artifacts': list[str], 'recommendations': list[str]}"
        )
    )
