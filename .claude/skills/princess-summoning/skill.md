# Princess Summoning

## Overview

This skill handles Princess agent selection and spawning within the SPEK Platform's 3-tier Queen → Princess → Drone hierarchy. Use this skill when the Queen (Claude Code) needs to delegate work to one of the three Princess coordinators based on the current loop and task type. This skill is automatically invoked by Loop 1, Loop 2, and Loop 3 skills during their workflow phases.

The Princess layer provides intelligent coordination between the Queen (strategic oversight) and Drones (tactical execution), ensuring work is properly organized, monitored, and validated throughout the development lifecycle.

## When to Use This Skill

Activate this skill when:
- **Starting a new loop phase**: Loop 1/2/3 needs to spawn its designated Princess coordinator
- **Task delegation required**: Queen determines work needs Princess-level coordination
- **Multi-drone coordination**: Task requires spawning multiple specialized Drone agents
- **Audit coordination**: Running 3-part audit system (functionality, style, theater)
- **Milestone validation**: Checking Loop 1 plan milestones during implementation

**Auto-Trigger Patterns**:
- Loop skills invoke this automatically during initialization
- Keywords: "spawn princess", "coordinate", "delegate to princess"
- Memory signal: `memory["current_loop"]` changes (loop1/loop2/loop3)
- Task complexity: >3 Drones needed (requires Princess coordination)

**DO NOT use this skill for**:
- Direct Drone spawning (use `drone-selection` skill instead)
- Queen-level decisions (Queen handles this directly)
- Single-agent tasks (spawn Drone directly without Princess)

## Princess Selection Logic

The skill uses loop context and task analysis to select the appropriate Princess:

### Selection Algorithm

```python
def select_princess(loop: str, task_type: str) -> str:
    """
    Select Princess based on current loop and task characteristics.

    Args:
        loop: Current loop (loop1/loop2/loop3)
        task_type: Type of task (research/development/quality)

    Returns:
        Princess agent ID (princess-coordination/princess-dev/princess-quality)
    """
    # Primary selection: By loop
    if loop == "loop1":
        return "princess-coordination"  # Research & Planning
    elif loop == "loop2":
        return "princess-dev"  # Development & Implementation
    elif loop == "loop3":
        return "princess-quality"  # Quality & Validation

    # Secondary selection: By task type (if loop unknown)
    if any(kw in task_type for kw in ["research", "plan", "design", "spec", "architecture"]):
        return "princess-coordination"
    elif any(kw in task_type for kw in ["implement", "code", "build", "develop", "create"]):
        return "princess-dev"
    elif any(kw in task_type for kw in ["test", "review", "audit", "quality", "validate"]):
        return "princess-quality"

    # Fallback: Default to Development Princess
    return "princess-dev"
```

### Princess Capabilities

**Princess-Coordination** (Loop 1):
- **Responsibility**: Research and planning coordination
- **Spawns**: researcher, spec-writer, architect, pseudocode-writer, planner
- **Loop**: Loop 1 (Planning & Research)
- **Output**: Specs, plans, pre-mortems, architecture docs

**Princess-Dev** (Loop 2):
- **Responsibility**: Development and implementation coordination
- **Spawns**: coder, tester, reviewer, frontend-dev, backend-dev, debugger
- **Loop**: Loop 2 (Implementation)
- **Output**: Working code, tests, reviewed implementations

**Princess-Quality** (Loop 3):
- **Responsibility**: Quality assurance and validation coordination
- **Spawns**: theater-detector, nasa-enforcer, docs-writer, code-analyzer, security-manager
- **Loop**: Loop 3 (Quality & Finalization)
- **Output**: Audit reports, documentation, deployment approval

## Princess Spawning Workflow

Follow this systematic workflow to spawn a Princess agent:

### Phase 1: Context Preparation

Gather all necessary context before spawning:

**Actions**:
1. Read current loop from memory: `memory["current_loop"]`
2. Load Loop N context (if Loop 1 complete, load Loop 1 outputs)
3. Extract task description and type
4. Determine which Drones the Princess will need to spawn
5. Prepare full delegation prompt with context

