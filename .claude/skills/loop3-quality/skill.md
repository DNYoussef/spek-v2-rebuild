# Loop 3: Quality & Integration Testing

## Overview

Loop 3 is the SPEK Platform's quality validation and integration testing phase that runs comprehensive audits, performs rewrites based on findings, and validates production readiness. This skill uses existing audit skills (functionality-audit, style-audit, theater-detection-audit), spawns quality-focused agents, and makes the critical GO/NO-GO deployment decision. If quality validation fails, Loop 3 escalates to Loop 1 for replanning, creating the debug route.

This skill represents the third phase of the 3-loop methodology: **Loop 1 (Planning) → Loop 2 (Implementation) → Loop 3 (Quality) → Production**. It also initiates the debug route when failures are detected: **Loop 3 (Failed) → Loop 1 (Replan) → Loop 2 (Fix) → Loop 3 (Revalidate)**.

## When to Use This Skill

Activate Loop 3 when:
- **Loop 2 complete**: Implementation finished, code exists, Loop 2 audits passed
- **Integration testing needed**: Multiple components merged, need E2E validation
- **Pre-deployment gate**: User requests deployment, need production readiness check
- **Quality validation requests**: User says "test", "audit", "review", "validate"

**Auto-Trigger Patterns**:
- Keywords: "test", "audit", "review", "validate", "quality", "deploy", "release", "integrate"
- Phrases: "Is this ready for production?", "Run full tests", "Deploy to staging", "Release v1.0"
- Memory signal: `memory["current_loop"] == "loop3"` (Loop 2 completed)
- User deployment request: "deploy to production", "push to staging"

## Loop 3 Workflow Phases

Loop 3 runs a comprehensive 47-point quality gate system with audit, rewrite, and escalation capabilities:

### Phase 1: Context Loading & Route Detection

**Actions**:
1. Verify Loop 2 completion: Check `memory["loop2"]["status"] == "complete"`
2. Load Loop 2 context:
   ```python
   loop2 = memory["loop2"]
   files_changed = loop2["files_changed"]
   agents_used = loop2["agents_spawned"]
   loop2_audits = loop2["audit_results"]  # Already passed in Loop 2
   route = loop2["route"]  # development or debug
   ```
3. Determine if this is revalidation (debug route) or first validation (development route)
4. Set Loop 3 status to "in_progress"
5. Initialize quality gate checklist (47 points)

**Debug Route Detection**:
```python
if route == "debug":
    # This is revalidation after Loop 1 → Loop 2 fix
    original_failure = memory["loop3"]["escalations"][-1]
    print(f"Revalidating fix for: {original_failure['failure_type']}")
    # Extra focus on regression testing
```

### Phase 2: Princess-Quality Coordination

**Use princess-summoning skill** to spawn Princess-Quality:

The princess-summoning skill handles Princess selection for Loop 3. Princess-Quality will coordinate all quality validation work using the drone-selection skill to spawn appropriate quality Drones.

```markdown
# Invoke princess-summoning skill
Use princess-summoning skill:
- Loop: loop3
- Task: {feature_name} quality validation
- Princess: princess-quality (automatically selected for loop3)
- Context: Loop 2 outputs (code changes, audit results, files modified)

Princess-Quality will then:
1. Use drone-selection skill to find quality Drones
2. Spawn theater-detector, nasa-enforcer, docs-writer, code-analyzer, security-manager
3. Run comprehensive 47-point quality gate
4. Make GO/NO-GO deployment decision
5. Escalate to Loop 1 if critical failures detected
```

### Phase 3: Comprehensive Audit Suite

Loop 3 runs 3 primary audits using existing skills + Princess-Quality agent coordination:

#### Audit 1: Functionality Audit (Enhanced)

**Use existing `functionality-audit` skill**:
```
Skill(command="functionality-audit")
```

