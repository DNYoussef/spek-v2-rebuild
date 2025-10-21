# Analyzer Runner (Atomic Skill)

**Skill ID**: `analyzer-runner`
**Type**: Atomic (Reusable Component)
**Version**: 1.0.0
**Priority**: P1 (Important - Legacy code analysis)
**Status**: ✅ PRODUCTION-READY

---

## Auto-Trigger Patterns

**TRIGGER**: Multiple situations
- Analyzing legacy/existing code for refactoring
- Validating code quality before merge
- Compliance checking (NASA Rule 10)
- Technical debt assessment
- Pre-refactoring analysis

**When to Use**:
- ✅ Legacy code analysis (primary use case)
- ✅ Large codebase audits
- ✅ Complexity metrics extraction
- ✅ Maintainability assessment
- ✅ Quality gate validation

**When NOT to Use**:
- ❌ New/greenfield code (use manual validation instead)
- ❌ Code with quality built-in from start
- ❌ Test-driven development (use tester skill)

**Used By** (3 workflows):
- analyzer-usage-workflow.dot (primary)
- completion-checklist.dot (optional quality gate)
- code-review workflow (technical debt analysis)

---

## Purpose

Runs SPEK Analyzer (Radon + Pylint) on legacy code and returns complexity metrics + violations. Single responsibility: Execute analyzers, return metrics and violations.

**Core Function**: Legacy code quality analysis with real linter integration

---

## Agent Integration

**Agent**: Can spawn `code-analyzer` Drone (or run directly via registry)
**Communication**: Direct Python execution or Task tool
**Input**: File path(s), linter selection (radon/pylint/all)
**Output**: Violations (critical/high/medium/low), metrics (CC, MI)

---

## Execution Process

### Method 1: Direct Registry Execution (Recommended)

```bash
# Single file analysis (all linters)
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

results = linter_registry.run_all_linters(Path('file.py'))
violations = linter_registry.aggregate_violations(results)

print(f'Violations: {len(violations)}')
for v in violations:
    print(f'  {v.severity}: {v.description}')
"
```

### Method 2: Specific Linter Execution

```bash
# Radon only (complexity + maintainability)
python -m radon cc file.py -j
python -m radon mi file.py -j

# Pylint only (logic + style)
python -m pylint file.py --output-format=json
```

### Method 3: Metrics Extraction

```bash
python -c "
from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge

bridge = RadonBridge()
result = bridge.run(Path('file.py'))

if 'metrics' in result:
    m = result['metrics']
    print(f'Functions: {m[\"total_functions\"]}')
    print(f'Avg CC: {m[\"average_complexity\"]:.1f}')
    print(f'Max CC: {m[\"max_complexity\"]}')
    print(f'Avg MI: {m[\"average_mi\"]:.1f}')
"
```

---

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | Path | Yes | - | File to analyze |
| `linters` | list[str] | No | `['radon', 'pylint']` | Which linters to run |
| `severity_filter` | list[str] | No | `['critical', 'high', 'medium', 'low']` | Severity levels to include |
| `extract_metrics` | bool | No | `True` | Include Radon metrics in output |

---

## Output Format

### Success Response

```json
{
  "success": true,
  "file": "src/module.py",
  "linters_run": ["radon", "pylint"],
  "violations": [
    {
      "severity": "medium",
      "description": "High cyclomatic complexity (CC=15, rank=C)",
      "line_number": 42,
      "source": "radon",
      "recommendation": "Consider refactoring to reduce complexity"
    }
  ],
  "metrics": {
    "total_functions": 12,
    "average_complexity": 4.2,
    "max_complexity": 15,
    "average_mi": 68.5
  },
  "summary": {
    "critical": 0,
    "high": 0,
    "medium": 1,
    "low": 3
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Linters not available",
  "available_linters": [],
  "recommendation": "pip install radon pylint"
}
```

---

## Decision Logic

### When to Run Analyzer

