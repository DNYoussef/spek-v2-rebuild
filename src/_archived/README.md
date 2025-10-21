# Archived Code

This directory contains deprecated code that has been replaced with newer, improved implementations.

## dspy_optimization_week6_gemini_deprecated/

**Deprecated**: Week 6 DSPy implementation (2025-10-08)
**Replaced by**: `src/dspy_optimizers/` (Week 21, 2025-10-10)

**Why deprecated**:
- Had Gemini-specific code (gemini_config.py, gemini_cli_adapter.py)
- User instructed: "remove all mention of gemini from the code, this is model agnostic"
- Not aligned with 250ms latency budget (had <100ms assumptions)
- Replaced with model-agnostic design using agent's configured LLM

**New implementation** (`src/dspy_optimizers/`):
- Model-agnostic (works with any LLM: Gemini, GPT, Claude)
- 250ms latency budget (user-approved)
- 34 communication paths (vs 4 agents in old version)
- MCP tool validation layer
- 300 training examples (100 per path)

**Migration**: All useful patterns migrated to new implementation.

**Status**: Safe to delete after Week 21 validation complete.
