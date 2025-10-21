# Skill Cascade Orchestrator (Meta-Skill)

**Skill ID**: `skill-cascade-orchestrator`
**Version**: 1.0.0
**Priority**: P0 (CRITICAL - Always Active)
**Type**: Meta-Skill (coordinates all other skills)

---

## Auto-Trigger Patterns

**TRIGGER**: ALWAYS ACTIVE (monitors EVERY user message and tool use)

**When to Use**:
- ✅ Every user message received
- ✅ Every tool use (Write, Edit, Bash, Task, etc.)
- ✅ Every agent spawn
- ✅ Every state change

**Never Stops**: This skill runs continuously throughout the session

---

## Purpose

**Meta-orchestrator** that:
1. Monitors all user messages and tool uses
2. Matches them against skill trigger patterns
3. Activates appropriate skills automatically
4. Chains skills together in intelligent cascades
5. Aggregates results from multiple skills
6. Learns which skill combinations work best

**Think of this as**: The "conductor" of the skill orchestra, deciding which skills to play and when.

---

## Agent Integration

**Role**: This skill does NOT spawn agents directly - it activates OTHER skills that spawn agents

**Communication**:
- Monitors: All user input, all tool calls
- Activates: Other skills based on trigger patterns
- Coordinates: Multi-skill cascades
- Aggregates: Results from all activated skills

**No Task Tool Usage**: This is coordination only, delegates to other skills

---

## Trigger Pattern Matching

### Pattern Library (What to Watch For)

**Development Keywords** → Trigger: `princess-dev-skill` + `tdd-enforcer`
```
Keywords: ["implement", "add", "create", "build", "code", "write", "develop"]
Example: "implement user authentication"
Actions:
  1. Activate: tdd-enforcer skill
  2. Activate: queen-delegation-orchestrator skill
  3. Route to: princess-dev-skill
  4. Chain to: nasa-compliance-gate (on Write/Edit)
  5. Chain to: completion-gate (when done)
```

**Research Keywords** → Trigger: `princess-coordination-skill`
```
Keywords: ["research", "analyze", "plan", "design", "architecture", "spec"]
Example: "research best practices for REST APIs"
Actions:
  1. Activate: queen-delegation-orchestrator skill
  2. Route to: princess-coordination-skill
  3. Spawn: researcher + spec-writer + architect Drones
```

**Quality Keywords** → Trigger: `princess-quality-skill` + `completion-gate`
```
Keywords: ["test", "review", "audit", "quality", "document", "finalize"]
Example: "audit the code for security issues"
Actions:
  1. Activate: completion-gate skill
  2. Activate: queen-delegation-orchestrator skill
  3. Route to: princess-quality-skill
  4. Spawn: theater-detector + nasa-enforcer + docs-writer Drones
```

**Completion Keywords** → Trigger: `completion-gate`
```
Keywords: ["done", "finished", "complete", "ready", "finalize"]
Example: "I'm done with this feature"
Actions:
  1. BLOCK immediate response
  2. Activate: completion-gate skill
  3. Run ALL quality checks
  4. If ALL pass → Allow completion
  5. If ANY fail → Show failures, BLOCK completion
```

**Stuck Detection** → Trigger: `stuck-escalation`
```
Patterns:
  - Same error 3+ times
  - >30 minutes on same task
  - User says: "I'm stuck", "this isn't working", "I don't know"
Example: TypeError 3 times in a row
Actions:
  1. Activate: stuck-escalation skill
  2. Spawn: debugger Drone
  3. If still failing → Spawn: researcher Drone
  4. If STILL failing → Escalate to user: "I don't understand X"
```

**Decision Keywords** → Trigger: `decision-matrix-enforcer`
```
Keywords: ["should I use FSM", "should I use Analyzer", "state machine", "which approach"]
Example: "should I use a finite state machine for this?"
Actions:
  1. Activate: decision-matrix-enforcer skill
  2. Load: fsm-decision-matrix.dot
  3. Apply criteria: ≥3 of 5 required
  4. If met → Allow FSM
  5. If NOT met → Suggest simpler solution
```

