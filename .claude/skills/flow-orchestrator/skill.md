# Flow Orchestrator: 3-Loop Bidirectional Routing System

## Overview

The Flow Orchestrator is the master coordination skill that manages bidirectional routing between Loop 1 (Planning), Loop 2 (Implementation), and Loop 3 (Quality). It enables both the **Development Route** (1→2→3) for new features and the **Debug Route** (3→1→2) for failures, creating a self-healing system that automatically replans and fixes issues.

This skill acts as the "traffic controller" for the SPEK Platform's 3-loop methodology, ensuring smooth transitions between phases, managing escalations, and maintaining system state across loops.

## When to Use This Skill

The Flow Orchestrator **auto-activates** at key transition points:
- **Session start**: Determines which loop to enter based on memory state
- **Loop transitions**: Manages 1→2, 2→3, 3→production handoffs
- **Escalations**: Routes 3→1 when quality validation fails
- **User requests**: Analyzes intent and routes to appropriate loop

**Auto-Trigger Patterns**:
- **Always active**: Flow Orchestrator monitors all activity
- **Explicit invocation**: User says "start development cycle", "run full workflow"
- **Memory-based**: Reads `memory["current_loop"]` to determine state
- **Escalation signals**: Loop 3 sends `ESCALATE_TO_LOOP1` event

## Bidirectional Flow Architecture

The Flow Orchestrator manages two routes through the 3-loop system:

### Development Route (Normal Flow: 1→2→3)

**Purpose**: New features, major refactors, greenfield development

**Flow**:
```
User Request
    ↓
Loop 1 (Planning)
    ├─ Research
    ├─ Planning
    └─ Pre-mortem
    ↓
Loop 2 (Implementation)
    ├─ Queen → Princess → Drones
    ├─ Continuous 3-part audit
    └─ Milestone validation
    ↓
Loop 3 (Quality)
    ├─ Comprehensive audits
    ├─ 47-point quality gate
    └─ GO/NO-GO decision
    ↓
Production (if GO) OR Debug Route (if NO-GO)
```

### Debug Route (Failure Recovery: 3→1→2→3)

**Purpose**: Quality failures, critical issues, production bugs

**Flow**:
```
Loop 3 Quality Failure
    ↓
Loop 1 (Replanning)
    ├─ Root cause research
    ├─ Fix strategy planning
    └─ Regression risk analysis
    ↓
Loop 2 (Fix Implementation)
    ├─ Targeted fix (not full feature)
    ├─ Regression testing focus
    └─ 3-part audit
    ↓
Loop 3 (Revalidation)
    ├─ Verify fix works
    ├─ No new issues introduced
    └─ GO/NO-GO decision
    ↓
Production (if GO) OR Repeat Debug Route (if still NO-GO)
```

## Flow Orchestrator State Machine

The orchestrator tracks system state using a finite state machine:

### States

1. **IDLE**: No active loop, awaiting user request
2. **LOOP1_ACTIVE**: Planning phase in progress
3. **LOOP2_ACTIVE**: Implementation phase in progress
4. **LOOP3_ACTIVE**: Quality validation in progress
5. **ESCALATED**: Loop 3 → Loop 1 transition (debug route)
6. **PRODUCTION**: All loops complete, deployment approved
7. **FAILED**: Unrecoverable failure (manual intervention required)

### Transitions

