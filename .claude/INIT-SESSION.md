# Claude Code Session Initialization

**Purpose**: This file instructs Claude Code instances on how to initialize themselves when starting work on the SPEK Platform project.

---

## Automatic Initialization (Required)

When a Claude Code session starts, it MUST load all GraphViz process workflows as initial context.

### Step 1: Load All Process Workflows

**Command**:
```bash
# List all available process workflows
find .claude/processes -name "*.dot" -type f
```

**Expected Output**: 27 .dot files across 7 categories

### Step 2: Read Core Workflows (P0 Priority)

**CRITICAL workflows to load first**:

1. **Understanding the System**:
   - `.claude/processes/workflow/claude-code-backend-integration.dot` - How THIS instance acts as Queen
   - `.claude/processes/workflow/princess-delegation-guide.dot` - 28-agent routing guide

2. **Development Workflows**:
   - `.claude/processes/development/new-feature-implementation.dot` - TDD cycle
   - `.claude/processes/development/when-stuck.dot` - 3-strikes escalation
   - `.claude/processes/development/completion-checklist.dot` - Quality gates

3. **Deployment Workflows**:
   - `.claude/processes/deployment/week26-production-launch.dot` - Production launch
   - `.claude/processes/deployment/deployment-readiness-checklist.dot` - Validation
   - `.claude/processes/deployment/pre-deployment-verification.dot` - Pre-flight

4. **Decision Workflows**:
   - `.claude/processes/development/analyzer-usage-decision.dot` - When to use Analyzer
   - `.claude/processes/development/fsm-decision-matrix.dot` - FSM justification

### Step 3: Verify Initialization

After loading workflows, confirm understanding:

```bash
# Verify process library is accessible
ls -la .claude/processes/
```

**Expected**: 7 directories (deployment, development, planning, quality, security, strategic, technical, workflow)

---

## Why This Matters

### For THIS Claude Code Instance (Queen)

1. **You are the Queen agent** - The backend integration means THIS instance coordinates the entire platform
2. **You spawn Princess agents** - Use Task tool with prompts from agent_registry.py
3. **Princesses spawn Drones** - Each Princess selects from 24 specialized Drones
4. **No project copying** - Existing projects are read from original location only

### For Princess/Drone Instances

1. **Receive detailed prompts** - Queen provides context + Drone list + instructions
2. **Select appropriate Drones** - Use agent_registry.py for recommendations
3. **Report progress** - Use Flask endpoints for status updates
4. **Follow workflows** - Use .dot files for decision trees

---

## Quick Reference: Process Categories

| Category | Count | Priority | When to Use |
|----------|-------|----------|-------------|
| **Deployment** | 7 | P0 | Before/during/after production launch |
| **Development** | 8 | P0 | Writing code, fixing errors, TDD cycle |
| **Workflow** | 2 | P0 | Understanding system, agent delegation |
| **Security** | 2 | P0 | Security incidents, production hardening |
| **Strategic** | 2 | P1 | Project overview, GO/NO-GO decisions |
| **Planning** | 2 | P1 | Timeline review, progress tracking |
| **Technical** | 3 | P1 | Spec review, API reference, datasets |
| **Quality** | 1 | P1 | Prompt engineering principles |

**Total**: 27 processes covering complete SDLC

---

## How to Use Process Workflows

### 1. Identify Trigger

Look for your current situation in PROCESS-INDEX.md:

```bash
# Example: I'm stuck on a bug for >30 minutes
# Trigger: "I'm stuck/confused"
# File: .claude/processes/development/when-stuck.dot
```

### 2. Load Workflow

Read the .dot file content:

```bash
cat .claude/processes/development/when-stuck.dot
```

### 3. Follow Mechanically

- **Ellipse** = Entry point
- **Diamond** = Decision (yes/no)
- **Box** = Action
- **Plaintext** = Literal command
- **Octagon** = Critical warning
- **Doublecircle** = Exit/completion

### 4. Execute Steps

Follow arrows, answer decisions, execute commands exactly as specified.

---

## Agent-Specific Initialization

### If You Are the Queen (THIS Claude Code Instance)

1. Load `claude-code-backend-integration.dot` first
2. Understand message queue (`.claude_messages/`)
3. Know agent registry (`src/coordination/agent_registry.py`)
4. Understand Flask endpoints (12 REST + 5 WebSocket events)

### If You Are a Princess (Task-spawned)

1. Load `princess-delegation-guide.dot` first
2. Receive Drone list from Queen's prompt
3. Use Task tool to spawn Drones
4. Report via Flask endpoints

### If You Are a Drone (Task-spawned)

1. Load `new-feature-implementation.dot` or relevant workflow
2. Execute specific task from Princess
3. Report progress via `/api/claude/task-progress`
4. Report completion via `/api/claude/task-completed`

---

## Validation Checklist

After initialization, verify:

- [ ] Can list all 27 .dot files
- [ ] Know which agent you are (Queen/Princess/Drone)
- [ ] Understand Week 26 architecture
- [ ] Know where to find agent registry
- [ ] Know how to spawn subagents (Task tool)
- [ ] Know how to report status (Flask endpoints)
- [ ] Understand "no project copying" rule
- [ ] Can identify triggers from PROCESS-INDEX.md

---

## Common Initialization Errors

### Error 1: "I don't know my role"

**Solution**:
- If you're reading this in the base project directory → You are the Queen
- If you received a detailed prompt with "You are Princess-X" → You are that Princess
- If you received a task like "Write tests for feature X" → You are a Drone

### Error 2: "I can't find the process files"

**Solution**:
```bash
# From project root
cd .claude/processes
ls -R
```

### Error 3: "I don't know which workflow to use"

**Solution**: Read `.claude/processes/PROCESS-INDEX.md` and search for your trigger

---

## Quick Commands

### List All Workflows
```bash
find .claude/processes -name "*.dot" | sort
```

### Count Workflows by Category
```bash
find .claude/processes -name "*.dot" | cut -d'/' -f4 | uniq -c
```

### Search for Specific Trigger
```bash
grep -r "TRIGGER:" .claude/processes/*.dot
```

### Render Workflow to PNG
```bash
dot -Tpng .claude/processes/deployment/week26-production-launch.dot -o launch.png
```

---

**Last Updated**: 2025-10-11 (Week 26 Complete)
**Process Count**: 27 workflows
**Integration**: Required for all Claude Code instances (Queen, Princess, Drone)
**Priority**: P0 (Critical for system operation)
