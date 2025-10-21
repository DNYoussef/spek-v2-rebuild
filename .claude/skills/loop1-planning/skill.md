# Loop 1: Planning & Research

## Overview

Loop 1 is the SPEK Platform's planning and research phase that automatically coordinates research, planning, and pre-mortem risk analysis before any code is written. Use this skill when starting new features, major refactors, or investigating complex problems. This skill spawns specialized agents (`researcher`, `planner`, and creates pre-mortem analyses) to produce comprehensive specifications, implementation plans, and risk assessments that feed directly into Loop 2 (Implementation).

This skill represents the first phase of the 3-loop methodology: **Loop 1 (Planning) → Loop 2 (Implementation) → Loop 3 (Quality)**. It can also be triggered via the debug route when Loop 3 discovers issues: **Loop 3 (Quality) → Loop 1 (Replan) → Loop 2 (Fix)**.

## When to Use This Skill

Activate Loop 1 when:
- **Starting new features or projects**: User requests "build", "create", "implement" without existing plans
- **Complex problem investigation**: User requests "research", "analyze", "investigate" for architectural decisions
- **Debug route escalation**: Loop 3 Quality validation fails and requires replanning
- **Major refactoring**: Significant code changes need upfront planning and risk analysis
- **Architecture decisions**: Choosing between technologies, patterns, or approaches

**Auto-Trigger Patterns**:
- Keywords: "plan", "research", "investigate", "design", "spec", "architecture", "analyze", "study"
- Phrases: "I need to build...", "How should I implement...", "Research best practices for...", "Create a spec for..."
- Debug escalation: Loop 3 sends "ESCALATE_TO_LOOP1" with failure context

## Loop 1 Workflow Phases

Loop 1 follows a systematic 5-phase workflow that produces actionable outputs for Loop 2:

### Phase 1: Route Detection & Context Loading

**Determine which route triggered Loop 1**:
- **Development Route** (1→2→3): Starting fresh, no existing context
- **Debug Route** (3→1→2): Loop 3 escalation, load failure context from memory

**Actions**:
1. Check memory for `flow_route` value
2. If debug route, load Loop 3 escalation context:
   ```python
   # Read from memory
   escalation = memory["loop3"]["escalations"][-1]
   # Contains: failure_type, affected_files, error_logs, quality_scores
   ```
3. If development route, load user request directly
4. Set Loop 1 status to "in_progress" in memory

### Phase 2: Research Coordination

**Spawn Princess-Coordination** to coordinate Loop 1 research and planning.

**Use princess-summoning skill**:
The princess-summoning skill handles Princess selection and spawning. Princess-Coordination will then use the drone-selection skill to find and spawn appropriate Drones.

```markdown
# Invoke princess-summoning skill
Use princess-summoning skill:
- Loop: loop1
- Task: {feature_name} research and planning
- Princess: princess-coordination (automatically selected for loop1)
- Context: User request, route (development/debug)

Princess-Coordination will then:
1. Use drone-selection skill to find best Drones
2. Spawn researcher, spec-writer, architect as needed
3. Coordinate their outputs into unified deliverables
```

**Alternative: Direct Drone spawning** (if Princess delegation not needed):

**Use agent_registry.py intelligent selection**:
```python
from src.coordination.agent_registry import find_drones_for_task

# Example: User says "build a REST API with OAuth2"
task_description = "research REST API best practices and OAuth2 implementation"
loop = "loop1"

# Get recommended Drones
drones = find_drones_for_task(task_description, loop)
# Returns: ["researcher", "architect", "spec-writer"]
```

**Spawn researcher using Task tool**:
```
Task(
  subagent_type="researcher",
  description="Research task",
  prompt=f"""You are the Researcher Drone for the SPEK Platform.

TASK: {task_description}

CONTEXT:
- Loop: Loop 1 (Planning & Research)
- Route: {route} (development or debug)
- User request: {user_request}
{f"- Loop 3 escalation: {escalation_context}" if debug_route else ""}

DELIVERABLES:
1. Research document: /research/[feature]-research.md
   - Best practices
   - Technology comparisons
   - Implementation patterns
   - Known pitfalls

2. Key findings summary (return to Queen)

CONSTRAINTS:
- Use existing project knowledge in /research/ folder
- Cite sources (URLs, documentation references)
- Focus on actionable insights for implementation
- Time limit: 15 minutes research

Return your findings as structured markdown."""
)
```

**Researcher Output**:
- Research document saved to `/research/`
- Summary returned to Queen (Claude Code)
- Key findings stored in memory for next phases

### Phase 3: Planning Coordination

**Spawn the `planner` agent** to create implementation timeline and strategy.

