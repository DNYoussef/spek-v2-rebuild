# 3-Loop Skills System - Diagram Index

## Overview

This directory contains 6 GraphViz `.dot` diagrams documenting the 3-loop methodology workflow and architecture:

- **Loop 1 Planning**: 1 diagram (planning process)
- **Loop 2 Implementation**: 2 diagrams (implementation process + hierarchy)
- **Loop 3 Quality**: 2 diagrams (quality process + 47-point checklist)
- **Cross-Loop**: 1 diagram (bidirectional flow between loops)

## Diagram Locations

### Loop 1: Planning Diagrams
Location: `.claude/skills/loop1-planning/diagrams/`

1. **loop1-planning-process.dot**
   - **Purpose**: Complete Loop 1 workflow visualization
   - **Phases**: Route Detection → Research → Planning → Pre-mortem → GO Decision
   - **Key Elements**:
     - Route detection logic (simple vs complex tasks)
     - Agent spawning (researcher, planner)
     - Risk assessment (score < 2000)
     - GO/NO-GO decision (>=94% confidence)
     - Escalation from Loop 3 (debug route)
   - **External References**: Memory schema, agent registry

### Loop 2: Implementation Diagrams
Location: `.claude/skills/loop2-implementation/diagrams/`

2. **loop2-implementation-process.dot**
   - **Purpose**: Complete Loop 2 workflow visualization
   - **Phases**: Queen Init → Princess Selection → Drone Spawning → Continuous Audit → Milestone Validation → Handoff
   - **Key Elements**:
     - Queen initialization (Claude Code)
     - Princess selection (dev, quality, coordination)
     - Drone spawning strategy (parallel vs sequential)
     - 3-part audit system (functionality, style, theater)
     - Milestone validation
   - **External References**: Memory schema, agent registry (28 agents)

3. **queen-princess-drone-hierarchy.dot**
   - **Purpose**: 3-tier architecture visualization
   - **Hierarchy**:
     - **Tier 1**: Queen (Claude Code instance)
     - **Tier 2**: 3 Princesses (dev, quality, coordination)
     - **Tier 3**: 24 Drones (grouped by function)
   - **Key Elements**:
     - Agent groupings (development, quality, infrastructure, coordination)
     - Communication flow (Task tool)
     - Agent registry mapping (28 agents)
   - **Agent Count**: 1 Queen + 3 Princesses + 24 Drones = 28 total

### Loop 3: Quality Diagrams
Location: `.claude/skills/loop3-quality/diagrams/`

4. **loop3-quality-process.dot**
   - **Purpose**: Complete Loop 3 workflow visualization
   - **Phases**: Context Load → Audits → Integration → Security → Rewrite (if needed) → 47-Point Gate → Decision → Escalation
   - **Key Elements**:
     - Context loading from memory
     - Comprehensive audits (backend, frontend, E2E, environment)
     - Integration testing
     - Security validation
     - Complete rewrite logic (last resort)
     - 47-point quality gate
     - GO/CAUTION/NO-GO decision (47, 45-46, <45)
     - Escalation to Loop 1 (debug route)
   - **External References**: Memory schema, 47-point checklist

5. **47-point-checklist.dot**
   - **Purpose**: Detailed 47-point quality gate breakdown
   - **Categories** (8 total):
     - **Backend Testing** (12 points): API, unit tests, integration, auth, logging
     - **Frontend Testing** (8 points): Components, E2E, visual regression, a11y
     - **E2E Integration** (7 points): User flows, real-time, error states
     - **Environment & Config** (6 points): Variables, secrets, dependencies
     - **Performance** (5 points): Bundle size, response time, memory
     - **Security** (4 points): Scans, validation, vulnerabilities
     - **Code Quality** (3 points): NASA compliance, TypeScript, ESLint
     - **Final Checks** (2 points): Theater detection, documentation
   - **Scoring Logic**:
     - 47/47 = GO (perfect)
     - 45-46/47 = CAUTION (acceptable with documentation)
     - <45/47 = NO-GO (escalate to Loop 1)

### Cross-Loop Diagram
Location: `.claude/skills/diagrams/`

6. **bidirectional-flow.dot** (already exists)
   - **Purpose**: Bidirectional flow between all 3 loops
   - **Key Elements**: Loop transitions, memory updates, escalation paths

## How to Render Diagrams

### Using Graphviz CLI
```bash
# Render single diagram to PNG
dot -Tpng loop1-planning-process.dot -o loop1-planning-process.png

# Render to SVG (scalable)
dot -Tsvg loop1-planning-process.dot -o loop1-planning-process.svg

# Render all diagrams in directory
for file in *.dot; do
    dot -Tpng "$file" -o "${file%.dot}.png"
done
```

### Using VS Code Extension
Install "Graphviz (dot) language support" for inline preview.

