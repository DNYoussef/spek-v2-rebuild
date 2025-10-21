# Loop 2: Implementation (Queen → Princess → Drone Hive System)

## Overview

Loop 2 is the SPEK Platform's implementation phase that uses the Queen → Princess → Drone hierarchical coordination system to transform Loop 1 plans into working, tested, quality code. This skill activates Claude Code as the Queen agent, which delegates to Princess coordinators, who spawn specialized Drone workers. Throughout implementation, a continuous 3-part audit system validates functionality, style, and theater detection.

This skill represents the second phase of the 3-loop methodology: **Loop 1 (Planning) → Loop 2 (Implementation) → Loop 3 (Quality)**. It also handles the debug route: **Loop 1 (Replan) → Loop 2 (Fix) → Loop 3 (Revalidate)**.

## When to Use This Skill

Activate Loop 2 when:
- **Loop 1 complete**: Plans, specs, and pre-mortem analysis exist and passed GO decision
- **User implementation requests**: "implement", "code", "build", "create", "write" keywords detected
- **Debug route from Loop 1**: Received fix plan from Loop 1 after Loop 3 escalation
- **Direct coding requests**: User asks to fix bugs, add features, or modify code

**Auto-Trigger Patterns**:
- Keywords: "implement", "code", "build", "create", "write", "develop", "fix", "add"
- Phrases: "Build the feature...", "Implement the plan...", "Fix the bug in...", "Add support for..."
- Memory signal: `memory["current_loop"] == "loop2"` (Loop 1 completed)
- Debug escalation: Loop 1 sends fix plan after Loop 3 failure

## Queen → Princess → Drone Architecture

Loop 2 uses a 3-tier hierarchical coordination system:

### Tier 1: Queen (Claude Code Instance)

**Role**: Top-level coordinator and orchestrator
**Identity**: This Claude Code instance IS the Queen agent
**Responsibilities**:
- Read Loop 1 plans from memory
- Determine which Princess to delegate to
- Monitor overall progress
- Handle escalations and blockers
- Coordinate transitions to Loop 3

**Queen Decision Logic**:
```python
# Queen analyzes task and selects Princess
task_type = analyze_task_type(user_request, loop1_plan)

if task_type in ["code", "implement", "build", "develop"]:
    princess = "princess-dev"
elif task_type in ["research", "plan", "design"]:
    princess = "princess-coordination"  # Rare in Loop 2
elif task_type in ["test", "review", "audit"]:
    princess = "princess-quality"  # Pre-Loop 3 validation
else:
    princess = "princess-dev"  # Default
```

### Tier 2: Princess (Coordination Layer)

**3 Princess Agents**:
1. **Princess-Dev**: Development coordination (primary for Loop 2)
2. **Princess-Coordination**: Research coordination (rare in Loop 2)
3. **Princess-Quality**: Quality coordination (pre-Loop 3 checks)

**Princess-Dev Responsibilities** (most used in Loop 2):
- Spawn Coder, Tester, Reviewer Drones
- Coordinate implementation phases
- Run 3-part audit system continuously
- Escalate blockers to Queen
- Validate milestones from Loop 1 plan

**Princess Spawning Pattern**:
```python
Task(
    subagent_type="princess-dev",
    description="Coordinate feature implementation",
    prompt=f"""You are Princess-Dev, the Development Coordinator.

TASK: Implement {feature_name}

CONTEXT FROM LOOP 1:
- Plan: {plan_path}
- Research: {research_path}
- Risks: {risks_path}
- Agents needed: {agents_needed}
- Phases: {phases}
- Milestones: {milestones}

YOUR RESPONSIBILITIES:
1. Spawn Drones from agent registry based on Loop 1 recommendations
2. Coordinate implementation across {num_phases} phases
3. Run 3-part audit after each phase:
   - Functionality audit (tests pass)
   - Style audit (NASA compliance, linting)
   - Theater audit (no TODOs, mocks, placeholders)
4. Escalate blockers to Queen
5. Mark milestones complete in memory

DRONE SPAWNING:
Use agent_registry.py to find best Drones:
```python
from src.coordination.agent_registry import find_drones_for_task
drones = find_drones_for_task("{task_description}", "loop2")
```

Spawn each Drone with Task tool and specific instructions.

AUDIT SYSTEM:
After each phase, run all 3 audits:
- If ALL pass → Continue to next phase
- If ANY fail → Fix issues, rerun audits
- If 3 audit failures → Escalate to Queen

DELIVERABLES:
- Working, tested code
- Audit reports (functionality, style, theater)
- Updated files list in memory
- Milestone completion status

Begin implementation Phase 1."""
)
```

