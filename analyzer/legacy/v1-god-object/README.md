# Legacy Analyzer Implementations & Orchestrators (v1 God Object Era)

**Deprecated**: 2025-10-19 (analyzers), 2025-10-19 (orchestrators)
**Reason**: Architectural consolidation to eliminate duplication and dead code
**Migration Path**: Use `analyzer/unified_analyzer.py` or `analyzer/core/` modules; Use `analyzer/analysis_orchestrator.py` for orchestration

## What Happened

During Weeks 1-2 of the SPEK v2 rebuild, the analyzer underwent multiple refactoring attempts. Each attempt created a new implementation without fully removing the old one, leading to **5 competing analyzer implementations** coexisting in the same codebase.

This directory archives those deprecated implementations for historical reference.

## Archived Files

### 1. `core.py` (1,043 LOC) - Original God Object
**Created**: Pre-Week 1 (original prototype)
**Status**: ❌ DEPRECATED

**What it was:**
- Monolithic analyzer with 83+ methods in single file
- Created mock import managers for CI compatibility
- Violated NASA POT10 Rule 3 (≤60 LOC per function)
- Contains `main()` function for CLI entry point
- Uses `IMPORT_MANAGER` from `core/unified_imports.py`

**Why deprecated:**
- God object anti-pattern (1,043 LOC in single file)
- High complexity, low maintainability
- Mock/theater code for testing instead of real implementations
- Refactored into modular `analyzer/core/` directory (Week 1-2)

**Replacement:**
- `analyzer/core/cli.py` - CLI entry point (`main()` function)
- `analyzer/core/api.py` - Public API (100 LOC, clean)
- `analyzer/core/engine.py` - Analysis engine
- `analyzer/core/unified_imports.py` - Import manager

**Migration:**
```python
# OLD (deprecated):
from analyzer.core import main
from analyzer.core import IMPORT_MANAGER

# NEW (use refactored architecture):
from analyzer.core.cli import main
from analyzer.core.unified_imports import IMPORT_MANAGER
```

---

### 2. `real_unified_analyzer.py` (536 LOC) - "NO THEATER" Attempt
**Created**: Mid-Week 1
**Status**: ❌ DEPRECATED

**What it was:**
- Reaction to discovery of mocks/theater in `unified_analyzer.py`
- Introduced `RealViolation` and `RealAnalysisResult` dataclasses
- Header claimed "NO THEATER, NO MOCKS - Every component does REAL work"
- Created parallel implementation instead of fixing original

**Why deprecated:**
- Duplication - solved same problem as `unified_analyzer.py`
- Created competing implementation instead of consolidating
- Never became canonical replacement
- Good ideas (dataclasses, no-mock guarantee) merged into `unified_analyzer.py`

**Replacement:**
- `analyzer/unified_analyzer.py` (enhanced with features from this file)

**Key Features Preserved:**
- `RealViolation` dataclass concept (for type safety)
- No-mock guarantee flag
- Dict-like compatibility methods

---

### 3. `consolidated_analyzer.py` (328 LOC) - Failed Consolidation
**Created**: Late Week 1
**Status**: ❌ DEPRECATED

**What it was:**
- Attempted to be "MECE compliant single source of truth"
- Header claimed to replace 7 duplicate implementations
- Created `ConsolidatedConnascenceAnalyzer` class
- Defined `ConnascenceViolation` dataclass

**Why deprecated:**
- Never achieved its consolidation goal
- The 7 files it claimed to replace continued to exist
- Added yet another layer instead of removing old ones
- No authority to delete "working" code, so became 6th implementation

**Replacement:**
- `analyzer/unified_analyzer.py` (actual consolidation achieved in Phase 1, Sprint 1.2)

---

### 4. `connascence_analyzer.py` (210 LOC) - Facade Layer
**Created**: Week 1-2
**Status**: ❌ DEPRECATED

**What it was:**
- Facade over `unified_analyzer.py`
- Provided `ConnascenceAnalyzer` class for workflow compatibility
- Tried `UnifiedConnascenceAnalyzer`, fell back to basic analysis if unavailable
- Redundant abstraction layer

**Why deprecated:**
- Unnecessary indirection (facade over facade)
- Added complexity without value
- Workflows can use `unified_analyzer.py` directly

**Replacement:**
- `analyzer/unified_analyzer.py` (use directly, no facade needed)

