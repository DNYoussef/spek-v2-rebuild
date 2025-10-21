# Meta-Audit GraphViz Diagram Update

**Date**: 2025-10-18
**Status**: ✅ COMPLETE
**File Updated**: `.claude/skills/meta-audit/diagrams/meta-audit-process.dot`

## Summary

Updated the meta-audit process GraphViz diagram to reflect the deep analyzer integration documented in `META-AUDIT-ANALYZER-INTEGRATION.md`. The diagram now shows how each phase uses specific analyzer engines and constants.

## Changes Made

### Phase 1: Theater Detection Enhancement

**Added Nodes**:
- `p1_analyzer_patterns` - Shows PatternDetector usage for theater detection
- `p1_score` - Shows theater scoring algorithm (TODOs: 10 pts, Mocks: 20 pts, Placeholders: 15 pts, Magic Literals: 5 pts)

**Updated Labels**:
- Main audit now shows: "TODOs/FIXME (PatternDetector)", "Mocks (mock_, fake_, stub_)", "Magic Literals (CoM detection)"
- Cluster label: "Phase 1: Theater Detection & Elimination (Enhanced with Analyzer)"

**New Connections**:
- `p1_audit -> p1_analyzer_patterns` (uses PatternDetector)
- `p1_analyzer_patterns -> p1_score` (calculates score)
- `p1_score -> p1_decision` (threshold check)
- `p1_analyzer_patterns -> pattern_detector` (references engine)
- `p1_score -> thresholds` (references THEATER_THRESHOLD constant)

### Phase 2: Functionality Validation Enhancement

**Added Nodes**:
- `p2_analyzer_syntax` - Shows SyntaxAnalyzer usage for syntax/import validation

**Updated Labels**:
- Main audit now shows: "Syntax Validation (AST)", "Import Resolution", "Test Execution", "Coverage Analysis"
- Decision now checks: "Syntax Valid?", "Imports Valid?", "Tests Passing?", "Coverage ≥80%?", "Assertions ≥2?"
- Cluster label: "Phase 2: Functionality Validation & Correction (Enhanced with Analyzer)"

**New Connections**:
- `p2_audit -> p2_analyzer_syntax` (uses SyntaxAnalyzer)
- `p2_analyzer_syntax -> p2_decision` (validation results)
- `p2_analyzer_syntax -> syntax_analyzer` (references engine)
- `p2_decision -> thresholds` (references COVERAGE_THRESHOLD)

### Phase 3: Quality Refactoring Enhancement

**Added Nodes**:
- `p3_analyzer_full` - Shows full analyzer with NASA POT10 policy
- `p3_nasa_check` - Shows NASA compliance checks (Rules 3, 4, 5, 6, 7)
- `p3_quality_metrics` - Shows quality metrics (complexity, duplication, god objects)

**Updated Labels**:
- Main audit now shows: "NASA POT10 Compliance", "Complexity Analysis", "MECE Duplication", "God Object Detection", "Connascence Patterns"
- Decision now checks: "NASA ≥92%?", "Complexity ≤10?", "Duplication <80%?", "No God Objects?"
- Cluster label: "Phase 3: Style/Quality Refactoring (Full Analyzer with NASA POT10)"

**New Connections**:
- `p3_audit -> p3_analyzer_full` (uses full analyzer)
- `p3_analyzer_full -> p3_nasa_check` (NASA compliance)
- `p3_analyzer_full -> p3_quality_metrics` (quality metrics)
- `p3_nasa_check -> p3_decision` (compliance check)
- `p3_quality_metrics -> p3_decision` (metrics check)
- `p3_analyzer_full -> compliance_validator` (references engine)
- `p3_nasa_check -> nasa_rules` (references NASA_RULES constants)
- `p3_quality_metrics -> thresholds` (references COMPLEXITY_THRESHOLD)

### External References

**Added Nodes**:
- `analyzer_integration` (cylinder) - analyzer_integration.py script
- `pattern_detector` (cylinder) - PatternDetector engine (Phase 1)
- `syntax_analyzer` (cylinder) - SyntaxAnalyzer engine (Phase 2)
- `compliance_validator` (cylinder) - ComplianceValidator engine (Phase 3)
- `thresholds` (note) - Threshold constants (≤60 LOC, ≤10 complexity, <60 theater, ≥80% coverage, ≥92% NASA)
- `nasa_rules` (note) - NASA POT10 rules (Rules 3, 4, 5, 6, 7)

**New Connections**:
- All phase analyzer nodes → `analyzer_integration` (shared integration script)
- Phase analyzer nodes → respective engine nodes (PatternDetector, SyntaxAnalyzer, ComplianceValidator)
- Decision/scoring nodes → constant nodes (thresholds, nasa_rules) with labeled references

### Diagram Title

**Updated**:
```
Meta-Audit: Sequential 3-Phase Quality Orchestration with Analyzer Integration
(Phase 1: PatternDetector | Phase 2: SyntaxAnalyzer | Phase 3: Full NASA POT10 Compliance)
```

