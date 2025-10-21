# How DSPy Works - Accurate Technical Description

## Executive Summary

DSPy is a **prompt optimization framework**, NOT a model training system. It optimizes HOW agents communicate (prompt structure), not WHAT they know (intelligence/capabilities).

**Key Points**:
- **Training**: Offline process that learns optimal instruction strings + few-shot demonstrations
- **Runtime**: Online process that CALLS LLM with optimized prompts (100-250ms per message)
- **No Model Weights**: Only saves demonstration examples as JSON, not neural network weights
- **Model-Agnostic**: Uses agent's configured LLM (Gemini, GPT, Claude, etc.)

---

## 1. DSPy Components

### 1.1 Signatures
**What**: Task schema defining inputs/outputs (like a function type signature for LLM calls)

**Example**:
```python
class TaskDecompositionSignature(dspy.Signature):
    """Decompose complex task into princess-level subtasks."""
    task_description = dspy.InputField(desc="Complex task requiring decomposition")
    objective = dspy.InputField(desc="Success criteria and constraints")
    reasoning = dspy.OutputField(desc="Step-by-step decomposition reasoning", prefix="Reasoning:")
    subtasks = dspy.OutputField(desc="Ordered list of princess-level subtasks as JSON")
```

**Purpose**: Define the structure of what goes INTO the LLM (inputs) and what comes OUT (outputs).

### 1.2 Modules
**What**: Parameterized LLM calls with learnable slots (instruction string + demonstrations)

**Example**:
```python
class QueenToPrincessOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # Creates a module with learnable instruction + demos
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str):
        # Calls LLM with optimized prompt
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )
        return result
```

**Learnable Parameters**:
- **Instruction String**: System prompt (e.g., "You are an expert Queen coordinating Princess agents...")
- **Demonstrations**: Few-shot examples (10 high-quality task decompositions)

**What's NOT Learned**: Neural network weights, model parameters

### 1.3 Programs
**What**: Pipelines that assemble multiple modules into workflows

**Example**:
```python
class QueenWorkflowProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)
        self.validate = dspy.ChainOfThought(ValidationSignature)
        self.delegate = dspy.ChainOfThought(DelegationSignature)

    def forward(self, complex_task: str):
        # Step 1: Decompose task
        subtasks = self.decompose(task=complex_task)

        # Step 2: Validate subtasks
        validation = self.validate(subtasks=subtasks.subtasks)

        # Step 3: Delegate to princesses
        if validation.valid:
            result = self.delegate(subtasks=subtasks.subtasks)
            return result
```

**Purpose**: Chain multiple LLM calls with different optimized prompts.

### 1.4 Metrics
**What**: Evaluation functions that score LLM outputs (drives optimization)

**Example**:
```python
def task_decomposition_quality(example, prediction, trace=None):
    """
    Score quality of task decomposition (0.0 to 1.0).

    Checks:
    - All subtasks are actionable
    - Dependencies are valid (no cycles)
    - Time estimates are realistic (15-60 min)
    - Appropriate princess assigned
    """
    try:
        subtasks = json.loads(prediction.subtasks)
    except:
        return 0.0  # Invalid JSON

    score = 0.0

    for subtask in subtasks:
        # Check required fields
        if all(k in subtask for k in ["princess", "description", "task_type"]):
            score += 0.3

        # Check time estimate
        if "estimated_minutes" in subtask and 15 <= subtask["estimated_minutes"] <= 60:
            score += 0.2

        # Check dependencies format
        if "dependencies" in subtask and isinstance(subtask["dependencies"], list):
            score += 0.1

    return min(1.0, score / len(subtasks))
```

**Purpose**: Quantify "goodness" of LLM outputs, guide optimizer to select best prompts.

### 1.5 Optimizers
**What**: Algorithms that find best instruction strings + demonstrations

**Common Optimizers**:
- **BootstrapFewShot**: Builds demo pool from training data, selects top N demos
- **MIPROv2**: Bayesian optimization for joint instruction+demo search
- **COPRO**: Coordinate-based optimization of prompts

**Example (BootstrapFewShot)**:
```python
optimizer = BootstrapFewShot(
    metric=task_decomposition_quality,  # How to score outputs
    max_bootstrapped_demos=10,  # Keep top 10 examples
    max_labeled_demos=5,  # Use 5 seed examples
    max_rounds=3  # 3 optimization iterations
)

# Train
compiled = optimizer.compile(
    student=module,  # Module to optimize
    trainset=trainset  # 100 training examples
)
```

---

## 2. Training Phase (Offline, One-Time)

### 2.1 What Happens During Training

**Step 1: Initialize Module**
```python
module = QueenToPrincessOptimizer()
# Module starts with basic instruction (from signature docstring)
# No demonstrations yet
```