**Migration:**
```python
# OLD (deprecated facade):
from analyzer.connascence_analyzer import ConnascenceAnalyzer
analyzer = ConnascenceAnalyzer(config_manager)
result = analyzer.analyze_directory("./src")

# NEW (use unified analyzer directly):
from analyzer.unified_analyzer import UnifiedConnascenceAnalyzer
analyzer = UnifiedConnascenceAnalyzer(config_path="config.json")
result = analyzer.analyze_codebase("./src")
```

---

## Architecture Evolution Timeline

### Phase 1: Monolithic Era (Pre-Week 1)
- Single `core.py` with 2,650 LOC god object
- 83+ methods, unmaintainable
- All functionality in one file

### Phase 2: First Refactoring Attempt (Early Week 1)
- Created `unified_analyzer.py` (267 LOC delegation layer)
- Claimed to eliminate 2,350 LOC through delegation
- **Problem**: Never removed original `core.py`
- **Root Cause**: Fear of breaking changes

### Phase 3: "NO THEATER" Rebellion (Mid Week 1)
- Discovered mocks/theater in implementations
- Created `real_unified_analyzer.py` (536 LOC)
- **Problem**: Created parallel implementation instead of fixing
- **Root Cause**: Faster to duplicate than refactor under pressure

### Phase 4: Consolidation Attempt (Late Week 1)
- Created `consolidated_analyzer.py` (328 LOC)
- Listed 7 files to replace, but never deleted them
- **Problem**: New layer added to existing chaos
- **Root Cause**: No authority to delete "working" code

### Phase 5: Facade Addition (Week 1-2)
- Created `connascence_analyzer.py` (210 LOC)
- Facade over `unified_analyzer.py`
- **Problem**: Unnecessary indirection
- **Root Cause**: Workflow compatibility concerns

### Phase 6: Week 1-2 Refactoring SUCCESS ✅
- Refactored `core.py` god object into modular `analyzer/core/` directory
- 7 focused modules: `api.py`, `cli.py`, `engine.py`, `unified_imports.py`, etc.
- 100 LOC per module (NASA compliant)
- **Result**: Clean architecture achieved, but old files lingered

### Phase 7: Production Hardening (Week 21)
- DSPy training failed, focus shifted to production readiness
- Architectural cleanup postponed

### Phase 8: Phase 1 Sprint 1.2 (2025-10-19) ✅ THIS CONSOLIDATION
- Moved 4 competing analyzers to `analyzer/legacy/v1-god-object/`
- Updated imports to use refactored `core/` modules
- **LOC Reduction**: 2,117 LOC eliminated from active codebase

---

## Total LOC by Implementation

| File | LOC | Status |
|------|-----|--------|
| `core.py` | 1,043 | ❌ Archived |
| `real_unified_analyzer.py` | 536 | ❌ Archived |
| `consolidated_analyzer.py` | 328 | ❌ Archived |
| `connascence_analyzer.py` | 210 | ❌ Archived |
| **Total Archived** | **2,117** | **Eliminated** |
| | | |
| `unified_analyzer.py` | 267 | ✅ Active |
| `core/` modules (7 files) | ~700 | ✅ Active |
| **Total Active** | **~967** | **Clean** |

**Reduction**: 78% LOC reduction (2,117 → 967 active code)

---

## Why This Happened: Engineering Psychology

### 1. Fear of Breaking Production
- Each implementation had different callers
- No one knew which was "canonical"
- Safer to add new layer than remove old one

### 2. Incomplete Ownership
- Multiple developers worked on refactoring
- No single person owned consolidation
- Each iteration left previous work intact

### 3. Time Pressure
- Week-by-week delivery targets (26-week plan)
- No slack time for cleanup
- "If it works, don't touch it" mentality

### 4. Missing Architectural Authority
- No tech lead to say "delete this, keep that"
- Democratic decision-making led to "keep both" compromises
- Backward compatibility prioritized over cleanliness

### 5. Week 21 Pivot
- DSPy failure created urgency
- Cleanup deprioritized for production readiness
- Architectural debt postponed

---

## Current Architecture (Post-Consolidation)

### Primary Entry Point
```python
from analyzer.unified_analyzer import UnifiedConnascenceAnalyzer

analyzer = UnifiedConnascenceAnalyzer(
    config_path="config.json",
    analysis_mode="batch"
)

result = analyzer.analyze_codebase("./src")
```

### CLI Usage
```bash
python -m analyzer ./src --policy nasa-compliance --format json
```

