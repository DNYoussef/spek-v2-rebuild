# DSPy Communication Layer - Model-Agnostic Design

**CRITICAL CLARIFICATION**: This document clarifies that the DSPy communication layer is **model-agnostic** and does NOT manage LLMs.

---

## 🎯 Model-Agnostic Architecture

### Core Principle

**DSPy uses the agent's existing LLM** - it does NOT configure or manage models separately.

### How It Works

**Agent Layer** (existing):
```python
# Agents already have LLM access configured
class QueenAgent(AgentBase):
    def __init__(self):
        # Agent has its own LLM configuration (Claude, GPT, Gemini, local, etc.)
        # This is managed at AGENT level, not DSPy level
        metadata = create_agent_metadata(
            agent_id="queen",
            system_instructions=QUEEN_SYSTEM_INSTRUCTIONS.to_prompt()
            # ↑ Agent's LLM uses these instructions
        )
```

**DSPy Layer** (what we're building):
```python
# DSPy modules use whatever LLM the agent is configured to use
class QueenToPrincessOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # DSPy will use dspy.LM() which delegates to agent's LLM
        # NO model configuration here!
        self.decompose = dspy.ChainOfThought("task_description, objective -> subtasks")

    def forward(self, task_description: str, objective: str):
        # This internally uses the agent's configured LLM
        # Could be Claude, GPT-4, Gemini, Llama, or any other model
        prediction = self.decompose(
            task_description=task_description,
            objective=objective
        )
        return prediction
```

---

## 🚫 What We're NOT Doing

**DO NOT**:
- ❌ Configure specific models (Gemini, GPT, Claude) in DSPy code
- ❌ Manage API keys or endpoints in DSPy layer
- ❌ Reference any specific LLM vendor in code
- ❌ Create model-specific adapters
- ❌ Hard-code model names anywhere

**Example of WRONG approach**:
```python
# ❌ WRONG - Don't do this!
from google.generativeai import configure
configure(api_key="...")
model = genai.GenerativeModel('gemini-1.5-flash')
```

---

## ✅ What We ARE Doing

**DO**:
- ✅ Use `dspy.LM()` which delegates to whatever LLM agent uses
- ✅ Keep all LLM configuration at agent level (outside DSPy)
- ✅ Make DSPy modules work with ANY LLM
- ✅ Focus on prompt structure optimization (model-agnostic)

**Example of CORRECT approach**:
```python
# ✅ CORRECT - DSPy uses agent's LLM automatically
class QueenToPrincessOptimizer(dspy.Module):
    def __init__(self):
        super().__init__()
        # No model configuration - uses agent's LLM
        self.decompose = dspy.ChainOfThought("task_description, objective -> subtasks")
```

---

## 📋 Changes to Original Plan

### Remove All Gemini References

**Original Plan References to Remove**:
1. ~~`gemini_config.py`~~ → Agent's LLM config (managed elsewhere)
2. ~~`gemini_cli_adapter.py`~~ → Not needed (use `dspy.LM()`)
3. ~~`GeminiConfigManager`~~ → Not needed
4. ~~`configure_dspy(temperature, max_tokens)`~~ → `dspy.LM()` uses agent config
5. ~~"Gemini free tier"~~ → Model-agnostic
6. ~~"Gemini API rate limits"~~ → Depends on agent's LLM

### Update Training Infrastructure

**Old Approach** (model-specific):
```python
# ❌ OLD - Don't do this
from src.dspy_optimization.gemini_config import configure_dspy
configure_dspy(model="gemini-1.5-flash", temperature=0.7)
```

**New Approach** (model-agnostic):
```python
# ✅ NEW - DSPy uses agent's LLM
import dspy

# DSPy will automatically use whatever LLM the agent is configured with
# No model configuration needed in DSPy layer
optimizer = QueenToPrincessOptimizer()
```

---

## 🔧 Implementation Changes

### Phase 2: DSPy Module Implementation

**Update dspy_modules.py** to be model-agnostic:

```python
"""
Communication optimizer modules.

IMPORTANT: These modules are model-agnostic.
They use dspy.LM() which delegates to whatever LLM
the agent is configured to use (Claude, GPT, Gemini, local, etc.)
"""

import dspy
from typing import Dict, Any

class QueenToPrincessOptimizer(dspy.Module):
    """
    Model-agnostic optimizer for Queen→Princess communication.

    Uses whatever LLM the agent is configured with.
    No model-specific code or configuration.
    """

    def __init__(self):
        super().__init__()
        # DSPy will use agent's configured LLM
        # No model selection or configuration here
        self.decompose = dspy.ChainOfThought(
            "task_description, objective -> subtasks"
        )

    def forward(self, task_description: str, objective: str) -> Dict[str, Any]:
        """
        Transform Queen task into Princess workflow.

        Uses agent's LLM (model-agnostic).
        """
        prediction = self.decompose(
            task_description=task_description,
            objective=objective
        )
        return self._parse_prediction(prediction)
```

### Phase 3: Training

**Update train_optimizers.py** to be model-agnostic:

```python
"""
Training script for communication optimizers.

Model-agnostic: Uses whatever LLM the agent is configured with.
No Gemini-specific or model-specific code.
"""

import dspy
from src.communication.dspy_modules import QueenToPrincessOptimizer
from src.communication.communication_metrics import queen_to_princess_metric
from src.dspy_optimization.data_loader import load_training_dataset, split_train_val

def train_optimizer(optimizer_id: str):
    """
    Train communication optimizer module.

    Model-agnostic: Uses agent's configured LLM.
    """
    # Load training data
    dataset = load_training_dataset(f"datasets/week21/communication/{optimizer_id}_examples.json")
    trainset, valset = split_train_val(dataset)

    # Initialize optimizer module (uses agent's LLM)
    module = QueenToPrincessOptimizer()

    # Train with BootstrapFewShot
    optimizer = dspy.BootstrapFewShot(
        metric=queen_to_princess_metric,
        max_bootstrapped_demos=10
    )

    # Compile (train) the module
    # Uses whatever LLM agent is configured with
    optimized_module = optimizer.compile(module, trainset=trainset)

    # Save trained module
    optimized_module.save(f"models/dspy/communication/{optimizer_id}_optimized.json")
```

---

## 📊 Benefits of Model-Agnostic Design

### 1. Flexibility
- Works with ANY LLM (Claude, GPT, Gemini, Llama, Mistral, etc.)
- Easy to switch models without changing DSPy code
- Agent teams can use different models

### 2. Simplicity
- No model management code in DSPy layer
- No API key handling
- No vendor-specific logic

### 3. Maintainability
- Model updates don't affect DSPy code
- No hard-coded model names
- Future-proof architecture

### 4. Cost Optimization
- Agents can use different models based on cost/performance trade-offs
- Queen might use GPT-4 for complex decomposition
- Drones might use Gemini Flash for speed
- DSPy works with all of them

---

## 🎯 Summary

**Key Takeaways**:

1. **DSPy is model-agnostic** - it uses whatever LLM the agent is configured with
2. **No model management in DSPy layer** - that's the agent's responsibility
3. **Use `dspy.LM()`** - it automatically delegates to agent's LLM
4. **Remove all Gemini references** - be model-agnostic throughout
5. **Focus on prompt optimization** - not model selection

**Updated Plan**:
- Remove `gemini_config.py`, `gemini_cli_adapter.py`
- Update `train_optimizers.py` to use `dspy.LM()` (agent's LLM)
- Make all DSPy modules model-agnostic
- Keep LLM configuration at agent level (where it belongs)

---

**Version**: 1.1
**Document**: MODEL-AGNOSTIC-ADDENDUM.md
**Timestamp**: 2025-10-10
**Status**: CLARIFICATION - READY TO IMPLEMENT
