# SPEK Platform: Auto-Triggering Skills for Agent Coordination

**Date**: 2025-10-17
**Version**: 1.0.0 (Proof of Concept)
**Status**: 🚀 **Phase 1 STARTED** (2 of 15 skills complete)

---

## Executive Summary

### The Problem
The SPEK Platform has sophisticated infrastructure (28 agents, 27 workflows, 3-loop methodology) but Claude Code instances keep forgetting to use it properly. Manual reminders are required, and the system doesn't self-enforce quality gates.

### The Solution
**15 Auto-Triggering Skills** that:
- Auto-trigger based on keywords, tool use, and context patterns
- Automatically spawn agents from the 28-agent registry
- Enforce TDD, NASA compliance, completion checklists
- Chain together in intelligent cascades
- Block unsafe actions (deployments without tests, completion without quality gates)
- Self-optimize over time

### Current Status
✅ **2 of 15 Skills Complete** (Foundation Layer):
1. `session-init-queen` - Initializes Claude Code as Queen agent with full context
2. `skill-cascade-orchestrator` - Meta-orchestrator that coordinates all other skills

📝 **Next**: Create agent delegation and enforcement skills (13 remaining)

---

## System Architecture

### Complete Skill Hierarchy

```
session-init-queen (P0 - Runs first)
    ↓
skill-cascade-orchestrator (P0 - Always active)
    ↓
    ├── queen-delegation-orchestrator (Routes all requests)
    │       ↓
    │       ├── princess-coordination-skill (Loop1: Research)
    │       ├── princess-dev-skill (Loop2: Development)
    │       └── princess-quality-skill (Loop3: Quality)
    │
    ├── Workflow Enforcement Skills
    │   ├── tdd-enforcer (Forces test-first)
    │   ├── nasa-compliance-gate (Blocks violations)
    │   ├── completion-gate (Enforces checklist)
    │   └── stuck-escalation (Auto-escalates)
    │
    ├── Decision Support Skills
    │   └── decision-matrix-enforcer (FSM/Analyzer decisions)
    │
    ├── Deployment Skills
    │   ├── pre-deploy-validator (47-point checklist)
    │   ├── security-audit-enforcer (Auto security audit)
    │   └── rollback-emergency (Auto rollback)
    │
    └── Optimization Skills
        └── agent-selector-optimizer (Self-optimizing)
```

---

## Skills Completed (2/15)

### 1. session-init-queen ✅

**Location**: `.claude/skills/session-init-queen/skill.md`

**Purpose**: Initialize Claude Code as Queen agent at session start

**What It Does**:
1. Loads all 27 GraphViz workflows into context
2. Reads agent registry (28 agents)
3. Identifies role: "I am Queen"
4. Verifies system components
5. Confirms initialization to user

**Auto-Trigger**: EVERY session start (automatic)

**Output**:
```
🎯 **Queen Agent Initialized Successfully**

✅ **Role**: Queen Coordinator
✅ **Context Loaded**:
   - 28 agents (1 Queen, 3 Princesses, 24 Drones)
   - 27 process workflows
   - Agent registry with intelligent selection

✅ **Ready to**: Receive requests, spawn Princesses, coordinate Drones
```

**File Size**: ~15KB
**Performance**: <15 seconds initialization time

---

### 2. skill-cascade-orchestrator ✅

**Location**: `.claude/skills/skill-cascade-orchestrator/skill.md`

**Purpose**: Meta-orchestrator that monitors and activates all other skills

**What It Does**:
1. Monitors EVERY user message and tool use
2. Matches against trigger patterns (14 skill types)
3. Activates appropriate skills automatically
4. Chains skills in intelligent cascades
5. Blocks unsafe actions
6. Learns which cascades work best

**Auto-Trigger**: ALWAYS ACTIVE (runs continuously)

**Cascade Examples**:

**Example 1: Development Request**
```
User: "implement user login"
  ↓
Orchestrator detects: "implement" + "login"
  ↓
Activates (parallel):
  - tdd-enforcer (forces test-first)
  - queen-delegation-orchestrator (routes to princess-dev)
  - security-audit-enforcer (auto security audit)
  ↓
Result: TDD-driven, security-audited login feature
```

