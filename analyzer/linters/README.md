# Linter Bridge System

**Status**: Infrastructure complete (Sprint 2.1 ✅), bridges pending (Sprints 2.2-2.4)
**Created**: 2025-10-19 (Phase 2, Sprint 2.1)

## Overview

The linter bridge system provides a pluggable architecture for integrating external Python linters (pylint, flake8, mypy) and code metrics tools (radon) into the SPEK analyzer workflow.

## Design Pattern: Bridge + Registry

### Bridge Pattern
Decouples linter-specific logic from analyzer core:
- Each linter implements `LinterBridge` abstract interface
- Analyzer core depends only on the interface, not specific linters
- Linters can be added/removed without changing analyzer code

### Registry Pattern
Central management of all linter instances:
- `LinterRegistry` discovers and initializes linters
- Lazy registration avoids import errors when linters missing
- Provides unified API for running linters

## Architecture

```
analyzer/
  linters/
    __init__.py             # LinterRegistry + public API
    base_linter.py          # LinterBridge abstract base class
    pylint_bridge.py        # Pylint integration (Sprint 2.2)
    flake8_bridge.py        # Flake8 integration (Sprint 2.3)
    mypy_bridge.py          # Mypy integration (Sprint 2.4)
    radon_bridge.py         # Radon metrics (Sprint 3.1)
```

## Base Infrastructure (✅ Sprint 2.1 Complete)

### `LinterBridge` (base_linter.py)

Abstract base class all linters inherit from:

```python
from abc import ABC, abstractmethod
from analyzer.linters import LinterBridge

class PylintBridge(LinterBridge):
    def is_available(self) -> bool:
        """Check if pylint is installed."""
        pass

    def run(self, file_path: Path) -> Dict[str, Any]:
        """Run pylint and return results."""
        pass

    def convert_to_violations(self, raw_output: Any) -> List[ConnascenceViolation]:
        """Convert pylint messages to violations."""
        pass
```

**Key methods**:
- `is_available()` - Check if linter installed
- `run(file_path)` - Execute linter, return structured results
- `convert_to_violations()` - Map linter output to `ConnascenceViolation`
- `safe_run()` - Run with error handling (implemented in base class)

### `LinterRegistry` (__init__.py)

Central registry managing all linters:

```python
from analyzer.linters import linter_registry

# Get available linters
available = linter_registry.get_available_linters()
# Returns: ['pylint', 'flake8', 'mypy'] (if installed)

# Run all linters on a file
results = linter_registry.run_all_linters(Path("myfile.py"))
# Returns: {'pylint': {...}, 'flake8': {...}, 'mypy': {...}}

# Run specific linter
result = linter_registry.run_linter('pylint', Path("myfile.py"))
# Returns: {'success': True, 'violations': [...], 'execution_time': 1.2}

# Aggregate violations from all linters
all_violations = linter_registry.aggregate_violations(results)
# Returns: List[ConnascenceViolation]
```

**Key methods**:
- `get_available_linters()` - List installed linters
- `run_all_linters(file_path)` - Run all available linters
- `run_linter(name, file_path)` - Run specific linter
- `aggregate_violations(results)` - Combine violations from all linters

## Result Format

All linters return standardized results:

```python
{
    'success': bool,              # True if linter ran successfully
    'violations': List[ConnascenceViolation],  # Violations found
    'raw_output': Any,            # Linter-specific raw output
    'execution_time': float,      # Execution time in seconds
    'linter': str,                # Name of linter ('pylint', etc.)
    'error': str                  # Error message (if success=False)
}
```

## ConnascenceViolation Integration

All linter results are converted to the canonical `ConnascenceViolation` type from `analyzer/utils/types.py`:

```python
@dataclass
class ConnascenceViolation:
    type: str                     # Violation type
    severity: str                 # 'critical', 'high', 'medium', 'low'
    description: str              # Human-readable description
    file_path: str                # File containing violation
    line_number: int              # Line number
    column: int                   # Column number
    recommendation: Optional[str] # How to fix
    # ... additional fields
```

This ensures consistency across all linters and analyzers in the SPEK system.

## Usage Examples

### Example 1: Run Pylint on a File

```python
from pathlib import Path
from analyzer.linters import linter_registry

# Run pylint
result = linter_registry.run_linter('pylint', Path("myfile.py"))

if result['success']:
    print(f"Found {len(result['violations'])} violations")
    for violation in result['violations']:
        print(f"  {violation.severity}: {violation.description} ({violation.file_path}:{violation.line_number})")
else:
    print(f"Pylint failed: {result['error']}")
```

### Example 2: Run All Linters and Aggregate Results

