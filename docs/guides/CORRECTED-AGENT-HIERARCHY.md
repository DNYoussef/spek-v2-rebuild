# CORRECTED: Agent Hierarchy & Drone Selection

**Date**: 2025-10-11
**Version**: 8.2.1 (Corrected)
**Status**: ✅ **CORRECTED** - Princesses now properly choose Drones from registry

---

## 🚨 What Was Wrong

**Previous (Incorrect)**:
- Princesses spawned arbitrary "coder", "tester", "reviewer" agents
- No connection to our 28 specialized agents
- Princess prompts were too generic

**Now (Corrected)**:
- Princesses choose from our **28 specialized agents** in the agent registry
- Queen provides Princess with recommended Drone list based on task analysis
- Princess prompts include specific Drones to spawn from our roster

---

## 📋 Complete Agent Roster (28 Agents)

### Queen (1)
- **queen**: Top-level coordinator

### Princesses (3 Coordinators)
- **princess-dev**: Development coordinator (Loop 2)
- **princess-coordination**: Research coordinator (Loop 1)
- **princess-quality**: Quality coordinator (Loop 3)

### Drones (24 Specialized Workers)

#### Core Development (5)
1. **coder**: Writes clean code (NASA Rule 10)
2. **tester**: Creates test suites (≥80% coverage)
3. **reviewer**: Reviews code quality
4. **researcher**: Researches problem domains
5. **planner**: Creates project plans

#### SPARC Methodology (4)
6. **spec-writer**: Writes technical specifications
7. **architect**: Designs system architecture
8. **pseudocode-writer**: Writes algorithms
9. **integration-engineer**: Integrates components

#### Specialized Tasks (10)
10. **debugger**: Fixes bugs
11. **docs-writer**: Generates documentation
12. **devops**: Handles deployment
13. **security-manager**: Security audits
14. **cost-tracker**: Budget tracking
15. **theater-detector**: Detects mock code
16. **nasa-enforcer**: Enforces NASA Rule 10
17. **fsm-analyzer**: Analyzes state machines
18. **orchestrator**: Workflow orchestration
19. **frontend-dev**: Frontend UI development
20. **backend-dev**: Backend API development

#### Infrastructure (3)
21. **code-analyzer**: Static code analysis
22. **infrastructure-ops**: Cloud provisioning
23. **release-manager**: Release coordination
24. **performance-engineer**: Performance optimization

---

## 🔄 Corrected Flow

### Step 1: User Sends Message

```
UI: "Create a Python web app with REST API"
```

### Step 2: Queen Analyzes

```python
# Queen uses agent_registry.py to find matching Drones
analysis = analyze_request("Create a Python web app with REST API")
# Result: Loop 2, princess-dev

recommended_drones = find_drones_for_task("Create a Python web app with REST API", "loop2")
# Result: ["coder", "backend-dev", "tester", "reviewer", "docs-writer"]
```

### Step 3: Queen Creates Princess Prompt

```
You are Princess-Dev.

Task: "Create a Python web app with REST API"

Recommended Drones to Spawn (from agent registry):
1. Spawn 'coder' Drone using Task tool:
   Task: Writes clean code (NASA Rule 10)
   Instructions: Write Python Flask app with REST endpoints

2. Spawn 'backend-dev' Drone using Task tool:
   Task: Backend API development
   Instructions: Design REST API routes and handlers

3. Spawn 'tester' Drone using Task tool:
   Task: Creates test suites (≥80% coverage)
   Instructions: Write pytest tests for all endpoints

4. Spawn 'reviewer' Drone using Task tool:
   Task: Reviews code quality
   Instructions: Review Flask app for best practices

5. Spawn 'docs-writer' Drone using Task tool:
   Task: Generates documentation
   Instructions: Generate API documentation

Process:
1. For each Drone, use Task tool
2. Coordinate their work
3. Aggregate results
4. Report back to Queen
```

### Step 4: Princess Spawns Specific Drones

