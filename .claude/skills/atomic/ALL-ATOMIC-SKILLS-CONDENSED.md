# All 22 Atomic Skills (Condensed Reference)

**Purpose**: Quick reference for all reusable atomic skills
**Format**: Condensed for rapid implementation
**Version**: 1.0.0

---

## 1. test-runner ✅

**Trigger**: Before commit, deployment, completion gate
**Purpose**: Runs test suite, validates all pass
**Agent**: `tester` Drone
**Commands**: `npm test`, `pytest`, `npx playwright test`
**Output**: `{passed: bool, total: int, failed: int, coverage: float}`
**Used In**: 5 workflows

---

## 2. build-verifier

**Trigger**: Before deployment, completion gate
**Purpose**: Runs build command, checks success
**Agent**: `coder` Drone
**Commands**: `npm run build`, `npm run typecheck`
**Output**: `{success: bool, errors: [], bundle_size_kb: int}`
**Used In**: 4 workflows

---

## 3. type-checker

**Trigger**: Before commit, on TypeScript errors
**Purpose**: Runs TypeScript compiler, checks type errors
**Agent**: `code-analyzer` Drone
**Commands**: `npx tsc --noEmit`
**Output**: `{errors: int, error_list: [], fixed: bool}`
**Used In**: 3 workflows

---

## 4. linter

**Trigger**: Before commit, completion gate
**Purpose**: Runs linter, checks code style violations
**Agent**: `reviewer` Drone
**Commands**: `npm run lint`, `eslint --fix`
**Output**: `{errors: int, warnings: int, auto_fixed: int}`
**Used In**: 3 workflows

---

## 5. nasa-compliance-checker

**Trigger**: On Write/Edit, before commit
**Purpose**: Checks ≤60 LOC per function, type hints, no recursion
**Agent**: `nasa-enforcer` Drone
**Commands**: Python AST analysis script
**Output**: `{compliant: bool, violations: [{function, loc, issue}]}`
**Used In**: 4 workflows

---

## 6. debug-output-cleaner

**Trigger**: Before commit, completion gate
**Purpose**: Scans for console.log, print(), debug statements
**Agent**: `reviewer` Drone
**Commands**: `grep -r 'console.log' src/`, `grep -r 'print(' src/`
**Output**: `{found: int, locations: [], removed: int}`
**Used In**: 2 workflows

---

## 7. e2e-test-runner

**Trigger**: Before deployment
**Purpose**: Runs end-to-end Playwright/Cypress tests
**Agent**: `tester` Drone
**Commands**: `npx playwright test`, `npx cypress run`
**Output**: `{passed: int, failed: int, screenshots: []}`
**Used In**: 3 workflows

---

## 8. docstring-validator

**Trigger**: Before commit
**Purpose**: Checks functions have docstrings, complex logic documented
**Agent**: `docs-writer` Drone
**Commands**: Python AST check for docstrings
**Output**: `{missing_docstrings: int, functions: []}`
**Used In**: 2 workflows

---

## 9. style-matcher

**Trigger**: Before commit
**Purpose**: Checks code matches codebase style (reads 2-3 similar files)
**Agent**: `reviewer` Drone
**Commands**: AST comparison, style analysis
**Output**: `{matches: bool, inconsistencies: []}`
**Used In**: 2 workflows

---

## 10. theater-scanner

**Trigger**: Before deployment, completion gate
**Purpose**: Scans for TODO, FIXME, mock code, placeholders
**Agent**: `theater-detector` Drone
**Commands**: `grep -r 'TODO\|FIXME\|mock\|placeholder' src/`
**Output**: `{score: int, locations: [], severity: str}`
**Used In**: 2 workflows

---

## 11. git-status-checker

**Trigger**: Before commit
**Purpose**: Runs git status, checks only intended files changed
**Agent**: None (direct git)
**Commands**: `git status`, `git diff --name-only`
**Output**: `{changed_files: [], unintended: [], clean: bool}`
**Used In**: 3 workflows

---

## 12. commit-message-validator

**Trigger**: Before commit
**Purpose**: Checks commit message clarity, follows conventions
**Agent**: `reviewer` Drone
**Commands**: `git log -1 --format=%B`
**Output**: `{valid: bool, score: int, suggestions: []}`
**Used In**: 2 workflows

---

## 13. rollback-executor

**Trigger**: Production errors, error rate >5%
**Purpose**: Executes git revert, vercel rollback, restart services
**Agent**: `devops` + `infrastructure-ops` Drones
**Commands**: `git revert HEAD`, `vercel rollback`, `systemctl restart`
**Output**: `{reverted: bool, services_restarted: [], health: str}`
**Used In**: 3 workflows

---

## 14. security-scanner

**Trigger**: Before deployment
**Purpose**: Runs npm audit, pip check, scans for vulnerabilities
**Agent**: `security-manager` Drone
**Commands**: `npm audit`, `pip check`, `bandit`, `semgrep`
**Output**: `{vulnerabilities: int, critical: int, fixes: []}`
**Used In**: 4 workflows

---

## 15. secrets-detector

**Trigger**: Before commit, deployment
**Purpose**: Scans codebase for hardcoded secrets, API keys, passwords
**Agent**: `security-manager` Drone
**Commands**: `grep -r 'API_KEY\|SECRET\|PASSWORD' src/`, `git-secrets`
**Output**: `{secrets_found: int, locations: [], remediation: []}`
**Used In**: 3 workflows

