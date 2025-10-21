# DSPy Integration Strategy for SPEK Platform v8

**COMPREHENSIVE GUIDE**: Research-Backed DSPy Integration with Correct Process Order

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What is DSPy?](#what-is-dspy)
3. [Why DSPy for SPEK?](#why-dspy-for-spek)
4. [Beginner Path: Chat-Based DSPy (5-Minute Start)](#beginner-path-chat-based-dspy-5-minute-start)
5. [Builder/Engineer Path: Complete DSPy Workflow](#builderengineer-path-complete-dspy-workflow)
6. [Phase 0: Planning (Before Any Code)](#phase-0-planning-before-any-code)
7. [Phase 1: Setup (10-30 Minutes)](#phase-1-setup-10-30-minutes)
8. [Phase 2: Implementation (2-4 Hours)](#phase-2-implementation-2-4-hours)
9. [Phase 3: Optimization (1-3 Hours)](#phase-3-optimization-1-3-hours)
10. [Phase 4: Validation & Deployment (1-2 Hours)](#phase-4-validation--deployment-1-2-hours)
11. [Best Practices & Critical Warnings](#best-practices--critical-warnings)
12. [SPEK Platform Integration Details](#spek-platform-integration-details)
13. [Timeline & Milestones](#timeline--milestones)
14. [Troubleshooting & Common Failures](#troubleshooting--common-failures)

---

## Executive Summary

**Objective**: Optimize 4-8 P0/P1 agents using DSPy framework with Gemini LM backend to achieve ≥10% quality improvement at $0 cost.

### Key Corrections from Research

This guide has been **completely restructured** based on expert insights and official DSPy documentation to follow the correct process order:

**❌ OLD (WRONG) ORDER**:
```
Install → Signatures → Data → Metrics → Train
```

**✅ NEW (CORRECT) ORDER**:
```
Define Task → Gather Examples → Define Metrics → Choose Optimizer →
Install → Signatures → Implementation → Train → Deploy
```

### Critical Changes

1. ✅ **Phase 0 (Planning) added BEFORE code** - Define task, examples, metrics first
2. ✅ **Beginner chat-based path** - 5-minute quickstart without coding
3. ✅ **Training data requirements corrected** - 5-10 minimum (not 1-2)
4. ✅ **Optimizer selection made proactive** - Choose BEFORE training, not after failure
5. ✅ **Metrics simplified** - 3-7 criteria per agent (not 16 total)
6. ✅ **Critical warnings added** - Input consistency, output quality, common failures

### Current Status

**Week 6 Day 2 Complete**:
- ✅ Infrastructure ready (1,274 LOC)
- ⚠️ **INSUFFICIENT Training Data**: Reviewer (1 example), Coder (1 example) → **MUST expand to 5-10 each**
- ✅ Gemini CLI verified (v0.3.4)
- ⚠️ **Metrics over-engineered**: 16 metrics → **Should simplify to 3-7 per agent**

**Next Steps**: Follow CORRECTED process below (Phase 0 → Phase 4)

---

## What is DSPy?

### Overview

**DSPy** (Declarative Self-improving Python) is a framework for **programming with language models** rather than prompting them. It treats LM calls as **parameterized modules** that can be automatically optimized.

### Core Philosophy

DSPy transforms prompt engineering from **personal expertise** into **programmable discipline**:

- **Traditional Prompting**: Manually write prompts, test, iterate (hours per agent, brittle, hard to scale)
- **DSPy Approach**: Define task signature, provide examples, let AI optimize prompts automatically (minutes, systematic, scalable)

### Key Insight from Research

> "DSPy allows AI to optimize prompts for AI. You provide input-output pairs and success criteria, and DSPy automatically bridges the gap by generating optimized prompts. This removes human dependency and enables consistent scaling."

### Fundamental Components

#### 1. Signatures
**Input/output contracts** that specify **WHAT** your task should do (not HOW):
```python
class TaskDecomposition(dspy.Signature):
    """Break down complex task into subtasks."""
    task_description: str = dspy.InputField(desc="Task to decompose")
    objective: str = dspy.InputField(desc="Overall objective")
    subtasks: list = dspy.OutputField(desc="List of subtasks with agent assignments")
```

**Key Principle**: Signatures are **declarative** - you describe desired behavior, not implementation.

#### 2. Modules
**Composable building blocks** that combine signatures with reasoning strategies:
```python
class QueenModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Choose reasoning strategy based on task complexity
        self.decompose = dspy.ChainOfThought(TaskDecomposition)
        # Alternatives: dspy.ReAct, dspy.ProgramOfThought, etc.

    def forward(self, task_description, objective):
        return self.decompose(task_description=task_description, objective=objective)
```

**Reasoning Strategies**:
- `ChainOfThought`: Step-by-step reasoning (best for task decomposition)
- `ReAct`: Reasoning + action loops (best for tool use, external APIs)
- `ProgramOfThought`: Code-based reasoning (best for math, logic)

#### 3. Optimizers
**Automatic prompt optimization algorithms** that improve your modules:

| Optimizer | Use When | Data Requirements | Speed |
|-----------|----------|-------------------|-------|
| **BootstrapFewShot** | Straightforward tasks | 5-20 examples | Fast (minutes) |
| **MIPROv2** | Complex reasoning OR large datasets | 50+ examples | Slow (hours) |
| **BootstrapFewShotWithRandomSearch** | Thorough exploration needed | 20-50 examples | Medium |
| **BootstrapFinetune** | Want to finetune model weights | 200+ examples | Very slow |

**Critical**: Choose optimizer **BEFORE** training based on task complexity and data volume, not reactively after first attempt fails.

#### 4. Metrics
**Quantifiable evaluation functions** that guide optimization:
```python
def task_decomposition_metric(example, prediction, trace=None):
    """
    Evaluate task decomposition quality with 3-5 specific criteria.
    Returns: float between 0.0 and 1.0
    """
    gold_steps = example.subtasks
    pred_steps = prediction.subtasks

    # Criterion 1: Agent selection accuracy (30%)
    correct_agents = sum(1 for g, p in zip(gold_steps, pred_steps)
                        if g['agent'] == p['agent'])
    agent_accuracy = correct_agents / len(gold_steps) if gold_steps else 0

    # Criterion 2: Completeness (30%)
    completeness = min(len(pred_steps) / len(gold_steps), 1.0) if gold_steps else 0

    # Criterion 3: Clarity (20%)
    clarity = 1.0 if all(len(s.get('description', '')) > 10 for s in pred_steps) else 0.5

    # Criterion 4: Sequencing (20%)
    sequencing = 1.0  # Implement actual logic based on dependencies

    # Weighted average (total = 100%)
    return (agent_accuracy * 0.3 + completeness * 0.3 +
            clarity * 0.2 + sequencing * 0.2)
```

**Best Practice**: Use **3-7 criteria** (not >10). More criteria = harder to debug, potential overfitting.

---

## Why DSPy for SPEK?

### Advantages

✅ **Removes Human Dependency**
- Traditional: Requires expert prompt engineer for each agent
- DSPy: AI optimizes prompts automatically, scales consistently

✅ **Systematic Improvement**
- Traditional: Trial-and-error, unclear if prompt is "good enough"
- DSPy: Quantifiable metrics, measurable quality gains

✅ **Cost-Effective**
- Training: 100 iterations × 4 agents = 400 LM calls (free tier: 1,500/day)
- Inference: Optimized prompts reused indefinitely (no ongoing cost)

✅ **Composable Architecture**
- Each agent = DSPy module
- Modules can call other modules (Queen → Princess → Drones)
- Matches our AgentContract interface perfectly

### Expected Outcomes

**Baseline** (Week 6 Day 1):
```
Queen:    66.7% quality, 0.13ms latency
Tester:    0.0% quality, 0.27ms latency
Reviewer:  0.0% quality, 0.27ms latency
Coder:     0.0% quality, 0.20ms latency
```

**Target** (Week 6 Day 7):
```
Queen:    ≥75% quality (+12.4% improvement)
Tester:   ≥10% quality
Reviewer: ≥10% quality
Coder:    ≥10% quality
```

**Success Rate**: ≥3/4 agents meet ≥10% improvement target

---

## Beginner Path: Chat-Based DSPy (5-Minute Start)

**For Non-Technical Users**: You can use DSPy principles WITHOUT writing code.

### Chat-Based DSPy Simulation Prompt

**Copy-paste this into ChatGPT, Claude, or any LLM**:

```markdown
I need to create a self-optimizing prompt system for my task.

**My Task**: [Describe what you want to accomplish]
Example: "Break down complex software development tasks into subtasks and assign them to specialized agents"

**My Examples** (provide at least 3-5 input-output pairs):

Example 1:
- Input: [Describe a typical input]
- Output: [Describe the ideal output for this input]

Example 2:
- Input: [Another typical input]
- Output: [Ideal output]

Example 3:
- Input: [Third input]
- Output: [Ideal output]

[Add 2-7 more examples if available]

**Scoring Criteria** (choose 3-7 specific criteria):
1. Functionality: [0-10 scale, define what "10" looks like]
2. Format: [0-10 scale, define format requirements]
3. Completeness: [0-10 scale, define what's "complete"]
4. [Add 0-4 more criteria based on your task]

Please do the following:
1. Write 3 different prompts that could handle my task
2. Test each of the 3 prompts on ALL my examples
3. Score each prompt using my criteria (give detailed scores)
4. Take the best-performing prompt
5. Improve it by fixing the element that scored lowest
6. Give me the final optimized prompt with:
   - Full prompt text
   - Score breakdown for each criterion
   - Explanation of improvements made
```

### What This Achieves

✅ Simulates DSPy's optimization process without code
✅ Gets you an optimized prompt in 5 minutes
✅ Teaches DSPy principles (signatures, examples, metrics, optimization)
❌ Not as systematic as full DSPy (no automatic retraining)

### When to Graduate to Full DSPy

Use chat-based approach when:
- Quick prototyping (1-2 tasks)
- Non-technical team members
- Learning DSPy concepts

Use full DSPy implementation when:
- Production deployment needed
- Multiple agents to optimize (4-22 agents)
- Continuous improvement required
- A/B testing and statistical validation needed

---

## Builder/Engineer Path: Complete DSPy Workflow

**For Technical Users**: Full systematic DSPy implementation with code.

### Workflow Overview

```
PHASE 0: PLANNING (Before any code) - 1-2 hours
  ↓ Define task clearly
  ↓ Gather 5-10+ input-output examples
  ↓ Define 3-7 success metrics
  ↓ Choose optimizer proactively

PHASE 1: SETUP (10-30 minutes)
  ↓ Install dependencies
  ↓ Configure LM backend

PHASE 2: IMPLEMENTATION (2-4 hours)
  ↓ Define signatures
  ↓ Create modules with reasoning strategy
  ↓ Prepare training data (train/val split)
  ↓ Implement metric function

PHASE 3: OPTIMIZATION (1-3 hours)
  ↓ Run chosen optimizer
  ↓ Evaluate on validation set
  ↓ Analyze results

PHASE 4: VALIDATION & DEPLOYMENT (1-2 hours)
  ↓ A/B testing (baseline vs optimized)
  ↓ Statistical significance testing
  ↓ Deploy with feature flags
  ↓ Monitor and iterate
```

**Total Time**: 5-9 hours per agent (parallelizable across 4 agents)

---

## Phase 0: Planning (Before Any Code)

**⚠️ CRITICAL**: Do NOT skip this phase. Most DSPy failures happen because users jump to code before understanding the problem.

### Step 0.1: Define Task Clearly

**Questions to Answer**:
1. What problem are you solving?
2. What does success look like?
3. What are the inputs?
4. What are the outputs?

**Example: Queen Agent**
```
Problem: Decompose complex tasks into agent-executable subtasks
Success: Correct agent assignment, proper sequencing, complete coverage
Inputs: task_description (str), objective (str)
Outputs: subtasks (list of dicts with 'agent', 'description', 'dependencies')
```

**Example: Tester Agent**
```
Problem: Generate comprehensive test cases for code
Success: High coverage, relevant test cases, executable tests
Inputs: code_snippet (str), function_name (str)
Outputs: test_cases (list of test functions as strings)
```

### Step 0.2: Gather Input-Output Examples

**Requirements**:
- **Minimum**: 5-10 high-quality pairs
- **Recommended**: 20-50 pairs for production
- **Critical**: Inputs must be **consistent in structure**
- **Critical**: Outputs must be **high-quality** (95%+ quality, not just "good enough")

**⚠️ WARNING**: Inconsistent input formatting is the #1 cause of DSPy optimization failure.

**Example: Queen Agent Training Data**

```json
{
  "examples": [
    {
      "input": {
        "task_description": "Implement user authentication system with JWT tokens",
        "objective": "Secure user login and session management"
      },
      "output": {
        "subtasks": [
          {
            "agent": "architect",
            "description": "Design authentication architecture with JWT flow",
            "dependencies": []
          },
          {
            "agent": "coder",
            "description": "Implement JWT token generation and validation",
            "dependencies": ["architect"]
          },
          {
            "agent": "tester",
            "description": "Create tests for authentication endpoints",
            "dependencies": ["coder"]
          },
          {
            "agent": "reviewer",
            "description": "Security review of authentication implementation",
            "dependencies": ["coder", "tester"]
          }
        ]
      }
    },
    // ... 4-49 more examples with SAME input/output structure
  ]
}
```

**Quality Checklist**:
- ✅ All inputs have identical keys (`task_description`, `objective`)
- ✅ All outputs have identical structure (list of dicts with `agent`, `description`, `dependencies`)
- ✅ Output quality is excellent (correct agents, logical sequencing, complete coverage)
- ❌ No mixed formats (e.g., some with `dependencies`, some without)

### Step 0.3: Define Success Metrics (3-7 Criteria)

**Best Practice**: Use **3-7 specific criteria** (not <3 or >10)
- <3 criteria: Not enough signal for optimization
- >10 criteria: Overfitting risk, hard to debug

**Example: Queen Agent Metrics (4 criteria)**

```python
def queen_metric(example, prediction, trace=None):
    """
    Evaluate Queen agent task decomposition quality.
    Returns: float 0.0-1.0
    """
    gold_steps = example.subtasks
    pred_steps = prediction.subtasks

    # Criterion 1: Agent selection accuracy (30%)
    # Score: % of steps with correct agent type
    correct_agents = sum(1 for g, p in zip(gold_steps, pred_steps)
                        if g['agent'] == p['agent'])
    agent_accuracy = correct_agents / len(gold_steps) if gold_steps else 0

    # Criterion 2: Completeness (30%)
    # Score: Ratio of predicted steps to gold steps (max 1.0)
    completeness = min(len(pred_steps) / len(gold_steps), 1.0) if gold_steps else 0

    # Criterion 3: Sequencing (20%)
    # Score: % of dependencies correctly identified
    # (Simplified: check if dependencies listed in correct order)
    sequencing_score = 1.0  # Implement actual dependency validation

    # Criterion 4: Clarity (20%)
    # Score: All descriptions >10 chars (basic quality check)
    clarity = 1.0 if all(len(s.get('description', '')) > 10 for s in pred_steps) else 0.5

    # Weighted average (total = 100%)
    return (agent_accuracy * 0.3 +
            completeness * 0.3 +
            sequencing_score * 0.2 +
            clarity * 0.2)
```

**Weighting Best Practices**:
- Most important criterion: 30-40%
- Secondary criteria: 20-30% each
- Nice-to-have criteria: 10-20% each
- Total must sum to 100%

**Example: Tester Agent Metrics (3 criteria)**

```python
def tester_metric(example, prediction, trace=None):
    """Simplified with just 3 criteria."""
    gold_tests = example.test_cases
    pred_tests = prediction.test_cases

    # Criterion 1: Coverage (40%)
    # Measures if all important cases covered
    coverage = min(len(pred_tests) / len(gold_tests), 1.0) if gold_tests else 0

    # Criterion 2: Relevance (40%)
    # Measures if tests actually test the target function
    # (Simplified: check if function_name appears in test)
    relevant = sum(1 for t in pred_tests if example.function_name in t) / len(pred_tests)

    # Criterion 3: Executability (20%)
    # Checks if tests are syntactically valid
    # (Simplified: basic syntax check)
    executable = 1.0 if all('def test_' in t for t in pred_tests) else 0.5

    return coverage * 0.4 + relevant * 0.4 + executable * 0.2
```

### Step 0.4: Choose Optimizer Proactively

**❌ WRONG APPROACH**: "Let's try BootstrapFewShot and switch to MIPRO if it fails"

**✅ CORRECT APPROACH**: Choose optimizer BEFORE training based on:
1. Number of training examples available
2. Task complexity (straightforward vs complex reasoning)
3. Time budget (fast vs thorough)

**Decision Matrix**:

| Optimizer | Examples | Task Complexity | Time | Use Case |
|-----------|----------|-----------------|------|----------|
| **BootstrapFewShot** | 5-20 | Straightforward | Fast (15-30 min) | Queen, Tester, Reviewer, Coder |
| **BootstrapFewShotWithRandomSearch** | 20-50 | Moderate | Medium (1-2 hours) | If more examples available |
| **MIPROv2** | 50+ | Complex reasoning | Slow (2-4 hours) | Advanced orchestration, multi-step reasoning |
| **BootstrapFinetune** | 200+ | Any | Very slow (4-8 hours) | Model weight optimization |

**SPEK Platform Recommendation**:
- **P0 Agents (Queen, Tester, Reviewer, Coder)**: Use **BootstrapFewShot**
  - Reason: 5-10 examples per agent, straightforward tasks, fast turnaround needed
  - Parameters: `max_bootstrapped_demos=5`, `max_rounds=3`

- **If we expand data to 50+ examples**: Switch to **MIPROv2**
  - Reason: More thorough optimization with larger dataset
  - Parameters: `auto="light"` for faster, `auto="medium"` for better quality

### Step 0.5: Document Planning Decisions

**Create Planning Document** (save for future reference):

```markdown
## DSPy Optimization Plan: Queen Agent

**Task Definition**:
- Problem: Decompose complex tasks into agent-executable subtasks
- Success: Correct agents, proper sequencing, complete coverage
- Inputs: task_description (str), objective (str)
- Outputs: subtasks (list[dict])

**Training Data**:
- Count: 10 examples
- Quality: 95%+ (manually verified)
- Input consistency: ✅ All use same keys
- Output consistency: ✅ All use same structure

**Success Metrics** (4 criteria):
1. Agent selection accuracy (30%)
2. Completeness (30%)
3. Sequencing (20%)
4. Clarity (20%)

**Optimizer Choice**: BootstrapFewShot
- Reason: 10 examples, straightforward task, fast needed
- Parameters: max_demos=5, max_rounds=3

**Estimated Time**: 3 hours (implementation + optimization)

**Success Target**: ≥10% improvement (baseline 66.7% → target 75%+)
```

---

## Phase 1: Setup (10-30 Minutes)

### Step 1.1: Install Dependencies

```bash
# Install DSPy framework
pip install -U dspy

# Install LM backend (choose one)
pip install google-generativeai  # For Gemini (SPEK Platform choice)
# OR
pip install openai               # For OpenAI GPT-4
# OR
pip install anthropic            # For Claude
```

**Verify Installation**:
```bash
python -c "import dspy; print(f'DSPy version: {dspy.__version__}')"
python -c "import google.generativeai as genai; print('Gemini SDK installed')"
```

### Step 1.2: Configure LM Backend

**Option 1: Gemini (SPEK Platform Recommendation)**

```python
# src/dspy_optimization/dspy_config.py
import dspy
import os

def configure_dspy_gemini():
    """Configure DSPy with Gemini backend (free tier)."""

    # Import Gemini SDK
    import google.generativeai as genai

    # Configure API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Create DSPy LM instance
    lm = dspy.LM(
        model="google/gemini-1.5-flash",
        api_key=api_key,
        temperature=0.7,
        max_output_tokens=2048
    )

    # Configure DSPy globally
    dspy.configure(lm=lm)

    print(f"✅ DSPy configured with Gemini 1.5 Flash")
    return lm

# Usage
if __name__ == "__main__":
    lm = configure_dspy_gemini()
```

**Option 2: OpenAI (Alternative)**

```python
def configure_dspy_openai():
    """Configure DSPy with OpenAI backend."""
    lm = dspy.LM(
        model="openai/gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )
    dspy.configure(lm=lm)
    return lm
```

**Environment Setup**:
```bash
# Add to .env file
GOOGLE_API_KEY=your_api_key_here

# OR export in terminal
export GOOGLE_API_KEY=your_api_key_here
```

### Step 1.3: Verify Configuration

```python
# test_dspy_setup.py
import dspy
from src.dspy_optimization.dspy_config import configure_dspy_gemini

def test_dspy_setup():
    """Test DSPy configuration."""

    # Configure DSPy
    lm = configure_dspy_gemini()

    # Simple test
    class SimpleSignature(dspy.Signature):
        """Test signature."""
        question: str = dspy.InputField()
        answer: str = dspy.OutputField()

    predictor = dspy.Predict(SimpleSignature)
    result = predictor(question="What is 2+2?")

    print(f"✅ DSPy working! Answer: {result.answer}")
    assert "4" in result.answer or "four" in result.answer.lower()

if __name__ == "__main__":
    test_dspy_setup()
```

**Expected Output**:
```
✅ DSPy configured with Gemini 1.5 Flash
✅ DSPy working! Answer: 4
```

---

## Phase 2: Implementation (2-4 Hours)

### Step 2.1: Define Signatures

**File Structure**:
```
src/dspy_optimization/
├── signatures/
│   ├── __init__.py
│   ├── queen_signature.py
│   ├── tester_signature.py
│   ├── reviewer_signature.py
│   └── coder_signature.py
```

**Example: Queen Signature** (`signatures/queen_signature.py`):

```python
import dspy
from typing import List, Dict

class TaskDecomposition(dspy.Signature):
    """
    Break down a complex task into agent-executable subtasks.

    This signature defines the input-output contract for task decomposition.
    Inputs describe the task and objective.
    Output is a structured list of subtasks with agent assignments.
    """

    # Input fields
    task_description: str = dspy.InputField(
        desc="Detailed description of the complex task to decompose"
    )
    objective: str = dspy.InputField(
        desc="Overall objective or goal to achieve"
    )

    # Output fields
    subtasks: List[Dict[str, str]] = dspy.OutputField(
        desc=(
            "List of subtasks, each with keys: "
            "'agent' (agent type), "
            "'description' (task description), "
            "'dependencies' (list of prerequisite subtask indices)"
        )
    )
```

**Example: Tester Signature** (`signatures/tester_signature.py`):

```python
import dspy
from typing import List

class TestGeneration(dspy.Signature):
    """
    Generate comprehensive test cases for code.

    Given a code snippet and function name, generate relevant test cases
    that cover edge cases, happy paths, and error conditions.
    """

    # Inputs
    code_snippet: str = dspy.InputField(
        desc="Code to generate tests for (function or class)"
    )
    function_name: str = dspy.InputField(
        desc="Name of the function/method to test"
    )

    # Outputs
    test_cases: List[str] = dspy.OutputField(
        desc="List of test functions as executable Python code strings"
    )
```

**Example: Reviewer Signature** (`signatures/reviewer_signature.py`):

```python
import dspy
from typing import List, Dict

class CodeReview(dspy.Signature):
    """
    Perform code review to identify issues and improvements.

    Analyzes code for bugs, security issues, performance problems,
    and code quality concerns.
    """

    # Inputs
    code_snippet: str = dspy.InputField(
        desc="Code to review"
    )
    context: str = dspy.InputField(
        desc="Additional context about the code's purpose"
    )

    # Outputs
    issues: List[Dict[str, str]] = dspy.OutputField(
        desc=(
            "List of issues found, each with keys: "
            "'severity' (critical/high/medium/low), "
            "'type' (bug/security/performance/style), "
            "'description' (detailed issue description), "
            "'suggestion' (recommended fix)"
        )
    )
```

**Example: Coder Signature** (`signatures/coder_signature.py`):

```python
import dspy

class CodeGeneration(dspy.Signature):
    """
    Generate code from specifications.

    Translates requirements and pseudocode into working code.
    """

    # Inputs
    specification: str = dspy.InputField(
        desc="Detailed specification of what code should do"
    )
    language: str = dspy.InputField(
        desc="Programming language (python/typescript/etc)"
    )

    # Outputs
    code: str = dspy.OutputField(
        desc="Generated code that implements the specification"
    )
```

### Step 2.2: Create Modules with Reasoning Strategy

**File Structure**:
```
src/dspy_optimization/
├── modules/
│   ├── __init__.py
│   ├── queen_module.py
│   ├── tester_module.py
│   ├── reviewer_module.py
│   └── coder_module.py
```

**Example: Queen Module** (`modules/queen_module.py`):

```python
import dspy
from src.dspy_optimization.signatures.queen_signature import TaskDecomposition

class QueenModule(dspy.Module):
    """
    Queen agent orchestration module.

    Uses ChainOfThought reasoning for step-by-step task decomposition.
    """

    def __init__(self):
        super().__init__()

        # Use ChainOfThought for step-by-step reasoning
        # This encourages the model to think through the decomposition
        # before generating final subtasks
        self.decompose = dspy.ChainOfThought(TaskDecomposition)

    def forward(self, task_description: str, objective: str):
        """
        Decompose task into subtasks.

        Args:
            task_description: Complex task to break down
            objective: Overall goal

        Returns:
            Result with subtasks field
        """
        result = self.decompose(
            task_description=task_description,
            objective=objective
        )
        return result
```

**Why ChainOfThought?**
- Encourages step-by-step reasoning (better for complex decomposition)
- Shows intermediate thinking (helpful for debugging)
- Generally improves quality for multi-step tasks

**Alternative Reasoning Strategies**:

```python
# If task required external tool use
self.decompose = dspy.ReAct(TaskDecomposition)

# If task was primarily mathematical/logical
self.decompose = dspy.ProgramOfThought(TaskDecomposition)

# Simple prediction without reasoning (faster but lower quality)
self.decompose = dspy.Predict(TaskDecomposition)
```

**Example: Tester Module** (`modules/tester_module.py`):

```python
import dspy
from src.dspy_optimization.signatures.tester_signature import TestGeneration

class TesterModule(dspy.Module):
    """Tester agent module with ChainOfThought reasoning."""

    def __init__(self):
        super().__init__()
        self.generate_tests = dspy.ChainOfThought(TestGeneration)

    def forward(self, code_snippet: str, function_name: str):
        """Generate test cases for code."""
        result = self.generate_tests(
            code_snippet=code_snippet,
            function_name=function_name
        )
        return result
```

### Step 2.3: Prepare Training Data

**File**: `src/dspy_optimization/data_loader.py`

```python
import json
from pathlib import Path
from typing import List
import dspy

def load_queen_training_data() -> List[dspy.Example]:
    """
    Load Queen agent training data.

    Returns:
        List of DSPy Example objects with inputs and outputs marked
    """
    dataset_path = Path("datasets/week6/queen_training_dataset.json")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    examples = []
    for ex in data['examples']:
        input_task = ex['input_task']
        expected = ex['expected_output']

        # Create DSPy example
        example = dspy.Example(
            task_description=input_task['description'],
            objective=input_task['payload']['workflow']['objective'],
            subtasks=expected['steps']  # Gold label
        ).with_inputs('task_description', 'objective')  # Mark which fields are inputs

        examples.append(example)

    return examples

def split_train_val(examples: List[dspy.Example], val_ratio: float = 0.2):
    """
    Split examples into train/validation sets.

    Args:
        examples: All examples
        val_ratio: Fraction for validation (default 20%)

    Returns:
        Tuple of (trainset, valset)
    """
    split_idx = int(len(examples) * (1 - val_ratio))
    trainset = examples[:split_idx]
    valset = examples[split_idx:]

    print(f"✅ Split data: {len(trainset)} train, {len(valset)} val")
    return trainset, valset

# Similar functions for other agents
def load_tester_training_data() -> List[dspy.Example]:
    """Load Tester agent training data."""
    # Similar implementation
    pass

def load_reviewer_training_data() -> List[dspy.Example]:
    """Load Reviewer agent training data."""
    pass

def load_coder_training_data() -> List[dspy.Example]:
    """Load Coder agent training data."""
    pass
```

**⚠️ CRITICAL WARNING**:
```python
# ❌ WRONG - Missing .with_inputs()
example = dspy.Example(
    task_description="...",
    objective="...",
    subtasks=[...]
)

# ✅ CORRECT - Must mark which fields are inputs
example = dspy.Example(
    task_description="...",
    objective="...",
    subtasks=[...]
).with_inputs('task_description', 'objective')
```

### Step 2.4: Implement Metric Functions

**File**: `src/dspy_optimization/dspy_metrics.py`

```python
import dspy
from typing import List, Dict

def queen_metric(example, prediction, trace=None) -> float:
    """
    Evaluate Queen agent task decomposition quality.

    Metrics (4 criteria):
    1. Agent selection accuracy (30%)
    2. Completeness (30%)
    3. Sequencing (20%)
    4. Clarity (20%)

    Args:
        example: DSPy Example with gold label subtasks
        prediction: Prediction from module with predicted subtasks
        trace: Optional trace (not used)

    Returns:
        Score between 0.0 and 1.0
    """
    gold_steps = example.subtasks
    pred_steps = prediction.subtasks

    # Handle empty predictions
    if not pred_steps or not gold_steps:
        return 0.0

    # Criterion 1: Agent selection accuracy (30%)
    correct_agents = sum(
        1 for g, p in zip(gold_steps, pred_steps)
        if g.get('agent') == p.get('agent')
    )
    agent_accuracy = correct_agents / len(gold_steps)

    # Criterion 2: Completeness (30%)
    # Penalize if too few or too many steps
    completeness = min(len(pred_steps) / len(gold_steps), 1.0)

    # Criterion 3: Sequencing (20%)
    # Check if dependencies make sense (simplified)
    # Full implementation would validate dependency graph
    sequencing_score = 1.0
    for pred_step in pred_steps:
        deps = pred_step.get('dependencies', [])
        # Ensure dependencies don't reference future steps
        if any(dep >= len(pred_steps) for dep in deps):
            sequencing_score = 0.5
            break

    # Criterion 4: Clarity (20%)
    # All descriptions should be meaningful (>10 chars)
    clarity = 1.0 if all(
        len(s.get('description', '')) > 10 for s in pred_steps
    ) else 0.5

    # Weighted average (total = 100%)
    score = (
        agent_accuracy * 0.3 +
        completeness * 0.3 +
        sequencing_score * 0.2 +
        clarity * 0.2
    )

    return score

def tester_metric(example, prediction, trace=None) -> float:
    """
    Evaluate Tester agent test generation quality.

    Metrics (3 criteria):
    1. Coverage (40%)
    2. Relevance (40%)
    3. Executability (20%)
    """
    gold_tests = example.test_cases
    pred_tests = prediction.test_cases

    if not pred_tests or not gold_tests:
        return 0.0

    # Criterion 1: Coverage (40%)
    coverage = min(len(pred_tests) / len(gold_tests), 1.0)

    # Criterion 2: Relevance (40%)
    # Tests should reference the function being tested
    function_name = example.function_name
    relevant_count = sum(1 for t in pred_tests if function_name in t)
    relevance = relevant_count / len(pred_tests)

    # Criterion 3: Executability (20%)
    # Basic check: tests start with 'def test_'
    executable_count = sum(1 for t in pred_tests if 'def test_' in t)
    executability = executable_count / len(pred_tests)

    score = coverage * 0.4 + relevance * 0.4 + executability * 0.2
    return score

def reviewer_metric(example, prediction, trace=None) -> float:
    """
    Evaluate Reviewer agent code review quality.

    Metrics (4 criteria):
    1. Issue detection accuracy (40%)
    2. Severity classification (30%)
    3. False positive rate (20%)
    4. Suggestion quality (10%)
    """
    gold_issues = example.issues
    pred_issues = prediction.issues

    if not gold_issues:
        # No issues expected - penalize false positives
        return 0.0 if pred_issues else 1.0

    if not pred_issues:
        # Issues exist but none found
        return 0.0

    # Criterion 1: Issue detection (40%)
    # Check if critical issues were found
    gold_critical = [i for i in gold_issues if i['severity'] == 'critical']
    pred_critical = [i for i in pred_issues if i['severity'] == 'critical']

    detection = min(len(pred_critical) / len(gold_critical), 1.0) if gold_critical else 1.0

    # Criterion 2: Severity classification (30%)
    # Simplified: just check if any severity marked as critical
    severity_score = 1.0 if pred_critical else 0.5

    # Criterion 3: False positive rate (20%)
    # Simplified: penalize if way more issues than expected
    false_positive_penalty = 0.0
    if len(pred_issues) > len(gold_issues) * 1.5:
        false_positive_penalty = 0.5
    fp_score = 1.0 - false_positive_penalty

    # Criterion 4: Suggestion quality (10%)
    # Check if suggestions provided
    has_suggestions = all(i.get('suggestion') for i in pred_issues)
    suggestion_score = 1.0 if has_suggestions else 0.5

    score = (detection * 0.4 + severity_score * 0.3 +
             fp_score * 0.2 + suggestion_score * 0.1)
    return score

def coder_metric(example, prediction, trace=None) -> float:
    """
    Evaluate Coder agent code generation quality.

    Metrics (3 criteria):
    1. Syntax validity (40%)
    2. Specification compliance (40%)
    3. Code quality (20%)
    """
    gold_code = example.code
    pred_code = prediction.code

    if not pred_code:
        return 0.0

    # Criterion 1: Syntax validity (40%)
    # Try to parse as Python
    import ast
    syntax_valid = False
    try:
        ast.parse(pred_code)
        syntax_valid = True
    except SyntaxError:
        syntax_valid = False

    syntax_score = 1.0 if syntax_valid else 0.0

    # Criterion 2: Specification compliance (40%)
    # Check if key terms from spec appear in code
    spec = example.specification
    spec_keywords = spec.lower().split()[:10]  # First 10 words
    compliance_count = sum(1 for kw in spec_keywords if kw in pred_code.lower())
    compliance = compliance_count / len(spec_keywords) if spec_keywords else 0.5

    # Criterion 3: Code quality (20%)
    # Simplified: check for docstrings, type hints
    has_docstring = '"""' in pred_code or "'''" in pred_code
    has_type_hints = '->' in pred_code
    quality = (0.5 if has_docstring else 0.0) + (0.5 if has_type_hints else 0.0)

    score = syntax_score * 0.4 + compliance * 0.4 + quality * 0.2
    return score
```

**Metric Best Practices**:
- ✅ Return float between 0.0 and 1.0
- ✅ Use 3-7 criteria (not >10)
- ✅ Weight criteria appropriately (total = 100%)
- ✅ Handle edge cases (empty predictions, no gold labels)
- ❌ Don't make metrics too complex (hard to debug)

---

## Phase 3: Optimization (1-3 Hours)

### Step 3.1: Create Training Script

**File**: `src/dspy_optimization/train.py`

```python
import dspy
from pathlib import Path
from src.dspy_optimization.dspy_config import configure_dspy_gemini
from src.dspy_optimization.data_loader import (
    load_queen_training_data,
    split_train_val
)
from src.dspy_optimization.dspy_metrics import queen_metric
from src.dspy_optimization.modules.queen_module import QueenModule
from dspy.evaluate import Evaluate

def train_queen_agent():
    """
    Train Queen agent with DSPy BootstrapFewShot optimizer.

    Process:
    1. Configure DSPy with Gemini backend
    2. Load and split training data
    3. Create baseline Queen module
    4. Run BootstrapFewShot optimization
    5. Evaluate baseline vs optimized
    6. Save optimized module

    Returns:
        Dict with training results
    """
    print("=" * 60)
    print("DSPy TRAINING: Queen Agent")
    print("=" * 60)

    # Step 1: Configure DSPy
    print("\n[1/6] Configuring DSPy with Gemini backend...")
    lm = configure_dspy_gemini()

    # Step 2: Load training data
    print("\n[2/6] Loading training data...")
    examples = load_queen_training_data()
    trainset, valset = split_train_val(examples, val_ratio=0.2)

    print(f"  - Total examples: {len(examples)}")
    print(f"  - Training set: {len(trainset)}")
    print(f"  - Validation set: {len(valset)}")

    # Step 3: Create baseline module
    print("\n[3/6] Creating baseline Queen module...")
    baseline_queen = QueenModule()

    # Evaluate baseline
    evaluator = Evaluate(
        devset=valset,
        metric=queen_metric,
        num_threads=1  # Sequential for debugging
    )

    baseline_score = evaluator(baseline_queen)
    print(f"  - Baseline score: {baseline_score:.3f} ({baseline_score*100:.1f}%)")

    # Step 4: Run optimization
    print("\n[4/6] Running BootstrapFewShot optimization...")
    print("  - This may take 15-30 minutes...")

    optimizer = dspy.BootstrapFewShot(
        metric=queen_metric,
        max_bootstrapped_demos=5,  # Generate 5 few-shot examples
        max_labeled_demos=len(trainset),  # Use all training examples
        max_rounds=3  # 3 optimization rounds
    )

    optimized_queen = optimizer.compile(
        baseline_queen,
        trainset=trainset
    )

    print("  ✅ Optimization complete!")

    # Step 5: Evaluate optimized
    print("\n[5/6] Evaluating optimized module...")
    optimized_score = evaluator(optimized_queen)
    print(f"  - Optimized score: {optimized_score:.3f} ({optimized_score*100:.1f}%)")

    improvement = ((optimized_score - baseline_score) / baseline_score) * 100
    print(f"  - Improvement: {improvement:+.1f}%")

    # Step 6: Save optimized module
    print("\n[6/6] Saving optimized module...")
    model_dir = Path("models/dspy")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "queen_optimized.json"
    optimized_queen.save(str(model_path))
    print(f"  ✅ Saved to: {model_path}")

    # Summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Baseline:  {baseline_score*100:.1f}%")
    print(f"Optimized: {optimized_score*100:.1f}%")
    print(f"Improvement: {improvement:+.1f}%")

    meets_target = improvement >= 10.0
    print(f"Meets ≥10% target: {'✅ YES' if meets_target else '❌ NO'}")

    return {
        'agent': 'queen',
        'baseline_score': baseline_score,
        'optimized_score': optimized_score,
        'improvement_pct': improvement,
        'meets_target': meets_target,
        'model_path': str(model_path)
    }

# Similar functions for other agents
def train_tester_agent():
    """Train Tester agent."""
    # Similar implementation
    pass

def train_reviewer_agent():
    """Train Reviewer agent."""
    pass

def train_coder_agent():
    """Train Coder agent."""
    pass

def train_all_agents():
    """
    Train all 4 P0 agents sequentially.

    Returns:
        List of training results for each agent
    """
    results = []

    results.append(train_queen_agent())
    results.append(train_tester_agent())
    results.append(train_reviewer_agent())
    results.append(train_coder_agent())

    # Summary
    print("\n" + "=" * 60)
    print("ALL AGENTS TRAINING COMPLETE")
    print("=" * 60)

    for result in results:
        agent = result['agent']
        improvement = result['improvement_pct']
        status = '✅' if result['meets_target'] else '❌'
        print(f"{agent:12} {improvement:+6.1f}% {status}")

    success_count = sum(1 for r in results if r['meets_target'])
    print(f"\nSuccess rate: {success_count}/4 agents meet ≥10% target")

    return results

if __name__ == "__main__":
    # Train all agents
    results = train_all_agents()
```

### Step 3.2: Run Training

```bash
# Train all 4 P0 agents
python -m src.dspy_optimization.train

# OR train individually
python -m src.dspy_optimization.train_queen
python -m src.dspy_optimization.train_tester
python -m src.dspy_optimization.train_reviewer
python -m src.dspy_optimization.train_coder
```

**Expected Output**:
```
============================================================
DSPy TRAINING: Queen Agent
============================================================

[1/6] Configuring DSPy with Gemini backend...
✅ DSPy configured with Gemini 1.5 Flash

[2/6] Loading training data...
✅ Split data: 8 train, 2 val
  - Total examples: 10
  - Training set: 8
  - Validation set: 2

[3/6] Creating baseline Queen module...
  - Baseline score: 0.667 (66.7%)

[4/6] Running BootstrapFewShot optimization...
  - This may take 15-30 minutes...
  ✅ Optimization complete!

[5/6] Evaluating optimized module...
  - Optimized score: 0.783 (78.3%)
  - Improvement: +17.4%

[6/6] Saving optimized module...
  ✅ Saved to: models/dspy/queen_optimized.json

============================================================
TRAINING COMPLETE
============================================================
Baseline:  66.7%
Optimized: 78.3%
Improvement: +17.4%
Meets ≥10% target: ✅ YES
```

### Step 3.3: Inspect Optimized Prompts

```python
# inspect_prompts.py
import dspy

def inspect_optimized_prompt(model_path: str):
    """
    Inspect what DSPy generated as the optimized prompt.

    Args:
        model_path: Path to saved optimized module
    """
    # Load optimized module
    optimized = dspy.Module.load(model_path)

    # Access the ChainOfThought predictor
    predictor = optimized.decompose

    # Print the optimized prompt
    print("=" * 60)
    print("OPTIMIZED PROMPT")
    print("=" * 60)
    print(predictor.extended_signature)
    print("\n" + "=" * 60)
    print("FEW-SHOT EXAMPLES")
    print("=" * 60)

    # Print few-shot demonstrations
    if hasattr(predictor, 'demos'):
        for i, demo in enumerate(predictor.demos, 1):
            print(f"\nExample {i}:")
            print(f"  Input: {demo['task_description'][:100]}...")
            print(f"  Output: {demo['subtasks'][:2]}...")  # First 2 subtasks
    else:
        print("No few-shot examples stored")

if __name__ == "__main__":
    inspect_optimized_prompt("models/dspy/queen_optimized.json")
```

**Why This Matters**:
- You can see WHAT DSPy optimized (the actual prompt text)
- Useful for debugging if results are unexpected
- Can manually review generated few-shot examples

---

## Phase 4: Validation & Deployment (1-2 Hours)

### Step 4.1: A/B Testing

**File**: `src/dspy_optimization/ab_testing.py`

```python
import asyncio
from typing import List, Dict
import dspy
from src.agents.core.QueenAgent import QueenAgent
from src.dspy_optimization.modules.queen_module import QueenModule
from src.dspy_optimization.dspy_metrics import queen_metric

async def ab_test_queen(
    test_tasks: List[Dict],
    optimized_model_path: str
) -> Dict:
    """
    A/B test baseline Queen vs optimized DSPy module.

    Args:
        test_tasks: List of test tasks (separate from train/val)
        optimized_model_path: Path to optimized DSPy module

    Returns:
        Comparison results with statistics
    """
    print("=" * 60)
    print("A/B TESTING: Queen Agent")
    print("=" * 60)

    # Load baseline and optimized
    baseline_agent = QueenAgent()  # Existing agent
    optimized_module = dspy.Module.load(optimized_model_path)

    baseline_scores = []
    optimized_scores = []

    print(f"\nTesting on {len(test_tasks)} tasks...")

    for i, task_data in enumerate(test_tasks, 1):
        print(f"  Task {i}/{len(test_tasks)}...")

        # Baseline
        # (Simplified - actual implementation would create Task objects)
        baseline_result = await baseline_agent.execute_orchestrate(task_data)
        baseline_score = calculate_score(baseline_result, task_data['expected'])
        baseline_scores.append(baseline_score)

        # Optimized
        optimized_result = optimized_module(
            task_description=task_data['description'],
            objective=task_data['objective']
        )
        optimized_score = calculate_score(optimized_result, task_data['expected'])
        optimized_scores.append(optimized_score)

    # Calculate statistics
    baseline_avg = sum(baseline_scores) / len(baseline_scores)
    optimized_avg = sum(optimized_scores) / len(optimized_scores)
    improvement = ((optimized_avg - baseline_avg) / baseline_avg) * 100

    # Statistical significance (paired t-test)
    from scipy import stats
    t_stat, p_value = stats.ttest_rel(baseline_scores, optimized_scores)

    results = {
        'baseline_avg': baseline_avg,
        'optimized_avg': optimized_avg,
        'improvement_pct': improvement,
        'p_value': p_value,
        'statistically_significant': p_value < 0.05,
        'meets_target': improvement >= 10.0
    }

    # Print summary
    print("\n" + "=" * 60)
    print("A/B TEST RESULTS")
    print("=" * 60)
    print(f"Baseline:  {baseline_avg*100:.1f}%")
    print(f"Optimized: {optimized_avg*100:.1f}%")
    print(f"Improvement: {improvement:+.1f}%")
    print(f"P-value: {p_value:.4f} ({'✅ significant' if p_value < 0.05 else '❌ not significant'})")
    print(f"Meets ≥10% target: {'✅ YES' if results['meets_target'] else '❌ NO'}")

    return results

def calculate_score(result, expected):
    """Helper to calculate score (placeholder)."""
    # Implement actual scoring logic
    return 0.75  # Placeholder
```

### Step 4.2: Deploy with Feature Flags

**File**: `src/agents/core/QueenAgent.py` (modified)

```python
import dspy
from pathlib import Path
from src.agents.base.AgentBase import AgentBase
from src.infrastructure.task.Task import Task

class QueenAgent(AgentBase):
    """
    Queen agent with optional DSPy optimization.

    Use environment variable USE_DSPY_OPTIMIZATION=true to enable.
    """

    def __init__(self):
        super().__init__(
            agent_id="queen",
            capabilities=["orchestrate", "delegate", "coordinate"]
        )

        # Check if DSPy optimization enabled
        import os
        self.use_dspy = os.getenv("USE_DSPY_OPTIMIZATION", "false").lower() == "true"

        if self.use_dspy:
            model_path = Path("models/dspy/queen_optimized.json")
            if model_path.exists():
                self.dspy_module = dspy.Module.load(str(model_path))
                print(f"✅ Queen agent using DSPy optimization")
            else:
                print(f"⚠️ DSPy model not found, falling back to baseline")
                self.use_dspy = False

    async def _execute_orchestrate(self, task: Task):
        """Execute task orchestration."""

        if self.use_dspy:
            # Use DSPy optimized version
            return await self._dspy_orchestrate(task)
        else:
            # Use baseline implementation
            return await self._baseline_orchestrate(task)

    async def _dspy_orchestrate(self, task: Task):
        """DSPy-optimized orchestration."""
        result = self.dspy_module(
            task_description=task.description,
            objective=task.payload['workflow']['objective']
        )

        # Convert DSPy result to agent result format
        return self._convert_dspy_to_result(result)

    async def _baseline_orchestrate(self, task: Task):
        """Baseline orchestration (original implementation)."""
        # Original implementation
        pass

    def _convert_dspy_to_result(self, dspy_result):
        """Convert DSPy output to agent result format."""
        # Conversion logic
        pass
```

**Usage**:
```bash
# Enable DSPy optimization
export USE_DSPY_OPTIMIZATION=true
python -m src.main

# Disable DSPy optimization (fallback to baseline)
export USE_DSPY_OPTIMIZATION=false
python -m src.main
```

### Step 4.3: Gradual Rollout

**Deployment Strategy**:
1. **10% traffic**: Enable for 10% of requests, monitor for 24 hours
2. **50% traffic**: If no issues, enable for 50%, monitor for 48 hours
3. **100% traffic**: Full rollout if quality improvement sustained

**Implementation** (simplified):
```python
import random

class QueenAgent(AgentBase):
    def __init__(self):
        super().__init__(...)

        # Gradual rollout percentage
        import os
        rollout_pct = int(os.getenv("DSPY_ROLLOUT_PCT", "0"))

        # Randomly decide if this instance uses DSPy
        self.use_dspy = random.random() * 100 < rollout_pct
```

### Step 4.4: Monitoring & Rollback

**Monitoring Setup**:
```python
# src/dspy_optimization/monitoring.py
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DSPyMetrics:
    """Track DSPy performance in production."""
    timestamp: datetime
    agent_id: str
    version: str  # 'baseline' or 'dspy'
    quality_score: float
    latency_ms: float
    success: bool

def log_dspy_metric(metric: DSPyMetrics):
    """Log DSPy metric for monitoring."""
    with open("logs/dspy_metrics.jsonl", "a") as f:
        f.write(json.dumps(metric.__dict__) + "\n")

def check_quality_regression():
    """Alert if DSPy quality drops below baseline."""
    # Load recent metrics
    # Compare DSPy vs baseline
    # Alert if DSPy < baseline - 5%
    pass
```

**Rollback Script**:
```bash
# rollback_dspy.sh
#!/bin/bash

echo "Rolling back DSPy optimization..."

# Disable DSPy
export USE_DSPY_OPTIMIZATION=false

# Restart service
systemctl restart spek-platform

echo "✅ Rollback complete - using baseline agents"
```

---

## Best Practices & Critical Warnings

### ✅ Data Preparation Best Practices

1. **Input Consistency is CRITICAL**
   ```python
   # ❌ WRONG - Inconsistent input structure
   examples = [
       {"task": "...", "goal": "..."},      # Different keys
       {"description": "...", "objective": "..."}  # Different keys
   ]

   # ✅ CORRECT - Consistent input structure
   examples = [
       {"task_description": "...", "objective": "..."},
       {"task_description": "...", "objective": "..."}
   ]
   ```

2. **Output Quality Matters**
   - **95%+ quality** for training outputs (not just "good enough")
   - Garbage in = garbage out
   - One bad example can corrupt optimization

3. **Sufficient Volume**
   - **Minimum**: 5-10 examples (will work but limited improvement)
   - **Recommended**: 20-50 examples (good improvement)
   - **Optimal**: 50+ examples (best results, enable MIPRO)

### ⚠️ Common Failures & How to Avoid

#### Failure 1: "Optimization didn't improve quality"

**Causes**:
- ❌ Insufficient training data (<5 examples)
- ❌ Poor quality training outputs
- ❌ Wrong optimizer choice (MIPRO on 5 examples)
- ❌ Too many metrics (>10 criteria, overfitting)

**Solutions**:
- ✅ Gather 5-10+ high-quality examples
- ✅ Manually verify training output quality
- ✅ Use BootstrapFewShot for <20 examples
- ✅ Simplify to 3-7 metrics

#### Failure 2: "DSPy crashes during training"

**Causes**:
- ❌ Missing `.with_inputs()` on examples
- ❌ LM backend not configured
- ❌ API key issues

**Solutions**:
```python
# ✅ Always mark inputs
example = dspy.Example(...).with_inputs('input1', 'input2')

# ✅ Verify configuration
lm = dspy.LM("google/gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
dspy.configure(lm=lm)
```

#### Failure 3: "Optimized prompts are worse than baseline"

**Causes**:
- ❌ Metric doesn't align with actual quality
- ❌ Training data not representative
- ❌ Overfitting to training examples

**Solutions**:
- ✅ Validate metric on held-out test set
- ✅ Ensure training data covers edge cases
- ✅ Use separate validation set (20% of data)

### 🚨 Critical Warnings

**1. Input Structure MUST Be Consistent**
```python
# This will FAIL silently (DSPy can't learn patterns)
examples = [
    {"task": "...", "goal": "..."},
    {"description": "...", "objective": "..."}
]
```

**2. Don't Over-Engineer Metrics**
```python
# ❌ TOO MANY (16 metrics) - overfitting, hard to debug
# ✅ JUST RIGHT (3-7 metrics) - clear signal, debuggable
```

**3. Choose Optimizer BEFORE Training**
```python
# ❌ REACTIVE: Try BootstrapFewShot, switch to MIPRO if fails
# ✅ PROACTIVE: Choose based on data volume + task complexity
```

**4. Validate with A/B Testing**
```python
# ❌ Deploy without validation
# ✅ A/B test baseline vs optimized, require p < 0.05
```

---

## SPEK Platform Integration Details

### Current Status (Week 6 Day 2)

**Infrastructure Ready** ✅:
- Gemini CLI adapter (206 LOC)
- Baseline metrics collector (164 LOC)
- Quality metrics defined (250 LOC)
- Training datasets generator (331 LOC)

**CRITICAL ISSUES** ⚠️:
1. **Insufficient Training Data**
   - Current: Reviewer (1 example), Coder (1 example)
   - Minimum needed: 5-10 examples each
   - **Action Required**: Expand datasets BEFORE training

2. **Over-Complicated Metrics**
   - Current: 16 metrics total (4 per agent)
   - Recommended: 3-7 criteria per agent
   - **Action Required**: Simplify metric functions

### Corrected Implementation Plan

#### Week 6 Day 3: Data Expansion + Signatures (4 hours)

**Tasks**:
- [ ] Expand Reviewer dataset: 1 → 10 examples (2 hours)
- [ ] Expand Coder dataset: 1 → 10 examples (2 hours)
- [ ] Create 4 signature modules (1 hour)
- [ ] Create 4 module wrappers (1 hour)
- [ ] Simplify metrics to 3-7 criteria each (1 hour)

**Deliverables**:
- `datasets/week6/reviewer_training_dataset.json` (10 examples)
- `datasets/week6/coder_training_dataset.json` (10 examples)
- `src/dspy_optimization/signatures/` (4 files)
- `src/dspy_optimization/modules/` (4 files)
- `src/dspy_optimization/dspy_metrics.py` (simplified)

#### Week 6 Day 4-5: Training (6 hours)

**Tasks**:
- [ ] Install DSPy + dependencies (30 min)
- [ ] Configure Gemini backend (30 min)
- [ ] Implement data loader (1 hour)
- [ ] Train Queen agent (1 hour)
- [ ] Train Tester agent (1 hour)
- [ ] Train Reviewer agent (1 hour)
- [ ] Train Coder agent (1 hour)
- [ ] Generate training reports (30 min)

**Deliverables**:
- `models/dspy/queen_optimized.json`
- `models/dspy/tester_optimized.json`
- `models/dspy/reviewer_optimized.json`
- `models/dspy/coder_optimized.json`
- Training reports with baseline vs optimized scores

**Success Criteria**:
- ✅ All 4 agents trained without errors
- ✅ ≥2 agents show ≥10% improvement
- ✅ Optimized models saved successfully

#### Week 6 Day 6: A/B Testing (4 hours)

**Tasks**:
- [ ] Create A/B testing framework (2 hours)
- [ ] Generate 20 test tasks per agent (1 hour)
- [ ] Run A/B tests (1 hour)
- [ ] Statistical significance testing (30 min)
- [ ] Generate comparison report (30 min)

**Deliverables**:
- `src/dspy_optimization/ab_testing.py`
- A/B test results report
- Statistical analysis (t-test, p-values)

**Success Criteria**:
- ✅ ≥3 agents meet ≥10% improvement
- ✅ Statistical significance (p < 0.05)
- ✅ No latency regression (≤20% slowdown acceptable)

#### Week 6 Day 7: Deployment (4 hours)

**Tasks**:
- [ ] Integrate DSPy into agent classes (2 hours)
- [ ] Add feature flags (30 min)
- [ ] Implement monitoring (1 hour)
- [ ] Deploy to production (gradual rollout) (1 hour)
- [ ] Generate Week 6 final report (30 min)

**Deliverables**:
- Modified agent classes with DSPy integration
- Monitoring dashboard
- Week 6 final report
- P1 optimization decision (GO/NO-GO)

**Success Criteria**:
- ✅ Production deployment successful
- ✅ No critical issues in first 24 hours
- ✅ Quality improvement sustained

### P1 Optimization Decision (End of Week 6)

**GO Criteria** (proceed with P1 agents):
- ✅ ≥3/4 P0 agents achieve ≥15% improvement
- ✅ No production issues
- ✅ Team capacity available

**NO-GO Criteria** (defer P1 to Week 7):
- ❌ <3/4 P0 agents meet ≥10% improvement
- ❌ Production stability issues
- ❌ Team capacity constraints

**P1 Agents** (if GO):
- Researcher, Architect, Spec-Writer, Debugger

---

## Timeline & Milestones

### Week 6 Revised Schedule

| Day | Phase | Tasks | Hours | Success Metric |
|-----|-------|-------|-------|----------------|
| 3 | Planning + Data | Expand datasets (1→10), create signatures | 7 | 4 datasets with 10+ examples each |
| 4 | Setup + Training | Install DSPy, train Queen + Tester | 6 | 2 optimized models, ≥10% improvement |
| 5 | Training | Train Reviewer + Coder, generate reports | 6 | 4 optimized models total |
| 6 | Validation | A/B testing, statistical analysis | 4 | ≥3 agents significant improvement |
| 7 | Deployment | Integration, monitoring, production rollout | 4 | Production deployment successful |

**Total Time**: 27 hours (Week 6)

### Cost Estimate

**Gemini API Calls** (free tier: 1,500/day):
- Training: 100 calls × 4 agents = 400 calls
- Evaluation: 20 calls × 4 agents = 80 calls
- A/B testing: 20 calls × 4 agents = 80 calls
- **Total**: 560 calls (37% of daily limit)

**Cost**: $0 (within free tier)

---

## Troubleshooting & Common Failures

### Issue: "ModuleNotFoundError: No module named 'dspy'"

**Solution**:
```bash
pip install -U dspy
python -c "import dspy; print(dspy.__version__)"
```

### Issue: "API key not configured"

**Solution**:
```bash
export GOOGLE_API_KEY=your_key_here
# OR add to .env file
echo "GOOGLE_API_KEY=your_key" >> .env
```

### Issue: "Training takes too long (>1 hour per agent)"

**Causes**:
- Too many training examples (>50)
- Too many optimization rounds (>5)
- Slow LM backend

**Solutions**:
```python
# Reduce optimization rounds
optimizer = dspy.BootstrapFewShot(
    metric=...,
    max_rounds=2  # Instead of 3
)

# Use faster model
lm = dspy.LM("google/gemini-1.5-flash")  # Faster than Pro
```

### Issue: "Optimized score worse than baseline"

**Debug Steps**:
1. Inspect optimized prompt: `inspect_prompts.py`
2. Validate metric function: Test on known examples
3. Check training data quality: Review outputs manually
4. Try different optimizer: Switch BootstrapFewShot ↔ MIPRO

### Issue: "Can't load optimized module"

**Solution**:
```python
# Check file exists
from pathlib import Path
model_path = Path("models/dspy/queen_optimized.json")
assert model_path.exists(), f"Model not found: {model_path}"

# Load with error handling
try:
    optimized = dspy.Module.load(str(model_path))
except Exception as e:
    print(f"Error loading model: {e}")
    # Fallback to baseline
```

---

## Conclusion

### Summary

**DSPy Integration Strategy** (Research-Backed, Correct Process):

1. ✅ **PHASE 0: PLANNING (BEFORE CODE)**
   - Define task clearly
   - Gather 5-10+ input-output examples
   - Define 3-7 success metrics
   - Choose optimizer proactively

2. ✅ **PHASE 1: SETUP**
   - Install dependencies
   - Configure LM backend

3. ✅ **PHASE 2: IMPLEMENTATION**
   - Define signatures
   - Create modules with reasoning strategy
   - Prepare training data (train/val split)
   - Implement metric function

4. ✅ **PHASE 3: OPTIMIZATION**
   - Run chosen optimizer
   - Evaluate on validation set

5. ✅ **PHASE 4: VALIDATION & DEPLOYMENT**
   - A/B testing
   - Statistical significance testing
   - Deploy with feature flags
   - Monitor and iterate

### Key Success Factors

1. **Follow CORRECT Process Order**
   - Planning BEFORE code (Phase 0 is critical)
   - Examples + metrics BEFORE signatures
   - Optimizer choice BEFORE training

2. **Data Quality Over Quantity**
   - 5-10 high-quality examples > 50 mediocre examples
   - Input consistency is CRITICAL
   - Output quality must be 95%+

3. **Simplicity in Metrics**
   - 3-7 criteria per agent (not >10)
   - Quantifiable, weighted appropriately
   - Aligned with actual business value

4. **Proactive Decision Making**
   - Choose optimizer based on task, not trial-and-error
   - Validate with A/B testing BEFORE deployment
   - Monitor continuously AFTER deployment

### Expected Outcomes (Week 6)

**P0 Agents** (Queen, Tester, Reviewer, Coder):
- **Baseline**: 66.7%, 0%, 0%, 0% quality
- **Target**: ≥75%, ≥10%, ≥10%, ≥10% quality
- **Improvement**: ≥10% for 3/4 agents

**Cost**: $0 (Gemini free tier)

**Time**: 27 hours total (Week 6)

**Risk**: LOW (Phase 0 planning mitigates most common failures)

### Next Steps

**Immediate** (Week 6 Day 3):
1. Expand Reviewer dataset: 1 → 10 examples
2. Expand Coder dataset: 1 → 10 examples
3. Simplify metrics: 16 → 3-7 per agent
4. Create signatures + modules

**Short-term** (Week 6 Days 4-7):
1. Train all 4 P0 agents
2. A/B test baseline vs optimized
3. Deploy to production with feature flags

**Long-term** (Week 7+):
1. Expand to P1 agents if ROI > 15%
2. Collect new examples from production
3. Re-run optimization quarterly

---

**Version**: 9.0.0 (CORRECTED)
**Document**: DSPY-INTEGRATION-STRATEGY.md
**Timestamp**: 2025-10-10T00:00:00-05:00
**Status**: PRODUCTION-READY (Research-Backed)

**Authors**:
- DSPy Research Analysis: Claude Sonnet 4
- Process Correction: Based on expert transcript + official DSPy docs
- SPEK Integration: Claude Sonnet 4

**References**:
- DSPy Documentation: https://dspy.ai/
- DSPy GitHub: https://github.com/stanfordnlp/dspy
- Expert Transcript: "I Found the Easiest Way to Build Self-Optimizing AI Prompts"
- SPEK SPEC-v6-FINAL.md: Agent optimization requirements
