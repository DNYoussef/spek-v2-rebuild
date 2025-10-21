"""DSPy Training Script for P0 Agents (Week 6 Day 3, v8.0.0)

Orchestrates complete training pipeline:
1. Load training datasets
2. Configure DSPy with Gemini
3. Initialize agent modules
4. Run BootstrapFewShot optimization
5. Save optimized modules
6. Evaluate performance

Run with: python src/dspy_optimization/train.py --agent queen
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import dspy

from src.dspy_optimization.dspy_config import configure_dspy, validate_api_connection
from src.dspy_optimization.data_loader import load_training_dataset, split_train_val
from src.dspy_optimization.dspy_metrics import (
    queen_metric,
    tester_metric,
    reviewer_metric,
    coder_metric
)
from src.dspy_optimization.signatures import (
    QueenModule,
    TesterModule,
    ReviewerModule,
    CoderModule
)


AGENT_CONFIG = {
    "queen": {
        "module_class": QueenModule,
        "metric_func": queen_metric,
        "dataset_path": "datasets/week6/queen_training_dataset.json",
        "max_demos": 7,
        "max_rounds": 3
    },
    "tester": {
        "module_class": TesterModule,
        "metric_func": tester_metric,
        "dataset_path": "datasets/week6/tester_training_dataset.json",
        "max_demos": 7,
        "max_rounds": 3
    },
    "reviewer": {
        "module_class": ReviewerModule,
        "metric_func": reviewer_metric,
        "dataset_path": "datasets/week6/reviewer_training_dataset.json",
        "max_demos": 5,
        "max_rounds": 2
    },
    "coder": {
        "module_class": CoderModule,
        "metric_func": coder_metric,
        "dataset_path": "datasets/week6/coder_training_dataset.json",
        "max_demos": 5,
        "max_rounds": 2
    }
}


def train_agent(
    agent_id: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    val_ratio: float = 0.2,
    output_dir: str = "models/dspy"
) -> Dict[str, Any]:
    """Train a single P0 agent with DSPy optimization.

    Args:
        agent_id: Agent to train (queen, tester, reviewer, coder)
        temperature: Gemini temperature (default: 0.7)
        max_tokens: Max output tokens (default: 2048)
        val_ratio: Validation set ratio (default: 0.2)
        output_dir: Directory to save optimized model

    Returns:
        Training results dictionary with metrics

    Raises:
        ValueError: If agent_id not in AGENT_CONFIG
        FileNotFoundError: If dataset not found

    Example:
        >>> results = train_agent("queen")
        >>> print(f"Final score: {results['final_score']}")
    """
    if agent_id not in AGENT_CONFIG:
        raise ValueError(f"Unknown agent: {agent_id}. Must be one of {list(AGENT_CONFIG.keys())}")

    config = AGENT_CONFIG[agent_id]
    print(f"\n=== Training {agent_id.upper()} Agent ===\n")

    print("[1/6] Configuring DSPy with Gemini...")
    configure_dspy(temperature=temperature, max_tokens=max_tokens)

    if not validate_api_connection():
        raise RuntimeError("Gemini API connection failed")

    print(f"\n[2/6] Loading training dataset: {config['dataset_path']}")
    # Use min_quality=70.0 to include synthetic examples (quality_label>=70)
    examples, info = load_training_dataset(config['dataset_path'], min_quality=70.0)
    print(f"      Loaded {len(examples)} examples (avg quality: {info.avg_quality:.1f})")

    print(f"\n[3/6] Splitting train/val ({1-val_ratio:.0%}/{val_ratio:.0%})")
    trainset, valset = split_train_val(examples, val_ratio=val_ratio)
    print(f"      Train: {len(trainset)}, Val: {len(valset)}")

    print(f"\n[4/6] Initializing {agent_id} module...")
    module = config['module_class']()
    print(f"      Module type: {type(module).__name__}")

    print(f"\n[5/6] Running BootstrapFewShot optimization...")
    print(f"      Max demos: {config['max_demos']}, Max rounds: {config['max_rounds']}")

    optimizer = dspy.BootstrapFewShot(
        metric=config['metric_func'],
        max_bootstrapped_demos=config['max_demos'],
        max_labeled_demos=config['max_demos'],
        max_rounds=config['max_rounds']
    )

    start_time = time.time()

    try:
        optimized_module = optimizer.compile(module, trainset=trainset)
        training_time = time.time() - start_time

        print(f"\n[6/6] Evaluating optimized module on validation set...")
        val_scores = []
        for example in valset:
            try:
                prediction = optimized_module.forward(**example.inputs())
                score = config['metric_func'](example, prediction)
                val_scores.append(score)
            except Exception as e:
                print(f"      [WARN] Validation failed for example: {e}")
                val_scores.append(0.0)

        avg_score = sum(val_scores) / len(val_scores) if val_scores else 0.0

        print(f"\n[OK] Training complete!")
        print(f"     Training time: {training_time:.1f}s")
        print(f"     Validation score: {avg_score:.1f}/100")

        output_path = Path(output_dir) / f"{agent_id}_optimized.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        optimized_module.save(str(output_path))
        print(f"     Saved to: {output_path}")

        return {
            "agent_id": agent_id,
            "training_time_sec": training_time,
            "train_examples": len(trainset),
            "val_examples": len(valset),
            "final_score": avg_score,
            "model_path": str(output_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(f"\n[FAIL] Training failed: {e}")
        raise


def train_all_p0_agents(
    temperature: float = 0.7,
    max_tokens: int = 2048,
    output_dir: str = "models/dspy"
) -> Dict[str, Dict[str, Any]]:
    """Train all 4 P0 agents sequentially.

    Args:
        temperature: Gemini temperature
        max_tokens: Max output tokens
        output_dir: Directory to save models

    Returns:
        Dictionary mapping agent_id to training results

    Example:
        >>> results = train_all_p0_agents()
        >>> for agent, result in results.items():
        ...     print(f"{agent}: {result['final_score']:.1f}")
    """
    results = {}

    for agent_id in ["queen", "tester", "reviewer", "coder"]:
        try:
            result = train_agent(
                agent_id,
                temperature=temperature,
                max_tokens=max_tokens,
                output_dir=output_dir
            )
            results[agent_id] = result
        except Exception as e:
            print(f"\n[FAIL] Failed to train {agent_id}: {e}")
            results[agent_id] = {"error": str(e)}

    print("\n=== Training Summary ===")
    for agent_id, result in results.items():
        if "error" in result:
            print(f"{agent_id:<12} [FAIL] {result['error']}")
        else:
            print(
                f"{agent_id:<12} [OK] Score: {result['final_score']:.1f}, "
                f"Time: {result['training_time_sec']:.1f}s"
            )

    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Train DSPy-optimized P0 agents for SPEK Platform"
    )
    parser.add_argument(
        "--agent",
        type=str,
        choices=["queen", "tester", "reviewer", "coder", "all"],
        default="all",
        help="Agent to train (default: all)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Gemini temperature (default: 0.7)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max output tokens (default: 2048)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/dspy",
        help="Output directory for models (default: models/dspy)"
    )

    args = parser.parse_args()

    if args.agent == "all":
        train_all_p0_agents(
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            output_dir=args.output_dir
        )
    else:
        train_agent(
            args.agent,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            output_dir=args.output_dir
        )


if __name__ == "__main__":
    main()


# Version: 1.0
# Timestamp: 2025-10-08T00:00:00-04:00
# Agent/Model: Claude Sonnet 4.5
# Changes: Created complete training pipeline with BootstrapFewShot optimization
# Status: COMPLETE
#
# Receipt:
# run_id: week6-day3-train-script
# inputs: [DSPY-INTEGRATION-STRATEGY.md (Training Pipeline), all signature modules]
# tools_used: [Write]
# changes: Created train_agent(), train_all_p0_agents(), main() CLI with 6-phase pipeline