```
IDLE → LOOP1_ACTIVE
    Trigger: User request detected
    Action: Activate loop1-planning skill

LOOP1_ACTIVE → LOOP2_ACTIVE
    Trigger: Loop 1 status = "complete", GO decision
    Action: Activate loop2-implementation skill

LOOP2_ACTIVE → LOOP3_ACTIVE
    Trigger: Loop 2 status = "complete", all audits passed
    Action: Activate loop3-quality skill

LOOP3_ACTIVE → PRODUCTION
    Trigger: Quality score = 1.0, GO decision
    Action: Approve deployment

LOOP3_ACTIVE → ESCALATED
    Trigger: Quality score <0.95, NO-GO decision, P0 failures
    Action: Escalate to Loop 1 (debug route)

ESCALATED → LOOP1_ACTIVE
    Trigger: Escalation signal received
    Action: Activate loop1-planning with failure context

LOOP1_ACTIVE → LOOP2_ACTIVE (debug route)
    Trigger: Fix plan complete
    Action: Activate loop2-implementation with fix context

LOOP2_ACTIVE → LOOP3_ACTIVE (debug route)
    Trigger: Fix complete
    Action: Activate loop3-quality for revalidation

LOOP3_ACTIVE → ESCALATED (repeated failure)
    Trigger: Revalidation failed again
    Action: Re-escalate to Loop 1 (or FAILED state if 3x)

* → FAILED
    Trigger: 3 consecutive debug cycles failed
    Action: Request manual intervention
```

### State Machine Implementation

```python
class FlowOrchestratorFSM:
    """Manages 3-loop bidirectional flow."""

    states = ["IDLE", "LOOP1_ACTIVE", "LOOP2_ACTIVE", "LOOP3_ACTIVE",
              "ESCALATED", "PRODUCTION", "FAILED"]

    def __init__(self):
        self.current_state = "IDLE"
        self.route = "development"  # or "debug"
        self.escalation_count = 0

    def transition(self, event: str, context: dict):
        """Handle state transitions."""
        if self.current_state == "IDLE" and event == "USER_REQUEST":
            return self._start_loop1(context)

        elif self.current_state == "LOOP1_ACTIVE" and event == "LOOP1_COMPLETE":
            return self._start_loop2(context)

        elif self.current_state == "LOOP2_ACTIVE" and event == "LOOP2_COMPLETE":
            return self._start_loop3(context)

        elif self.current_state == "LOOP3_ACTIVE" and event == "QUALITY_GO":
            return self._approve_production(context)

        elif self.current_state == "LOOP3_ACTIVE" and event == "QUALITY_NO_GO":
            return self._escalate_to_loop1(context)

        elif self.current_state == "ESCALATED" and event == "ESCALATION_HANDLED":
            return self._restart_loop1_debug(context)

        else:
            raise InvalidTransitionError(f"{self.current_state} → {event}")

    def _start_loop1(self, context):
        self.current_state = "LOOP1_ACTIVE"
        self.route = "development"
        activate_skill("loop1-planning", context)

    def _escalate_to_loop1(self, context):
        self.escalation_count += 1

        if self.escalation_count >= 3:
            self.current_state = "FAILED"
            request_manual_intervention(context)
        else:
            self.current_state = "ESCALATED"
            self.route = "debug"
            activate_skill("loop1-planning", context, route="debug")
```

## Flow Orchestrator Workflow

### Phase 1: Session Initialization

**Actions on every Claude Code session start**:

1. **Read memory state**:
   ```python
   current_loop = memory.get("current_loop", "idle")
   flow_route = memory.get("flow_route", "development")
   escalation_count = memory.get("escalation_count", 0)
   ```

2. **Determine resumption point**:
   ```python
   if current_loop == "loop1":
       print("Resuming Loop 1 (Planning)...")
       activate_skill("loop1-planning")
   elif current_loop == "loop2":
       print("Resuming Loop 2 (Implementation)...")
       activate_skill("loop2-implementation")
   elif current_loop == "loop3":
       print("Resuming Loop 3 (Quality)...")
       activate_skill("loop3-quality")
   elif current_loop == "production":
       print("✅ System in production state")
   else:
       print("Awaiting user request...")
       set_state("IDLE")
   ```

3. **Validate memory integrity**:
   ```python
   # Ensure memory structure exists
   if "loop1" not in memory:
       memory["loop1"] = {}
   if "loop2" not in memory:
       memory["loop2"] = {}
   if "loop3" not in memory:
       memory["loop3"] = {"escalations": []}
   ```

