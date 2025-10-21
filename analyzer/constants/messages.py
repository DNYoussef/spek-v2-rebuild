"""
User Messages - Error messages and templates

User-facing messages, error templates, detection messages.

NASA Rule 3 Compliance: ≤150 LOC target
Version: 6.0.0 (Week 2 Day 1)
"""

# Exit codes
EXIT_SUCCESS = 0
EXIT_VIOLATIONS_FOUND = 1
EXIT_ERROR = 2
EXIT_INVALID_ARGUMENTS = 3
EXIT_CONFIGURATION_ERROR = 4
EXIT_INTERRUPTED = 130

# Detection message templates
DETECTION_MESSAGES = {
    "magic_literal": "Magic literal '{value}' found at line {line}. Consider using a named constant.",
    "position_coupling": "Function '{function}' has {count} parameters. Consider reducing to ≤{threshold}.",
    "god_object": "Class '{class}' has {methods} methods (>{threshold}). Consider splitting responsibilities.",
    "long_function": "Function '{function}' has {lines} lines (>{threshold} LOC). Consider refactoring.",
    "no_assertions": "Function '{function}' has {count} assertions (<{threshold}). Add validation.",
    "recursion": "Function '{function}' uses recursion. Use iterative alternative (NASA Rule 5).",
}

# Error response schema template
ERROR_RESPONSE_TEMPLATE = {
    "status": "error",
    "error_code": None,
    "message": None,
    "details": {},
    "timestamp": None,
}

# Success response schema
SUCCESS_RESPONSE_TEMPLATE = {
    "status": "success",
    "data": {},
    "timestamp": None,
}

# File pattern magic strings
# REMOVED: FILE_PATTERNS (duplicate of quality_standards.SUPPORTED_EXTENSIONS)
# Use: from analyzer.constants.quality_standards import SUPPORTED_EXTENSIONS

# Common exclusion patterns
EXCLUSION_MESSAGES = {
    "ignored_directory": "Directory '{path}' ignored (matches exclusion pattern '{pattern}')",
    "ignored_file": "File '{file}' ignored (matches exclusion pattern '{pattern}')",
    "binary_file": "File '{file}' skipped (binary file)",
}


def format_detection_message(message_type: str, **kwargs) -> str:
    """
    Format a detection message with variables.

    Args:
        message_type: Type of detection message
        **kwargs: Template variables

    Returns:
        Formatted message string
    """
    template = DETECTION_MESSAGES.get(message_type, "Unknown violation: {message_type}")
    return template.format(message_type=message_type, **kwargs)