**Context Template**:
```python
context = {
    "loop": memory["current_loop"],  # loop1/loop2/loop3
    "task_description": user_request,
    "loop1_outputs": memory.get("loop1", {}),  # Plans, specs, risks
    "loop2_outputs": memory.get("loop2", {}),  # Code changes, audits
    "route": memory.get("flow_route", "development"),  # development/debug
    "agents_needed": [],  # Will be determined by Princess
    "milestones": [],  # From Loop 1 plan (if exists)
}
```

### Phase 2: Princess Selection

Use the selection algorithm to choose the correct Princess:

**Actions**:
1. Identify current loop from memory
2. Analyze task keywords to confirm Princess choice
3. Select Princess using `get_princess_for_loop(loop)` from agent_registry
4. Verify Princess is appropriate for task type

**Selection Examples**:
```python
# Example 1: Loop 1 (Planning)
loop = "loop1"
princess = get_princess_for_loop(loop)  # Returns: "princess-coordination"

# Example 2: Loop 2 (Implementation)
loop = "loop2"
princess = get_princess_for_loop(loop)  # Returns: "princess-dev"

# Example 3: Loop 3 (Quality)
loop = "loop3"
princess = get_princess_for_loop(loop)  # Returns: "princess-quality"
```

### Phase 3: Delegation Prompt Construction

Build the Princess delegation prompt with complete context:

**Prompt Structure**:
```markdown
You are {PRINCESS_NAME}, the {RESPONSIBILITY} coordinator for the SPEK Platform.

TASK: {task_description}

CONTEXT:
- Current Loop: {loop}
- Route: {route} (development or debug)
- User Request: {user_request}

{IF LOOP 2 OR LOOP 3:}
LOOP 1 OUTPUTS:
- Plan: {plan_path}
- Research: {research_path}
- Risks: {risks_path}
- Phases: {phases}
- Milestones: {milestones}
- Agents Recommended: {agents_needed}

YOUR RESPONSIBILITIES:
1. Spawn Drones from agent registry based on task requirements
2. Coordinate {work_type} across {num_phases} phases
3. {LOOP_SPECIFIC_TASKS}
4. Escalate blockers to Queen (Claude Code)
5. Update memory with progress and results

DRONE SPAWNING:
Use the drone-selection skill to find best Drones:
- Analyze task requirements
- Use agent_registry.py intelligent selection
- Spawn Drones with specific, detailed instructions
- Coordinate Drone outputs into unified deliverables

{LOOP_SPECIFIC_INSTRUCTIONS}

DELIVERABLES:
{loop_specific_deliverables}

QUALITY STANDARDS:
{loop_specific_quality_standards}

ESCALATION PROTOCOL:
- If 3 Drone failures → Escalate to Queen
- If milestone not met → Escalate with context
- If blocked → Report blocker and wait for Queen decision

Begin {work_phase}."""
```

**Loop-Specific Instructions**:

**Loop 1 (Princess-Coordination)**:
```markdown
LOOP 1 SPECIFIC TASKS:
- Generate research document (/research/)
- Create implementation plan (/plans/)
- Produce pre-mortem analysis (/premortem/)
- Calculate risk score (target: <5000)
- Make GO/NO-GO recommendation

DELIVERABLES:
- Research: /research/{feature}-research.md (≥500 words, ≥3 citations)
- Plan: /plans/{feature}-plan.md (phases, milestones, file tree)
- Pre-mortem: /premortem/{feature}-risks.md (P0/P1/P2/P3 risks, risk score)

QUALITY STANDARDS:
- Research: Substantive, cited, actionable
- Plan: Clear phases, success criteria, rollback strategy
- Risks: <5000 score for GO, specific mitigations
```

