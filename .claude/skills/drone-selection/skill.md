# Drone Selection

## Overview

This skill handles intelligent Drone agent selection and spawning within the SPEK Platform's 3-tier hierarchy. Use this skill when a Princess coordinator needs to spawn specialized Drone workers based on task requirements. This skill leverages the agent_registry.py intelligent matching system to recommend the best Drones for any given task, ensuring optimal agent utilization and task success.

Drones are the tactical execution layer (Tier 3) that perform specialized work under Princess coordination. The 24 available Drones cover all aspects of software development: coding, testing, review, research, planning, architecture, security, documentation, and deployment.

## When to Use This Skill

Activate this skill when:
- **Princess needs Drones**: Any Princess (coordination/dev/quality) must spawn workers
- **Task requires specialization**: Work needs specific expertise (frontend, backend, security, etc.)
- **Intelligent selection needed**: Multiple Drone options exist, need best match
- **Multi-drone coordination**: Task requires spawning 2+ Drones in sequence or parallel
- **Loop work begins**: Loop 1/2/3 transitions from planning to execution

**Auto-Trigger Patterns**:
- Princess agents invoke this during their workflow
- Keywords: "spawn drone", "find agent", "select worker"
- Task complexity: Princess determines work requires Drone specialization
- Agent registry query: Need to find best Drone for task

**DO NOT use this skill for**:
- Princess selection (use `princess-summoning` skill instead)
- Queen-level decisions (Queen handles directly)
- Single known Drone (spawn directly without selection)

## Drone Selection Logic

The skill uses keyword matching and task analysis to recommend Drones:

### Selection Algorithm

From `src/coordination/agent_registry.py`:

```python
def find_drones_for_task(task_description: str, loop: str) -> List[str]:
    """
    Find the best Drone agents for a given task.

    This is the core logic Princesses use to choose Drones.

    Args:
        task_description: User's task description
        loop: Current loop (loop1/loop2/loop3)

    Returns:
        List of Drone agent IDs ranked by relevance (top 5)
    """
    task_lower = task_description.lower()
    matching_drones = []

    # Get all drones available for this loop
    available_drones = get_drones_for_loop(loop)

    # Score each drone based on keyword matches
    drone_scores = {}
    for drone_id in available_drones:
        caps = AGENT_REGISTRY[drone_id]
        score = 0

        # Check keyword matches (high priority)
        for keyword in caps.keywords:
            if keyword in task_lower:
                score += 2

        # Check task type matches (medium priority)
        for task_type in caps.task_types:
            if task_type in task_lower:
                score += 1

        if score > 0:
            drone_scores[drone_id] = score

    # Sort by score and return top matches
    sorted_drones = sorted(drone_scores.items(), key=lambda x: x[1], reverse=True)

    # Return top 5 matches (or fewer if not enough)
    return [drone_id for drone_id, score in sorted_drones[:5]]
```

### Scoring System

**Keyword Match** (+2 points):
- Task description contains Drone's primary keywords
- Example: "frontend" matches frontend-dev (+2)

**Task Type Match** (+1 point):
- Task description contains Drone's task types
- Example: "implementation" matches coder (+1)

**Final Ranking**:
- Drones sorted by total score (descending)
- Top 5 returned as recommendations
- Princess chooses from top matches based on context

## Complete Drone Registry

### Loop 1 Drones (Research & Planning) - 5 Agents

| Drone | Keywords | Description |
|-------|----------|-------------|
| **researcher** | research, investigate, study, analyze, explore | Researches problem domains and gathers information |
| **planner** | plan, strategy, roadmap, schedule, timeline | Creates project plans and schedules |
| **spec-writer** | specification, requirements, spec, document | Writes technical specifications and requirements documents |
| **architect** | architecture, design, system, structure, pattern | Designs system architecture and component interactions |
| **pseudocode-writer** | pseudocode, algorithm, logic, flow | Writes pseudocode and algorithm designs |

### Loop 2 Drones (Development & Implementation) - 10 Agents

| Drone | Keywords | Description |
|-------|----------|-------------|
| **coder** | code, implement, write, function, class, module | Writes clean, tested code following NASA Rule 10 (≤60 LOC per function) |
| **tester** | test, pytest, unittest, coverage, assertion | Writes comprehensive test suites with ≥80% coverage |
| **reviewer** | review, critique, feedback, improve, refactor | Reviews code for quality, security, and best practices |
| **frontend-dev** | frontend, ui, react, component, interface | Develops frontend UI components (React, Next.js, etc.) |
| **backend-dev** | backend, api, server, endpoint, database | Develops backend APIs and server logic |
| **debugger** | debug, fix, bug, error, issue | Debugs issues and fixes bugs |
| **integration-engineer** | integrate, merge, combine, connect | Integrates components and ensures they work together |
| **orchestrator** | orchestrate, workflow, coordinate, manage | Orchestrates complex multi-agent workflows |

