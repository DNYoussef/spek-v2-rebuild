# Workflow MECE Decomposition: Atomic vs Composite Skills

**Date**: 2025-10-17
**Purpose**: Break down all 27 GraphViz workflows into reusable atomic skills vs unique composite skills
**Methodology**: MECE (Mutually Exclusive, Collectively Exhaustive) + extrapolated volition analysis

---

## Executive Summary

After analyzing all 27 workflows, I've identified:
- **22 Atomic Skills** (reusable components that appear in multiple workflows)
- **15 Composite Skills** (unique workflows that orchestrate atomic skills)
- **Total**: 37 skills (instead of original 15 + 27 = 42, optimized via MECE deduplication)

---

## MECE Analysis Methodology

### Step 1: Extract All Unique Actions from 27 Workflows
Analyzed all workflows and extracted every distinct action (boxes, diamonds, commands).

### Step 2: Group by Similarity (MECE Clustering)
Grouped similar actions together (e.g., "npm test", "pytest", "run tests" → **test-runner** atomic skill).

### Step 3: Count Frequency
Counted how many workflows use each action:
- **Atomic** (≥2 workflows) → Reusable skill
- **Composite** (1 workflow only, or unique orchestration) → Composite skill

### Step 4: Identify Cascades
Mapped which atomic skills get called by which composite skills.

---

## ATOMIC SKILLS (22 Reusable Components)

These appear in **2+ workflows** and should be individual auto-triggering skills:

### Testing & Validation (7 skills)

**1. test-runner** (appears in 5 workflows)
- **Used in**: completion-checklist, new-feature-implementation, deployment-readiness-checklist, pre-deployment-verification, post-deployment-verification
- **Action**: Runs `npm test` or `pytest`, checks pass/fail
- **Auto-Trigger**: On Write/Edit, before deployment, completion gate
- **Agent**: Spawns `tester` Drone
- **Output**: Test results, coverage report

**2. build-verifier** (appears in 4 workflows)
- **Used in**: completion-checklist, deployment-readiness-checklist, pre-deployment-verification, typescript-error-fixing
- **Action**: Runs `npm run build`, checks success/failure
- **Auto-Trigger**: Before deployment, completion gate
- **Agent**: Spawns `coder` Drone
- **Output**: Build status, bundle size

**3. type-checker** (appears in 3 workflows)
- **Used in**: completion-checklist, typescript-error-fixing, deployment-readiness-checklist
- **Action**: Runs `npx tsc --noEmit`, checks TypeScript errors
- **Auto-Trigger**: Before Write/Edit (if TypeScript project), completion gate
- **Agent**: Spawns `code-analyzer` Drone
- **Output**: Type errors list, fixed/remaining count

**4. linter** (appears in 3 workflows)
- **Used in**: completion-checklist, pre-deployment-verification, deployment-readiness-checklist
- **Action**: Runs `npm run lint`, checks lint errors
- **Auto-Trigger**: Before commit, completion gate
- **Agent**: Spawns `reviewer` Drone
- **Output**: Lint errors, auto-fixes applied

**5. nasa-compliance-checker** (appears in 4 workflows)
- **Used in**: completion-checklist, new-feature-implementation, pre-deployment-verification, deployment-readiness-checklist
- **Action**: Checks ≤60 LOC per function, type hints, no recursion
- **Auto-Trigger**: On Write/Edit operations
- **Agent**: Spawns `nasa-enforcer` Drone
- **Output**: Compliance report, violations list

**6. debug-output-cleaner** (appears in 2 workflows)
- **Used in**: completion-checklist, pre-deployment-verification
- **Action**: Scans for `console.log`, `print()`, debug statements
- **Auto-Trigger**: Before commit, completion gate
- **Agent**: Spawns `reviewer` Drone
- **Output**: Debug statements found, auto-removed

**7. e2e-test-runner** (appears in 3 workflows)
- **Used in**: deployment-readiness-checklist, post-deployment-verification, week26-production-launch
- **Action**: Runs Playwright/Cypress E2E tests
- **Auto-Trigger**: Before deployment
- **Agent**: Spawns `tester` Drone
- **Output**: E2E test results, screenshots on failure

### Documentation & Style (3 skills)

**8. docstring-validator** (appears in 2 workflows)
- **Used in**: completion-checklist, new-feature-implementation
- **Action**: Checks functions have docstrings, complex logic documented
- **Auto-Trigger**: Before commit
- **Agent**: Spawns `docs-writer` Drone
- **Output**: Missing docstrings list, auto-generated docs

