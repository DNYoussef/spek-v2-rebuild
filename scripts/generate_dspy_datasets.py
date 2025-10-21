"""
Generate DSPy training datasets for Drone→Princess communication paths.

Creates 50 training examples for each of 11 communication paths:
- Dev Hive: coder, reviewer, debugger, integration-engineer → princess-dev
- Quality Hive: tester, nasa-enforcer, theater-detector, fsm-analyzer → princess-quality
- Coordination Hive: orchestrator, planner, cost-tracker → princess-coordination

Week 6 Day 1
Version: 8.0.0
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any


# ============================================================================
# Dataset Templates and Generators
# ============================================================================

def generate_reviewer_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for reviewer→princess-dev path."""
    examples = []

    # Success examples (40)
    for i in range(1, 41):
        if i % 5 == 0:  # Every 5th is perfect score
            score = round(random.uniform(95, 100), 1)
            issues = []
            critical, high, medium, low = 0, 0, 0, 0
        elif i % 3 == 0:  # Every 3rd has minor issues
            score = round(random.uniform(85, 94), 1)
            issues = random.randint(1, 3)
            critical, high, medium, low = 0, 0, random.randint(0, 2), random.randint(1, 2)
        else:
            score = round(random.uniform(90, 95), 1)
            issues = random.randint(0, 2)
            critical, high, medium, low = 0, 0, random.randint(0, 1), random.randint(0, 1)

        examples.append({
            "example_id": i,
            "drone_id": "reviewer",
            "task_completed": f"review-code-{i}",
            "drone_results": {
                "success": True,
                "files_reviewed": random.randint(1, 5),
                "issues_found": issues,
                "critical_issues": critical,
                "high_issues": high,
                "medium_issues": medium,
                "low_issues": low,
                "overall_score": score,
                "nasa_compliance": round(random.uniform(92, 100), 1),
                "type_coverage": random.randint(95, 100),
                "execution_time_ms": random.randint(3000, 8000)
            },
            "expected_aggregated_result": {
                "phase": "review",
                "status": "complete" if score >= 85 else "needs_rework",
                "summary": f"Code review complete with overall score {score}/100. Found {issues} issues.",
                "quality_metrics": {
                    "review_score": score,
                    "nasa_compliance": round(random.uniform(92, 100), 1),
                    "type_coverage": random.randint(95, 100),
                    "critical_issues": critical,
                    "total_issues": issues
                },
                "next_phase": "integrate" if score >= 90 else "code",
                "blockers": [] if score >= 85 else [f"Address {issues} code quality issues"],
                "recommendations": ["Deploy to staging" if score >= 95 else "Address medium priority issues"]
            }
        })

    # Failure examples (10)
    for i in range(41, 51):
        score = round(random.uniform(50, 79), 1)
        issues = random.randint(5, 15)
        critical = random.randint(1, 3)
        high = random.randint(2, 5)

        examples.append({
            "example_id": i,
            "drone_id": "reviewer",
            "task_completed": f"review-code-{i}",
            "drone_results": {
                "success": False,
                "files_reviewed": random.randint(1, 5),
                "issues_found": issues,
                "critical_issues": critical,
                "high_issues": high,
                "medium_issues": random.randint(2, 5),
                "low_issues": random.randint(1, 3),
                "overall_score": score,
                "nasa_compliance": round(random.uniform(70, 89), 1),
                "type_coverage": random.randint(60, 90),
                "execution_time_ms": random.randint(3000, 8000)
            },
            "expected_aggregated_result": {
                "phase": "review",
                "status": "blocked",
                "summary": f"Code review failed with score {score}/100. Found {critical} critical and {high} high priority issues.",
                "quality_metrics": {
                    "review_score": score,
                    "nasa_compliance": round(random.uniform(70, 89), 1),
                    "type_coverage": random.randint(60, 90),
                    "critical_issues": critical,
                    "total_issues": issues
                },
                "next_phase": "code",
                "blockers": [
                    f"Fix {critical} critical security/NASA violations",
                    f"Address {high} high priority code quality issues"
                ],
                "recommendations": [
                    "Refactor functions exceeding LOC limits",
                    "Add missing type hints",
                    "Address security vulnerabilities"
                ]
            }
        })

    return examples


