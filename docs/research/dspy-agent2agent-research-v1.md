# DSPy & Agent2Agent Protocol Research - Gap 4 Analysis

**Version**: 1.0
**Date**: 2025-10-08
**Status**: Complete
**Priority**: P1 - Critical
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild

---

## Executive Summary

This research document addresses **Gap 4: DSPy & Agent2Agent Protocol** from the SPEK v2 research gaps analysis. It provides comprehensive findings on Agenspy framework, Context DNA encoding, MIPROv2 optimizer, quality scoring implementation, and integration recommendations for the Queen-Princess-Drone hierarchy with 22 agents.

**Key Findings**:
- Agenspy is a protocol-first framework built on DSPy with MCP + A2A support
- Context DNA uses JSON-RPC format for cross-session persistence
- MIPROv2 optimizer achieves 2x+ performance improvements (24% -> 51% accuracy)
- Quality scoring implements 0.0-1.0 normalized metrics with comparative evaluation
- GEPA optimizer enables multi-agent RAG with reflective prompt evolution
- A2A protocol standardizes multi-agent communication across frameworks

---

## Table of Contents

1. [Agenspy Framework](#agenspy-framework)
2. [Context DNA Format](#context-dna-format)
3. [MIPROv2 Optimizer](#miprov2-optimizer)
4. [Quality Scoring Implementation](#quality-scoring-implementation)
5. [GEPA Optimizer for Multi-Agent RAG](#gepa-optimizer-for-multi-agent-rag)
6. [Agent2Agent (A2A) Protocol](#agent2agent-a2a-protocol)
7. [Integration Recommendations](#integration-recommendations)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Code Examples](#code-examples)
10. [References](#references)

---

## 1. Agenspy Framework

### Overview

**Agenspy** (Agentic DSPy) is a protocol-first AI agent framework built on top of DSPy, introduced by Superagentic AI in 2025. It enables building sophisticated, production-ready AI agents with support for multiple communication protocols including:

- **MCP (Model Context Protocol)**: Anthropic's standard for AI-tool integration
- **A2A (Agent2Agent)**: Google's multi-agent communication protocol
- **DSPy Optimization**: Automatic prompt and pipeline optimization

### Key Capabilities

1. **Protocol-First Design**: Agents communicate via standardized protocols (MCP, A2A)
2. **Multi-Framework Interoperability**: Works with AutoGen, LangChain, DSPy agents
3. **Production-Ready**: Built-in error handling, retry logic, and monitoring
4. **Optimization Engine**: Leverages DSPy's MIPROv2 and GEPA optimizers

### Installation

```bash
# Install from PyPI (when available)
pip install agenspy

# Install from GitHub (current)
git clone https://github.com/SuperagenticAI/Agenspy
cd Agenspy
pip install -e .

# Install dependencies
pip install dspy-ai>=2.5.0
pip install anthropic>=0.18.0  # For MCP support
```

### Architecture Components

```
Agenspy Architecture:
+------------------+
|   BaseAgent      |  <- Core agent abstraction
+------------------+
        |
        +-- Protocol Adapters
        |   +-- MCP Adapter (tools, resources, prompts)
        |   +-- A2A Adapter (tasks, messages, artifacts)
        |
        +-- Communication Layer
        |   +-- JSON-RPC transport
        |   +-- HTTP/SSE endpoints
        |
        +-- Optimization Layer
            +-- MIPROv2 (prompt optimization)
            +-- GEPA (program evolution)
```

### Basic Agent Implementation

```python
import dspy
from agenspy import BaseAgent
from typing import Dict, Any

class ResearchAgent(BaseAgent):
    """Research specialist agent for codebase analysis."""

    def __init__(self, name: str):
        super().__init__(name)
        self.domain = "research"
        self.capabilities = ["code_analysis", "pattern_detection", "documentation_review"]

    async def analyze_codebase(self, repo_path: str) -> Dict[str, Any]:
        """Analyze codebase for patterns and issues."""
        # Implementation uses DSPy modules
        analysis = {
            "patterns": [],
            "issues": [],
            "recommendations": []
        }
        return analysis

    async def forward(self, **kwargs) -> dspy.Prediction:
        """Process agent request with DSPy prediction."""
        task_type = kwargs.get("task_type", "analyze")

        if task_type == "analyze":
            repo_path = kwargs.get("repo_path")
            result = await self.analyze_codebase(repo_path)
            return dspy.Prediction(**result)

        return dspy.Prediction(error="Unknown task type")
```

### MCP Server Integration

```python
from agenspy.servers.mcp_python_server import PythonMCPServer

class ResearchMCPServer(PythonMCPServer):
    """MCP server exposing research agent capabilities."""

    def __init__(self, port: int = 9001):
        super().__init__(name="research-mcp-server", port=port)

        # Register tools
        self.register_tool(
            name="analyze_patterns",
            description="Analyze codebase patterns",
            parameters={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "pattern_types": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["repo_path"]
            },
            handler=self.handle_pattern_analysis
        )

        # Register resources
        self.register_resource(
            uri="research://agent/status",
            name="Agent Status",
            description="Current agent status and metrics",
            handler=self.get_agent_status
        )

    async def handle_pattern_analysis(self, **kwargs):
        """Handle pattern analysis requests."""
        repo_path = kwargs.get("repo_path")
        pattern_types = kwargs.get("pattern_types", ["all"])

        # Delegate to research agent
        result = await self.agent.analyze_codebase(repo_path)
        return result

    async def get_agent_status(self):
        """Return agent status as resource."""
        return {
            "status": "active",
            "tasks_completed": 42,
            "uptime_seconds": 3600
        }
```

### Current Status

- **GitHub Repository**: https://github.com/SuperagenticAI/Agenspy
- **Development Stage**: Active development (2025)
- **Community**: Growing adoption, 50+ technology partners
- **Documentation**: In progress, examples available
- **Production Readiness**: Beta stage, used in Agentic DevOps demos

---

## 2. Context DNA Format

### Overview

**Context DNA** is a structured encoding format for cross-session persistence in multi-agent systems. It enables agents to maintain context across sessions, coordinate state, and share knowledge effectively.

### Standard Format: JSON-RPC

Based on Model Context Protocol (MCP) specification, Context DNA uses **JSON-RPC 2.0** format:

```json
{
  "jsonrpc": "2.0",
  "id": "session-uuid",
  "method": "context/update",
  "params": {
    "agent_id": "researcher-001",
    "session_id": "20251008-session-abc123",
    "context_type": "task_execution",
    "timestamp": "2025-10-08T14:30:00Z",
    "context_data": {
      "domain": "research",
      "task": "analyze_codebase",
      "inputs": {
        "repo_path": "/path/to/repo",
        "focus_areas": ["patterns", "violations"]
      },
      "state": {
        "progress": 0.65,
        "completed_steps": ["scan_files", "detect_patterns"],
        "pending_steps": ["generate_report", "recommendations"]
      },
      "artifacts": [
        {
          "type": "analysis_result",
          "location": ".claude/.artifacts/pattern-analysis-v1.json",
          "hash": "abc123def456"
        }
      ],
      "memory_keys": [
        "research/codebase_patterns",
        "research/violations_found"
      ]
    },
    "metadata": {
      "model": "gemini-2.5-pro",
      "tokens_used": 45000,
      "cost_usd": 0.012,
      "quality_score": 0.92
    }
  }
}
```

### Context DNA Schema

```typescript
interface ContextDNA {
  // Session identification
  session_id: string;
  agent_id: string;
  timestamp: string; // ISO 8601

  // Context classification
  context_type:
    | "task_execution"
    | "agent_communication"
    | "knowledge_update"
    | "error_recovery"
    | "quality_validation";

  // Core context data
  context_data: {
    domain: string;
    task: string;
    inputs: Record<string, any>;
    state: {
      progress: number; // 0.0-1.0
      completed_steps: string[];
      pending_steps: string[];
      errors?: string[];
    };
    artifacts: Artifact[];
    memory_keys: string[];
  };

  // Execution metadata
  metadata: {
    model: string;
    tokens_used: number;
    cost_usd: number;
    quality_score: number; // 0.0-1.0
    parent_session_id?: string; // For hierarchical agents
    child_session_ids?: string[]; // For spawned agents
  };
}

interface Artifact {
  type: string;
  location: string; // File path or URI
  hash: string; // SHA-256 for validation
  size_bytes?: number;
  mime_type?: string;
}
```

### Persistence Strategies

#### Strategy 1: MCP Memory (Knowledge Graph)

```python
# Using MCP memory tools for structured context persistence
from typing import Dict, Any

async def persist_context_dna(context: Dict[str, Any]):
    """Persist context DNA to MCP memory knowledge graph."""

    # Create entity for this session
    await mcp__memory__create_entities([{
        "name": context["session_id"],
        "entityType": "agent_session",
        "observations": [
            f"Agent: {context['agent_id']}",
            f"Task: {context['context_data']['task']}",
            f"Progress: {context['context_data']['state']['progress']:.0%}",
            f"Quality: {context['metadata']['quality_score']:.2f}"
        ]
    }])

    # Create relations to artifacts
    for artifact in context["context_data"]["artifacts"]:
        await mcp__memory__create_relations([{
            "from": context["session_id"],
            "to": artifact["location"],
            "relationType": "produced_artifact"
        }])

    # Create parent-child relations for hierarchy
    if "parent_session_id" in context["metadata"]:
        await mcp__memory__create_relations([{
            "from": context["session_id"],
            "to": context["metadata"]["parent_session_id"],
            "relationType": "child_of"
        }])

async def restore_context_dna(session_id: str) -> Dict[str, Any]:
    """Restore context DNA from MCP memory."""

    # Read full graph
    graph = await mcp__memory__read_graph()

    # Search for specific session
    nodes = await mcp__memory__search_nodes(query=session_id)

    # Open specific entity
    session_data = await mcp__memory__open_nodes(names=[session_id])

    return session_data
```

#### Strategy 2: Filesystem Persistence

```python
import json
import hashlib
from pathlib import Path

class ContextDNAStore:
    """Filesystem-based Context DNA persistence."""

    def __init__(self, base_path: str = ".claude/.context"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, context: Dict[str, Any]):
        """Save context DNA to filesystem."""
        session_id = context["session_id"]
        agent_id = context["agent_id"]

        # Organize by agent -> session
        agent_dir = self.base_path / agent_id
        agent_dir.mkdir(exist_ok=True)

        # Save with timestamp in filename
        filename = f"{session_id}_{context['timestamp']}.json"
        filepath = agent_dir / filename

        # Compute hash for validation
        content = json.dumps(context, sort_keys=True, indent=2)
        hash_value = hashlib.sha256(content.encode()).hexdigest()

        # Save with hash footer
        with open(filepath, 'w') as f:
            f.write(content)
            f.write(f"\n\n# Content Hash: {hash_value}\n")

        # Create latest symlink
        latest = agent_dir / "latest.json"
        if latest.exists():
            latest.unlink()
        latest.symlink_to(filepath.name)

    def load(self, session_id: str, agent_id: str = None) -> Dict[str, Any]:
        """Load context DNA from filesystem."""
        if agent_id:
            # Load specific session
            pattern = f"{session_id}_*.json"
            matches = list((self.base_path / agent_id).glob(pattern))
            if matches:
                return json.loads(matches[0].read_text())
        else:
            # Search all agents
            for agent_dir in self.base_path.iterdir():
                matches = list(agent_dir.glob(f"{session_id}_*.json"))
                if matches:
                    return json.loads(matches[0].read_text())

        raise FileNotFoundError(f"Context DNA not found: {session_id}")

    def load_latest(self, agent_id: str) -> Dict[str, Any]:
        """Load latest context for agent."""
        latest = self.base_path / agent_id / "latest.json"
        if latest.exists():
            return json.loads(latest.read_text())
        raise FileNotFoundError(f"No context found for agent: {agent_id}")
```

### Context DNA Best Practices

1. **Immutable Sessions**: Never modify existing context DNA, create new versions
2. **Hash Validation**: Always validate content hash before restoring
3. **Memory Cleanup**: Prune old sessions beyond retention policy (30 days)
4. **Hierarchical Tracking**: Maintain parent-child relations for agent spawning
5. **Artifact References**: Store artifact locations, not full content
6. **Quality Metadata**: Include quality scores for context filtering
7. **Cost Tracking**: Record token usage and costs for optimization

---

## 3. MIPROv2 Optimizer

### Overview

**MIPROv2** (Multi-Prompt Instruction Proposal Optimizer Version 2) is a DSPy optimizer capable of jointly optimizing both instructions and few-shot examples. It achieves significant performance improvements through Bayesian optimization and surrogate models.

### Performance Benchmarks

- **ReAct Agent**: 24% -> 51% accuracy (2.13x improvement)
- **RAG Pipeline**: 30% -> 68% accuracy (2.27x improvement)
- **Classification**: 65% -> 89% accuracy (1.37x improvement)

### How MIPROv2 Works

#### Three-Stage Optimization Process

```
Stage 1: BOOTSTRAPPING
+---------------------+
| Run program many    |
| times on training   | --> Collect execution traces
| data to collect     |
| input/output traces | --> Filter high-scoring trajectories
+---------------------+

Stage 2: GROUNDED PROPOSAL
+---------------------+
| Analyze program     |
| code, data, and     | --> Draft potential instructions
| traces to generate  | --> Create few-shot examples
| instruction         |
| candidates          |
+---------------------+

Stage 3: DISCRETE SEARCH
+---------------------+
| Sample mini-batches |
| Propose instruction | --> Evaluate candidate programs
| combinations        | --> Update surrogate model
| Update Bayesian     | --> Iterate until convergence
| optimizer           |
+---------------------+
```

#### Mathematical Foundation

MIPROv2 uses Bayesian Optimization to model:

```
P(score | instructions, examples)

Where:
- instructions: Set of prompt instructions for each module
- examples: Few-shot demonstrations
- score: Metric value (0.0-1.0)
```

The surrogate model guides exploration-exploitation tradeoff:
- **Exploration**: Try novel instruction combinations
- **Exploitation**: Refine known high-performing combinations

### Implementation Example

```python
import dspy
from dspy.teleprompt import MIPROv2

# 1. Define your DSPy program
class RAGPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=3)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

# 2. Define evaluation metric (0.0-1.0)
def validate_answer(example, pred, trace=None):
    """Metric returning 0.0-1.0 score."""
    answer_match = float(example.answer.lower() == pred.answer.lower())

    # Check if answer is grounded in context
    context_match = any(
        pred.answer.lower() in c.lower()
        for c in pred.context
    )

    if trace is None:  # Evaluation mode
        return (answer_match + float(context_match)) / 2.0
    else:  # Bootstrapping mode
        return answer_match and context_match

# 3. Prepare training data
trainset = [
    dspy.Example(
        question="What is DSPy?",
        answer="A framework for programming language models"
    ).with_inputs("question"),
    # ... more examples
]

# 4. Configure optimizer
mipro_optimizer = MIPROv2(
    metric=validate_answer,
    num_candidates=10,  # Instructions to try per iteration
    init_temperature=1.4,  # Exploration temperature
    verbose=True,
    track_stats=True,
    requires_permission_to_run=False  # Set True for production
)

# 5. Run optimization
optimized_program = mipro_optimizer.compile(
    student=RAGPipeline(),
    trainset=trainset,
    num_trials=50,  # Bayesian optimization iterations
    max_bootstrapped_demos=4,  # Few-shot examples per module
    max_labeled_demos=8,  # Max demonstrations to use
    eval_kwargs={"num_threads": 4, "display_progress": True}
)

# 6. Compare performance
baseline_score = dspy.Evaluate(
    devset=testset,
    metric=validate_answer,
    num_threads=4
)(RAGPipeline())

optimized_score = dspy.Evaluate(
    devset=testset,
    metric=validate_answer,
    num_threads=4
)(optimized_program)

print(f"Baseline: {baseline_score:.2%}")
print(f"Optimized: {optimized_score:.2%}")
print(f"Improvement: {(optimized_score/baseline_score - 1):.1%}")
```

### Agent Prompt Optimization

For optimizing agent prompts in the Queen-Princess-Drone hierarchy:

```python
# Define agent as DSPy module
class QueenAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.plan = dspy.ChainOfThought(
            "task_description, available_agents -> delegation_plan"
        )
        self.validate = dspy.ChainOfThought(
            "delegation_plan, constraints -> validation_result"
        )

    def forward(self, task_description, available_agents, constraints):
        plan = self.plan(
            task_description=task_description,
            available_agents=available_agents
        )
        validation = self.validate(
            delegation_plan=plan.delegation_plan,
            constraints=constraints
        )
        return validation

# Metric for queen agent (0.0-1.0)
def validate_queen_delegation(example, pred, trace=None):
    """Validate queen agent delegation quality."""

    # Check plan completeness
    has_all_tasks = all(
        task in pred.delegation_plan
        for task in example.required_tasks
    )

    # Check agent assignment validity
    valid_assignments = all(
        agent in example.available_agents
        for agent in extract_assigned_agents(pred.delegation_plan)
    )

    # Check constraint satisfaction
    satisfies_constraints = check_constraints(
        pred.validation_result,
        example.constraints
    )

    if trace is None:
        # Return normalized score
        return (
            float(has_all_tasks) * 0.4 +
            float(valid_assignments) * 0.3 +
            float(satisfies_constraints) * 0.3
        )
    else:
        return has_all_tasks and valid_assignments and satisfies_constraints

# Optimize queen agent
optimized_queen = mipro_optimizer.compile(
    student=QueenAgent(),
    trainset=queen_trainset,
    num_trials=30,
    max_bootstrapped_demos=3
)
```

### MIPROv2 Configuration Parameters

```python
MIPROv2(
    metric=callable,              # Required: scoring function (0.0-1.0)

    # Optimization parameters
    num_candidates=10,            # Instructions per iteration (default: 10)
    init_temperature=1.4,         # Exploration temperature (default: 1.4)
    num_trials=50,                # Bayesian optimization iterations (default: 50)

    # Few-shot parameters
    max_bootstrapped_demos=4,     # Examples per module (default: 4)
    max_labeled_demos=8,          # Max demonstrations total (default: 8)

    # Search parameters
    minibatch_size=25,            # Training subset size (default: 25)
    minibatch_full_eval_steps=10, # Full eval frequency (default: 10)

    # Agent-specific (optional)
    task_config=TaskConfig(
        tools=[...],              # Enable agent optimization
        max_iterations=10         # ReAct agent iterations
    ),

    # Execution parameters
    num_threads=4,                # Parallel evaluation threads
    verbose=True,                 # Show optimization progress
    track_stats=True,             # Track detailed statistics
    requires_permission_to_run=False  # Require user confirmation
)
```

### Best Practices

1. **Start Small**: Begin with num_trials=20-30, increase if needed
2. **Quality Metrics**: Ensure metric returns 0.0-1.0 normalized scores
3. **Training Data**: Minimum 50 examples, ideal 200+ for complex agents
4. **Few-Shot Examples**: Start with max_bootstrapped_demos=3-4
5. **Parallel Evaluation**: Use num_threads=4-8 for faster optimization
6. **Agent Tools**: Provide task_config.tools for ReAct agent optimization
7. **Cost Management**: Monitor token usage, can consume 100K+ tokens
8. **Iterative Refinement**: Optimize incrementally, save checkpoints

---

## 4. Quality Scoring Implementation

### Overview

DSPy implements quality scoring with 0.0-1.0 normalized metrics that support comparative evaluation across different models, prompts, and configurations.

### Metric Design Principles

1. **Normalization**: All scores in 0.0-1.0 range for consistency
2. **Composability**: Combine multiple sub-metrics with weighted sums
3. **Dual Mode**: Support evaluation (float) and bootstrapping (bool) modes
4. **Interpretability**: Scores should be human-understandable
5. **Stability**: Small input changes should produce small score changes

### Basic Metric Implementation

```python
def basic_metric(example, pred, trace=None):
    """
    Basic 0.0-1.0 metric template.

    Args:
        example: Ground truth example with inputs and expected outputs
        pred: Prediction from DSPy program
        trace: Optional trace for bootstrapping mode

    Returns:
        float (0.0-1.0) for evaluation, bool for bootstrapping
    """
    # Check correctness
    is_correct = example.answer.lower() == pred.answer.lower()

    if trace is None:
        # Evaluation mode: return 0.0-1.0 score
        return 1.0 if is_correct else 0.0
    else:
        # Bootstrapping mode: return boolean
        return is_correct
```

### Composite Metrics

```python
from typing import List, Tuple

def weighted_composite_metric(
    checks: List[Tuple[str, callable, float]]
) -> callable:
    """
    Create composite metric from weighted checks.

    Args:
        checks: List of (name, check_function, weight) tuples

    Returns:
        Metric function returning 0.0-1.0 score
    """
    def metric(example, pred, trace=None):
        total_weight = sum(weight for _, _, weight in checks)
        score = 0.0

        for name, check_fn, weight in checks:
            result = check_fn(example, pred)
            score += (float(result) * weight)

        normalized_score = score / total_weight

        if trace is None:
            return normalized_score
        else:
            # Bootstrapping: require all checks to pass
            return normalized_score >= 0.8  # Threshold

    return metric

# Example usage
agent_quality_metric = weighted_composite_metric([
    ("completeness", check_task_completeness, 0.3),
    ("correctness", check_answer_correctness, 0.4),
    ("efficiency", check_token_efficiency, 0.1),
    ("safety", check_constraint_satisfaction, 0.2)
])
```

### Advanced Metrics

#### Semantic F1 Score

```python
class SemanticF1:
    """Semantic F1 score using embeddings."""

    def __init__(self, embedding_model="text-embedding-3-small"):
        self.embeddings = dspy.Embeddings(model=embedding_model)

    def __call__(self, example, pred, trace=None):
        # Get embeddings
        expected_emb = self.embeddings.embed(example.answer)
        predicted_emb = self.embeddings.embed(pred.answer)

        # Compute cosine similarity (0.0-1.0)
        similarity = cosine_similarity(expected_emb, predicted_emb)

        # Extract key terms for precision/recall
        expected_terms = extract_terms(example.answer)
        predicted_terms = extract_terms(pred.answer)

        # Calculate F1
        precision = len(expected_terms & predicted_terms) / len(predicted_terms)
        recall = len(expected_terms & predicted_terms) / len(expected_terms)

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        # Combine with semantic similarity
        score = (f1 * 0.6) + (similarity * 0.4)

        if trace is None:
            return score
        else:
            return score >= 0.75

def cosine_similarity(a, b):
    """Compute cosine similarity between embeddings."""
    import numpy as np
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def extract_terms(text: str) -> set:
    """Extract key terms from text."""
    import re
    words = re.findall(r'\w+', text.lower())
    # Filter stopwords and short words
    return {w for w in words if len(w) > 3 and w not in STOPWORDS}
```

#### Grounded Answer Metric

```python
class GroundedAnswerMetric:
    """Validate answer is grounded in retrieved context."""

    def __call__(self, example, pred, trace=None):
        answer = pred.answer.lower()
        context_passages = getattr(pred, 'context', [])

        # Check answer appears in context
        is_grounded = any(
            answer in passage.lower()
            for passage in context_passages
        )

        # Check answer matches expected
        is_correct = (
            example.answer.lower() in answer or
            answer in example.answer.lower()
        )

        # Check answer length reasonable
        is_concise = 10 <= len(answer.split()) <= 100

        # Composite score
        groundedness = float(is_grounded)
        correctness = float(is_correct)
        conciseness = float(is_concise)

        score = (
            groundedness * 0.4 +
            correctness * 0.5 +
            conciseness * 0.1
        )

        if trace is None:
            return score
        else:
            return is_grounded and is_correct
```

### Agent-Specific Metrics

For Queen-Princess-Drone hierarchy:

```python
# Queen Agent Metric
def queen_delegation_metric(example, pred, trace=None):
    """Validate queen agent task delegation."""

    # 1. Completeness: All tasks assigned
    tasks_assigned = extract_tasks(pred.delegation_plan)
    completeness = len(tasks_assigned) / len(example.required_tasks)

    # 2. Load Balancing: Fair distribution
    agent_loads = compute_agent_loads(pred.delegation_plan)
    balance_score = 1.0 - coefficient_of_variation(agent_loads)

    # 3. Constraint Satisfaction: Requirements met
    constraint_score = check_constraints(
        pred.delegation_plan,
        example.constraints
    )

    # 4. Estimated Quality: Expected outcome
    quality_estimate = estimate_outcome_quality(
        pred.delegation_plan,
        example.task_difficulty
    )

    # Weighted composite
    score = (
        completeness * 0.3 +
        balance_score * 0.2 +
        constraint_score * 0.3 +
        quality_estimate * 0.2
    )

    if trace is None:
        return max(0.0, min(1.0, score))
    else:
        return score >= 0.8

# Princess Agent Metric
def princess_orchestration_metric(example, pred, trace=None):
    """Validate princess agent task orchestration."""

    # 1. Execution Order: Dependencies respected
    order_valid = validate_execution_order(
        pred.execution_plan,
        example.dependencies
    )

    # 2. Resource Allocation: Drones assigned
    allocation_valid = validate_resource_allocation(
        pred.execution_plan,
        example.available_drones
    )

    # 3. Parallel Efficiency: Parallelism utilized
    parallelism = compute_parallelism_score(pred.execution_plan)

    # 4. Risk Mitigation: Fallbacks defined
    risk_score = validate_fallback_plans(pred.execution_plan)

    score = (
        float(order_valid) * 0.3 +
        float(allocation_valid) * 0.3 +
        parallelism * 0.2 +
        risk_score * 0.2
    )

    if trace is None:
        return score
    else:
        return order_valid and allocation_valid

# Drone Agent Metric
def drone_execution_metric(example, pred, trace=None):
    """Validate drone agent task execution."""

    # 1. Task Completion: Output produced
    is_complete = hasattr(pred, 'result') and pred.result is not None

    # 2. Quality Gates: NASA/FSM compliance
    nasa_score = check_nasa_compliance(pred.result)
    fsm_score = check_fsm_compliance(pred.result)

    # 3. Test Coverage: Tests pass
    test_score = check_test_coverage(pred.result)

    # 4. No Theater: Genuine work
    theater_score = 1.0 - check_theater_patterns(pred.result)

    score = (
        float(is_complete) * 0.2 +
        nasa_score * 0.25 +
        fsm_score * 0.25 +
        test_score * 0.2 +
        theater_score * 0.1
    )

    if trace is None:
        return score
    else:
        return is_complete and nasa_score >= 0.92 and fsm_score >= 0.90
```

### Evaluation Framework

```python
# Evaluate with metrics
from dspy import Evaluate

# Setup evaluator
evaluator = Evaluate(
    devset=test_examples,
    metric=queen_delegation_metric,
    num_threads=4,
    display_progress=True,
    display_table=5,  # Show top 5 examples
    return_all_scores=True
)

# Run evaluation
scores = evaluator(optimized_queen_agent)

# Analyze results
print(f"Mean Score: {np.mean(scores):.3f}")
print(f"Std Dev: {np.std(scores):.3f}")
print(f"Min Score: {np.min(scores):.3f}")
print(f"Max Score: {np.max(scores):.3f}")
print(f"Pass Rate (>=0.8): {np.mean([s >= 0.8 for s in scores]):.1%}")
```

### Comparative Evaluation

```python
def compare_agents(
    agents: List[Tuple[str, dspy.Module]],
    testset: List[dspy.Example],
    metric: callable
) -> dict:
    """Compare multiple agents on same testset."""

    results = {}

    for name, agent in agents:
        evaluator = Evaluate(
            devset=testset,
            metric=metric,
            num_threads=4
        )

        scores = evaluator(agent, return_all_scores=True)

        results[name] = {
            "mean": np.mean(scores),
            "std": np.std(scores),
            "min": np.min(scores),
            "max": np.max(scores),
            "scores": scores
        }

    # Print comparison table
    print("\nAgent Comparison:")
    print(f"{'Agent':<20} {'Mean':<8} {'Std':<8} {'Min':<8} {'Max':<8}")
    print("-" * 60)
    for name, stats in results.items():
        print(
            f"{name:<20} "
            f"{stats['mean']:.3f}    "
            f"{stats['std']:.3f}    "
            f"{stats['min']:.3f}    "
            f"{stats['max']:.3f}"
        )

    return results

# Example usage
comparison = compare_agents(
    agents=[
        ("baseline_queen", baseline_queen_agent),
        ("optimized_queen_v1", optimized_queen_v1),
        ("optimized_queen_v2", optimized_queen_v2)
    ],
    testset=queen_test_examples,
    metric=queen_delegation_metric
)
```

---

## 5. GEPA Optimizer for Multi-Agent RAG

### Overview

**GEPA** (Generalized Evolutionary Prompt Adapter) is a reflective prompt optimizer that works by leveraging LLM's ability to reflect on DSPy program trajectories, identifying what went well, what didn't, and what can be improved. It uses evolutionary search algorithms with LLM-based reflection for mutating candidates.

### Key Capabilities

1. **Reflective Evolution**: Uses LLM to reflect on failures and suggest improvements
2. **Full Program Optimization**: Optimizes signatures, modules, and control flow
3. **Multi-Agent Support**: Particularly effective for coordinating multiple specialized agents
4. **High-Stakes Domains**: Ideal for healthcare, finance, defense applications

### How GEPA Works

```
GEPA Optimization Process:
+-------------------------+
| 1. GENERATE VARIANTS    |
|    Create N versions of |
|    the prompt           |
+-------------------------+
         |
         v
+-------------------------+
| 2. EVALUATE VARIANTS    |
|    Run all versions on  |
|    examples, Judge      |
|    scores performance   |
+-------------------------+
         |
         v
+-------------------------+
| 3. REFLECT ON FAILURES  |
|    Teacher analyzes     |
|    failed examples,     |
|    suggests changes     |
+-------------------------+
         |
         v
+-------------------------+
| 4. EVOLVE POPULATION    |
|    Apply suggestions to |
|    create new variants  |
+-------------------------+
         |
         v
    Repeat until convergence
```

### Multi-Agent RAG Architecture

```python
import dspy
from dspy.teleprompt import GEPA

# Step 1: Define specialized sub-agents
class MedicalAgent(dspy.Module):
    """Specialist for medical queries."""

    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought(
            "context, question -> medical_answer"
        )

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

class LegalAgent(dspy.Module):
    """Specialist for legal queries."""

    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought(
            "context, question -> legal_answer"
        )

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

class FinanceAgent(dspy.Module):
    """Specialist for finance queries."""

    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought(
            "context, question -> finance_answer"
        )

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

# Step 2: Define lead/coordinator agent
class LeadAgent(dspy.Module):
    """Coordinates specialized agents."""

    def __init__(self):
        super().__init__()

        # Initialize sub-agents
        self.medical = MedicalAgent()
        self.legal = LegalAgent()
        self.finance = FinanceAgent()

        # Routing module
        self.router = dspy.ChainOfThought(
            "question -> domain: str, confidence: float"
        )

        # Synthesis module
        self.synthesize = dspy.ChainOfThought(
            "question, answers -> final_answer"
        )

    def forward(self, question):
        # Route to appropriate agent
        routing = self.router(question=question)
        domain = routing.domain.lower()

        # Get answer from specialist
        if domain == "medical":
            specialist_answer = self.medical(question)
        elif domain == "legal":
            specialist_answer = self.legal(question)
        elif domain == "finance":
            specialist_answer = self.finance(question)
        else:
            # Fallback: query all agents
            answers = [
                self.medical(question),
                self.legal(question),
                self.finance(question)
            ]
            specialist_answer = self.synthesize(
                question=question,
                answers=answers
            )

        return specialist_answer

# Step 3: Define metric for lead agent
def multi_agent_rag_metric(example, pred, trace=None):
    """Metric for multi-agent RAG system."""

    # Check domain routing accuracy
    correct_domain = (
        example.domain.lower() in pred.domain.lower() or
        pred.domain.lower() in example.domain.lower()
    )

    # Check answer quality
    answer_correct = check_answer_correctness(example.answer, pred.answer)

    # Check confidence calibration
    confidence_calibrated = (
        (pred.confidence >= 0.8 and answer_correct) or
        (pred.confidence < 0.8 and not answer_correct)
    )

    # Composite score
    score = (
        float(correct_domain) * 0.3 +
        float(answer_correct) * 0.5 +
        float(confidence_calibrated) * 0.2
    )

    if trace is None:
        return score
    else:
        return correct_domain and answer_correct

# Step 4: Optimize with GEPA
gepa_optimizer = GEPA(
    metric=multi_agent_rag_metric,
    breadth=5,  # Number of prompt variants
    depth=3,    # Evolutionary generations
    init_temperature=1.0,
    verbose=True
)

# Prepare training data
trainset = [
    dspy.Example(
        question="What are the side effects of aspirin?",
        domain="medical",
        answer="Common side effects include stomach upset..."
    ).with_inputs("question"),
    # ... more examples
]

# Optimize lead agent
optimized_lead = gepa_optimizer.compile(
    student=LeadAgent(),
    trainset=trainset,
    max_iters=20
)
```

### GEPA for Queen-Princess-Drone Hierarchy

```python
# Queen Agent: Task delegation coordinator
class QueenAgentProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze_task = dspy.ChainOfThought(
            "task_description -> task_breakdown, complexity, requirements"
        )
        self.assign_agents = dspy.ChainOfThought(
            "task_breakdown, available_agents -> delegation_plan"
        )
        self.validate_plan = dspy.ChainOfThought(
            "delegation_plan, constraints -> validation, adjustments"
        )

    def forward(self, task_description, available_agents, constraints):
        # Analyze task
        analysis = self.analyze_task(task_description=task_description)

        # Assign to agents
        plan = self.assign_agents(
            task_breakdown=analysis.task_breakdown,
            available_agents=available_agents
        )

        # Validate
        validation = self.validate_plan(
            delegation_plan=plan.delegation_plan,
            constraints=constraints
        )

        return validation

# Optimize Queen Agent with GEPA
queen_gepa = GEPA(
    metric=queen_delegation_metric,
    breadth=8,  # More variants for complex coordination
    depth=4,    # Deeper evolution
    init_temperature=1.2
)

optimized_queen = queen_gepa.compile(
    student=QueenAgentProgram(),
    trainset=queen_trainset,
    max_iters=30
)

# Princess Agent: Task orchestration
class PrincessAgentProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.plan_execution = dspy.ChainOfThought(
            "task_list, dependencies -> execution_plan"
        )
        self.allocate_resources = dspy.ChainOfThought(
            "execution_plan, available_drones -> resource_allocation"
        )
        self.monitor_progress = dspy.ChainOfThought(
            "progress_updates -> status, interventions"
        )

    def forward(self, task_list, dependencies, available_drones):
        # Plan execution
        plan = self.plan_execution(
            task_list=task_list,
            dependencies=dependencies
        )

        # Allocate resources
        allocation = self.allocate_resources(
            execution_plan=plan.execution_plan,
            available_drones=available_drones
        )

        return allocation

# Optimize Princess Agent
princess_gepa = GEPA(
    metric=princess_orchestration_metric,
    breadth=6,
    depth=3
)

optimized_princess = princess_gepa.compile(
    student=PrincessAgentProgram(),
    trainset=princess_trainset,
    max_iters=25
)
```

### GEPA Configuration

```python
GEPA(
    metric=callable,           # Required: evaluation metric (0.0-1.0)

    # Evolution parameters
    breadth=5,                 # Prompt variants per generation (default: 5)
    depth=3,                   # Evolutionary generations (default: 3)
    init_temperature=1.0,      # Initial exploration temperature

    # Reflection parameters
    teacher_model=None,        # LLM for reflection (default: same as main)
    judge_model=None,          # LLM for scoring (default: same as main)

    # Optimization parameters
    max_iters=20,              # Maximum iterations
    num_candidates_per_iter=5, # Candidates to evaluate per iteration

    # Execution parameters
    verbose=True,              # Show progress
    track_stats=True           # Track detailed statistics
)
```

### GEPA vs MIPROv2 Comparison

| Feature | GEPA | MIPROv2 |
|---------|------|---------|
| **Optimization Approach** | Evolutionary search with reflection | Bayesian optimization |
| **Best For** | Complex multi-agent systems | Single agents, RAG pipelines |
| **Optimization Scope** | Full programs (signatures + control flow) | Instructions + few-shot examples |
| **Iterations Required** | 15-30 | 30-50 |
| **Compute Cost** | Medium | High |
| **Interpretability** | High (reflections explain changes) | Medium (Bayesian model opaque) |
| **Performance Gain** | 1.5-2.5x | 2.0-3.0x |

### Best Practices for Multi-Agent RAG

1. **Specialized Agents**: Create domain-specific agents with focused retrieval
2. **Lead Coordinator**: Use lead agent for routing and synthesis
3. **Metric Design**: Ensure metric captures routing accuracy + answer quality
4. **Training Data**: Include examples from all domains (balanced)
5. **Iterative Optimization**: Optimize sub-agents first, then lead agent
6. **Fallback Strategies**: Handle unknown domains gracefully
7. **Confidence Calibration**: Train agents to output reliable confidence scores

---

## 6. Agent2Agent (A2A) Protocol

### Overview

The **Agent2Agent (A2A) protocol** is an open communication protocol for AI agents designed for multi-agent systems, allowing interoperability between AI agents from varied providers or those built using different AI agent frameworks. Initially introduced by Google in April 2025, it has been adopted by 50+ technology partners including Microsoft, Atlassian, Box, Cohere, MongoDB, and PayPal.

### Core Concepts

#### 1. Agent Cards

Agents advertise their capabilities using an **Agent Card** in JSON format:

```json
{
  "agent_id": "research-agent-001",
  "name": "Research Specialist",
  "version": "1.0.0",
  "description": "Specialized agent for codebase research and pattern analysis",
  "capabilities": [
    "code_analysis",
    "pattern_detection",
    "documentation_review",
    "dependency_mapping"
  ],
  "supported_domains": ["research", "analysis"],
  "input_format": {
    "type": "object",
    "properties": {
      "task_type": {"type": "string", "enum": ["analyze", "search", "review"]},
      "repo_path": {"type": "string"},
      "focus_areas": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["task_type", "repo_path"]
  },
  "output_format": {
    "type": "object",
    "properties": {
      "patterns": {"type": "array"},
      "issues": {"type": "array"},
      "recommendations": {"type": "array"}
    }
  },
  "quality_guarantees": {
    "response_time_ms": 5000,
    "accuracy_threshold": 0.85,
    "supported_concurrency": 3
  },
  "endpoint": "http://localhost:9001/a2a",
  "protocol_version": "1.0"
}
```

#### 2. Tasks

Communication is oriented towards **task completion** with defined lifecycle:

```json
{
  "task_id": "task-uuid-12345",
  "from_agent": "queen-agent",
  "to_agent": "research-agent-001",
  "task_type": "analyze_codebase",
  "priority": "high",
  "deadline": "2025-10-08T16:00:00Z",
  "parameters": {
    "repo_path": "/path/to/codebase",
    "focus_areas": ["connascence", "nasa_compliance"]
  },
  "context": {
    "session_id": "session-abc123",
    "parent_task_id": "task-uuid-parent",
    "previous_results": [...]
  },
  "status": "pending"
}
```

Task lifecycle states:
- `pending`: Task created, awaiting acceptance
- `accepted`: Agent accepted task
- `in_progress`: Agent working on task
- `completed`: Task finished successfully
- `failed`: Task failed with error
- `cancelled`: Task cancelled by requester

#### 3. Messages

Messages relay answers, context, instructions, prompts, questions, replies and status updates:

```json
{
  "message_id": "msg-uuid-67890",
  "conversation_id": "conv-uuid-abc",
  "from_agent": "research-agent-001",
  "to_agent": "queen-agent",
  "message_type": "progress_update",
  "timestamp": "2025-10-08T14:45:00Z",
  "content": {
    "task_id": "task-uuid-12345",
    "progress": 0.65,
    "status": "in_progress",
    "current_step": "analyzing_patterns",
    "preliminary_findings": {
      "patterns_detected": 12,
      "violations_found": 5
    }
  },
  "requires_response": false
}
```

Message types:
- `task_assignment`: Assign task to agent
- `task_acceptance`: Agent accepts task
- `task_rejection`: Agent rejects task
- `progress_update`: Status update during execution
- `result`: Final task result
- `error`: Error notification
- `query`: Question requiring response
- `response`: Answer to query

#### 4. Artifacts

An artifact is a tangible product generated by the A2A server:

```json
{
  "artifact_id": "artifact-uuid-111",
  "task_id": "task-uuid-12345",
  "type": "analysis_report",
  "name": "connascence-analysis-v1.json",
  "mime_type": "application/json",
  "size_bytes": 45678,
  "location": ".claude/.artifacts/connascence-analysis-v1.json",
  "hash": "sha256:abc123def456...",
  "created_at": "2025-10-08T15:00:00Z",
  "metadata": {
    "quality_score": 0.92,
    "nasa_compliance": 0.94,
    "theater_score": 0.15
  }
}
```

### A2A Server Implementation

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uuid

app = FastAPI()

# Data models
class AgentCard(BaseModel):
    agent_id: str
    name: str
    version: str
    description: str
    capabilities: List[str]
    supported_domains: List[str]
    endpoint: str
    protocol_version: str = "1.0"

class Task(BaseModel):
    task_id: str
    from_agent: str
    to_agent: str
    task_type: str
    priority: str
    parameters: Dict[str, Any]
    status: str = "pending"

class Message(BaseModel):
    message_id: str
    conversation_id: str
    from_agent: str
    to_agent: str
    message_type: str
    content: Dict[str, Any]
    requires_response: bool = False

# In-memory storage
agent_registry: Dict[str, AgentCard] = {}
tasks: Dict[str, Task] = {}
messages: List[Message] = []

# A2A Endpoints

@app.post("/a2a/register")
async def register_agent(card: AgentCard):
    """Register agent with A2A server."""
    agent_registry[card.agent_id] = card
    return {"status": "registered", "agent_id": card.agent_id}

@app.get("/a2a/agents")
async def list_agents():
    """List all registered agents."""
    return {"agents": list(agent_registry.values())}

@app.get("/a2a/agents/{agent_id}")
async def get_agent_card(agent_id: str):
    """Get specific agent card."""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_registry[agent_id]

@app.post("/a2a/tasks")
async def create_task(task: Task):
    """Create new task for agent."""
    task.task_id = str(uuid.uuid4())
    tasks[task.task_id] = task

    # Send task assignment message
    message = Message(
        message_id=str(uuid.uuid4()),
        conversation_id=task.task_id,
        from_agent=task.from_agent,
        to_agent=task.to_agent,
        message_type="task_assignment",
        content=task.dict(),
        requires_response=True
    )
    messages.append(message)

    return {"task_id": task.task_id, "status": "created"}

@app.get("/a2a/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.put("/a2a/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: str):
    """Update task status."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks[task_id].status = status
    return {"task_id": task_id, "status": status}

@app.post("/a2a/messages")
async def send_message(message: Message):
    """Send message between agents."""
    message.message_id = str(uuid.uuid4())
    messages.append(message)
    return {"message_id": message.message_id, "status": "sent"}

@app.get("/a2a/messages/{agent_id}")
async def get_messages(agent_id: str, limit: int = 10):
    """Get messages for agent."""
    agent_messages = [
        m for m in messages
        if m.to_agent == agent_id
    ]
    return {"messages": agent_messages[-limit:]}
```

### A2A Client Implementation

```python
import httpx
from typing import Dict, Any

class A2AClient:
    """Client for A2A protocol communication."""

    def __init__(self, server_url: str, agent_id: str):
        self.server_url = server_url
        self.agent_id = agent_id
        self.client = httpx.AsyncClient()

    async def register(self, card: AgentCard):
        """Register agent with A2A server."""
        response = await self.client.post(
            f"{self.server_url}/a2a/register",
            json=card.dict()
        )
        return response.json()

    async def discover_agents(self) -> List[AgentCard]:
        """Discover available agents."""
        response = await self.client.get(f"{self.server_url}/a2a/agents")
        return [AgentCard(**a) for a in response.json()["agents"]]

    async def assign_task(
        self,
        to_agent: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: str = "medium"
    ) -> str:
        """Assign task to another agent."""
        task = Task(
            task_id="",  # Will be assigned by server
            from_agent=self.agent_id,
            to_agent=to_agent,
            task_type=task_type,
            priority=priority,
            parameters=parameters
        )

        response = await self.client.post(
            f"{self.server_url}/a2a/tasks",
            json=task.dict()
        )
        return response.json()["task_id"]

    async def check_task_status(self, task_id: str) -> str:
        """Check task status."""
        response = await self.client.get(
            f"{self.server_url}/a2a/tasks/{task_id}"
        )
        return response.json()["status"]

    async def send_message(
        self,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any],
        conversation_id: str = None
    ):
        """Send message to another agent."""
        message = Message(
            message_id="",
            conversation_id=conversation_id or str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content
        )

        response = await self.client.post(
            f"{self.server_url}/a2a/messages",
            json=message.dict()
        )
        return response.json()

    async def poll_messages(self, limit: int = 10) -> List[Message]:
        """Poll for new messages."""
        response = await self.client.get(
            f"{self.server_url}/a2a/messages/{self.agent_id}",
            params={"limit": limit}
        )
        return [Message(**m) for m in response.json()["messages"]]
```

### Queen-Princess-Drone A2A Integration

```python
# Queen Agent with A2A
class QueenAgentA2A:
    def __init__(self, a2a_server_url: str):
        self.agent_id = "queen-agent"
        self.a2a = A2AClient(a2a_server_url, self.agent_id)

        # Register with A2A
        self.card = AgentCard(
            agent_id=self.agent_id,
            name="Queen Agent",
            version="1.0.0",
            description="Top-level coordinator for task delegation",
            capabilities=["task_decomposition", "agent_selection", "validation"],
            supported_domains=["coordination", "planning"],
            endpoint=f"http://localhost:9000/queen"
        )

    async def initialize(self):
        """Initialize and register."""
        await self.a2a.register(self.card)

    async def delegate_task(self, task_description: str):
        """Delegate task to princess agents."""

        # Discover available princess agents
        agents = await self.a2a.discover_agents()
        princess_agents = [
            a for a in agents
            if "princess" in a.agent_id.lower()
        ]

        # Decompose task
        subtasks = self.decompose_task(task_description)

        # Assign to princess agents
        task_ids = []
        for i, subtask in enumerate(subtasks):
            princess = princess_agents[i % len(princess_agents)]

            task_id = await self.a2a.assign_task(
                to_agent=princess.agent_id,
                task_type="execute_subtask",
                parameters={"subtask": subtask},
                priority="high"
            )
            task_ids.append(task_id)

        # Monitor progress
        return await self.monitor_tasks(task_ids)

    async def monitor_tasks(self, task_ids: List[str]):
        """Monitor task completion."""
        pending = set(task_ids)

        while pending:
            for task_id in list(pending):
                status = await self.a2a.check_task_status(task_id)

                if status in ["completed", "failed"]:
                    pending.remove(task_id)

            await asyncio.sleep(1)

        return "All tasks completed"

# Princess Agent with A2A
class PrincessAgentA2A:
    def __init__(self, a2a_server_url: str, princess_id: str, domain: str):
        self.agent_id = princess_id
        self.domain = domain
        self.a2a = A2AClient(a2a_server_url, self.agent_id)

        # Register
        self.card = AgentCard(
            agent_id=self.agent_id,
            name=f"Princess Agent ({domain})",
            version="1.0.0",
            description=f"Domain specialist for {domain}",
            capabilities=["task_orchestration", "resource_allocation"],
            supported_domains=[domain],
            endpoint=f"http://localhost:900{hash(princess_id) % 10}/princess"
        )

    async def initialize(self):
        """Initialize and register."""
        await self.a2a.register(self.card)

        # Start message polling
        asyncio.create_task(self.poll_tasks())

    async def poll_tasks(self):
        """Poll for task assignments."""
        while True:
            messages = await self.a2a.poll_messages()

            for message in messages:
                if message.message_type == "task_assignment":
                    await self.handle_task(message.content)

            await asyncio.sleep(1)

    async def handle_task(self, task_data: Dict[str, Any]):
        """Handle assigned task."""
        task_id = task_data["task_id"]
        subtask = task_data["parameters"]["subtask"]

        # Update status
        await self.a2a.client.put(
            f"{self.a2a.server_url}/a2a/tasks/{task_id}/status",
            params={"status": "in_progress"}
        )

        # Delegate to drones
        result = await self.delegate_to_drones(subtask)

        # Update status
        await self.a2a.client.put(
            f"{self.a2a.server_url}/a2a/tasks/{task_id}/status",
            params={"status": "completed"}
        )

        # Send result message
        await self.a2a.send_message(
            to_agent=task_data["from_agent"],
            message_type="result",
            content={"task_id": task_id, "result": result},
            conversation_id=task_id
        )
```

### A2A vs MCP Comparison

| Feature | A2A | MCP |
|---------|-----|-----|
| **Purpose** | Agent-to-agent communication | LLM-to-tool integration |
| **Scope** | Multi-agent systems | Single agent + tools |
| **Protocol Type** | Application-level | System-level |
| **Message Format** | Tasks, Messages, Artifacts | Resources, Tools, Prompts |
| **Discovery** | Agent Cards | Server capabilities |
| **State Management** | Task lifecycle | Stateless |
| **Best For** | Agent coordination | Tool access |
| **Introduced** | Google, April 2025 | Anthropic, Nov 2024 |

### Integration Strategy

Use **both protocols** in SPEK v2:
- **MCP**: For tool access (filesystem, memory, GitHub, playwright, etc.)
- **A2A**: For agent coordination (Queen-Princess-Drone communication)

---

## 7. Integration Recommendations

### Architecture Overview for SPEK v2

```
SPEK v2 Enhanced Architecture with DSPy + A2A + MCP

+---------------------------------------------------------------+
|                      QUEEN AGENT (DSPy)                       |
|  - MIPROv2 optimized delegation prompts                       |
|  - A2A client for princess coordination                       |
|  - Context DNA persistence                                    |
+---------------------------------------------------------------+
         |
         | A2A Protocol (Task delegation)
         |
    +----+----+----+----+
    |    |    |    |    |
    v    v    v    v    v
+------+ +------+ +------+ +------+ +------+
|PRIN1 | |PRIN2 | |PRIN3 | |PRIN4 | |...   |  <- Princess Agents (DSPy)
|GEPA  | |GEPA  | |GEPA  | |GEPA  | |      |     - GEPA optimized orchestration
|Opt   | |Opt   | |Opt   | |Opt   | |      |     - A2A task management
+------+ +------+ +------+ +------+ +------+     - MCP tool access
    |        |        |        |        |
    | A2A    | A2A    | A2A    | A2A    | A2A
    |        |        |        |        |
    v        v        v        v        v
+------+ +------+ +------+ +------+ +------+
|DRONE1| |DRONE2| |DRONE3| |DRONE4| |...   |  <- Drone Agents (DSPy)
|MIPROv2| |MIPROv2| |MIPROv2| |MIPROv2| |      |     - MIPROv2 optimized execution
+------+ +------+ +------+ +------+ +------+     - MCP tool access
    |        |        |        |        |         - Quality metrics (0.0-1.0)
    |        |        |        |        |
    +--------+--------+--------+--------+
                    |
                    v
          +-------------------+
          |   MCP Servers     |
          |-------------------|
          | - Filesystem      |
          | - Memory (Graph)  |
          | - GitHub          |
          | - Playwright      |
          | - Eva (Quality)   |
          | - Sequential      |
          +-------------------+
```

### Component Mapping

#### 1. Queen Agent (1 instance)

**Framework**: DSPy with MIPROv2 optimizer
**Protocol**: A2A client
**Responsibilities**: Task decomposition, princess selection, validation
**Model**: Claude Sonnet 4 + Sequential Thinking
**MCP Servers**: memory, sequential-thinking, github-project-manager

```python
# Queen Agent Implementation
class QueenAgent(dspy.Module):
    def __init__(self, a2a_server_url: str):
        super().__init__()

        # DSPy modules
        self.decompose = dspy.ChainOfThought(
            "task_description, constraints -> subtasks: List[str], dependencies: Dict"
        )
        self.select_agents = dspy.ChainOfThought(
            "subtasks, available_princesses -> assignments: List[Dict]"
        )
        self.validate = dspy.ChainOfThought(
            "assignments, constraints -> validation: bool, adjustments: List[str]"
        )

        # A2A integration
        self.a2a = A2AClient(a2a_server_url, "queen-agent")

        # Context DNA store
        self.context_store = ContextDNAStore()

    async def forward(self, task_description: str, constraints: Dict):
        # Generate session ID
        session_id = f"queen-{uuid.uuid4()}"

        # Decompose task
        decomposition = self.decompose(
            task_description=task_description,
            constraints=constraints
        )

        # Discover princess agents
        princesses = await self.a2a.discover_agents()
        princess_list = [
            p for p in princesses
            if "princess" in p.agent_id.lower()
        ]

        # Select and assign
        assignments = self.select_agents(
            subtasks=decomposition.subtasks,
            available_princesses=princess_list
        )

        # Validate plan
        validation = self.validate(
            assignments=assignments.assignments,
            constraints=constraints
        )

        # Save context DNA
        context = {
            "session_id": session_id,
            "agent_id": "queen-agent",
            "timestamp": datetime.now().isoformat(),
            "context_type": "task_execution",
            "context_data": {
                "domain": "coordination",
                "task": "delegate_task",
                "inputs": {
                    "task_description": task_description,
                    "constraints": constraints
                },
                "state": {
                    "progress": 1.0,
                    "completed_steps": ["decompose", "select", "validate"],
                    "pending_steps": []
                },
                "artifacts": [],
                "memory_keys": [f"queen/{session_id}/plan"]
            },
            "metadata": {
                "model": "claude-sonnet-4",
                "tokens_used": 5000,
                "cost_usd": 0.015,
                "quality_score": 0.95
            }
        }
        self.context_store.save(context)

        return validation

# Optimize Queen with MIPROv2
queen_optimizer = MIPROv2(
    metric=queen_delegation_metric,
    num_candidates=10,
    num_trials=30
)

optimized_queen = queen_optimizer.compile(
    student=QueenAgent("http://localhost:8000"),
    trainset=queen_trainset,
    max_bootstrapped_demos=4
)
```

#### 2. Princess Agents (4 instances - one per domain)

**Domains**: Development, Quality, Research, Security
**Framework**: DSPy with GEPA optimizer
**Protocol**: A2A server + client
**Model**: Gemini Flash + Sequential Thinking (cost-effective)
**MCP Servers**: memory, sequential-thinking, github

```python
# Princess Agent Implementation
class PrincessAgent(dspy.Module):
    def __init__(
        self,
        a2a_server_url: str,
        princess_id: str,
        domain: str
    ):
        super().__init__()

        # DSPy modules
        self.plan_execution = dspy.ChainOfThought(
            "subtasks, dependencies -> execution_plan: List[Step]"
        )
        self.allocate_drones = dspy.ChainOfThought(
            "execution_plan, available_drones -> allocation: Dict"
        )
        self.monitor = dspy.ChainOfThought(
            "progress_updates -> status: str, interventions: List[str]"
        )

        # A2A integration
        self.a2a = A2AClient(a2a_server_url, princess_id)
        self.domain = domain

        # Context DNA
        self.context_store = ContextDNAStore()

    async def forward(self, subtasks: List[str], dependencies: Dict):
        session_id = f"princess-{self.domain}-{uuid.uuid4()}"

        # Plan execution
        plan = self.plan_execution(
            subtasks=subtasks,
            dependencies=dependencies
        )

        # Discover drones
        agents = await self.a2a.discover_agents()
        drones = [
            a for a in agents
            if "drone" in a.agent_id.lower()
            and self.domain in a.supported_domains
        ]

        # Allocate drones
        allocation = self.allocate_drones(
            execution_plan=plan.execution_plan,
            available_drones=drones
        )

        # Delegate via A2A
        task_ids = []
        for step in plan.execution_plan:
            drone_id = allocation.allocation[step["id"]]

            task_id = await self.a2a.assign_task(
                to_agent=drone_id,
                task_type=step["type"],
                parameters=step["parameters"],
                priority=step.get("priority", "medium")
            )
            task_ids.append(task_id)

        # Monitor execution
        result = await self.monitor_execution(task_ids)

        # Save context
        context = {
            "session_id": session_id,
            "agent_id": f"princess-{self.domain}",
            "timestamp": datetime.now().isoformat(),
            "context_type": "task_execution",
            "context_data": {
                "domain": self.domain,
                "task": "orchestrate_subtasks",
                "inputs": {"subtasks": subtasks, "dependencies": dependencies},
                "state": {
                    "progress": 1.0,
                    "completed_steps": ["plan", "allocate", "delegate", "monitor"],
                    "pending_steps": []
                },
                "artifacts": result["artifacts"],
                "memory_keys": [f"princess/{self.domain}/{session_id}"]
            },
            "metadata": {
                "model": "gemini-2.5-flash",
                "tokens_used": 8000,
                "cost_usd": 0.002,
                "quality_score": result["quality_score"],
                "parent_session_id": None,
                "child_session_ids": task_ids
            }
        }
        self.context_store.save(context)

        return result

# Optimize Princess with GEPA
princess_optimizer = GEPA(
    metric=princess_orchestration_metric,
    breadth=6,
    depth=3
)

optimized_princess_dev = princess_optimizer.compile(
    student=PrincessAgent("http://localhost:8000", "princess-dev", "development"),
    trainset=princess_dev_trainset,
    max_iters=25
)
```

#### 3. Drone Agents (13 specialized + 4 swarm = 17 total)

**Categories**:
- Core: coder, reviewer, tester, planner, researcher
- Swarm: hierarchical-coordinator, mesh-coordinator, task-orchestrator, swarm-memory-manager
- Specialized: backend-dev, frontend-dev, security-manager, etc.

**Framework**: DSPy with MIPROv2 optimizer
**Protocol**: A2A server (receive tasks)
**Model**: Varies by agent type (GPT-5, Opus, Gemini Pro)
**MCP Servers**: Varies by agent (playwright, github, eva, etc.)

```python
# Drone Agent Implementation
class DroneAgent(dspy.Module):
    def __init__(
        self,
        a2a_server_url: str,
        drone_id: str,
        specialization: str,
        mcp_servers: List[str]
    ):
        super().__init__()

        # DSPy module for task execution
        self.execute = dspy.ChainOfThought(
            "task_type, parameters -> implementation: str, tests: str, artifacts: List"
        )

        # A2A integration
        self.a2a = A2AClient(a2a_server_url, drone_id)
        self.specialization = specialization
        self.mcp_servers = mcp_servers

        # Context DNA
        self.context_store = ContextDNAStore()

    async def forward(self, task_type: str, parameters: Dict):
        session_id = f"drone-{self.specialization}-{uuid.uuid4()}"

        # Execute task
        result = self.execute(
            task_type=task_type,
            parameters=parameters
        )

        # Validate quality
        quality_score = self.validate_quality(result)

        # Save context
        context = {
            "session_id": session_id,
            "agent_id": f"drone-{self.specialization}",
            "timestamp": datetime.now().isoformat(),
            "context_type": "task_execution",
            "context_data": {
                "domain": self.specialization,
                "task": task_type,
                "inputs": parameters,
                "state": {
                    "progress": 1.0,
                    "completed_steps": ["execute", "validate"],
                    "pending_steps": []
                },
                "artifacts": result.artifacts,
                "memory_keys": [f"drone/{self.specialization}/{session_id}"]
            },
            "metadata": {
                "model": self.get_model_for_specialization(),
                "tokens_used": 12000,
                "cost_usd": self.calculate_cost(),
                "quality_score": quality_score
            }
        }
        self.context_store.save(context)

        return result

# Optimize Drone with MIPROv2
coder_optimizer = MIPROv2(
    metric=drone_execution_metric,
    num_candidates=10,
    num_trials=40
)

optimized_coder_drone = coder_optimizer.compile(
    student=DroneAgent(
        "http://localhost:8000",
        "drone-coder",
        "coding",
        ["github", "eva"]
    ),
    trainset=coder_trainset,
    max_bootstrapped_demos=4
)
```

### Implementation Phases

#### Phase 1: Foundation (Week 1-2)

1. **Install DSPy and Agenspy**
   ```bash
   pip install dspy-ai>=2.5.0
   git clone https://github.com/SuperagenticAI/Agenspy
   cd Agenspy && pip install -e .
   ```

2. **Setup A2A Server**
   - Deploy FastAPI server with A2A endpoints
   - Configure at http://localhost:8000
   - Test registration and discovery

3. **Implement Context DNA Storage**
   - Create `.claude/.context/` directory structure
   - Implement ContextDNAStore class
   - Test persistence and restoration

4. **Define Base Metrics**
   - Implement queen_delegation_metric (0.0-1.0)
   - Implement princess_orchestration_metric (0.0-1.0)
   - Implement drone_execution_metric (0.0-1.0)

#### Phase 2: Agent Development (Week 3-4)

1. **Develop Queen Agent**
   - Implement QueenAgent DSPy module
   - Integrate A2A client
   - Create training dataset (50+ examples)
   - Test basic delegation

2. **Develop Princess Agents** (4 instances)
   - Development Princess
   - Quality Princess
   - Research Princess
   - Security Princess

   For each:
   - Implement PrincessAgent DSPy module
   - Register with A2A server
   - Create domain-specific training data
   - Test orchestration

3. **Develop Drone Agents** (start with 5 core)
   - Coder Drone
   - Reviewer Drone
   - Tester Drone
   - Planner Drone
   - Researcher Drone

   For each:
   - Implement DroneAgent DSPy module
   - Configure MCP server access
   - Create specialization-specific training data
   - Test execution

#### Phase 3: Optimization (Week 5-6)

1. **Optimize Queen with MIPROv2**
   - Prepare 200+ training examples
   - Run MIPROv2 with num_trials=30
   - Validate improvement (target: 2x baseline)
   - Save optimized prompts

2. **Optimize Princesses with GEPA**
   - Prepare 150+ training examples per domain
   - Run GEPA with breadth=6, depth=3
   - Validate orchestration quality
   - Save optimized programs

3. **Optimize Drones with MIPROv2**
   - Prepare 100+ training examples per specialization
   - Run MIPROv2 with num_trials=40
   - Validate execution quality
   - Save optimized prompts

#### Phase 4: Integration (Week 7-8)

1. **Connect to MCP Servers**
   - Configure MCP client connections
   - Test tool access (filesystem, memory, github, etc.)
   - Validate security boundaries

2. **Implement Full Workflow**
   - Test complete Queen -> Princess -> Drone flow
   - Validate A2A communication
   - Verify Context DNA persistence
   - Measure quality scores

3. **Performance Tuning**
   - Optimize concurrency (max 25 agents per Claude Flow docs)
   - Implement caching (prompt caching for GPT-5 Codex)
   - Monitor token usage and costs
   - Tune quality thresholds

#### Phase 5: Validation & Deployment (Week 9-10)

1. **Quality Gate Validation**
   - NASA POT10 compliance: >=92%
   - FSM compliance: >=90%
   - Theater detection: <60
   - Test coverage: >=80%

2. **End-to-End Testing**
   - Run complete 3-loop workflow
   - Test all 22 agents
   - Validate quality convergence
   - Measure cost per task

3. **Production Deployment**
   - Deploy A2A server to production
   - Configure agent auto-scaling
   - Setup monitoring and alerts
   - Create runbooks

### Configuration Files

#### `dspy-config.yaml`

```yaml
# DSPy Configuration for SPEK v2
language_models:
  queen:
    model: "claude-sonnet-4"
    max_tokens: 8000
    temperature: 0.7
    mcp_servers:
      - memory
      - sequential-thinking
      - github-project-manager

  princess:
    model: "gemini-2.5-flash"
    max_tokens: 4000
    temperature: 0.6
    mcp_servers:
      - memory
      - sequential-thinking
      - github

  drone_coder:
    model: "gpt-5-codex"
    max_tokens: 8000
    temperature: 0.5
    mcp_servers:
      - github
      - eva

  drone_reviewer:
    model: "claude-opus-4.1"
    max_tokens: 6000
    temperature: 0.3
    mcp_servers:
      - github
      - eva

optimization:
  queen:
    optimizer: "miprov2"
    num_trials: 30
    num_candidates: 10
    max_bootstrapped_demos: 4

  princess:
    optimizer: "gepa"
    breadth: 6
    depth: 3
    max_iters: 25

  drone:
    optimizer: "miprov2"
    num_trials: 40
    num_candidates: 12
    max_bootstrapped_demos: 4

quality_thresholds:
  queen_delegation: 0.80
  princess_orchestration: 0.85
  drone_execution: 0.90
  nasa_compliance: 0.92
  fsm_compliance: 0.90
  theater_max: 0.60
  test_coverage: 0.80
```

#### `a2a-config.yaml`

```yaml
# A2A Configuration for SPEK v2
server:
  url: "http://localhost:8000"
  protocol_version: "1.0"

agents:
  queen:
    agent_id: "queen-agent"
    name: "Queen Agent"
    version: "1.0.0"
    capabilities:
      - task_decomposition
      - agent_selection
      - validation
    endpoint: "http://localhost:9000/queen"

  princess_dev:
    agent_id: "princess-development"
    name: "Development Princess"
    version: "1.0.0"
    domain: "development"
    capabilities:
      - task_orchestration
      - resource_allocation
    endpoint: "http://localhost:9001/princess"

  princess_quality:
    agent_id: "princess-quality"
    name: "Quality Princess"
    version: "1.0.0"
    domain: "quality"
    capabilities:
      - quality_validation
      - testing_coordination
    endpoint: "http://localhost:9002/princess"

  # ... other agents

task_lifecycle:
  timeout_seconds: 3600
  retry_attempts: 3
  progress_update_interval: 30

message_routing:
  max_queue_size: 1000
  delivery_timeout: 10
```

---

## 8. Implementation Roadmap

### Timeline: 10 Weeks

#### Week 1-2: Foundation Setup
- [ ] Install DSPy 2.5+ and Agenspy
- [ ] Deploy A2A server (FastAPI)
- [ ] Implement Context DNA storage
- [ ] Define quality metrics (0.0-1.0)
- [ ] Create training data templates

#### Week 3-4: Agent Development
- [ ] Develop Queen Agent (DSPy module)
- [ ] Develop 4 Princess Agents (Development, Quality, Research, Security)
- [ ] Develop 5 Core Drone Agents (Coder, Reviewer, Tester, Planner, Researcher)
- [ ] Integrate A2A communication
- [ ] Test basic workflows

#### Week 5-6: Optimization
- [ ] Collect 200+ training examples for Queen
- [ ] Optimize Queen with MIPROv2 (30 trials)
- [ ] Collect 150+ training examples per Princess
- [ ] Optimize Princesses with GEPA (breadth=6, depth=3)
- [ ] Collect 100+ training examples per Drone
- [ ] Optimize Drones with MIPROv2 (40 trials)

#### Week 7-8: Integration
- [ ] Connect all agents to MCP servers
- [ ] Implement full Queen->Princess->Drone flow
- [ ] Test Context DNA persistence and restoration
- [ ] Validate quality scores across hierarchy
- [ ] Performance tuning (concurrency, caching)

#### Week 9-10: Validation & Deployment
- [ ] Run quality gate validation (NASA, FSM, Theater, Tests)
- [ ] Execute end-to-end 3-loop workflows
- [ ] Measure cost per task and optimize
- [ ] Deploy to production environment
- [ ] Create monitoring dashboards

### Success Metrics

- **Queen Agent**: Delegation accuracy >=80%, load balancing variance <=20%
- **Princess Agents**: Orchestration quality >=85%, parallelism efficiency >=70%
- **Drone Agents**: Execution quality >=90%, NASA compliance >=92%, FSM >=90%
- **System-Wide**: Theater score <60, test coverage >=80%, cost per task <=$0.60
- **Performance**: Agent response time <5s, task completion within SLA

---

## 9. Code Examples

### Complete Queen-Princess-Drone Example

```python
# complete_hierarchy_example.py
import dspy
import asyncio
import uuid
from typing import List, Dict, Any
from datetime import datetime

# --- METRICS ---

def queen_delegation_metric(example, pred, trace=None):
    """Queen agent delegation quality metric."""
    tasks_assigned = len(pred.assignments)
    tasks_required = len(example.required_tasks)
    completeness = tasks_assigned / tasks_required if tasks_required > 0 else 0

    # Check constraint satisfaction
    constraint_score = float(pred.validation == "valid")

    score = (completeness * 0.6) + (constraint_score * 0.4)

    if trace is None:
        return max(0.0, min(1.0, score))
    else:
        return score >= 0.8

def princess_orchestration_metric(example, pred, trace=None):
    """Princess agent orchestration quality metric."""
    has_plan = hasattr(pred, 'execution_plan') and len(pred.execution_plan) > 0
    has_allocation = hasattr(pred, 'allocation') and len(pred.allocation) > 0

    score = (float(has_plan) * 0.5) + (float(has_allocation) * 0.5)

    if trace is None:
        return score
    else:
        return has_plan and has_allocation

def drone_execution_metric(example, pred, trace=None):
    """Drone agent execution quality metric."""
    is_complete = hasattr(pred, 'result') and pred.result is not None

    # Check quality (simplified)
    quality_score = 0.9 if is_complete else 0.0

    if trace is None:
        return quality_score
    else:
        return is_complete

# --- CONTEXT DNA ---

class ContextDNAStore:
    """Simple context DNA storage."""

    def __init__(self, base_path: str = ".claude/.context"):
        from pathlib import Path
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, context: Dict[str, Any]):
        """Save context DNA."""
        import json
        agent_id = context["agent_id"]
        session_id = context["session_id"]

        agent_dir = self.base_path / agent_id
        agent_dir.mkdir(exist_ok=True)

        filename = f"{session_id}.json"
        filepath = agent_dir / filename

        with open(filepath, 'w') as f:
            json.dump(context, f, indent=2)

    def load(self, session_id: str, agent_id: str) -> Dict[str, Any]:
        """Load context DNA."""
        import json
        filepath = self.base_path / agent_id / f"{session_id}.json"

        with open(filepath, 'r') as f:
            return json.load(f)

# --- AGENTS ---

class QueenAgent(dspy.Module):
    """Top-level coordinator."""

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(
            "task_description -> subtasks: List[str]"
        )
        self.assign = dspy.ChainOfThought(
            "subtasks, available_agents -> assignments: List[Dict]"
        )
        self.validate = dspy.ChainOfThought(
            "assignments -> validation: str"
        )
        self.context_store = ContextDNAStore()

    def forward(self, task_description: str, available_agents: List[str]):
        session_id = f"queen-{uuid.uuid4()}"

        # Decompose
        decomposition = self.decompose(task_description=task_description)

        # Assign
        assignment = self.assign(
            subtasks=decomposition.subtasks,
            available_agents=available_agents
        )

        # Validate
        validation = self.validate(assignments=assignment.assignments)

        # Save context
        context = {
            "session_id": session_id,
            "agent_id": "queen-agent",
            "timestamp": datetime.now().isoformat(),
            "context_type": "task_execution",
            "context_data": {
                "domain": "coordination",
                "task": "delegate_task",
                "inputs": {"task_description": task_description},
                "state": {
                    "progress": 1.0,
                    "completed_steps": ["decompose", "assign", "validate"],
                    "pending_steps": []
                },
                "artifacts": [],
                "memory_keys": []
            },
            "metadata": {
                "model": "claude-sonnet-4",
                "tokens_used": 5000,
                "cost_usd": 0.015,
                "quality_score": 0.95
            }
        }
        self.context_store.save(context)

        return dspy.Prediction(
            subtasks=decomposition.subtasks,
            assignments=assignment.assignments,
            validation=validation.validation
        )

class PrincessAgent(dspy.Module):
    """Domain orchestrator."""

    def __init__(self, domain: str):
        super().__init__()
        self.domain = domain
        self.plan = dspy.ChainOfThought(
            "subtasks -> execution_plan: List[Dict]"
        )
        self.allocate = dspy.ChainOfThought(
            "execution_plan, available_drones -> allocation: Dict"
        )
        self.context_store = ContextDNAStore()

    def forward(self, subtasks: List[str], available_drones: List[str]):
        session_id = f"princess-{self.domain}-{uuid.uuid4()}"

        # Plan
        planning = self.plan(subtasks=subtasks)

        # Allocate
        allocation = self.allocate(
            execution_plan=planning.execution_plan,
            available_drones=available_drones
        )

        # Save context
        context = {
            "session_id": session_id,
            "agent_id": f"princess-{self.domain}",
            "timestamp": datetime.now().isoformat(),
            "context_type": "task_execution",
            "context_data": {
                "domain": self.domain,
                "task": "orchestrate_subtasks",
                "inputs": {"subtasks": subtasks},
                "state": {
                    "progress": 1.0,
                    "completed_steps": ["plan", "allocate"],
                    "pending_steps": []
                },
                "artifacts": [],
                "memory_keys": []
            },
            "metadata": {
                "model": "gemini-2.5-flash",
                "tokens_used": 3000,
                "cost_usd": 0.001,
                "quality_score": 0.88
            }
        }
        self.context_store.save(context)

        return dspy.Prediction(
            execution_plan=planning.execution_plan,
            allocation=allocation.allocation
        )

class DroneAgent(dspy.Module):
    """Specialized executor."""

    def __init__(self, specialization: str):
        super().__init__()
        self.specialization = specialization
        self.execute = dspy.ChainOfThought(
            "task_type, parameters -> result: str"
        )
        self.context_store = ContextDNAStore()

    def forward(self, task_type: str, parameters: Dict):
        session_id = f"drone-{self.specialization}-{uuid.uuid4()}"

        # Execute
        execution = self.execute(task_type=task_type, parameters=parameters)

        # Save context
        context = {
            "session_id": session_id,
            "agent_id": f"drone-{self.specialization}",
            "timestamp": datetime.now().isoformat(),
            "context_type": "task_execution",
            "context_data": {
                "domain": self.specialization,
                "task": task_type,
                "inputs": parameters,
                "state": {
                    "progress": 1.0,
                    "completed_steps": ["execute"],
                    "pending_steps": []
                },
                "artifacts": [],
                "memory_keys": []
            },
            "metadata": {
                "model": "gpt-5-codex",
                "tokens_used": 8000,
                "cost_usd": 0.024,
                "quality_score": 0.92
            }
        }
        self.context_store.save(context)

        return dspy.Prediction(result=execution.result)

# --- OPTIMIZATION ---

async def optimize_hierarchy():
    """Optimize complete hierarchy with DSPy."""

    # Configure DSPy
    lm = dspy.LM('openai/gpt-4o-mini')
    dspy.configure(lm=lm)

    # --- QUEEN OPTIMIZATION ---
    print("Optimizing Queen Agent with MIPROv2...")

    queen_trainset = [
        dspy.Example(
            task_description="Build authentication system",
            available_agents=["princess-dev", "princess-security"],
            required_tasks=["implement auth", "security audit"]
        ).with_inputs("task_description", "available_agents"),
        # ... more examples
    ]

    queen = QueenAgent()
    queen_optimizer = dspy.teleprompt.MIPROv2(
        metric=queen_delegation_metric,
        num_candidates=5,
        num_trials=10,
        verbose=True
    )

    optimized_queen = queen_optimizer.compile(
        student=queen,
        trainset=queen_trainset,
        max_bootstrapped_demos=3
    )

    # --- PRINCESS OPTIMIZATION ---
    print("\nOptimizing Princess Agent with GEPA...")

    princess_trainset = [
        dspy.Example(
            subtasks=["implement auth", "write tests"],
            available_drones=["drone-coder", "drone-tester"]
        ).with_inputs("subtasks", "available_drones"),
        # ... more examples
    ]

    princess_dev = PrincessAgent("development")
    princess_optimizer = dspy.teleprompt.GEPA(
        metric=princess_orchestration_metric,
        breadth=4,
        depth=2,
        verbose=True
    )

    optimized_princess = princess_optimizer.compile(
        student=princess_dev,
        trainset=princess_trainset,
        max_iters=10
    )

    # --- DRONE OPTIMIZATION ---
    print("\nOptimizing Drone Agent with MIPROv2...")

    drone_trainset = [
        dspy.Example(
            task_type="implement_feature",
            parameters={"feature": "login form"}
        ).with_inputs("task_type", "parameters"),
        # ... more examples
    ]

    drone_coder = DroneAgent("coding")
    drone_optimizer = dspy.teleprompt.MIPROv2(
        metric=drone_execution_metric,
        num_candidates=5,
        num_trials=15,
        verbose=True
    )

    optimized_drone = drone_optimizer.compile(
        student=drone_coder,
        trainset=drone_trainset,
        max_bootstrapped_demos=3
    )

    print("\n✅ Optimization complete!")

    return {
        "queen": optimized_queen,
        "princess_dev": optimized_princess,
        "drone_coder": optimized_drone
    }

# --- MAIN ---

if __name__ == "__main__":
    optimized_agents = asyncio.run(optimize_hierarchy())

    # Test optimized queen
    result = optimized_agents["queen"](
        task_description="Build user authentication system with OAuth2",
        available_agents=["princess-dev", "princess-security", "princess-quality"]
    )

    print(f"\n📋 Queen Delegation Result:")
    print(f"  Subtasks: {result.subtasks}")
    print(f"  Assignments: {result.assignments}")
    print(f"  Validation: {result.validation}")
```

---

## 10. References

### Official Documentation

1. **Agenspy**
   - GitHub: https://github.com/SuperagenticAI/Agenspy
   - Medium Article: https://medium.com/superagentic-ai/introducing-agenspy-agentic-dspy-a-protocol-first-ai-agent-framework-52eac7ae153d

2. **DSPy**
   - Website: https://dspy.ai/
   - GitHub: https://github.com/stanfordnlp/dspy
   - MIPROv2 Docs: https://dspy.ai/deep-dive/optimizers/miprov2/
   - GEPA Docs: https://dspy.ai/api/optimizers/GEPA/
   - Metrics: https://dspy.ai/learn/evaluation/metrics/

3. **Model Context Protocol (MCP)**
   - Specification: https://modelcontextprotocol.io/specification/2025-03-26
   - DSPy Tutorial: https://dspy.ai/tutorials/mcp/

4. **Agent2Agent (A2A) Protocol**
   - Official Site: https://a2aprotocol.ai/
   - Google Announcement: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
   - Microsoft Support: https://www.microsoft.com/en-us/microsoft-cloud/blog/2025/05/07/empowering-multi-agent-apps-with-the-open-agent2agent-a2a-protocol/

### Research Papers & Articles

1. **DSPy MIPROv2**
   - "Optimizing Prompts for Language Model Pipelines: DSPy MIPROv2" (Medium)
   - "Grokking MIPROv2 - the new optimizer from DSPy" (Langtrace)

2. **GEPA Optimizer**
   - "Building and Optimizing Multi-Agent RAG Systems with DSPy and GEPA" (Medium)
   - "Crafting Multi-Agent RAG Systems with DSPy and GEPA Optimization" (Medium)

3. **A2A Protocol**
   - "Designing Collaborative Multi-Agent Systems with the A2A Protocol" (O'Reilly)
   - "Orchestrating heterogeneous and distributed multi-agent systems using A2A" (Fractal Analytics)

### Tutorials & Examples

1. **DSPy Tutorials**
   - Building RAG as Agent: https://dspy.ai/tutorials/agents/
   - Customer Service Agent: https://dspy.ai/tutorials/customer_service_agent/
   - GEPA Full Program: https://dspy.ai/tutorials/gepa_ai_program/

2. **Agentic DevOps Demo**
   - GitHub: https://github.com/SuperagenticAI/Agentic-DevOps

3. **Context Engineering**
   - "Context Engineering — A Comprehensive Hands-On Tutorial with DSPy" (Towards Data Science)

### Community Resources

1. **GitHub Discussions**
   - DSPy Enhancement Proposal: https://github.com/stanfordnlp/dspy/issues/8273
   - MCP Support: https://github.com/stanfordnlp/dspy/issues/7799

2. **Medium Publications**
   - Superagentic AI: https://medium.com/superagentic-ai
   - Agent Native: https://agentissue.medium.com/

---

## Version & Run Log

| Version | Timestamp | Agent/Model | Change Summary | Artifacts | Status | Notes | Cost | Hash |
|--------:|-----------|-------------|----------------|-----------|--------|-------|------|------|
| 1.0.0   | 2025-10-08T15:30:00-04:00 | Research Agent @ Sonnet 4 | Complete Gap 4 research | dspy-agent2agent-research-v1.md | OK | Comprehensive research with 10 sections, code examples, integration guide | 0.15 | a7c4f21 |

### Receipt
- status: OK
- reason: Research complete with actionable recommendations
- run_id: research-gap4-dspy-a2a-v1
- inputs: ["RESEARCH-GAPS-v1.md", "PLAN-v1.md", "SPEC-v1.md"]
- tools_used: ["WebSearch", "Read", "Write", "analysis"]
- versions: {"model": "claude-sonnet-4", "dspy": "2.5+", "agenspy": "2025-latest"}

---

**END OF DOCUMENT**
