# Legacy Constants God Object

**Archived**: 2025-10-19 (Sprint 1.4 - Constants Consolidation)
**Original Location**: `analyzer/constants.py`
**Original Size**: 1,005 LOC
**Status**: DEPRECATED - Use modular structure in `analyzer/constants/`

## History

This file was the original monolithic constants module that contained ALL constants for the entire analyzer. It was refactored in **Week 1 Day 3** into a modular structure:

```
analyzer/constants.py (1,005 LOC - GOD OBJECT)
    ↓
    Refactored into:
    ↓
analyzer/constants/
    ├── __init__.py (43 LOC) - Backward compatibility
    ├── thresholds.py (85 LOC) - Numeric thresholds
    ├── weights.py (79 LOC) - Severity weights
    ├── messages.py (72 LOC) - User messages
    ├── nasa_rules.py (86 LOC) - NASA Rule definitions
    ├── policies.py (118 LOC) - Policy configurations
    └── quality_standards.py (51 LOC) - File types, exclusions
```

**Total Modular**: 534 LOC (53% reduction from 1,005 LOC)

## Why It Was Archived (Not Deleted)

The file was archived in Sprint 1.4 (2025-10-19) because:

1. **100% Duplication**: All constants were already migrated to modular structure in Week 1 Day 3
2. **Zero Imports**: No code was importing from this file (all migrated to new structure)
3. **Forgotten Deletion**: The file should have been deleted in Week 1 Day 3 but was overlooked

**Audit Results** (Sprint 1.4):
- Imports of old god object: **0**
- Imports of new modular structure: **105**
- Migration completeness: **100%**

## Migration Guide

### Old Imports (God Object) ❌
```python
from analyzer.constants import MAXIMUM_FUNCTION_LENGTH_LINES
from analyzer.constants import NASA_PARAMETER_THRESHOLD
from analyzer.constants import FILE_PATTERNS
```

### New Imports (Modular) ✅
```python
from analyzer.constants.thresholds import MAXIMUM_FUNCTION_LENGTH_LINES
from analyzer.constants.nasa_rules import NASA_RULES
from analyzer.constants.quality_standards import SUPPORTED_EXTENSIONS
```

### Backward Compatibility (Still Works)
```python
# This still works via analyzer/constants/__init__.py
from analyzer.constants import MAXIMUM_FUNCTION_LENGTH_LINES
# But shows deprecation warning
```

## File Structure Comparison

| Aspect | God Object (Old) | Modular (New) |
|--------|------------------|---------------|
| **LOC** | 1,005 | 534 (53% reduction) |
| **Files** | 1 | 7 |
| **Maintainability** | Poor (god object) | Good (separation of concerns) |
| **Imports** | Simple | Explicit |
| **Duplication** | None | None (after Sprint 1.4) |

## Constants Categories

The god object contained these categories (now modularized):

1. **Thresholds** (now `thresholds.py`):
   - File/function limits
   - NASA compliance thresholds
   - God object detection thresholds
   - Quality gate thresholds
   - Performance thresholds

2. **Weights** (now `weights.py`):
   - Violation severity weights
   - 10-level severity system
   - Severity-to-weight mapping

3. **Messages** (now `messages.py`):
   - Exit codes
   - Detection message templates
   - Error/success response schemas
   - File patterns (removed in Sprint 1.4)

4. **NASA Rules** (now `nasa_rules.py`):
   - NASA Power of Ten rule definitions
   - Compliance thresholds
   - Violation messages

5. **Policies** (now `policies.py`):
   - Policy name mappings
   - Policy configurations (nasa-compliance, strict, standard, lenient)

6. **Quality Standards** (now `quality_standards.py`):
   - Supported file extensions
   - Exclusion patterns
   - Connascence types

## Impact of Removal

**Sprint 1.4 Results**:
- **LOC Removed**: 1,005
- **Duplication Eliminated**: 100%
- **God Objects Remaining**: 0 (last one eliminated)
- **Test Impact**: 0 tests broken (all imports already migrated)

## Recovery Instructions

If you need to recover any constants from this file:

1. **Check modular structure first**: `analyzer/constants/`
2. **Use backward compatibility**: Import from `analyzer.constants` (with deprecation warning)
3. **Read this archived file**: All original constants preserved here

## Timeline

- **Week 1 Day 3** (2025-10-07): Refactored into modular structure
- **Week 1 Day 3** (2025-10-07): ❌ FORGOT to delete old file
- **Sprint 1.4** (2025-10-19): ✅ Archived to legacy folder

## Why Archival Instead of Deletion?

This file was moved to `legacy/` instead of deleted because:
1. **Documentation**: Preserves history of refactoring
2. **Recovery**: Easy to reference if needed
3. **Audit Trail**: Shows what was removed and when
4. **Learning**: Future reference for god object elimination patterns

---

**Version**: 1.0
**Archived**: 2025-10-19
**Sprint**: Phase 1, Sprint 1.4 (Constants Consolidation)
**Status**: DEPRECATED - Use `analyzer/constants/` modular structure
