# Meta-Audit: Comprehensive Code Quality Orchestrator

## Overview

The Meta-Audit skill is a comprehensive quality orchestrator that runs three sequential audit phases with automatic fixes between each stage. This skill ensures code progresses from theater-free → functionally correct → highest quality standards by coordinating theater detection, functionality validation, and style/quality refactoring with intelligent fix agents spawned between each phase.

Use this skill when you need end-to-end quality validation and improvement, not just detection. Meta-Audit doesn't just report issues—it fixes them systematically, ensuring production-ready code at the end of the workflow.

## When to Use This Skill

Activate Meta-Audit when:
- **Pre-deployment validation**: Comprehensive quality check before production
- **Post-implementation cleanup**: After Loop 2 completes, before Loop 3
- **Legacy code refactoring**: Bringing existing code up to standards
- **Quality gate enforcement**: Ensuring code meets all quality criteria
- **Continuous improvement**: Regular quality sweeps of codebase

**Auto-Trigger Patterns**:
- Keywords: "meta audit", "comprehensive audit", "full quality check", "audit and fix"
- Phrases: "Make this production-ready", "Clean up the code", "Run full quality validation"
- Loop 3 Phase 3: Comprehensive audit suite
- User requests: "Fix all quality issues", "Bring code to highest standards"

**DO NOT use for**:
- Quick spot checks (use individual audit skills instead)
- Single-issue fixes (spawn specific Drone directly)
- Read-only audits (Meta-Audit makes changes)

## Meta-Audit Workflow: 3-Phase Sequential Process

The Meta-Audit follows a strict sequential workflow where each phase MUST pass before proceeding to the next:

```
Phase 1: Theater Detection & Fix
         ↓ (theater-free code)
Phase 2: Functionality Validation & Fix
         ↓ (working code)
Phase 3: Style/Quality Refactoring
         ↓ (production-ready code)
```

Each phase follows the **Audit → Fix → Verify** pattern:
1. Run audit to detect issues
2. Spawn fix agent(s) to resolve issues
3. Re-run audit to verify fixes worked
4. If fixes fail after 3 attempts → Escalate to user

---

## Phase 1: Theater Detection & Elimination

**Purpose**: Remove all fake, mock, placeholder code before validating functionality

**Why First**: Can't validate real functionality if code contains mocks/TODOs/placeholders

### Step 1: Theater Detection Audit

Run theater detection to find all theater patterns:

**Actions**:
1. Invoke existing audit system:
   ```python
   from .scripts.meta_audit_orchestrator import MetaAuditOrchestrator

   orchestrator = MetaAuditOrchestrator(target_path="src/")
   theater_results = orchestrator.run_theater_audit()
   ```

2. Theater audit checks for:
   - **TODO/FIXME comments**: Unfinished work markers
   - **Mock implementations**: `mock_`, `fake_`, `Mock()`, `MagicMock`
   - **Placeholder code**: `pass  # TODO`, `raise NotImplementedError`, `...`
   - **Hardcoded test data**: `test_data = [...]` in production code
   - **Commented-out code**: `# def old_function()...`

3. Theater scoring system:
   ```python
   score = (
       todo_count * 10 +
       mock_count * 20 +
       placeholder_count * 15 +
       commented_code_count * 5
   )
   # PASS: score < 60
   # FAIL: score ≥ 60 (requires fixes)
   ```

**Theater Audit Output**:
```json
{
  "audit": "theater",
  "passed": false,
  "score": 125,
  "results": {
    "todo_count": 5,
    "mocks": [
      {"file": "src/auth.py", "line": 42, "pattern": "mock_user_data"},
      {"file": "src/payments.py", "line": 89, "pattern": "fake_payment_gateway"}
    ],
    "placeholders": [
      {"file": "src/notifications.py", "line": 15, "pattern": "pass  # TODO: implement email"}
    ]
  },
  "files_affected": ["src/auth.py", "src/payments.py", "src/notifications.py"]
}
```

### Step 2: Spawn Theater Fix Agent