**Deployment Keywords** → Trigger: `pre-deploy-validator`
```
Keywords: ["deploy", "production", "release", "publish", "go live"]
Example: "deploy to production"
Actions:
  1. BLOCK immediate deployment
  2. Activate: pre-deploy-validator skill
  3. Run 47-point checklist
  4. If ALL pass → Allow deployment
  5. If ANY fail → Show failures, BLOCK deployment
```

**Security Keywords** → Trigger: `security-audit-enforcer`
```
Keywords: ["authentication", "auth", "security", "login", "password", "token"]
Example: "implement authentication"
Actions:
  1. Activate: security-audit-enforcer skill (parallel with dev)
  2. Spawn: security-manager Drone
  3. Run security audit
  4. Flag vulnerabilities
```

**Tool Use Patterns** → Trigger: Tool-specific skills
```
Write/Edit operations → Trigger: nasa-compliance-gate
  Actions:
    1. Intercept Write/Edit call
    2. Activate: nasa-compliance-gate skill
    3. Spawn: nasa-enforcer Drone
    4. Check: ≤60 LOC per function, type hints
    5. If violations → BLOCK, show errors
    6. If clean → Allow write

Task tool use → Monitor agent spawns
  Actions:
    1. Log which agents spawned
    2. Track success/failure
    3. Feed to: agent-selector-optimizer skill

Bash errors → Track repeat failures
  Actions:
    1. Count same error occurrences
    2. If ≥3 → Trigger: stuck-escalation skill
```

---

## Cascade Patterns

### Pattern 1: Development Cascade (Most Common)
```
User: "implement user login"
  ↓
Cascade Orchestrator matches: "implement" + "login"
  ↓
Activates Skills (parallel):
  - queen-delegation-orchestrator → Routes to princess-dev-skill
  - tdd-enforcer → Forces test-first workflow
  - security-audit-enforcer → Auto security audit (login detected)
  ↓
princess-dev-skill spawns (sequence):
  - tester Drone: "Write failing test for login"
  - coder Drone: "Implement minimal login code"
  - reviewer Drone: "Review code quality"
  ↓
On Write/Edit operations:
  - nasa-compliance-gate activates automatically
  ↓
When user says "done":
  - completion-gate activates
  - Runs ALL quality checks
  - Blocks until ALL pass
  ↓
Result: Fully tested, secure, NASA-compliant login feature
```

### Pattern 2: Research Cascade
```
User: "research microservices architecture"
  ↓
Cascade Orchestrator matches: "research" + "architecture"
  ↓
Activates:
  - queen-delegation-orchestrator → Routes to princess-coordination-skill
  ↓
princess-coordination-skill spawns:
  - researcher Drone: "Research microservices patterns"
  - architect Drone: "Design architecture"
  - spec-writer Drone: "Document findings"
  ↓
Result: Research artifacts, architecture design, specification
```

### Pattern 3: Quality Cascade
```
User: "audit the codebase"
  ↓
Cascade Orchestrator matches: "audit"
  ↓
Activates:
  - queen-delegation-orchestrator → Routes to princess-quality-skill
  - completion-gate → Quality checklist
  ↓
princess-quality-skill spawns (parallel):
  - theater-detector Drone: "Scan for TODO/mock code"
  - nasa-enforcer Drone: "Check NASA Rule 10 compliance"
  - security-manager Drone: "Security audit"
  - docs-writer Drone: "Check documentation coverage"
  ↓
Aggregates:
  - Theater score: 0/100 (no mocks found) ✅
  - NASA compliance: 99.0% (3 minor violations) ⚠️
  - Security: No critical vulnerabilities ✅
  - Docs coverage: 85% ✅
  ↓
Result: Comprehensive quality report
```

### Pattern 4: Stuck Cascade (Auto-Escalation)
```
Situation: Same TypeError 3 times
  ↓
Cascade Orchestrator detects: Repeat error pattern
  ↓
Activates: stuck-escalation skill
  ↓
stuck-escalation spawns:
  - debugger Drone: "Debug TypeError in module X"
  ↓
If still failing after 5 minutes:
  - researcher Drone: "Research TypeError solutions"
  ↓
If STILL failing after 10 minutes:
  - Escalate to user: "I don't understand why TypeError occurs in X.
     I've tried: [list of attempts]. I need help with: [specific question]"
  ↓
Result: Automatic escalation prevents infinite loops
```