**Alternative: Princess-Quality spawns integration-engineer Drone**:
```python
# Spawn integration-engineer for E2E tests
Task(
    subagent_type="integration-engineer",
    description="Run E2E integration tests",
    prompt=f"""You are the Integration Engineer Drone.

TASK: Run comprehensive E2E integration tests

FILES CHANGED (from Loop 2):
{files_changed}

TEST REQUIREMENTS:
1. Run full E2E test suite (Playwright/Cypress)
2. Test happy paths
3. Test error paths
4. Test edge cases
5. Test integration between components
6. Measure performance (response times, memory)

DELIVERABLES:
- E2E test results (pass/fail)
- Performance metrics
- Integration report
- Screenshots/videos of failures (if any)

PASS CRITERIA:
- 100% E2E tests passing
- Response times <200ms (95th percentile)
- No memory leaks detected
- No console errors

TIME BUDGET: 20 minutes

Report results."""
)
```

**Functionality Audit Checklist** (15 points):
1. ✅ Unit tests: 100% passing
2. ✅ Integration tests: 100% passing
3. ✅ E2E tests: 100% passing
4. ✅ Code coverage: ≥80% (≥90% for critical paths)
5. ✅ Performance: Response times within targets
6. ✅ Memory: No leaks detected
7. ✅ Error handling: All error paths tested
8. ✅ Edge cases: Boundary conditions validated
9. ✅ Regression: No new test failures
10. ✅ Build: Production build successful
11. ✅ Dependencies: All installed correctly
12. ✅ Database migrations: Applied successfully (if applicable)
13. ✅ API contracts: All endpoints validated
14. ✅ WebSocket events: All handlers tested (if applicable)
15. ✅ Console: No errors in browser/server logs

#### Audit 2: Style Audit (Enhanced)

**Use existing `style-audit` skill**:
```
Skill(command="style-audit")
```

**Additional Style Checks**:
```python
# Spawn code-analyzer for deep inspection
Task(
    subagent_type="code-analyzer",
    description="Static code analysis",
    prompt=f"""You are the Code Analyzer Drone.

TASK: Perform static code analysis

FILES CHANGED:
{files_changed}

ANALYSIS REQUIREMENTS:
1. NASA Rule 10 compliance (≤60 LOC per function)
2. Type hints/TypeScript strict mode
3. Cyclomatic complexity (<10 per function)
4. Code duplication detection
5. Unused imports/variables
6. Security vulnerabilities (Bandit/Semgrep)
7. Best practices adherence

DELIVERABLES:
- Compliance report (NASA Rule 10)
- Complexity metrics
- Security scan results
- Refactoring recommendations

PASS CRITERIA:
- ≥96% NASA compliance
- Complexity <10 for all functions
- Zero critical security issues
- Zero high-priority linter warnings

TIME BUDGET: 15 minutes

Report results."""
)
```

**Style Audit Checklist** (16 points):
1. ✅ NASA compliance: ≥96% (≤60 LOC per function)
2. ✅ Type hints: 100% coverage (Python) or TypeScript strict
3. ✅ Linting: Zero errors (ESLint/Pylint)
4. ✅ Formatting: Prettier/Black auto-formatted
5. ✅ Naming: Descriptive variable/function names
6. ✅ Comments: Docstrings for all public functions
7. ✅ Complexity: Cyclomatic complexity <10
8. ✅ Duplication: No copy-paste code detected
9. ✅ Imports: No unused imports
10. ✅ Variables: No unused variables
11. ✅ Recursion: None detected (NASA Rule 10)
12. ✅ Loop bounds: All loops have fixed bounds
13. ✅ Security: Zero critical vulnerabilities
14. ✅ Dependencies: No known CVEs
15. ✅ File organization: Proper directory structure
16. ✅ Code smell: No anti-patterns detected

#### Audit 3: Theater Detection Audit (Enhanced)

**Use existing `theater-detection-audit` skill**:
```
Skill(command="theater-detection-audit")
```

**Additional Theater Checks**:
```python
# Spawn theater-detector agent
Task(
    subagent_type="theater-detector",
    description="Deep theater scan",
    prompt=f"""You are the Theater Detector Drone.

TASK: Scan for placeholder/mock code

FILES CHANGED:
{files_changed}

SCAN REQUIREMENTS:
1. TODO/FIXME comments
2. Mock data (mock_, fake_, dummy_)
3. Placeholder implementations
4. Commented-out code
5. Console.log/print debug statements
6. Hardcoded test data
7. Incomplete error handling (bare except, empty catch)

DELIVERABLES:
- Theater score (0-100, lower is better)
- List of all issues found
- Severity (P0/P1/P2) for each issue

PASS CRITERIA:
- Theater score <60
- Zero P0 issues (critical placeholders)
- Zero TODO/FIXME comments
- No mock/fake data in production code

TIME BUDGET: 10 minutes

Report results."""
)
```