If theater audit FAILS (score ≥ 60), spawn `coder` Drone to eliminate theater:

**Spawn Pattern**:
```python
Task(
    subagent_type="coder",
    description="Eliminate theater code (TODOs, mocks, placeholders)",
    prompt=f"""You are the Coder Drone in Meta-Audit Phase 1: Theater Elimination.

TASK: Remove ALL theater code and replace with genuine implementations

THEATER AUDIT RESULTS:
{json.dumps(theater_results, indent=2)}

FILES TO FIX:
{theater_results['files_affected']}

INSTRUCTIONS:
1. For each TODO/FIXME:
   - Implement the actual feature (not another TODO)
   - Ensure implementation is complete and functional

2. For each mock/fake:
   - Replace with real implementation
   - Use actual services/APIs/databases
   - Add proper error handling

3. For each placeholder:
   - Replace `pass` with actual logic
   - Replace `NotImplementedError` with implementation
   - Replace `...` with concrete code

4. For commented-out code:
   - Remove entirely if obsolete
   - Uncomment and fix if needed

CONSTRAINTS:
- NO new TODO comments
- NO mock/fake implementations
- ALL functions must have real logic
- NASA Rule 10: ≤60 LOC per function
- Write tests for new implementations

DELIVERABLES:
- Modified files with theater eliminated
- Brief summary of changes per file
- New tests for implementations (if needed)

TIME BUDGET: 45 minutes

Report when complete or if blocked."""
)
```

### Step 3: Verify Theater Elimination

After Coder completes fixes, re-run theater audit:

**Actions**:
1. Re-run theater audit on fixed files
2. Check if score < 60 (PASS threshold)
3. If PASS → Proceed to Phase 2
4. If FAIL after 3 attempts → Escalate to user

**Retry Logic**:
```python
attempt = 0
max_attempts = 3

while attempt < max_attempts:
    # Spawn coder to fix theater
    coder_fixes = spawn_theater_fix_agent(theater_results)

    # Re-audit
    theater_results = orchestrator.run_theater_audit()

    if theater_results['passed']:
        print("✅ Phase 1 Complete: Theater eliminated")
        break

    attempt += 1

if not theater_results['passed']:
    escalate_to_user("Theater elimination failed after 3 attempts", theater_results)
```

**Phase 1 Success Criteria**:
- ✅ Theater score < 60
- ✅ Zero TODO/FIXME comments
- ✅ Zero mock/fake implementations
- ✅ Zero placeholder code
- ✅ All code is genuine implementation

---

## Phase 2: Functionality Validation & Correction

**Purpose**: Ensure all code actually works (tests pass, imports valid, runtime correct)

**Why Second**: Now that theater is eliminated, we can validate real functionality

### Step 1: Functionality Audit

Run comprehensive functionality validation:

**Actions**:
1. Run functionality audit:
   ```python
   functionality_results = orchestrator.run_functionality_audit()
   ```

2. Functionality audit checks:
   - **Test Execution**: All pytest/jest tests pass
   - **Import Validation**: All imports resolve correctly
   - **Runtime Checks**: Code executes without errors
   - **Coverage**: ≥80% code coverage target
   - **Edge Cases**: Error handling tested

**Functionality Audit Output**:
```json
{
  "audit": "functionality",
  "passed": false,
  "results": {
    "tests": {
      "total": 42,
      "passed": 38,
      "failed": 4,
      "failures": [
        {"test": "test_auth_login", "error": "AssertionError: Expected 200, got 401"},
        {"test": "test_payment_process", "error": "AttributeError: 'NoneType' has no attribute 'charge'"}
      ]
    },
    "imports": {
      "success": true,
      "files_checked": 25
    },
    "coverage": 0.73
  },
  "files_with_failures": ["tests/test_auth.py", "tests/test_payments.py"]
}
```

### Step 2: Spawn Functionality Fix Agents

If functionality audit FAILS, spawn appropriate fix agents:

**Fix Strategy**:
1. **Test failures** → Spawn `debugger` Drone
2. **Import errors** → Spawn `coder` Drone
3. **Low coverage** → Spawn `tester` Drone