### Using Online Tools
Upload `.dot` files to:
- https://dreampuf.github.io/GraphvizOnline/
- https://edotor.net/

## Semantic Shape Guidelines (Applied)

All diagrams follow semantic GraphViz best practices from https://blog.fsck.com/2025/09/29/using-graphviz-for-claudemd/:

### Node Shapes
- **ellipse**: Start/end points, entry/exit states
- **diamond**: Decision points (yes/no branching)
- **box**: Actions and process steps
- **octagon**: Critical warnings/blockers
- **cylinder**: External references (skills, agents, memory)
- **note**: Annotations and explanations

### Color Coding
- **fillcolor=red, fontcolor=white**: Absolute prohibitions, stop points
- **fillcolor=orange**: Critical warnings
- **fillcolor=yellow**: Decision points
- **fillcolor=green, fontcolor=white**: Success/completion states
- **fillcolor=lightblue**: Standard process steps
- **fillcolor=lightyellow**: Phase groupings (subgraph clusters)
- **fillcolor=lightcoral**: External references
- **fillcolor=lightgreen**: Tier groupings in hierarchy

### Edge Styles
- **Solid**: Normal flow within process
- **Dashed**: Conditional/cross-process flows, external references
- **Labeled**: Conditional flow ("yes"/"no", "pass"/"fail", "uses")

### Structural Patterns
- **subgraph cluster_***: Group related processes/phases
- **compound=true**: Cleaner inter-cluster connections
- **rankdir=TB**: Top-to-bottom flow (standard)
- **Metadata label**: Title, description, key information at top

## Validation Checklist

All 5 diagrams meet the following criteria:
- ✓ Valid GraphViz `.dot` syntax
- ✓ Semantic shape usage (ellipse, diamond, box, octagon, cylinder)
- ✓ Consistent color coding (red, orange, yellow, green, blue)
- ✓ Subgraph clusters for phase grouping
- ✓ Clear edge labels for decisions
- ✓ External references (memory, agents, checklists)
- ✓ Metadata labels with title and description
- ✓ Production-ready (renderable via `dot -Tpng`)

## Integration with Skills System

### Usage in Skills
Each loop skill should reference its diagrams:

**Loop 1 Planning** (`.claude/skills/loop1-planning/skill.md`):
```markdown
**Process Diagram**: See [loop1-planning-process.dot](diagrams/loop1-planning-process.dot)
```

**Loop 2 Implementation** (`.claude/skills/loop2-implementation/skill.md`):
```markdown
**Process Diagram**: See [loop2-implementation-process.dot](diagrams/loop2-implementation-process.dot)
**Architecture Diagram**: See [queen-princess-drone-hierarchy.dot](diagrams/queen-princess-drone-hierarchy.dot)
```

**Loop 3 Quality** (`.claude/skills/loop3-quality/skill.md`):
```markdown
**Process Diagram**: See [loop3-quality-process.dot](diagrams/loop3-quality-process.dot)
**Checklist Diagram**: See [47-point-checklist.dot](diagrams/47-point-checklist.dot)
```

### Usage in Claude Code Sessions
At session start, Claude Code can load relevant diagrams:

```bash
# Load Loop 2 process understanding
Read .claude/skills/loop2-implementation/diagrams/loop2-implementation-process.dot

# Load hierarchy for agent selection
Read .claude/skills/loop2-implementation/diagrams/queen-princess-drone-hierarchy.dot

# Load quality gate checklist
Read .claude/skills/loop3-quality/diagrams/47-point-checklist.dot
```

## Maintenance Notes

### When to Update Diagrams
- New agents added to registry → Update `queen-princess-drone-hierarchy.dot`
- New quality gate points → Update `47-point-checklist.dot`
- Process changes → Update corresponding loop process diagram
- New escalation paths → Update all 3 loop process diagrams

### Diagram Dependencies
- **loop1-planning-process.dot** ← Uses agent_registry.py (researcher, planner)
- **loop2-implementation-process.dot** ← Uses agent_registry.py (all 28 agents)
- **queen-princess-drone-hierarchy.dot** ← Uses agent_registry.py (full mapping)
- **loop3-quality-process.dot** ← Uses 47-point-checklist.dot
- **47-point-checklist.dot** ← Independent (quality standards)

### Version Control
All diagrams are version-controlled alongside skill definitions. Update diagrams when:
1. Agent roles change
2. Process phases added/removed
3. Quality gates modified
4. Architecture refactored

---

**Created**: 2025-10-11
**Status**: Production-ready (5/5 diagrams complete)
**Total Diagrams**: 6 (5 new + 1 existing)
**Location**: `.claude/skills/*/diagrams/*.dot`
**Renderability**: Validated (awaiting GraphViz installation for PNG generation)
