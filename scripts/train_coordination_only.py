"""
Train only the Coordination optimizer using Claude.
Quick script to complete the 3rd optimizer after hitting Gemini daily limit.
"""

import dspy
import json
import sys
import os
from pathlib import Path
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dspy_optimizers.core import QueenToPrincessCoordinationOptimizer


def task_decomposition_quality(example, prediction, trace=None):
    """Evaluate quality of task decomposition (0.0 to 1.0)."""
    try:
        if hasattr(prediction, 'subtasks'):
            subtasks_json = prediction.subtasks
        else:
            return 0.0

        subtasks = json.loads(subtasks_json)
        if not isinstance(subtasks, list) or len(subtasks) == 0:
            return 0.0

        score = 0.0
        max_score = 0.0

        for subtask in subtasks:
            required_fields = ["princess", "task_type", "description", "dependencies", "estimated_minutes"]
            for field in required_fields:
                max_score += 0.04
                if field in subtask:
                    score += 0.04

            max_score += 0.1
            if "princess" in subtask and subtask["princess"] in ["princess-dev", "princess-quality", "princess-coordination"]:
                score += 0.1

            max_score += 0.1
            if "estimated_minutes" in subtask:
                minutes = subtask["estimated_minutes"]
                if isinstance(minutes, (int, float)) and 15 <= minutes <= 60:
                    score += 0.1

            max_score += 0.1
            if "dependencies" in subtask and isinstance(subtask["dependencies"], list):
                score += 0.1

            max_score += 0.1
            if "description" in subtask and len(subtask["description"]) > 20:
                score += 0.1

        if 2 <= len(subtasks) <= 8:
            score += 0.2
        max_score += 0.2

        if max_score > 0:
            return min(1.0, score / max_score)
        else:
            return 0.0

    except json.JSONDecodeError:
        return 0.0
    except Exception as e:
        print(f"Error evaluating quality: {e}")
        return 0.0


def main():
    # Configure Claude
    print("Configuring DSPy with Claude Sonnet 4...")
    dspy.configure(lm=dspy.LM("anthropic/claude-3-5-sonnet-20241022"))

    # Load dataset
    print("Loading training examples...")
    dataset_path = Path(__file__).parent.parent / "datasets/dspy/queen_to_princess_coordination_top10.json"

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = []
    for ex in data['examples']:
        subtasks_json = json.dumps(ex['expected_subtasks'])
        example = dspy.Example(
            task_description=ex['task_description'],
            objective=ex['objective'],
            subtasks=subtasks_json
        ).with_inputs('task_description', 'objective')
        examples.append(example)

    print(f"Loaded {len(examples)} examples\n")

    # Create module
    print("Creating Coordination optimizer module...")
    module = QueenToPrincessCoordinationOptimizer()

    # Create optimizer
    print("Configuring BootstrapFewShot (max_demos=10, max_rounds=3)...")
    optimizer = BootstrapFewShot(
        metric=task_decomposition_quality,
        max_bootstrapped_demos=10,
        max_labeled_demos=5,
        max_rounds=3
    )

    # Train
    print("\nTraining with Claude... (this may take 5-10 minutes)\n")
    compiled = optimizer.compile(student=module, trainset=examples)

    # Evaluate
    print("\nEvaluating trained model...")
    evaluator = Evaluate(
        devset=examples,
        metric=task_decomposition_quality,
        num_threads=1
    )
    score_result = evaluator(compiled)
    score = float(score_result) if hasattr(score_result, '__float__') else score_result
    print(f"Training set score: {score:.2%}\n")

    # Save
    output_path = Path(__file__).parent.parent / "models/dspy/queen_to_princess_coordination.json"
    print(f"Saving compiled model to {output_path}...")
    os.makedirs(output_path.parent, exist_ok=True)
    compiled.save(str(output_path))

    print(f"\n[SUCCESS] Training complete! Model saved to {output_path}")
    print(f"   Training score: {score:.2%}")
    print(f"   Demonstrations: 10")
    print(f"   Optimization rounds: 3\n")


if __name__ == "__main__":
    main()