**Theater Audit Checklist** (10 points):
1. ✅ TODO comments: Zero found
2. ✅ FIXME comments: Zero found
3. ✅ HACK comments: Zero found
4. ✅ Mock data: None in production code
5. ✅ Fake data: None in production code
6. ✅ Placeholder functions: None (all implemented)
7. ✅ Commented code: None (deleted or uncommented)
8. ✅ Debug statements: Removed (console.log, print)
9. ✅ Hardcoded values: None (use config/env vars)
10. ✅ Theater score: <60

### Phase 3: Integration & Performance Validation

**Additional Quality Checks** (6 points):

```python
# Spawn performance-engineer
Task(
    subagent_type="performance-engineer",
    description="Performance benchmarking",
    prompt=f"""You are the Performance Engineer Drone.

TASK: Benchmark performance and identify bottlenecks

FILES CHANGED:
{files_changed}

BENCHMARKING:
1. Response time: 95th percentile <200ms
2. Memory usage: <500MB steady state
3. CPU usage: <70% under load
4. Database queries: <50ms average
5. Bundle size: Frontend <5MB (post-gzip)
6. Lighthouse score: >90 (if web app)

DELIVERABLES:
- Performance report
- Bottleneck analysis
- Optimization recommendations
- Before/after metrics (vs Loop 2 baseline)

PASS CRITERIA:
- All performance targets met
- No P0 bottlenecks detected
- Lighthouse score >90

TIME BUDGET: 15 minutes

Report results."""
)
```

**Integration Checklist** (6 points):
1. ✅ Performance: All targets met
2. ✅ Database: Queries optimized
3. ✅ API: Endpoints respond quickly
4. ✅ Frontend: Bundle size within limits
5. ✅ Dependencies: No version conflicts
6. ✅ Environment: Env vars validated

### Phase 4: Security & Compliance Validation

```python
# Spawn security-manager
Task(
    subagent_type="security-manager",
    description="Security audit",
    prompt=f"""You are the Security Manager Drone.

TASK: Perform comprehensive security audit

FILES CHANGED:
{files_changed}

SECURITY AUDIT:
1. Authentication: Properly implemented
2. Authorization: Correct permissions checked
3. Input validation: All inputs sanitized
4. SQL injection: None detected (use parameterized queries)
5. XSS: None detected (proper escaping)
6. CSRF: Protection enabled
7. Secrets: None hardcoded (use env vars)
8. Dependencies: No known CVEs
9. HTTPS: Enforced (no HTTP in production)
10. Rate limiting: Implemented (if API)

DELIVERABLES:
- Security report
- Vulnerability list (P0/P1/P2)
- Compliance checklist
- Remediation recommendations

PASS CRITERIA:
- Zero P0 vulnerabilities
- Zero P1 vulnerabilities
- All secrets in env vars
- HTTPS enforced

TIME BUDGET: 20 minutes

Report results."""
)
```

**Security Checklist** (10 points):
1. ✅ Authentication: Secure implementation
2. ✅ Authorization: Proper access control
3. ✅ Input validation: All inputs sanitized
4. ✅ SQL injection: None detected
5. ✅ XSS: None detected
6. ✅ CSRF: Protection enabled
7. ✅ Secrets: None hardcoded
8. ✅ Dependencies: No CVEs
9. ✅ HTTPS: Enforced
10. ✅ Rate limiting: Implemented (if needed)

### Phase 5: Rewrite Coordination (If Audits Fail)

**If ANY audit fails**, Loop 3 coordinates rewrites before re-auditing.

**Rewrite Workflow**:
```python
# Analyze failure
failures = collect_audit_failures()

if len(failures) > 0:
    # Categorize by severity
    p0_failures = [f for f in failures if f["severity"] == "P0"]
    p1_failures = [f for f in failures if f["severity"] == "P1"]

    if len(p0_failures) > 0:
        # Critical failures → Escalate to Loop 1
        escalate_to_loop1(p0_failures)
    else:
        # Non-critical → Coordinate rewrites
        coordinate_rewrites(p1_failures)
```