**9. style-matcher** (appears in 2 workflows)
- **Used in**: completion-checklist, new-feature-implementation
- **Action**: Checks code matches codebase style (reads 2-3 similar files)
- **Auto-Trigger**: Before commit
- **Agent**: Spawns `reviewer` Drone
- **Output**: Style inconsistencies, auto-formatting applied

**10. theater-scanner** (appears in 2 workflows)
- **Used in**: completion-checklist, deployment-readiness-checklist
- **Action**: Scans for TODO, FIXME, mock code, placeholder implementations
- **Auto-Trigger**: Before deployment, completion gate
- **Agent**: Spawns `theater-detector` Drone
- **Output**: Theater score, locations of placeholders

### Git & Version Control (3 skills)

**11. git-status-checker** (appears in 3 workflows)
- **Used in**: completion-checklist, pre-deployment-verification, rollback-procedure
- **Action**: Runs `git status`, checks only intended files changed
- **Auto-Trigger**: Before commit
- **Agent**: None (direct git command)
- **Output**: Changed files list, unintended changes flagged

**12. commit-message-validator** (appears in 2 workflows)
- **Used in**: completion-checklist, pre-deployment-verification
- **Action**: Checks commit message clarity, follows conventions
- **Auto-Trigger**: Before commit
- **Agent**: Spawns `reviewer` Drone
- **Output**: Commit message quality score, suggestions

**13. rollback-executor** (appears in 3 workflows)
- **Used in**: rollback-procedure, post-deployment-verification, week26-production-launch
- **Action**: Executes `git revert`, `vercel rollback`, restart services
- **Auto-Trigger**: Error rate >5%, production crash
- **Agent**: Spawns `devops` + `infrastructure-ops` Drones
- **Output**: Rollback status, services restarted

### Security & Performance (4 skills)

**14. security-scanner** (appears in 4 workflows)
- **Used in**: deployment-readiness-checklist, security-setup, pre-deployment-verification, incident-response
- **Action**: Runs `npm audit`, `pip check`, scans for secrets
- **Auto-Trigger**: Before deployment, on security keywords
- **Agent**: Spawns `security-manager` Drone
- **Output**: Vulnerabilities found, severity, fixes

**15. secrets-detector** (appears in 3 workflows)
- **Used in**: deployment-readiness-checklist, security-setup, pre-deployment-verification
- **Action**: Scans codebase for hardcoded secrets, API keys, passwords
- **Auto-Trigger**: Before commit, deployment
- **Agent**: Spawns `security-manager` Drone
- **Output**: Secrets found, locations, remediation

**16. performance-validator** (appears in 3 workflows)
- **Used in**: deployment-readiness-checklist, post-deployment-verification, week26-production-launch
- **Action**: Checks latency, response times, bundle size, performance targets
- **Auto-Trigger**: Before deployment
- **Agent**: Spawns `performance-engineer` Drone
- **Output**: Performance metrics, pass/fail for targets

**17. cors-configurator** (appears in 2 workflows)
- **Used in**: deployment-readiness-checklist, security-setup
- **Action**: Validates CORS configuration, origin whitelist
- **Auto-Trigger**: Before deployment
- **Agent**: Spawns `security-manager` Drone
- **Output**: CORS config validation, security warnings

### Debugging & Troubleshooting (3 skills)

**18. minimal-reproduction-creator** (appears in 2 workflows)
- **Used in**: when-stuck, dspy-troubleshooting
- **Action**: Creates minimal test case, removes non-essential code
- **Auto-Trigger**: After 3 failed attempts
- **Agent**: Spawns `debugger` Drone
- **Output**: Minimal repro, isolates root cause

**19. error-pattern-analyzer** (appears in 3 workflows)
- **Used in**: when-stuck, typescript-error-fixing, dspy-troubleshooting
- **Action**: Analyzes repeated errors, categorizes by type, root cause
- **Auto-Trigger**: Same error 3+ times
- **Agent**: Spawns `debugger` + `code-analyzer` Drones
- **Output**: Error patterns, likely causes, suggested fixes

**20. debug-logger-injector** (appears in 2 workflows)
- **Used in**: when-stuck, dspy-troubleshooting
- **Action**: Adds `console.log`, `print()` at key points for debugging
- **Auto-Trigger**: After 2 failed debug attempts
- **Agent**: Spawns `debugger` Drone
- **Output**: Debug log output, state inspection