### Tier 3: Drones (Specialized Workers)

**Available Drones for Loop 2** (from `agent_registry.py`):
- `coder`: Writes code following NASA Rule 10
- `tester`: Creates test suites with ≥80% coverage
- `reviewer`: Reviews code quality and security
- `debugger`: Fixes bugs and issues
- `frontend-dev`: Develops UI components
- `backend-dev`: Develops APIs and server logic
- `integration-engineer`: Integrates components
- `orchestrator`: Coordinates multi-agent workflows

**Drone Selection (Intelligent)**:
```python
# Princess-Dev uses agent registry for intelligent selection
task = "Implement REST API with authentication"
drones = find_drones_for_task(task, "loop2")
# Returns: ["backend-dev", "coder", "security-manager", "tester"]

# Spawn top 3 Drones in parallel
for drone_id in drones[:3]:
    Task(subagent_type=drone_id, description=f"{drone_id} work", prompt=...)
```

**Drone Spawning Pattern** (by Princess):
```python
# Example: Princess-Dev spawns Coder Drone
Task(
    subagent_type="coder",
    description="Implement authentication module",
    prompt=f"""You are the Coder Drone.

TASK: Implement authentication module per plan

PLAN EXCERPT:
{relevant_plan_section}

CONSTRAINTS:
- NASA Rule 10: ≤60 LOC per function
- Type hints required (Python) or TypeScript strict mode
- Write tests FIRST (TDD)
- No TODO comments (complete work only)
- No mock data (use real implementations)

FILES TO CREATE/MODIFY:
{file_list_from_plan}

DEPENDENCIES:
{dependencies_from_plan}

DELIVERABLES:
1. Implementation files in /src/
2. Test files in /tests/
3. Type definitions (if TypeScript)
4. Brief summary of changes

CODE STYLE:
- Follow existing project conventions
- Use descriptive variable names
- Add docstrings for functions
- Handle errors gracefully

TESTING:
- Write tests BEFORE implementation
- Aim for ≥80% coverage
- Include edge cases
- Use existing test frameworks

TIME BUDGET: 30 minutes

Report when complete or if blocked."""
)
```

## Loop 2 Workflow Phases

Loop 2 follows the phases defined in Loop 1's implementation plan, with continuous auditing:

### Phase 1: Queen Initialization & Context Loading

**Actions**:
1. Verify Loop 1 completion: Check `memory["loop1"]["status"] == "complete"`
2. Load Loop 1 context:
   ```python
   loop1 = memory["loop1"]
   plan_path = loop1["plans"][0]
   research_path = loop1["specs"][0]
   risks = loop1["risks"][0]
   agents_needed = loop1["plan"]["agents_needed"]
   phases = loop1["plan"]["phases"]
   ```
3. Read implementation plan file
4. Set Loop 2 status to "in_progress"
5. Initialize audit system
6. Determine route (development vs debug)

### Phase 2: Princess Selection & Delegation

**Use princess-summoning skill** to spawn Princess-Dev:

The princess-summoning skill handles Princess selection and spawning for Loop 2. Princess-Dev will then use the drone-selection skill to find and spawn implementation Drones.

