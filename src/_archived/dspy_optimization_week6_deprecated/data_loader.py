"""Training Data Loader for DSPy Optimization (Week 6 Day 3, v8.0.0)

Loads training datasets from JSON files and converts to DSPy Example format.
Supports train/validation split and quality filtering.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import dspy


@dataclass
class DatasetInfo:
    """Metadata about a loaded dataset."""

    agent_id: str
    total_examples: int
    train_examples: int
    val_examples: int
    avg_quality: float
    file_path: str


def load_training_dataset(
    dataset_path: str,
    min_quality: float = 70.0,  # Changed from 90.0 to include synthetic examples
    max_examples: Optional[int] = None
) -> Tuple[List[dspy.Example], DatasetInfo]:
    """Load training dataset from JSON file.

    Supports two dataset formats:
    1. Queen format: task_description, objective, expected_subtasks
    2. Princess/Drone format: phase, context, expected_drone_task

    Args:
        dataset_path: Path to dataset JSON file
        min_quality: Minimum quality label to include (default: 70.0)
        max_examples: Maximum examples to load (None = all)

    Returns:
        Tuple of (examples list, dataset info)

    Raises:
        FileNotFoundError: If dataset file not found
        ValueError: If dataset format invalid

    Example:
        >>> examples, info = load_training_dataset(
        ...     "datasets/dspy/queen_to_princess_dev.json"
        ... )
        >>> print(f"Loaded {len(examples)} examples for {info.agent_id}")
    """
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract agent ID from filename or data
    agent_id = data.get("agent_id", path.stem)  # Use filename if no agent_id
    raw_examples = data.get("examples", [])

    # Filter by quality if quality_label exists
    filtered = [
        ex for ex in raw_examples
        if ex.get("quality_label", 100) >= min_quality  # Default 100 if no label
    ]

    if max_examples:
        filtered = filtered[:max_examples]

    # Bug #5 FIX: Convert lists to tuples for hashability
    # DSPy's BootstrapFewShot requires all Example fields to be hashable for caching
    def make_hashable(obj):
        if isinstance(obj, dict):
            return {k: make_hashable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return tuple(make_hashable(item) for item in obj)
        else:
            return obj

    examples = []
    for ex in filtered:
        # Detect dataset format
        if "task_description" in ex and "objective" in ex:
            # Format 1: Queen datasets (queen_to_princess_X.json)
            task_description = ex.get("task_description", "")
            objective = ex.get("objective", "")
            expected_output = make_hashable(ex.get("expected_subtasks", []))

        elif "expected_drone_task" in ex:
            # Format 2: Princess/Drone datasets (princess_X_to_Y.json)
            drone_task = ex.get("expected_drone_task", {})
            context = ex.get("context", {})
            phase = ex.get("phase", "unknown")

            # Build comprehensive task_description from context + description
            task_description = f"Phase: {phase}\n"
            if context:
                task_description += f"Context: {json.dumps(context, indent=2)}\n"
            task_description += f"Task: {drone_task.get('description', '')}"

            # Extract objective from specifications
            specs = drone_task.get("specifications", {})
            objective = json.dumps(specs, indent=2) if specs else ""

            # Expected output is the full drone task
            expected_output = make_hashable(drone_task)

        else:
            # Unknown format - skip
            print(f"⚠️  Warning: Skipping example {ex.get('id', '?')} - unknown format")
            continue

        example = dspy.Example(
            task_description=task_description,
            objective=objective,
            expected_output=expected_output
        ).with_inputs("task_description", "objective")

        examples.append(example)

    avg_quality = (
        sum(ex.get("quality_label", 100) for ex in filtered) / len(filtered)
        if filtered else 100.0
    )

    info = DatasetInfo(
        agent_id=agent_id,
        total_examples=len(raw_examples),
        train_examples=len([ex for ex in examples]),  # All loaded examples are training
        val_examples=0,  # Validation split happens in split_train_val()
        avg_quality=avg_quality,
        file_path=str(path)
    )

    return examples, info


def load_all_p0_datasets(
    datasets_dir: str = "datasets/week6",
    min_quality: float = 90.0
) -> Dict[str, Tuple[List[dspy.Example], DatasetInfo]]:
    """Load all P0 agent training datasets.

    Args:
        datasets_dir: Directory containing dataset JSON files
        min_quality: Minimum quality label to include

    Returns:
        Dictionary mapping agent_id to (examples, info) tuple

    Example:
        >>> datasets = load_all_p0_datasets()
        >>> queen_examples, queen_info = datasets["queen"]
        >>> print(f"Queen: {len(queen_examples)} examples")
    """
    datasets_path = Path(datasets_dir)
    if not datasets_path.exists():
        raise FileNotFoundError(f"Datasets directory not found: {datasets_dir}")

    p0_agents = ["queen", "tester", "reviewer", "coder"]
    datasets = {}

    for agent_id in p0_agents:
        dataset_file = datasets_path / f"{agent_id}_training_dataset.json"

        if dataset_file.exists():
            try:
                examples, info = load_training_dataset(
                    str(dataset_file),
                    min_quality=min_quality
                )
                datasets[agent_id] = (examples, info)
                print(f"[OK] Loaded {agent_id}: {len(examples)} examples (avg quality: {info.avg_quality:.1f})")
            except Exception as e:
                print(f"[FAIL] Failed to load {agent_id}: {e}")
        else:
            print(f"[WARN] Dataset not found: {dataset_file}")

    return datasets


def split_train_val(
    examples: List[dspy.Example],
    val_ratio: float = 0.2
) -> Tuple[List[dspy.Example], List[dspy.Example]]:
    """Split examples into train and validation sets.

    Args:
        examples: List of DSPy examples
        val_ratio: Validation set ratio (default: 0.2 = 20%)

    Returns:
        Tuple of (train_examples, val_examples)

    Example:
        >>> train, val = split_train_val(examples, val_ratio=0.2)
        >>> print(f"Train: {len(train)}, Val: {len(val)}")
    """
    assert 0.0 < val_ratio < 1.0, "val_ratio must be between 0 and 1"

    total = len(examples)
    val_size = int(total * val_ratio)
    train_size = total - val_size

    return examples[:train_size], examples[train_size:]


def print_dataset_summary(datasets: Dict[str, Tuple[List[dspy.Example], DatasetInfo]]) -> None:
    """Print summary of loaded datasets.

    Args:
        datasets: Dictionary from load_all_p0_datasets()

    Example:
        >>> datasets = load_all_p0_datasets()
        >>> print_dataset_summary(datasets)
    """
    print("\n=== Dataset Summary ===")
    print(f"{'Agent':<12} {'Total':<8} {'Train':<8} {'Val':<8} {'Avg Quality':<12}")
    print("-" * 60)

    for agent_id, (examples, info) in datasets.items():
        print(
            f"{agent_id:<12} {info.total_examples:<8} "
            f"{info.train_examples:<8} {info.val_examples:<8} "
            f"{info.avg_quality:<12.1f}"
        )

    print(f"\nTotal datasets: {len(datasets)}")


# Version: 1.0
# Timestamp: 2025-10-08T00:00:00-04:00
# Agent/Model: Claude Sonnet 4.5
# Changes: Created data loader with DSPy Example conversion and train/val split
# Status: COMPLETE
#
# Receipt:
# run_id: week6-day3-data-loader
# inputs: [DSPY-INTEGRATION-STRATEGY.md (Data Loading), training_datasets.py]
# tools_used: [Write]
# changes: Created load_training_dataset(), load_all_p0_datasets(), split_train_val()
