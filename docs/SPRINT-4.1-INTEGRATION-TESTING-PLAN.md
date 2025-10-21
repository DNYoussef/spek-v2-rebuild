# SPRINT 4.1: Integration Testing Plan

**Sprint**: Sprint 4.1 - Production Readiness Validation
**Duration**: 8 hours
**Priority**: P0 (Production validation)
**Date**: 2025-10-19

## Executive Summary

This sprint validates production readiness by testing the analyzer with **real Radon and Pylint executables** (not mocks). This ensures the linter bridges work correctly in real-world scenarios before deployment.

**Goal**: Validate that Radon and Pylint bridges work with actual executables, not just unit test mocks.

**Success Criteria**:
- ✅ Real Radon executable integration works
- ✅ Real Pylint executable integration works
- ✅ End-to-end workflow validated
- ✅ Production-ready confirmation

## Background

**Current State**:
- ✅ Phase 1 complete (all god objects eliminated)
- ✅ Radon bridge implemented (410 LOC, 56 tests passing)
- ✅ Pylint bridge implemented (230 LOC, 46 tests passing)
- ⚠️ **All tests use mocks** (no real executable testing yet)

**Why Integration Testing Matters**:
1. **Mock ≠ Reality**: Mocks simulate behavior, but real executables may have quirks
2. **JSON parsing**: Real Radon/Pylint output may differ from mocked output
3. **Error handling**: Real errors (timeouts, malformed output) need validation
4. **Performance**: Real execution times vs. mock assumptions
5. **Installation validation**: Ensure linters are actually available

## Testing Strategy

### Part 1: Environment Validation (1 hour)

**Goal**: Check if Radon and Pylint are installed

**Tasks**:
1. Check Radon installation: `radon --version`
2. Check Pylint installation: `pylint --version`
3. Install missing linters if needed
4. Verify JSON output format

**Expected Results**:
- Radon version ≥5.0 installed
- Pylint version ≥2.0 installed

### Part 2: Radon Integration Testing (3 hours)

**Goal**: Test Radon bridge with real executable

**Test Cases**:

1. **Simple Python file** (cyclomatic complexity)
   - Create test file with known complexity
   - Run real `radon cc -j`
   - Verify violations match expectations

2. **Complex Python file** (high complexity)
   - Create file with CC > 50 (rank F)
   - Verify critical severity violations

3. **Clean Python file** (low complexity)
   - Create file with CC < 10 (rank A/B)
   - Verify no violations or low severity

4. **Maintainability index**
   - Run real `radon mi -j`
   - Verify MI scores match expectations

5. **Edge cases**
   - Empty file
   - File with syntax errors
   - Very large file (1000+ LOC)

**Expected Results**:
- All real Radon commands execute successfully
- JSON parsing works with real output
- Violations are created correctly
- Performance is acceptable (<5s per file)

### Part 3: Pylint Integration Testing (2 hours)

**Goal**: Test Pylint bridge with real executable

**Test Cases**:

1. **Simple Python file** (clean code)
   - Create PEP8-compliant file
   - Run real `pylint --output-format=json`
   - Verify no violations or low severity

2. **Problematic Python file** (many issues)
   - Create file with style violations, logic errors
   - Verify high severity violations

3. **Mixed violations**
   - Fatal, error, warning, refactor, convention, info
   - Verify severity mapping (fatal→critical, etc.)

4. **Edge cases**
   - Empty file
   - File with syntax errors
   - Very large file

**Expected Results**:
- All real Pylint commands execute successfully
- JSON parsing works with real output
- Severity mapping works correctly
- Performance is acceptable (<3s per file)

### Part 4: End-to-End Workflow (2 hours)

**Goal**: Validate complete analyzer workflow with real linters

**Test Scenarios**:

1. **Single file analysis**
   - Analyze real Python file from analyzer codebase
   - Run Radon + Pylint via linter_registry
   - Aggregate violations
   - Generate report

2. **Batch file analysis**
   - Analyze 10 files from analyzer codebase
   - Verify all files processed
   - Check performance (should be <60s total)

3. **Error recovery**
   - Analyze file that causes Radon/Pylint error
   - Verify graceful error handling
   - Ensure other files continue processing

4. **Registry integration**
   - Use `linter_registry.run_all_linters()`
   - Verify both Radon + Pylint run
   - Aggregate violations correctly