def generate_tester_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for tester→princess-quality path."""
    examples = []

    for i in range(1, 51):
        if i <= 40:  # 80% success
            coverage = random.randint(85, 100)
            passed = random.randint(15, 25)
            failed = random.randint(0, 2)
            success = True
            status = "complete"
        else:  # 20% failure
            coverage = random.randint(50, 79)
            passed = random.randint(5, 15)
            failed = random.randint(3, 10)
            success = False
            status = "blocked"

        total = passed + failed

        examples.append({
            "example_id": i,
            "drone_id": "tester",
            "task_completed": f"test-suite-{i}",
            "drone_results": {
                "success": success,
                "tests_total": total,
                "tests_passed": passed,
                "tests_failed": failed,
                "coverage_percent": coverage,
                "test_types": {
                    "unit": random.randint(10, 20),
                    "integration": random.randint(3, 8),
                    "e2e": random.randint(0, 3)
                },
                "execution_time_ms": random.randint(5000, 15000)
            },
            "expected_aggregated_result": {
                "phase": "test",
                "status": status,
                "summary": f"Test suite {'passed' if success else 'failed'}: {passed}/{total} tests passed, {coverage}% coverage.",
                "quality_metrics": {
                    "test_coverage": coverage,
                    "test_pass_rate": round((passed / total) * 100, 1),
                    "tests_total": total,
                    "tests_failed": failed
                },
                "next_phase": "deploy" if success and coverage >= 90 else "code",
                "blockers": [] if success else [f"Fix {failed} failing tests", "Increase coverage to ≥80%"],
                "recommendations": ["Add edge case tests" if success else "Debug failing test scenarios"]
            }
        })

    return examples


def generate_debugger_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for debugger→princess-dev path."""
    examples = []

    for i in range(1, 51):
        if i <= 38:  # 76% success
            bugs_fixed = random.randint(1, 5)
            bugs_remaining = 0
            success = True
            status = "complete"
        elif i <= 44:  # 12% partial
            bugs_fixed = random.randint(2, 4)
            bugs_remaining = random.randint(1, 2)
            success = True
            status = "partial"
        else:  # 12% failure
            bugs_fixed = random.randint(0, 1)
            bugs_remaining = random.randint(3, 6)
            success = False
            status = "blocked"

        examples.append({
            "example_id": i,
            "drone_id": "debugger",
            "task_completed": f"fix-bugs-{i}",
            "drone_results": {
                "success": success,
                "bugs_fixed": bugs_fixed,
                "bugs_remaining": bugs_remaining,
                "root_causes_identified": bugs_fixed,
                "files_modified": random.randint(1, 4),
                "tests_added": random.randint(bugs_fixed, bugs_fixed + 2),
                "execution_time_ms": random.randint(8000, 20000)
            },
            "expected_aggregated_result": {
                "phase": "debug",
                "status": status,
                "summary": f"Fixed {bugs_fixed} bugs, {bugs_remaining} remaining. {'All issues resolved.' if bugs_remaining == 0 else f'{bugs_remaining} issues need further investigation.'}",
                "quality_metrics": {
                    "bugs_fixed": bugs_fixed,
                    "bugs_remaining": bugs_remaining,
                    "fix_rate": round((bugs_fixed / (bugs_fixed + bugs_remaining)) * 100, 1) if (bugs_fixed + bugs_remaining) > 0 else 0,
                    "tests_added": random.randint(bugs_fixed, bugs_fixed + 2)
                },
                "next_phase": "review" if bugs_remaining == 0 else "debug",
                "blockers": [] if bugs_remaining == 0 else [f"Debug {bugs_remaining} remaining issues"],
                "recommendations": ["Proceed to code review" if bugs_remaining == 0 else "Continue debugging session"]
            }
        })

    return examples


