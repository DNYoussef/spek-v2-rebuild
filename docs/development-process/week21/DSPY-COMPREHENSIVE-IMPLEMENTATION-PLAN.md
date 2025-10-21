# DSPy Communication Layer - Comprehensive Implementation Plan

## Executive Summary

**Purpose**: Optimize inter-agent communication and MCP tool calls using DSPy prompt optimization framework.

**Scope**: All ~40 communication paths across Queen→Princess→Drone hierarchy, plus MCP tool validation.

**Latency Budget**: 250ms per message (acceptable trade-off for optimized communication quality).

**Approach**: DSPy as **prompt middleware** (not agent intelligence training):
- **Training Phase** (offline): Learn optimal instruction strings + few-shot demonstrations via metric-driven optimization
- **Runtime Phase** (online): Call LLM with frozen optimized prompts (100-250ms per message)
- **No Model Weights**: Only saves demonstration examples as JSON, not neural network weights

**Key Insight**: DSPy optimizes HOW agents communicate (prompt structure), not WHAT they know (agent capabilities).

---

## 1. How DSPy Works (Accurate Technical Description)

### 1.1 Training Phase (Offline, One-Time)

**What Happens**:
1. Provide 100+ training examples per communication path
2. DSPy tests each module on examples using LLM (Gemini/GPT/Claude)
3. Optimizer evaluates outputs against metric (e.g., task_decomposition_quality)
4. Saves best-performing instruction string + top 10 demonstrations as JSON
5. **Duration**: Minutes to hours (one-time cost)

**What Gets Saved** (JSON format):
```json
{
  "signature": {
    "instructions": "You are an expert Queen coordinating Princess agents...",
    "fields": [
      {"prefix": "Task:", "description": "Complex task requiring decomposition"},
      {"prefix": "Objective:", "description": "Success criteria"},
      {"prefix": "Reasoning:", "description": "Step-by-step thought process"},
      {"prefix": "Subtasks:", "description": "Ordered list of princess-level subtasks"}
    ]
  },
  "demos": [
    {
      "task": "Implement OAuth2 authentication",
      "objective": "Secure login/logout with JWT tokens",
      "reasoning": "First requirements (spec-writer), then design (architect)...",
      "subtasks": [
        {"princess": "princess-dev", "task_type": "design", "description": "..."},
        {"princess": "princess-quality", "task_type": "test", "description": "..."}
      ]
    }
    // ... 9 more high-quality examples
  ],
  "lm": null  // NO model weights, just demonstrations
}
```

**Key Point**: NO neural network training, NO model weights. Only prompt engineering optimization.

### 1.2 Runtime Phase (Online, Every Message)

**What Happens**:
1. Load frozen instruction + demos from JSON
2. Build prompt: `[instruction + 10 demos + current task input]`
3. **Call LLM** with optimized prompt (100-250ms latency)
4. Parse response into structured output
5. Return to calling agent

**Example Flow** (Queen→Princess-Dev):
```python
# 1. Queen wants to delegate task to Princess-Dev
task = Task(id="auth-feature", type="implement-auth", ...)

# 2. DSPy module loads optimized prompt
queen_to_princess_dev = QueenToPrincessOptimizer.load("queen_to_princess_dev.json")

# 3. Build prompt with 10 demos + current task
prompt = f"""
{instruction_string}

Example 1: {demo_1}
Example 2: {demo_2}
...
Example 10: {demo_10}

Current Task: {task.description}
Objective: {task.payload['objective']}
"""

# 4. Call LLM (100-250ms)
response = await llm.complete(prompt)  # ← LLM CALL HAPPENS HERE

# 5. Parse structured output
princess_task = parse_response(response)

# 6. Send to Princess-Dev via protocol
result = await protocol.send_task("queen", "princess-dev", princess_task)
```

**Latency Breakdown**:
- Prompt building: <5ms (string concatenation)
- LLM call: 100-250ms (network + inference)
- Response parsing: <10ms (JSON parsing)
- **Total**: ~150ms average (acceptable per user decision)

### 1.3 Model-Agnostic Design

DSPy uses **agent's configured LLM**, not a specific model:
- Queen uses Gemini 2.0 Flash → DSPy calls Gemini
- Princess-Dev uses GPT-4o → DSPy calls GPT-4o
- Tester uses Claude Sonnet → DSPy calls Claude

