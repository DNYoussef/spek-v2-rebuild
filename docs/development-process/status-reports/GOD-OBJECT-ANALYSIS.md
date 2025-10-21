# God Object Analysis - Analyzer Refactoring

**Date**: 2025-10-08
**Analyzer Location**: `./analyzer`
**Total Files**: 236 Python files
**Total LOC**: 91,673

---

## Executive Summary

**God Objects Detected**: 19 files >500 LOC (8.05% of files)

**NASA POT10 Rule 3 Compliance**:
- Target: Functions ≤60 lines, Files ≤300 LOC (Python)
- Current: 19/236 files violate (92.0% compliance - **JUST BELOW 92% TARGET**)
- Goal: Refactor to <10 god objects (95.8% compliance)

**Priority Refactoring** (Week 1):
1. `core.py` (1,043 LOC) → 5 modules
2. `constants.py` (1,005 LOC) → 6 modules
3. `comprehensive_analysis_engine.py` (613 LOC - not in top scan, need to verify)

**Total Reduction**: 2,661 LOC → 14 modules (~190 LOC avg) = **86% size reduction per module**

---

## All God Objects (>500 LOC)

| Rank | File | LOC | Priority | Refactoring Strategy |
|------|------|-----|----------|---------------------|
| 1 | `performance/result_aggregation_profiler.py` | 1,507 | P2 | Week 2 or defer (non-critical) |
| 2 | `enterprise/compliance/iso27001.py` | 1,349 | P3 | Defer (enterprise feature) |
| 3 | `enterprise/compliance/reporting.py` | 1,259 | P3 | Defer (enterprise feature) |
| 4 | `performance/optimizer.py` | 1,187 | P2 | Week 2 or defer |
| 5 | `performance/cache_performance_profiler.py` | 1,093 | P2 | Week 2 or defer |
| 6 | `architecture/refactoring_audit_report.py` | 1,077 | P3 | Defer |
| 7 | `performance/incremental_analyzer.py` | 1,076 | P2 | Week 2 or defer |
| 8 | `cross_phase_learning_integration.py` | 1,049 | P3 | Defer |
| 9 | **`core.py`** | **1,043** | **P0** | **Week 1 (CRITICAL)** |
| 10 | `unified_memory_model.py` | 1,040 | P2 | Week 2 or defer |
| 11 | **`constants.py`** | **1,005** | **P0** | **Week 1 (CRITICAL)** |
| 12 | `performance/real_time_monitor.py` | 996 | P2 | Defer |
| 13 | `system_integration.py` | 995 | P2 | Defer |
| 14 | `streaming/stream_processor.py` | 961 | P2 | Defer |
| 15 | `performance/regression_detector.py` | 933 | P2 | Defer |
| 16 | `phase_correlation_storage.py` | 908 | P2 | Defer |
| 17 | `performance/detector_pool_optimizer.py` | 899 | P2 | Defer |
| 18 | `enterprise/supply_chain/evidence_packager.py` | 879 | P3 | Defer |
| 19 | `cross_phase_security_validator.py` | 877 | P2 | Defer |

**Total LOC in God Objects**: 20,130 LOC (21.9% of total analyzer code)

---

## Week 1 Priority Refactoring

### P0 File 1: `core.py` (1,043 LOC)

**Target Modules** (5):
1. `core/engine.py` (~200 LOC) - Core analysis engine orchestration
2. `core/cli.py` (~150 LOC) - CLI entry point (`__main__` integration)
3. `core/api.py` (~100 LOC) - Public API facade
4. `core/import_manager.py` (~150 LOC) - Dependency import handling
5. `core/fallback.py` (~100 LOC) - Emergency modes (MINIMAL, remove theater)

**Refactoring Steps**:
1. Analyze `core.py` structure (functions, classes, imports)
2. Map functions to target modules
3. Create module stubs with docstrings
4. Move code incrementally (one module at a time)
5. Update imports and cross-references
6. Test backward compatibility