**Rewrite Coordination**:
```python
Task(
    subagent_type="princess-quality",
    description="Coordinate quality rewrites",
    prompt=f"""You are Princess-Quality, the Quality Coordinator.

TASK: Coordinate rewrites to address audit failures

FAILURES:
{format_failures(failures)}

YOUR RESPONSIBILITIES:
1. Analyze each failure
2. Spawn appropriate Drones to fix:
   - Functionality failures → debugger, tester
   - Style failures → reviewer, code-analyzer
   - Theater failures → coder (complete work)
   - Security failures → security-manager
   - Performance failures → performance-engineer
3. Coordinate fixes across multiple files
4. Rerun audits after fixes
5. Escalate to Queen if 3 rewrite attempts fail

DELIVERABLES:
- Fixed code
- Updated audit results
- Fix summary

Begin rewrite coordination."""
)
```

**Rewrite Agents** (from `agent_registry.py`):
- `debugger`: Fix functionality issues
- `reviewer`: Fix style issues
- `coder`: Complete placeholder work (theater)
- `security-manager`: Fix security vulnerabilities
- `performance-engineer`: Optimize performance bottlenecks

### Phase 6: Final Quality Gate (47-Point Checklist)

**All 47 points must pass for GO decision**:

**Backend (8 points)**:
1. ✅ Unit tests passing
2. ✅ Integration tests passing
3. ✅ API endpoints validated
4. ✅ Database migrations applied
5. ✅ Error handling complete
6. ✅ Logging configured
7. ✅ Environment variables set
8. ✅ Dependencies installed

**Frontend (6 points)**:
9. ✅ Build successful
10. ✅ Bundle size within limits
11. ✅ E2E tests passing
12. ✅ No console errors
13. ✅ TypeScript strict mode
14. ✅ Lighthouse score >90

**E2E & Integration (7 points)**:
15. ✅ Happy path tests passing
16. ✅ Error path tests passing
17. ✅ Edge case tests passing
18. ✅ Integration tests passing
19. ✅ WebSocket tests passing (if applicable)
20. ✅ Performance tests passing
21. ✅ Regression tests passing

**Environment (3 points)**:
22. ✅ .env file exists
23. ✅ All required env vars present
24. ✅ Secrets not hardcoded

**Performance (4 points)**:
25. ✅ Response times <200ms
26. ✅ Memory usage acceptable
27. ✅ CPU usage acceptable
28. ✅ No memory leaks

**Security (7 points)**:
29. ✅ Authentication secure
30. ✅ Authorization correct
31. ✅ Input validation complete
32. ✅ No SQL injection
33. ✅ No XSS vulnerabilities
34. ✅ CSRF protection enabled
35. ✅ HTTPS enforced

**Quality (6 points)**:
36. ✅ NASA compliance ≥96%
37. ✅ Code coverage ≥80%
38. ✅ Linting passing
39. ✅ Type hints complete
40. ✅ Complexity <10
41. ✅ No code duplication

**Final Checks (6 points)**:
42. ✅ Theater score <60
43. ✅ No TODO/FIXME comments
44. ✅ No mock/fake data
45. ✅ Documentation complete
46. ✅ Changelog updated
47. ✅ Deployment artifacts ready

**Scoring**:
```python
total_points = 47
passed_points = count_passed_checks()
quality_score = passed_points / total_points

if quality_score == 1.0:
    decision = "GO"  # Production ready
elif quality_score >= 0.95:
    decision = "CAUTION"  # Minor issues, acceptable
else:
    decision = "NO-GO"  # Needs work
```

### Phase 7: GO/NO-GO Decision

**Decision Matrix**:

```python
if quality_score == 1.0:
    # 47/47 points passed
    decision = "GO"
    action = "approve_deployment"

elif quality_score >= 0.95:
    # 45-46/47 points passed
    decision = "CAUTION"
    action = "warn_user_and_approve"
    warnings = list_failed_checks()

else:
    # <45/47 points passed
    decision = "NO-GO"
    action = "escalate_or_rewrite"

    if has_critical_failures():
        # P0 failures (security, data loss, etc.)
        escalate_to_loop1("Critical quality failures")
    else:
        # P1/P2 failures
        coordinate_rewrites(failures)
        rerun_loop3()
```

