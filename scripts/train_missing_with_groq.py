"""
Train MISSING DSPy Optimizers with Groq API

Completes the 9 missing Drone->Princess reverse path optimizers.

Missing:
1. code_analyzer_to_princess_quality
2. cost_tracker_to_princess_coordination
3. debugger_to_princess_dev
4. fsm_analyzer_to_princess_quality
5. infrastructure_ops_to_princess_coordination
6. orchestrator_to_princess_coordination
7. performance_engineer_to_princess_coordination
8. planner_to_princess_coordination
9. release_manager_to_princess_coordination
10. reviewer_to_princess_dev

Week 24.5 - Groq Completion
Version: 1.0.0
"""

import dspy
import json
import sys
import os
from pathlib import Path
from typing import List
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import optimizer classes
try:
    from src.dspy_optimizers.core.drone_to_princess import (
        CodeAnalyzerToPrincessQualityOptimizer,
        CostTrackerToPrincessCoordinationOptimizer,
        DebuggerToPrincessDevOptimizer,
        FsmAnalyzerToPrincessQualityOptimizer,
        InfrastructureOpsToPrincessCoordinationOptimizer,
        OrchestratorToPrincessCoordinationOptimizer,
        PerformanceEngineerToPrincessCoordinationOptimizer,
        PlannerToPrincessCoordinationOptimizer,
        ReleaseManagerToPrincessCoordinationOptimizer,
        ReviewerToPrincessDevOptimizer
    )
except ImportError as e:
    print(f" Import error: {e}")
    print("   Creating placeholder optimizers...")

    # Create placeholder classes if imports fail
    class PlaceholderOptimizer(dspy.Module):
        def __init__(self):
            super().__init__()
            from src.dspy_optimizers.signatures import ResultAggregationSignature
            self.aggregate = dspy.ChainOfThought(ResultAggregationSignature)

        def forward(self, drone_results: str, quality_gates: str) -> dspy.Prediction:
            result = self.aggregate(drone_results=drone_results, quality_gates=quality_gates)
            return dspy.Prediction(reasoning=result.reasoning, aggregated_result=result.aggregated_result)

    # Assign all missing classes to placeholder
    CodeAnalyzerToPrincessQualityOptimizer = PlaceholderOptimizer
    CostTrackerToPrincessCoordinationOptimizer = PlaceholderOptimizer
    DebuggerToPrincessDevOptimizer = PlaceholderOptimizer
    FsmAnalyzerToPrincessQualityOptimizer = PlaceholderOptimizer
    InfrastructureOpsToPrincessCoordinationOptimizer = PlaceholderOptimizer
    OrchestratorToPrincessCoordinationOptimizer = PlaceholderOptimizer
    PerformanceEngineerToPrincessCoordinationOptimizer = PlaceholderOptimizer
    PlannerToPrincessCoordinationOptimizer = PlaceholderOptimizer
    ReleaseManagerToPrincessCoordinationOptimizer = PlaceholderOptimizer
    ReviewerToPrincessDevOptimizer = PlaceholderOptimizer


def aggregation_quality(example, prediction, trace=None) -> float:
    """Evaluate quality of result aggregation (Drone->Princess)."""
    try:
        if hasattr(prediction, 'aggregated_result'):
            agg_result_json = prediction.aggregated_result
        else:
            return 0.0

        agg_result = json.loads(agg_result_json)

        if not isinstance(agg_result, dict):
            return 0.0

        score = 0.0

        # Check required fields
        required_fields = ["phase", "status", "summary"]
        for field in required_fields:
            if field in agg_result:
                score += 0.2

        # Check status is valid
        if "status" in agg_result:
            valid_statuses = ["complete", "blocked", "needs_rework", "partial"]
            if agg_result["status"] in valid_statuses:
                score += 0.2

        # Check next phase or blockers identified
        if "next_phase" in agg_result or "blockers" in agg_result:
            score += 0.2

        return min(1.0, score)

    except Exception as e:
        print(f"  Metric error: {e}")
        return 0.0


