"""
DSPy Optimizer Training Script

Trains Queen→Princess communication optimizers using BootstrapFewShot.
Uses top 10 examples from each dataset as demonstrations.

Week 21 Day 3
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

from src.dspy_optimizers.core import (
    QueenToPrincessDevOptimizer,
    QueenToPrincessQualityOptimizer,
    QueenToPrincessCoordinationOptimizer
)


# ============================================================================
# Metric Functions
# ============================================================================

def task_decomposition_quality(example, prediction, trace=None) -> float:
    """
    Evaluate quality of task decomposition (0.0 to 1.0).

    Checks:
    - Valid JSON structure
    - All subtasks actionable (2-8 subtasks)
    - Dependencies valid (no cycles)
    - Time estimates realistic (15-60 min)
    - Appropriate princess assignment

    Args:
        example: Training example with expected_subtasks
        prediction: Model prediction with subtasks
        trace: Optional trace (unused)

    Returns:
        Quality score 0.0-1.0
    """
    try:
        # Parse predicted subtasks
        if hasattr(prediction, 'subtasks'):
            subtasks_json = prediction.subtasks
        else:
            return 0.0

        subtasks = json.loads(subtasks_json)

        if not isinstance(subtasks, list) or len(subtasks) == 0:
            return 0.0

        score = 0.0
        max_score = 0.0

        # Check each subtask
        for subtask in subtasks:
            # Check required fields (0.2 points each)
            required_fields = ["princess", "task_type", "description", "dependencies", "estimated_minutes"]
            for field in required_fields:
                max_score += 0.04  # 0.2 / 5 fields
                if field in subtask:
                    score += 0.04

            # Check princess assignment valid (0.1 points)
            max_score += 0.1
            if "princess" in subtask and subtask["princess"] in ["princess-dev", "princess-quality", "princess-coordination"]:
                score += 0.1

            # Check time estimate realistic (0.1 points)
            max_score += 0.1
            if "estimated_minutes" in subtask:
                minutes = subtask["estimated_minutes"]
                if isinstance(minutes, (int, float)) and 15 <= minutes <= 60:
                    score += 0.1

            # Check dependencies format (0.1 points)
            max_score += 0.1
            if "dependencies" in subtask and isinstance(subtask["dependencies"], list):
                score += 0.1

            # Check description length (0.1 points)
            max_score += 0.1
            if "description" in subtask and len(subtask["description"]) > 20:
                score += 0.1

        # Check number of subtasks (2-8 ideal)
        if 2 <= len(subtasks) <= 8:
            score += 0.2
        max_score += 0.2

        # Normalize by max possible score
        if max_score > 0:
            return min(1.0, score / max_score)
        else:
            return 0.0

    except json.JSONDecodeError:
        return 0.0
    except Exception as e:
        print(f"Error evaluating quality: {e}")
        return 0.0


# ============================================================================
# Training Functions
# ============================================================================

def load_training_examples(dataset_path: str) -> List[dspy.Example]:
    """
    Load training examples from JSON dataset.

    Args:
        dataset_path: Path to *_top10.json file

    Returns:
        List of dspy.Example objects
    """
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = []
    for ex in data['examples']:
        # Convert expected_subtasks to JSON string (DSPy output format)
        subtasks_json = json.dumps(ex['expected_subtasks'])

        example = dspy.Example(
            task_description=ex['task_description'],
            objective=ex['objective'],
            subtasks=subtasks_json  # Ground truth
        ).with_inputs('task_description', 'objective')

        examples.append(example)

    return examples


def train_optimizer(
    optimizer_class,
    dataset_path: str,
    output_path: str,
    max_demos: int = 10,
    max_rounds: int = 3
) -> None:
    """
    Train a DSPy optimizer using BootstrapFewShot.

    Args:
        optimizer_class: Optimizer class to train (e.g., QueenToPrincessDevOptimizer)
        dataset_path: Path to training dataset JSON
        output_path: Path to save compiled model JSON
        max_demos: Maximum demonstrations to use (default: 10)
        max_rounds: Maximum optimization rounds (default: 3)
    """
    print(f"\n{'='*80}")
    print(f"Training {optimizer_class.__name__}")
    print(f"Dataset: {dataset_path}")
    print(f"Output: {output_path}")
    print(f"{'='*80}\n")

    # Load examples
    print("Loading training examples...")
    trainset = load_training_examples(dataset_path)
    print(f"Loaded {len(trainset)} examples\n")

    # Create module
    print("Creating optimizer module...")
    module = optimizer_class()

    # Create BootstrapFewShot optimizer
    print(f"Configuring BootstrapFewShot (max_demos={max_demos}, max_rounds={max_rounds})...")
    optimizer = BootstrapFewShot(
        metric=task_decomposition_quality,
        max_bootstrapped_demos=max_demos,
        max_labeled_demos=5,  # Use 5 seed examples
        max_rounds=max_rounds
    )

    # Train (compile)
    print("\nTraining... (this may take 5-30 minutes)\n")
    try:
        compiled = optimizer.compile(
            student=module,
            trainset=trainset
        )

        # Evaluate on training set
        print("\nEvaluating trained model...")
        evaluator = Evaluate(
            devset=trainset,
            metric=task_decomposition_quality,
            num_threads=1
        )
        score_result = evaluator(compiled)
        # Extract score value (handle EvaluationResult object)
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

    except Exception as e:
        print(f"\n[FAILED] Training failed: {e}\n")
        raise


# ============================================================================
# Main Training Script
# ============================================================================

def main():
    """Train all 3 P0 optimizers."""
    # Configure DSPy to use Claude Sonnet 4
    print("Configuring DSPy with Claude Sonnet 4...")

    # Check if Claude API key is set
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    if not claude_key:
        print("\n[WARNING] ANTHROPIC_API_KEY not set!")
        print("   Please set ANTHROPIC_API_KEY environment variable or training will fail.")
        print("   Example: export ANTHROPIC_API_KEY='your-api-key'\n")

    dspy.configure(lm=dspy.LM("anthropic/claude-3-5-sonnet-20241022"))

    # Project root
    root = Path(__file__).parent.parent

    # Training configurations
    configs = [
        {
            "optimizer_class": QueenToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/queen_to_princess_dev_top10.json",
            "output": root / "models/dspy/queen_to_princess_dev.json",
            "name": "Development"
        },
        {
            "optimizer_class": QueenToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/queen_to_princess_quality_top10.json",
            "output": root / "models/dspy/queen_to_princess_quality.json",
            "name": "Quality"
        },
        {
            "optimizer_class": QueenToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/queen_to_princess_coordination_top10.json",
            "output": root / "models/dspy/queen_to_princess_coordination.json",
            "name": "Coordination"
        }
    ]

    print(f"\n{'='*80}")
    print("DSPy Optimizer Training Suite")
    print(f"{'='*80}")
    print("Training 3 P0 optimizers (Queen->Princess communication)")
    print(f"Estimated time: 15-90 minutes total")
    print(f"{'='*80}\n")

    # Train each optimizer
    results = []
    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/3] Training {config['name']} Optimizer...")

        try:
            train_optimizer(
                optimizer_class=config['optimizer_class'],
                dataset_path=str(config['dataset']),
                output_path=str(config['output']),
                max_demos=10,
                max_rounds=3
            )
            results.append({"name": config['name'], "status": "[SUCCESS]"})
        except Exception as e:
            print(f"[FAILED] Failed to train {config['name']} optimizer: {e}")
            results.append({"name": config['name'], "status": f"[FAILED]: {e}"})

    # Summary
    print(f"\n{'='*80}")
    print("Training Summary")
    print(f"{'='*80}\n")
    for result in results:
        print(f"{result['name']:20} {result['status']}")
    print()


if __name__ == "__main__":
    main()