### Phase 2: User Request Routing

**When user makes a request, analyze intent and route to appropriate loop**:

```python
def route_user_request(user_message: str) -> str:
    """Determine which loop to activate."""

    # Check memory for active loop
    current_loop = memory.get("current_loop", "idle")
    if current_loop != "idle":
        # Continue current loop
        return current_loop

    # Analyze user intent
    intent = analyze_intent(user_message)

    # Route based on keywords
    planning_keywords = ["plan", "research", "design", "spec", "architecture"]
    implementation_keywords = ["implement", "code", "build", "create", "write", "fix"]
    quality_keywords = ["test", "audit", "review", "validate", "deploy"]

    if any(kw in intent["keywords"] for kw in planning_keywords):
        return "loop1"
    elif any(kw in intent["keywords"] for kw in implementation_keywords):
        # Check if plan exists
        if memory.get("loop1", {}).get("status") == "complete":
            return "loop2"  # Has plan, implement
        else:
            return "loop1"  # No plan, start with planning
    elif any(kw in intent["keywords"] for kw in quality_keywords):
        return "loop3"
    else:
        # Default: start with planning
        return "loop1"
```

**Example Routing**:
- "Build a REST API" → Loop 1 (no plan exists)
- "Implement the auth API" (plan exists) → Loop 2
- "Fix bug in auth.py" → Loop 2 (targeted fix)
- "Deploy to production" → Loop 3 (quality gate)
- "Test the new feature" → Loop 3

### Phase 3: Loop Transition Management

**Manage transitions between loops**:

#### Transition: Loop 1 → Loop 2

```python
def transition_loop1_to_loop2():
    """Handoff from planning to implementation."""

    # Verify Loop 1 completion
    loop1 = memory["loop1"]
    assert loop1["status"] == "complete", "Loop 1 not complete"
    assert loop1["go_decision"] in ["GO", "CAUTION"], "NO-GO decision"

    # Update memory
    memory["current_loop"] = "loop2"
    memory["flow_route"] = memory.get("flow_route", "development")

    # Notify user
    print(f"""
    ✅ Loop 1 (Planning) Complete → Loop 2 (Implementation)

    📋 Planning Outputs:
    - Research: {loop1['specs'][0]}
    - Plan: {loop1['plans'][0]}
    - Risks: {loop1['risks'][0]}
    - Risk Score: {loop1['risk_score']}

    ➡️  Activating Loop 2 (Implementation)...
    """)

    # Activate Loop 2
    activate_skill("loop2-implementation")
```

#### Transition: Loop 2 → Loop 3

```python
def transition_loop2_to_loop3():
    """Handoff from implementation to quality."""

    # Verify Loop 2 completion
    loop2 = memory["loop2"]
    assert loop2["status"] == "complete", "Loop 2 not complete"
    assert loop2["audit_results"]["functionality"] == "pass"
    assert loop2["audit_results"]["style"] == "pass"
    assert loop2["audit_results"]["theater"] == "pass"

    # Update memory
    memory["current_loop"] = "loop3"

    # Notify user
    print(f"""
    ✅ Loop 2 (Implementation) Complete → Loop 3 (Quality)

    📝 Implementation Outputs:
    - Files changed: {len(loop2['files_changed'])}
    - Agents used: {', '.join(loop2['agents_spawned'])}
    - Audits: All passed ✅

    ➡️  Activating Loop 3 (Quality Validation)...
    """)

    # Activate Loop 3
    activate_skill("loop3-quality")
```

#### Transition: Loop 3 → Production (GO)