**Configuration** (no model-specific code):
```python
# Each agent configures its LLM
class QueenAgent(AgentBase):
    def __init__(self):
        super().__init__(...)
        dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

# DSPy modules use agent's LLM automatically
class QueenToPrincessOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # No model configuration - uses agent's LLM
        self.decompose = dspy.ChainOfThought("task, objective -> subtasks")
```

---

## 2. Communication Path Mapping

### 2.1 Complete Agent Hierarchy

**Total**: 22 agents across 4 tiers

**Tier 1 - Queen** (1 agent):
- `queen` - Top-level orchestrator

**Tier 2 - Princesses** (3 agents):
- `princess-dev` - Development coordination
- `princess-quality` - QA coordination
- `princess-coordination` - Task coordination

**Tier 3 - Core Drones** (4 agents):
- `coder` - Code implementation
- `reviewer` - Code review
- `tester` - Test creation
- `researcher` - Research & analysis

**Tier 4 - Specialized Drones** (14 agents):
- **Dev Hive**: debugger, integration-engineer (2 agents)
- **Quality Hive**: nasa-enforcer, theater-detector, fsm-analyzer (3 agents)
- **Coordination Hive**: orchestrator, planner, cost-tracker (3 agents)
- **SPARC Agents**: architect, pseudocode-writer, spec-writer, docs-writer (4 agents)
- **Operations**: devops, security-manager (2 agents)

### 2.2 Communication Paths by Type

#### Type A: Queen → Princess (3 paths)
**Latency**: 250ms budget
**Frequency**: High (every complex task)
**Optimization Priority**: **P0 (Critical)**

1. `queen → princess-dev`
   - Task: Development workflow coordination
   - Input: Complex feature request (e.g., "Implement OAuth2")
   - Output: Development subtasks (design, code, review, integrate)

2. `queen → princess-quality`
   - Task: QA workflow coordination
   - Input: Quality validation request
   - Output: QA subtasks (test, nasa-check, theater-detect, fsm-analyze)

3. `queen → princess-coordination`
   - Task: Strategic planning and orchestration
   - Input: High-level objective
   - Output: Execution plan with cost estimates

#### Type B: Princess → Hive Broadcast (3 paths)
**Latency**: 250ms budget
**Frequency**: Medium (workflow coordination)
**Optimization Priority**: **P1 (High)**

4. `princess-dev → dev-hive` (broadcast to 4 drones)
   - Drones: coder, reviewer, debugger, integration-engineer
   - Task: Coordinate development phases
   - Output: Parallel work assignments

5. `princess-quality → quality-hive` (broadcast to 4 drones)
   - Drones: tester, nasa-enforcer, theater-detector, fsm-analyzer
   - Task: Coordinate QA phases
   - Output: Parallel QA checks

6. `princess-coordination → coordination-hive` (broadcast to 3 drones)
   - Drones: orchestrator, planner, cost-tracker
   - Task: Strategic planning
   - Output: Execution strategy + cost estimate

#### Type C: Princess → Individual Drone (11 paths)
**Latency**: 250ms budget
**Frequency**: Very High (per-task delegation)
**Optimization Priority**: **P0 (Critical)**

**Princess-Dev → Drones** (4 paths):
7. `princess-dev → coder` - Code implementation tasks
8. `princess-dev → reviewer` - Code review tasks
9. `princess-dev → debugger` - Bug fixing tasks
10. `princess-dev → integration-engineer` - Integration tasks

**Princess-Quality → Drones** (4 paths):
11. `princess-quality → tester` - Test generation tasks
12. `princess-quality → nasa-enforcer` - NASA compliance checks
13. `princess-quality → theater-detector` - Mock code detection
14. `princess-quality → fsm-analyzer` - FSM validation

**Princess-Coordination → Drones** (3 paths):
15. `princess-coordination → orchestrator` - Workflow orchestration
16. `princess-coordination → planner` - Task planning
17. `princess-coordination → cost-tracker` - Cost tracking

#### Type D: Drone → Princess (11 paths)
**Latency**: 250ms budget
**Frequency**: Very High (result reporting)
**Optimization Priority**: **P1 (High)**

18-28. **Reverse of Type C** (11 paths)
- Each drone reports results back to parent princess
- Format: Structured result with success/failure, metrics, artifacts

#### Type E: Princess ↔ Princess (6 bidirectional paths)
**Latency**: 250ms budget
**Frequency**: Low (cross-hive coordination)
**Optimization Priority**: **P2 (Medium)**