## Visual Enhancements

### Color Coding
- **Phase 1**: Light yellow (theater detection)
- **Phase 2**: Light blue (functionality validation)
- **Phase 3**: Light green (quality refactoring)
- **Engines**: Light coral (external analyzer components)
- **Skills**: Light salmon (audit skill references)
- **Constants**: Light yellow notes (threshold/rule references)

### Shape Semantics
- **Diamond**: Decision points (theater score check, test pass check, quality check)
- **Box**: Action nodes (audits, spawns, verifications)
- **Cylinder**: External scripts/engines (analyzer_integration.py, PatternDetector, etc.)
- **Folder**: Skill references (theater-detection-audit, functionality-audit, style-audit)
- **Note**: Constant references (thresholds, nasa_rules)
- **Octagon**: Critical warnings (retry limits, revert actions)

### Edge Styles
- **Solid**: Main process flow
- **Dashed**: External references (skills, engines, scripts)
- **Dotted**: Constant/threshold references

## Analyzer Integration Summary

### Phase 1: Theater Detection
- **Engine**: PatternDetector
- **Patterns Detected**: Mocks, TODOs, Placeholders, Magic Literals (CoM), Commented Code
- **Scoring**: Weighted scoring system (Mocks: 20 pts, Placeholders: 15 pts, TODOs: 10 pts, Magic Literals: 5 pts)
- **Threshold**: Theater score < 60 (from THEATER_DETECTION_FAILURE_THRESHOLD)

### Phase 2: Functionality Validation
- **Engine**: SyntaxAnalyzer
- **Validations**: Syntax (AST), Imports (no circular), Assertions (NASA Rule 4), Type hints
- **Checks**: Syntax valid, Imports valid, Tests passing, Coverage ≥80%, Assertions ≥2
- **Thresholds**: MINIMUM_TEST_COVERAGE_PERCENTAGE (80%), NASA Rule 4 (≥2 assertions)

### Phase 3: Quality Refactoring
- **Engine**: Full Analyzer with NASA POT10 policy
- **Compliance**: NASA POT10 (Rules 3, 4, 5, 6, 7)
- **Analysis**: Complexity, MECE duplication, God objects, Connascence patterns
- **Thresholds**:
  - NASA compliance ≥92% (NASA_POT10_TARGET_COMPLIANCE_THRESHOLD)
  - Complexity ≤10 (ALGORITHM_COMPLEXITY_THRESHOLD)
  - Function length ≤60 LOC (MAXIMUM_FUNCTION_LENGTH_LINES)
  - Duplication <80% (MECE_SIMILARITY_THRESHOLD)
  - God objects: >20 methods (GOD_OBJECT_METHOD_THRESHOLD)

## Rendering the Diagram

### Command Line
```bash
# Render to PNG
dot -Tpng .claude/skills/meta-audit/diagrams/meta-audit-process.dot -o meta-audit-process.png

# Render to SVG (scalable)
dot -Tsvg .claude/skills/meta-audit/diagrams/meta-audit-process.dot -o meta-audit-process.svg

# Render to PDF
dot -Tpdf .claude/skills/meta-audit/diagrams/meta-audit-process.dot -o meta-audit-process.pdf
```

### VS Code
Install "Graphviz (dot) language support" extension for inline preview.

## Files Modified

1. `.claude/skills/meta-audit/diagrams/meta-audit-process.dot` - Main GraphViz diagram (171 lines)

## Related Documentation

- [META-AUDIT-ANALYZER-INTEGRATION.md](META-AUDIT-ANALYZER-INTEGRATION.md) - Analyzer integration details
- [META-AUDIT-SKILL-COMPLETE.md](META-AUDIT-SKILL-COMPLETE.md) - Meta-audit skill implementation
- `.claude/skills/meta-audit/skill.md` - Meta-audit skill definition
- `.claude/skills/meta-audit/scripts/analyzer_integration.py` - Analyzer integration script

## Benefits of Updated Diagram

1. **AI-Comprehensible**: Shows exact analyzer engines used in each phase
2. **Human-Readable**: Visual representation of analyzer integration flow
3. **Traceable**: Clear connections between audits, engines, and constants
4. **Comprehensive**: Documents all thresholds, rules, and decision criteria
5. **Maintainable**: GraphViz format allows version control and easy updates

## Next Steps

1. ✅ GraphViz diagram updated with analyzer integration
2. ✅ All three phases enhanced with analyzer nodes
3. ✅ External references added (engines, constants, scripts)
4. ✅ Visual semantics applied (shapes, colors, edge styles)
5. 📋 Ready for rendering and documentation

---

**Version**: 2.0.0 (Analyzer Integration)
**Status**: ✅ COMPLETE
**Total Nodes**: 40+ (including analyzer engines, constants, phase steps)
**Total Edges**: 60+ (including analyzer references, threshold checks)