```python
def transition_loop3_to_production():
    """Approve production deployment."""

    # Verify Loop 3 completion
    loop3 = memory["loop3"]
    assert loop3["quality_score"] >= 0.95, "Quality score too low"
    assert loop3["decision"] in ["GO", "CAUTION"], "NO-GO decision"
    assert loop3["deployment_approved"], "Deployment not approved"

    # Update memory
    memory["current_loop"] = "production"
    memory["production_deployed_at"] = timestamp()

    # Notify user
    print(f"""
    ✅ Loop 3 (Quality) Complete → Production Approved

    📊 Quality Score: {loop3['quality_score']} ({loop3['passed_checks']}/{loop3['total_checks']})
    ✅ Decision: {loop3['decision']}

    🚀 Ready for production deployment!
    """)

    # Return to IDLE (workflow complete)
    reset_state()
```

#### Transition: Loop 3 → Loop 1 (Escalation / Debug Route)

```python
def transition_loop3_to_loop1_escalation():
    """Escalate quality failure to replanning."""

    # Verify escalation is warranted
    loop3 = memory["loop3"]
    assert loop3["decision"] == "NO-GO", "Not a NO-GO decision"

    # Increment escalation count
    escalation_count = memory.get("escalation_count", 0) + 1
    memory["escalation_count"] = escalation_count

    # Check for repeated failures
    if escalation_count >= 3:
        print(f"""
        ❌ CRITICAL: 3 consecutive quality failures

        Manual intervention required. System entering FAILED state.
        """)
        memory["current_loop"] = "failed"
        request_manual_intervention()
        return

    # Get escalation context
    escalation = loop3["escalations"][-1]

    # Update memory for debug route
    memory["current_loop"] = "loop1"
    memory["flow_route"] = "debug"

    # Notify user
    print(f"""
    ❌ Loop 3 Quality Validation Failed → Escalating to Loop 1

    🚨 Failure Type: {escalation['failure_type']}
    🎯 Severity: {escalation['severity']}
    📉 Quality Score: {loop3['quality_score']} (target: 1.0)

    🔄 Debug Route Initiated:
    Loop 3 → Loop 1 (Replan) → Loop 2 (Fix) → Loop 3 (Revalidate)

    ➡️  Activating Loop 1 in debug mode...
    """)

    # Activate Loop 1 with escalation context
    activate_skill("loop1-planning", route="debug", escalation=escalation)
```

### Phase 4: Debug Route Management

**Handle the debug route cycle**:

```python
def manage_debug_route():
    """Coordinate debug route: Loop 3 → Loop 1 → Loop 2 → Loop 3."""

    route = memory.get("flow_route")
    assert route == "debug", "Not in debug route"

    current_loop = memory["current_loop"]

    if current_loop == "loop1":
        # Loop 1 creates fix plan
        print("Loop 1 (Debug): Creating fix plan...")
        # Wait for Loop 1 completion
        # Then transition to Loop 2

    elif current_loop == "loop2":
        # Loop 2 implements fix
        print("Loop 2 (Debug): Implementing fix...")
        # Targeted fix, not full feature
        # Wait for Loop 2 completion
        # Then transition to Loop 3

    elif current_loop == "loop3":
        # Loop 3 revalidates
        print("Loop 3 (Debug): Revalidating fix...")
        # Extra focus on:
        # - Original issue fixed?
        # - No new issues introduced?
        # - Regression testing passed?

        result = revalidate_fix()

        if result["decision"] == "GO":
            print("✅ Fix validated, returning to production flow")
            memory["flow_route"] = "development"
            transition_loop3_to_production()
        else:
            print("❌ Fix still failing, re-escalating...")
            transition_loop3_to_loop1_escalation()
```

### Phase 5: Memory State Management

**Maintain consistent memory state across loops**:

```python
def update_memory_state(loop_name: str, status: str, data: dict):
    """Update memory for a specific loop."""

    memory[loop_name]["status"] = status
    memory[loop_name].update(data)

    # Update global state
    memory["current_loop"] = determine_next_loop(loop_name, status)
    memory["last_updated"] = timestamp()

    # Persist to disk
    save_memory_to_disk(memory)
```