```markdown
# Invoke princess-summoning skill
Use princess-summoning skill:
- Loop: loop2
- Task: {feature_name} implementation
- Princess: princess-dev (automatically selected for loop2)
- Context: Loop 1 outputs (plans, specs, risks, milestones)

Princess-Dev will then:
1. Use drone-selection skill to find best Drones for implementation
2. Spawn appropriate Drones (coder, tester, reviewer, frontend-dev, backend-dev, etc.)
3. Run 3-part audit system after each phase
4. Validate milestones from Loop 1 plan
5. Coordinate Drone outputs into working, tested code
```

**Alternative: Direct Queen Decision** (if not using skill system):
```python
# Analyze task type from plan
task_type = extract_task_type(plan)

# Select Princess
if "implement" or "code" or "build" in task_type:
    princess = "princess-dev"  # 95% of Loop 2 cases
elif "test" or "quality" in task_type:
    princess = "princess-quality"
else:
    princess = "princess-dev"  # Default

# Spawn Princess with full context
Task(
    subagent_type=princess,
    description="Coordinate implementation",
    prompt=queen_delegation_prompt(loop1_context, plan)
)
```

### Phase 3: Princess Spawns Drones

**Princess-Dev Actions**:
1. Read Loop 1 plan thoroughly
2. **Use drone-selection skill** to find best Drones:
   ```markdown
   # Princess-Dev invokes drone-selection skill
   Use drone-selection skill:
   - Task: "Implement REST API with OAuth2"
   - Loop: loop2
   - Context: Loop 1 plan, user requirements

   Drone-selection returns: ["backend-dev", "coder", "security-manager", "tester", "reviewer"]
   ```

   **Alternative: Direct agent registry call**:
   ```python
   # Example from plan: "Implement REST API with OAuth2"
   from src.coordination.agent_registry import find_drones_for_task

   drones = find_drones_for_task("REST API OAuth2 implementation", "loop2")
   # Returns: ["backend-dev", "coder", "security-manager", "tester", "reviewer"]
   ```
3. Spawn Drones in optimal order:
   - **Phase 1**: Spawn `tester` FIRST (TDD - tests before code)
   - **Phase 2**: Spawn `coder` or `backend-dev` (implement to pass tests)
   - **Phase 3**: Spawn `reviewer` (code review)
   - **Phase 4**: Run 3-part audit
4. Coordinate Drone outputs
5. Handle Drone failures/blockers

**Parallel vs Sequential Spawning**:
```python
# Parallel: Independent tasks (single message, multiple Task calls)
Task(subagent_type="frontend-dev", description="Build UI", prompt=...)
Task(subagent_type="backend-dev", description="Build API", prompt=...)

# Sequential: Dependencies (wait for output before next)
tests = Task(subagent_type="tester", description="Write tests", prompt=...)
# Wait for tests to complete
code = Task(subagent_type="coder", description="Implement code", prompt=f"Pass these tests: {tests}")
```

### Phase 4: Continuous 3-Part Audit System

**The 3 Audits** (run after EVERY phase):

#### Audit 1: Functionality Audit

**Purpose**: Verify code actually works
**Actions**:
```python
# Run test suite
result = run_tests()

# Check:
- All tests pass ✅
- Coverage ≥80% ✅
- No failing edge cases ✅

# If pass → Continue
# If fail → Spawn debugger Drone, fix, retest
```

**Using Helper Script**:
```python
from .scripts.audit_runner import FunctionalityAudit

auditor = FunctionalityAudit(project_root=".")
result = auditor.run()

if result["passed"]:
    print("✅ Functionality audit passed")
else:
    print(f"❌ Functionality audit failed: {result['failures']}")
    # Escalate to debugger Drone
```

#### Audit 2: Style Audit