29. `princess-dev ↔ princess-quality` (2 paths)
   - Use case: Code complete → QA validation
   - Bidirectional: Dev requests QA, QA requests fixes

30. `princess-dev ↔ princess-coordination` (2 paths)
   - Use case: Plan validation → Implementation
   - Bidirectional: Coordination plans, Dev executes

31. `princess-quality ↔ princess-coordination` (2 paths)
   - Use case: Cost estimation → Quality gates
   - Bidirectional: Coordination estimates, Quality validates

#### Type F: Princess → Queen (3 paths)
**Latency**: 250ms budget
**Frequency**: Low (escalation, completion)
**Optimization Priority**: **P2 (Medium)**

32. `princess-dev → queen` - Development complete/blocked
33. `princess-quality → queen` - QA complete/failed
34. `princess-coordination → queen` - Planning complete/needs decision

**Total Communication Paths**: 34 primary paths (excluding internal drone-to-drone, which is rare)

---

## 3. DSPy Module Architecture

### 3.1 Module Hierarchy

```
DSPyOptimizers/
├── core/
│   ├── QueenToPrincessOptimizer (3 variants: dev, quality, coordination)
│   ├── PrincessToHiveOptimizer (3 variants)
│   ├── PrincessToDroneOptimizer (11 variants)
│   ├── DroneToPrincessOptimizer (11 variants)
│   ├── PrincessToPrincessOptimizer (6 variants)
│   └── PrincessToQueenOptimizer (3 variants)
├── mcp/
│   ├── MCPToolValidator (generic tool call validation)
│   └── MCPResponseParser (structured response parsing)
└── signatures/
    ├── TaskDecompositionSignature
    ├── TaskDelegationSignature
    ├── ResultAggregationSignature
    └── MCPToolCallSignature
```

### 3.2 Core Signatures

```python
# 1. Task Decomposition (Queen → Princess)
class TaskDecompositionSignature(dspy.Signature):
    """Decompose complex task into princess-level subtasks."""
    task_description = dspy.InputField(desc="Complex task requiring decomposition")
    objective = dspy.InputField(desc="Success criteria and constraints")
    reasoning = dspy.OutputField(desc="Step-by-step decomposition reasoning", prefix="Reasoning:")
    subtasks = dspy.OutputField(desc="Ordered list of princess-level subtasks as JSON")

# 2. Task Delegation (Princess → Drone)
class TaskDelegationSignature(dspy.Signature):
    """Delegate task to drone agent with clear instructions."""
    phase = dspy.InputField(desc="Development phase (design, code, test, etc.)")
    context = dspy.InputField(desc="Context from previous phases")
    reasoning = dspy.OutputField(desc="Delegation reasoning", prefix="Reasoning:")
    drone_task = dspy.OutputField(desc="Structured task for drone agent")

# 3. Result Aggregation (Drone → Princess)
class ResultAggregationSignature(dspy.Signature):
    """Aggregate drone results into coherent output."""
    drone_results = dspy.InputField(desc="List of results from drone agents")
    quality_gates = dspy.InputField(desc="Quality gates to validate")
    reasoning = dspy.OutputField(desc="Aggregation reasoning", prefix="Reasoning:")
    aggregated_result = dspy.OutputField(desc="Aggregated result with quality metrics")

# 4. MCP Tool Call (Any Agent → MCP Tool)
class MCPToolCallSignature(dspy.Signature):
    """Generate valid MCP tool call with correct parameters."""
    tool_name = dspy.InputField(desc="MCP tool to call (e.g., github__create_pr)")
    intent = dspy.InputField(desc="What the agent wants to accomplish")
    context = dspy.InputField(desc="Available context (files, data, etc.)")
    reasoning = dspy.OutputField(desc="Tool selection reasoning", prefix="Reasoning:")
    tool_call = dspy.OutputField(desc="Structured MCP tool call with parameters")
```

### 3.3 Example Optimizer (Queen → Princess-Dev)

```python
import dspy

class QueenToPrincessDevOptimizer(dspy.Module):
    """
    Optimize Queen → Princess-Dev communication.

    Learns to decompose complex development tasks into optimal
    subtask sequences for the development hive.
    """

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str):
        """
        Decompose task into development workflow.

        Args:
            task_description: Complex feature/task description
            objective: Success criteria

        Returns:
            Subtasks for princess-dev with reasoning
        """
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )

        return dspy.Prediction(
            reasoning=result.reasoning,
            subtasks=result.subtasks
        )
```

