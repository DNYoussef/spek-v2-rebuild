"""
DSPy NEW Agents Optimizer Training Script

Trains 12 DSPy optimizers for the 6 NEW specialized drone agents:
- Frontend-Dev, Backend-Dev (Princess-Dev hive)
- Infrastructure-Ops, Release-Manager, Performance-Engineer (Princess-Coordination hive)
- Code-Analyzer (Princess-Quality hive)

Week 21 Day 4
Version: 1.0.0
"""

import dspy
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import NEW agent optimizers
from src.dspy_optimizers.core.princess_to_drone import (
    PrincessDevToFrontendDevOptimizer,
    PrincessDevToBackendDevOptimizer,
    PrincessCoordinationToInfrastructureOpsOptimizer,
    PrincessCoordinationToReleaseManagerOptimizer,
    PrincessCoordinationToPerformanceEngineerOptimizer,
    PrincessQualityToCodeAnalyzerOptimizer
)
from src.dspy_optimizers.core.drone_to_princess import (
    FrontendDevToPrincessDevOptimizer,
    BackendDevToPrincessDevOptimizer,
    InfrastructureOpsToPrincessCoordinationOptimizer,
    ReleaseManagerToPrincessCoordinationOptimizer,
    PerformanceEngineerToPrincessCoordinationOptimizer,
    CodeAnalyzerToPrincessQualityOptimizer
)


# ============================================================================
# Metric Functions (reuse from main training script)
# ============================================================================

def delegation_quality(example, prediction, trace=None) -> float:
    """Evaluate quality of task delegation (Princess->Drone)."""
    try:
        if hasattr(prediction, 'drone_task'):
            drone_task_json = prediction.drone_task
        else:
            return 0.0

        drone_task = json.loads(drone_task_json)

        if not isinstance(drone_task, dict):
            return 0.0

        score = 0.0

        # Check required fields (0.6 points)
        required_fields = ["drone_id", "task_type", "description", "estimated_minutes"]
        for field in required_fields:
            if field in drone_task:
                score += 0.15

        # Check specifications exist (0.2 points)
        if "specifications" in drone_task and isinstance(drone_task["specifications"], dict):
            score += 0.2

        # Check time estimate realistic (0.2 points)
        if "estimated_minutes" in drone_task:
            minutes = drone_task["estimated_minutes"]
            if isinstance(minutes, (int, float)) and 10 <= minutes <= 60:
                score += 0.2

        return min(1.0, score)

    except json.JSONDecodeError:
        return 0.0
    except Exception as e:
        print(f"Error evaluating delegation quality: {e}")
        return 0.0


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

        # Check required fields (0.6 points)
        required_fields = ["phase", "status", "summary"]
        for field in required_fields:
            if field in agg_result:
                score += 0.2

        # Check status is valid (0.2 points)
        if "status" in agg_result:
            valid_statuses = ["complete", "blocked", "needs_rework", "partial"]
            if agg_result["status"] in valid_statuses:
                score += 0.2

        # Check next phase or blockers identified (0.2 points)
        if "next_phase" in agg_result or "blockers" in agg_result:
            score += 0.2

        return min(1.0, score)

    except json.JSONDecodeError:
        return 0.0
    except Exception as e:
        print(f"Error evaluating aggregation quality: {e}")
        return 0.0


# ============================================================================
# Dataset Loading Functions
# ============================================================================