def generate_integration_engineer_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for integration-engineer→princess-dev path."""
    examples = []

    for i in range(1, 51):
        if i <= 40:  # 80% success
            conflicts = random.randint(0, 2)
            success = True
            status = "complete"
        else:  # 20% failure
            conflicts = random.randint(3, 8)
            success = False
            status = "blocked"

        examples.append({
            "example_id": i,
            "drone_id": "integration-engineer",
            "task_completed": f"integrate-feature-{i}",
            "drone_results": {
                "success": success,
                "files_merged": random.randint(3, 12),
                "merge_conflicts": conflicts,
                "conflicts_resolved": conflicts if success else 0,
                "tests_passed": success,
                "integration_tests_run": random.randint(10, 25),
                "execution_time_ms": random.randint(6000, 18000)
            },
            "expected_aggregated_result": {
                "phase": "integrate",
                "status": status,
                "summary": f"Integration {'successful' if success else 'blocked'}. {conflicts} conflicts {'resolved' if success else 'detected'}.",
                "quality_metrics": {
                    "files_integrated": random.randint(3, 12),
                    "conflicts_resolved": conflicts if success else 0,
                    "integration_test_pass_rate": 100 if success else random.randint(60, 85)
                },
                "next_phase": "deploy" if success else "code",
                "blockers": [] if success else [f"Resolve {conflicts} merge conflicts", "Fix failing integration tests"],
                "recommendations": ["Deploy to staging" if success else "Coordinate with feature branch owner"]
            }
        })

    return examples


def generate_nasa_enforcer_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for nasa-enforcer→princess-quality path."""
    examples = []

    for i in range(1, 51):
        if i <= 42:  # 84% pass
            compliance = round(random.uniform(92, 100), 1)
            violations = random.randint(0, 2)
            success = True
            status = "pass"
        else:  # 16% fail
            compliance = round(random.uniform(70, 89), 1)
            violations = random.randint(3, 8)
            success = False
            status = "fail"

        examples.append({
            "example_id": i,
            "drone_id": "nasa-enforcer",
            "task_completed": f"nasa-check-{i}",
            "drone_results": {
                "success": success,
                "compliance_percent": compliance,
                "functions_checked": random.randint(15, 40),
                "violations_found": violations,
                "violations": [
                    {"function": f"func_{j}", "rule": "max_function_loc", "actual": random.randint(61, 85)}
                    for j in range(violations)
                ],
                "execution_time_ms": random.randint(2000, 5000)
            },
            "expected_aggregated_result": {
                "phase": "nasa_compliance",
                "status": status,
                "summary": f"NASA Rule 10 compliance: {compliance}%. {violations} violations found.",
                "quality_metrics": {
                    "nasa_compliance": compliance,
                    "target_compliance": 92.0,
                    "violations": violations,
                    "functions_compliant": random.randint(15, 40) - violations
                },
                "next_phase": "deploy" if success else "code",
                "blockers": [] if success else [f"Fix {violations} NASA Rule 10 violations"],
                "recommendations": ["Excellent compliance" if compliance >= 95 else "Refactor functions exceeding 60 LOC"]
            }
        })

    return examples