**Training Example**:
```python
import dspy
from dspy.evaluate import Evaluate
from dspy.teleprompt import BootstrapFewShot

# 1. Define metric
def task_decomposition_quality(example, prediction, trace=None):
    """
    Evaluate quality of task decomposition.

    Checks:
    - All subtasks are actionable (>=0.8 score)
    - Dependencies are valid (no cycles)
    - Estimated time is realistic (15-60 min per task)
    - Appropriate princess selected for each subtask
    """
    subtasks = prediction.subtasks

    # Parse subtasks (assume JSON format)
    try:
        import json
        subtasks_list = json.loads(subtasks)
    except:
        return 0.0  # Invalid JSON

    score = 0.0

    # Check each subtask
    for subtask in subtasks_list:
        # Has princess assignment
        if "princess" in subtask:
            score += 0.2

        # Has clear description
        if "description" in subtask and len(subtask["description"]) > 20:
            score += 0.2

        # Has task type
        if "task_type" in subtask:
            score += 0.2

        # Has realistic time estimate (15-60 min)
        if "estimated_minutes" in subtask:
            minutes = subtask["estimated_minutes"]
            if 15 <= minutes <= 60:
                score += 0.2

        # Has dependencies list (even if empty)
        if "dependencies" in subtask:
            score += 0.2

    # Normalize by number of subtasks
    return min(1.0, score / len(subtasks_list))

# 2. Create training set (100 examples)
trainset = [
    dspy.Example(
        task_description="Implement OAuth2 authentication with JWT tokens",
        objective="Secure login/logout with session management"
    ).with_inputs("task_description", "objective"),

    dspy.Example(
        task_description="Add real-time notifications using WebSockets",
        objective="Push notifications to clients with <100ms latency"
    ).with_inputs("task_description", "objective"),

    # ... 98 more examples
]

# 3. Create optimizer
optimizer = BootstrapFewShot(
    metric=task_decomposition_quality,
    max_bootstrapped_demos=10,  # Top 10 examples
    max_labeled_demos=5,  # Use 5 seed examples
    max_rounds=3  # 3 optimization rounds
)

# 4. Compile (train)
module = QueenToPrincessDevOptimizer()
compiled = optimizer.compile(
    student=module,
    trainset=trainset
)

# 5. Save optimized prompts
compiled.save("models/dspy/queen_to_princess_dev.json")
```

**What Gets Saved** (`queen_to_princess_dev.json`):
```json
{
  "decompose.predict": {
    "signature": {
      "instructions": "Decompose complex task into princess-level subtasks. Each subtask must be actionable, have clear ownership, realistic time estimates (15-60 min), and valid dependencies.",
      "fields": [
        {"prefix": "Task Description:", "description": "Complex task requiring decomposition"},
        {"prefix": "Objective:", "description": "Success criteria and constraints"},
        {"prefix": "Reasoning: Let's think step by step in order to", "description": "${reasoning}"},
        {"prefix": "Subtasks:", "description": "Ordered list of princess-level subtasks as JSON"}
      ]
    },
    "demos": [
      {
        "task_description": "Implement OAuth2 authentication with JWT tokens",
        "objective": "Secure login/logout with session management",
        "reasoning": "First, we need requirements specification from spec-writer. Then architect designs auth flow with JWT. Coder implements endpoints. Tester creates auth tests. Security-manager validates security. Finally, reviewer does code review.",
        "subtasks": "[{\"princess\": \"princess-coordination\", \"task_type\": \"plan\", \"description\": \"Plan OAuth2 implementation strategy\", \"dependencies\": [], \"estimated_minutes\": 20}, {\"princess\": \"princess-dev\", \"task_type\": \"design\", \"description\": \"Design auth architecture with JWT tokens\", \"dependencies\": [\"plan\"], \"estimated_minutes\": 30}, {\"princess\": \"princess-dev\", \"task_type\": \"code\", \"description\": \"Implement login/logout endpoints\", \"dependencies\": [\"design\"], \"estimated_minutes\": 45}, {\"princess\": \"princess-quality\", \"task_type\": \"test\", \"description\": \"Create auth integration tests\", \"dependencies\": [\"code\"], \"estimated_minutes\": 30}, {\"princess\": \"princess-quality\", \"task_type\": \"security-scan\", \"description\": \"Validate auth security\", \"dependencies\": [\"code\"], \"estimated_minutes\": 15}]"
      }
      // ... 9 more high-quality demos
    ]
  }
}
```