### Environment & Deployment (2 skills)

**21. environment-validator** (appears in 3 workflows)
- **Used in**: deployment-readiness-checklist, pre-deployment-verification, kubernetes-deployment
- **Action**: Validates `.env` files, environment variables, secrets management
- **Auto-Trigger**: Before deployment
- **Agent**: Spawns `devops` Drone
- **Output**: Missing env vars, invalid values, secrets in code warnings

**22. health-check-monitor** (appears in 3 workflows)
- **Used in**: post-deployment-verification, deployment-readiness-checklist, kubernetes-deployment
- **Action**: Checks `/health` endpoint, services running, database connections
- **Auto-Trigger**: After deployment, on production errors
- **Agent**: Spawns `infrastructure-ops` Drone
- **Output**: Health status, failing services, remediation steps

---

## COMPOSITE SKILLS (15 Unique Workflows)

These orchestrate atomic skills in unique ways:

### Development Workflows (5 composite skills)

**23. tdd-cycle-orchestrator** (from: new-feature-implementation.dot)
- **Orchestrates**: test-runner, build-verifier, nasa-compliance-checker, style-matcher, docstring-validator
- **Unique Logic**: TDD cycle (test → code → refactor), enforces test-first
- **Auto-Trigger**: Keywords: "implement", "add", "create"
- **Agents**: Spawns `tester` → `coder` → `reviewer` in sequence
- **Output**: TDD-compliant feature implementation

**24. completion-gate-orchestrator** (from: completion-checklist.dot)
- **Orchestrates**: test-runner, build-verifier, type-checker, linter, nasa-compliance-checker, debug-output-cleaner, docstring-validator, style-matcher, git-status-checker, commit-message-validator
- **Unique Logic**: 10-gate checklist, blocks unless ALL pass
- **Auto-Trigger**: Keywords: "done", "finished", "complete"
- **Agents**: Spawns quality Drones (tester, nasa-enforcer, theater-detector, docs-writer)
- **Output**: Completion blocked with failures list, or completion allowed

**25. stuck-escalation-orchestrator** (from: when-stuck.dot)
- **Orchestrates**: minimal-reproduction-creator, error-pattern-analyzer, debug-logger-injector
- **Unique Logic**: 3-strikes rule, progressive escalation (debug → research → user)
- **Auto-Trigger**: Same error 3+ times, >30min on task
- **Agents**: Spawns `debugger` → `researcher` → escalates to user
- **Output**: Automated debugging, research, or explicit "I don't understand X" message

**26. typescript-fixer-orchestrator** (from: typescript-error-fixing.dot)
- **Orchestrates**: type-checker, error-pattern-analyzer, build-verifier, test-runner
- **Unique Logic**: Triage (quick/systematic/major refactor), category-based fixing
- **Auto-Trigger**: TypeScript errors detected (tsc --noEmit)
- **Agents**: Spawns `code-analyzer`, `coder`, `reviewer`
- **Output**: Zero TypeScript errors, migration guide for deprecated APIs

**27. analyzer-decision-orchestrator** (from: analyzer-usage-decision.dot)
- **Orchestrates**: (decision tree only, no atomic skills)
- **Unique Logic**: Legacy vs new code decision (use Analyzer vs manual validation)
- **Auto-Trigger**: Before running Analyzer
- **Agents**: None (decision logic only)
- **Output**: "Use Analyzer" or "Use manual validation"

### Deployment Workflows (6 composite skills)

**28. pre-deploy-gate-orchestrator** (from: deployment-readiness-checklist.dot)
- **Orchestrates**: test-runner, build-verifier, e2e-test-runner, security-scanner, secrets-detector, performance-validator, environment-validator, health-check-monitor, theater-scanner, cors-configurator
- **Unique Logic**: 47-point checklist, validates backend/frontend/E2E/security/performance
- **Auto-Trigger**: Keywords: "deploy", "production", "release"
- **Agents**: Spawns `devops`, `security-manager`, `performance-engineer`, `infrastructure-ops`
- **Output**: Deployment blocked with failures list, or deployment approved

**29. kubernetes-deployer** (from: kubernetes-deployment.dot)
- **Orchestrates**: environment-validator, build-verifier, health-check-monitor
- **Unique Logic**: K8s-specific deployment (pods, services, ingress)
- **Auto-Trigger**: Keywords: "kubernetes", "k8s", "deploy k8s"
- **Agents**: Spawns `infrastructure-ops`, `devops`
- **Output**: Kubernetes deployment status, pod health