**Debugger Spawn** (for test failures):
```python
Task(
    subagent_type="debugger",
    description="Fix failing tests and functionality bugs",
    prompt=f"""You are the Debugger Drone in Meta-Audit Phase 2: Functionality Correction.

TASK: Fix all failing tests and functionality bugs

FUNCTIONALITY AUDIT RESULTS:
{json.dumps(functionality_results, indent=2)}

FAILING TESTS:
{failing_tests}

INSTRUCTIONS:
1. Analyze each test failure:
   - Read test code to understand expected behavior
   - Read implementation code to find bug
   - Identify root cause (logic error, missing edge case, etc.)

2. Fix the bugs:
   - Modify implementation to pass tests
   - DO NOT modify tests to pass implementation (wrong direction!)
   - Ensure fix doesn't break other tests
   - Add missing edge case handling

3. Verify fixes:
   - Run tests after each fix
   - Confirm all tests pass
   - Check for regression (other tests still passing)

CONSTRAINTS:
- Fix implementation, not tests
- Maintain NASA Rule 10 (≤60 LOC per function)
- Add error handling for edge cases
- NO new theater code (no TODOs, mocks)

DELIVERABLES:
- Fixed implementation files
- Test run summary (all passing)
- Brief explanation of each fix

TIME BUDGET: 60 minutes

Report when all tests pass or if blocked."""
)
```

**Tester Spawn** (for low coverage):
```python
Task(
    subagent_type="tester",
    description="Add tests to reach ≥80% coverage",
    prompt=f"""You are the Tester Drone in Meta-Audit Phase 2: Coverage Improvement.

TASK: Add tests to reach ≥80% code coverage

CURRENT COVERAGE: {functionality_results['results']['coverage'] * 100}%
TARGET COVERAGE: 80%

UNCOVERED CODE:
{uncovered_lines}

INSTRUCTIONS:
1. Identify uncovered code paths:
   - Functions without any tests
   - Branches not tested (if/else, try/except)
   - Edge cases not covered

2. Write comprehensive tests:
   - Unit tests for each function
   - Integration tests for workflows
   - Edge case tests (null inputs, errors, boundaries)
   - Use existing test framework (pytest/jest)

3. Aim for quality coverage:
   - Test happy paths
   - Test error paths
   - Test edge cases
   - Use meaningful assertions

CONSTRAINTS:
- ≥80% coverage target
- All new tests must pass
- Follow existing test conventions
- Clear test names (test_function_when_condition_then_result)

DELIVERABLES:
- New test files/functions
- Coverage report showing ≥80%
- Brief summary of tests added

TIME BUDGET: 45 minutes

Report when coverage ≥80% or if blocked."""
)
```

### Step 3: Verify Functionality Fixes

After fix agents complete, re-run functionality audit:

**Actions**:
1. Re-run functionality audit
2. Check all criteria:
   - All tests passing ✅
   - All imports valid ✅
   - Coverage ≥80% ✅
3. If PASS → Proceed to Phase 3
4. If FAIL after 3 attempts → Escalate

**Retry Logic**:
```python
attempt = 0
max_attempts = 3

while attempt < max_attempts:
    # Spawn appropriate fix agent(s)
    if has_test_failures:
        spawn_debugger(functionality_results)
    if low_coverage:
        spawn_tester(functionality_results)

    # Re-audit
    functionality_results = orchestrator.run_functionality_audit()

    if functionality_results['passed']:
        print("✅ Phase 2 Complete: All tests passing, coverage ≥80%")
        break

    attempt += 1

if not functionality_results['passed']:
    escalate_to_user("Functionality fixes failed after 3 attempts", functionality_results)
```

**Phase 2 Success Criteria**:
- ✅ All tests passing (100%)
- ✅ All imports valid
- ✅ Code coverage ≥80%
- ✅ Runtime checks passing
- ✅ No functionality bugs

---

## Phase 3: Style/Quality Refactoring