**Step 2: Bootstrap Demonstrations**
```python
# Optimizer runs module on training examples
for example in trainset:
    # Call LLM with current prompt
    prediction = module.forward(
        task_description=example.task_description,
        objective=example.objective
    )

    # Score output
    score = metric(example, prediction)

    # Save if high-scoring
    if score > 0.8:
        demos.append({
            "input": example,
            "output": prediction,
            "score": score
        })
```

**Step 3: Select Best Demonstrations**
```python
# Sort by score, take top 10
best_demos = sorted(demos, key=lambda d: d["score"], reverse=True)[:10]
```

**Step 4: Optimize Instruction String** (if using MIPROv2)
```python
# Try different instruction variations
instructions = [
    "You are an expert Queen agent coordinating Princess agents...",
    "As a top-level orchestrator, decompose tasks into princess-level subtasks...",
    "Break down complex tasks into actionable subtasks for princess agents..."
]

best_instruction = None
best_score = 0.0

for instruction in instructions:
    module.set_instruction(instruction)
    score = evaluate_on_devset(module, devset)
    if score > best_score:
        best_score = score
        best_instruction = instruction
```

**Step 5: Save Optimized Prompt**
```python
compiled.save("models/dspy/queen_to_princess_dev.json")
```

### 2.2 What Gets Saved (JSON Format)

```json
{
  "decompose.predict": {
    "signature": {
      "instructions": "You are an expert Queen agent coordinating Princess agents. Decompose complex tasks into actionable princess-level subtasks. Each subtask must have clear ownership (princess assignment), realistic time estimates (15-60 min), valid dependencies (no cycles), and specific task types.",
      "fields": [
        {
          "prefix": "Task Description:",
          "description": "Complex task requiring decomposition"
        },
        {
          "prefix": "Objective:",
          "description": "Success criteria and constraints"
        },
        {
          "prefix": "Reasoning: Let's think step by step in order to",
          "description": "${reasoning}"
        },
        {
          "prefix": "Subtasks:",
          "description": "Ordered list of princess-level subtasks as JSON"
        }
      ]
    },
    "demos": [
      {
        "task_description": "Implement OAuth2 authentication with JWT tokens",
        "objective": "Secure login/logout with session management",
        "reasoning": "First, we need requirements specification from spec-writer. Then architect designs auth flow with JWT. Coder implements endpoints. Tester creates auth tests. Security-manager validates security. Finally, reviewer does code review.",
        "subtasks": "[{\"princess\": \"princess-coordination\", \"task_type\": \"plan\", \"description\": \"Plan OAuth2 implementation strategy\", \"dependencies\": [], \"estimated_minutes\": 20}, {\"princess\": \"princess-dev\", \"task_type\": \"design\", \"description\": \"Design auth architecture with JWT tokens\", \"dependencies\": [\"plan\"], \"estimated_minutes\": 30}, {\"princess\": \"princess-dev\", \"task_type\": \"code\", \"description\": \"Implement login/logout endpoints\", \"dependencies\": [\"design\"], \"estimated_minutes\": 45}, {\"princess\": \"princess-quality\", \"task_type\": \"test\", \"description\": \"Create auth integration tests\", \"dependencies\": [\"code\"], \"estimated_minutes\": 30}]"
      },
      {
        "task_description": "Add real-time notifications using WebSockets",
        "objective": "Push notifications to clients with <100ms latency",
        "reasoning": "Requirements first (spec-writer), then architecture design (architect), WebSocket server implementation (coder), client library (coder), integration tests (tester), and load testing (tester).",
        "subtasks": "[{\"princess\": \"princess-dev\", \"task_type\": \"design\", \"description\": \"Design WebSocket architecture\", \"dependencies\": [], \"estimated_minutes\": 25}, {\"princess\": \"princess-dev\", \"task_type\": \"code\", \"description\": \"Implement WebSocket server\", \"dependencies\": [\"design\"], \"estimated_minutes\": 50}, {\"princess\": \"princess-dev\", \"task_type\": \"code\", \"description\": \"Create client notification library\", \"dependencies\": [\"code\"], \"estimated_minutes\": 40}, {\"princess\": \"princess-quality\", \"task_type\": \"test\", \"description\": \"Create WebSocket integration tests\", \"dependencies\": [\"code\"], \"estimated_minutes\": 35}]"
      }
      // ... 8 more high-quality demonstrations
    ]
  },
  "lm": null,  // NO MODEL WEIGHTS - just prompt optimization
  "metadata": {
    "training_score": 0.87,
    "examples_used": 100,
    "optimization_rounds": 3
  }
}
```