### Loop 3 Drones (Quality & Finalization) - 9 Agents

| Drone | Keywords | Description |
|-------|----------|-------------|
| **theater-detector** | mock, fake, placeholder, todo, fixme | Detects mock code, TODOs, and placeholder implementations |
| **nasa-enforcer** | nasa, compliance, rule10, lint, standard | Enforces NASA Rule 10 (≤60 LOC per function, ≥2 assertions) |
| **docs-writer** | documentation, readme, guide, tutorial, docs | Generates comprehensive documentation |
| **code-analyzer** | analyze, static, ast, parse, inspect | Performs static code analysis and AST inspection |
| **security-manager** | security, vulnerability, audit, penetration, threat | Performs security audits and vulnerability assessments |
| **devops** | deploy, ci/cd, docker, kubernetes, pipeline | Handles deployment and CI/CD pipeline setup |
| **cost-tracker** | cost, budget, pricing, expense, billing | Tracks costs and manages budgets |
| **infrastructure-ops** | infrastructure, k8s, terraform, cloud, provision | Manages infrastructure and cloud provisioning |
| **release-manager** | release, version, changelog, tag, publish | Coordinates releases and versioning |
| **performance-engineer** | performance, optimize, profile, benchmark, speed | Optimizes performance and conducts benchmarks |
| **fsm-analyzer** | fsm, state, machine, xstate, transition | Analyzes and validates finite state machines |

**Total**: 24 Drones across all 3 loops

## Drone Selection Workflow

Follow this systematic workflow to select and spawn Drones:

### Phase 1: Task Analysis

Analyze the task to understand requirements:

**Actions**:
1. Extract task description from user request or Princess instructions
2. Identify task type (research/coding/testing/deployment/etc.)
3. Determine current loop context (loop1/loop2/loop3)
4. Identify any explicit agent requests in task description

**Task Analysis Template**:
```python
task_context = {
    "description": "Implement REST API with OAuth2 authentication",
    "loop": "loop2",  # Implementation phase
    "explicit_agents": [],  # Any agents specifically requested
    "task_type": "backend",  # Inferred from description
    "keywords": ["api", "oauth2", "authentication"]  # Extracted keywords
}
```

### Phase 2: Intelligent Drone Selection

Use agent_registry.py to find best Drone matches:

**Actions**:
1. Call `find_drones_for_task(task_description, loop)`
2. Review top 5 recommended Drones
3. Select appropriate number of Drones (1-5) based on task complexity
4. Consider dependencies (e.g., tester before coder for TDD)

**Selection Examples**:

**Example 1: Frontend Development**
```python
task = "Create React component for user profile"
loop = "loop2"

drones = find_drones_for_task(task, loop)
# Returns: ["frontend-dev", "coder", "tester", "reviewer"]

# Select top 3 for implementation
selected = drones[:3]  # ["frontend-dev", "coder", "tester"]
```

**Example 2: Backend API**
```python
task = "Build REST API for payment processing with security audit"
loop = "loop2"

drones = find_drones_for_task(task, loop)
# Returns: ["backend-dev", "security-manager", "coder", "tester", "reviewer"]

# Select backend-dev + security-manager (both high relevance)
selected = ["backend-dev", "security-manager", "tester"]
```

**Example 3: Research & Planning**
```python
task = "Research best practices for microservices architecture"
loop = "loop1"

drones = find_drones_for_task(task, loop)
# Returns: ["researcher", "architect", "spec-writer"]

# Select researcher + architect for thorough research
selected = drones[:2]  # ["researcher", "architect"]
```

**Example 4: Quality Validation**
```python
task = "Validate code quality and detect placeholder implementations"
loop = "loop3"

drones = find_drones_for_task(task, loop)
# Returns: ["theater-detector", "nasa-enforcer", "code-analyzer", "reviewer"]

# Select all quality Drones
selected = drones[:4]  # Full quality audit
```

### Phase 3: Drone Task Prompt Construction

Build specific task prompts for each selected Drone:

**Prompt Structure**:
```markdown
You are the {DRONE_NAME} Drone for the SPEK Platform.

TASK: {specific_task_for_drone}

CONTEXT:
- Loop: {loop}
- Princess Coordinator: {princess_id}
- Overall Goal: {parent_task_description}
- Route: {route} (development or debug)

{LOOP_SPECIFIC_CONTEXT}

DELIVERABLES:
{drone_specific_deliverables}

CONSTRAINTS:
{drone_specific_constraints}

QUALITY STANDARDS:
{drone_specific_quality_standards}

TIME BUDGET: {estimated_time}

Report when complete or if blocked. Escalate to Princess if:
- 3 attempts fail
- Blocker encountered
- Unclear requirements
```

