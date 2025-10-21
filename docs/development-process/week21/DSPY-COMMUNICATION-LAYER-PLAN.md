# DSPy Communication & MCP Tool Layer - Implementation Plan

**Date**: 2025-10-10
**Week**: 21 Day 3
**Status**: READY TO IMPLEMENT
**Estimated Duration**: 12-16 hours (2-3 days)

---

## ✅ Corrected Understanding

### What DSPy Actually Does

DSPy is **NOT** for training agent intelligence. It's a **prompt manipulation middleware** that:

1. **Optimizes message structure** at agent communication boundaries
   - Queen→Princess: High-level task → Structured subtasks
   - Princess→Drone: Workflow phase → Specific instructions
   - Drone↔Drone: Coordination messages
   - Princess↔Princess: Cross-hive collaboration

2. **Validates MCP tool calls** to ensure correct formatting
   - Parameter validation before API calls
   - Schema enforcement for tool signatures
   - Error prevention and automatic correction

### What We Keep vs What Changes

**✅ KEEP (Agent System Instructions)**:
- All 22 agent instruction templates we just built
- AgentInstructionBase framework
- System instructions define HOW agents think internally
- **These are correct and complete**

**🆕 ADD (DSPy Communication Layer)**:
- Message optimization BETWEEN agents
- MCP tool call validation
- Communication middleware
- **This is what we're building now**

---

## 📊 Current State Analysis

### Communication Flow (Discovered from Code)

**1. Current Message Flow**:
```python
# AgentBase.py:333 - delegate_task()
async def delegate_task(self, target_agent_id: str, task: Task) -> Result:
    result_data = await self.protocol.send_task(
        sender_id=self.metadata.agent_id,
        receiver_id=target_agent_id,
        task=task.__dict__  # ← Current: Direct Task serialization
    )
    return Result(**result_data)
```

**2. Task Structure** (AgentBase.py:68-77):
```python
@dataclass
class Task:
    id: str
    type: str
    description: str
    payload: Dict[str, Any]  # ← Unstructured - DSPy will optimize this
    priority: int
    timeout: Optional[int] = 300000
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**3. Communication Paths Identified**:

| Source | Target | Method | Location | Optimization Need |
|--------|--------|--------|----------|-------------------|
| Queen | Princess-Dev | `delegate_task()` | QueenAgent.py:328 | HIGH - Task decomposition |
| Queen | Princess-Quality | `delegate_task()` | QueenAgent.py:328 | HIGH - Quality gate definition |
| Queen | Princess-Coordination | `delegate_task()` | QueenAgent.py:328 | MEDIUM - Planning clarity |
| Princess | Drone (any) | `delegate_task()` | PrincessDevAgent.py:181 | HIGH - Instruction specificity |
| Drone | Drone | `delegate_task()` | AgentBase.py:333 | MEDIUM - Coordination protocol |

**4. MCP Tool Usage** (From research docs):
- Currently: **NO MCP tools integrated yet**
- MCP server spec exists: claude-flow with 87 tools
- Priority tools: `swarm_init`, `agent_spawn`, `task_orchestrate`, `repo_analyze`

---

## 🎯 Implementation Plan

### Phase 1: Communication Schema Definition (3-4 hours)

**Goal**: Document and formalize current communication patterns

#### 1.1 Analyze Existing Communication (1 hour)

**Files to Read**:
- ✅ AgentBase.py:333 - `delegate_task()` method
- ✅ QueenAgent.py:311-335 - Queen delegation logic
- ✅ PrincessDevAgent.py:159-194 - Princess delegation
- ✅ EnhancedLightweightProtocol.py:124-176 - Protocol layer
- ✅ datasets/week6/queen_training_dataset.json - Existing examples

**Deliverable**: Current state document with:
- Message flow diagrams
- Task payload examples
- Communication bottlenecks

#### 1.2 Create Communication Schemas (2-3 hours)

**Schema Files to Create**:

```
src/communication/schemas/
  ├── __init__.py
  ├── base_schema.py              # Base Task schema validation
  ├── queen_to_princess.py        # Queen→Princess message format
  ├── princess_to_drone.py        # Princess→Drone message format
  ├── drone_coordination.py       # Drone↔Drone protocol
  └── cross_princess.py           # Princess↔Princess collaboration