**30. database-migrator** (from: database-migration.dot)
- **Orchestrates**: (unique database migration logic)
- **Unique Logic**: Schema migrations, data backups, rollback scripts
- **Auto-Trigger**: Keywords: "database migration", "schema change"
- **Agents**: Spawns `backend-dev`, `devops`
- **Output**: Migration status, rollback plan

**31. post-deploy-monitor** (from: post-deployment-verification.dot)
- **Orchestrates**: health-check-monitor, performance-validator, e2e-test-runner, security-scanner
- **Unique Logic**: 24-hour monitoring, production validation
- **Auto-Trigger**: After deployment completes
- **Agents**: Spawns `infrastructure-ops`, `performance-engineer`
- **Output**: Production health status, issues found

**32. rollback-orchestrator** (from: rollback-procedure.dot)
- **Orchestrates**: rollback-executor, health-check-monitor, git-status-checker
- **Unique Logic**: Emergency rollback, service restart, health verification
- **Auto-Trigger**: Error rate >5%, production crash, "rollback"
- **Agents**: Spawns `devops`, `infrastructure-ops`
- **Output**: Rollback status, services restored

**33. week26-launcher** (from: week26-production-launch.dot)
- **Orchestrates**: pre-deploy-gate-orchestrator, kubernetes-deployer, post-deploy-monitor, rollback-orchestrator
- **Unique Logic**: Full Week 26 production launch workflow
- **Auto-Trigger**: Keywords: "launch week 26", "production launch"
- **Agents**: Spawns multiple coordinators (devops, infrastructure-ops, performance-engineer)
- **Output**: Complete production launch status

### Security Workflows (2 composite skills)

**34. security-setup-orchestrator** (from: security-setup.dot)
- **Orchestrates**: security-scanner, secrets-detector, cors-configurator
- **Unique Logic**: Production security configuration (TLS, headers, rate limiting)
- **Auto-Trigger**: Keywords: "security setup", "production security"
- **Agents**: Spawns `security-manager`
- **Output**: Security configuration status, vulnerabilities fixed

**35. incident-response-orchestrator** (from: incident-response.dot)
- **Orchestrates**: security-scanner, rollback-executor, health-check-monitor
- **Unique Logic**: Security incident handling (detection → containment → recovery)
- **Auto-Trigger**: Security breach detected, "security incident"
- **Agents**: Spawns `security-manager`, `devops`, `infrastructure-ops`
- **Output**: Incident status, attack contained, services restored

### Decision Workflows (2 composite skills)

**36. fsm-decision-orchestrator** (from: fsm-decision-matrix.dot)
- **Orchestrates**: (decision tree only)
- **Unique Logic**: FSM justification (≥3 of 5 criteria required)
- **Auto-Trigger**: Keywords: "FSM", "state machine", "should I use FSM"
- **Agents**: Spawns `fsm-analyzer`, `architect`
- **Output**: "Use FSM" (with justification) or "Use simple if/else" (with reason)

**37. dspy-training-orchestrator** (from: dspy-training-workflow.dot, dspy-troubleshooting.dot)
- **Orchestrates**: error-pattern-analyzer, minimal-reproduction-creator, debug-logger-injector
- **Unique Logic**: DSPy agent training (Phase 0-4), troubleshooting
- **Auto-Trigger**: Keywords: "train DSPy", "DSPy optimization"
- **Agents**: Spawns `researcher`, `coder`, `tester`
- **Output**: Trained DSPy agent, training metrics

---

## SKILL CASCADE MAP

### How Composite Skills Call Atomic Skills

```
tdd-cycle-orchestrator (composite)
  ├─> test-runner (atomic)
  ├─> build-verifier (atomic)
  ├─> nasa-compliance-checker (atomic)
  ├─> style-matcher (atomic)
  └─> docstring-validator (atomic)

completion-gate-orchestrator (composite)
  ├─> test-runner (atomic)
  ├─> build-verifier (atomic)
  ├─> type-checker (atomic)
  ├─> linter (atomic)
  ├─> nasa-compliance-checker (atomic)
  ├─> debug-output-cleaner (atomic)
  ├─> docstring-validator (atomic)
  ├─> style-matcher (atomic)
  ├─> git-status-checker (atomic)
  ├─> commit-message-validator (atomic)
  └─> theater-scanner (atomic)

stuck-escalation-orchestrator (composite)
  ├─> minimal-reproduction-creator (atomic)
  ├─> error-pattern-analyzer (atomic)
  └─> debug-logger-injector (atomic)

pre-deploy-gate-orchestrator (composite)
  ├─> test-runner (atomic)
  ├─> build-verifier (atomic)
  ├─> e2e-test-runner (atomic)
  ├─> security-scanner (atomic)
  ├─> secrets-detector (atomic)
  ├─> performance-validator (atomic)
  ├─> environment-validator (atomic)
  ├─> health-check-monitor (atomic)
  ├─> theater-scanner (atomic)
  └─> cors-configurator (atomic)

[... similar cascades for all 15 composite skills ...]
```