**GO Decision**:
```python
# All checks passed, ready for production
memory["loop3"] = {
    "feature_name": feature_name,
    "quality_score": 1.0,
    "decision": "GO",
    "passed_checks": 47,
    "total_checks": 47,
    "integration_tests": "pass",
    "e2e_tests": "pass",
    "security_audit": "pass",
    "performance_audit": "pass",
    "deployment_approved": True,
    "status": "complete",
    "completed_at": timestamp
}

memory["current_loop"] = "production"  # Final state

# Spawn deployment agent
Task(
    subagent_type="devops",
    description="Deploy to production",
    prompt=f"""Deploy to production.

QUALITY SCORE: {quality_score} (47/47)
DECISION: GO

Proceed with deployment per deployment plan."""
)
```

**CAUTION Decision**:
```python
# Minor issues, user decision required
warnings = ["Bundle size 5.1MB (target: 5MB)", "1 P2 performance issue"]

warn_user(f"""
⚠️  CAUTION: Minor issues detected

Quality Score: {quality_score} (46/47)
Failed Checks: {format_failed_checks(warnings)}

These are non-critical issues. Proceed with deployment?
[Y] Deploy anyway
[N] Fix issues first
""")
```

**NO-GO Decision**:
```python
# Critical failures, escalate to Loop 1
if has_critical_failures():
    escalate_to_loop1({
        "failure_type": "security_vulnerability",
        "severity": "P0",
        "affected_files": [...],
        "error_logs": [...],
        "quality_scores": {
            "functionality": 0.85,
            "style": 0.92,
            "theater": 0.98,
            "security": 0.32  # FAILED
        },
        "recommendation": "Replan authentication strategy"
    })
else:
    # Non-critical, coordinate rewrites
    coordinate_rewrites(failures)
```

### Phase 8: Escalation to Loop 1 (Debug Route Initiation)

**When to Escalate**:
- P0 failures (security, data corruption, fundamental design flaws)
- 3 consecutive rewrite attempts failed
- Quality score <0.80 (multiple severe issues)

**Escalation Workflow**:
```python
# Step 1: Document failure
escalation = {
    "timestamp": now(),
    "failure_type": "security_vulnerability",
    "severity": "P0",
    "affected_files": ["src/auth.py", "src/tokens.py"],
    "error_logs": ["SQL injection risk in line 42"],
    "quality_scores": {
        "functionality": 0.85,
        "style": 0.92,
        "theater": 0.98,
        "security": 0.32
    },
    "recommendation": "Replan authentication strategy, research parameterized queries",
    "failed_checks": [29, 32],  # Checklist items
    "root_cause_analysis": "Concatenating SQL queries instead of using ORM"
}

# Step 2: Store in memory
memory["loop3"]["escalations"].append(escalation)
memory["loop3"]["status"] = "escalated"

# Step 3: Transition to Loop 1
memory["current_loop"] = "loop1"
memory["flow_route"] = "debug"

# Step 4: Activate Loop 1 with escalation context
Task(
    subagent_type="general-purpose",
    description="Escalate to Loop 1",
    prompt=f"""ESCALATION: Loop 3 → Loop 1

FAILURE: {escalation['failure_type']}
SEVERITY: {escalation['severity']}

Loop 1 will now:
1. Research root cause
2. Create fix plan
3. Update pre-mortem (regression risks)
4. Transition to Loop 2 for fix implementation

ESCALATION CONTEXT:
{json.dumps(escalation, indent=2)}

Activating Loop 1 (Planning) in debug mode."""
)
```

**User Notification**:
```
❌ Loop 3 Quality Validation FAILED

🚨 Critical Issue Detected:
- Type: {failure_type}
- Severity: P0 (project-blocking)
- Quality Score: {quality_score} (target: 1.0)

📋 Failed Checks:
{format_failed_checks(failed_checks)}

🔄 Debug Route Initiated:
Loop 3 → Loop 1 (Replan) → Loop 2 (Fix) → Loop 3 (Revalidate)

Loop 1 will research root cause and create fix plan.
```

## Agent Registry Integration