**Drone-Specific Prompts**:

**Coder Drone**:
```markdown
You are the Coder Drone.

TASK: Implement authentication module per plan

CONTEXT:
- Loop: loop2
- Princess: princess-dev
- Overall Goal: Build OAuth2 authentication system

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

Report when complete or if blocked.
```

**Tester Drone** (TDD - spawned FIRST):
```markdown
You are the Tester Drone.

TASK: Write test suite for authentication module (TDD)

CONTEXT:
- Loop: loop2
- Princess: princess-dev
- Overall Goal: Build OAuth2 authentication system
- TDD: You write tests BEFORE Coder implements

REQUIREMENTS:
{authentication_requirements_from_plan}

DELIVERABLES:
1. Comprehensive test suite (/tests/)
   - Unit tests for all functions
   - Integration tests for auth flow
   - Edge case tests
2. Test coverage report (target: ≥80%)
3. Test documentation

TEST STRUCTURE:
- Use pytest (Python) or Jest (TypeScript)
- Arrange-Act-Assert pattern
- Clear test names (test_user_login_with_valid_credentials)
- Fixtures for common test data

COVERAGE TARGETS:
- Core auth logic: ≥90%
- Integration flows: ≥80%
- Edge cases: ≥70%

TIME BUDGET: 20 minutes

Report when complete. Coder will implement to pass your tests.
```

**Reviewer Drone**:
```markdown
You are the Reviewer Drone.

TASK: Review authentication module implementation

CONTEXT:
- Loop: loop2
- Princess: princess-dev
- Overall Goal: Build OAuth2 authentication system

CODE TO REVIEW:
{list_of_files_to_review}

REVIEW CHECKLIST:
Security:
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] XSS prevention

Quality:
- [ ] NASA Rule 10 compliance (≤60 LOC/function)
- [ ] Type hints present
- [ ] Error handling robust
- [ ] No TODO/FIXME comments

Best Practices:
- [ ] DRY principle followed
- [ ] Single Responsibility Principle
- [ ] Clear function/variable names
- [ ] Adequate comments

Testing:
- [ ] All tests passing
- [ ] Coverage ≥80%
- [ ] Edge cases covered

DELIVERABLES:
1. Review report with:
   - Issues found (P0/P1/P2/P3)
   - Recommendations
   - Approval status (APPROVED/CHANGES_REQUIRED/REJECTED)
2. Specific fix suggestions for issues

TIME BUDGET: 15 minutes

Report findings to Princess.
```

### Phase 4: Spawn Drones

Spawn Drones using the Task tool with constructed prompts:

**Spawning Patterns**:

**Sequential Spawning** (dependencies exist):
```python
# Step 1: Spawn Tester FIRST (TDD)
tests = Task(
    subagent_type="tester",
    description="Write auth tests (TDD)",
    prompt=tester_prompt
)

# Wait for tests to complete...

# Step 2: Spawn Coder to implement
code = Task(
    subagent_type="coder",
    description="Implement auth to pass tests",
    prompt=f"Implement to pass these tests: {tests}"
)

# Wait for code to complete...

# Step 3: Spawn Reviewer
review = Task(
    subagent_type="reviewer",
    description="Review auth implementation",
    prompt=reviewer_prompt
)
```

**Parallel Spawning** (independent tasks):
```python
# Spawn multiple Drones in parallel (single message, multiple Task calls)
Task(subagent_type="frontend-dev", description="Build UI", prompt=frontend_prompt)
Task(subagent_type="backend-dev", description="Build API", prompt=backend_prompt)
Task(subagent_type="docs-writer", description="Write docs", prompt=docs_prompt)
```

**Conditional Spawning** (based on context):
```python
# If debug route, spawn debugger
if route == "debug":
    Task(subagent_type="debugger", description="Fix bug", prompt=debugger_prompt)
# If development route, spawn coder
else:
    Task(subagent_type="coder", description="Implement feature", prompt=coder_prompt)
```

### Phase 5: Coordinate Drone Outputs

After Drones complete work, coordinate their outputs:

**Actions**:
1. Collect Drone results
2. Validate deliverables meet requirements
3. Integrate Drone outputs (if multiple Drones)
4. Update memory with completed work
5. Report to Princess with summary

**Coordination Example**:
```python
# Tester completed
test_results = {
    "total_tests": 42,
    "coverage": 0.87,
    "files": ["/tests/test_auth.py"]
}

# Coder completed
code_results = {
    "files_created": ["/src/auth.py", "/src/tokens.py"],
    "tests_passing": True,
    "loc": 245
}

# Reviewer completed
review_results = {
    "status": "APPROVED",
    "issues": [],
    "nasa_compliance": 0.98
}

# Integrate and report to Princess
princess_report = {
    "phase": "Backend Implementation",
    "status": "complete",
    "drones_used": ["tester", "coder", "reviewer"],
    "deliverables": {
        "tests": test_results,
        "code": code_results,
        "review": review_results
    },
    "quality": "PASS"  # All audits passed
}
```

