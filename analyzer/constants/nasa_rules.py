"""
NASA POT10 Rules - NASA Power of Ten rule definitions

Defines NASA JPL Power of Ten safety-critical coding rules.

NASA Rule 3 Compliance: ≤120 LOC target
Version: 6.0.0 (Week 2 Day 1)
"""

# NASA Power of Ten Rules (subset enforced by analyzer)
NASA_RULES = {
    "RULE_2": {
        "title": "No dynamic memory allocation after initialization",
        "description": "All memory allocation shall be done during initialization",
        "severity": "critical",
        "enforced": False,  # Python doesn't expose manual memory management
    },
    "RULE_3": {
        "title": "Function length limit",
        "description": "Functions shall not exceed 60 lines of code",
        "severity": "high",
        "enforced": True,
        "threshold": 60,
    },
    "RULE_4": {
        "title": "Minimum assertions",
        "description": "Functions shall have at least 2 assertions (critical paths)",
        "severity": "medium",
        "enforced": True,
        "threshold": 2,
    },
    "RULE_5": {
        "title": "No recursion",
        "description": "No function shall call itself directly or indirectly",
        "severity": "high",
        "enforced": True,
    },
    "RULE_6": {
        "title": "Parameter limit",
        "description": "Functions shall not exceed 6 parameters",
        "severity": "medium",
        "enforced": True,
        "threshold": 6,
    },
    "RULE_7": {
        "title": "Fixed loop bounds",
        "description": "All loops shall have fixed upper bounds",
        "severity": "high",
        "enforced": True,
    },
    "RULE_10": {
        "title": "Compiler warnings as errors",
        "description": "All compiler warnings shall be treated as errors",
        "severity": "critical",
        "enforced": True,
    },
}

# NASA compliance thresholds
NASA_COMPLIANCE_THRESHOLDS = {
    "excellent": 0.95,  # ≥95% compliance
    "good": 0.90,  # ≥90% compliance
    "acceptable": 0.80,  # ≥80% compliance
    "needs_improvement": 0.80,  # <80% compliance
}

# NASA rule violation messages
NASA_VIOLATION_MESSAGES = {
    "RULE_3": "Function exceeds {threshold} lines (found: {actual})",
    "RULE_4": "Function has < {threshold} assertions (found: {actual})",
    "RULE_5": "Function uses recursion (not allowed)",
    "RULE_6": "Function exceeds {threshold} parameters (found: {actual})",
    "RULE_7": "Loop has unbounded upper limit",
    "RULE_10": "Compiler/linter warning present: {warning}",
}


def get_nasa_rule(rule_id: str) -> dict:
    """Get NASA rule definition by ID."""
    return NASA_RULES.get(rule_id, {})


def is_rule_enforced(rule_id: str) -> bool:
    """Check if NASA rule is enforced."""
    rule = NASA_RULES.get(rule_id, {})
    return rule.get("enforced", False)