```

**Example Schema** (queen_to_princess.py):
```python
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class QueenToPrincessMessage:
    """Structured message format for Queen→Princess communication."""

    # Input (from Queen)
    objective: str                    # High-level goal
    requirements: List[str]           # Explicit requirements
    constraints: Dict[str, Any]       # Time, budget, quality constraints
    context: Dict[str, Any]           # Additional context

    # Expected Output (to Princess)
    workflow_id: str                  # Unique workflow identifier
    subtasks: List[Dict[str, Any]]    # Structured subtask list
    dependencies: Dict[str, List[str]] # Task dependency graph
    quality_gates: List[str]          # Required quality checks
    estimated_duration_min: int       # Total estimated time

    def validate(self) -> List[str]:
        """Validate message structure."""
        errors = []
        if not self.objective:
            errors.append("Missing objective")
        if not self.subtasks:
            errors.append("No subtasks defined")
        if self.estimated_duration_min > 480:  # 8 hours max
            errors.append("Workflow too long (>8 hours)")
        return errors
```

**Deliverables**:
- 5 schema definition files
- Schema validation functions
- Example messages for each schema

---

### Phase 2: DSPy Module Implementation (5-6 hours)

**Goal**: Create DSPy modules that optimize communication messages

#### 2.1 Communication Optimizer Modules (3-4 hours)

**Files to Create**:

```
src/communication/
  ├── __init__.py
  ├── dspy_modules.py              # All communication optimizer modules
  ├── optimizer_middleware.py      # Middleware integration layer
  └── communication_metrics.py     # Quality metrics for optimization
```

**Core Module** (dspy_modules.py):

```python
import dspy
from typing import Dict, Any, List
from src.communication.schemas.queen_to_princess import QueenToPrincessMessage

class QueenToPrincessOptimizer(dspy.Module):
    """
    Optimizes Queen→Princess messages for:
    - Clear task decomposition
    - Realistic time estimates
    - Proper dependency ordering
    - Complete quality gates
    """

    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought("task_description, objective -> subtasks")

    def forward(self, task_description: str, objective: str) -> Dict[str, Any]:
        """
        Transform high-level Queen task into structured Princess workflow.

        Args:
            task_description: Detailed task description from Queen
            objective: Overall objective and success criteria

        Returns:
            Optimized workflow with subtasks, dependencies, quality gates
        """
        # DSPy will learn optimal decomposition from training examples
        prediction = self.decompose(
            task_description=task_description,
            objective=objective
        )

        # Parse prediction into structured format
        workflow = self._parse_prediction(prediction)

        # Validate against schema
        message = QueenToPrincessMessage(**workflow)
        errors = message.validate()

        if errors:
            raise ValueError(f"Invalid workflow: {errors}")

        return workflow

    def _parse_prediction(self, prediction) -> Dict[str, Any]:
        """Parse DSPy prediction into workflow structure."""
        # Implementation here - convert prediction text to structured dict
        ...
```

**All Modules**:
1. `QueenToPrincessOptimizer` - Task decomposition
2. `PrincessToDroneOptimizer` - Instruction clarity
3. `DroneCoordinationOptimizer` - Peer coordination
4. `CrossPrincessOptimizer` - Cross-hive collaboration

**Deliverables**:
- 4 DSPy optimizer modules
- Validation logic for each
- Unit tests for module initialization

#### 2.2 MCP Tool Validator Modules (2 hours)

**Files to Create**:

```
src/mcp_layer/
  ├── __init__.py
  ├── dspy_validators.py          # MCP tool validation modules
  ├── tool_schemas.py             # MCP tool parameter schemas
  └── mcp_metrics.py              # Validation quality metrics
