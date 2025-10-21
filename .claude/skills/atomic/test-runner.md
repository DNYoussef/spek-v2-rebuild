# Test Runner (Atomic Skill)

**Skill ID**: `test-runner`
**Type**: Atomic (Reusable Component)
**Version**: 1.0.0
**Priority**: P0 (Critical - Used in 5+ workflows)

---

## Auto-Trigger Patterns

**TRIGGER**: Multiple situations
- Before marking work complete
- On Write/Edit operations (optional gate)
- Before deployment
- After code changes

**When to Use**:
- ✅ Before commit/push
- ✅ In completion checklist
- ✅ In TDD cycle
- ✅ Before deployment
- ✅ After fixing bugs

**Used By** (5 workflows):
- completion-checklist.dot
- new-feature-implementation.dot
- deployment-readiness-checklist.dot
- pre-deployment-verification.dot
- post-deployment-verification.dot

---

## Purpose

Runs test suite and validates all tests pass. Single responsibility: Execute tests, return pass/fail.

---

## Agent Integration

**Agent**: Spawns `tester` Drone
**Communication**: Task tool → Flask endpoint
**Input**: Test command, target files
**Output**: Pass/fail status, coverage, failed tests list

---

## Execution Process

### Step 1: Detect Test Framework
```bash
# Check which test framework exists
if [ -f "package.json" ] && grep -q "jest\|vitest\|playwright" package.json; then
    framework="npm"
    command="npm test"
elif [ -f "pytest.ini" ] || [ -f "setup.py" ]; then
    framework="pytest"
    command="pytest"
else
    framework="unknown"
fi
```

### Step 2: Run Tests
```bash
# Execute test command
$command

# Capture exit code
exit_code=$?
```

### Step 3: Parse Results
```python
def parse_test_results(output, exit_code):
    return {
        "passed": exit_code == 0,
        "total": extract_total_tests(output),
        "failed": extract_failed_tests(output),
        "coverage": extract_coverage(output),
        "duration": extract_duration(output),
        "failed_tests": extract_failed_test_names(output)
    }
```

### Step 4: Return Structured Result
```json
{
    "skill": "test-runner",
    "passed": true,
    "total_tests": 139,
    "failed_tests": 0,
    "coverage": 85.3,
    "duration_ms": 4500,
    "failed_test_list": [],
    "recommendation": "All tests passed ✅"
}
```

---

## Cascade Integration

**Called By**:
- completion-gate-orchestrator
- tdd-cycle-orchestrator
- pre-deploy-gate-orchestrator

**Calls**: `tester` Drone via Task tool

**Example**:
```
completion-gate-orchestrator (composite)
  ├─> test-runner (this atomic skill)
  │     └─> Spawns: tester Drone
  │           └─> Executes: npm test
  │                 └─> Returns: pass/fail
  ├─> build-verifier (another atomic)
  └─> ... 8 more gates
```

---

## Implementation

### Command Mapping
```python
TEST_COMMANDS = {
    "npm": "npm test",
    "pytest": "pytest --cov=src --cov-report=term-missing",
    "playwright": "npx playwright test",
    "jest": "npx jest --coverage",
    "vitest": "npx vitest run"
}
```

### Execution Function
```python
async def run_tests(framework="auto", target=None):
    """
    Run test suite and return structured results.

    Args:
        framework: Test framework (auto-detect if not specified)
        target: Specific test file/pattern (optional)

    Returns:
        dict: Test results with pass/fail, coverage, failed tests
    """
    # Auto-detect framework
    if framework == "auto":
        framework = detect_test_framework()

    # Build command
    command = TEST_COMMANDS.get(framework, "npm test")
    if target:
        command += f" {target}"

    # Execute
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )

    # Parse results
    return parse_test_results(result.stdout, result.returncode)
```

---

## Agent Spawn Instructions

```python
# When this atomic skill needs agent help
from src.coordination.agent_registry import find_drones_for_task

# Find tester drone
drones = find_drones_for_task("run tests", loop="loop2")
tester_drone = drones[0]  # Should be "tester"

# Spawn via Task tool
Task(
    subagent_type=tester_drone,
    description="Run test suite",
    prompt=f"""
You are the Tester Drone. Execute the test suite and report results.

Project Context: {project_context}

Task: Run all tests using {framework}
Command: {command}

Report:
1. Total tests run
2. Tests passed/failed
3. Coverage percentage
4. List of failed tests (if any)
5. Recommendation (fix failures or proceed)
"""
)
```

---

## Output Examples

### Success Case
```
✅ **Test Runner**: All tests passed

📊 **Results**:
- Total: 139 tests
- Passed: 139 ✅
- Failed: 0
- Coverage: 85.3%
- Duration: 4.5s

✅ **Recommendation**: Proceed to next gate
```

### Failure Case
```
❌ **Test Runner**: 3 tests failed

📊 **Results**:
- Total: 139 tests
- Passed: 136 ✅
- Failed: 3 ❌
- Coverage: 82.1%
- Duration: 4.8s

❌ **Failed Tests**:
1. test_user_auth.py::test_login_invalid_password
2. test_api.py::test_rate_limiting
3. test_database.py::test_connection_retry

🔧 **Recommendation**: Fix failing tests before proceeding
```

---

## Performance Targets

- **Execution Time**: <5 minutes (full test suite)
- **Parsing Time**: <100ms
- **Memory Usage**: <200MB
- **Timeout**: 300 seconds (5 minutes)

---

## Error Handling

### Error: Test framework not found
```
❌ Error: No test framework detected
✅ Fix: Install pytest (pip install pytest) or configure package.json
```

### Error: Tests timeout
```
❌ Error: Tests exceeded 5 minute timeout
✅ Fix: Optimize slow tests or increase timeout
```

### Error: Import errors
```
❌ Error: ImportError in test files
✅ Fix: Check Python path, install dependencies
```

---

## Integration with Other Atomic Skills

**Before test-runner**:
- (none - usually runs first)

**After test-runner**:
- If passed → Continue to build-verifier
- If failed → Call minimal-reproduction-creator (if stuck)

---

## Version History

**1.0.0** (2025-10-17):
- Initial implementation
- Support for npm, pytest, playwright
- Coverage parsing
- Failed test extraction

---

**Last Updated**: 2025-10-17
**Status**: ✅ ACTIVE
**Used In**: 5 workflows
**Calls**: tester Drone
**Performance**: <5min execution