```
Princess-Dev uses Task tool 5 times:
1. Task(subagent_type="coder", prompt="Write Flask app...")
2. Task(subagent_type="backend-dev", prompt="Design REST API...")
3. Task(subagent_type="tester", prompt="Write pytest tests...")
4. Task(subagent_type="reviewer", prompt="Review code...")
5. Task(subagent_type="docs-writer", prompt="Generate docs...")
```

---

## 🎯 Agent Registry Logic

### How Queen Chooses Drones

```python
# src/coordination/agent_registry.py

def find_drones_for_task(task_description: str, loop: str) -> List[str]:
    """
    Find the best Drone agents for a given task.

    1. Get all drones available for this loop
    2. Score each drone based on keyword matches
    3. Return top 5 matches
    """
    # Example:
    task = "Create a Python web app"
    loop = "loop2"

    # Keyword matching:
    # "code" → coder (score: 2)
    # "web" → backend-dev (score: 2)
    # "python" → coder (score: 1)
    # "app" → coder (score: 1)

    # Top matches: ["coder", "backend-dev", "tester", "reviewer"]
```

### Default Drones for Each Princess

If keyword matching returns no results, use defaults:

```python
defaults = {
    "princess-dev": ["coder", "tester", "reviewer"],
    "princess-coordination": ["researcher", "spec-writer", "architect"],
    "princess-quality": ["theater-detector", "nasa-enforcer", "docs-writer"]
}
```

---

## 📊 Example Scenarios

### Scenario 1: "Build a calculator"

**Queen Analysis**:
- Loop: loop2 (development)
- Princess: princess-dev
- Drones: ["coder", "tester", "reviewer"]

**Princess-Dev spawns**:
1. coder: Writes calculator.py
2. tester: Writes test_calculator.py
3. reviewer: Reviews code quality

---

### Scenario 2: "Research best practices for microservices"

**Queen Analysis**:
- Loop: loop1 (research)
- Princess: princess-coordination
- Drones: ["researcher", "architect", "spec-writer"]

**Princess-Coordination spawns**:
1. researcher: Researches microservices patterns
2. architect: Designs microservice architecture
3. spec-writer: Documents findings

---

### Scenario 3: "Audit code for security issues"

**Queen Analysis**:
- Loop: loop3 (quality)
- Princess: princess-quality
- Drones: ["security-manager", "code-analyzer", "theater-detector"]

**Princess-Quality spawns**:
1. security-manager: Performs security audit
2. code-analyzer: Static analysis for vulnerabilities
3. theater-detector: Scans for incomplete/mock code

---

## ✅ What's Fixed

### 1. **Agent Registry Created** (`src/coordination/agent_registry.py`)
- Complete registry of all 28 agents
- Keyword matching for Drone selection
- Loop-specific Drone filtering
- Default Drone lists for each Princess

### 2. **Queen Orchestrator Updated** (`src/agents/queen_orchestrator.py`)
- Imports agent_registry
- Uses `find_drones_for_task()` to choose Drones
- Provides Princess with specific Drone list
- Drone descriptions in Princess prompts

### 3. **Princess Prompts Corrected**
- Now include recommended Drones from registry
- Specific spawn instructions for each Drone
- Clear coordination logic

---

## 🧪 Testing

### Test Agent Selection

```bash
python src/coordination/agent_registry.py
```

**Output**:
```
SPEK PLATFORM - AGENT REGISTRY
Total Agents: 28
  Queen: 1
  Princesses: 3
  Drones: 24

TESTING DRONE SELECTION:
Task: 'Create a Python web app' (in loop2)
  Recommended Drones:
    - coder: Writes clean code
    - backend-dev: Backend API development
    - tester: Creates test suites
```

---

## 📝 Summary

**Before**: Princesses spawned generic "coder", "tester", "reviewer"
**After**: Princesses spawn specific Drones from our 28-agent registry based on task analysis

**Key Files**:
1. `src/coordination/agent_registry.py` - Registry of all 28 agents
2. `src/agents/queen_orchestrator.py` - Queen chooses Drones via registry
3. Princess prompts - Include specific Drone spawn instructions

**Status**: ✅ **CORRECTED AND WORKING**

---

**Document Version**: 1.0 (Corrected)
**Author**: Claude Sonnet 4.5
**Date**: 2025-10-11