**Key Observations**:
- **NO model weights**: Only instruction string + demonstration examples
- **Demonstrations are full examples**: Input + output + reasoning
- **Frozen after training**: Won't change at runtime

### 2.3 Training Duration & Cost

**Example (Queen→Princess-Dev)**:
- Training set: 100 examples
- Optimization rounds: 3
- LLM calls: 100 examples × 3 rounds = 300 calls
- Average tokens per call: 500 input + 300 output = 800 tokens
- Total tokens: 300 × 800 = 240,000 tokens
- Cost (Gemini Flash): 240K tokens × $0.10/1M = $0.024 (negligible)
- Time: 300 calls × 1s = 5 minutes

**Total Training Cost** (37 optimizers):
- 37 optimizers × $0.024 ≈ $0.90
- Manual dataset curation: 20 hours × $50/hour = $1,000
- **Total**: ~$1,000 (one-time, primarily human labor)

---

## 3. Runtime Phase (Online, Every Message)

### 3.1 What Happens at Runtime

**Step 1: Load Optimized Module**
```python
# In QueenAgent.__init__() or lazy-load
optimizer = QueenToPrincessDevOptimizer()
optimizer.load("models/dspy/queen_to_princess_dev.json")
# Loads frozen instruction + 10 demos into memory
```

**Step 2: Receive Task**
```python
# Queen receives complex task from user
task = Task(
    id="feature-123",
    type="implement-feature",
    description="Implement OAuth2 authentication with JWT tokens",
    payload={"objective": "Secure login/logout with session management"},
    priority=10
)
```

**Step 3: Build Optimized Prompt**
```python
# DSPy constructs prompt internally:
prompt = f"""
{instruction_string}

Example 1:
Task Description: Implement user profile page with avatar upload
Objective: CRUD operations + file upload with S3 integration
Reasoning: Let's think step by step in order to implement user profile page. First, we need requirements specification...
Subtasks: [{{"princess": "princess-dev", "task_type": "design", ...}}]

Example 2:
Task Description: Add real-time notifications using WebSockets
Objective: Push notifications to clients with <100ms latency
Reasoning: Let's think step by step in order to add real-time notifications. Requirements first...
Subtasks: [{{"princess": "princess-dev", "task_type": "design", ...}}]

... (8 more examples)

Current Task:
Task Description: {task.description}
Objective: {task.payload['objective']}
Reasoning: Let's think step by step in order to
"""
```

**Step 4: Call LLM**
```python
# DSPy calls agent's configured LLM
response = await llm.complete(prompt)
# ← 100-250ms LATENCY HERE (network + inference)
```

**Example LLM Response**:
```
Reasoning: Let's think step by step in order to implement OAuth2 authentication. First, we need strategic planning from princess-coordination to define the implementation strategy. Then, princess-dev handles architecture design with JWT tokens. After design, princess-dev implements the login/logout endpoints. Finally, princess-quality creates comprehensive tests and security validation.

Subtasks: [
  {
    "princess": "princess-coordination",
    "task_type": "plan",
    "description": "Plan OAuth2 implementation strategy with rollback plan",
    "dependencies": [],
    "estimated_minutes": 20
  },
  {
    "princess": "princess-dev",
    "task_type": "design",
    "description": "Design auth architecture with JWT token generation and validation",
    "dependencies": ["plan"],
    "estimated_minutes": 30
  },
  {
    "princess": "princess-dev",
    "task_type": "code",
    "description": "Implement login/logout endpoints with JWT integration",
    "dependencies": ["design"],
    "estimated_minutes": 45
  },
  {
    "princess": "princess-quality",
    "task_type": "test",
    "description": "Create auth integration tests with security validation",
    "dependencies": ["code"],
    "estimated_minutes": 35
  }
]
```

**Step 5: Parse Response**
```python
# DSPy parses LLM response into structured output
import json
result = optimizer.forward(
    task_description=task.description,
    objective=task.payload['objective']
)

reasoning = result.reasoning
subtasks = json.loads(result.subtasks)
```

**Step 6: Delegate to Princesses**
```python
# Queen delegates first subtask to princess-coordination
princess_task = Task(
    id=f"{task.id}-coord",
    type="plan",
    description=subtasks[0]["description"],
    payload={"strategy": {"phases": ["plan"]}},
    priority=task.priority
)

result = await self.delegate_task("princess-coordination", princess_task)
```

### 3.2 Latency Breakdown (Typical)

| Step | Duration | Notes |
|------|----------|-------|
| Load module (first call) | 50ms | JSON parsing, one-time per agent startup |
| Build prompt | 5ms | String concatenation |
| **LLM call** | **100-250ms** | **Network + inference (main latency)** |
| Parse response | 10ms | JSON parsing |
| **Total** | **165-315ms** | **Average: ~200ms** |

