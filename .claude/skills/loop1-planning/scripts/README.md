# Loop 1 Planning Scripts - Production-Ready Helpers

## Overview

Three production-ready helper scripts for Loop 1 Pre-Mortem Driven Planning phase of the SPEK Platform v2 development methodology.

**Status**: ✅ Production-Ready (100% NASA Rule 10 Compliant)

## Scripts

### 1. research_coordinator.py (227 LOC)

Spawns and coordinates researcher agents for gathering evidence-based findings.

**Functions** (6 total, all ≤60 LOC):
- `validate_research_topic()` - 23 LOC - Validates research topic inputs
- `build_researcher_prompt()` - 41 LOC - Constructs structured prompts
- `_execute_spawn_command()` - 52 LOC - Executes spawn via subprocess
- `spawn_researcher_agent()` - 36 LOC - Main spawn orchestration
- `collect_research_findings()` - 42 LOC - Aggregates research files
- `export_research_summary()` - 29 LOC - Exports findings to JSON

**Features**:
- Claude Flow integration via subprocess
- Focus area specification
- Research depth control (quick/moderate/comprehensive)
- Automatic timestamp-based file naming
- 300-second timeout protection
- Complete error handling

**Usage**:
```python
from research_coordinator import spawn_researcher_agent
from pathlib import Path

result = spawn_researcher_agent(
    topic="AI agent coordination best practices",
    output_dir=Path("research"),
    focus_areas=["performance", "error handling", "testing"],
    depth="comprehensive"
)

if result["success"]:
    print(f"Research output: {result['output_path']}")
```

### 2. premortem_generator.py (188 LOC)

Calculates risk scores and implements GO/NO-GO decision logic using SPEK methodology.

**Functions** (10 total, all ≤34 LOC):
- `__init__()` - 9 LOC - Initializes generator with output directory
- `calculate_risk_score()` - 19 LOC - Weighted risk calculation
- `determine_decision()` - 16 LOC - GO/CAUTION/NO-GO logic
- `calculate_confidence()` - 13 LOC - Confidence percentage (0-100)
- `analyze_risks()` - 34 LOC - Complete risk analysis
- `generate_report()` - 29 LOC - Markdown report generation
- `_format_report()` - 25 LOC - Report formatting
- `_format_risk_breakdown()` - 9 LOC - Breakdown section
- `_get_decision_rationale()` - 8 LOC - Decision explanation
- `_format_risk_details()` - 9 LOC - Risk detail formatting

**Risk Weights** (SPEK Methodology):
- P0 (Critical): 500 points
- P1 (High): 200 points
- P2 (Medium): 50 points
- P3 (Low): 10 points

**Decision Thresholds**:
- GO: ≤2,000 points
- CAUTION: 2,001-3,500 points
- NO-GO: >3,500 points

**Usage**:
```python
from premortem_generator import PremorteMGenerator
from pathlib import Path

generator = PremorteMGenerator(output_dir=Path("premortem"))

risks = [
    {"level": "P1", "count": 2, "title": "DB Migration",
     "description": "Schema changes"},
    {"level": "P2", "count": 5, "title": "API Changes",
     "description": "Breaking changes"}
]

result = generator.generate_report(risks, version="1.0")

if result["success"]:
    print(f"Decision: {result['analysis']['decision']}")
    print(f"Score: {result['analysis']['score']}")
    print(f"Report: {result['report_file']}")
```

### 3. loop1_memory.py (188 LOC)

Manages memory persistence for Loop 1 planning state and Loop 2 handoff.

**Functions** (7 total, all ≤47 LOC):
- `__init__()` - 10 LOC - Initializes memory directory
- `save_state()` - 47 LOC - Persists Loop 1 state with checksum
- `load_state()` - 33 LOC - Loads and validates state integrity
- `prepare_loop2_handoff()` - 43 LOC - Creates handoff package
- `_calculate_checksum()` - 6 LOC - SHA256 integrity check
- `_generate_next_actions()` - 22 LOC - Action list by decision
- `get_summary()` - 24 LOC - Quick state summary

**Features**:
- SHA256 checksum integrity validation
- Automatic versioning
- Decision-based next actions
- JSON-based persistence
- Loop 2 handoff package generation

