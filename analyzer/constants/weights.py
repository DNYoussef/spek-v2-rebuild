"""
Violation Weights - Severity weights and mappings

Defines violation severity levels and weighted scoring.

NASA Rule 3 Compliance: ≤100 LOC target
Version: 6.0.0 (Week 2 Day 1)
"""

# Violation weight constants (for aggregated scoring)
VIOLATION_WEIGHTS = {
    "critical": 10,
    "high": 5,
    "medium": 2,
    "low": 1
}

# 10-level NASA-compliant severity system
SEVERITY_LEVELS = {
    10: "CATASTROPHIC",  # God Objects >1000 LOC, critical security flaws
    9: "CRITICAL",  # God Objects, Globals >5, recursion
    8: "MAJOR",  # Parameters >10 (NASA violation)
    7: "SIGNIFICANT",  # Functions >60 LOC (NASA violation)
    6: "MODERATE",  # Magic numbers in conditionals
    5: "MINOR",  # Parameters 6-10
    4: "TRIVIAL",  # Basic magic literals
    3: "INFORMATIONAL",  # Style violations
    2: "ADVISORY",  # Best practice suggestions
    1: "NOTICE",  # Documentation recommendations
}

# Reverse mapping (severity name → level)
SEVERITY_NAME_TO_LEVEL = {v: k for k, v in SEVERITY_LEVELS.items()}

# Severity to weight mapping (for aggregation)
SEVERITY_TO_WEIGHT = {
    10: "critical",
    9: "critical",
    8: "high",
    7: "high",
    6: "medium",
    5: "medium",
    4: "low",
    3: "low",
    2: "low",
    1: "low",
}


def calculate_weighted_score(violations: list) -> float:
    """
    Calculate weighted violation score.

    Args:
        violations: List of violation dicts with 'severity' key

    Returns:
        Weighted score (lower is better)
    """
    total = 0
    for violation in violations:
        severity = violation.get("severity", "low")
        weight = VIOLATION_WEIGHTS.get(severity, 1)
        total += weight

    return float(total)


def severity_level_to_weight(level: int) -> str:
    """
    Convert severity level (1-10) to weight category.

    Args:
        level: Severity level (1-10)

    Returns:
        Weight category (critical, high, medium, low)
    """
    return SEVERITY_TO_WEIGHT.get(level, "low")