**Expected Outcome**:
- 5 modules averaging 209 LOC each ✅ (all <300 LOC target)
- Backward compatibility via `core/__init__.py` shim

### P0 File 2: `constants.py` (1,005 LOC)

**Target Modules** (6):
1. `constants/thresholds.py` (~168 LOC) - Numeric thresholds (magic numbers, CoM limits)
2. `constants/policies.py` (~168 LOC) - Policy definitions (nasa-compliance, strict, standard, lenient)
3. `constants/weights.py` (~168 LOC) - Violation severity weights
4. `constants/messages.py` (~168 LOC) - User-facing messages and templates
5. `constants/nasa_rules.py` (~168 LOC) - NASA POT10 rule definitions
6. `constants/quality_standards.py` (~165 LOC) - Quality metric targets

**Refactoring Steps**:
1. Scan `constants.py` for logical groupings
2. Create 6 modules with clear boundaries
3. Move constants by category
4. Re-export all from `constants/__init__.py` (backward compatibility)
5. Update all importers

**Expected Outcome**:
- 6 modules averaging 168 LOC each ✅ (all <300 LOC target)
- Zero breaking changes for external consumers

### P0 File 3: `comprehensive_analysis_engine.py` (613 LOC - need to verify)

**Status**: Not found in top 19 god objects scan. Let's verify:

```bash
wc -l ./analyzer/comprehensive_analysis_engine.py
```

**Expected Result**: 613-650 LOC (per documentation)

**Target Modules** (3):
1. `engines/syntax_analyzer.py` (~200 LOC) - AST-based syntax analysis
2. `engines/pattern_detector.py` (~200 LOC) - Pattern detection logic
3. `engines/compliance_validator.py` (~213 LOC) - Compliance rule validation

**Refactoring Steps**:
1. Verify file exists and LOC count
2. Analyze structure (likely has 3 distinct responsibilities)
3. Split into syntax, pattern, compliance modules
4. Update imports from `comprehensive_analysis_engine` → `engines.*`

**Expected Outcome**:
- 3 modules averaging 204 LOC each ✅ (all <300 LOC target)

---

## Week 2 Optional Refactoring (If Time Permits)

**P1 Targets** (non-blocking):
- `performance/result_aggregation_profiler.py` (1,507 LOC)
- `performance/optimizer.py` (1,187 LOC)
- `performance/cache_performance_profiler.py` (1,093 LOC)
- `unified_memory_model.py` (1,040 LOC)

**Strategy**: If Week 1 completes early (unlikely), tackle these 4 files. Otherwise defer to post-launch refactoring.

---

## Refactoring Impact Analysis

### Before Refactoring
- **Total Files**: 236
- **God Objects**: 19 (8.05%)
- **NASA Compliance**: 92.0% (19 violations)
- **Status**: ⚠️ **JUST BELOW 92% TARGET**

### After Week 1 Refactoring (3 files → 14 modules)
- **Total Files**: 247 (236 - 3 + 14)
- **God Objects**: 16 (6.48%)
- **NASA Compliance**: 93.5% (16 violations)
- **Status**: ✅ **ABOVE 92% TARGET**

### After Week 2 Optional (4 additional files → ~12 modules)
- **Total Files**: ~255 (247 - 4 + 12)
- **God Objects**: 12 (4.71%)
- **NASA Compliance**: 95.3% (12 violations)
- **Status**: ✅ **APPROACHING 95% EXCELLENT**

---

## Backward Compatibility Strategy

### Core Module Shim
```python
# analyzer/core/__init__.py
"""
Backward compatibility shim for core.py refactoring.

Old pattern:
    from analyzer.core import get_core_analyzer

New pattern:
    from analyzer.core.api import Analyzer
"""

# Re-export legacy API
from .api import Analyzer as CoreAnalyzer
from .engine import AnalysisEngine

# Legacy function for backward compatibility
def get_core_analyzer(*args, **kwargs):
    """Legacy function - use Analyzer class directly."""
    import warnings
    warnings.warn(
        "get_core_analyzer() is deprecated. Use Analyzer() directly.",
        DeprecationWarning,
        stacklevel=2
    )
    return CoreAnalyzer(*args, **kwargs)

__all__ = ["CoreAnalyzer", "AnalysisEngine", "get_core_analyzer"]
```