### Pattern 5: Deployment Cascade (Safety Checks)
```
User: "deploy to production"
  ↓
Cascade Orchestrator matches: "deploy" + "production"
  ↓
BLOCKS immediate deployment
  ↓
Activates: pre-deploy-validator skill
  ↓
pre-deploy-validator runs 47-point checklist:
  - All tests passing? (npm test)
  - Build successful? (npm run build)
  - No TypeScript errors? (npx tsc)
  - NASA compliant? (nasa-enforcer Drone)
  - No theater code? (theater-detector Drone)
  - Security audit passed? (security-manager Drone)
  - Documentation updated? (docs-writer Drone)
  - Environment variables set?
  - Database migrations ready?
  - Rollback plan documented?
  - [... 37 more checks ...]
  ↓
If ALL 47 pass:
  - Allow deployment
  - Activate: devops Drone for deployment execution
  ↓
If ANY fail:
  - BLOCK deployment
  - Show failed checks
  - Require fixes before retry
  ↓
Result: Zero unvalidated production deployments
```

---

## Orchestration Logic

### Phase 1: Pattern Recognition (always running)
```python
def on_user_message(message: str):
    """Analyze every user message for trigger patterns."""

    # Normalize message
    message_lower = message.lower()

    # Match against patterns
    matched_skills = []

    # Check development keywords
    if any(kw in message_lower for kw in ["implement", "add", "create", "build", "code"]):
        matched_skills.append("tdd-enforcer")
        matched_skills.append("queen-delegation-orchestrator")

    # Check quality keywords
    if any(kw in message_lower for kw in ["done", "finished", "complete", "ready"]):
        matched_skills.append("completion-gate")

    # Check security keywords
    if any(kw in message_lower for kw in ["auth", "login", "security", "password"]):
        matched_skills.append("security-audit-enforcer")

    # Check deployment keywords
    if any(kw in message_lower for kw in ["deploy", "production", "release"]):
        matched_skills.append("pre-deploy-validator")

    # Check decision keywords
    if any(kw in message_lower for kw in ["should I use", "which approach", "fsm"]):
        matched_skills.append("decision-matrix-enforcer")

    return matched_skills
```

### Phase 2: Skill Activation (parallel where possible)
```python
def activate_skills(matched_skills: list):
    """Activate all matched skills."""

    # Determine execution order
    # Some skills MUST run before others
    priority_order = {
        "completion-gate": 1,          # BLOCK actions first
        "pre-deploy-validator": 1,     # BLOCK deployments first
        "decision-matrix-enforcer": 2, # Decide BEFORE implementing
        "tdd-enforcer": 3,             # Enforce TDD BEFORE coding
        "queen-delegation-orchestrator": 4, # Route to agents
        "security-audit-enforcer": 5,  # Run in parallel with dev
        "nasa-compliance-gate": 6      # Check on every write
    }

    # Sort by priority
    sorted_skills = sorted(matched_skills, key=lambda s: priority_order.get(s, 10))

    # Activate in order
    results = {}
    for skill in sorted_skills:
        results[skill] = activate_skill(skill)

    return results
```

### Phase 3: Result Aggregation
```python
def aggregate_results(results: dict):
    """Combine results from multiple skills."""

    # Check for blocking skills
    blockers = []
    for skill, result in results.items():
        if result.get("blocked"):
            blockers.append({
                "skill": skill,
                "reason": result.get("block_reason"),
                "failures": result.get("failures", [])
            })

    # If any skill blocked, return early
    if blockers:
        return {
            "blocked": True,
            "blockers": blockers,
            "message": "Action blocked by quality gates. Fix issues before proceeding."
        }

    # Otherwise, aggregate success results
    return {
        "blocked": False,
        "skills_activated": list(results.keys()),
        "results": results
    }
```

---

## Monitoring & Learning