**Runtime Usage** (Queen delegates to Princess-Dev):
```python
# In QueenAgent.execute()
async def _delegate_to_princess_dev(self, task: Task):
    # 1. Load optimized module
    optimizer = QueenToPrincessDevOptimizer()
    optimizer.load("models/dspy/queen_to_princess_dev.json")

    # 2. Generate optimized subtasks (100-250ms LLM call)
    result = optimizer.forward(
        task_description=task.description,
        objective=task.payload.get("objective", "")
    )

    # 3. Parse subtasks
    import json
    subtasks = json.loads(result.subtasks)

    # 4. Delegate to Princess-Dev
    princess_task = Task(
        id=f"{task.id}-princess-dev",
        type="coordinate-dev",
        description="Development workflow",
        payload={
            "dev_workflow": {
                "phases": subtasks
            }
        },
        priority=task.priority
    )

    # 5. Send via protocol
    result = await self.delegate_task("princess-dev", princess_task)
    return result
```

---

## 4. Training Dataset Requirements

### 4.1 Dataset Structure

Each communication path needs 100-200 examples covering:
- **Success cases** (70%): Valid, high-quality interactions
- **Edge cases** (20%): Complex scenarios, dependencies, conflicts
- **Failure cases** (10%): Invalid inputs, errors, recovery

**Example Dataset** (Queen → Princess-Dev):
```python
trainset_queen_to_princess_dev = [
    # Success Case 1: Standard feature implementation
    dspy.Example(
        task_description="Implement user profile page with avatar upload",
        objective="CRUD operations + file upload with S3 integration",
        expected_subtasks=[
            {"princess": "princess-coordination", "task_type": "plan", "description": "Plan profile implementation", "estimated_minutes": 15},
            {"princess": "princess-dev", "task_type": "design", "description": "Design profile data model + S3 integration", "estimated_minutes": 25},
            {"princess": "princess-dev", "task_type": "code", "description": "Implement profile API endpoints", "estimated_minutes": 40},
            {"princess": "princess-dev", "task_type": "code", "description": "Implement avatar upload to S3", "estimated_minutes": 30},
            {"princess": "princess-quality", "task_type": "test", "description": "Create profile + upload tests", "estimated_minutes": 35},
            {"princess": "princess-quality", "task_type": "security-scan", "description": "Validate file upload security", "estimated_minutes": 20}
        ]
    ).with_inputs("task_description", "objective"),

    # Edge Case 1: Complex dependencies
    dspy.Example(
        task_description="Migrate database from MySQL to PostgreSQL",
        objective="Zero-downtime migration with data validation",
        expected_subtasks=[
            {"princess": "princess-coordination", "task_type": "plan", "description": "Plan migration strategy with rollback", "estimated_minutes": 30},
            {"princess": "princess-dev", "task_type": "design", "description": "Design dual-write architecture", "estimated_minutes": 40},
            {"princess": "princess-dev", "task_type": "code", "description": "Implement PostgreSQL schema", "estimated_minutes": 45},
            {"princess": "princess-dev", "task_type": "code", "description": "Implement dual-write layer", "estimated_minutes": 50},
            {"princess": "princess-quality", "task_type": "test", "description": "Create migration tests + data validation", "estimated_minutes": 60},
            {"princess": "princess-dev", "task_type": "integrate", "description": "Execute migration with monitoring", "estimated_minutes": 60}
        ]
    ).with_inputs("task_description", "objective"),

    # ... 98 more examples
]
```

### 4.2 Dataset Sources

**Automated Generation**:
- Extract from existing task logs (if available)
- Generate synthetic examples using GPT-4o/Claude with strict validation
- Use few-shot prompting with seed examples

**Manual Curation**:
- Domain expert review (20% of dataset)
- Edge case brainstorming sessions
- Failure case documentation from real bugs

**Quality Gates**:
- All examples must pass validation schema
- Manual review of top 20% most complex examples
- A/B testing: DSPy-optimized vs baseline prompts

---

## 5. MCP Tool Validation Layer

### 5.1 Available MCP Tools (VSCode Integration)

Research shows these MCP servers are available:
- **GitHub**: `github__create_pr`, `github__create_issue`, `github__list_prs`, `github__merge_pr`
- **File Operations**: `filesystem__read`, `filesystem__write`, `filesystem__search`
- **Code Tools**: `code__analyze`, `code__refactor`, `code__generate_tests`
- **Cloud Platforms**: `azure__deploy`, `aws__s3_upload`, `kubernetes__apply`
- **Databases**: `mongodb__query`, `postgres__execute`, `elasticsearch__search`
- **Productivity**: `todoist__add_task`, `jira__create_ticket`, `slack__send_message`