**Optimization Opportunities**:
- Cache frequently-used modules (already loaded)
- Use faster LLMs (Gemini Flash vs Pro)
- Batch multiple predictions (parallel processing)
- Skip DSPy for simple tasks (fallback to baseline)

---

## 4. Model-Agnostic Design

### 4.1 How DSPy Uses Agent's LLM

DSPy does NOT configure which LLM to use. It delegates to the **agent's configured LLM**.

**Agent Configuration** (per agent):
```python
# QueenAgent.py
class QueenAgent(AgentBase):
    def __init__(self):
        super().__init__(...)

        # Configure Queen's LLM (Gemini 2.0 Flash)
        dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

# PrincessDevAgent.py
class PrincessDevAgent(AgentBase):
    def __init__(self):
        super().__init__(...)

        # Configure Princess-Dev's LLM (GPT-4o)
        dspy.configure(lm=dspy.LM("openai/gpt-4o"))

# TesterAgent.py
class TesterAgent(AgentBase):
    def __init__(self):
        super().__init__(...)

        # Configure Tester's LLM (Claude Sonnet)
        dspy.configure(lm=dspy.LM("anthropic/claude-sonnet-4"))
```

**DSPy Module** (model-agnostic):
```python
class QueenToPrincessOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # NO model configuration - uses agent's LLM
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description: str, objective: str):
        # Calls whatever LLM the agent configured
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )
        # If called by Queen → uses Gemini
        # If called by Princess-Dev → uses GPT-4o
        return result
```

**Key Insight**: Same DSPy module can be used by different agents with different LLMs. The optimized prompt (instruction + demos) is model-agnostic.

### 4.2 Training vs Runtime LLM

**Training**:
- Can use ANY LLM (Gemini, GPT, Claude, Llama)
- Typically use free/cheap LLM (Gemini Flash)
- LLM choice affects training cost but NOT runtime behavior

**Runtime**:
- Uses agent's configured LLM
- Optimized prompt works across different LLMs (though quality may vary)

**Example**:
```python
# Training with Gemini Flash (cheap)
dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))
compiled = optimizer.compile(student=module, trainset=trainset)
compiled.save("queen_to_princess_dev.json")

# Runtime with GPT-4o (higher quality)
dspy.configure(lm=dspy.LM("openai/gpt-4o"))
module.load("queen_to_princess_dev.json")
result = module.forward(...)  # Uses GPT-4o with Gemini-trained prompt
```

---

## 5. What DSPy Does NOT Do

### 5.1 NOT Fine-Tuning

**DSPy is NOT**:
- Fine-tuning a neural network
- Creating model weights
- Training embeddings
- Updating model parameters

**DSPy IS**:
- Optimizing prompt structure (instruction + examples)
- Finding best few-shot demonstrations
- Learning which examples work best

### 5.2 NOT Static Rules

**DSPy is NOT**:
- Simple pattern matching
- If-then rules
- Template filling
- Regex-based transformations

**DSPy IS**:
- Calling LLM at runtime (every message)
- Using optimized prompts to guide LLM
- Still dependent on LLM quality

### 5.3 NOT Zero-Latency

**DSPy is NOT**:
- Instantaneous (still calls LLM)
- Faster than baseline prompting (same latency, better quality)
- Suitable for <100ms requirements

**DSPy IS**:
- 100-250ms per message (acceptable for 250ms budget)
- Worth the latency for quality improvement
- Can be cached/optimized for frequently-used paths

---

## 6. Summary: Training vs Runtime

| Aspect | Training (Offline) | Runtime (Online) |
|--------|-------------------|------------------|
| **When** | One-time, before deployment | Every message |
| **What** | Find best instruction + demos | Call LLM with optimized prompt |
| **LLM Calls** | 100-300 calls (training set) | 1 call per message |
| **Duration** | Minutes to hours (one-time) | 100-250ms (per message) |
| **Cost** | $0.02-0.10 per optimizer | $0.0001-0.0003 per message |
| **Output** | JSON file (instruction + demos) | Structured task/result |
| **Saved** | Prompt optimization (no weights) | Nothing (stateless) |

**Key Takeaway**: DSPy training is cheap and fast (minutes, pennies). Runtime latency is acceptable (100-250ms). No model weights involved, just prompt engineering optimization.

---

**Version**: 2.0 (UPDATED)
**Timestamp**: 2025-10-10T00:00:00-04:00
**Agent/Model**: Claude Sonnet 4
**Status**: ACCURATE - Replaces DSPY-HOW-IT-WORKS.md
**Changes**: Complete rewrite with accurate technical description of training/runtime phases, latency breakdown, model-agnostic design