```
START
  ↓
Is code LEGACY/EXISTING? ──NO──> Use manual validation
  ↓ YES                          (LOC count, NASA check, mypy)
  ↓
Need complexity metrics? ──NO──> Run Pylint only (logic/style)
  ↓ YES                          python -m pylint file.py
  ↓
  ↓
Run full analyzer (Radon + Pylint)
  ↓
python -c "from analyzer.linters import linter_registry; ..."
  ↓
Interpret results:
  - Critical violations? → BLOCK (refactor required)
  - High violations? → WARNING (fix before merge)
  - Medium/low violations? → PASS (document tech debt)
  ↓
END
```

### Severity Response Actions

| Severity | Count | Action |
|----------|-------|--------|
| Critical | ≥1 | ❌ BLOCK: Refactor immediately |
| High | ≥1 | ⚠️ WARNING: Fix before merge |
| Medium | ≥5 | ⚠️ CAUTION: Plan refactoring |
| Low | Any | ℹ️ INFO: Document tech debt |

---

## Interpretation Guide

### Radon Metrics

**Cyclomatic Complexity (CC)**:
- **1-5 (Rank A)**: ✅ Excellent - Easy to test
- **6-10 (Rank B)**: ⚠️ Good - Moderate complexity
- **11-20 (Rank C)**: 🔴 Fair - Consider refactoring
- **21-30 (Rank D)**: 🔴 Poor - Refactor soon
- **30+ (Rank E)**: 🔴🔴 Critical - Refactor immediately

**Maintainability Index (MI)**:
- **80-100 (Rank A)**: ✅ Excellent maintainability
- **60-80 (Rank B)**: ⚠️ Good maintainability
- **40-60 (Rank C)**: 🔴 Fair - Needs improvement
- **20-40 (Rank D)**: 🔴 Poor - Refactor soon
- **0-20 (Rank E)**: 🔴🔴 Critical - Refactor immediately

### Pylint Violations

| Type | Severity | Examples |
|------|----------|----------|
| fatal | critical | Syntax errors, import failures |
| error | high | Undefined variables, type errors |
| warning | medium | Unused vars, deprecated calls |
| refactor | low | Code structure suggestions |
| convention | low | PEP8 style issues |

---

## Common Workflows

### Workflow 1: Single File Analysis

```bash
# Quick analysis (all linters)
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

results = linter_registry.run_all_linters(Path('legacy_module.py'))
violations = linter_registry.aggregate_violations(results)

# Decision logic
critical = sum(1 for v in violations if v.severity == 'critical')
high = sum(1 for v in violations if v.severity == 'high')

if critical > 0:
    print('❌ BLOCK: Refactor required')
elif high > 0:
    print('⚠️ WARNING: Fix before merge')
else:
    print('✅ PASS: No blocking violations')
"
```

### Workflow 2: Directory Analysis

```bash
# Batch analysis
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

all_violations = []
for file in Path('src/legacy/').rglob('*.py'):
    results = linter_registry.run_all_linters(file)
    violations = linter_registry.aggregate_violations(results)
    all_violations.extend(violations)

print(f'Total violations: {len(all_violations)}')
print(f'Critical: {sum(1 for v in all_violations if v.severity == \"critical\")}')
print(f'High: {sum(1 for v in all_violations if v.severity == \"high\")}')
"
```

### Workflow 3: Metrics-Only Extraction

```bash
# Just get metrics (no violations)
python -c "
from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge

bridge = RadonBridge()
result = bridge.run(Path('module.py'))

m = result.get('metrics', {})
print(f'Avg Complexity: {m.get(\"average_complexity\", 0):.1f}')
print(f'Maintainability: {m.get(\"average_mi\", 0):.1f}')
"
```

---

## Prerequisites

### Required Dependencies

```bash
# Install linters
pip install radon pylint

# Verify installation
python -m radon --version  # Expected: 5.1.0+
python -m pylint --version  # Expected: 2.17.7+
```

### Verification

```bash
# Check analyzer availability
python -c "
from analyzer.linters import linter_registry
available = linter_registry.get_available_linters()
print(f'Available linters: {available}')
# Expected: ['pylint', 'radon']
"
```

---

## Performance

**Measured Performance** (Production Validation):
- Radon: ~1-2s per file
- Pylint: ~2-3s per file
- Combined: ~3.78s average per file
- 10 files: ~38s (sequential)
- 100 files: ~6.3 minutes (sequential)