**Loop 2 (Princess-Dev)**:
```markdown
LOOP 2 SPECIFIC TASKS:
- Implement per Loop 1 plan phases
- Run 3-part audit after each phase:
  * Functionality (tests pass, ≥80% coverage)
  * Style (NASA Rule 10, ≥96% compliance)
  * Theater (<60 score, no TODOs/mocks)
- Validate milestones from Loop 1 plan
- Coordinate TDD workflow (tests BEFORE code)

DELIVERABLES:
- Working, tested code (/src/)
- Comprehensive test suite (/tests/)
- Audit reports (functionality, style, theater)
- Updated files list in memory

QUALITY STANDARDS:
- All tests passing (zero failures)
- ≥80% code coverage (≥90% critical paths)
- ≥96% NASA compliance
- Zero TODO/FIXME comments
- Zero mock/placeholder implementations
```

**Loop 3 (Princess-Quality)**:
```markdown
LOOP 3 SPECIFIC TASKS:
- Run comprehensive quality validation (47-point checklist)
- Detect theater (TODOs, mocks, placeholders)
- Enforce NASA Rule 10 compliance
- Generate production documentation
- Make deployment recommendation (GO/NO-GO/ESCALATE)

DELIVERABLES:
- Quality audit report (/docs/)
- Documentation (README, API docs, guides)
- Deployment checklist
- GO/NO-GO decision with evidence

QUALITY STANDARDS:
- All 47 checklist items validated
- Zero theater detected
- 100% NASA compliance for critical paths
- Documentation complete and accurate
- Production-ready determination
```

### Phase 4: Princess Spawning

Spawn the Princess using the Task tool with the constructed prompt:

**Spawning Pattern**:
```python
# Build delegation prompt using template above
delegation_prompt = build_princess_delegation_prompt(
    princess_id=princess_id,
    context=context,
    loop=loop
)

# Spawn Princess agent
Task(
    subagent_type=princess_id,  # "princess-coordination", "princess-dev", or "princess-quality"
    description=f"Coordinate {loop} work",
    prompt=delegation_prompt
)
```

**Example: Spawning Princess-Dev** (Loop 2):
```python
Task(
    subagent_type="princess-dev",
    description="Coordinate user authentication implementation",
    prompt="""You are Princess-Dev, the Development Coordinator.

TASK: Implement user authentication with OAuth2

CONTEXT:
- Current Loop: loop2
- Route: development
- User Request: Build authentication system with OAuth2

LOOP 1 OUTPUTS:
- Plan: /plans/user-auth-plan.md
- Research: /research/user-auth-research.md
- Risks: /premortem/user-auth-risks.md
- Phases: 5 (Backend, Frontend, Tests, Security, Integration)
- Milestones: ["API routes defined", "Auth working", "Tests passing"]
- Agents Recommended: ["backend-dev", "tester", "security-manager"]

YOUR RESPONSIBILITIES:
1. Spawn Drones from agent registry (use drone-selection skill)
2. Coordinate implementation across 5 phases
3. Run 3-part audit after each phase (functionality, style, theater)
4. Validate milestones from Loop 1 plan
5. Escalate blockers to Queen

DRONE SPAWNING:
Use drone-selection skill to find best Drones for each task.
Spawn with specific instructions per phase.

Begin Phase 1: Backend implementation."""
)
```

### Phase 5: Monitor & Coordinate

After spawning, the Queen monitors Princess progress:

**Monitoring Actions**:
1. Track Princess status via memory updates
2. Handle Princess escalations (3 Drone failures, blockers, milestone failures)
3. Provide guidance when Princess requests Queen decision
4. Validate Princess deliverables before loop transition

**Escalation Handling**:
```python
# Princess reports escalation
if princess_escalation["type"] == "drone_failure":
    # 3 Drones failed to complete task
    analyze_failure_pattern(princess_escalation["context"])
    provide_guidance_or_replan()

elif princess_escalation["type"] == "milestone_not_met":
    # Loop 1 milestone not validated
    review_milestone(princess_escalation["milestone"])
    extend_timeline_or_adjust_scope()

elif princess_escalation["type"] == "blocked":
    # Princess cannot proceed
    unblock(princess_escalation["blocker"])
```

## Integration with Loop Skills

This skill is invoked by Loop 1, Loop 2, and Loop 3 skills at specific points:

