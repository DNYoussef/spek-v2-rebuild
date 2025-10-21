"""
Numeric Thresholds - Core analysis limits

All magic numbers centralized here for consistency.

NASA Rule 3 Compliance: ≤170 LOC target
Version: 6.0.0 (Week 1 Day 3 Refactoring)
"""

# Core File and Function Thresholds
MAXIMUM_FILE_LENGTH_LINES = 500
MAXIMUM_FUNCTION_LENGTH_LINES = 60
MAXIMUM_FUNCTION_PARAMETERS = 10
MAXIMUM_NESTED_DEPTH = 5

# NASA Power of Ten Rules Thresholds
# REMOVED: NASA_PARAMETER_THRESHOLD, NASA_GLOBAL_THRESHOLD (duplicates nasa_rules.py)
# Use: from analyzer.constants.nasa_rules import NASA_RULES
NASA_POT10_TARGET_COMPLIANCE_THRESHOLD = 0.92  # Minimum NASA compliance score

# God Object Detection Thresholds
GOD_OBJECT_METHOD_THRESHOLD = 20  # Classes with >20 methods are god objects
GOD_OBJECT_LOC_THRESHOLD = 500  # Classes with >500 LOC are god objects
GOD_OBJECT_PARAMETER_THRESHOLD = MAXIMUM_FUNCTION_PARAMETERS  # Methods with >10 params

# MECE Analysis Thresholds
MECE_SIMILARITY_THRESHOLD = 0.8  # Minimum similarity for duplication detection
MECE_QUALITY_THRESHOLD = 0.80  # Production threshold (see thresholds_ci.py for CI/CD override)
MECE_CLUSTER_MIN_SIZE = 3  # Minimum functions in duplication cluster

# NOTE: CI/CD temporary thresholds moved to thresholds_ci.py (Sprint 1.4)
# Import from: analyzer.constants.thresholds_ci

# Connascence Severity Thresholds
MAGIC_LITERAL_THRESHOLD = 3  # Number of magic literals before warning
POSITION_COUPLING_THRESHOLD = 4  # Parameter count before position coupling
ALGORITHM_COMPLEXITY_THRESHOLD = 10  # Cyclomatic complexity threshold

# Quality Gate Thresholds
OVERALL_QUALITY_THRESHOLD = 0.75  # Minimum overall quality score
REGULATORY_FACTUALITY_REQUIREMENT = 0.90  # Factual accuracy requirement
THEATER_DETECTION_FAILURE_THRESHOLD = 0.60  # Theater score limit (fail below this)
THEATER_DETECTION_WARNING_THRESHOLD = 0.30  # Theater score warning (warn below this)
MINIMUM_TEST_COVERAGE_PERCENTAGE = 80.0  # Test coverage requirement

# NOTE: OVERALL_QUALITY_THRESHOLD_CI moved to thresholds_ci.py (Sprint 1.4)

# Quality Violation Limits
CRITICAL_VIOLATION_LIMIT = 0  # Maximum allowed critical violations
HIGH_VIOLATION_LIMIT = 5  # Maximum allowed high-severity violations

# Performance Thresholds
MAX_ANALYSIS_TIME_SECONDS = 300  # Maximum time allowed for analysis
MAX_FILE_SIZE_KB = 1000  # Maximum file size for analysis
MAX_FILES_PER_BATCH = 100  # Maximum files per analysis batch
API_TIMEOUT_SECONDS = 30  # API request timeout
MAXIMUM_RETRY_ATTEMPTS = 5  # Maximum retry attempts

# Storage and Retention
DAYS_RETENTION_PERIOD = 90  # Data retention period in days
MINIMUM_TRADE_THRESHOLD = 100  # Minimum trade threshold (legacy)

# Backward Compatibility Aliases (Sprint 1.4)
# NOTE: Import from thresholds_ci.py for CI/CD-specific constants
MAXIMUM_GOD_OBJECTS_ALLOWED = 5  # Alias → thresholds_ci.MAXIMUM_GOD_OBJECTS_ALLOWED
QUALITY_GATE_MINIMUM_PASS_RATE = OVERALL_QUALITY_THRESHOLD  # Alias (legacy)
TAKE_PROFIT_PERCENTAGE = 0.02  # Legacy ML module (deprecated, unused)

# NASA Compliance Aliases (for backward compatibility)
NASA_COMPLIANCE_THRESHOLD = NASA_POT10_TARGET_COMPLIANCE_THRESHOLD