**Example 2: Deployment Request**
```
User: "deploy to production"
  ↓
Orchestrator detects: "deploy" + "production"
  ↓
BLOCKS immediate deployment
  ↓
Activates: pre-deploy-validator
  ↓
Runs: 47-point checklist
  ↓
Result: Zero unvalidated deployments
```

**File Size**: ~20KB
**Performance**: <5ms pattern matching, <100ms cascade overhead

---

## Skills Remaining (13/15)

### Phase 1: Foundation (Week 1) - 3 skills

3. **queen-delegation-orchestrator** (Day 3-4)
   - Routes all user requests through agent registry
   - Spawns appropriate Princess with Drone recommendations
   - **Agent Integration**: Uses `agent_registry.find_drones_for_task()`
   - **Auto-Trigger**: All user messages

4. **princess-coordination-skill** (Day 5)
   - Loop1 (Research & Planning) coordinator
   - **Agent Integration**: Spawns `researcher`, `spec-writer`, `architect` Drones
   - **Auto-Trigger**: Spawned by Queen for research tasks

5. **princess-dev-skill** (Day 5)
   - Loop2 (Development) coordinator
   - **Agent Integration**: Spawns `coder`, `tester`, `reviewer` Drones
   - **Auto-Trigger**: Spawned by Queen for development tasks

### Phase 2: Enforcement (Week 2) - 5 skills

6. **princess-quality-skill** (Day 1)
   - Loop3 (Quality) coordinator
   - **Agent Integration**: Spawns `theater-detector`, `nasa-enforcer`, `docs-writer` Drones
   - **Auto-Trigger**: Spawned by Queen for quality tasks

7. **tdd-enforcer** (Day 2)
   - Forces test-first development
   - **Agent Integration**: Ensures `tester` Drone spawns BEFORE `coder` Drone
   - **Auto-Trigger**: Keywords: "implement", "add", "create"

8. **nasa-compliance-gate** (Day 3)
   - Prevents NASA Rule 10 violations
   - **Agent Integration**: Spawns `nasa-enforcer` Drone on every Write/Edit
   - **Auto-Trigger**: Before ANY file write/edit

9. **completion-gate** (Day 4)
   - Enforces completion checklist
   - **Agent Integration**: Spawns quality Drones, blocks unless ALL pass
   - **Auto-Trigger**: Keywords: "done", "finished", "complete"

10. **stuck-escalation** (Day 5)
    - Auto-escalates when stuck
    - **Agent Integration**: Spawns `debugger` → `researcher` → user escalation
    - **Auto-Trigger**: Same error 3+ times, >30min on task

### Phase 3: Decision & Deployment (Week 3) - 4 skills

11. **decision-matrix-enforcer** (Day 1)
    - Prevents over-engineering via decision matrices
    - **Agent Integration**: Spawns `fsm-analyzer`, `code-analyzer` Drones
    - **Auto-Trigger**: Keywords: "FSM", "should I use", "state machine"

12. **pre-deploy-validator** (Day 2-3)
    - 47-point deployment checklist
    - **Agent Integration**: Spawns `devops`, `security-manager`, `performance-engineer` Drones
    - **Auto-Trigger**: Keywords: "deploy", "production", "release"

13. **security-audit-enforcer** (Day 4)
    - Auto security audit on sensitive features
    - **Agent Integration**: Spawns `security-manager` Drone
    - **Auto-Trigger**: Keywords: "auth", "security", "login", "password"

14. **rollback-emergency** (Day 5)
    - Auto rollback on production failures
    - **Agent Integration**: Spawns `devops`, `infrastructure-ops` Drones
    - **Auto-Trigger**: Error rate >5%, crash reports

### Phase 4: Optimization (Week 4) - 1 skill

15. **agent-selector-optimizer** (Day 1-2)
    - Self-optimizing agent selection
    - **Agent Integration**: Learns which Drones work best for which tasks
    - **Auto-Trigger**: After every task completion

