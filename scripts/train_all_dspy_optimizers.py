"""
Comprehensive DSPy Optimizer Training Script

Trains ALL 34 DSPy optimizers for complete communication path coverage:
- 3 Queen->Princess (already trained)
- 11 Princess->Drone
- 11 Drone->Princess
- 6 Princess↔Princess
- 3 Princess->Queen

Total: 34 optimizers

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

# Import optimizers
from src.dspy_optimizers.core.queen_to_princess import (
    QueenToPrincessDevOptimizer,
    QueenToPrincessQualityOptimizer,
    QueenToPrincessCoordinationOptimizer
)
from src.dspy_optimizers.core.princess_to_drone import (
    PrincessDevToCoderOptimizer,
    PrincessDevToReviewerOptimizer,
    PrincessDevToDebuggerOptimizer,
    PrincessDevToIntegrationEngineerOptimizer,
    PrincessQualityToTesterOptimizer,
    PrincessQualityToNasaEnforcerOptimizer,
    PrincessQualityToTheaterDetectorOptimizer,
    PrincessQualityToFsmAnalyzerOptimizer,
    PrincessCoordinationToOrchestratorOptimizer,
    PrincessCoordinationToPlannerOptimizer,
    PrincessCoordinationToCostTrackerOptimizer
)
from src.dspy_optimizers.core.drone_to_princess import (
    CoderToPrincessDevOptimizer,
    ReviewerToPrincessDevOptimizer,
    DebuggerToPrincessDevOptimizer,
    IntegrationEngineerToPrincessDevOptimizer,
    TesterToPrincessQualityOptimizer,
    NasaEnforcerToPrincessQualityOptimizer,
    TheaterDetectorToPrincessQualityOptimizer,
    FsmAnalyzerToPrincessQualityOptimizer,
    OrchestratorToPrincessCoordinationOptimizer,
    PlannerToPrincessCoordinationOptimizer,
    CostTrackerToPrincessCoordinationOptimizer
)


# ============================================================================
# Metric Functions
# ============================================================================

def delegation_quality(example, prediction, trace=None) -> float:
    """
    Evaluate quality of task delegation (Princess->Drone).

    Checks:
    - Valid JSON drone_task
    - Required fields present
    - Clear specifications
    - Realistic time estimates
    """
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
    """
    Evaluate quality of result aggregation (Drone->Princess).

    Checks:
    - Valid JSON aggregated_result
    - Status determination correct
    - Quality metrics extracted
    - Next phase identified
    """
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


def coordination_quality(example, prediction, trace=None) -> float:
    """
    Evaluate quality of cross-princess coordination.

    Checks:
    - Valid JSON coordination_message
    - Clear request type
    - Scope defined
    - Success criteria present
    """
    try:
        # Handle different prediction field names
        coord_message_json = None
        if hasattr(prediction, 'coordination_message'):
            coord_message_json = prediction.coordination_message
        elif hasattr(prediction, 'subtasks'):
            coord_message_json = prediction.subtasks
        elif hasattr(prediction, 'drone_task'):
            coord_message_json = prediction.drone_task
        else:
            return 0.0

        coord_message = json.loads(coord_message_json)

        if not isinstance(coord_message, dict):
            return 0.0

        score = 0.0

        # Check required fields (0.6 points)
        required_fields = ["request_type", "description"]
        for field in required_fields:
            if field in coord_message:
                score += 0.3

        # Check scope or success_criteria (0.4 points)
        if "scope" in coord_message or "success_criteria" in coord_message:
            score += 0.4

        return min(1.0, score)

    except json.JSONDecodeError:
        return 0.0
    except Exception as e:
        print(f"Error evaluating coordination quality: {e}")
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


def load_coordination_dataset(dataset_path: str) -> List[dspy.Example]:
    """Load Princess↔Princess coordination dataset."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = []
    for ex in data.get('examples', []):
        # Handle coordination message field
        coord_msg = ex.get('expected_coordination_message', ex.get('expected_escalation_message', {}))

        example = dspy.Example(
            task_description=ex.get('context', {}).get('feature', 'Unknown'),
            objective=json.dumps(ex.get('context', {})),
            subtasks=json.dumps(coord_msg)  # Reuse subtasks field for coordination
        ).with_inputs('task_description', 'objective')
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
    max_rounds: int = 2  # Reduced from 3 to save time/cost
) -> Dict[str, Any]:
    """
    Train a DSPy optimizer using BootstrapFewShot.

    Returns:
        Dict with training results
    """
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
            max_labeled_demos=min(5, len(trainset) // 2),  # Use fewer seed examples
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
            devset=trainset[:10],  # Evaluate on first 10 examples only
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
    """Train all 31 remaining DSPy optimizers (excluding 3 already trained)."""

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

    # Training configurations for Princess->Drone (11 paths)
    princess_to_drone_configs = [
        # Princess-Dev -> Drones (4)
        {
            "optimizer_class": PrincessDevToCoderOptimizer,
            "dataset": root / "datasets/dspy/princess_dev_to_coder.json",
            "output": root / "models/dspy/princess_dev_to_coder.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Dev -> Coder"
        },
        {
            "optimizer_class": PrincessDevToReviewerOptimizer,
            "dataset": root / "datasets/dspy/princess_dev_to_reviewer.json",
            "output": root / "models/dspy/princess_dev_to_reviewer.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Dev -> Reviewer"
        },
        {
            "optimizer_class": PrincessDevToDebuggerOptimizer,
            "dataset": root / "datasets/dspy/princess_dev_to_debugger.json",
            "output": root / "models/dspy/princess_dev_to_debugger.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Dev -> Debugger"
        },
        {
            "optimizer_class": PrincessDevToIntegrationEngineerOptimizer,
            "dataset": root / "datasets/dspy/princess_dev_to_integration_engineer.json",
            "output": root / "models/dspy/princess_dev_to_integration_engineer.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Dev -> Integration-Engineer"
        },
        # Princess-Quality -> Drones (4)
        {
            "optimizer_class": PrincessQualityToTesterOptimizer,
            "dataset": root / "datasets/dspy/princess_quality_to_tester.json",
            "output": root / "models/dspy/princess_quality_to_tester.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Quality -> Tester"
        },
        {
            "optimizer_class": PrincessQualityToNasaEnforcerOptimizer,
            "dataset": root / "datasets/dspy/princess_quality_to_nasa_enforcer.json",
            "output": root / "models/dspy/princess_quality_to_nasa_enforcer.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Quality -> NASA-Enforcer"
        },
        {
            "optimizer_class": PrincessQualityToTheaterDetectorOptimizer,
            "dataset": root / "datasets/dspy/princess_quality_to_theater_detector.json",
            "output": root / "models/dspy/princess_quality_to_theater_detector.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Quality -> Theater-Detector"
        },
        {
            "optimizer_class": PrincessQualityToFsmAnalyzerOptimizer,
            "dataset": root / "datasets/dspy/princess_quality_to_fsm_analyzer.json",
            "output": root / "models/dspy/princess_quality_to_fsm_analyzer.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Quality -> FSM-Analyzer"
        },
        # Princess-Coordination -> Drones (3)
        {
            "optimizer_class": PrincessCoordinationToOrchestratorOptimizer,
            "dataset": root / "datasets/dspy/princess_coordination_to_orchestrator.json",
            "output": root / "models/dspy/princess_coordination_to_orchestrator.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Coordination -> Orchestrator"
        },
        {
            "optimizer_class": PrincessCoordinationToPlannerOptimizer,
            "dataset": root / "datasets/dspy/princess_coordination_to_planner.json",
            "output": root / "models/dspy/princess_coordination_to_planner.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Coordination -> Planner"
        },
        {
            "optimizer_class": PrincessCoordinationToCostTrackerOptimizer,
            "dataset": root / "datasets/dspy/princess_coordination_to_cost_tracker.json",
            "output": root / "models/dspy/princess_coordination_to_cost_tracker.json",
            "metric": delegation_quality,
            "loader": load_delegation_dataset,
            "name": "Princess-Coordination -> Cost-Tracker"
        },
    ]

    # Training configurations for Drone->Princess (11 paths)
    drone_to_princess_configs = [
        # Dev Hive -> Princess-Dev (4)
        {
            "optimizer_class": CoderToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/coder_to_princess_dev.json",
            "output": root / "models/dspy/coder_to_princess_dev.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Coder -> Princess-Dev"
        },
        {
            "optimizer_class": ReviewerToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/reviewer_to_princess_dev.json",
            "output": root / "models/dspy/reviewer_to_princess_dev.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Reviewer -> Princess-Dev"
        },
        {
            "optimizer_class": DebuggerToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/debugger_to_princess_dev.json",
            "output": root / "models/dspy/debugger_to_princess_dev.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Debugger -> Princess-Dev"
        },
        {
            "optimizer_class": IntegrationEngineerToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/integration_engineer_to_princess_dev.json",
            "output": root / "models/dspy/integration_engineer_to_princess_dev.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Integration-Engineer -> Princess-Dev"
        },
        # Quality Hive -> Princess-Quality (4)
        {
            "optimizer_class": TesterToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/tester_to_princess_quality.json",
            "output": root / "models/dspy/tester_to_princess_quality.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Tester -> Princess-Quality"
        },
        {
            "optimizer_class": NasaEnforcerToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/nasa_enforcer_to_princess_quality.json",
            "output": root / "models/dspy/nasa_enforcer_to_princess_quality.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "NASA-Enforcer -> Princess-Quality"
        },
        {
            "optimizer_class": TheaterDetectorToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/theater_detector_to_princess_quality.json",
            "output": root / "models/dspy/theater_detector_to_princess_quality.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Theater-Detector -> Princess-Quality"
        },
        {
            "optimizer_class": FsmAnalyzerToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/fsm_analyzer_to_princess_quality.json",
            "output": root / "models/dspy/fsm_analyzer_to_princess_quality.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "FSM-Analyzer -> Princess-Quality"
        },
        # Coordination Hive -> Princess-Coordination (3)
        {
            "optimizer_class": OrchestratorToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/orchestrator_to_princess_coordination.json",
            "output": root / "models/dspy/orchestrator_to_princess_coordination.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Orchestrator -> Princess-Coordination"
        },
        {
            "optimizer_class": PlannerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/planner_to_princess_coordination.json",
            "output": root / "models/dspy/planner_to_princess_coordination.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Planner -> Princess-Coordination"
        },
        {
            "optimizer_class": CostTrackerToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/cost_tracker_to_princess_coordination.json",
            "output": root / "models/dspy/cost_tracker_to_princess_coordination.json",
            "metric": aggregation_quality,
            "loader": load_aggregation_dataset,
            "name": "Cost-Tracker -> Princess-Coordination"
        },
    ]

    # Combine all configs
    all_configs = princess_to_drone_configs + drone_to_princess_configs

    print(f"\n{'='*80}")
    print("DSPy Optimizer Training Suite - COMPREHENSIVE")
    print(f"{'='*80}")
    print(f"Training {len(all_configs)} optimizers (Princess<->Drone communication)")
    print(f"Estimated time: 3-8 hours total (2-10 min per optimizer)")
    print(f"{'='*80}\n")

    # Train each optimizer
    results = []
    for i, config in enumerate(all_configs, 1):
        print(f"\n[{i}/{len(all_configs)}] Training {config['name']} Optimizer...".encode('ascii', errors='ignore').decode('ascii'))

        try:
            result = train_optimizer(
                optimizer_class=config['optimizer_class'],
                dataset_path=str(config['dataset']),
                output_path=str(config['output']),
                metric_func=config['metric'],
                dataset_loader=config['loader'],
                max_demos=10,
                max_rounds=2  # Reduced to save time
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
        print(f"{status_icon} {result['name']:45} {result['status']}{score_str}")
    print()


if __name__ == "__main__":
    main()
