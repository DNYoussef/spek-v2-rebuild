"""
Generate Training Datasets for P0 Agents

Creates realistic training datasets with proper payloads for DSPy optimization.
Saves datasets to JSON files for training pipeline.

Usage:
    python scripts/generate_training_datasets.py

Week 6 Day 2
Version: 8.0.0
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dspy_optimization.training_datasets import create_dataset_generator


def main():
    """Generate all P0 agent training datasets."""
    print("="*80)
    print("TRAINING DATASET GENERATION - P0 AGENTS")
    print("Week 6 Day 2")
    print("="*80)
    print()

    generator = create_dataset_generator(output_dir="datasets/week6")

    # Generate datasets for each P0 agent
    agents = {
        "queen": ("Queen", 100),
        "tester": ("Tester", 100),
        "reviewer": ("Reviewer", 100),
        "coder": ("Coder", 100)
    }

    for agent_id, (agent_name, size) in agents.items():
        print(f"\nGenerating {agent_name} dataset ({size} examples)...")
        print("-"*80)

        if agent_id == "queen":
            dataset = generator.generate_queen_dataset(size=size)
        elif agent_id == "tester":
            dataset = generator.generate_tester_dataset(size=size)
        elif agent_id == "reviewer":
            dataset = generator.generate_reviewer_dataset(size=size)
        elif agent_id == "coder":
            dataset = generator.generate_coder_dataset(size=size)

        # Save dataset
        generator.save_dataset(dataset)

    print("\n" + "="*80)
    print("Dataset Generation Complete!")
    print("="*80)
    print("\nDatasets created in: datasets/week6/")
    print("\nNext steps:")
    print("1. Review generated datasets")
    print("2. Implement DSPy signatures for each agent")
    print("3. Build training pipeline")
    print("4. Begin optimization training")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
