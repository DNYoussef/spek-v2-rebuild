"""
Quality Standards - Quality metrics and file patterns

Defines quality metric standards, file types, exclusions.

NASA Rule 3 Compliance: ≤100 LOC target
Version: 6.0.0 (Week 2 Day 1)
"""

# File type extensions
SUPPORTED_EXTENSIONS = {
    "python": [".py", ".pyx", ".pyi"],
    "javascript": [".js", ".mjs", ".jsx", ".ts", ".tsx"],
    "c_cpp": [".c", ".cpp", ".cxx", ".cc", ".h", ".hpp", ".hxx"],
}

# Analysis exclusion patterns
DEFAULT_EXCLUSIONS = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    ".env",
    "build",
    "dist",
    ".tox",
    "coverage",
]

# Legacy compatibility aliases
EXCLUDED_PATTERNS = DEFAULT_EXCLUSIONS  # v5 compatibility
PYTHON_EXTENSIONS = SUPPORTED_EXTENSIONS["python"]  # v5 compatibility

# Connascence types (analyzed by detectors)
CONNASCENCE_TYPES = [
    "CoN",  # Connascence of Name
    "CoT",  # Connascence of Type
    "CoM",  # Connascence of Meaning (magic literals)
    "CoP",  # Connascence of Position (parameter order)
    "CoA",  # Connascence of Algorithm (duplicated logic)
    "CoE",  # Connascence of Execution (order dependencies)
    "CoTm",  # Connascence of Timing (race conditions)
    "CoV",  # Connascence of Value (synchronized state)
    "CoI",  # Connascence of Identity (object references)
]

# Version information
__version__ = "6.0.0"
__version_info__ = (6, 0, 0)
