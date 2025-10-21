"""
DSPy Optimizer Training with Groq API

Fast, free training using Groq's high-performance inference.
Trains Queen->Princess communication optimizers (3 P0 agents).

Week 24.5 - Groq Migration
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

from src.dspy_optimizers.core import (
    QueenToPrincessDevOptimizer,
    QueenToPrincessQualityOptimizer,
    QueenToPrincessCoordinationOptimizer
)


def task_decomposition_quality(example, prediction, trace=None) -> float:
    """
    Evaluate quality of task decomposition (0.0 to 1.0).

    Checks: Valid JSON, actionable subtasks, dependencies, time estimates
    """
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

        # Check each subtask
        for subtask in subtasks:
            required_fields = ["princess", "task_type", "description", "dependencies", "estimated_minutes"]
            for field in required_fields:
                max_score += 0.04
                if field in subtask:
                    score += 0.04

            # Princess assignment valid
            max_score += 0.1
            if "princess" in subtask and subtask["princess"] in ["princess-dev", "princess-quality", "princess-coordination"]:
                score += 0.1

            # Time estimate realistic
            max_score += 0.1
            if "estimated_minutes" in subtask:
                minutes = subtask["estimated_minutes"]
                if isinstance(minutes, (int, float)) and 15 <= minutes <= 60:
                    score += 0.1

            # Dependencies format
            max_score += 0.1
            if "dependencies" in subtask and isinstance(subtask["dependencies"], list):
                score += 0.1

            # Description length
            max_score += 0.1
            if "description" in subtask and len(subtask["description"]) > 20:
                score += 0.1

        # Number of subtasks (2-8 ideal)
        if 2 <= len(subtasks) <= 8:
            score += 0.2
        max_score += 0.2

        return min(1.0, score / max_score if max_score > 0 else 0.0)

    except Exception as e:
        print(f"⚠️  Metric error: {e}")
        return 0.0


def load_training_examples(dataset_path: str) -> List[dspy.Example]:
    """Load training examples from JSON dataset."""
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

    return examples


def train_optimizer(
    optimizer_class,
    dataset_path: str,
    output_path: str,
    max_demos: int = 10,
    max_rounds: int = 3
) -> None:
    """Train a DSPy optimizer using BootstrapFewShot."""
    print(f"\n{'='*80}")
    print(f"Training {optimizer_class.__name__}")
    print(f"Dataset: {Path(dataset_path).name}")
    print(f"Output: {Path(output_path).name}")
    print(f"{'='*80}\n")

    # Load examples
    print("📥 Loading training examples...")
    trainset = load_training_examples(dataset_path)
    print(f"   Loaded {len(trainset)} examples\n")

    # Create module
    print("🔧 Creating optimizer module...")
    module = optimizer_class()

    # Create BootstrapFewShot optimizer
    print(f"⚙️  Configuring BootstrapFewShot (demos={max_demos}, rounds={max_rounds})...\n")
    optimizer = BootstrapFewShot(
        metric=task_decomposition_quality,
        max_bootstrapped_demos=max_demos,
        max_labeled_demos=5,
        max_rounds=max_rounds
    )

    # Train
    print("🚀 Training... (this may take 2-5 minutes with Groq)\n")
    try:
        compiled = optimizer.compile(
            student=module,
            trainset=trainset
        )

        # Evaluate
        print("📊 Evaluating trained model...")
        evaluator = Evaluate(
            devset=trainset,
            metric=task_decomposition_quality,
            num_threads=1
        )
        score_result = evaluator(compiled)
        score = float(score_result) if hasattr(score_result, '__float__') else score_result
        print(f"   Score: {score:.1%}\n")

        # Save
        print(f"💾 Saving to {Path(output_path).name}...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        compiled.save(output_path)

        print(f"\n✅ SUCCESS! Model saved")
        print(f"   Score: {score:.1%}")
        print(f"   Demos: {max_demos}")
        print(f"   Rounds: {max_rounds}\n")

    except Exception as e:
        print(f"\n❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Train all 3 Queen->Princess optimizers with Groq."""
    print(f"\n{'='*80}")
    print("DSPy Optimizer Training with Groq API")
    print(f"{'='*80}\n")

    # Configure Groq
    groq_key = os.getenv('GROQ_API_KEY', '')  # Set GROQ_API_KEY environment variable
    if not groq_key:
        print("❌ ERROR: GROQ_API_KEY not set!")
        print("   Set it with: export GROQ_API_KEY='your-key'")
        sys.exit(1)

    # Set API key
    os.environ['GROQ_API_KEY'] = groq_key

    print(f"🔧 Configuring DSPy with Groq...")
    print(f"   Model: groq/llama-3.3-70b-versatile")
    print(f"   Speed: 1000 tokens/sec (15x faster than Gemini CLI)")
    print(f"   Cost: FREE tier\n")

    # Configure DSPy with Groq
    lm = dspy.LM('groq/llama-3.3-70b-versatile', api_key=groq_key)
    dspy.configure(lm=lm)

    # Test connection
    print("🔌 Testing Groq connection...")
    try:
        test_response = lm("Test: 2+2=?", max_tokens=10)
        print(f"   ✅ Connection successful! Response: {test_response[:50]}\n")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}\n")
        sys.exit(1)

    # Project root
    root = Path(__file__).parent.parent

    # Training configurations
    configs = [
        {
            "optimizer_class": QueenToPrincessDevOptimizer,
            "dataset": root / "datasets/dspy/queen_to_princess_dev_top10.json",
            "output": root / "models/dspy/queen_to_princess_dev_groq.json",
            "name": "Development"
        },
        {
            "optimizer_class": QueenToPrincessQualityOptimizer,
            "dataset": root / "datasets/dspy/queen_to_princess_quality_top10.json",
            "output": root / "models/dspy/queen_to_princess_quality_groq.json",
            "name": "Quality"
        },
        {
            "optimizer_class": QueenToPrincessCoordinationOptimizer,
            "dataset": root / "datasets/dspy/queen_to_princess_coordination_top10.json",
            "output": root / "models/dspy/queen_to_princess_coordination_groq.json",
            "name": "Coordination"
        }
    ]

    print(f"{'='*80}")
    print(f"Training 3 P0 Optimizers (Queen->Princess)")
    print(f"Estimated time: 6-15 minutes total (2-5 min each with Groq)")
    print(f"{'='*80}\n")

    # Train each
    results = []
    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/3] {config['name']} Optimizer")

        try:
            train_optimizer(
                optimizer_class=config['optimizer_class'],
                dataset_path=str(config['dataset']),
                output_path=str(config['output']),
                max_demos=10,
                max_rounds=3
            )
            results.append({"name": config['name'], "status": "✅ SUCCESS"})
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({"name": config['name'], "status": f"❌ FAILED: {e}"})

    # Summary
    print(f"\n{'='*80}")
    print("Training Summary")
    print(f"{'='*80}\n")
    for result in results:
        print(f"{result['name']:20} {result['status']}")
    print()

    successful = sum(1 for r in results if "SUCCESS" in r['status'])
    print(f"✅ {successful}/3 optimizers trained successfully")

    if successful == 3:
        print("\n🎉 ALL TRAINING COMPLETE! Ready for production use.")
    else:
        print(f"\n⚠️  {3 - successful} optimizer(s) failed. Check logs above.")


if __name__ == "__main__":
    main()