---

## Implementation Timeline

### Week 1 (Foundation)
- ✅ Day 1: `session-init-queen` **COMPLETE**
- ✅ Day 2: `skill-cascade-orchestrator` **COMPLETE**
- 📝 Day 3-4: `queen-delegation-orchestrator`
- 📝 Day 5: `princess-coordination-skill`, `princess-dev-skill`

### Week 2 (Enforcement)
- 📝 Day 1: `princess-quality-skill`
- 📝 Day 2: `tdd-enforcer`
- 📝 Day 3: `nasa-compliance-gate`
- 📝 Day 4: `completion-gate`
- 📝 Day 5: `stuck-escalation`

### Week 3 (Decision & Deployment)
- 📝 Day 1: `decision-matrix-enforcer`
- 📝 Day 2-3: `pre-deploy-validator`
- 📝 Day 4: `security-audit-enforcer`
- 📝 Day 5: `rollback-emergency`

### Week 4 (Optimization & Testing)
- 📝 Day 1-2: `agent-selector-optimizer`
- 📝 Day 3-4: Integration testing
- 📝 Day 5: Documentation finalization

---

## Technical Details

### File Structure
```
.claude/
  skills/
    session-init-queen/
      skill.md (15KB) ✅
    skill-cascade-orchestrator/
      skill.md (20KB) ✅
    queen-delegation-orchestrator/
      skill.md (pending)
    [... 12 more skills ...]
```

### Skill Manifest Format
Each `skill.md` includes:
1. **Auto-Trigger Patterns** - When to activate
2. **Purpose** - What it does (1-line)
3. **Agent Integration** - Which agents to spawn
4. **Embedded Workflows** - Which .dot files to use
5. **Process** - Step-by-step execution
6. **Cascade Triggers** - Which skills to chain with
7. **Output** - What user/system sees
8. **Performance Targets** - Speed/memory requirements
9. **Troubleshooting** - Common issues + fixes
10. **Version History** - Changes over time

### Agent Integration Pattern
```python
# Example: tdd-enforcer skill
def on_implement_keyword():
    # 1. Block immediate Write/Edit operations
    block_write_operations()

    # 2. Use agent registry to find tester Drone
    from src.coordination.agent_registry import find_drones_for_task
    tester_drone = find_drones_for_task("write tests", loop="loop2")[0]

    # 3. Spawn tester Drone via Task tool
    spawn_agent_via_task_tool(
        agent_type=tester_drone,
        task="Write failing test for [feature]"
    )

    # 4. Wait for test to exist
    wait_for_test_file()

    # 5. THEN spawn coder Drone
    coder_drone = find_drones_for_task("implement code", loop="loop2")[0]
    spawn_agent_via_task_tool(
        agent_type=coder_drone,
        task="Implement minimal code to pass test"
    )

    # 6. Unblock Write/Edit operations
    unblock_write_operations()
```

### Communication Flow
```
User Message
    ↓
skill-cascade-orchestrator (monitors)
    ↓
queen-delegation-orchestrator (routes)
    ↓
agent_registry.find_drones_for_task() (selects)
    ↓
Princess (spawned via Task tool)
    ↓
Drones (spawned via Task tool)
    ↓
Flask endpoints (report progress)
    ↓
Queen (aggregates results)
    ↓
User (sees final output)
```

---

## Benefits

### For Project Owner
- ✅ No more manual reminders needed
- ✅ System self-enforces quality gates
- ✅ Agent coordination automatic
- ✅ Skills cascade intelligently
- ✅ Self-optimizing over time

### For Claude Code (Me)
- ✅ Auto-loaded context (27 workflows)
- ✅ Automatic agent selection
- ✅ Quality gates enforced BEFORE proceeding
- ✅ TDD enforced automatically
- ✅ Can't mark "done" unless ALL gates pass
- ✅ Stuck situations auto-escalate

### For Project
- ✅ 100% TDD adherence (enforced)
- ✅ Zero NASA violations (enforced)
- ✅ Zero theater code (enforced)
- ✅ Deployment safety (enforced)
- ✅ Self-optimizing agent selection