**Purpose**: Refactor code to highest quality standards without breaking functionality

**Why Last**: Code is now theater-free and working—safe to refactor for quality

### Step 1: Style/Quality Audit

Run comprehensive style and quality analysis using the Analyzer:

**Actions**:
1. Run full analyzer on codebase:
   ```bash
   python -m analyzer.api analyze --source src/ --format json > style_audit.json
   ```

2. Run NASA compliance check:
   ```python
   style_results = orchestrator.run_style_audit()
   ```

3. Style/quality audit checks:
   - **NASA Rule 10 Compliance**: ≤60 LOC per function, ≥2 assertions (critical paths)
   - **Linting**: Flake8/ESLint passing
   - **Type Safety**: MyPy/TypeScript strict mode passing
   - **Code Complexity**: Cyclomatic complexity ≤10
   - **Duplication**: <5% duplicate code
   - **Naming**: Descriptive variable/function names
   - **Documentation**: Docstrings for public functions

**Style Audit Output**:
```json
{
  "audit": "style",
  "passed": false,
  "results": {
    "nasa_compliance": {
      "passed": false,
      "compliance_rate": 0.91,
      "violations": [
        {"file": "src/payments.py", "function": "process_payment", "length": 75},
        {"file": "src/auth.py", "function": "authenticate_user", "length": 68}
      ]
    },
    "linting": {
      "passed": false,
      "issues": [
        {"file": "src/utils.py", "line": 23, "message": "E501 line too long"},
        {"file": "src/models.py", "line": 45, "message": "F841 unused variable 'result'"}
      ]
    },
    "complexity": {
      "high_complexity": [
        {"file": "src/parser.py", "function": "parse_config", "complexity": 15}
      ]
    },
    "duplicates": {
      "percentage": 0.08,
      "instances": [...]
    }
  }
}
```

### Step 2: Spawn Quality Refactoring Agent

If style audit FAILS, spawn `reviewer` Drone for quality refactoring:

**Reviewer Spawn**:
```python
Task(
    subagent_type="reviewer",
    description="Refactor code to highest quality standards",
    prompt=f"""You are the Reviewer Drone in Meta-Audit Phase 3: Quality Refactoring.

TASK: Refactor code to meet highest quality standards WITHOUT breaking functionality

STYLE AUDIT RESULTS:
{json.dumps(style_results, indent=2)}

ANALYZER REPORT:
{analyzer_report_path}

INSTRUCTIONS:
1. NASA Rule 10 Violations:
   - Refactor functions >60 LOC into smaller functions
   - Extract helper functions for clarity
   - Maintain single responsibility per function
   - Preserve ALL functionality (tests must still pass)

2. Linting Issues:
   - Fix line length violations (wrap lines appropriately)
   - Remove unused variables
   - Fix import order/formatting
   - Apply consistent code style

3. Type Safety:
   - Add missing type hints (Python) or types (TypeScript)
   - Fix type errors
   - Use proper generic types where needed

4. Code Complexity:
   - Refactor high-complexity functions (complexity >10)
   - Extract nested logic into functions
   - Simplify conditional logic
   - Use early returns to reduce nesting

5. Code Duplication:
   - Extract duplicate code into shared functions
   - Create utility modules for common patterns
   - Use composition over copy-paste

6. Documentation:
   - Add docstrings for all public functions
   - Document complex logic with inline comments
   - Update type hints in docstrings

CONSTRAINTS:
- ⚠️ CRITICAL: Run tests after EVERY refactoring step
- ⚠️ If tests break, revert and try different approach
- ⚠️ Functionality MUST remain unchanged
- NASA Rule 10: ≤60 LOC per function (strict)
- Maintain existing API contracts
- Keep changes minimal (only quality improvements)

REFACTORING STRATEGY:
1. Start with smallest violations first
2. Refactor one function at a time
3. Run tests after each function refactored
4. If tests fail, revert immediately
5. Commit working refactorings, skip breaking ones

DELIVERABLES:
- Refactored files meeting quality standards
- Test run confirmation (all tests still passing)
- Summary of refactorings with before/after metrics
- List of any violations that couldn't be fixed (with reasons)

TIME BUDGET: 90 minutes

Report when complete or if blocked."""
)
```