**Purpose**: Verify code meets quality standards
**Actions**:
```python
# Check:
- NASA Rule 10: ≤60 LOC per function ✅
- Type hints present (Python) or TypeScript strict ✅
- ESLint/Pylint passes ✅
- No recursion ✅
- Fixed loop bounds ✅

# If pass → Continue
# If fail → Auto-fix or spawn reviewer Drone
```

**Using Helper Script**:
```python
from .scripts.audit_runner import StyleAudit

auditor = StyleAudit(path="src/")
result = auditor.run()

if result["compliant"]:
    print(f"✅ Style audit passed ({result['compliance_rate']}%)")
else:
    print(f"❌ Style violations: {result['violations']}")
    # Auto-fix or escalate
```

#### Audit 3: Theater Detection Audit

**Purpose**: Ensure no placeholder/mock code
**Actions**:
```python
# Check:
- No TODO comments ✅
- No FIXME comments ✅
- No mock/fake data ✅
- No placeholder implementations ✅
- No commented-out code ✅

# If pass → Continue
# If fail → Spawn coder Drone to complete work
```

**Using Helper Script**:
```python
from .scripts.audit_runner import TheaterAudit

auditor = TheaterAudit(path="src/")
result = auditor.run()

if result["score"] < 60:  # Score: lower is better
    print("✅ Theater audit passed (no placeholders)")
else:
    print(f"❌ Theater detected: {result['issues']}")
    # Spawn coder to complete work
```

**Audit Workflow**:
```
After each implementation phase:

1. Run all 3 audits in parallel
2. If ALL pass → Mark phase complete, continue
3. If ANY fail → Fix issues, rerun audits
4. If 3 consecutive audit failures → Escalate to Queen
5. Queen decides: retry with different Drones OR escalate to Loop 1 (replan)
```

### Phase 5: Milestone Validation

**Check Loop 1 Plan Milestones**:
```python
# Loop 1 plan defined milestones
milestones = loop1["plan"]["milestones"]
# Example: ["API routes defined", "Authentication working", "Tests passing"]

# After each phase, check milestone completion
current_phase = 2
milestone = milestones[current_phase - 1]

# Validate milestone
if validate_milestone(milestone):
    memory["loop2"]["completed_milestones"].append(milestone)
else:
    # Milestone not met, retry phase or escalate
    escalate_to_queen(f"Milestone not met: {milestone}")
```

### Phase 6: Loop 2 Completion & Handoff to Loop 3

**Completion Criteria**:
- ✅ All phases from Loop 1 plan complete
- ✅ All 3 audits passing (functionality, style, theater)
- ✅ All milestones validated
- ✅ No blockers or P0 issues
- ✅ Files in proper directories (not root)

**Memory State Update**:
```python
memory["loop2"] = {
    "feature_name": feature_name,
    "files_changed": [
        "/src/auth.py",
        "/src/tokens.py",
        "/tests/test_auth.py"
    ],
    "agents_spawned": ["coder", "tester", "reviewer"],
    "audit_results": {
        "functionality": "pass",
        "style": "pass",
        "theater": "pass"
    },
    "completed_milestones": [
        "API routes defined",
        "Authentication working",
        "Tests passing"
    ],
    "phases_completed": 5,
    "status": "complete",
    "completed_at": timestamp,
    "route": "development" | "debug"
}

memory["current_loop"] = "loop3"  # Transition
```

**Handoff to Loop 3**:
```
Task(
    subagent_type="general-purpose",
    description="Transition to Loop 3",
    prompt=f"""Loop 2 (Implementation) is complete. Transition to Loop 3 (Quality).

LOOP 2 OUTPUTS:
- Files changed: {files_changed}
- Audits: Functionality ✅, Style ✅, Theater ✅
- Milestones: {completed_milestones}

NEXT STEPS:
1. Activate Loop 3 (Quality) skill
2. Pass Loop 2 context via memory
3. Loop 3 will run comprehensive quality validation

MEMORY CONTEXT:
{json.dumps(memory["loop2"], indent=2)}

The Loop 3 skill will now take over."""
)
```

