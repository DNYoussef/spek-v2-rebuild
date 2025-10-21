"""
Constants Module - Backward compatibility shim

Refactored from monolithic constants.py (1,005 LOC) into 6 specialized modules.

New structure:
- thresholds.py: Numeric thresholds and limits
- policies.py: Analysis policy definitions
- weights.py: Violation severity weights
- messages.py: User-facing messages
- nasa_rules.py: NASA POT10 rule constants
- quality_standards.py: Quality metric standards

Version: 6.0.0 (Week 1 Day 3 Refactoring)
"""

import warnings

# Re-export all constants from submodules for backward compatibility
from .thresholds import *
from .policies import *
from .weights import *
from .messages import *
from .nasa_rules import *
from .quality_standards import *

# Log deprecation warning
warnings.warn(
    "Importing from analyzer.constants directly is deprecated. "
    "Use specific submodules: analyzer.constants.thresholds, etc.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    # Thresholds
    "MAXIMUM_FILE_LENGTH_LINES",
    "MAXIMUM_FUNCTION_LENGTH_LINES",
    "NASA_POT10_TARGET_COMPLIANCE_THRESHOLD",
    # ... (all constants re-exported)
]

__version__ = "6.0.0"