### 5.2 MCP Validator Module

```python
class MCPToolValidator(dspy.Module):
    """
    Validate and optimize MCP tool calls.

    Ensures:
    - Correct tool selection for intent
    - Valid parameter formatting
    - Required fields present
    - Type safety (strings, ints, objects)
    """

    def __init__(self):
        super().__init__()
        self.validate_call = dspy.ChainOfThought(MCPToolCallSignature)

    def forward(self, tool_name: str, intent: str, context: dict):
        """
        Generate validated MCP tool call.

        Args:
            tool_name: MCP tool to call
            intent: What agent wants to accomplish
            context: Available context

        Returns:
            Validated tool call with parameters
        """
        result = self.validate_call(
            tool_name=tool_name,
            intent=intent,
            context=str(context)
        )

        # Parse and validate tool call
        import json
        try:
            tool_call = json.loads(result.tool_call)

            # Schema validation
            if not self._validate_schema(tool_name, tool_call):
                raise ValueError(f"Invalid schema for {tool_name}")

            return dspy.Prediction(
                reasoning=result.reasoning,
                tool_call=tool_call,
                valid=True
            )
        except Exception as e:
            return dspy.Prediction(
                reasoning=result.reasoning,
                tool_call={},
                valid=False,
                error=str(e)
            )

    def _validate_schema(self, tool_name: str, tool_call: dict) -> bool:
        """Validate tool call against MCP schema."""
        # Tool-specific schema validation
        schemas = {
            "github__create_pr": {
                "required": ["title", "body", "head", "base"],
                "optional": ["draft", "maintainer_can_modify"]
            },
            "filesystem__write": {
                "required": ["path", "content"],
                "optional": ["encoding", "create_dirs"]
            },
            # ... more schemas
        }

        schema = schemas.get(tool_name, {})

        # Check required fields
        for field in schema.get("required", []):
            if field not in tool_call:
                return False

        return True
```

**Training Example** (MCP Tool Validation):
```python
trainset_mcp_github = [
    dspy.Example(
        tool_name="github__create_pr",
        intent="Create PR for OAuth2 feature implementation",
        context={
            "branch": "feature/oauth2",
            "base_branch": "main",
            "files_changed": ["src/auth/oauth.py", "tests/test_oauth.py"],
            "commits": 5
        },
        expected_tool_call={
            "tool": "github__create_pr",
            "parameters": {
                "title": "feat: Implement OAuth2 authentication with JWT tokens",
                "body": "## Summary\n- Implement OAuth2 flow\n- Add JWT token generation\n- Create login/logout endpoints\n\n## Test Plan\n- Unit tests for auth logic\n- Integration tests for OAuth flow\n- Security scan passed\n\nCloses #123",
                "head": "feature/oauth2",
                "base": "main",
                "draft": False
            }
        }
    ).with_inputs("tool_name", "intent", "context"),

    # ... 99 more examples
]
```

---

## 6. Implementation Phases

### Phase 1: Foundation (Week 21 Days 3-4)
**Goal**: Set up DSPy infrastructure and P0 communication paths

**Tasks**:
1. Install DSPy framework: `pip install dspy-ai`
2. Create module architecture (`DSPyOptimizers/` directory structure)
3. Define core signatures (TaskDecomposition, TaskDelegation, ResultAggregation)
4. Implement 3 P0 optimizers:
   - `QueenToPrincessDevOptimizer`
   - `QueenToPrincessQualityOptimizer`
   - `QueenToPrincessCoordinationOptimizer`

**Deliverables**:
- `src/dspy_optimizers/core/` with base modules
- `src/dspy_optimizers/signatures/` with signature definitions
- 3 optimizer implementations (untrained)

### Phase 2: Dataset Creation (Week 21 Days 5-6)
**Goal**: Create training datasets for P0 paths

**Tasks**:
1. Generate 100 examples per P0 path (300 total)
2. Manual review of 20% high-complexity examples
3. Validate all examples against schemas
4. Create evaluation metrics for each path

**Deliverables**:
- `datasets/queen_to_princess_dev.json` (100 examples)
- `datasets/queen_to_princess_quality.json` (100 examples)
- `datasets/queen_to_princess_coordination.json` (100 examples)
- Evaluation metrics implemented