**User Notification**:
```
✅ Loop 2 (Implementation) Complete

📝 Changes:
- Files modified: {len(files_changed)}
- Agents used: {", ".join(agents_spawned)}
- Phases completed: {phases_completed}/{total_phases}

✅ Audits:
- Functionality: PASS
- Style: PASS
- Theater: PASS

✅ Milestones:
{format_milestones(completed_milestones)}

➡️  Next: Loop 3 (Quality) will validate for production readiness
```

## Agent Registry Integration

Loop 2 uses these agents from `agent_registry.py`:

**Queen**:
- `queen`: Claude Code instance (top coordinator)

**Princess**:
- `princess-dev`: Development coordinator (primary for Loop 2)

**Drones** (24 available, top 8 for Loop 2):
- `coder`: Core implementation
- `tester`: Test creation
- `reviewer`: Code review
- `debugger`: Bug fixing
- `frontend-dev`: UI development
- `backend-dev`: API development
- `integration-engineer`: Component integration
- `orchestrator`: Workflow coordination

**Selection Examples**:
```python
# Example 1: Frontend feature
task = "Build React component for user profile"
drones = find_drones_for_task(task, "loop2")
# Returns: ["frontend-dev", "coder", "tester", "reviewer"]

# Example 2: Backend API
task = "Create REST API for payments"
drones = find_drones_for_task(task, "loop2")
# Returns: ["backend-dev", "coder", "security-manager", "tester"]

# Example 3: Bug fix
task = "Fix authentication bug in login flow"
drones = find_drones_for_task(task, "loop2")
# Returns: ["debugger", "tester", "reviewer"]
```

## Memory Integration

Loop 2 reads from Loop 1 and writes for Loop 3 consumption.

**Read from Loop 1**:
```python
# Load Loop 1 context
loop1 = memory["loop1"]
plan_path = loop1["plans"][0]
agents_needed = loop1["plan"]["agents_needed"]
phases = loop1["plan"]["phases"]
risk_score = loop1["risk_score"]
```

**Write for Loop 3**:
```python
# Store Loop 2 outputs
memory["loop2"] = {
    "feature_name": "user-authentication",
    "files_changed": [...],
    "agents_spawned": [...],
    "audit_results": {...},
    "completed_milestones": [...],
    "status": "complete"
}
```

## 3-Part Audit System Details

The audit system runs continuously throughout Loop 2:

### Audit Timing

**When to Run Audits**:
1. After each implementation phase (from Loop 1 plan)
2. Before milestone validation
3. Before Loop 2 → Loop 3 transition
4. On-demand (Queen/Princess request)

### Audit Failure Handling

**3-Strike Rule**:
```
Audit Failure #1 → Retry (spawn debugger/reviewer Drone)
Audit Failure #2 → Retry with different Drone
Audit Failure #3 → Escalate to Queen
```

**Queen Escalation Decision**:
```python
if audit_failures >= 3:
    # Queen analyzes situation
    if is_fundamental_issue(failures):
        # Escalate to Loop 1 (replan)
        escalate_to_loop1("Fundamental design flaw detected")
    else:
        # Retry with expert Drone
        spawn_expert_drone(failure_context)
```

### Audit Scripts

Loop 2 includes helper scripts for deterministic audit execution:

**Functionality Audit Script**:
```python
# .claude/skills/loop2-implementation/scripts/audit_runner.py
class FunctionalityAudit:
    def run(self) -> Dict[str, Any]:
        # Auto-detect test framework
        # Run tests
        # Parse output
        # Return structured results
        return {
            "passed": True,
            "total_tests": 42,
            "failed_tests": 0,
            "coverage": 0.87,
            "duration": 4.2
        }
```