### What to Track
```json
{
  "session_id": "session-20250101-1234",
  "skill_activations": [
    {
      "skill": "tdd-enforcer",
      "trigger": "user said 'implement login'",
      "timestamp": "2025-01-01T12:34:56Z",
      "success": true,
      "agents_spawned": ["tester", "coder", "reviewer"],
      "execution_time_ms": 450
    },
    {
      "skill": "security-audit-enforcer",
      "trigger": "detected 'auth' keyword",
      "timestamp": "2025-01-01T12:35:10Z",
      "success": true,
      "agents_spawned": ["security-manager"],
      "vulnerabilities_found": 2
    }
  ],
  "cascades": [
    {
      "cascade_id": "cascade-1",
      "skills": ["tdd-enforcer", "queen-delegation-orchestrator", "security-audit-enforcer"],
      "trigger": "implement login",
      "success": true,
      "total_time_ms": 12500
    }
  ],
  "blocked_actions": [
    {
      "action": "deployment",
      "blocked_by": "pre-deploy-validator",
      "reason": "3 tests failing",
      "timestamp": "2025-01-01T12:40:00Z"
    }
  ]
}
```

### Learning Patterns
```python
def learn_from_session():
    """Analyze session to improve skill selection."""

    # Which cascades were successful?
    successful_cascades = [c for c in session.cascades if c["success"]]

    # Which skill combinations work well together?
    for cascade in successful_cascades:
        skill_combo = tuple(sorted(cascade["skills"]))
        skill_combo_success_rate[skill_combo] = skill_combo_success_rate.get(skill_combo, 0) + 1

    # Which triggers reliably activate correct skills?
    for activation in session.skill_activations:
        trigger = activation["trigger"]
        skill = activation["skill"]
        if activation["success"]:
            trigger_skill_map[trigger] = trigger_skill_map.get(trigger, {})
            trigger_skill_map[trigger][skill] = trigger_skill_map[trigger].get(skill, 0) + 1

    # Save learnings for next session
    save_learnings_to_disk()
```

---

## Integration with Other Skills

**Coordinates**:
1. `session-init-queen` - Waits for this to complete before activating
2. `queen-delegation-orchestrator` - Triggers this for routing
3. `princess-coordination-skill` - Activates via queen-delegation
4. `princess-dev-skill` - Activates via queen-delegation
5. `princess-quality-skill` - Activates via queen-delegation
6. `tdd-enforcer` - Activates on "implement" keywords
7. `nasa-compliance-gate` - Activates on Write/Edit operations
8. `completion-gate` - Activates on "done" keywords
9. `stuck-escalation` - Activates on repeat errors
10. `decision-matrix-enforcer` - Activates on decision keywords
11. `pre-deploy-validator` - Activates on deployment keywords
12. `security-audit-enforcer` - Activates on security keywords
13. `rollback-emergency` - Activates on production errors
14. `agent-selector-optimizer` - Feeds data to for optimization

---

## Output

**Visible to User**:
```
🎼 **Skill Orchestrator**: Activated 3 skills for your request

✅ **tdd-enforcer**: Enforcing test-first development
✅ **queen-delegation-orchestrator**: Routing to Princess-Dev
✅ **security-audit-enforcer**: Running security audit (parallel)

⏳ Processing... (you'll see agent activity in the sidebar)
```

**Internal Logging**:
```
[Orchestrator] User message: "implement user login"
[Orchestrator] Matched patterns: ["implement", "login"]
[Orchestrator] Activating skills: [tdd-enforcer, queen-delegation-orchestrator, security-audit-enforcer]
[Orchestrator] Cascade created: cascade-20250101-1234
[Orchestrator] Monitoring progress...
```

---

## Performance Targets

- **Pattern Matching**: <5ms per message
- **Skill Activation**: <10ms per skill
- **Cascade Coordination**: <100ms total overhead
- **Memory Usage**: <100KB (pattern library + state tracking)

---

## Troubleshooting

### Issue: "Too many skills activated"
**Cause**: Overly broad trigger patterns
**Fix**: Refine patterns to be more specific

### Issue: "Skills conflicting with each other"
**Cause**: Execution order incorrect
**Fix**: Adjust priority_order dict

### Issue: "Cascade taking too long"
**Cause**: Too many sequential dependencies
**Fix**: Identify skills that can run in parallel

---

## Version History

**1.0.0** (2025-10-17):
- Initial implementation
- 14 skill coordination
- Pattern matching library
- Cascade logic
- Learning system

---

**Last Updated**: 2025-10-17
**Status**: ✅ ACTIVE (P0 - Critical, Always Running)
**Dependencies**: session-init-queen (must complete first)
**Integration**: Coordinates ALL other skills
**Maintained By**: SPEK Platform Team