### Loop 1 Integration

**When**: Phase 2 (Research Coordination)
**Princess**: princess-coordination
**Drones Spawned**: researcher, spec-writer, architect, planner
**Output**: Research docs, plans, pre-mortems

**Invocation Point in loop1-planning/skill.md**:
```markdown
### Phase 2: Research Coordination

**Spawn Princess-Coordination** to coordinate Loop 1 research and planning.

Use princess-summoning skill:
- Loop: loop1
- Task: Feature research and planning
- Princess: princess-coordination
```

### Loop 2 Integration

**When**: Phase 2 (Princess Selection & Delegation)
**Princess**: princess-dev
**Drones Spawned**: coder, tester, reviewer, frontend-dev, backend-dev
**Output**: Working code, tests, audit results

**Invocation Point in loop2-implementation/skill.md**:
```markdown
### Phase 2: Princess Selection & Delegation

**Spawn Princess-Dev** to coordinate Loop 2 implementation.

Use princess-summoning skill:
- Loop: loop2
- Task: Feature implementation
- Princess: princess-dev
- Context: Loop 1 plans, specs, risks
```

### Loop 3 Integration

**When**: Phase 2 (Quality Coordination)
**Princess**: princess-quality
**Drones Spawned**: theater-detector, nasa-enforcer, docs-writer, code-analyzer
**Output**: Quality reports, documentation, deployment decision

**Invocation Point in loop3-quality/skill.md**:
```markdown
### Phase 2: Quality Coordination

**Spawn Princess-Quality** to coordinate Loop 3 validation.

Use princess-summoning skill:
- Loop: loop3
- Task: Quality validation and documentation
- Princess: princess-quality
- Context: Loop 2 code changes, audit results
```

## Helper Scripts & Resources

### Scripts

**princess_selector.py** - Princess selection logic:
```python
from src.coordination.agent_registry import get_princess_for_loop

def select_princess_for_context(loop: str, task_type: str = None) -> str:
    """Select Princess based on loop and optional task type."""
    return get_princess_for_loop(loop)
```

**delegation_prompt_builder.py** - Build Princess delegation prompts:
```python
def build_princess_delegation_prompt(
    princess_id: str,
    context: dict,
    loop: str
) -> str:
    """Construct complete Princess delegation prompt with context."""
    # Load template for loop
    # Insert context variables
    # Return formatted prompt
    pass
```

### Diagrams

**princess-summoning-process.dot** - Visual workflow:
See [diagrams/princess-summoning-process.dot](diagrams/princess-summoning-process.dot)

## Error Handling

**If Princess spawn fails**:
1. Retry spawn (may be temporary issue)
2. If 2 failures, verify Princess exists in agent registry
3. If 3 failures, escalate to user with error context

**If Princess requests unknown Drone**:
1. Check agent_registry.py for Drone existence
2. If missing, suggest alternative Drone
3. Update Princess with available Drones

**If Princess escalates to Queen**:
1. Analyze escalation context
2. Provide guidance or make Queen-level decision
3. Update memory with resolution
4. Resume Princess work

## Success Criteria

Princess summoning is successful when:
- ✅ Correct Princess selected for loop/task
- ✅ Complete context provided to Princess
- ✅ Princess spawned successfully via Task tool
- ✅ Princess begins coordinating Drone work
- ✅ Memory updated with Princess status

**Quality Bar**:
- Princess receives ALL necessary context
- Delegation prompt is complete and specific
- Princess knows which Drones to spawn
- Escalation protocol is clear
- Deliverables are well-defined

## Related Skills

- **drone-selection**: Princess uses this to choose Drones
- **loop1-planning**: Invokes this for Princess-Coordination
- **loop2-implementation**: Invokes this for Princess-Dev
- **loop3-quality**: Invokes this for Princess-Quality

---

**Version**: 1.0.0
**Last Updated**: 2025-10-18
**Part of**: SPEK Platform 3-Loop Methodology
**Related Skills**: `drone-selection`, `loop1-planning`, `loop2-implementation`, `loop3-quality`