**Style Audit Script** (uses existing NASA compliance checker):
```python
from .scripts.nasa_compliance_checker import NASAComplianceChecker

checker = NASAComplianceChecker(path="src/", max_loc=60)
result = checker.run()

if result["compliant"]:
    print(f"✅ NASA compliance: {result['compliance_rate']}%")
```

**Theater Audit Script**:
```python
class TheaterAudit:
    PATTERNS = [
        r"TODO",
        r"FIXME",
        r"HACK",
        r"mock_",
        r"fake_",
        r"placeholder",
        r"# .* implementation"
    ]

    def run(self) -> Dict[str, Any]:
        # Search for theater patterns
        # Score: 0-100 (lower is better)
        return {
            "score": 12,
            "issues": [...],
            "passed": True  # score < 60
        }
```

## Debug Route (Loop 1 → Loop 2 Fix)

When Loop 3 escalates to Loop 1, Loop 1 creates a fix plan, then Loop 2 implements the fix.

**Debug Route Differences**:
1. **Context**: Load Loop 3 failure context + Loop 1 fix plan
2. **Focus**: Targeted fix (not full feature implementation)
3. **Agents**: Spawn `debugger` + `tester` (minimal team)
4. **Audits**: Extra focus on regression testing
5. **Validation**: Ensure original issue fixed, no new issues

**Debug Route Workflow**:
```python
# Step 1: Load context
loop3_failure = memory["loop3"]["escalations"][-1]
loop1_fix_plan = memory["loop1"]["plans"][-1]  # Fix plan

# Step 2: Princess-Dev spawns debugger
Task(
    subagent_type="debugger",
    description="Fix issue",
    prompt=f"""Fix issue per plan.

ISSUE: {loop3_failure['error_logs']}
FIX PLAN: {loop1_fix_plan}
AFFECTED FILES: {loop3_failure['affected_files']}

Apply fix, ensure tests pass, verify no regressions."""
)

# Step 3: Extra regression testing
Task(
    subagent_type="tester",
    description="Regression testing",
    prompt="Run full test suite, check for new failures"
)

# Step 4: Run 3-part audit (same as development route)
# Step 5: Transition to Loop 3 for revalidation
```

## Error Handling & Escalation

**If Drone Spawn Fails**:
1. Retry with same Drone (maybe temporary issue)
2. If 2 failures, try alternative Drone from registry
3. If 3 failures, escalate to Queen with error context

**If Audit Fails 3 Times**:
1. Queen analyzes failure pattern
2. If design issue → Escalate to Loop 1 (replan)
3. If implementation issue → Spawn expert Drone
4. If unknown → Ask user for guidance

**If Milestone Not Met**:
1. Retry current phase with different Drones
2. If 2 failures, escalate to Queen
3. Queen may extend timeline or replanning

**If Time Budget Exceeded**:
```python
# Loop 1 plan estimated 3 weeks
if time_elapsed > plan_estimate * 1.5:
    warn_user(f"Implementation taking longer than planned: {time_elapsed} vs {plan_estimate}")
    ask_user("Continue or replan?")
```

## Success Criteria

Loop 2 is considered successful when:
- ✅ All phases from Loop 1 plan completed
- ✅ All milestones validated
- ✅ Functionality audit passing (tests ✅, coverage ≥80%)
- ✅ Style audit passing (NASA compliance ≥96%)
- ✅ Theater audit passing (score <60)
- ✅ Files in proper directories (not root)
- ✅ Memory state updated with Loop 2 context
- ✅ User notified of completion
- ✅ Loop 3 transition initiated

**Quality Bar**:
- Zero failing tests
- ≥80% code coverage (≥90% for critical paths)
- ≥96% NASA compliance
- Zero TODO/FIXME comments
- Zero mock/placeholder implementations
- All TypeScript/Python type hints present

## Integration with Flow Orchestrator

Loop 2 is part of the bidirectional flow system:

**Development Route (Normal)**:
```
Loop 1 (Planning) → Loop 2 (Implementation) → Loop 3 (Quality) → Done
```