```python
from pathlib import Path
from analyzer.linters import linter_registry

# Run all available linters
results = linter_registry.run_all_linters(Path("myfile.py"))

# Aggregate violations
all_violations = linter_registry.aggregate_violations(results)

# Group by severity
critical = [v for v in all_violations if v.severity == 'critical']
high = [v for v in all_violations if v.severity == 'high']

print(f"Total violations: {len(all_violations)}")
print(f"Critical: {len(critical)}, High: {len(high)}")
```

### Example 3: Check Linter Availability

```python
from analyzer.linters import linter_registry

# Check which linters are available
available = linter_registry.get_available_linters()
print(f"Available linters: {available}")

# Get detailed info
info = linter_registry.get_linter_info()
for name, details in info.items():
    print(f"{name}: available={details['available']}, timeout={details['timeout']}s")
```

## Integration with Analyzer Core

The linter system integrates with the analyzer core engine:

```python
# analyzer/core/engine.py (enhancement)
from analyzer.linters import linter_registry

class AnalysisEngine:
    def __init__(self, policy: str = "standard", use_external_linters: bool = False):
        self.use_external_linters = use_external_linters

    def run_analysis(self, target_path: str) -> Dict[str, Any]:
        results = {...}  # Internal AST analysis

        # Optionally run external linters
        if self.use_external_linters:
            linter_results = linter_registry.run_all_linters(Path(target_path))
            linter_violations = linter_registry.aggregate_violations(linter_results)
            results["violations"].extend(linter_violations)
            results["linter_results"] = linter_results

        return results
```

## NASA POT10 Compliance

All linter bridge code follows NASA POT10 rules:
- ✅ **Rule 3**: ≤60 LOC per function
- ✅ **Rule 4**: ≥2 assertions for input validation
- ✅ **Rule 5**: No recursion (iterative only)
- ✅ **Rule 6**: Fixed loop bounds

## Error Handling

All linters implement fail-safe error handling:

1. **Availability checks**: `is_available()` returns False if linter not installed
2. **Graceful fallbacks**: `safe_run()` catches all exceptions
3. **Empty results**: Failed linters return empty violation lists
4. **No crashes**: Analyzer never crashes due to missing/failing linters

## Implementation Status

| Sprint | Linter | Status | LOC | Tests |
|--------|--------|--------|-----|-------|
| 2.1 | **Infrastructure** | ✅ **COMPLETE** | 350 | Pending |
| 2.2 | Pylint | 📅 Pending | ~150 | ~100 |
| 2.3 | Flake8 | 📅 Pending | ~140 | ~80 |
| 2.4 | Mypy | 📅 Pending | ~130 | ~80 |
| 3.1 | Radon | 📅 Pending | ~120 | ~80 |

**Total (when complete)**: ~890 LOC, ~340 tests

## Next Steps

### Sprint 2.2: Pylint Bridge (8 hours)
- Implement `pylint_bridge.py`
- Map pylint message types to severity levels
- Handle JSON output parsing
- Create 100 test cases

### Sprint 2.3: Flake8 Bridge (8 hours)
- Implement `flake8_bridge.py`
- Parse text-based output format
- Map error codes to severity
- Create 80 test cases

### Sprint 2.4: Mypy Bridge (8 hours)
- Implement `mypy_bridge.py`
- Handle type checking errors
- Map mypy error codes
- Create 80 test cases

## Testing Strategy

Each linter bridge will have:
1. **Availability tests**: Verify `is_available()` works
2. **Execution tests**: Run linter on sample files
3. **Conversion tests**: Validate output → ConnascenceViolation mapping
4. **Error handling tests**: Test failure modes
5. **Integration tests**: Test with analyzer core engine

## Dependencies

**Required packages** (in setup.py):
```python
install_requires=[
    'pylint>=2.0.0',   # For Pylint bridge
    'flake8>=4.0.0',   # For Flake8 bridge
    'mypy>=1.0.0',     # For Mypy bridge
    'radon>=5.0.0'     # For Radon metrics
]
```

**Note**: Linters are optional - analyzer works without them (internal AST analysis only).

## Design Decisions

### Why Bridge Pattern?
- **Decoupling**: Analyzer core doesn't depend on specific linters
- **Extensibility**: Easy to add new linters (just implement interface)
- **Testing**: Each linter can be tested independently
- **Optional**: Linters work even if some are missing

### Why Lazy Registration?
- **No import errors**: Registry initializes even if linter packages missing
- **Performance**: Don't load unused linters
- **CI/CD friendly**: Tests pass even without all linters installed

### Why ConnascenceViolation?
- **Consistency**: Same format as internal detectors
- **Aggregation**: Can combine internal + external violations
- **Reporting**: Unified reporting format for all violations

---

**Created**: 2025-10-19 (Phase 2, Sprint 2.1)
**Status**: Infrastructure complete, ready for bridge implementations
**Next**: Sprint 2.2 - Pylint Bridge