def load_delegation_dataset(dataset_path: str) -> List[dspy.Example]:
    """Load Princess->Drone delegation dataset."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = []
    for ex in data.get('examples', []):
        example = dspy.Example(
            phase=ex['phase'],
            context=json.dumps(ex['context']),
            drone_task=json.dumps(ex['expected_drone_task'])
        ).with_inputs('phase', 'context')
        examples.append(example)

    return examples


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


# ============================================================================
# Training Function
# ============================================================================

def train_optimizer(
    optimizer_class,
    dataset_path: str,
    output_path: str,
    metric_func,
    dataset_loader,
    max_demos: int = 10,
    max_rounds: int = 2
) -> Dict[str, Any]:
    """Train a DSPy optimizer using BootstrapFewShot."""
    print(f"\n{'='*80}")
    print(f"Training {optimizer_class.__name__}")
    print(f"Dataset: {dataset_path}")
    print(f"Output: {output_path}")
    print(f"{'='*80}\n")

    try:
        # Load examples
        print("Loading training examples...")
        trainset = dataset_loader(dataset_path)
        print(f"Loaded {len(trainset)} examples\n")

        if len(trainset) == 0:
            print("[WARNING] No examples found in dataset!")
            return {"status": "skipped", "reason": "no_examples"}

        # Create module
        print("Creating optimizer module...")
        module = optimizer_class()

        # Create BootstrapFewShot optimizer
        print(f"Configuring BootstrapFewShot (max_demos={max_demos}, max_rounds={max_rounds})...")
        optimizer = BootstrapFewShot(
            metric=metric_func,
            max_bootstrapped_demos=max_demos,
            max_labeled_demos=min(5, len(trainset) // 2),
            max_rounds=max_rounds
        )

        # Train (compile)
        print("\nTraining... (this may take 2-10 minutes per optimizer)\n")
        compiled = optimizer.compile(
            student=module,
            trainset=trainset
        )

        # Evaluate on training set
        print("\nEvaluating trained model...")
        evaluator = Evaluate(
            devset=trainset[:10],
            metric=metric_func,
            num_threads=1
        )
        score_result = evaluator(compiled)
        score = float(score_result) if hasattr(score_result, '__float__') else score_result
        print(f"Training set score: {score:.2%}\n")

        # Save compiled model
        print(f"Saving compiled model to {output_path}...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        compiled.save(output_path)

        print(f"\n[SUCCESS] Training complete! Model saved to {output_path}")
        print(f"   Training score: {score:.2%}")
        print(f"   Demonstrations: {max_demos}")
        print(f"   Optimization rounds: {max_rounds}\n")

        return {
            "status": "success",
            "score": score,
            "examples": len(trainset),
            "demos": max_demos,
            "rounds": max_rounds
        }

    except Exception as e:
        print(f"\n[FAILED] Training failed: {e}\n")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


# ============================================================================
# Main Training Orchestrator
# ============================================================================

def main():
    """Train all 12 NEW agent DSPy optimizers."""

    # Configure DSPy to use Claude Sonnet 4
    print("Configuring DSPy with Claude Sonnet 4...")

    # Check if Claude API key is set
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    if not claude_key:
        print("\n[ERROR] ANTHROPIC_API_KEY not set!")
        print("   Please set ANTHROPIC_API_KEY environment variable.")
        print("   Example: export ANTHROPIC_API_KEY='your-api-key'\n")
        sys.exit(1)

    dspy.configure(lm=dspy.LM("anthropic/claude-3-5-sonnet-20241022"))

    # Project root
    root = Path(__file__).parent.parent

    # Training configurations for NEW agents (12 paths)
    new_agent_configs = [
        # Princess-Dev -> NEW Drones (2)
        {
            "optimizer_class": PrincessDevToFrontendDevOptimizer,
            "dataset": root / "datasets/dspy/princess_dev_to_frontend_dev.json",
            "output": root / "models/dspy/princess_dev_to_frontend_dev.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Dev -> Frontend-Dev"
        },
        {
            "optimizer_class": PrincessDevToBackendDevOptimizer,
            "dataset": root / "datasets/dspy/princess_dev_to_backend_dev.json",
            "output": root / "models/dspy/princess_dev_to_backend_dev.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Dev -> Backend-Dev"
        },
        # Princess-Coordination -> NEW Drones (3)
        {
            "optimizer_class": PrincessCoordinationToInfrastructureOpsOptimizer,
            "dataset": root / "datasets/dspy/princess_coordination_to_infrastructure_ops.json",
            "output": root / "models/dspy/princess_coordination_to_infrastructure_ops.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Coordination -> Infrastructure-Ops"
        },
        {
            "optimizer_class": PrincessCoordinationToReleaseManagerOptimizer,
            "dataset": root / "datasets/dspy/princess_coordination_to_release_manager.json",
            "output": root / "models/dspy/princess_coordination_to_release_manager.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Coordination -> Release-Manager"
        },
        {
            "optimizer_class": PrincessCoordinationToPerformanceEngineerOptimizer,
            "dataset": root / "datasets/dspy/princess_coordination_to_performance_engineer.json",
            "output": root / "models/dspy/princess_coordination_to_performance_engineer.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Coordination -> Performance-Engineer"
        },
        # Princess-Quality -> NEW Drones (1)
        {
            "optimizer_class": PrincessQualityToCodeAnalyzerOptimizer,
            "dataset": root / "datasets/dspy/princess_quality_to_code_analyzer.json",
            "output": root / "models/dspy/princess_quality_to_code_analyzer.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Quality -> Code-Analyzer"
        },
        # NEW Drones -> Princess (6 reverse paths)
        {
            "optimizer_class": FrontendDevToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/frontend_dev_to_princess_dev.json",
            "output": root / "models/dspy/frontend_dev_to_princess_dev.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Frontend-Dev -> Princess-Dev"
        },
        {
            "optimizer_class": BackendDevToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/backend_dev_to_princess_dev.json",
            "output": root / "models/dspy/backend_dev_to_princess_dev.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Backend-Dev -> Princess-Dev"
        },
        {
            "optimizer_class": InfrastructureOpsToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/infrastructure_ops_to_princess_coordination.json",
            "output": root / "models/dspy/infrastructure_ops_to_princess_coordination.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Infrastructure-Ops -> Princess-Coordination"
        },
        {
            "optimizer_class": ReleaseManagerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/release_manager_to_princess_coordination.json",
            "output": root / "models/dspy/release_manager_to_princess_coordination.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Release-Manager -> Princess-Coordination"
        },
        {
            "optimizer_class": PerformanceEngineerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/performance_engineer_to_princess_coordination.json",
            "output": root / "models/dspy/performance_engineer_to_princess_coordination.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Performance-Engineer -> Princess-Coordination"
        },
        {
            "optimizer_class": CodeAnalyzerToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/code_analyzer_to_princess_quality.json",
            "output": root / "models/dspy/code_analyzer_to_princess_quality.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Code-Analyzer -> Princess-Quality"
        },
    ]

    print(f"\n{'='*80}")
    print("DSPy NEW Agents Optimizer Training Suite")
    print(f"{'='*80}")
    print(f"Training {len(new_agent_configs)} NEW agent optimizers")
    print(f"Estimated time: 2-4 hours total (10-20 min per optimizer)")
    print(f"{'='*80}\n")

    # Train each optimizer
    results = []
    for i, config in enumerate(new_agent_configs, 1):
        print(f"\n[{i}/{len(new_agent_configs)}] Training {config['name']} Optimizer...")

        try:
            result = train_optimizer(
                optimizer_class=config['optimizer_class'],
                dataset_path=str(config['dataset']),
                output_path=str(config['output']),
                metric_func=config['metric'],
                dataset_loader=config['loader'],
                max_demos=10,
                max_rounds=2
            )
            results.append({
                "name": config['name'],
                "status": result['status'],
                "score": result.get('score', 0),
                "examples": result.get('examples', 0)
            })
        except Exception as e:
            print(f"[FAILED] Failed to train {config['name']} optimizer: {e}")
            results.append({
                "name": config['name'],
                "status": "failed",
                "error": str(e)
            })

    # Summary
    print(f"\n{'='*80}")
    print("Training Summary")
    print(f"{'='*80}\n")

    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')

    print(f"Total: {len(results)} optimizers")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}\n")

    for result in results:
        status_icon = "[SUCCESS]" if result['status'] == 'success' else "[FAILED]"
        score_str = f" ({result['score']:.1%})" if 'score' in result else ""
        print(f"{status_icon} {result['name']:50} {result['status']}{score_str}")
    print()


if __name__ == "__main__":
    main()