def generate_theater_detector_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for theater-detector→princess-quality path."""
    examples = []

    for i in range(1, 51):
        if i <= 45:  # 90% clean
            score = random.randint(0, 10)
            patterns = random.randint(0, 2)
            success = True
            status = "clean"
        else:  # 10% theatrical
            score = random.randint(50, 100)
            patterns = random.randint(5, 15)
            success = False
            status = "theatrical"

        examples.append({
            "example_id": i,
            "drone_id": "theater-detector",
            "task_completed": f"theater-scan-{i}",
            "drone_results": {
                "success": success,
                "theater_score": score,
                "theatrical_patterns": patterns,
                "todo_comments": random.randint(0, patterns),
                "placeholder_code": random.randint(0, patterns // 2),
                "mock_implementations": random.randint(0, patterns // 2),
                "execution_time_ms": random.randint(1500, 4000)
            },
            "expected_aggregated_result": {
                "phase": "theater_detection",
                "status": status,
                "summary": f"Theater score: {score}/100. {'Code is production-ready.' if score < 30 else f'Found {patterns} theatrical patterns.'}",
                "quality_metrics": {
                    "theater_score": score,
                    "threshold": 30,
                    "patterns_detected": patterns
                },
                "next_phase": "deploy" if success else "code",
                "blockers": [] if success else [f"Remove {patterns} theatrical code patterns"],
                "recommendations": ["Code quality excellent" if score < 10 else "Replace TODOs and placeholders with real implementation"]
            }
        })

    return examples


def generate_fsm_analyzer_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for fsm-analyzer→princess-quality path."""
    examples = []

    for i in range(1, 51):
        if i <= 43:  # 86% justified
            states = random.randint(3, 8)
            transitions = random.randint(5, 15)
            criteria_met = random.randint(3, 5)
            justified = True
            status = "justified"
        else:  # 14% unjustified
            states = random.randint(1, 2)
            transitions = random.randint(1, 4)
            criteria_met = random.randint(0, 2)
            justified = False
            status = "unjustified"

        examples.append({
            "example_id": i,
            "drone_id": "fsm-analyzer",
            "task_completed": f"fsm-check-{i}",
            "drone_results": {
                "success": justified,
                "fsm_justified": justified,
                "states_count": states,
                "transitions_count": transitions,
                "criteria_met": criteria_met,
                "decision_matrix_score": random.randint(3, 5) if justified else random.randint(0, 2),
                "execution_time_ms": random.randint(1000, 3000)
            },
            "expected_aggregated_result": {
                "phase": "fsm_validation",
                "status": status,
                "summary": f"FSM {'justified' if justified else 'not justified'}: {states} states, {transitions} transitions, {criteria_met}/5 criteria met.",
                "quality_metrics": {
                    "fsm_complexity": states * transitions,
                    "criteria_met": criteria_met,
                    "threshold": 3
                },
                "next_phase": "deploy" if justified else "code",
                "blockers": [] if justified else [f"FSM does not meet ≥3 decision matrix criteria"],
                "recommendations": ["FSM appropriately used" if justified else "Replace with simple if/else logic"]
            }
        })

    return examples


def generate_orchestrator_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for orchestrator→princess-coordination path."""
    examples = []

    for i in range(1, 51):
        if i <= 40:  # 80% success
            phases_completed = random.randint(4, 8)
            phases_total = phases_completed
            success = True
            status = "complete"
        else:  # 20% partial
            phases_completed = random.randint(2, 5)
            phases_total = random.randint(6, 10)
            success = False
            status = "partial"

        examples.append({
            "example_id": i,
            "drone_id": "orchestrator",
            "task_completed": f"workflow-{i}",
            "drone_results": {
                "success": success,
                "workflow_id": f"wf-{i}",
                "phases_completed": phases_completed,
                "phases_total": phases_total,
                "agents_coordinated": random.randint(3, 8),
                "total_execution_time_ms": random.randint(20000, 60000),
                "bottlenecks": [] if success else [f"Phase {random.randint(1, phases_completed)} delayed"]
            },
            "expected_aggregated_result": {
                "phase": "orchestration",
                "status": status,
                "summary": f"Workflow {'completed' if success else 'partially completed'}: {phases_completed}/{phases_total} phases.",
                "quality_metrics": {
                    "completion_rate": round((phases_completed / phases_total) * 100, 1),
                    "agents_utilized": random.randint(3, 8),
                    "average_phase_time_ms": random.randint(3000, 8000)
                },
                "next_phase": "complete" if success else "orchestrate",
                "blockers": [] if success else [f"Complete remaining {phases_total - phases_completed} phases"],
                "recommendations": ["Workflow successful" if success else "Review bottleneck phases"]
            }
        })

    return examples


def generate_planner_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for planner→princess-coordination path."""
    examples = []

    for i in range(1, 51):
        if i <= 42:  # 84% success
            tasks = random.randint(8, 20)
            feasible = True
            success = True
            status = "complete"
        else:  # 16% infeasible
            tasks = random.randint(15, 30)
            feasible = False
            success = False
            status = "infeasible"

        examples.append({
            "example_id": i,
            "drone_id": "planner",
            "task_completed": f"plan-{i}",
            "drone_results": {
                "success": success,
                "plan_feasible": feasible,
                "tasks_generated": tasks,
                "estimated_duration_hours": random.randint(10, 100),
                "resource_requirements": {
                    "agents": random.randint(3, 10),
                    "compute": f"{random.randint(1, 8)}GB RAM"
                },
                "dependencies_mapped": random.randint(5, 15),
                "execution_time_ms": random.randint(3000, 8000)
            },
            "expected_aggregated_result": {
                "phase": "planning",
                "status": status,
                "summary": f"Plan {'generated successfully' if success else 'infeasible'}: {tasks} tasks, {random.randint(10, 100)}h estimated.",
                "quality_metrics": {
                    "tasks_count": tasks,
                    "feasibility_score": 100 if feasible else random.randint(40, 70),
                    "dependencies_resolved": random.randint(5, 15)
                },
                "next_phase": "orchestrate" if success else "planning",
                "blockers": [] if success else ["Resource constraints exceed capacity", "Timeline unrealistic"],
                "recommendations": ["Proceed to execution" if success else "Reduce scope or extend timeline"]
            }
        })

    return examples