---

## 16. performance-validator

**Trigger**: Before deployment
**Purpose**: Checks latency, response times, bundle size, performance targets
**Agent**: `performance-engineer` Drone
**Commands**: Lighthouse, bundle analyzer, latency tests
**Output**: `{targets_met: bool, metrics: {latency, bundle_size, score}}`
**Used In**: 3 workflows

---

## 17. cors-configurator

**Trigger**: Before deployment
**Purpose**: Validates CORS configuration, origin whitelist
**Agent**: `security-manager` Drone
**Commands**: Check CORS headers, validate origins
**Output**: `{valid: bool, origins: [], warnings: []}`
**Used In**: 2 workflows

---

## 18. minimal-reproduction-creator

**Trigger**: After 3 failed attempts, stuck situations
**Purpose**: Creates minimal test case, removes non-essential code
**Agent**: `debugger` Drone
**Commands**: Code stripping, isolation, minimal repro
**Output**: `{minimal_repro: str, isolated: bool, root_cause: str}`
**Used In**: 2 workflows

---

## 19. error-pattern-analyzer

**Trigger**: Same error 3+ times
**Purpose**: Analyzes repeated errors, categorizes by type, root cause
**Agent**: `debugger` + `code-analyzer` Drones
**Commands**: Error log analysis, pattern matching
**Output**: `{patterns: [], root_causes: [], suggested_fixes: []}`
**Used In**: 3 workflows

---

## 20. debug-logger-injector

**Trigger**: After 2 failed debug attempts
**Purpose**: Adds console.log, print() at key points for debugging
**Agent**: `debugger` Drone
**Commands**: AST injection of debug statements
**Output**: `{injected: int, locations: [], log_output: str}`
**Used In**: 2 workflows

---

## 21. environment-validator

**Trigger**: Before deployment
**Purpose**: Validates .env files, environment variables, secrets management
**Agent**: `devops` Drone
**Commands**: Check .env, validate required vars, check secrets
**Output**: `{valid: bool, missing_vars: [], secrets_in_code: bool}`
**Used In**: 3 workflows

---

## 22. health-check-monitor

**Trigger**: After deployment, on production errors
**Purpose**: Checks /health endpoint, services running, database connections
**Agent**: `infrastructure-ops` Drone
**Commands**: `curl /health`, `systemctl status`, DB connection test
**Output**: `{healthy: bool, services: [], failing: [], remediation: []}`
**Used In**: 3 workflows

---

## Usage Pattern (All Atomic Skills)

### Standard Call Format
```python
# From composite skill
result = await call_atomic_skill(
    skill_name="test-runner",
    context=project_context,
    options={}
)

if result["passed"]:
    continue_to_next_gate()
else:
    block_and_show_errors(result["errors"])
```

### Agent Spawn Pattern (All Atomic Skills)
```python
from src.coordination.agent_registry import find_drones_for_task

# Find appropriate drone
drones = find_drones_for_task(skill_description, loop="loop2")
drone = drones[0]

# Spawn via Task tool
Task(
    subagent_type=drone,
    description=f"Execute {skill_name}",
    prompt=f"You are {drone} Drone. {task_instructions}"
)
```

### Output Format (Standard for All)
```json
{
    "skill": "skill-name",
    "success": true/false,
    "data": { ... skill-specific results ... },
    "agent_used": "drone-name",
    "duration_ms": 1234,
    "recommendation": "Action to take next"
}
```

---

## Integration Matrix

| Atomic Skill | Used In # Workflows | Spawns Agent | Typical Duration |
|--------------|---------------------|--------------|------------------|
| test-runner | 5 | tester | 5-30s |
| build-verifier | 4 | coder | 10-60s |
| type-checker | 3 | code-analyzer | 5-15s |
| linter | 3 | reviewer | 3-10s |
| nasa-compliance-checker | 4 | nasa-enforcer | 2-5s |
| debug-output-cleaner | 2 | reviewer | 1-3s |
| e2e-test-runner | 3 | tester | 30-300s |
| docstring-validator | 2 | docs-writer | 2-5s |
| style-matcher | 2 | reviewer | 3-8s |
| theater-scanner | 2 | theater-detector | 2-5s |
| git-status-checker | 3 | none | 1s |
| commit-message-validator | 2 | reviewer | 1-2s |
| rollback-executor | 3 | devops + infra | 10-30s |
| security-scanner | 4 | security-manager | 10-60s |
| secrets-detector | 3 | security-manager | 5-15s |
| performance-validator | 3 | performance-engineer | 15-90s |
| cors-configurator | 2 | security-manager | 2-5s |
| minimal-reproduction-creator | 2 | debugger | 30-180s |
| error-pattern-analyzer | 3 | debugger + analyzer | 10-30s |
| debug-logger-injector | 2 | debugger | 5-15s |
| environment-validator | 3 | devops | 3-10s |
| health-check-monitor | 3 | infrastructure-ops | 5-15s |

---

## Next Steps

1. ✅ All 22 atomic skills documented
2. 📝 Create 15 composite skills (next)
3. 📝 Create integration tests
4. 📝 Validate cascade patterns

---

**Last Updated**: 2025-10-17
**Status**: ✅ All 22 Atomic Skills Documented
**Format**: Condensed reference (expandable on demand)
**Total Size**: ~8KB (vs ~300KB if all full-format)