**Spawn planner using Task tool**:
```
Task(
  subagent_type="planner",
  description="Create implementation plan",
  prompt=f"""You are the Planner Drone for the SPEK Platform.

TASK: Create detailed implementation plan for: {feature_name}

CONTEXT:
- Research findings: {research_summary}
- Project structure: {project_structure}
- Existing codebase: {codebase_summary}

DELIVERABLES:
1. Implementation plan: /plans/[feature]-plan.md
   Format:
   - **Objective**: What we're building
   - **Phases**: Break into 3-5 phases
   - **Dependencies**: What must exist first
   - **Timeline**: Estimated effort per phase
   - **Milestones**: Checkpoints for Loop 3 validation
   - **Success Criteria**: How we know it's done

2. File tree: Which files will be created/modified
3. Agent assignments: Which agents (Drones) needed for Loop 2

CONSTRAINTS:
- Follow NASA Rule 10 (≤60 LOC per function)
- Plan for test-driven development (tests before code)
- Include rollback strategy for each phase
- Time limit: 10 minutes planning

Return plan as structured markdown."""
)
```

**Planner Output**:
- Implementation plan saved to `/plans/`
- File tree and agent assignments
- Timeline with milestones

### Phase 4: Pre-Mortem Risk Analysis

**Generate pre-mortem analysis** to identify risks before implementation begins.

**Create pre-mortem document**:
```
Task(
  subagent_type="researcher",  # Reuse researcher for risk analysis
  description="Pre-mortem risk analysis",
  prompt=f"""You are conducting a Pre-Mortem Risk Analysis for the SPEK Platform.

TASK: Identify risks for: {feature_name}

CONTEXT:
- Implementation plan: {plan_summary}
- Research findings: {research_summary}
- Historical failures: {load_previous_premortems()}

DELIVERABLES:
1. Pre-mortem document: /premortem/[feature]-risks.md
   Format:
   - **P0 Risks** (project-killers, must address)
   - **P1 Risks** (major blockers, should address)
   - **P2 Risks** (minor issues, monitor)
   - **P3 Risks** (low priority, accept)

   For each risk:
   - Risk description
   - Probability (high/medium/low)
   - Impact (critical/high/medium/low)
   - Mitigation strategy
   - Owner (which agent handles this)

2. Risk score calculation:
   ```
   Total Risk = Σ(probability × impact × weight)
   Where: P0=1000, P1=100, P2=10, P3=1
   ```

3. GO/NO-GO recommendation:
   - GO: Total risk <2000
   - CAUTION: 2000-5000
   - NO-GO: >5000 (needs replanning)

CONSTRAINTS:
- Reference historical failures from /premortem/ folder
- Be specific (not generic risks)
- Provide actionable mitigations
- Time limit: 10 minutes analysis

Return pre-mortem as structured markdown."""
)
```

**Pre-Mortem Output**:
- Risk document saved to `/premortem/`
- Risk score and GO/NO-GO decision
- Mitigation strategies for Loop 2

### Phase 5: Loop 1 Completion & Handoff to Loop 2

**Validate Loop 1 outputs** before transitioning to Loop 2.

**Quality Gates**:
1. ✅ Research document exists (`/research/[feature]-research.md`)
2. ✅ Implementation plan exists (`/plans/[feature]-plan.md`)
3. ✅ Pre-mortem analysis exists (`/premortem/[feature]-risks.md`)
4. ✅ Risk score <5000 (GO or CAUTION acceptable)
5. ✅ All deliverables in proper directories (not root folder)

**Memory State Update**:
```python
memory["loop1"] = {
    "feature_name": feature_name,
    "specs": [f"/research/{feature_name}-research.md"],
    "plans": [f"/plans/{feature_name}-plan.md"],
    "risks": [f"/premortem/{feature_name}-risks.md"],
    "risk_score": calculated_risk_score,
    "go_decision": "GO" | "CAUTION" | "NO-GO",
    "agents_needed_for_loop2": ["coder", "tester", "reviewer"],
    "status": "complete",
    "completed_at": timestamp,
    "route": "development" | "debug"
}

memory["current_loop"] = "loop2"  # Transition
memory["flow_route"] = "development" | "debug"
```

**Handoff to Loop 2**:
```
Task(
  subagent_type="general-purpose",  # Special transition agent
  description="Transition to Loop 2",
  prompt=f"""Loop 1 (Planning) is complete. Transition to Loop 2 (Implementation).

LOOP 1 OUTPUTS:
- Research: {research_path}
- Plan: {plan_path}
- Pre-mortem: {premortem_path}
- Risk Score: {risk_score}
- Decision: {go_decision}

NEXT STEPS:
1. Activate Loop 2 (Implementation) skill
2. Pass Loop 1 context via memory
3. Queen will read plans and spawn Princesses

MEMORY CONTEXT:
{json.dumps(memory["loop1"], indent=2)}

The Loop 2 skill will now take over."""
)
```