### Refactored Core Modules
```
analyzer/
  core/                      # Week 1-2 refactored architecture ✅
    api.py                   # Public API (100 LOC)
    cli.py                   # CLI entry point (146 LOC)
    engine.py                # Analysis engine
    unified_imports.py       # Import manager (IMPORT_MANAGER)
    import_manager.py        # Import utilities
    fallback.py              # Fallback handlers
  unified_analyzer.py        # Delegation layer (267 LOC) ✅
  legacy/
    v1-god-object/          # Deprecated implementations ❌
      core.py               # (1,043 LOC)
      real_unified_analyzer.py   # (536 LOC)
      consolidated_analyzer.py   # (328 LOC)
      connascence_analyzer.py    # (210 LOC)
```

---

## Lessons Learned

1. **Delete early, delete often**: Don't let old implementations linger
2. **Single source of truth**: Enforce one canonical implementation
3. **Ruthless deprecation**: Mark old code as deprecated immediately
4. **Authority matters**: Assign ownership for architectural decisions
5. **Cleanup is work**: Schedule time for architectural cleanup in sprint planning

---

## Migration Checklist

If you're updating code that references these deprecated files:

- [ ] Replace `from analyzer.core import main` with `from analyzer.core.cli import main`
- [ ] Replace `from analyzer.core import IMPORT_MANAGER` with `from analyzer.core.unified_imports import IMPORT_MANAGER`
- [ ] Replace `from analyzer.connascence_analyzer import ConnascenceAnalyzer` with `from analyzer.unified_analyzer import UnifiedConnascenceAnalyzer`
- [ ] Replace `from analyzer.consolidated_analyzer import ConsolidatedConnascenceAnalyzer` with `from analyzer.unified_analyzer import UnifiedConnascenceAnalyzer`
- [ ] Replace `from analyzer.real_unified_analyzer import RealUnifiedAnalyzer` with `from analyzer.unified_analyzer import UnifiedConnascenceAnalyzer`
- [ ] Update config paths if needed
- [ ] Run tests to verify no breaking changes

---

---

## 5. `unified_orchestrator.py` (466 LOC) - Dead Code Orchestrator
**Created**: Week 1-2 (exact date unknown)
**Status**: ❌ DEPRECATED (Dead Code - Never Used)

**What it was:**
- Production-ready orchestrator integrating all analyzer components
- Supported streaming, parallel processing, comprehensive analysis
- Had its own CLI `main()` function
- Initialized enterprise analyzers (NASA, Six Sigma, DFARS)
- Used ThreadPoolExecutor for parallel detection

**Why deprecated:**
- **ZERO external usages** - completely dead code
- Never imported by any file in the codebase
- Created but never integrated into workflows
- Duplicate of `analysis_orchestrator.py` which IS actively used

**Replacement:**
- `analyzer/analysis_orchestrator.py` (633 LOC) - ACTIVE orchestrator used by bridge.py, components/, etc.

**Migration:**
N/A - No migration needed since nothing used it

---

## Total LOC Summary (Updated with Orchestrator)

| File | LOC | Sprint Archived | Status |
|------|-----|-----------------|--------|
| `core.py` | 1,043 | Sprint 1.2 | ❌ Archived |
| `real_unified_analyzer.py` | 536 | Sprint 1.2 | ❌ Archived |
| `consolidated_analyzer.py` | 328 | Sprint 1.2 | ❌ Archived |
| `connascence_analyzer.py` | 210 | Sprint 1.2 | ❌ Archived |
| `unified_orchestrator.py` | 466 | Sprint 1.3 | ❌ Archived |
| **Total Archived** | **2,583** | **Phase 1** | **Eliminated** |
| | | | |
| `unified_analyzer.py` | 267 | Active | ✅ Canonical |
| `analysis_orchestrator.py` | 633 | Active | ✅ Used |
| `core/` modules (7 files) | ~700 | Active | ✅ Refactored |
| **Total Active** | **~1,600** | | **Clean** |

**Total Reduction**: 62% LOC reduction (2,583 archived / 4,183 original = 62% eliminated)

---

## Consolidation History

### Sprint 1.2 (2025-10-19): Analyzer Consolidation
- Archived 4 competing analyzers (2,117 LOC)
- Updated imports in `__main__.py` and `__init__.py`
- Created comprehensive documentation

### Sprint 1.3 (2025-10-19): Orchestrator Consolidation
- Archived 1 dead orchestrator (466 LOC)
- Zero usages found - pure dead code
- No import updates needed

**Total Phase 1**: 5 files archived, 2,583 LOC eliminated, 62% reduction

---

**Last Updated**: 2025-10-19 (Sprint 1.3 complete)
**Consolidation**: Phase 1, Sprints 1.2 + 1.3
**Status**: Deprecated, archived for historical reference only
**Do NOT use these files** - they are kept only for understanding the evolution of the codebase.