**Optimization**:
- Use parallel execution for large codebases (future)
- Filter files (skip tests, skip known-good files)
- Run only needed linters (Radon OR Pylint, not both)

---

## Error Handling

### Common Errors

1. **Linters not available**:
   ```
   Error: No linters available
   Fix: pip install radon pylint
   ```

2. **Import errors**:
   ```
   Error: ModuleNotFoundError: No module named 'analyzer'
   Fix: export PYTHONPATH=$PWD:$PYTHONPATH
   ```

3. **Cross-platform issues**:
   ```
   Error: FileNotFoundError: radon not found
   Fix: Analyzer uses 'python -m' pattern, ensure linters installed
   ```

### Graceful Degradation

If linters unavailable, skill should:
1. Report which linters are missing
2. Provide installation instructions
3. Offer alternative (manual validation commands)
4. Never fail silently

---

## Integration with Other Skills

### Combines With

- **completion-checklist**: Optional quality gate before marking work complete
- **code-review-assistant**: Technical debt analysis during PR review
- **refactoring-planner**: Identify refactoring targets based on metrics

### Calls From

- **pre-merge-gate**: Validate legacy code before merging changes
- **technical-debt-audit**: Comprehensive codebase quality assessment
- **refactoring-prioritization**: Identify highest-priority refactoring targets

---

## Success Criteria

- ✅ Linters execute successfully (no crashes)
- ✅ Violations returned in unified format
- ✅ Metrics extracted accurately (Radon)
- ✅ Performance <5s per file average
- ✅ Cross-platform compatible (Windows/Linux/macOS)

---

## Resources

### Documentation

- **Quick Reference**: `docs/ANALYZER-QUICK-REFERENCE.md`
- **Full Guide**: `docs/ANALYZER-USAGE-GUIDE.md`
- **Architecture**: `.claude/processes/development/analyzer-architecture.dot`
- **Usage Workflow**: `.claude/processes/development/analyzer-usage-workflow.dot`

### Test Suite

- **Unit Tests**: 119 tests (100% passing)
- **Integration Tests**: 6 tests (real linters, 100% passing)
- **Coverage**: ≥80% (≥90% for critical paths)

### Production Validation

- **Report**: `docs/PRODUCTION-VALIDATION-COMPLETE.md`
- **Files Analyzed**: 4 (radon_bridge, pylint_bridge, api, engine)
- **Result**: 7 violations (all low-severity), production-ready ✅

---

## Maintenance

### Version History

- **1.0.0** (2025-10-19): Initial production release
  - Radon bridge (CC + MI metrics)
  - Pylint bridge (logic + style violations)
  - Registry pattern (multi-linter coordination)
  - Cross-platform compatibility

### Known Issues

1. **Pylint astroid warnings** (Python 3.12):
   - `AttributeError: 'TreeRebuilder' object has no attribute 'visit_typealias'`
   - Impact: Non-blocking, Pylint still produces valid results
   - Fix: Upgrade Pylint/astroid (optional)

### Future Enhancements

1. **Parallel execution** (4x speedup for large codebases)
2. **Caching** (skip unchanged files)
3. **Additional linters** (Flake8, Mypy, Bandit)
4. **Custom thresholds** (per-project configuration)

---

## Example Usage in Claude Code

```markdown
USER: I need to analyze this legacy module for refactoring

CLAUDE: I'll use the analyzer-runner skill to analyze the legacy code.

[Runs analyzer via registry]

Results:
- 12 violations found
- Critical: 0
- High: 2 (undefined variables)
- Medium: 3 (complexity rank C)
- Low: 7 (style issues)

Metrics:
- Avg Complexity: 8.5 (Rank B)
- Avg MI: 62.3 (Rank B)

Recommendation:
⚠️ WARNING: Fix 2 high-severity violations before proceeding.
Consider refactoring 3 medium-complexity functions.

[Lists specific violations with line numbers and recommendations]
```

---

**Version**: 1.0.0
**Created**: 2025-10-19
**Status**: ✅ PRODUCTION-READY
**Test Coverage**: 125 tests (119 unit + 6 integration), 100% passing
**Performance**: <5s per file average (3.78s validated)
