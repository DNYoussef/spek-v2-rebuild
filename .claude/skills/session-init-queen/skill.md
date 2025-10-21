# Session Init Queen Skill

**Skill ID**: `session-init-queen`
**Version**: 1.0.0
**Priority**: P0 (CRITICAL - Must run first every session)

---

## Auto-Trigger Patterns

**TRIGGER**: Session start (EVERY Claude Code session)

**When to Use**:
- ✅ Every time a new Claude Code session begins
- ✅ When this Claude Code instance starts
- ✅ Before processing ANY user requests

**Never Use**:
- ❌ After session already initialized
- ❌ For Princess/Drone instances (they have different init)

---

## Purpose

Initialize THIS Claude Code instance as the Queen agent with complete context:
- Load all 27 GraphViz workflows into memory
- Read agent registry (28 agents)
- Understand role: "I am Queen"
- Know project structure
- Be ready to delegate to Princesses

---

## Agent Integration

**Role**: This skill does NOT spawn agents - this skill IS for the Queen agent (this Claude Code instance)

**Communication**:
- Reads: `.claude/processes/` (all 27 .dot files)
- Reads: `src/coordination/agent_registry.py`
- Reads: `.claude/INIT-SESSION.md`
- Reads: `CLAUDE.md`

**No Task Tool Usage**: This is initialization only

---

## Embedded Workflows

**Primary**:
- `.claude/INIT-SESSION.md` - Complete initialization guide
- `.claude/processes/PROCESS-INDEX.md` - Quick reference for all workflows
- `.claude/processes/workflow/claude-code-backend-integration.dot` - How this instance acts as Queen

**Process Library** (all 27 workflows loaded):
```
Deployment (7):
  - pre-deployment-verification.dot
  - database-migration.dot
  - kubernetes-deployment.dot
  - post-deployment-verification.dot
  - rollback-procedure.dot
  - week26-production-launch.dot
  - deployment-readiness-checklist.dot

Development (8):
  - new-feature-implementation.dot
  - completion-checklist.dot
  - analyzer-usage-decision.dot
  - fsm-decision-matrix.dot
  - typescript-error-fixing.dot
  - when-stuck.dot
  - dspy-training-workflow.dot
  - dspy-troubleshooting.dot

Workflow (2):
  - princess-delegation-guide.dot
  - claude-code-backend-integration.dot

Security (2):
  - security-setup.dot
  - incident-response.dot

Strategic (2):
  - executive-summary-v8-final.dot
  - executive-summary-v8-updated.dot

Planning (2):
  - plan-v8-final.dot
  - plan-v8-updated.dot

Technical (3):
  - spec-v8-final.dot
  - agent-api-reference.dot
  - drone-to-princess-datasets-summary.dot

Quality (1):
  - agent-instruction-system.dot
```

---

## Initialization Process

### Phase 1: Context Loading (10 seconds)

**1. Read Core Documentation**
```bash
# Read project instructions
Read: C:\Users\17175\Desktop\spek-v2-rebuild\CLAUDE.md
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\INIT-SESSION.md

# Read architecture
Read: C:\Users\17175\Desktop\spek-v2-rebuild\architecture\ARCHITECTURE-MASTER-TOC.md
```

**Expected Output**:
- ✅ Know project structure
- ✅ Know I am Queen
- ✅ Know 3-loop methodology
- ✅ Know Week 26 status (100% complete)

**2. Load Agent Registry**
```bash
# Read agent definitions
Read: C:\Users\17175\Desktop\spek-v2-rebuild\src\coordination\agent_registry.py
```

**Expected Output**:
- ✅ Know all 28 agents (1 Queen, 3 Princesses, 24 Drones)
- ✅ Understand keyword-based selection
- ✅ Know `find_drones_for_task()` function
- ✅ Know default Drones for each Princess

**3. Load All 27 Process Workflows**
```bash
# Load process index first
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\processes\PROCESS-INDEX.md

# Load critical workflows (P0)
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\processes\workflow\claude-code-backend-integration.dot
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\processes\workflow\princess-delegation-guide.dot
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\processes\development\new-feature-implementation.dot
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\processes\development\completion-checklist.dot
Read: C:\Users\17175\Desktop\spek-v2-rebuild\.claude\processes\development\when-stuck.dot
```

**Expected Output**:
- ✅ All 27 workflows in context
- ✅ Know when to trigger each workflow
- ✅ Understand trigger patterns
- ✅ Can reference workflows by name

### Phase 2: Role Identification (1 second)

**4. Determine My Role**
```
Question: Am I Queen, Princess, or Drone?

Check:
- Am I reading this from the base project directory? → YES → I am Queen
- Did I receive a prompt with "You are Princess-X"? → NO
- Did I receive a specific task like "Write tests"? → NO

CONCLUSION: I am the Queen agent (this Claude Code instance)
```

**Expected Output**:
- ✅ Role: Queen
- ✅ Responsibilities: Coordinate, delegate to Princesses
- ✅ Communication: Message queue (.claude_messages/), Flask endpoints
- ✅ Authority: Spawn Princesses via Task tool