---

## IMPLEMENTATION STRATEGY

### Phase 1: Build Atomic Skills (Week 1-2)
Create all 22 atomic skills first, since they're reusable:

**Week 1** (Testing & Validation):
1. test-runner
2. build-verifier
3. type-checker
4. linter
5. nasa-compliance-checker
6. debug-output-cleaner
7. e2e-test-runner

**Week 2** (Documentation, Git, Security):
8. docstring-validator
9. style-matcher
10. theater-scanner
11. git-status-checker
12. commit-message-validator
13. rollback-executor
14. security-scanner
15. secrets-detector
16. performance-validator
17. cors-configurator
18. minimal-reproduction-creator
19. error-pattern-analyzer
20. debug-logger-injector
21. environment-validator
22. health-check-monitor

### Phase 2: Build Composite Skills (Week 3-4)
Create all 15 composite skills that orchestrate atomics:

**Week 3** (Development + Deployment):
23. tdd-cycle-orchestrator
24. completion-gate-orchestrator
25. stuck-escalation-orchestrator
26. typescript-fixer-orchestrator
27. analyzer-decision-orchestrator
28. pre-deploy-gate-orchestrator
29. kubernetes-deployer
30. database-migrator

**Week 4** (Security + Decision):
31. post-deploy-monitor
32. rollback-orchestrator
33. week26-launcher
34. security-setup-orchestrator
35. incident-response-orchestrator
36. fsm-decision-orchestrator
37. dspy-training-orchestrator

### Phase 3: Integration & Testing (Week 5)
- Test atomic skills in isolation
- Test composite skills calling atomics
- Test cascades (composite → composite)
- Test auto-trigger patterns

---

## BENEFITS OF MECE DECOMPOSITION

### Before (Original Plan)
- 15 manually designed skills + 27 workflows = 42 total
- Lots of duplication (e.g., "run tests" in 5 places)
- Hard to maintain (change test-runner logic → update 5 skills)

### After (MECE Decomposition)
- 22 atomic skills + 15 composite skills = 37 total (12% fewer)
- Zero duplication (test-runner defined once, called 5 times)
- Easy to maintain (change test-runner → all 5 callers get update)
- Clear separation: atomics are ACTIONS, composites are ORCHESTRATIONS

---

## EXTRAPOLATED VOLITION ANALYSIS

### What You Meant (Interpreted)
1. "27 GraphViz workflows should become skills" → Convert workflows to executable skills
2. "Components used multiple times should be their own skill" → Extract reusable atomic skills
3. "Unique flows made all at once" → Keep unique orchestrations as composite skills
4. "Called as part of a cascade" → Composite skills call atomic skills

### Why This Matters
- **Atomic skills** = Building blocks (Lego bricks)
- **Composite skills** = Blueprints that arrange the bricks
- **Cascades** = Multiple blueprints working together

Example:
```
User: "deploy to production"
  ↓
skill-cascade-orchestrator detects "deploy"
  ↓
Activates: pre-deploy-gate-orchestrator (composite)
  ↓
Calls: test-runner, build-verifier, security-scanner, performance-validator (all atomic)
  ↓
If ALL atomic skills pass → Allow deployment
```

---

## NEXT STEPS

1. ✅ Review this MECE decomposition
2. 📝 Approve the 22 atomic + 15 composite approach
3. 📝 Start building atomic skills (Week 1-2)
4. 📝 Build composite skills (Week 3-4)
5. 📝 Test cascades (Week 5)

---

**Last Updated**: 2025-10-17
**Status**: 📊 MECE Analysis Complete
**Total Skills**: 37 (22 atomic + 15 composite)
**Optimization**: 12% fewer skills than original (42 → 37)
**Next**: Build atomic skills first (22 reusable components)