```

**Core Validator** (dspy_validators.py):

```python
import dspy
from typing import Dict, Any

class SwarmToolValidator(dspy.Module):
    """
    Validates swarm tool calls (swarm_init, agent_spawn, task_orchestrate).

    Ensures:
    - All required parameters present
    - Parameter types correct
    - Parameter values within valid ranges
    - Dependencies satisfied
    """

    def __init__(self):
        super().__init__()
        self.validate_params = dspy.ChainOfThought(
            "tool_name, params -> validated_params"
        )

    def forward(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and potentially correct MCP tool parameters.

        Args:
            tool_name: MCP tool to call (swarm_init, agent_spawn, etc.)
            params: Tool parameters to validate

        Returns:
            Validated (and possibly corrected) parameters

        Raises:
            ValueError: If parameters cannot be corrected
        """
        # Get tool schema
        schema = self._get_tool_schema(tool_name)

        # Validate parameters
        prediction = self.validate_params(
            tool_name=tool_name,
            params=params
        )

        # Check against schema
        validated = self._validate_against_schema(prediction, schema)

        return validated

    def _get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get parameter schema for MCP tool."""
        schemas = {
            "swarm_init": {
                "required": ["topology", "maxAgents"],
                "optional": ["optimization", "persistence"]
            },
            "agent_spawn": {
                "required": ["type", "task"],
                "optional": ["priority", "resources"]
            },
            # ... more tools
        }
        return schemas.get(tool_name, {})
```

**All Validators**:
1. `SwarmToolValidator` - swarm_init, agent_spawn, task_orchestrate
2. `GitHubToolValidator` - repo_analyze, pr_enhance, issue_triage
3. `MemoryToolValidator` - memory_store, memory_retrieve
4. `NeuralToolValidator` - neural_train, neural_patterns

**Deliverables**:
- 4 MCP tool validator modules
- Tool parameter schemas
- Validation error messages

---

### Phase 3: Training Datasets & Optimization (4-6 hours)

**Goal**: Create training data and train optimizer modules

#### 3.1 Create Training Datasets (2-3 hours)

**Dataset Structure**:

```
datasets/week21/
  ├── communication/
  │   ├── queen_to_princess_examples.json       # 15 examples
  │   ├── princess_to_drone_examples.json       # 15 examples
  │   ├── drone_coordination_examples.json      # 10 examples
  │   └── cross_princess_examples.json          # 10 examples
  └── mcp_tools/
      ├── swarm_tool_calls.json                 # 15 examples
      ├── github_tool_calls.json                # 15 examples
      ├── memory_tool_calls.json                # 10 examples
      └── neural_tool_calls.json                # 10 examples
```

**Example Dataset** (queen_to_princess_examples.json):

```json
{
  "dataset_id": "queen-to-princess-v1",
  "total_examples": 15,
  "examples": [
    {
      "input": {
        "task_description": "Implement OAuth2 authentication with JWT tokens, supporting GitHub and Google providers. Must include secure token storage, refresh token rotation, and session management.",
        "objective": "Add production-ready authentication system with <200ms login latency and 99.9% uptime",
        "constraints": {
          "max_duration_hours": 6,
          "security_level": "production",
          "test_coverage_min": 90
        }
      },
      "expected_output": {
        "workflow_id": "auth-oauth2-001",
        "subtasks": [
          {
            "id": "auth-001-spec",
            "agent": "spec-writer",
            "task_type": "write-spec",
            "description": "Document OAuth2 requirements: providers (GitHub, Google), token types (access, refresh), security requirements (PKCE, state validation)",
            "dependencies": [],
            "estimated_minutes": 30,
            "deliverables": ["OAuth2 specification document", "Security checklist"]
          },
          {
            "id": "auth-001-arch",
            "agent": "architect",
            "task_type": "design-architecture",
            "description": "Design token storage architecture: Redis for active sessions, PostgreSQL for refresh tokens, secure cookie handling, CSRF protection",
            "dependencies": ["auth-001-spec"],
            "estimated_minutes": 45,
            "deliverables": ["Architecture diagram", "Database schema", "API endpoint design"]
          },
          {
            "id": "auth-001-impl",
            "agent": "coder",
            "task_type": "implement-code",
            "description": "Implement OAuth2 flow: authorization endpoint, token exchange, refresh token rotation, session middleware. Use passport.js for OAuth integration.",
            "dependencies": ["auth-001-arch"],
            "estimated_minutes": 90,
            "deliverables": ["OAuth2 service implementation", "Session middleware", "Provider adapters"]
          },
          {
            "id": "auth-001-test",
            "agent": "tester",
            "task_type": "generate-tests",
            "description": "Create OAuth2 test suite: unit tests for token generation/validation, integration tests for full OAuth flow, security tests for CSRF/XSS prevention",
            "dependencies": ["auth-001-impl"],
            "estimated_minutes": 60,
            "deliverables": ["Unit test suite (≥90% coverage)", "Integration test suite", "Security test suite"]
          },
          {
            "id": "auth-001-security",
            "agent": "security-manager",
            "task_type": "audit-security",
            "description": "Security audit: validate PKCE implementation, check token expiration, verify secure cookie flags, test CSRF protection, scan for OAuth vulnerabilities",
            "dependencies": ["auth-001-impl"],
            "estimated_minutes": 30,
            "deliverables": ["Security audit report", "Vulnerability scan results"]
          },
          {
            "id": "auth-001-review",
            "agent": "reviewer",
            "task_type": "review-code",
            "description": "Code review: verify NASA Rule 10 compliance, check error handling, validate logging, ensure proper async/await usage",
            "dependencies": ["auth-001-impl", "auth-001-test", "auth-001-security"],
            "estimated_minutes": 40,
            "deliverables": ["Code review report", "Quality score"]
          },
          {
            "id": "auth-001-docs",
            "agent": "docs-writer",
            "task_type": "write-documentation",
            "description": "Documentation: API documentation for OAuth endpoints, setup guide for providers, troubleshooting guide, security best practices",
            "dependencies": ["auth-001-review"],
            "estimated_minutes": 35,
            "deliverables": ["API documentation", "Setup guide", "Security documentation"]
          }
        ],
        "dependencies": {
          "auth-001-spec": [],
          "auth-001-arch": ["auth-001-spec"],
          "auth-001-impl": ["auth-001-arch"],
          "auth-001-test": ["auth-001-impl"],
          "auth-001-security": ["auth-001-impl"],
          "auth-001-review": ["auth-001-impl", "auth-001-test", "auth-001-security"],
          "auth-001-docs": ["auth-001-review"]
        },
        "quality_gates": [
          "security-audit-passed",
          "test-coverage-90-percent",
          "code-review-approved",
          "nasa-compliance-check"
        ],
        "estimated_duration_min": 330,
        "critical_path": ["auth-001-spec", "auth-001-arch", "auth-001-impl", "auth-001-review", "auth-001-docs"]
      },
      "quality_score": 98.0,
      "rationale": "Comprehensive workflow with proper dependency ordering, realistic time estimates, security-first approach, complete quality gates, and NASA-compliant deliverables"
    }
    // ... 14 more examples
  ]
}
```

**Dataset Categories**:

**Communication Datasets**:
1. **Simple tasks** (3 examples): 2-3 subtasks, <2 hours
2. **Medium complexity** (6 examples): 4-6 subtasks, 2-4 hours
3. **Complex workflows** (4 examples): 7-10 subtasks, 4-8 hours
4. **Edge cases** (2 examples): Error handling, dependency conflicts

**MCP Tool Datasets**:
1. **Valid calls** (10 examples per tool): Correct parameters
2. **Common mistakes** (3 examples per tool): Missing params, wrong types
3. **Edge cases** (2 examples per tool): Boundary values, complex scenarios

**Deliverables**:
- 8 training dataset files
- 90-120 total training examples
- Quality scores for each example

#### 3.2 Training Script Adaptation (1-2 hours)

**Modify Existing Training Infrastructure**:

**File**: `src/communication/train_optimizers.py` (adapt from `src/dspy_optimization/train.py`)

```python
"""
Training script for communication optimizer modules.

Reuses DSPy infrastructure from Week 6:
- dspy_config.py: Gemini configuration
- data_loader.py: Dataset loading (with Bug #5 fix)
- gemini_cli_adapter.py: Gemini interface

New additions:
- Communication-specific metrics
- Multi-module training orchestration
- Validation against communication schemas
"""

import argparse
from pathlib import Path
from typing import Dict, Any

# Reuse existing DSPy infrastructure
from src.dspy_optimization.dspy_config import configure_dspy, validate_api_connection
from src.dspy_optimization.data_loader import load_training_dataset, split_train_val

# New communication modules
from src.communication.dspy_modules import (
    QueenToPrincessOptimizer,
    PrincessToDroneOptimizer,
    DroneCoordinationOptimizer,
    CrossPrincessOptimizer
)
from src.communication.communication_metrics import (
    queen_to_princess_metric,
    princess_to_drone_metric,
    drone_coordination_metric,
    cross_princess_metric
)

OPTIMIZER_CONFIG = {
    "queen-to-princess": {
        "module_class": QueenToPrincessOptimizer,
        "metric_func": queen_to_princess_metric,
        "dataset_path": "datasets/week21/communication/queen_to_princess_examples.json",
        "max_demos": 10,
        "max_rounds": 3
    },
    "princess-to-drone": {
        "module_class": PrincessToDroneOptimizer,
        "metric_func": princess_to_drone_metric,
        "dataset_path": "datasets/week21/communication/princess_to_drone_examples.json",
        "max_demos": 10,
        "max_rounds": 3
    },
    # ... more configurations
}

def train_optimizer(optimizer_id: str) -> Dict[str, Any]:
    """Train a single communication optimizer module."""
    # Similar to train_agent() from Week 6, but for communication optimization
    ...
```

**Deliverables**:
- Training script for communication optimizers
- Training script for MCP tool validators
- Evaluation scripts for both

#### 3.3 Run Training & Validation (1 hour)

**Training Sequence**:

```bash
# 1. Train communication optimizers (sequentially to avoid Gemini rate limits)
python src/communication/train_optimizers.py --optimizer queen-to-princess
python src/communication/train_optimizers.py --optimizer princess-to-drone
python src/communication/train_optimizers.py --optimizer drone-coordination
python src/communication/train_optimizers.py --optimizer cross-princess

# 2. Train MCP tool validators
python src/mcp_layer/train_validators.py --validator swarm-tools
python src/mcp_layer/train_validators.py --validator github-tools
python src/mcp_layer/train_validators.py --validator memory-tools
python src/mcp_layer/train_validators.py --validator neural-tools
```

**Validation**:
- Evaluate on validation sets (20% of data)
- Target: ≥85% quality score on validation
- Manual review of 10 sample predictions

**Deliverables**:
- 8 trained DSPy modules in `models/dspy/communication/`
- Training reports with metrics
- Validation results

---

### Phase 4: Integration (3-4 hours)

**Goal**: Integrate DSPy middleware into existing protocol

#### 4.1 Middleware Integration (2 hours)

**File**: `src/communication/optimizer_middleware.py`

```python
"""
Communication middleware that intercepts agent messages.

Integrates with EnhancedLightweightProtocol to optimize messages
before transmission.
"""

import dspy
from typing import Dict, Any, Optional
from src.communication.dspy_modules import (
    QueenToPrincessOptimizer,
    PrincessToDroneOptimizer,
    DroneCoordinationOptimizer,
    CrossPrincessOptimizer
)

class CommunicationMiddleware:
    """
    Middleware layer that optimizes agent-to-agent messages using DSPy.
    """

    def __init__(self, models_dir: str = "models/dspy/communication"):
        """Load trained optimizer modules."""
        self.queen_to_princess = self._load_optimizer(
            f"{models_dir}/queen_to_princess_optimized.json",
            QueenToPrincessOptimizer
        )
        self.princess_to_drone = self._load_optimizer(
            f"{models_dir}/princess_to_drone_optimized.json",
            PrincessToDroneOptimizer
        )
        # ... load other optimizers

    async def optimize_message(
        self,
        source_agent_id: str,
        target_agent_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize message based on source→target communication path.

        Args:
            source_agent_id: Sending agent (e.g., "queen")
            target_agent_id: Receiving agent (e.g., "princess-dev")
            message: Raw message to optimize

        Returns:
            Optimized message with improved structure
        """
        # Determine communication path
        path = self._determine_path(source_agent_id, target_agent_id)

        # Select appropriate optimizer
        if path == "queen-to-princess":
            return self.queen_to_princess.forward(
                task_description=message.get("description", ""),
                objective=message.get("payload", {}).get("workflow", {}).get("objective", "")
            )
        elif path == "princess-to-drone":
            return self.princess_to_drone.forward(
                workflow_phase=message.get("phase", ""),
                requirements=message.get("description", "")
            )
        # ... other paths

        # Fallback: return unmodified message
        return message

    def _determine_path(self, source: str, target: str) -> str:
        """Determine communication path from agent IDs."""
        if source == "queen" and target.startswith("princess-"):
            return "queen-to-princess"
        elif source.startswith("princess-") and not target.startswith("princess-"):
            return "princess-to-drone"
        # ... more path detection
        return "unknown"
```

#### 4.2 Protocol Integration (1-2 hours)

**Modify**: `src/protocols/EnhancedLightweightProtocol.py`

```python
# Add to ProtocolConfig
@dataclass
class ProtocolConfig:
    # ... existing fields
    dspy_optimization_enabled: bool = False  # Feature flag
    dspy_models_dir: str = "models/dspy/communication"

# Modify EnhancedLightweightProtocol.__init__
class EnhancedLightweightProtocol:
    def __init__(self, config: Optional[ProtocolConfig] = None):
        self.config = config or ProtocolConfig()
        # ... existing initialization

        # NEW: Initialize DSPy middleware if enabled
        if self.config.dspy_optimization_enabled:
            from src.communication.optimizer_middleware import CommunicationMiddleware
            self.communication_middleware = CommunicationMiddleware(
                models_dir=self.config.dspy_models_dir
            )

# Modify send_task() method
async def send_task(
    self,
    sender_id: str,
    receiver_id: str,
    task: Dict[str, Any]
) -> Dict[str, Any]:
    start_time = time.time()

    # NEW: Optimize message with DSPy if enabled
    if self.config.dspy_optimization_enabled:
        task = await self.communication_middleware.optimize_message(
            source_agent_id=sender_id,
            target_agent_id=receiver_id,
            message=task
        )

    # Existing circuit breaker check
    if not self._check_circuit_breaker(receiver_id):
        raise RuntimeError(f"Circuit breaker OPEN for {receiver_id}")

    # ... rest of existing send logic
```

**Deliverables**:
- Communication middleware implementation
- EnhancedLightweightProtocol integration
- Feature flag for gradual rollout

---

## 📊 Success Metrics

### Communication Optimization

**Quality Metrics**:
- ✅ **Completeness**: 100% of required fields present
- ✅ **Validity**: 100% of agent IDs and task types valid
- ✅ **Clarity**: ≥90% of subtask descriptions meet clarity standards
- ✅ **Efficiency**: ≥85% of time estimates within 20% of actual

**Performance Metrics**:
- ⚡ **Latency**: <50ms optimization overhead (p95)
- 📈 **Success Rate**: ≥95% of optimized messages execute successfully
- 🎯 **Quality Score**: ≥85% average quality score on validation set

### MCP Tool Validation

**Validation Metrics**:
- ✅ **Parameter Coverage**: 100% of required params validated
- ✅ **Type Safety**: 100% of type mismatches caught
- ✅ **Error Prevention**: ≥90% of invalid calls caught before API
- ⚡ **Validation Speed**: <10ms per validation (p95)

---

## 🔄 Rollout Strategy

### Phase 1: Development (Week 21)
- Implement all modules
- Train on synthetic datasets
- Validate with unit tests

### Phase 2: Internal Testing (Week 22)
- Enable DSPy for Queen→Princess only
- Monitor quality metrics
- Collect real-world examples

### Phase 3: Gradual Rollout (Week 23)
- Expand to Princess→Drone
- Add MCP tool validation
- A/B test optimized vs baseline

### Phase 4: Production (Week 24)
- Enable for all communication paths
- Monitor performance
- Iterate based on metrics

---

## 🚫 What We're NOT Changing

- ❌ Agent system instructions (those are correct)
- ❌ AgentBase.py core logic (only add middleware hook)
- ❌ EnhancedLightweightProtocol core protocol (only add optimization layer)
- ❌ Task dataclass structure (keep for type safety)

---

## 📁 File Structure Summary

```
src/
  ├── communication/
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   ├── queen_to_princess.py
  │   │   ├── princess_to_drone.py
  │   │   ├── drone_coordination.py
  │   │   └── cross_princess.py
  │   ├── __init__.py
  │   ├── dspy_modules.py               # 4 optimizer modules
  │   ├── optimizer_middleware.py       # Middleware integration
  │   ├── communication_metrics.py      # Quality metrics
  │   └── train_optimizers.py           # Training script
  ├── mcp_layer/
  │   ├── schemas/
  │   │   ├── __init__.py
  │   │   ├── swarm_tools_schema.py
  │   │   ├── github_tools_schema.py
  │   │   ├── memory_tools_schema.py
  │   │   └── neural_tools_schema.py
  │   ├── __init__.py
  │   ├── dspy_validators.py            # 4 validator modules
  │   ├── mcp_metrics.py                # Validation metrics
  │   └── train_validators.py           # Training script
  └── protocols/
      └── EnhancedLightweightProtocol.py  # Modified: add middleware hook

datasets/
  └── week21/
      ├── communication/
      │   ├── queen_to_princess_examples.json
      │   ├── princess_to_drone_examples.json
      │   ├── drone_coordination_examples.json
      │   └── cross_princess_examples.json
      └── mcp_tools/
          ├── swarm_tool_calls.json
          ├── github_tool_calls.json
          ├── memory_tool_calls.json
          └── neural_tool_calls.json

models/
  └── dspy/
      └── communication/
          ├── queen_to_princess_optimized.json
          ├── princess_to_drone_optimized.json
          ├── drone_coordination_optimized.json
          ├── cross_princess_optimized.json
          ├── swarm_tools_validator.json
          ├── github_tools_validator.json
          ├── memory_tools_validator.json
          └── neural_tools_validator.json
```

**Total Files**: ~30 new files + 2 modified files

---

## ⏱️ Timeline & Effort Estimate

| Phase | Duration | Complexity | Dependencies |
|-------|----------|------------|--------------|
| Phase 1: Schema Definition | 3-4 hours | LOW | None |
| Phase 2: DSPy Modules | 5-6 hours | MEDIUM | Phase 1 |
| Phase 3: Training | 4-6 hours | MEDIUM | Phase 2, Gemini API |
| Phase 4: Integration | 3-4 hours | MEDIUM | Phase 3 |
| **TOTAL** | **15-20 hours** | **MEDIUM** | **2-3 days** |

---

## ✅ Next Steps

1. **Get Approval**: Review this plan with user
2. **Start Phase 1**: Begin with schema definition
3. **Validate Early**: Test each module independently before integration
4. **Measure Everything**: Track quality metrics throughout

---

**Version**: 1.0
**Document**: DSPY-COMMUNICATION-LAYER-PLAN.md
**Timestamp**: 2025-10-10
**Status**: READY FOR IMPLEMENTATION