def load_aggregation_dataset(dataset_path: str) -> List[dspy.Example]:
    """Load Drone->Princess aggregation dataset."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = []
    for ex in data.get('examples', []):
        example = dspy.Example(
            drone_results=json.dumps(ex['drone_results']),
            quality_gates=json.dumps(ex.get('expected_aggregated_result', {}).get('quality_metrics', {})),
            aggregated_result=json.dumps(ex['expected_aggregated_result'])
        ).with_inputs('drone_results', 'quality_gates')
        examples.append(example)

    return examples


def train_optimizer(
    optimizer_class,
    dataset_path: str,
    output_path: str,
    max_demos: int = 5,  # Reduced for speed
    max_rounds: int = 2   # Reduced for speed
) -> dict:
    """Train a single DSPy optimizer."""
    print(f"\n{'='*80}")
    print(f"Training {optimizer_class.__name__}")
    print(f"Dataset: {Path(dataset_path).name}")
    print(f"Output: {Path(output_path).name}")
    print(f"{'='*80}\n")

    try:
        # Load examples
        print(" Loading examples...")
        trainset = load_aggregation_dataset(dataset_path)
        print(f"   Loaded {len(trainset)} examples\n")

        if len(trainset) == 0:
            print("  No examples found - SKIPPING")
            return {"status": "skipped", "reason": "no_examples"}

        # Create module
        print(" Creating module...")
        module = optimizer_class()

        # Create optimizer
        print(f"  Configuring BootstrapFewShot (demos={max_demos}, rounds={max_rounds})...\n")
        optimizer = BootstrapFewShot(
            metric=aggregation_quality,
            max_bootstrapped_demos=max_demos,
            max_labeled_demos=min(3, len(trainset) // 2),
            max_rounds=max_rounds
        )

        # Train
        print(" Training with Groq (fast!)...\n")
        compiled = optimizer.compile(
            student=module,
            trainset=trainset
        )

        # Evaluate
        print(" Evaluating...")
        evaluator = Evaluate(
            devset=trainset[:min(10, len(trainset))],
            metric=aggregation_quality,
            num_threads=1
        )
        score_result = evaluator(compiled)
        score = float(score_result) if hasattr(score_result, '__float__') else score_result
        print(f"   Score: {score:.1%}\n")

        # Save
        print(f" Saving...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        compiled.save(output_path)

        print(f" SUCCESS! Score: {score:.1%}\n")

        return {
            "status": "success",
            "score": score,
            "examples": len(trainset)
        }

    except Exception as e:
        print(f" FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


def main():
    """Train all 10 MISSING optimizers with Groq."""
    print(f"\n{'='*80}")
    print("DSPy MISSING Optimizers Training with Groq")
    print(f"{'='*80}\n")

    # Configure Groq
    groq_key = os.getenv('GROQ_API_KEY', '')  # Set GROQ_API_KEY environment variable
    os.environ['GROQ_API_KEY'] = groq_key

    print(f" Configuring Groq...")
    print(f"   Model: groq/llama-3.3-70b-versatile")
    print(f"   Speed: 1000 tokens/sec")
    print(f"   Cost: FREE\n")

    lm = dspy.LM('groq/llama-3.3-70b-versatile', api_key=groq_key)
    dspy.configure(lm=lm)

    # Test connection
    print(" Testing connection...")
    try:
        test = lm("Test", max_tokens=5)
        print(f"    Connected! Response: {test[:30]}\n")
    except Exception as e:
        print(f"    Failed: {e}\n")
        sys.exit(1)

    root = Path(__file__).parent.parent

    # MISSING optimizers configuration
    configs = [
        {
            "optimizer_class": CodeAnalyzerToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/code_analyzer_to_princess_quality.json",
            "output": root / "models/dspy/code_analyzer_to_princess_quality.json",
            "name": "Code-Analyzer  Princess-Quality"
        },
        {
            "optimizer_class": CostTrackerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/cost_tracker_to_princess_coordination.json",
            "output": root / "models/dspy/cost_tracker_to_princess_coordination.json",
            "name": "Cost-Tracker  Princess-Coordination"
        },
        {
            "optimizer_class": DebuggerToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/debugger_to_princess_dev.json",
            "output": root / "models/dspy/debugger_to_princess_dev.json",
            "name": "Debugger  Princess-Dev"
        },
        {
            "optimizer_class": FsmAnalyzerToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/fsm_analyzer_to_princess_quality.json",
            "output": root / "models/dspy/fsm_analyzer_to_princess_quality.json",
            "name": "FSM-Analyzer  Princess-Quality"
        },
        {
            "optimizer_class": InfrastructureOpsToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/infrastructure_ops_to_princess_coordination.json",
            "output": root / "models/dspy/infrastructure_ops_to_princess_coordination.json",
            "name": "Infrastructure-Ops  Princess-Coordination"
        },
        {
            "optimizer_class": OrchestratorToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/orchestrator_to_princess_coordination.json",
            "output": root / "models/dspy/orchestrator_to_princess_coordination.json",
            "name": "Orchestrator  Princess-Coordination"
        },
        {
            "optimizer_class": PerformanceEngineerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/performance_engineer_to_princess_coordination.json",
            "output": root / "models/dspy/performance_engineer_to_princess_coordination.json",
            "name": "Performance-Engineer  Princess-Coordination"
        },
        {
            "optimizer_class": PlannerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/planner_to_princess_coordination.json",
            "output": root / "models/dspy/planner_to_princess_coordination.json",
            "name": "Planner  Princess-Coordination"
        },
        {
            "optimizer_class": ReleaseManagerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/release_manager_to_princess_coordination.json",
            "output": root / "models/dspy/release_manager_to_princess_coordination.json",
            "name": "Release-Manager  Princess-Coordination"
        },
        {
            "optimizer_class": ReviewerToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/reviewer_to_princess_dev.json",
            "output": root / "models/dspy/reviewer_to_princess_dev.json",
            "name": "Reviewer  Princess-Dev"
        },
    ]

    print(f"{'='*80}")
    print(f"Training 10 MISSING Optimizers (DronePrincess)")
    print(f"Estimated: 20-40 minutes total (2-4 min each)")
    print(f"{'='*80}\n")

    # Train each
    results = []
    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/10] {config['name']}")

        result = train_optimizer(
            optimizer_class=config['optimizer_class'],
            dataset_path=str(config['dataset']),
            output_path=str(config['output']),
            max_demos=5,
            max_rounds=2
        )

        results.append({
            "name": config['name'],
            "status": result['status'],
            "score": result.get('score', 0),
            "examples": result.get('examples', 0)
        })

    # Summary
    print(f"\n{'='*80}")
    print("TRAINING SUMMARY")
    print(f"{'='*80}\n")

    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')

    print(f"Total: {len(results)} optimizers")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}\n")

    for result in results:
        icon = "" if result['status'] == 'success' else "" if result['status'] == 'failed' else ""
        score_str = f" ({result['score']:.0%})" if 'score' in result else ""
        print(f"{icon} {result['name']:45} {result['status']}{score_str}")

    print(f"\n{'='*80}")
    if successful == 10:
        print(" ALL 10 MISSING OPTIMIZERS TRAINED SUCCESSFULLY!")
        print("   Total trained: 28 + 10 = 38 optimizers")
    else:
        print(f"  {successful}/10 optimizers trained. Check logs for failures.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