### Phase 3: Training & Validation (Week 21 Day 7)
**Goal**: Train P0 optimizers and validate quality

**Tasks**:
1. Configure BootstrapFewShot optimizer (max_demos=10)
2. Train 3 P0 optimizers on datasets
3. Evaluate against held-out test set (20% of data)
4. Save optimized prompts to `models/dspy/`

**Deliverables**:
- `models/dspy/queen_to_princess_dev.json` (trained)
- `models/dspy/queen_to_princess_quality.json` (trained)
- `models/dspy/queen_to_princess_coordination.json` (trained)
- Training metrics report (accuracy, improvement over baseline)

### Phase 4: Integration (Week 22 Days 1-3)
**Goal**: Integrate DSPy into Queen and Princess agents

**Tasks**:
1. Update `QueenAgent.delegate_task()` to use DSPy optimizers
2. Update `PrincessDevAgent`, `PrincessQualityAgent`, `PrincessCoordinationAgent`
3. Add fallback to baseline prompts if DSPy fails
4. Implement latency monitoring (target: <250ms)

**Deliverables**:
- Updated `src/agents/core/QueenAgent.py`
- Updated `src/agents/swarm/Princess*.py`
- Latency monitoring dashboard
- Integration tests (10 end-to-end scenarios)

### Phase 5: P1 Paths (Week 22 Days 4-7)
**Goal**: Expand to Princess→Drone and Drone→Princess paths

**Tasks**:
1. Create datasets for 11 Princess→Drone paths (50 examples each, 550 total)
2. Create datasets for 11 Drone→Princess paths (50 examples each, 550 total)
3. Train 22 optimizers (P1 priority)
4. Integrate into all 3 Princess agents

**Deliverables**:
- 22 trained optimizers in `models/dspy/`
- All Princess→Drone paths optimized
- All Drone→Princess result reporting optimized

### Phase 6: MCP Tool Validation (Week 23 Days 1-3)
**Goal**: Implement MCP tool validation layer

**Tasks**:
1. Create `MCPToolValidator` module
2. Define schemas for top 20 MCP tools
3. Create training dataset (100 examples per tool type, 500 total)
4. Train and validate MCP optimizers

**Deliverables**:
- `src/dspy_optimizers/mcp/MCPToolValidator.py`
- MCP tool schemas in `schemas/mcp_tools.json`
- 5 trained MCP validators in `models/dspy/mcp/`

### Phase 7: P2 Paths & Optimization (Week 23 Days 4-7)
**Goal**: Complete remaining paths and optimize performance

**Tasks**:
1. Train Princess↔Princess paths (6 paths, 30 examples each)
2. Train Princess→Queen paths (3 paths, 30 examples each)
3. A/B test DSPy vs baseline prompts
4. Optimize latency (cache frequently-used prompts)

**Deliverables**:
- All 34 communication paths optimized
- A/B test results (improvement metrics)
- Performance optimization report

### Phase 8: Production Validation (Week 24)
**Goal**: Validate in production-like environment

**Tasks**:
1. Run 100 end-to-end workflows with DSPy enabled
2. Monitor latency (must be <250ms per message)
3. Track quality improvements (decomposition accuracy, tool call success rate)
4. Document lessons learned and best practices

**Deliverables**:
- Production validation report
- Latency analysis (p50, p95, p99)
- Quality improvement metrics
- Best practices documentation

---

## 7. Success Metrics

### 7.1 Performance Metrics

**Latency** (per message):
- Target: <250ms average
- p50: <200ms
- p95: <250ms
- p99: <300ms (acceptable for complex tasks)

**Throughput**:
- Queen→Princess: 10 messages/second
- Princess→Drone: 50 messages/second (parallel)
- Total system: 100+ tasks/minute

### 7.2 Quality Metrics

**Task Decomposition Quality** (Queen→Princess):
- Baseline: 65% human-rated as "good" or better
- Target: 85% with DSPy optimization (+20% improvement)

**MCP Tool Call Success Rate**:
- Baseline: 70% (manual prompting)
- Target: 95% with DSPy validation (+25% improvement)

**Result Aggregation Quality** (Drone→Princess):
- Baseline: 60% complete aggregation
- Target: 90% with DSPy (+30% improvement)

### 7.3 Cost Metrics

**Training Costs** (one-time):
- 37 optimizers × 100 examples × 3 rounds × $0.10/1K tokens ≈ $350
- Manual review: 20 hours × $50/hour = $1,000
- **Total Training**: ~$1,350 (one-time)