**User Notification**:
```
✅ Loop 1 (Planning) Complete

📋 Deliverables:
- Research: /research/{feature_name}-research.md
- Plan: /plans/{feature_name}-plan.md
- Risks: /premortem/{feature_name}-risks.md

📊 Risk Assessment:
- Total Risk Score: {risk_score}
- Decision: {go_decision}
- P0 Risks: {p0_count}
- P1 Risks: {p1_count}

➡️  Next: Loop 2 (Implementation) will begin automatically
```

## Agent Registry Integration

Loop 1 uses these agents from `agent_registry.py`:

**Princess (Coordinator)**:
- `princess-coordination`: Research coordinator (spawns Loop 1 Drones)

**Drones (Workers)**:
- `researcher`: Investigates problem domains, gathers information
- `planner`: Creates implementation plans and timelines
- `spec-writer`: Writes technical specifications
- `architect`: Designs system architecture
- `pseudocode-writer`: Creates algorithm designs

**Selection Logic**:
```python
# Princess-Coordination automatically selected for loop1
princess = get_princess_for_loop("loop1")  # Returns "princess-coordination"

# Intelligent Drone selection based on task
task = "Design a microservices architecture for user management"
drones = find_drones_for_task(task, "loop1")
# Returns: ["architect", "spec-writer", "researcher"]
```

## Memory Integration

Loop 1 persists state for Loop 2 and Loop 3 consumption.

**Write to Memory**:
```python
# Store Loop 1 outputs
memory["loop1"] = {
    "feature_name": "user-authentication",
    "specs": ["/research/user-authentication-research.md"],
    "plans": ["/plans/user-authentication-plan.md"],
    "risks": ["/premortem/user-authentication-risks.md"],
    "research": {
        "key_findings": [...],
        "technology_choice": "OAuth2 + JWT",
        "best_practices": [...]
    },
    "plan": {
        "phases": 5,
        "estimated_effort": "3 weeks",
        "agents_needed": ["coder", "tester", "security-manager"]
    },
    "risk_score": 1650,
    "go_decision": "GO",
    "status": "complete"
}
```

**Read from Memory** (Loop 2 access):
```python
# Loop 2 reads Loop 1 context
loop1_context = memory["loop1"]
research_path = loop1_context["specs"][0]
plan_path = loop1_context["plans"][0]
agents_needed = loop1_context["plan"]["agents_needed"]
```

## Debug Route (Loop 3 → Loop 1 Escalation)

When Loop 3 Quality validation fails, it escalates to Loop 1 for replanning.

**Trigger**: Loop 3 sends `ESCALATE_TO_LOOP1` signal with failure context.

**Loop 3 Escalation Format**:
```python
memory["loop3"]["escalations"].append({
    "timestamp": "2025-10-17T14:30:00Z",
    "failure_type": "security_vulnerability",
    "severity": "P0",
    "affected_files": ["src/auth.py", "src/tokens.py"],
    "error_logs": ["SQL injection risk in line 42"],
    "quality_scores": {
        "functionality": 0.85,
        "style": 0.92,
        "theater": 0.98,
        "security": 0.32  # FAILED
    },
    "recommendation": "Replan authentication strategy, research parameterized queries"
})
```

**Loop 1 Debug Route Actions**:
1. Load escalation context from memory
2. Spawn `researcher` to investigate root cause
3. Spawn `planner` to create fix strategy
4. Generate updated pre-mortem (regression risks)
5. Transition to Loop 2 with fix plan

**Debug Route Output**:
- `/research/{feature}-fix-research.md`
- `/plans/{feature}-fix-plan.md`
- `/premortem/{feature}-fix-risks.md`

## Helper Scripts & Resources

Loop 1 includes bundled resources for deterministic execution:

**Scripts** (`.claude/skills/loop1-planning/scripts/`):
- `research_coordinator.py`: Spawns researcher with proper context
- `premortem_generator.py`: Calculates risk scores and GO/NO-GO decisions
- `loop1_memory.py`: Memory persistence helpers

**Templates** (`.claude/skills/loop1-planning/templates/`):
- `spec_template.md`: Research document structure
- `plan_template.md`: Implementation plan structure
- `premortem_template.md`: Risk analysis structure

**Diagrams** (`.claude/skills/loop1-planning/diagrams/`):
- `loop1-planning-process.dot`: Visual workflow (GraphViz)

**Usage Example**:
```python
# Use helper script for pre-mortem
from scripts.premortem_generator import calculate_risk_score

risks = [
    {"severity": "P0", "probability": 0.3, "impact": "critical"},
    {"severity": "P1", "probability": 0.5, "impact": "high"},
]

score, decision = calculate_risk_score(risks)
# Returns: (1650, "GO")
```

## Quality Standards

Loop 1 outputs must meet these standards before Loop 2 begins:

