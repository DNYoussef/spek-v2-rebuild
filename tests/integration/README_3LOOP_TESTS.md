# 3-Loop System Integration Tests

## Overview

Comprehensive integration tests for the SPEK Platform 3-loop skills system, validating both development route (Loop 1→2→3→Production) and debug route (Loop 3→1→2→3→Production).

**File**: `tests/integration/test_3loop_system.py`

## Test Coverage

### Development Route Tests (5 tests)

Tests the normal development flow for new features:

1. **test_development_route_new_feature**
   - Validates complete Loop 1→2→3→Production workflow
   - Ensures all transitions occur correctly
   - Verifies final production state

2. **test_loop1_planning_outputs**
   - Validates Loop 1 creates all required deliverables:
     - Research document (`/research/*.md`)
     - Implementation plan (`/plans/*.md`)
     - Pre-mortem risk analysis (`/premortem/*.md`)
   - Verifies risk score calculation
   - Validates GO/NO-GO decision

3. **test_loop2_implementation_audits**
   - Validates Loop 2 runs all 3 audits:
     - Functionality audit (tests pass, ≥80% coverage)
     - Style audit (NASA Rule 10, linting)
     - Theater detection (no TODOs, mocks)
   - Ensures all audits pass before proceeding

4. **test_loop3_quality_gate**
   - Validates Loop 3 runs 47-point quality checklist
   - Calculates quality score (0.0-1.0)
   - Makes GO/NO-GO decision (≥0.95 required)
   - Approves deployment on GO

5. **test_memory_persistence_across_loops**
   - Validates memory state updates at each transition
   - Ensures data persists across loops
   - Verifies memory integrity throughout workflow

### Debug Route Tests (5 tests)

Tests the failure recovery flow when quality validation fails:

6. **test_debug_route_escalation**
   - Validates complete Loop 3→1→2→3→Production workflow
   - Simulates P0 security failure in Loop 3
   - Verifies escalation to Loop 1
   - Validates fix implementation in Loop 2
   - Confirms revalidation in Loop 3

7. **test_loop3_failure_detection**
   - Validates Loop 3 detects quality failures
   - Creates escalation context with:
     - Failure type
     - Severity (P0/P1/P2/P3)
     - Affected files
     - Quality scores
     - Recommendation
   - Triggers NO-GO decision

8. **test_loop1_replan_on_escalation**
   - Validates Loop 1 receives escalation context
   - Creates targeted fix plan (not full feature)
   - Analyzes regression risks
   - Makes GO decision for fix

9. **test_loop2_fix_implementation**
   - Validates Loop 2 applies targeted fix
   - Spawns appropriate agents (debugger, security-manager)
   - Runs audits with focus on regression
   - Ensures minimal changes (not full feature)

10. **test_loop3_revalidation**
    - Validates Loop 3 revalidates fix
    - Checks:
      - Original issue fixed
      - No new issues introduced
      - Regression tests pass
      - Security audit passes
    - Returns to development route on success

### Agent Integration Tests (3 tests)

Tests the agent registry and spawning system:

11. **test_agent_registry_integration**
    - Validates `find_drones_for_task()` function
    - Tests intelligent agent selection:
      - "Implement REST API" → backend-dev, coder
      - "Research OAuth2" → researcher
      - "Security audit" → security-manager
      - "Fix bug" → debugger

12. **test_princess_drone_spawning**
    - Validates Princess spawns correct Drones:
      - Princess-Dev → coder, tester, reviewer
      - Princess-Coordination → researcher, spec-writer, architect
      - Princess-Quality → theater-detector, nasa-enforcer, docs-writer

13. **test_queen_princess_delegation**
    - Validates Queen delegates to correct Princess:
      - Loop 1 → Princess-Coordination
      - Loop 2 → Princess-Dev
      - Loop 3 → Princess-Quality

### Flow Orchestrator Tests (3 tests)

Tests the Flow Orchestrator state machine:

14. **test_fsm_state_transitions**
    - Validates all state machine transitions:
      - IDLE → LOOP1_ACTIVE (user request)
      - LOOP1_ACTIVE → LOOP2_ACTIVE (Loop 1 complete)
      - LOOP2_ACTIVE → LOOP3_ACTIVE (Loop 2 complete)
      - LOOP3_ACTIVE → PRODUCTION (GO decision)
      - LOOP3_ACTIVE → ESCALATED (NO-GO decision)

15. **test_route_determination**
    - Validates user request routing:
      - "Build REST API" → Loop 1 (no plan)
      - "Implement auth API" → Loop 2 (plan exists)
      - "Fix bug" → Loop 2 (targeted fix)
      - "Deploy to production" → Loop 3

16. **test_escalation_count_limit**
    - Validates system enters FAILED state after 3 consecutive escalations
    - Prevents infinite debug loops
    - Requires manual intervention

## Running the Tests

### Run all 3-loop tests:
```bash
pytest tests/integration/test_3loop_system.py -v
```

### Run specific test class:
```bash
# Development route tests
pytest tests/integration/test_3loop_system.py::TestDevelopmentRoute -v

# Debug route tests
pytest tests/integration/test_3loop_system.py::TestDebugRoute -v

# Agent integration tests
pytest tests/integration/test_3loop_system.py::TestAgentIntegration -v

# Flow orchestrator tests
pytest tests/integration/test_3loop_system.py::TestFlowOrchestrator -v
```

### Run specific test:
```bash
pytest tests/integration/test_3loop_system.py::TestDevelopmentRoute::test_development_route_new_feature -v
```

## Test Results

**Status**: ✅ All 16 tests passing

**Execution Time**: ~20 seconds

**Test Characteristics**:
- Fast execution (mocked agents, no real implementation)
- Isolated (each test independent)
- Repeatable (deterministic results)
- Self-validating (clear pass/fail)

## Test Fixtures

### mock_memory
Mock memory system for testing loop states. Includes:
- Global state (current_loop, flow_route, escalation_count)
- Loop 1 state (feature_name, specs, plans, risks, risk_score, go_decision)
- Loop 2 state (files_changed, agents_spawned, audit_results)
- Loop 3 state (quality_score, decision, passed_checks, escalations)
- Production state (deployed_at)

### mock_fsm_state
Mock FSM state for testing state transitions. Includes:
- current_state (IDLE/LOOP1_ACTIVE/LOOP2_ACTIVE/LOOP3_ACTIVE/ESCALATED/PRODUCTION/FAILED)
- valid_states list
- transition_count

### mock_escalation_context
Mock escalation context for debug route testing. Includes:
- failure_type
- severity (P0/P1/P2/P3)
- affected_files
- quality_scores
- recommendation

## Test Quality Metrics

- **Coverage**: Tests validate all major workflows
- **Function Length**: All test functions ≤60 LOC (NASA Rule 10)
- **Assertions**: Clear, descriptive assertion messages
- **Documentation**: Comprehensive docstrings for all tests

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/3loop-tests.yml
name: 3-Loop Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run 3-loop tests
        run: pytest tests/integration/test_3loop_system.py -v
```

## Next Steps

1. Add E2E tests that spawn real agents (not mocked)
2. Add performance benchmarks for loop transitions
3. Add memory persistence tests (save/restore)
4. Add concurrency tests (multiple loops running)

---

**Version**: 1.0.0
**Created**: 2025-10-17
**Author**: Tester Drone
**Status**: Production-ready