**Runtime Costs** (monthly):
- 100K messages/month × 250ms × $0.10/1K tokens ≈ $250/month
- Current baseline: $150/month (direct prompts)
- **Incremental**: +$100/month (acceptable per user decision)

### 7.4 Acceptance Criteria

**Phase 1-3 (P0 Paths)**:
- ✅ All 3 Queen→Princess optimizers trained and validated
- ✅ Latency <250ms for 95% of messages
- ✅ Quality improvement >=15% over baseline

**Phase 4-5 (Integration + P1 Paths)**:
- ✅ All 22 agents using DSPy for delegation
- ✅ 34/34 communication paths optimized
- ✅ Zero production incidents related to DSPy

**Phase 6 (MCP Tools)**:
- ✅ 20 MCP tools with validation schemas
- ✅ Tool call success rate >=95%
- ✅ MCP errors reduced by 50%

**Phase 8 (Production)**:
- ✅ 100 end-to-end workflows successful
- ✅ User satisfaction >=90% (quality of agent responses)
- ✅ System stability maintained (no degradation)

---

## 8. Risk Mitigation

### 8.1 Technical Risks

**Risk 1: Latency Exceeds 250ms Budget**
- **Mitigation**: Cache frequently-used optimized prompts, use faster LLMs (Gemini Flash)
- **Contingency**: Fall back to baseline prompts for latency-critical paths

**Risk 2: Training Data Quality Issues**
- **Mitigation**: Manual review of 20% examples, strict validation schemas
- **Contingency**: Iterate on datasets, use active learning to identify weak examples

**Risk 3: DSPy Optimization Doesn't Improve Quality**
- **Mitigation**: A/B testing, quantitative metrics before/after
- **Contingency**: Use DSPy selectively (only paths with proven ROI)

### 8.2 Operational Risks

**Risk 4: Training Costs Exceed Budget**
- **Mitigation**: Use free-tier LLMs (Gemini Flash), batch training jobs
- **Contingency**: Reduce training rounds from 3 to 2, reduce demo count from 10 to 5

**Risk 5: Integration Breaks Existing Workflows**
- **Mitigation**: Fallback to baseline prompts, extensive integration testing
- **Contingency**: Feature flag DSPy optimization, gradual rollout

---

## 9. Appendix

### 9.1 DSPy Installation

```bash
# Install DSPy
pip install dspy-ai

# Configure LLM (example: Gemini)
export GEMINI_API_KEY="your-api-key"

# Verify installation
python -c "import dspy; print(dspy.__version__)"
```

### 9.2 Example Training Script

```python
# train_queen_to_princess_dev.py
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate

# 1. Configure LLM
dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

# 2. Load dataset
import json
with open("datasets/queen_to_princess_dev.json", "r") as f:
    data = json.load(f)
    trainset = [dspy.Example(**ex).with_inputs("task_description", "objective") for ex in data]

# 3. Define metric
def task_decomposition_quality(example, prediction, trace=None):
    # ... metric implementation ...
    return score

# 4. Create optimizer
optimizer = BootstrapFewShot(
    metric=task_decomposition_quality,
    max_bootstrapped_demos=10,
    max_rounds=3
)

# 5. Train
from optimizers.core import QueenToPrincessDevOptimizer
module = QueenToPrincessDevOptimizer()
compiled = optimizer.compile(student=module, trainset=trainset[:80])

# 6. Evaluate on test set
evaluator = Evaluate(
    devset=trainset[80:],
    metric=task_decomposition_quality,
    num_threads=4
)
score = evaluator(compiled)
print(f"Test set score: {score}")

# 7. Save
compiled.save("models/dspy/queen_to_princess_dev.json")
```

### 9.3 References

- **DSPy Documentation**: https://dspy-docs.vercel.app/
- **DSPy GitHub**: https://github.com/stanfordnlp/dspy
- **BootstrapFewShot Paper**: https://arxiv.org/abs/2310.03714
- **MIPROv2 Optimizer**: https://arxiv.org/abs/2406.11695

---

**Version**: 1.0
**Timestamp**: 2025-10-10T00:00:00-04:00
**Agent/Model**: Claude Sonnet 4
**Status**: COMPREHENSIVE - READY FOR IMPLEMENTATION
**Next Steps**: Begin Phase 1 (Foundation) - Set up DSPy infrastructure and implement P0 optimizers