### Step 3: Verify Quality Refactoring

After Reviewer completes refactoring, verify changes didn't break functionality:

**Actions**:
1. **CRITICAL**: Re-run Phase 2 functionality audit
   - Ensure ALL tests still pass
   - Ensure coverage didn't drop
   - Ensure no new bugs introduced

2. Re-run Phase 3 style audit
   - Check NASA compliance improved
   - Check linting issues resolved
   - Check complexity reduced

3. Compare metrics:
   ```python
   before_metrics = {
       "nasa_compliance": 0.91,
       "linting_issues": 15,
       "avg_complexity": 8.5,
       "duplicates": 0.08
   }

   after_metrics = {
       "nasa_compliance": 0.98,
       "linting_issues": 2,
       "avg_complexity": 6.2,
       "duplicates": 0.03
   }

   improvement = calculate_improvement(before_metrics, after_metrics)
   ```

4. If refactoring broke tests:
   - Revert changes
   - Retry with more conservative approach
   - If fails after 3 attempts, accept current quality level

**Retry Logic**:
```python
attempt = 0
max_attempts = 3

while attempt < max_attempts:
    # Spawn reviewer for refactoring
    reviewer_refactoring = spawn_reviewer(style_results)

    # CRITICAL: Verify tests still pass
    functionality_check = orchestrator.run_functionality_audit()
    if not functionality_check['passed']:
        print("⚠️ Refactoring broke tests, reverting...")
        revert_changes()
        attempt += 1
        continue

    # Re-audit style
    style_results = orchestrator.run_style_audit()

    if style_results['passed']:
        print("✅ Phase 3 Complete: Code meets highest quality standards")
        break

    attempt += 1

if not style_results['passed']:
    # Accept current quality level, don't break working code
    print("⚠️ Some quality standards not met, but code is functional")
    log_remaining_issues(style_results)
```

**Phase 3 Success Criteria**:
- ✅ NASA Rule 10: ≥96% compliance
- ✅ Linting: <5 minor issues remaining
- ✅ Type safety: 100% coverage
- ✅ Complexity: Average ≤8, max ≤12
- ✅ Duplication: <5%
- ✅ **MOST IMPORTANT**: All tests still passing

---

## Meta-Audit Orchestration Script

The Meta-Audit uses a centralized orchestrator script to coordinate all phases:

**Script**: `.claude/skills/meta-audit/scripts/meta_audit_orchestrator.py`

**Key Functions**:
```python
class MetaAuditOrchestrator:
    def run_meta_audit(self, target_path: Path) -> Dict[str, Any]:
        """Run complete 3-phase meta-audit with fixes."""
        results = {"phases": []}

        # Phase 1: Theater
        phase1 = self.run_phase1_theater(target_path)
        results["phases"].append(phase1)
        if not phase1["passed"]:
            return self._escalate("Phase 1 failed", results)

        # Phase 2: Functionality
        phase2 = self.run_phase2_functionality(target_path)
        results["phases"].append(phase2)
        if not phase2["passed"]:
            return self._escalate("Phase 2 failed", results)

        # Phase 3: Style/Quality
        phase3 = self.run_phase3_style(target_path)
        results["phases"].append(phase3)
        if not phase3["passed"]:
            # Acceptable: code works, just not perfect quality
            results["warning"] = "Some quality standards not met"

        results["overall_status"] = "SUCCESS"
        return results

    def run_phase1_theater(self, target_path: Path) -> Dict[str, Any]:
        """Phase 1: Theater detection and elimination."""
        for attempt in range(3):
            audit = self.run_theater_audit(target_path)
            if audit["passed"]:
                return {"phase": 1, "passed": True, "attempts": attempt + 1}

            # Spawn fix agent
            self._spawn_theater_fix_agent(audit)

        return {"phase": 1, "passed": False, "attempts": 3}

    # Similar for phase2 and phase3...
```

