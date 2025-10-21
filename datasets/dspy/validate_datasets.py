#!/usr/bin/env python3
"""
Dataset Validation Script for Princess-Dev Delegation Training Data

This script validates the structure, completeness, and quality of DSPy training datasets
for Princess-Dev's delegation patterns to drone agents.

Usage:
    python validate_datasets.py

Returns:
    Exit code 0 if all validations pass, 1 otherwise
"""

import json
import os
import sys
from typing import Dict, List, Tuple
from collections import Counter


class DatasetValidator:
    """Validates Princess-Dev delegation training datasets"""

    REQUIRED_EXAMPLE_FIELDS = ['id', 'phase', 'context', 'expected_drone_task']
    REQUIRED_TASK_FIELDS = [
        'drone_id', 'task_type', 'description', 'specifications',
        'dependencies', 'estimated_minutes', 'quality_gates'
    ]

    VALID_PHASES = {
        'coder': ['code'],
        'reviewer': ['review'],
        'debugger': ['debug'],
        'integration_engineer': ['integration'],
        'integration-engineer': ['integration']
    }

    TIME_RANGES = {
        'coder': (15, 60),
        'reviewer': (15, 60),
        'debugger': (15, 60),
        'integration_engineer': (30, 60),
        'integration-engineer': (30, 60)
    }

    def __init__(self, datasets_dir: str):
        self.datasets_dir = datasets_dir
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Validate all datasets and return True if all pass"""
        print("Princess-Dev Delegation Dataset Validator")
        print("=" * 80)
        print()

        files = [
            'princess_dev_to_coder.json',
            'princess_dev_to_reviewer.json',
            'princess_dev_to_debugger.json',
            'princess_dev_to_integration_engineer.json'
        ]

        all_valid = True

        for filename in files:
            drone_type = filename.split('_to_')[1].replace('.json', '')
            print(f"Validating: {filename}")

            filepath = os.path.join(self.datasets_dir, filename)

            if not os.path.exists(filepath):
                self.errors.append(f"{filename}: File not found")
                all_valid = False
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self.errors.append(f"{filename}: Invalid JSON - {e}")
                all_valid = False
                continue
            except Exception as e:
                self.errors.append(f"{filename}: Error reading file - {e}")
                all_valid = False
                continue

            # Validate dataset structure
            is_valid = self.validate_dataset(data, drone_type, filename)
            all_valid = all_valid and is_valid

            print()

        # Print summary
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  [ERROR] {error}")

        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  [WARN] {warning}")

        if not self.errors and not self.warnings:
            print("\n[PASS] All datasets valid! Ready for DSPy training.")
        elif not self.errors:
            print(f"\n[PASS] All datasets valid with {len(self.warnings)} warnings.")
        else:
            print(f"\n[FAIL] Validation failed with {len(self.errors)} errors.")

        return all_valid and len(self.errors) == 0

    def validate_dataset(self, data: Dict, drone_type: str, filename: str) -> bool:
        """Validate a single dataset"""
        is_valid = True

        # Check top-level fields
        if 'communication_path' not in data:
            self.errors.append(f"{filename}: Missing 'communication_path' field")
            is_valid = False

        if 'examples' not in data or not isinstance(data['examples'], list):
            self.errors.append(f"{filename}: Missing or invalid 'examples' field")
            return False

        examples = data['examples']

        # Check example count
        if len(examples) != 50:
            self.warnings.append(
                f"{filename}: Expected 50 examples, found {len(examples)}"
            )

        print(f"  Examples: {len(examples)}")

        # Validate each example
        valid_count = 0
        time_estimates = []
        quality_gate_counts = []
        dependency_counts = []

        for i, example in enumerate(examples):
            example_valid = self.validate_example(
                example, drone_type, filename, i + 1
            )

            if example_valid:
                valid_count += 1

                # Collect statistics
                task = example['expected_drone_task']
                time_estimates.append(task['estimated_minutes'])
                quality_gate_counts.append(len(task['quality_gates']))
                dependency_counts.append(len(task['dependencies']))

        print(f"  Valid: {valid_count}/{len(examples)} ({valid_count/len(examples)*100:.1f}%)")

        # Statistical validation
        if time_estimates:
            min_time, max_time = self.TIME_RANGES[drone_type]
            avg_time = sum(time_estimates) / len(time_estimates)

            print(f"  Time estimates: min={min(time_estimates)}, "
                  f"max={max(time_estimates)}, avg={avg_time:.1f}")

            if min(time_estimates) < min_time:
                self.warnings.append(
                    f"{filename}: Some time estimates below {min_time} minutes"
                )

            if max(time_estimates) > max_time:
                self.warnings.append(
                    f"{filename}: Some time estimates above {max_time} minutes"
                )

        if quality_gate_counts:
            avg_gates = sum(quality_gate_counts) / len(quality_gate_counts)
            print(f"  Quality gates: avg={avg_gates:.1f} per example")

            if avg_gates < 2.5:
                self.warnings.append(
                    f"{filename}: Low average quality gates ({avg_gates:.1f})"
                )

        if dependency_counts:
            avg_deps = sum(dependency_counts) / len(dependency_counts)
            print(f"  Dependencies: avg={avg_deps:.1f} per example")

        return is_valid and valid_count == len(examples)

    def validate_example(
        self, example: Dict, drone_type: str, filename: str, example_num: int
    ) -> bool:
        """Validate a single example"""
        is_valid = True

        # Check required fields
        for field in self.REQUIRED_EXAMPLE_FIELDS:
            if field not in example:
                self.errors.append(
                    f"{filename} example {example_num}: Missing field '{field}'"
                )
                is_valid = False

        if 'expected_drone_task' not in example:
            return False

        task = example['expected_drone_task']

        # Check task fields
        for field in self.REQUIRED_TASK_FIELDS:
            if field not in task:
                self.errors.append(
                    f"{filename} example {example_num}: Missing task field '{field}'"
                )
                is_valid = False

        # Validate drone_id matches (normalize underscores and hyphens)
        if 'drone_id' in task:
            normalized_task_id = task['drone_id'].replace('-', '_')
            normalized_drone_type = drone_type.replace('-', '_')
            if normalized_task_id != normalized_drone_type:
                self.errors.append(
                    f"{filename} example {example_num}: drone_id mismatch "
                    f"(expected '{drone_type}', got '{task['drone_id']}')"
                )
                is_valid = False

        # Validate phase
        if 'phase' in example:
            valid_phases = self.VALID_PHASES.get(drone_type, [])
            if example['phase'] not in valid_phases:
                self.errors.append(
                    f"{filename} example {example_num}: Invalid phase "
                    f"'{example['phase']}' (expected {valid_phases})"
                )
                is_valid = False

        # Validate time estimate
        if 'estimated_minutes' in task:
            time = task['estimated_minutes']
            if not isinstance(time, int) or time <= 0:
                self.errors.append(
                    f"{filename} example {example_num}: Invalid time estimate {time}"
                )
                is_valid = False

        # Validate quality gates
        if 'quality_gates' in task:
            gates = task['quality_gates']
            if not isinstance(gates, list) or len(gates) == 0:
                self.warnings.append(
                    f"{filename} example {example_num}: No quality gates defined"
                )

        # Validate dependencies
        if 'dependencies' in task:
            deps = task['dependencies']
            if not isinstance(deps, list):
                self.errors.append(
                    f"{filename} example {example_num}: Dependencies not a list"
                )
                is_valid = False

        return is_valid


def main():
    """Main entry point"""
    # Determine datasets directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = script_dir

    # Run validation
    validator = DatasetValidator(datasets_dir)
    is_valid = validator.validate_all()

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
