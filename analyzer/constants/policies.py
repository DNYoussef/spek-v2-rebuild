"""
Analysis Policies - Policy definitions and mappings

Defines analysis policies (nasa-compliance, strict, standard, lenient).

NASA Rule 3 Compliance: ≤150 LOC target
Version: 6.0.0 (Week 2 Day 1)
"""

# Standard unified policy names
UNIFIED_POLICY_NAMES = [
    "nasa-compliance",  # Highest safety standards (NASA JPL Power of Ten)
    "strict",  # Strict core analysis
    "standard",  # Balanced service defaults
    "lenient",  # Relaxed experimental settings
]

# Legacy policy name mappings for backward compatibility
LEGACY_POLICY_MAPPINGS = {
    # Old v5 policy names → new v6 canonical names
    "nasa": "nasa-compliance",
    "production": "strict",
    "default": "standard",
    "experimental": "lenient",
    "relaxed": "lenient",
}

# Reverse mapping for API responses
CANONICAL_TO_LEGACY = {v: k for k, v in LEGACY_POLICY_MAPPINGS.items()}

# Policy configuration presets
POLICY_CONFIGS = {
    "nasa-compliance": {
        "max_function_lines": 60,
        "min_assertions": 2,
        "allow_recursion": False,
        "require_fixed_loops": True,
        "nasa_compliance_threshold": 0.92,
        "theater_threshold": 40,
        "god_object_threshold": 0,
    },
    "strict": {
        "max_function_lines": 100,
        "min_assertions": 1,
        "allow_recursion": False,
        "require_fixed_loops": True,
        "nasa_compliance_threshold": 0.85,
        "theater_threshold": 50,
        "god_object_threshold": 2,
    },
    "standard": {
        "max_function_lines": 200,
        "min_assertions": 0,
        "allow_recursion": True,
        "require_fixed_loops": False,
        "nasa_compliance_threshold": 0.75,
        "theater_threshold": 60,
        "god_object_threshold": 5,
    },
    "lenient": {
        "max_function_lines": 300,
        "min_assertions": 0,
        "allow_recursion": True,
        "require_fixed_loops": False,
        "nasa_compliance_threshold": 0.60,
        "theater_threshold": 70,
        "god_object_threshold": 10,
    },
}


def normalize_policy_name(policy: str) -> str:
    """
    Normalize legacy policy names to canonical v6 names.

    Args:
        policy: Policy name (legacy or canonical)

    Returns:
        Canonical policy name

    Raises:
        ValueError: If policy name is invalid
    """
    # Already canonical
    if policy in UNIFIED_POLICY_NAMES:
        return policy

    # Legacy mapping
    if policy in LEGACY_POLICY_MAPPINGS:
        import warnings
        canonical = LEGACY_POLICY_MAPPINGS[policy]
        warnings.warn(
            f"Policy '{policy}' is deprecated. Use '{canonical}' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return canonical

    # Invalid policy
    raise ValueError(
        f"Unknown policy: '{policy}'. "
        f"Valid policies: {', '.join(UNIFIED_POLICY_NAMES)}"
    )


def get_policy_config(policy: str) -> dict:
    """
    Get configuration for a policy.

    Args:
        policy: Policy name

    Returns:
        Policy configuration dictionary
    """
    canonical = normalize_policy_name(policy)
    return POLICY_CONFIGS[canonical].copy()