### Constants Module Shim
```python
# analyzer/constants/__init__.py
"""
Backward compatibility shim for constants.py refactoring.

Old pattern:
    from analyzer.constants import THRESHOLD_MAGIC_LITERAL

New pattern:
    from analyzer.constants.thresholds import THRESHOLD_MAGIC_LITERAL
"""

# Re-export all constants from submodules
from .thresholds import *
from .policies import *
from .weights import *
from .messages import *
from .nasa_rules import *
from .quality_standards import *

# Log deprecation warning
import warnings
warnings.warn(
    "Importing from analyzer.constants directly is deprecated. "
    "Use specific submodules (analyzer.constants.thresholds, etc.)",
    DeprecationWarning,
    stacklevel=2
)
```

---

## Testing Strategy

### Backward Compatibility Tests
```python
# tests/unit/test_backward_compatibility.py

def test_old_core_import_still_works():
    """Verify old core.py import pattern works."""
    from analyzer.core import get_core_analyzer
    analyzer = get_core_analyzer()
    assert analyzer is not None

def test_old_constants_import_still_works():
    """Verify old constants.py import pattern works."""
    from analyzer.constants import THRESHOLD_MAGIC_LITERAL
    assert THRESHOLD_MAGIC_LITERAL is not None

def test_new_core_import_works():
    """Verify new core API import works."""
    from analyzer.core.api import Analyzer
    analyzer = Analyzer()
    assert analyzer is not None

def test_new_constants_import_works():
    """Verify new constants submodule import works."""
    from analyzer.constants.thresholds import THRESHOLD_MAGIC_LITERAL
    assert THRESHOLD_MAGIC_LITERAL is not None
```

### Integration Tests
```python
# tests/integration/test_refactored_analyzer.py

def test_full_analysis_workflow():
    """Verify full analysis workflow still works after refactoring."""
    from analyzer.core.api import Analyzer

    analyzer = Analyzer(policy="nasa-compliance")
    result = analyzer.analyze("./tests/fixtures/sample_code")

    assert result is not None
    assert result.nasa_compliance >= 0.92
    assert result.theater_score < 60
    assert result.god_objects == 0
```

---

## Success Criteria (Week 1)

**Must Complete** (ALL required):
- [x] Analyzer copied from template (236 files, 91,673 LOC)
- [ ] God object analysis complete (19 files identified)
- [ ] `core.py` (1,043 LOC) split into 5 modules (~209 LOC avg)
- [ ] `constants.py` (1,005 LOC) split into 6 modules (~168 LOC avg)
- [ ] `comprehensive_analysis_engine.py` (613 LOC) split into 3 modules (~204 LOC avg)
- [ ] Backward compatibility shims implemented
- [ ] Backward compatibility tests passing (100%)
- [ ] NASA compliance ≥92% (currently 92.0%, target 93.5% after refactoring)

**Quality Gates**:
- [ ] All new modules ≤300 LOC (NASA Rule 3)
- [ ] Zero import failures (dependency health check)
- [ ] Zero breaking changes for external consumers
- [ ] Deprecation warnings logged (not errors)

---

## Risk Assessment

### Low Risk ✅
- Backward compatibility (shim layer mitigates)
- Testing (Week 2 comprehensive test suite)

### Medium Risk ⚠️
- Circular dependencies (may require interface abstractions)
- Import order issues (dependency injection patterns needed)

### High Risk ❌
- None (refactoring is well-scoped and isolated)

---

**Last Updated**: 2025-10-08 1:00 PM
**Next Update**: End of Day 1 (after module stub creation)