**Expected Results**:
- End-to-end workflow works with real linters
- Error handling is robust
- Performance is acceptable
- Reports are accurate

## Test Files

We'll create test files with known characteristics:

### test_simple_clean.py
```python
def add(a: int, b: int) -> int:
    """Add two numbers."""
    assert isinstance(a, int), "a must be int"
    assert isinstance(b, int), "b must be int"
    return a + b
```
**Expected**:
- Radon CC: 1 (rank A)
- Radon MI: ~90 (rank A)
- Pylint: No violations

### test_complex_function.py
```python
def complex_logic(data):
    # High cyclomatic complexity (15+ paths)
    if data is None:
        return None
    if len(data) == 0:
        return []
    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        if isinstance(item, str):
            if len(item) > 10:
                results.append(item.upper())
            else:
                results.append(item.lower())
        elif isinstance(item, int):
            if item > 100:
                results.append(item * 2)
            elif item > 50:
                results.append(item * 1.5)
            else:
                results.append(item)
        elif isinstance(item, dict):
            if 'value' in item:
                results.append(item['value'])
            else:
                results.append(None)

    return results
```
**Expected**:
- Radon CC: 15-20 (rank C/D)
- Radon MI: 40-50 (rank C)
- Pylint: Multiple refactoring suggestions

### test_god_function.py
```python
def god_function(x, y, z, a, b, c, d, e, f, g):
    # Extreme complexity (50+ paths)
    # ... (implement with 50+ if/elif branches)
```
**Expected**:
- Radon CC: 50+ (rank E/F)
- Radon MI: <20 (rank C/F)
- Pylint: Critical violations

## Success Criteria

### Radon Bridge
- ✅ Real `radon cc -j` executes successfully
- ✅ Real `radon mi -j` executes successfully
- ✅ JSON output parsed correctly
- ✅ Violations created with correct severity
- ✅ Edge cases handled gracefully
- ✅ Performance: <5s per file

### Pylint Bridge
- ✅ Real `pylint --output-format=json` executes successfully
- ✅ JSON output parsed correctly
- ✅ Severity mapping works (fatal→critical, etc.)
- ✅ Edge cases handled gracefully
- ✅ Performance: <3s per file

### End-to-End
- ✅ `linter_registry.run_all_linters()` works
- ✅ Violations aggregated correctly
- ✅ Error handling prevents crashes
- ✅ Batch processing works (10+ files)
- ✅ Performance: <60s for 10 files

### Production Readiness
- ✅ Zero crashes with real executables
- ✅ All edge cases handled
- ✅ Performance meets targets
- ✅ Reports are accurate
- ✅ Ready for deployment

## Timeline

| Part | Task | Duration | Dependencies |
|------|------|----------|--------------|
| 1 | Environment validation | 1 hour | None |
| 2 | Radon integration testing | 3 hours | Part 1 |
| 3 | Pylint integration testing | 2 hours | Part 1 |
| 4 | End-to-end workflow | 2 hours | Parts 2-3 |
| **Total** | | **8 hours** | Sequential |

## Risks & Mitigations

### Risk 1: Linters Not Installed
**Probability**: Medium
**Impact**: High
**Mitigation**: Install via pip if missing: `pip install radon pylint`

### Risk 2: JSON Format Differences
**Probability**: Low
**Impact**: Medium
**Mitigation**: Compare real output vs. mocked output, adjust parsing if needed

### Risk 3: Performance Issues
**Probability**: Low
**Impact**: Medium
**Mitigation**: Profile slow executions, add caching if needed

### Risk 4: Edge Case Failures
**Probability**: Medium
**Impact**: Low
**Mitigation**: Fix error handling, add more comprehensive error messages

## Deliverables

1. **Integration test results** (real Radon + Pylint)
2. **Performance benchmarks** (execution times)
3. **Edge case validation** (error handling)
4. **Production readiness report**
5. **Bug fixes** (if any issues found)

## Next Steps After Completion

If integration testing passes:
- ✅ **Production deployment ready**
- Document deployment procedure
- Create production configuration
- Deploy to staging environment

If issues found:
- Fix bugs in bridges
- Re-run integration tests
- Validate fixes

---

**Version**: 1.0
**Created**: 2025-10-19
**Author**: Claude Sonnet 4
**Sprint**: Sprint 4.1 (Integration Testing)
**Status**: READY TO START