---

## Integration with Existing Systems

### Analyzer Integration

Meta-Audit uses the existing analyzer for comprehensive code analysis:

**Usage**:
```python
# Full analyzer scan
result = subprocess.run(
    ["python", "-m", "analyzer.api", "analyze",
     "--source", "src/", "--format", "json"],
    capture_output=True
)

analyzer_report = json.loads(result.stdout)

# Extract quality metrics
nasa_compliance = analyzer_report["nasa_compliance_rate"]
complexity = analyzer_report["avg_complexity"]
duplicates = analyzer_report["duplication_percentage"]
```

### Audit Runner Integration

Meta-Audit extends the existing `audit_runner.py`:

**Usage**:
```python
from .scripts.audit_runner import AuditRunner

runner = AuditRunner(project_root=Path.cwd())

# Use existing audit methods
theater_results = runner.run_theater_audit(Path("src"))
functionality_results = runner.run_functionality_audit(Path("src"))
style_results = runner.run_style_audit(Path("src"))
```

### Loop 3 Integration

Meta-Audit is invoked during Loop 3 comprehensive quality validation:

**Loop 3 Phase 3** (Comprehensive Audit Suite):
```markdown
### Phase 3: Comprehensive Audit Suite

**Use Meta-Audit skill** for end-to-end quality validation and fixes:

Use meta-audit skill:
- Target: src/ (all implementation files)
- Mode: full (all 3 phases with auto-fix)
- Quality target: production-ready

Meta-Audit will:
1. Eliminate all theater code (Phase 1)
2. Fix all functionality issues (Phase 2)
3. Refactor to highest quality standards (Phase 3)
4. Report final quality metrics
```

---

## Success Criteria

Meta-Audit is successful when:

### Phase 1 (Theater):
- ✅ Theater score <60
- ✅ Zero TODO/FIXME/HACK comments
- ✅ Zero mock/fake implementations
- ✅ Zero placeholder code (pass/NotImplementedError/...)

### Phase 2 (Functionality):
- ✅ All tests passing (100%)
- ✅ Code coverage ≥80%
- ✅ All imports valid
- ✅ Runtime checks passing

### Phase 3 (Style/Quality):
- ✅ NASA Rule 10: ≥96% compliance
- ✅ Linting: <5 minor issues
- ✅ Type safety: 100% coverage
- ✅ Complexity: avg ≤8
- ✅ Duplication: <5%
- ✅ **ALL TESTS STILL PASSING** (regression check)

### Overall:
- ✅ All 3 phases completed
- ✅ Code is production-ready
- ✅ No breaking changes introduced
- ✅ Quality metrics improved from baseline

---

## Error Handling & Escalation

**3-Strike Rule Per Phase**:
- Each phase gets 3 attempts to fix issues
- If phase fails after 3 attempts → Escalate to user
- User decides: continue to next phase OR abort

**Escalation Scenarios**:

1. **Phase 1 Escalation** (Theater elimination failed):
   - Remaining theater issues documented
   - User decides: manual fix OR accept theater
   - If accept: Warning added, continue to Phase 2

2. **Phase 2 Escalation** (Functionality fixes failed):
   - Failing tests documented
   - User decides: manual fix OR abort
   - If abort: Meta-Audit stops, no Phase 3

3. **Phase 3 Escalation** (Refactoring broke tests):
   - Revert refactoring, keep working code
   - Report: "Code functional but quality standards not fully met"
   - Document remaining quality issues

**Escalation Message Template**:
```
⚠️ META-AUDIT ESCALATION: Phase {phase} Failed After 3 Attempts

PHASE: {phase_name}
ATTEMPTS: 3
ISSUES REMAINING: {issue_count}

DETAILS:
{issue_details}

OPTIONS:
1. Manual fix: Review issues and fix manually
2. Skip phase: Accept current state, continue to next phase (if applicable)
3. Abort: Stop meta-audit at current phase

What would you like to do?
```

---

## Helper Scripts & Resources