**Debug Route (Failure)**:
```
Loop 1 (Fix Plan) → Loop 2 (Apply Fix) → Loop 3 (Revalidate) → Done
```

The Flow Orchestrator skill manages routing based on:
- Memory state (`current_loop`, `flow_route`)
- Loop 1 completion status
- Loop 3 escalation signals

See `flow-orchestrator` skill for complete routing logic.

## Helper Scripts & Resources

Loop 2 includes bundled resources:

**Scripts** (`.claude/skills/loop2-implementation/scripts/`):
- `audit_runner.py`: Runs all 3 audits (functionality, style, theater)
- `queen_coordinator.py`: Queen orchestration helpers
- `princess_spawner.py`: Princess selection and spawning logic
- `drone_selector.py`: Wraps `find_drones_for_task()`
- `loop2_memory.py`: Memory persistence helpers

**Diagrams** (`.claude/skills/loop2-implementation/diagrams/`):
- `loop2-implementation-process.dot`: Visual workflow (GraphViz)
- `queen-princess-drone-hierarchy.dot`: Architecture diagram

**Agent Prompts** (`.claude/skills/loop2-implementation/prompts/`):
- `queen_delegation_prompt.txt`: Template for Queen → Princess
- `princess_coordination_prompt.txt`: Template for Princess → Drones
- `drone_task_prompt.txt`: Template for Drone tasks

**Usage Example**:
```python
# Use helper script for audit
from scripts.audit_runner import run_all_audits

results = run_all_audits(project_root=".")

if all(r["passed"] for r in results.values()):
    print("✅ All audits passed")
    transition_to_loop3()
else:
    print("❌ Audit failures detected")
    handle_failures(results)
```

## Appendix: Complete Example Flow

**User Request**: "Implement user authentication with OAuth2"

**Loop 2 Execution**:

```python
# Step 1: Queen reads Loop 1 context
loop1 = memory["loop1"]
plan = read_file(loop1["plans"][0])  # /plans/user-auth-plan.md

# Step 2: Queen spawns Princess-Dev
Task(
    subagent_type="princess-dev",
    description="Coordinate user auth implementation",
    prompt=f"""Princess-Dev, coordinate implementation.

PLAN: {plan}
PHASES: 5 (Backend, Frontend, Tests, Security, Integration)
AGENTS NEEDED: backend-dev, frontend-dev, tester, security-manager
ROUTE: development

Begin Phase 1: Backend implementation."""
)

# Step 3: Princess-Dev spawns Drones (Phase 1)
# First: Tester (TDD)
Task(subagent_type="tester", description="Write auth tests", prompt="...")
# Then: Backend-Dev (implementation)
Task(subagent_type="backend-dev", description="Implement OAuth2 flow", prompt="...")

# Step 4: After Phase 1, run 3-part audit
functionality_audit = run_functionality_audit()  # ✅ Pass
style_audit = run_style_audit()  # ✅ Pass
theater_audit = run_theater_audit()  # ✅ Pass

# Step 5: Validate Phase 1 milestone
milestone_met = validate_milestone("Backend OAuth2 endpoints working")  # ✅

# Step 6: Continue to Phase 2 (Frontend)...
# ... (repeat for all 5 phases)

# Step 7: Loop 2 complete, transition to Loop 3
memory["loop2"]["status"] = "complete"
memory["current_loop"] = "loop3"
activate_loop3()
```

**Result**:
- 5 phases completed
- 15+ files created/modified
- All tests passing (87% coverage)
- NASA compliance: 97.2%
- Theater score: 8 (no placeholders)
- Ready for Loop 3 quality validation

---

**Version**: 1.1.0
**Last Updated**: 2025-10-18
**Part of**: SPEK Platform 3-Loop Methodology
**Related Skills**: `princess-summoning`, `drone-selection`, `loop1-planning`, `loop3-quality`, `flow-orchestrator`