## Default Drones by Princess

Each Princess has default Drones for common tasks:

### Princess-Coordination Defaults

**Default Team**: researcher, spec-writer, architect

**Common Patterns**:
- **Research Task**: researcher + architect
- **Spec Writing**: spec-writer + researcher
- **Architecture Design**: architect + pseudocode-writer + spec-writer

### Princess-Dev Defaults

**Default Team**: coder, tester, reviewer

**Common Patterns**:
- **TDD Workflow**: tester (first) → coder → reviewer
- **Frontend**: frontend-dev + tester + reviewer
- **Backend**: backend-dev + tester + security-manager
- **Bug Fix**: debugger + tester + reviewer
- **Integration**: integration-engineer + tester + reviewer

### Princess-Quality Defaults

**Default Team**: theater-detector, nasa-enforcer, docs-writer

**Common Patterns**:
- **Quality Audit**: theater-detector + nasa-enforcer + code-analyzer
- **Security Audit**: security-manager + reviewer
- **Documentation**: docs-writer + reviewer
- **Deployment**: devops + infrastructure-ops + release-manager

## Integration with Princess-Summoning Skill

This skill is invoked BY Princess agents (spawned via princess-summoning):

**Workflow**:
1. Queen spawns Princess (via princess-summoning skill)
2. Princess analyzes task requirements
3. Princess invokes drone-selection skill to find best Drones
4. Princess spawns selected Drones with specific prompts
5. Princess coordinates Drone outputs
6. Princess reports results to Queen

**Example Integration**:
```markdown
# In princess-summoning skill:
"Princess, use drone-selection skill to find best Drones for this task"

# Princess then uses drone-selection:
drones = find_drones_for_task(task, loop)
for drone_id in drones[:3]:
    spawn_drone(drone_id, task_context)
```

## Helper Scripts & Resources

### Scripts

**drone_selector.py** - Wraps agent_registry.py:
```python
from src.coordination.agent_registry import find_drones_for_task, get_drone_description

def select_drones(task: str, loop: str, max_drones: int = 5) -> List[str]:
    """Select top N Drones for task."""
    return find_drones_for_task(task, loop)[:max_drones]

def get_drone_info(drone_id: str) -> str:
    """Get Drone description."""
    return get_drone_description(drone_id)
```

**drone_prompt_builder.py** - Build Drone task prompts:
```python
def build_drone_prompt(
    drone_id: str,
    task: str,
    context: dict,
    loop: str
) -> str:
    """Construct complete Drone task prompt with context."""
    # Load template for drone type
    # Insert context variables
    # Return formatted prompt
    pass
```

### Diagrams

**drone-selection-process.dot** - Visual workflow:
See [diagrams/drone-selection-process.dot](diagrams/drone-selection-process.dot)

## Error Handling

**If no Drones match task**:
1. Fall back to default Drones for Princess
2. Use `coder` as universal fallback for loop2
3. Use `researcher` as universal fallback for loop1
4. Report to Princess for manual selection

**If Drone spawn fails**:
1. Retry spawn (may be temporary issue)
2. If 2 failures, try alternative Drone from recommendations
3. If 3 failures, escalate to Princess

**If Drone requests unknown capability**:
1. Check agent_registry.py for capability
2. Suggest alternative approach
3. Escalate to Princess if cannot proceed

## Success Criteria

Drone selection is successful when:
- ✅ Best Drones identified for task (top 5 recommendations)
- ✅ Appropriate number selected (1-5 based on complexity)
- ✅ Drones spawned with complete context
- ✅ Drone prompts are specific and actionable
- ✅ Drones begin executing assigned work

**Quality Bar**:
- Drone matches task requirements (keyword/task type alignment)
- Drone has necessary capabilities for task
- Drone prompt includes all required context
- Dependencies handled (TDD: tester before coder)
- Escalation protocol is clear

## Related Skills

- **princess-summoning**: Spawns Princesses who use this skill
- **loop1-planning**: Princess-Coordination uses this for research Drones
- **loop2-implementation**: Princess-Dev uses this for dev Drones
- **loop3-quality**: Princess-Quality uses this for quality Drones

---

**Version**: 1.0.0
**Last Updated**: 2025-10-18
**Part of**: SPEK Platform 3-Loop Methodology
**Related Skills**: `princess-summoning`, `loop1-planning`, `loop2-implementation`, `loop3-quality`