**Memory Schema** (complete):
```python
{
    # Global state
    "current_loop": "loop1 | loop2 | loop3 | production | failed",
    "flow_route": "development | debug",
    "escalation_count": 0,
    "last_updated": "2025-10-17T14:30:00Z",

    # Loop 1 state
    "loop1": {
        "feature_name": "user-authentication",
        "specs": ["/research/user-auth-research.md"],
        "plans": ["/plans/user-auth-plan.md"],
        "risks": ["/premortem/user-auth-risks.md"],
        "risk_score": 1650,
        "go_decision": "GO",
        "status": "complete",
        "completed_at": "2025-10-17T14:30:00Z"
    },

    # Loop 2 state
    "loop2": {
        "feature_name": "user-authentication",
        "files_changed": [...],
        "agents_spawned": [...],
        "audit_results": {...},
        "completed_milestones": [...],
        "status": "complete",
        "completed_at": "2025-10-17T15:00:00Z"
    },

    # Loop 3 state
    "loop3": {
        "quality_score": 1.0,
        "decision": "GO",
        "passed_checks": 47,
        "total_checks": 47,
        "escalations": [],  # List of escalations (if any)
        "deployment_approved": True,
        "status": "complete",
        "completed_at": "2025-10-17T15:30:00Z"
    },

    # Production state
    "production_deployed_at": "2025-10-17T16:00:00Z"
}
```

### Phase 6: Escalation Handling

**Detailed escalation workflow**:

```python
def handle_escalation(escalation: dict):
    """Process Loop 3 → Loop 1 escalation."""

    # Validate escalation
    required_fields = ["failure_type", "severity", "affected_files",
                      "quality_scores", "recommendation"]
    for field in required_fields:
        assert field in escalation, f"Missing field: {field}"

    # Store escalation
    memory["loop3"]["escalations"].append(escalation)

    # Analyze severity
    if escalation["severity"] == "P0":
        # Critical, escalate immediately
        print(f"🚨 P0 ESCALATION: {escalation['failure_type']}")
        transition_loop3_to_loop1_escalation()

    elif escalation["severity"] == "P1":
        # High priority, ask user
        user_choice = ask_user(f"""
        ⚠️  P1 Issue Detected: {escalation['failure_type']}

        [1] Escalate to Loop 1 (replan)
        [2] Attempt rewrites in Loop 3
        [3] Accept risk and deploy anyway

        Your choice: """)

        if user_choice == 1:
            transition_loop3_to_loop1_escalation()
        elif user_choice == 2:
            coordinate_rewrites_in_loop3(escalation)
        else:
            accept_risk_and_deploy(escalation)

    else:
        # P2/P3, coordinate rewrites
        print(f"ℹ️  Non-critical issue, coordinating rewrites...")
        coordinate_rewrites_in_loop3(escalation)
```

## Helper Scripts & Resources

Flow Orchestrator includes bundled resources:

**Scripts** (`.claude/skills/flow-orchestrator/scripts/`):
- `flow_manager.py`: Core FSM implementation
- `memory_manager.py`: Memory state persistence
- `transition_coordinator.py`: Loop transition logic
- `escalation_handler.py`: Escalation workflow
- `route_analyzer.py`: User intent routing

**Diagrams** (`.claude/skills/flow-orchestrator/diagrams/`):
- `bidirectional-flow.dot`: Development + Debug routes
- `state-machine.dot`: FSM states and transitions
- `escalation-workflow.dot`: Escalation handling

**Usage Example**:
```python
from scripts.flow_manager import FlowOrchestrator

orchestrator = FlowOrchestrator()

# User makes request
orchestrator.handle_user_request("Build a REST API")
# Routes to Loop 1

# Loop 1 completes
orchestrator.handle_event("LOOP1_COMPLETE")
# Transitions to Loop 2

# Loop 2 completes
orchestrator.handle_event("LOOP2_COMPLETE")
# Transitions to Loop 3

# Loop 3 quality check
orchestrator.handle_event("QUALITY_GO")
# Transitions to Production
```