Loop 3 uses these agents from `agent_registry.py`:

**Princess**:
- `princess-quality`: Quality coordinator (primary for Loop 3)

**Drones** (10 quality-focused):
- `tester`: Additional test creation
- `reviewer`: Code review and refactoring
- `integration-engineer`: E2E testing
- `code-analyzer`: Static analysis
- `security-manager`: Security audits
- `performance-engineer`: Performance optimization
- `theater-detector`: Placeholder detection
- `nasa-enforcer`: NASA Rule 10 compliance
- `docs-writer`: Documentation validation
- `devops`: Deployment preparation

**Selection Example**:
```python
# Princess-Quality selects Drones based on audit failures
failures = ["security_vulnerability", "performance_bottleneck"]

for failure in failures:
    drones = find_drones_for_task(f"fix {failure}", "loop3")
    # Returns appropriate specialists
```

## Memory Integration

Loop 3 reads from Loop 2 and writes final results:

**Read from Loop 2**:
```python
loop2 = memory["loop2"]
files_changed = loop2["files_changed"]
loop2_audits = loop2["audit_results"]
```

**Write Final Results**:
```python
memory["loop3"] = {
    "feature_name": "user-authentication",
    "quality_score": 1.0,
    "decision": "GO",
    "passed_checks": 47,
    "total_checks": 47,
    "audits": {
        "functionality": "pass",
        "style": "pass",
        "theater": "pass",
        "security": "pass",
        "performance": "pass",
        "integration": "pass"
    },
    "deployment_approved": True,
    "status": "complete"
}
```

**If Escalation**:
```python
memory["loop3"]["escalations"].append({...})
memory["current_loop"] = "loop1"  # Debug route
memory["flow_route"] = "debug"
```

## Success Criteria

Loop 3 is considered successful when:
- ✅ All 47 quality gate checks passed
- ✅ Quality score 1.0 (47/47)
- ✅ All audits passing (functionality, style, theater, security, performance, integration)
- ✅ GO decision approved
- ✅ Deployment approved
- ✅ User notified
- ✅ Production transition initiated

**Quality Bar**:
- 47/47 points for GO
- 45-46/47 points for CAUTION (user decision)
- <45/47 points for NO-GO (rewrite or escalate)

## Integration with Flow Orchestrator

Loop 3 completes the 3-loop cycle or initiates debug route:

**Development Route (Success)**:
```
Loop 1 → Loop 2 → Loop 3 (GO) → Production
```

**Debug Route (Failure)**:
```
Loop 3 (NO-GO) → Loop 1 (Replan) → Loop 2 (Fix) → Loop 3 (Revalidate)
```

The Flow Orchestrator skill manages routing based on:
- Loop 3 decision (GO/NO-GO)
- Escalation signals
- Memory state

See `flow-orchestrator` skill for complete routing logic.

## Helper Scripts & Resources

Loop 3 includes bundled resources:

**Scripts** (`.claude/skills/loop3-quality/scripts/`):
- `quality_gate.py`: 47-point checklist validator
- `integration_tester.py`: E2E test orchestration
- `rewrite_coordinator.py`: Coordinates rewrites based on failures
- `deployment_approver.py`: Final deployment gate
- `escalation_manager.py`: Manages Loop 1 escalations

**Diagrams** (`.claude/skills/loop3-quality/diagrams/`):
- `loop3-quality-process.dot`: Visual workflow
- `47-point-checklist.dot`: Quality gate diagram

**Templates** (`.claude/skills/loop3-quality/templates/`):
- `quality_report_template.md`: Quality report structure
- `escalation_template.json`: Escalation format

**Usage Example**:
```python
from scripts.quality_gate import run_quality_gate

result = run_quality_gate(project_root=".")

if result["decision"] == "GO":
    approve_deployment()
elif result["decision"] == "CAUTION":
    warn_user_and_approve()
else:
    escalate_to_loop1(result["failures"])
```

---

**Version**: 1.1.0
**Last Updated**: 2025-10-18
**Part of**: SPEK Platform 3-Loop Methodology
**Related Skills**: `princess-summoning`, `drone-selection`, `loop1-planning`, `loop2-implementation`, `functionality-audit`, `style-audit`, `theater-detection-audit`, `flow-orchestrator`