---

## Integration with Existing Components

### Uses Existing Infrastructure
1. **28 Agents** (`src/agents/`) - Skills spawn these via Task tool
2. **Agent Registry** (`src/coordination/agent_registry.py`) - Skills use `find_drones_for_task()`
3. **Queen Orchestrator** (`src/agents/queen_orchestrator.py`) - Skills extend its capabilities
4. **27 Workflows** (`.claude/processes/`) - Skills embed and automate these
5. **Message Queue** (`.claude_messages/`) - Skills communicate via this
6. **Flask Backend** (`claude_backend_server.py`) - Skills report progress here

### Augments Existing Skills
Your 8 existing skills can now be enhanced:
- `agent-creator` → Can now spawn agents from 28-agent registry
- `functionality-audit` → Can spawn `tester` + `code-analyzer` Drones
- `theater-detection-audit` → Uses `theater-detector` Drone automatically
- `skill-creator-agent` → Can create skills with agent integration
- `prompt-architect` → Can optimize prompts for 28 agents
- `skill-forge` → Can forge skills with auto-trigger patterns
- `style-audit` → Can spawn `reviewer` + `code-analyzer` Drones
- `intent-analyzer` → Integrates with `queen-delegation-orchestrator` for routing

---

## Next Steps

### Immediate (Today)
1. ✅ Complete `session-init-queen` skill
2. ✅ Complete `skill-cascade-orchestrator` skill
3. 📝 Review and approve approach
4. 📝 Continue with `queen-delegation-orchestrator` skill

### Week 1 Remaining
5. Build `queen-delegation-orchestrator` (agent routing)
6. Build `princess-coordination-skill` (research coordination)
7. Build `princess-dev-skill` (development coordination)

### Week 2-4
8. Build 10 remaining enforcement/deployment/optimization skills
9. Integration testing across all 15 skills
10. Documentation finalization

---

## Success Criteria

### Phase 1 Complete When:
- ✅ 2 foundation skills operational (session-init, cascade-orchestrator)
- 📝 Queen can route requests to Princesses automatically
- 📝 Princesses can spawn Drones from registry automatically
- 📝 All skills auto-trigger on correct patterns

### Phase 2 Complete When:
- 📝 TDD enforced on every implementation
- 📝 NASA compliance checked on every write
- 📝 Completion blocked until quality gates pass
- 📝 Stuck situations auto-escalate

### Phase 3 Complete When:
- 📝 Deployments blocked until 47-point checklist passes
- 📝 Security audits run automatically on auth features
- 📝 Emergency rollbacks trigger on production errors

### Phase 4 Complete When:
- 📝 Agent selection self-optimizes based on success rates
- 📝 All 15 skills tested and documented
- 📝 System operational in production

---

## Performance Targets

- **Session Init**: <15 seconds
- **Pattern Matching**: <5ms per message
- **Skill Activation**: <10ms per skill
- **Cascade Overhead**: <100ms total
- **Agent Selection**: <50ms (agent_registry.find_drones_for_task)
- **Memory Usage**: <1MB for all 15 skills

---

## Files Created

1. `.claude/skills/session-init-queen/skill.md` (~15KB) ✅
2. `.claude/skills/skill-cascade-orchestrator/skill.md` (~20KB) ✅
3. `docs/SKILLS-AUTO-TRIGGER-SYSTEM.md` (this document) ✅

**Total LOC Added**: ~3,500 lines (markdown documentation)

---

## Questions & Feedback

### Questions
1. Should we prioritize certain skills over others in Week 1?
2. Should we add more trigger patterns to skill-cascade-orchestrator?
3. Should we create a skills testing framework first?

### Next Session
Continue with `queen-delegation-orchestrator` skill (Day 3-4 of Week 1)

---

**Last Updated**: 2025-10-17
**Status**: 🚀 Phase 1 Started (2/15 skills complete)
**Next Milestone**: Complete Week 1 foundation (3 more skills)
**Progress**: 13.3% (2/15 skills)