def generate_cost_tracker_examples() -> List[Dict[str, Any]]:
    """Generate 50 examples for cost-tracker→princess-coordination path."""
    examples = []

    for i in range(1, 51):
        if i <= 43:  # 86% within budget
            cost = round(random.uniform(10, 90), 2)
            budget = 100
            within_budget = True
            status = "within_budget"
        else:  # 14% over budget
            cost = round(random.uniform(105, 150), 2)
            budget = 100
            within_budget = False
            status = "over_budget"

        examples.append({
            "example_id": i,
            "drone_id": "cost-tracker",
            "task_completed": f"cost-analysis-{i}",
            "drone_results": {
                "success": within_budget,
                "total_cost": cost,
                "budget": budget,
                "within_budget": within_budget,
                "breakdown": {
                    "compute": round(cost * 0.4, 2),
                    "storage": round(cost * 0.3, 2),
                    "api_calls": round(cost * 0.3, 2)
                },
                "execution_time_ms": random.randint(1500, 4000)
            },
            "expected_aggregated_result": {
                "phase": "cost_tracking",
                "status": status,
                "summary": f"Cost tracking: ${cost}/${budget} ({'within' if within_budget else 'exceeds'} budget).",
                "quality_metrics": {
                    "cost_utilization_percent": round((cost / budget) * 100, 1),
                    "budget_remaining": max(0, budget - cost),
                    "cost_efficiency": "good" if within_budget else "poor"
                },
                "next_phase": "complete" if within_budget else "planning",
                "blockers": [] if within_budget else [f"Cost exceeds budget by ${round(cost - budget, 2)}"],
                "recommendations": ["Budget management excellent" if cost < 80 else "Optimize resource usage to reduce costs"]
            }
        })

    return examples


# ============================================================================
# Dataset Generation
# ============================================================================