### Scripts

**meta_audit_orchestrator.py** - Main orchestrator:
See [scripts/meta_audit_orchestrator.py](scripts/meta_audit_orchestrator.py)

**phase_runners.py** - Individual phase execution:
Contains `run_phase1_theater()`, `run_phase2_functionality()`, `run_phase3_style()`

**fix_agent_spawner.py** - Agent spawning logic:
Spawns appropriate fix agents based on audit results

### Diagrams

**meta-audit-process.dot** - Complete workflow visualization:
See [diagrams/meta-audit-process.dot](diagrams/meta-audit-process.dot)

---

## Usage Examples

### Example 1: Complete Meta-Audit

**User Request**: "Run meta-audit on src/ to make it production-ready"

**Execution**:
```python
# Use skill via orchestrator
from .scripts.meta_audit_orchestrator import MetaAuditOrchestrator

orchestrator = MetaAuditOrchestrator(target_path="src/")
result = orchestrator.run_meta_audit()

# Result structure
{
  "overall_status": "SUCCESS",
  "phases": [
    {
      "phase": 1,
      "name": "Theater Elimination",
      "passed": True,
      "attempts": 2,
      "before_score": 145,
      "after_score": 15,
      "fixes_applied": 8
    },
    {
      "phase": 2,
      "name": "Functionality Validation",
      "passed": True,
      "attempts": 1,
      "tests_before": {"passed": 38, "failed": 4},
      "tests_after": {"passed": 42, "failed": 0},
      "coverage_before": 0.73,
      "coverage_after": 0.85
    },
    {
      "phase": 3,
      "name": "Quality Refactoring",
      "passed": True,
      "attempts": 2,
      "nasa_compliance_before": 0.91,
      "nasa_compliance_after": 0.98,
      "complexity_reduction": 2.3,
      "duplicates_removed": 0.05
    }
  ],
  "final_quality_score": 0.95,
  "production_ready": True
}
```

### Example 2: Phase-by-Phase Execution

**User Request**: "Run theater audit first, let me review before continuing"

**Execution**:
```python
orchestrator = MetaAuditOrchestrator(target_path="src/")

# Phase 1 only
phase1 = orchestrator.run_phase1_theater()
print(f"Theater elimination: {phase1['status']}")

# User reviews, then continues
phase2 = orchestrator.run_phase2_functionality()
phase3 = orchestrator.run_phase3_style()
```

### Example 3: Selective Meta-Audit

**User Request**: "Skip theater, just validate functionality and quality"

**Execution**:
```python
orchestrator = MetaAuditOrchestrator(target_path="src/")

# Skip Phase 1
result = orchestrator.run_meta_audit(skip_phases=[1])

# Runs Phase 2 and Phase 3 only
```

---

## Performance Targets

| Phase | Target Time | Typical Time |
|-------|-------------|--------------|
| Phase 1 (Theater) | 45 min | 30-60 min |
| Phase 2 (Functionality) | 60 min | 45-90 min |
| Phase 3 (Quality) | 90 min | 60-120 min |
| **Total Meta-Audit** | **195 min (3.25 hrs)** | **135-270 min (2.25-4.5 hrs)** |

**Time varies based on**:
- Codebase size
- Number of issues found
- Fix complexity
- Number of retries needed

---

## Related Skills

- **theater-detection-audit**: Phase 1 detection (Meta-Audit adds auto-fix)
- **functionality-audit**: Phase 2 validation (Meta-Audit adds auto-fix)
- **style-audit**: Phase 3 analysis (Meta-Audit adds auto-refactoring)
- **loop3-quality**: Uses Meta-Audit for comprehensive validation
- **drone-selection**: Used to spawn appropriate fix agents
- **analyzer**: Used for comprehensive code quality analysis

---

**Version**: 1.0.0
**Last Updated**: 2025-10-18
**Part of**: SPEK Platform Quality System
**Related Skills**: `loop3-quality`, `theater-detection-audit`, `functionality-audit`, `style-audit`, `drone-selection`