## Error Handling

**If transition fails**:
1. Log error to memory
2. Attempt rollback to previous state
3. If rollback fails, enter FAILED state
4. Request manual intervention

**If memory corruption detected**:
1. Attempt recovery from backup
2. If no backup, rebuild from loop outputs (files in /research, /plans, etc.)
3. If unrecoverable, request user to restart workflow

**If 3 consecutive debug cycles fail**:
1. Enter FAILED state
2. Generate comprehensive failure report
3. Suggest manual code review
4. Offer to start fresh (discard current work)

## Success Criteria

Flow Orchestrator is successful when:
- ✅ Seamless transitions between loops
- ✅ No transition failures
- ✅ Memory state always consistent
- ✅ Debug route recovers from failures
- ✅ User always informed of current state
- ✅ Escalations handled appropriately

**Performance Targets**:
- Transition overhead: <5 seconds
- Memory state updates: <1 second
- Route determination: <100ms
- State machine transitions: <50ms

## Integration with Other Skills

Flow Orchestrator coordinates with:
- **loop1-planning**: Activates for planning phase
- **loop2-implementation**: Activates for implementation phase
- **loop3-quality**: Activates for quality validation
- **skill-cascade-orchestrator**: Delegates to atomic skills as needed
- **session-init-queen**: Initializes on every session start

## Appendix: Complete Flow Examples

### Example 1: Successful Development Route

```
User: "Build a REST API for user management"

Flow Orchestrator:
├─ Route analysis: "build" → Loop 1
├─ Activate loop1-planning
│   ├─ Research API best practices
│   ├─ Create implementation plan
│   └─ Generate pre-mortem (risk: 1650, GO)
├─ Transition: Loop 1 → Loop 2
├─ Activate loop2-implementation
│   ├─ Queen delegates to Princess-Dev
│   ├─ Princess spawns: backend-dev, tester, reviewer
│   └─ 3-part audit: All pass
├─ Transition: Loop 2 → Loop 3
├─ Activate loop3-quality
│   ├─ Run 47-point quality gate
│   ├─ Quality score: 1.0 (47/47)
│   └─ Decision: GO
├─ Transition: Loop 3 → Production
└─ ✅ Deployment approved

Result: Feature deployed to production successfully
```

### Example 2: Debug Route (Security Failure)

```
User: "Build authentication system"

Flow Orchestrator:
├─ Route analysis: "build" → Loop 1
├─ [Loop 1 complete]
├─ [Loop 2 complete]
├─ Activate loop3-quality
│   ├─ Security audit: FAIL (SQL injection detected)
│   ├─ Quality score: 0.78
│   └─ Decision: NO-GO (P0 failure)
├─ Transition: Loop 3 → Loop 1 (Escalation)
├─ Activate loop1-planning (debug mode)
│   ├─ Research SQL injection prevention
│   ├─ Create fix plan (use parameterized queries)
│   └─ Update pre-mortem (regression risks)
├─ Transition: Loop 1 → Loop 2 (debug route)
├─ Activate loop2-implementation (fix mode)
│   ├─ Spawn debugger + security-manager
│   ├─ Apply fix (ORM usage)
│   └─ Regression testing
├─ Transition: Loop 2 → Loop 3 (revalidation)
├─ Activate loop3-quality (revalidation mode)
│   ├─ Security audit: PASS ✅
│   ├─ Regression tests: PASS ✅
│   ├─ Quality score: 1.0
│   └─ Decision: GO
├─ Transition: Loop 3 → Production
└─ ✅ Deployment approved

Result: Issue fixed, feature deployed successfully
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-17
**Part of**: SPEK Platform 3-Loop Methodology
**Related Skills**: `loop1-planning`, `loop2-implementation`, `loop3-quality`, `session-init-queen`
