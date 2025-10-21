# ⚠️ DEPRECATED - DO NOT USE

This directory (`src/dspy_optimization/`) is **DEPRECATED** as of Week 21 Day 3 (2025-10-10).

## Replacement

**Use instead**: `src/dspy_optimizers/`

## Why Deprecated

1. **Model-Specific Code**: Contains Gemini-specific implementations (gemini_config.py, gemini_cli_adapter.py)
2. **User Directive**: "remove all mention of gemini from the code, this is model agnostic"
3. **Outdated Architecture**: Targeted 4 P0 agents vs new 34 communication paths
4. **Wrong Latency Budget**: Assumed <100ms vs user-approved 250ms budget

## Migration Path

All functionality has been migrated to `src/dspy_optimizers/`:

| Old File | New File | Notes |
|----------|----------|-------|
| `signatures/queen_signature.py` | `signatures/task_decomposition.py` | Renamed, model-agnostic |
| `signatures/coder_signature.py` | `signatures/task_delegation.py` | Expanded for Princess→Drone |
| `signatures/tester_signature.py` | `signatures/result_aggregation.py` | Generalized for all drones |
| `signatures/reviewer_signature.py` | `signatures/result_aggregation.py` | Merged into aggregation |
| `gemini_config.py` | ❌ REMOVED | Model-agnostic design |
| `gemini_cli_adapter.py` | ❌ REMOVED | Not needed |
| `dspy_config.py` | `core/queen_to_princess.py` | Integrated into modules |
| `train.py` | `../../scripts/train_dspy_optimizers.py` | Rewritten |
| `dspy_metrics.py` | `../../scripts/train_dspy_optimizers.py` | Metric functions integrated |

## New Features in `dspy_optimizers/`

1. **Model-Agnostic**: Works with any LLM (Gemini, GPT, Claude, Llama)
2. **34 Communication Paths**: Complete Queen↔Princess↔Drone hierarchy
3. **MCP Tool Validation**: 16 MCP tool schemas with validation
4. **300 Training Examples**: 100 per path (Dev, Quality, Coordination)
5. **Top 10 Demos**: Curated demonstrations for BootstrapFewShot
6. **Comprehensive Docs**: 61KB of implementation guides

## Action Required

**For Scripts**: Update imports from `src.dspy_optimization` to `src.dspy_optimizers`

**Example**:
```python
# OLD (deprecated)
from src.dspy_optimization.signatures.queen_signature import TaskDecompositionSignature

# NEW (correct)
from src.dspy_optimizers.signatures import TaskDecompositionSignature
```

## Timeline

- **Week 6** (2025-10-08): Original implementation created
- **Week 21** (2025-10-10): Replaced with model-agnostic version
- **Week 22** (2025-10-17): This directory will be removed

## Questions

See: `docs/development-process/week21/DSPY-DOCUMENTATION-INDEX.md`

---

**Status**: ⚠️ DEPRECATED - Use `src/dspy_optimizers/` instead
**Last Updated**: 2025-10-10