**Usage**:
```python
from loop1_memory import Loop1Memory
from pathlib import Path

memory = Loop1Memory(memory_dir=Path(".claude/memory"))

# Save Loop 1 state
result = memory.save_state(
    spec={"version": "1.0", "title": "Feature X"},
    plan={"total_weeks": 4, "phases": ["Week 1", "Week 2"]},
    premortem={"decision": "GO", "score": 1500},
    research={"findings": [...]}
)

# Load state
state = memory.load_state()
if state["success"]:
    print(f"Decision: {state['state']['premortem']['decision']}")

# Prepare handoff to Loop 2
handoff = memory.prepare_loop2_handoff()
if handoff["success"]:
    print(f"Ready for Loop 2: {handoff['handoff']['loop1_complete']}")
    print(f"Next actions: {handoff['handoff']['next_actions']}")
```

## Quality Metrics

### NASA Rule 10 Compliance
✅ **100% Compliant** - All 23 functions ≤60 LOC

| Script | Functions | Max LOC | Status |
|--------|-----------|---------|--------|
| research_coordinator.py | 6 | 52 | ✅ PASS |
| premortem_generator.py | 10 | 34 | ✅ PASS |
| loop1_memory.py | 7 | 47 | ✅ PASS |

### Code Quality Standards

✅ **100% Type Hints** - All functions fully typed
✅ **100% Docstrings** - Google-style docstrings
✅ **Complete Error Handling** - Try/except with Dict[str, Any] returns
✅ **Example Usage** - All scripts have `__main__` examples
✅ **Production-Ready** - No placeholders, no TODOs

### LOC Summary

| Script | Total LOC | Code LOC | Comment LOC |
|--------|-----------|----------|-------------|
| research_coordinator.py | 280 | 227 | 53 |
| premortem_generator.py | 245 | 188 | 57 |
| loop1_memory.py | 233 | 188 | 45 |
| **TOTAL** | **758** | **603** | **155** |

## Integration with Loop 1 Workflow

### Phase 1: Research (research_coordinator.py)
```bash
# Spawn researcher for evidence gathering
python research_coordinator.py
```

### Phase 2: Risk Analysis (premortem_generator.py)
```bash
# Generate pre-mortem with risk scoring
python premortem_generator.py --risks risks.json
```

### Phase 3: State Persistence (loop1_memory.py)
```bash
# Save Loop 1 state and prepare handoff
python loop1_memory.py --action save --data state.json
```

## File Organization

```
.claude/skills/loop1-planning/scripts/
├── README.md                    # This file
├── research_coordinator.py      # Researcher agent spawning (227 LOC)
├── premortem_generator.py       # Risk scoring & GO/NO-GO (188 LOC)
└── loop1_memory.py              # Memory persistence (188 LOC)
```

## Dependencies

- Python 3.8+
- `subprocess` (standard library)
- `json` (standard library)
- `pathlib` (standard library)
- `datetime` (standard library)
- `hashlib` (standard library)
- `typing` (standard library)
- `enum` (standard library)

**External**:
- `npx claude-flow@alpha` (for researcher spawning)

## Error Handling

All functions return `Dict[str, Any]` with consistent structure:

```python
# Success
{
    "success": True,
    "data_key": "value",
    ...
}

# Failure
{
    "success": False,
    "error": "Human-readable error message"
}
```

## Testing

Run example usage for each script:

```bash
# Test research coordinator
python research_coordinator.py

# Test premortem generator
python premortem_generator.py

# Test memory persistence
python loop1_memory.py
```

## Version History

**v1.0.0** (2025-10-17)
- Initial production-ready release
- 100% NASA Rule 10 compliance
- Complete type hints and docstrings
- Full error handling
- Example usage in all scripts

## License

Part of SPEK Platform v2 - Internal tooling

## Support

For issues or questions, refer to:
- Main project: `CLAUDE.md` in repository root
- Architecture docs: `architecture/ARCHITECTURE-MASTER-TOC.md`
- Loop 1 methodology: `specs/SPEC-v6-FINAL.md`

---

**Last Updated**: 2025-10-17
**Status**: ✅ Production-Ready
**NASA Rule 10**: ✅ 100% Compliant (23/23 functions ≤60 LOC)
**Total Deliverable**: 603 LOC across 3 scripts
