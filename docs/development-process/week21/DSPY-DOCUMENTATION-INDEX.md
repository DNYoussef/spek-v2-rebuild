# DSPy Documentation Index - Week 21

## Overview

This directory contains complete documentation for DSPy prompt optimization integration into the SPEK v2 agent communication system.

**Last Updated**: 2025-10-10
**Status**: PLAN COMPLETE - Ready for implementation

---

## Current Documentation (ACTIVE)

### 1. DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md ⭐ **PRIMARY**
**Purpose**: Complete implementation plan for all 34+ communication paths

**Contents**:
- Accurate technical description of DSPy (training vs runtime)
- Complete communication path mapping (Queen↔Princess↔Drone)
- Module architecture for all path types
- Training dataset requirements (100-200 examples per path)
- MCP tool validation layer design
- 8-phase implementation timeline
- Success metrics and risk mitigation

**Key Specs**:
- Latency Budget: 250ms per message (acceptable)
- Training Cost: ~$1,000 (one-time, mostly human curation)
- Runtime Cost: +$100/month incremental
- 34 primary communication paths
- Model-agnostic (uses agent's configured LLM)

**Use This For**: All implementation work, training dataset creation, module development

---

### 2. DSPY-HOW-IT-WORKS-UPDATED.md ⭐ **TECHNICAL REFERENCE**
**Purpose**: Accurate technical explanation of DSPy mechanics

**Contents**:
- DSPy component breakdown (Signatures, Modules, Programs, Metrics, Optimizers)
- Training phase mechanics (what happens during compile())
- Runtime phase mechanics (what happens per message)
- Model-agnostic design explanation
- Latency breakdown (165-315ms average)
- What DSPy does NOT do (not fine-tuning, not static rules)

**Key Insights**:
- **Training**: Offline, one-time, learns instruction string + 10 demos
- **Runtime**: Online, every message, calls LLM with optimized prompts
- **No Model Weights**: Only saves demonstration examples as JSON
- **100-250ms latency**: Acceptable per user decision

**Use This For**: Understanding DSPy internals, explaining to team, debugging issues

---

## Archived Documentation (SUPERSEDED)

### 3. DSPY-COMMUNICATION-LAYER-PLAN.md ❌ **DEPRECATED**
**Status**: Superseded by DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md

**Why Deprecated**:
- Had Gemini-specific references (should be model-agnostic)
- Missing complete communication path mapping
- Incomplete MCP tool validation design
- Pre-dated 250ms latency decision

**Do NOT Use**: Reference comprehensive plan instead

---

### 4. DSPY-HOW-IT-WORKS.md ❌ **DEPRECATED**
**Status**: Superseded by DSPY-HOW-IT-WORKS-UPDATED.md

**Why Deprecated**:
- Initial misunderstanding (thought DSPy was static rules)
- Incomplete latency analysis
- Missing model-agnostic explanation

**Do NOT Use**: Reference updated version instead

---

### 5. MODEL-AGNOSTIC-ADDENDUM.md ✅ **HISTORICAL**
**Status**: Informational only (concepts integrated into comprehensive docs)

**Contents**: Clarification that DSPy is model-agnostic, uses agent's LLM

**Note**: Content fully integrated into comprehensive plan and updated how-it-works doc. Kept for historical reference only.

---

## Quick Reference

### When to Use Which Document

| Task | Document |
|------|----------|
| Implementing DSPy integration | DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md |
| Creating training datasets | DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md (Section 4) |
| Understanding DSPy mechanics | DSPY-HOW-IT-WORKS-UPDATED.md |
| Debugging latency issues | DSPY-HOW-IT-WORKS-UPDATED.md (Section 3.2) |
| Designing new optimizers | DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md (Section 3) |
| MCP tool validation | DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md (Section 5) |

---

## Key Technical Facts (Quick Lookup)

### DSPy in One Sentence
**DSPy optimizes prompt structure (instruction + few-shot demos) via metric-driven search, then calls LLM at runtime with optimized prompts (100-250ms per message).**

### What DSPy IS
- ✅ Prompt optimization framework
- ✅ Few-shot demonstration selector
- ✅ Instruction string optimizer
- ✅ Calls LLM at runtime (every message)
- ✅ Model-agnostic (uses agent's LLM)

### What DSPy is NOT
- ❌ NOT model fine-tuning
- ❌ NOT neural network training
- ❌ NOT static rules/pattern matching
- ❌ NOT zero-latency
- ❌ NOT model-specific

### Communication Paths (34 Total)

**Tier 1 (P0 - Critical)**:
- Queen → 3 Princesses (3 paths)
- Princess → Individual Drones (11 paths)

**Tier 2 (P1 - High)**:
- Princess → Hive Broadcast (3 paths)
- Drone → Princess (11 paths)

**Tier 3 (P2 - Medium)**:
- Princess ↔ Princess (6 bidirectional paths)
- Princess → Queen (3 paths)

### Latency Budget
- **Target**: <250ms average per message
- **Breakdown**: 5ms prompt build + 100-250ms LLM call + 10ms parsing
- **Acceptable**: User explicitly approved 250ms budget

### Training vs Runtime

| Aspect | Training | Runtime |
|--------|----------|---------|
| When | One-time (before deploy) | Every message |
| LLM Calls | 100-300 per optimizer | 1 per message |
| Duration | 5-30 minutes | 100-250ms |
| Cost | $0.02-0.10 per optimizer | $0.0001-0.0003 per message |
| Output | JSON (instruction + demos) | Structured result |

---

## Implementation Phases (8 Phases, 3 Weeks)

### Week 21 (Days 3-7): Foundation + P0 Training
- Phase 1: DSPy infrastructure setup
- Phase 2: Dataset creation (300 examples)
- Phase 3: Train P0 optimizers (3 Queen→Princess paths)

### Week 22 (Days 1-7): Integration + P1 Training
- Phase 4: Integrate into Queen + Princesses
- Phase 5: Train P1 optimizers (22 Princess↔Drone paths)

### Week 23 (Days 1-7): MCP + P2 + Optimization
- Phase 6: MCP tool validation layer
- Phase 7: Train P2 optimizers (9 remaining paths)
- Phase 8: Production validation

---

## File Maintenance

### Active Files (DO NOT DELETE)
- ✅ DSPY-COMPREHENSIVE-IMPLEMENTATION-PLAN.md
- ✅ DSPY-HOW-IT-WORKS-UPDATED.md
- ✅ This index (DSPY-DOCUMENTATION-INDEX.md)

### Historical Files (KEEP FOR REFERENCE)
- 📄 MODEL-AGNOSTIC-ADDENDUM.md

### Deprecated Files (CAN ARCHIVE)
- ❌ DSPY-COMMUNICATION-LAYER-PLAN.md → Move to `archive/` subdirectory
- ❌ DSPY-HOW-IT-WORKS.md → Move to `archive/` subdirectory

---

## Related Documentation

### Agent System Docs
- `src/agents/core/QueenAgent.py` - Queen delegation logic (lines 115-144)
- `src/agents/swarm/PrincessDevAgent.py` - Dev hive coordination (lines 110-144)
- `src/agents/swarm/PrincessQualityAgent.py` - QA hive coordination (lines 115-130)
- `src/agents/swarm/PrincessCoordinationAgent.py` - Task coordination (lines 113-118)
- `src/agents/AgentBase.py` - Base delegation method (lines 333-357)

### System Instructions (Week 21)
- `src/agents/instructions.py` - All 22 agent instructions with 26 prompting principles
- `research/26-PROMPT-ENGINEERING-PRINCIPLES-ANALYSIS.md` - Prompting research

### DSPy Model Artifacts (Week 6)
- `models/dspy/queen_optimized.json` - Example optimized Queen model (from v6 training)

---

## Version History

**v3.0 (2025-10-10)**:
- Created comprehensive implementation plan (all 34 paths)
- Updated technical docs with accurate DSPy mechanics
- Integrated user feedback (250ms latency, model-agnostic, no model weights)
- Deprecated old plans with Gemini references

**v2.0 (2025-10-10)**:
- Added model-agnostic addendum
- Clarified DSPy as prompt middleware (not training)

**v1.0 (2025-10-10)**:
- Initial DSPy communication layer plan
- Initial how-it-works explanation

---

## Contact / Questions

**Stakeholder**: User (approved 250ms latency budget)
**Implementation Lead**: TBD (assign during Week 21 Day 3)
**Timeline**: 3 weeks (Weeks 21-23)
**Budget**: $1,000 training (one-time) + $100/month runtime (incremental)

---

**Document Version**: 3.0
**Last Updated**: 2025-10-10T21:35:00-04:00
**Status**: COMPLETE - Ready for implementation kickoff
**Next Action**: Begin Phase 1 (Foundation) - Set up DSPy infrastructure