DATASETS = {
    # Dev Hive → Princess-Dev
    "coder_to_princess_dev": {
        "description": "Coder reports implementation results to Princess-Dev",
        "princess_id": "princess-dev",
        "generator": None  # Already created manually
    },
    "reviewer_to_princess_dev": {
        "description": "Reviewer reports code review results to Princess-Dev",
        "princess_id": "princess-dev",
        "generator": generate_reviewer_examples
    },
    "debugger_to_princess_dev": {
        "description": "Debugger reports bug fix results to Princess-Dev",
        "princess_id": "princess-dev",
        "generator": generate_debugger_examples
    },
    "integration_engineer_to_princess_dev": {
        "description": "Integration-Engineer reports merge results to Princess-Dev",
        "princess_id": "princess-dev",
        "generator": generate_integration_engineer_examples
    },

    # Quality Hive → Princess-Quality
    "tester_to_princess_quality": {
        "description": "Tester reports test results to Princess-Quality",
        "princess_id": "princess-quality",
        "generator": generate_tester_examples
    },
    "nasa_enforcer_to_princess_quality": {
        "description": "NASA-Enforcer reports compliance results to Princess-Quality",
        "princess_id": "princess-quality",
        "generator": generate_nasa_enforcer_examples
    },
    "theater_detector_to_princess_quality": {
        "description": "Theater-Detector reports mock code scan to Princess-Quality",
        "princess_id": "princess-quality",
        "generator": generate_theater_detector_examples
    },
    "fsm_analyzer_to_princess_quality": {
        "description": "FSM-Analyzer reports state machine validation to Princess-Quality",
        "princess_id": "princess-quality",
        "generator": generate_fsm_analyzer_examples
    },

    # Coordination Hive → Princess-Coordination
    "orchestrator_to_princess_coordination": {
        "description": "Orchestrator reports workflow status to Princess-Coordination",
        "princess_id": "princess-coordination",
        "generator": generate_orchestrator_examples
    },
    "planner_to_princess_coordination": {
        "description": "Planner reports task planning results to Princess-Coordination",
        "princess_id": "princess-coordination",
        "generator": generate_planner_examples
    },
    "cost_tracker_to_princess_coordination": {
        "description": "Cost-Tracker reports budget analysis to Princess-Coordination",
        "princess_id": "princess-coordination",
        "generator": generate_cost_tracker_examples
    }
}


def generate_all_datasets(output_dir: Path) -> Dict[str, Any]:
    """
    Generate all DSPy training datasets.

    Args:
        output_dir: Output directory for datasets

    Returns:
        Summary statistics
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "total_datasets": 0,
        "total_examples": 0,
        "datasets": {}
    }

    for dataset_name, config in DATASETS.items():
        if config["generator"] is None:
            print(f"Skipping {dataset_name} (manually created)")
            continue

        print(f"Generating {dataset_name}...")

        examples = config["generator"]()

        # Calculate success/failure ratio
        success_count = sum(1 for ex in examples if ex["drone_results"]["success"])
        failure_count = len(examples) - success_count

        # Create dataset
        dataset = {
            "communication_path": dataset_name.replace("_to_", "→").replace("_", "-"),
            "description": config["description"],
            "drone_id": dataset_name.split("_to_")[0].replace("_", "-"),
            "princess_id": config["princess_id"],
            "total_examples": len(examples),
            "success_ratio": {
                "success": success_count,
                "failure": failure_count
            },
            "examples": examples
        }

        # Write to file
        output_file = output_dir / f"{dataset_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Generated {len(examples)} examples ({success_count} success, {failure_count} failure)")

        summary["total_datasets"] += 1
        summary["total_examples"] += len(examples)
        summary["datasets"][dataset_name] = {
            "examples": len(examples),
            "success": success_count,
            "failure": failure_count,
            "file": str(output_file)
        }

    return summary


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    output_dir = Path(__file__).parent.parent / "datasets" / "dspy"

    print("=" * 80)
    print("DSPy Training Dataset Generator")
    print("=" * 80)
    print()

    summary = generate_all_datasets(output_dir)

    print()
    print("=" * 80)
    print("Generation Complete")
    print("=" * 80)
    print(f"Total Datasets: {summary['total_datasets']}")
    print(f"Total Examples: {summary['total_examples']}")
    print()
    print("Datasets Generated:")
    for name, stats in summary["datasets"].items():
        print(f"  - {name}: {stats['examples']} examples ({stats['success']} success, {stats['failure']} failure)")
    print()
    print(f"Output Directory: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