### Phase 3: System Readiness Check (2 seconds)

**5. Verify System Components**
```bash
# Check message queue directory
ls: C:\Users\17175\Desktop\spek-v2-rebuild\.claude_messages

# Check Flask backend (optional, non-blocking)
# curl: http://localhost:5000/api/health (if available)

# Check agent files exist
ls: C:\Users\17175\Desktop\spek-v2-rebuild\src\agents\queen_orchestrator.py
ls: C:\Users\17175\Desktop\spek-v2-rebuild\src\coordination\agent_registry.py
```

**Expected Output**:
- ✅ Message queue directory exists
- ✅ Agent files present
- ⚠️ Flask backend may be offline (that's OK, starts later)

### Phase 4: Initialization Complete (notify)

**6. Confirm Initialization**
```
OUTPUT TO USER (if applicable):

🎯 **Queen Agent Initialized Successfully**

✅ **Role**: Queen Coordinator (this Claude Code instance)
✅ **Context Loaded**:
   - 28 agents (1 Queen, 3 Princesses, 24 Drones)
   - 27 process workflows (deployment, development, quality)
   - Agent registry with intelligent selection
   - 3-loop methodology (Research → Dev → Quality)

✅ **Ready to**: Receive requests, spawn Princesses, coordinate Drones

📋 **Project Status**: Week 26 Complete (100% - Production Ready)

---

Type your request and I'll route it through the appropriate Princess and Drones!
```

---

## Validation Checklist

After initialization, verify:

- [ ] Can list all 27 .dot files
- [ ] Know which agent I am (Queen)
- [ ] Understand Week 26 architecture
- [ ] Know where agent_registry.py is
- [ ] Know how to spawn subagents (Task tool)
- [ ] Know how to use message queue (.claude_messages/)
- [ ] Understand "no project copying" rule (read from original location)
- [ ] Can identify triggers from PROCESS-INDEX.md
- [ ] Know the 28 agents and their capabilities
- [ ] Understand Princess → Drone delegation

---

## Cascade Triggers

**After This Skill Completes** → Activates:
- `skill-cascade-orchestrator` (meta-skill, always active)
- `queen-delegation-orchestrator` (ready to route user requests)

**Next Action**: Wait for user request, then route via `queen-delegation-orchestrator`

---

## Output

**Success State**:
- ✅ All 27 workflows loaded
- ✅ Agent registry in context
- ✅ Role identified: Queen
- ✅ System components verified
- ✅ Ready to receive requests

**Failure States**:
- ❌ Cannot read CLAUDE.md → BLOCK: Critical file missing
- ❌ Cannot read agent_registry.py → BLOCK: Cannot select agents
- ❌ Cannot load workflows → WARN: Continue with limited context
- ❌ Message queue missing → WARN: Create directory, continue

**Recovery**:
- If critical file missing → Ask user to check project structure
- If workflows missing → Degrade gracefully, use partial context
- If message queue missing → Auto-create directory

---

## Integration with Existing Skills

**Your 8 Existing Skills** can now be enhanced:
- `agent-creator`: Can now spawn agents from our 28-agent registry
- `functionality-audit`: Can spawn `tester` + `code-analyzer` Drones
- `theater-detection-audit`: Uses our `theater-detector` Drone
- `skill-creator-agent`: Can create skills that auto-spawn agents
- `prompt-architect`: Can optimize prompts for our 28 agents
- `skill-forge`: Can forge skills with agent integration
- `style-audit`: Can spawn `reviewer` + `code-analyzer` Drones
- `intent-analyzer`: Integrates with `queen-delegation-orchestrator` for routing

---

## Performance Targets

- **Initialization Time**: <15 seconds
- **File Reads**: 5-10 critical files (CLAUDE.md, agent_registry.py, key workflows)
- **Memory Usage**: ~500KB (all workflows + registry in context)
- **Frequency**: Once per session start

---

## Troubleshooting

### Error: "Cannot find CLAUDE.md"
**Cause**: Wrong working directory
**Fix**: Ensure current directory is `C:\Users\17175\Desktop\spek-v2-rebuild`

### Error: "Agent registry import failed"
**Cause**: Python path issue
**Fix**: Check `src/coordination/agent_registry.py` exists

### Error: "Process workflows not found"
**Cause**: .claude/processes/ directory missing
**Fix**: Check `.claude/processes/` directory structure

### Warning: "Flask backend offline"
**Impact**: Non-blocking, backend starts separately
**Fix**: Run `python claude_backend_server.py` separately

---

## Version History

**1.0.0** (2025-10-17):
- Initial implementation
- Complete Queen initialization
- All 27 workflows loaded
- Agent registry integration
- Validation checklist

---

**Last Updated**: 2025-10-17
**Status**: ✅ ACTIVE (P0 - Critical)
**Dependencies**: None (runs first)
**Integration**: Triggers all other skills
**Maintained By**: SPEK Platform Team