**Research Document**:
- ✅ Minimum 500 words (substantive research)
- ✅ At least 3 cited sources (URLs, docs)
- ✅ Technology comparison table (if applicable)
- ✅ Best practices section
- ✅ Known pitfalls section

**Implementation Plan**:
- ✅ Clear objective statement
- ✅ 3-5 phases with milestones
- ✅ File tree (files to create/modify)
- ✅ Agent assignments for Loop 2
- ✅ Success criteria (how we know it's done)
- ✅ Rollback strategy per phase

**Pre-Mortem Analysis**:
- ✅ At least 5 identified risks
- ✅ Risks categorized (P0/P1/P2/P3)
- ✅ Each risk has mitigation strategy
- ✅ Risk score calculation shown
- ✅ GO/NO-GO recommendation
- ✅ Risk score <5000 for GO

**File Organization**:
- ✅ Research docs in `/research/` (NOT root)
- ✅ Plans in `/plans/` (NOT root)
- ✅ Pre-mortems in `/premortem/` (NOT root)
- ✅ Consistent naming: `[feature]-[type].md`

## Error Handling & Escalation

**If Research Fails**:
1. Retry with more specific task description
2. If 3 failures, escalate to user: "Need more context for research: [question]"

**If Planning Fails**:
1. Check if research completed successfully
2. If research incomplete, restart from Phase 2
3. If 3 failures, escalate to user with gap analysis

**If Risk Score >5000** (NO-GO):
1. Present risks to user
2. Ask: "Continue anyway?" or "Revise approach?"
3. If revise, restart Loop 1 with new constraints
4. If continue, warn user and proceed to Loop 2

**If Memory Write Fails**:
1. Retry memory write operation
2. If persistent failure, save context to `/tmp/loop1-backup.json`
3. Warn user: "Memory system unavailable, context saved locally"

## Success Criteria

Loop 1 is considered successful when:
- ✅ All 3 deliverables created (research, plan, pre-mortem)
- ✅ Risk score <5000 (GO or CAUTION)
- ✅ Files in proper directories
- ✅ Memory state updated with Loop 1 context
- ✅ User notified of completion
- ✅ Loop 2 transition initiated

**Time Budget**:
- Research: 15 minutes
- Planning: 10 minutes
- Pre-mortem: 10 minutes
- Total: ~35 minutes for Loop 1

If any phase exceeds budget, warn user and ask to continue or abort.

## Integration with Flow Orchestrator

Loop 1 is part of the bidirectional flow system:

**Development Route (Normal)**:
```
User Request → Loop 1 (Planning) → Loop 2 (Implementation) → Loop 3 (Quality) → Done
```

**Debug Route (Failure)**:
```
Loop 3 (Failed) → Loop 1 (Replan) → Loop 2 (Fix) → Loop 3 (Revalidate) → Done
```

The Flow Orchestrator skill manages routing between loops based on:
- User intent (new feature vs bug fix)
- Loop 3 escalation signals
- Memory state (`current_loop`, `flow_route`)

See `flow-orchestrator` skill for complete routing logic.

## Appendix: Agent Spawning Patterns

**Pattern 1: Simple Research**
```
Task(subagent_type="researcher", description="Research X", prompt="...")
```

**Pattern 2: Parallel Research & Architecture**
```
# Spawn both agents in parallel (single message, multiple Task calls)
Task(subagent_type="researcher", description="Research", prompt="...")
Task(subagent_type="architect", description="Design", prompt="...")
```

**Pattern 3: Sequential with Dependencies**
```
# Step 1: Research first
researcher_output = Task(subagent_type="researcher", ...)

# Step 2: Use research output in planning
planner_output = Task(
    subagent_type="planner",
    prompt=f"Using research: {researcher_output}..."
)
```

**Pattern 4: Princess Coordination** (Recommended)
```
# Use princess-summoning skill to spawn Princess-Coordination
# Princess will use drone-selection skill to find and spawn best Drones

Task(
    subagent_type="princess-coordination",
    description="Coordinate Loop 1",
    prompt=f"""You are Princess-Coordination.

    TASK: {feature_name} research and planning

    Use drone-selection skill to find best Drones for Loop 1:
    - researcher (investigate {topic})
    - spec-writer (document requirements)
    - architect (design system)
    - planner (create implementation plan)

    Coordinate their outputs into unified deliverables:
    - Research: /research/{feature}-research.md
    - Plan: /plans/{feature}-plan.md
    - Pre-mortem: /premortem/{feature}-risks.md"""
)
```

---

**Version**: 1.1.0
**Last Updated**: 2025-10-18
**Part of**: SPEK Platform 3-Loop Methodology
**Related Skills**: `princess-summoning`, `drone-selection`, `loop2-implementation`, `loop3-quality`, `flow-orchestrator`
