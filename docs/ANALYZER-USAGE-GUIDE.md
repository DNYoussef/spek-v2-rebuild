# SPEK Analyzer Usage Guide

**Version**: 1.0 (Production-Ready)
**Last Updated**: 2025-10-19
**Status**: ✅ PRODUCTION-READY (Sprint 4.1 Complete)

## Table of Contents

1. [Quick Start](#quick-start)
2. [When to Use the Analyzer](#when-to-use-the-analyzer)
3. [Available Linters](#available-linters)
4. [Command Reference](#command-reference)
5. [Interpreting Results](#interpreting-results)
6. [Common Workflows](#common-workflows)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Architecture Overview](#architecture-overview)

## Quick Start

### Installation Verification

```bash
# Verify linters are available
python -m radon --version
python -m pylint --version

# Verify analyzer installation
python -c "from analyzer.linters import linter_registry; print(linter_registry.get_available_linters())"
```

**Expected output**: `['pylint', 'radon']`

### Run Your First Analysis

```bash
# Analyze a single file
python -m analyzer.linters.radon_bridge file.py

# Or use the registry
python -c "
from pathlib import Path
from analyzer.linters import linter_registry
results = linter_registry.run_all_linters(Path('file.py'))
print(f'Linters run: {len(results)}')
print(f'Violations: {len(linter_registry.aggregate_violations(results))}')
"
```

## When to Use the Analyzer

### Decision Tree

**START HERE**: Do you have existing/legacy code or new/greenfield code?

#### For LEGACY/EXISTING Code → Use Full Analyzer ✅

**Use cases**:
- Analyzing inherited code for refactoring
- Detecting patterns in legacy systems
- Compliance validation of existing codebases
- Quality audits across large projects

**Why**: The analyzer excels at finding complexity, maintainability issues, and violations in code that wasn't written with quality gates.

#### For NEW/GREENFIELD Code → Use Manual Validation ✅

**Use cases**:
- Code written with NASA Rule 10 compliance from start
- Test-driven development with quality built-in
- Small modules under active development

**Why**: Manual validation is faster and more direct when quality is built-in during development.

**Full Decision Workflow**: See `.claude/processes/development/analyzer-usage-workflow.dot`

## Available Linters

### 1. Radon Bridge

**Purpose**: Cyclomatic complexity + maintainability index metrics

**Metrics Provided**:
- **Cyclomatic Complexity (CC)**: Measures code complexity (1-50+)
- **Maintainability Index (MI)**: Overall maintainability score (0-100)
- **Rank**: Letter grade (A-F) for both CC and MI

**Commands**:
```bash
# Complexity analysis (JSON output)
python -m radon cc src/ -j

# Maintainability index (JSON output)
python -m radon mi src/ -j

# Via bridge (programmatic)
python -c "
from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge
bridge = RadonBridge()
result = bridge.run(Path('file.py'))
print(result['metrics'])
"
```

**Rank Mapping**:
| Rank | CC Range | MI Range | Severity |
|------|----------|----------|----------|
| A | 1-5 | 80-100 | ✅ Excellent |
| B | 6-10 | 60-80 | ⚠️ Good (low severity) |
| C | 11-20 | 40-60 | ⚠️ Fair (medium severity) |
| D | 21-30 | 20-40 | 🔴 Poor (high severity) |
| E | 30+ | 0-20 | 🔴 Critical |

**Performance**: ~1-2s per file

### 2. Pylint Bridge

**Purpose**: Logic errors + style violations

**Checks Provided**:
- Fatal errors (blocking issues)
- Logic errors (bugs, undefined variables)
- Warnings (potential issues)
- Style conventions (PEP8-adjacent)

**Commands**:
```bash
# Pylint analysis (JSON output)
python -m pylint src/ --output-format=json

# Via bridge (programmatic)
python -c "
from pathlib import Path
from analyzer.linters.pylint_bridge import PylintBridge
bridge = PylintBridge()
result = bridge.run(Path('file.py'))
print(f'Violations: {len(result[\"violations\"])}')
"
```

**Severity Mapping**:
| Pylint Type | Severity | Description |
|-------------|----------|-------------|
| fatal | critical | Blocking errors (syntax, import failures) |
| error | high | Logic errors (undefined vars, bad logic) |
| warning | medium | Potential issues (unused vars, deprecated) |
| refactor | low | Code structure suggestions |
| convention | low | Style/PEP8 issues |
| info | low | Informational messages |

**Performance**: ~2-3s per file

**Known Issue**: May produce astroid warnings on Python 3.12 `type` statements (non-blocking).

### 3. Linter Registry

**Purpose**: Coordinate multiple linters with unified interface

**Features**:
- Lazy registration (linters registered on first use)
- Automatic availability checking
- Multi-linter execution
- Violation aggregation

**Commands**:
```bash
# Get available linters
python -c "
from analyzer.linters import linter_registry
print(linter_registry.get_available_linters())
"

# Run all available linters
python -c "
from pathlib import Path
from analyzer.linters import linter_registry
results = linter_registry.run_all_linters(Path('file.py'))
violations = linter_registry.aggregate_violations(results)
print(f'Total violations: {len(violations)}')
for v in violations[:5]:
    print(f'  - {v.severity}: {v.description}')
"

# Get linter info
python -c "
from analyzer.linters import linter_registry
info = linter_registry.get_linter_info()
for name, details in info.items():
    print(f'{name}: {details}')
"
```

## Command Reference

### Basic Analysis

```bash
# Analyze single file (all linters)
python -c "
from pathlib import Path
from analyzer.linters import linter_registry
results = linter_registry.run_all_linters(Path('file.py'))
print(f'Violations: {len(linter_registry.aggregate_violations(results))}')
"

# Analyze with Radon only
python -m radon cc file.py -j  # Complexity
python -m radon mi file.py -j  # Maintainability

# Analyze with Pylint only
python -m pylint file.py --output-format=json
```

### Module/Directory Analysis

```bash
# Analyze all files in directory (Radon)
python -m radon cc src/ -j > radon_cc.json
python -m radon mi src/ -j > radon_mi.json

# Analyze all files in directory (Pylint)
python -m pylint src/ --output-format=json > pylint.json

# Programmatic directory analysis
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

for file in Path('src/').rglob('*.py'):
    results = linter_registry.run_all_linters(file)
    violations = linter_registry.aggregate_violations(results)
    if len(violations) > 0:
        print(f'{file.name}: {len(violations)} violations')
"
```

### Filtering Results

```bash
# Filter by severity
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

results = linter_registry.run_all_linters(Path('file.py'))
violations = linter_registry.aggregate_violations(results)

critical = [v for v in violations if v.severity == 'critical']
high = [v for v in violations if v.severity == 'high']

print(f'Critical: {len(critical)}')
print(f'High: {len(high)}')
"

# Filter by linter
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

results = linter_registry.run_all_linters(Path('file.py'))
radon_violations = results['radon']['violations']
pylint_violations = results['pylint']['violations']

print(f'Radon: {len(radon_violations)}')
print(f'Pylint: {len(pylint_violations)}')
"
```

### Metrics Extraction

```bash
# Extract Radon metrics
python -c "
from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge

bridge = RadonBridge()
result = bridge.run(Path('file.py'))

if result['success'] and 'metrics' in result:
    metrics = result['metrics']
    print(f'Functions: {metrics[\"total_functions\"]}')
    print(f'Avg Complexity: {metrics[\"average_complexity\"]:.1f}')
    print(f'Max Complexity: {metrics[\"max_complexity\"]}')
    print(f'Avg MI: {metrics[\"average_mi\"]:.1f}')
"
```

## Interpreting Results

### Radon Results

**Cyclomatic Complexity (CC)**:
- **1-5 (Rank A)**: Simple, easy to test ✅
- **6-10 (Rank B)**: Moderate complexity ⚠️
- **11-20 (Rank C)**: Complex, consider refactoring 🔴
- **21-30 (Rank D)**: Very complex, refactor soon 🔴🔴
- **30+ (Rank E)**: Critical complexity, refactor immediately 🔴🔴🔴

**Maintainability Index (MI)**:
- **80-100 (Rank A)**: Excellent maintainability ✅
- **60-80 (Rank B)**: Good maintainability ⚠️
- **40-60 (Rank C)**: Fair, needs improvement 🔴
- **20-40 (Rank D)**: Poor, refactor soon 🔴🔴
- **0-20 (Rank E)**: Critical, refactor immediately 🔴🔴🔴

**Example**:
```json
{
  "metrics": {
    "total_functions": 12,
    "average_complexity": 3.8,
    "max_complexity": 7,
    "average_mi": 57.7
  }
}
```

**Interpretation**:
- 12 functions analyzed
- Average CC of 3.8 (Rank A, excellent)
- Max CC of 7 (Rank B, good)
- Average MI of 57.7 (Rank B, good maintainability)

### Pylint Results

**Severity Levels**:
1. **critical**: Blocking errors (syntax, imports) - Fix immediately
2. **high**: Logic errors (undefined vars, bad types) - Fix before commit
3. **medium**: Warnings (unused vars, deprecated calls) - Fix soon
4. **low**: Style issues (line length, naming) - Fix when refactoring

**Example**:
```json
{
  "violations": [
    {
      "severity": "high",
      "description": "Undefined variable 'foo'",
      "line_number": 42,
      "source": "pylint",
      "recommendation": "Define 'foo' before use"
    }
  ]
}
```

### Combined Analysis

**Example Workflow**:
```python
from pathlib import Path
from analyzer.linters import linter_registry

file_path = Path('src/module.py')
results = linter_registry.run_all_linters(file_path)
violations = linter_registry.aggregate_violations(results)

# Count by severity
severity_counts = {}
for v in violations:
    severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

print(f"Critical: {severity_counts.get('critical', 0)}")
print(f"High: {severity_counts.get('high', 0)}")
print(f"Medium: {severity_counts.get('medium', 0)}")
print(f"Low: {severity_counts.get('low', 0)}")

# Decision logic
if severity_counts.get('critical', 0) > 0:
    print("❌ BLOCK: Critical violations found")
elif severity_counts.get('high', 0) > 0:
    print("⚠️ WARNING: High-severity violations found")
else:
    print("✅ PASS: No blocking violations")
```

## Common Workflows

### 1. CI/CD Integration

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install radon pylint
          pip install -e .

      - name: Run analyzer
        run: |
          python -c "
          from pathlib import Path
          from analyzer.linters import linter_registry

          all_violations = []
          for file in Path('src/').rglob('*.py'):
              results = linter_registry.run_all_linters(file)
              violations = linter_registry.aggregate_violations(results)
              all_violations.extend(violations)

          critical = [v for v in all_violations if v.severity == 'critical']
          high = [v for v in all_violations if v.severity == 'high']

          print(f'Total violations: {len(all_violations)}')
          print(f'Critical: {len(critical)}')
          print(f'High: {len(high)}')

          if len(critical) > 0:
              exit(1)
          "
```

### 2. Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Get staged Python files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$FILES" ]; then
    exit 0
fi

echo "Running analyzer on staged files..."

python -c "
import sys
from pathlib import Path
from analyzer.linters import linter_registry

critical_found = False

for file in sys.argv[1:]:
    if not Path(file).exists():
        continue

    print(f'Analyzing {file}...')
    results = linter_registry.run_all_linters(Path(file))
    violations = linter_registry.aggregate_violations(results)

    critical = [v for v in violations if v.severity == 'critical']
    if len(critical) > 0:
        print(f'  ❌ {len(critical)} critical violations')
        critical_found = True
    else:
        print(f'  ✅ No critical violations')

if critical_found:
    print('\\n❌ COMMIT BLOCKED: Fix critical violations first')
    sys.exit(1)
else:
    print('\\n✅ Quality check passed')
    sys.exit(0)
" $FILES

exit $?
```

### 3. Batch Analysis Script

```python
# scripts/analyze_codebase.py
from pathlib import Path
from analyzer.linters import linter_registry
import json

def analyze_codebase(source_dir: Path, output_file: Path):
    """Analyze entire codebase and generate report"""

    all_results = {}

    for file in source_dir.rglob('*.py'):
        if 'test' in file.parts or '__pycache__' in file.parts:
            continue

        print(f"Analyzing {file.relative_to(source_dir)}...")
        results = linter_registry.run_all_linters(file)
        violations = linter_registry.aggregate_violations(results)

        all_results[str(file)] = {
            'violations': len(violations),
            'critical': len([v for v in violations if v.severity == 'critical']),
            'high': len([v for v in violations if v.severity == 'high']),
            'medium': len([v for v in violations if v.severity == 'medium']),
            'low': len([v for v in violations if v.severity == 'low']),
            'details': [
                {
                    'severity': v.severity,
                    'description': v.description,
                    'line': v.line_number,
                    'source': v.source
                }
                for v in violations
            ]
        }

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nReport saved to {output_file}")

    # Summary
    total_violations = sum(r['violations'] for r in all_results.values())
    total_critical = sum(r['critical'] for r in all_results.values())
    total_high = sum(r['high'] for r in all_results.values())

    print(f"\n=== Summary ===")
    print(f"Files analyzed: {len(all_results)}")
    print(f"Total violations: {total_violations}")
    print(f"Critical: {total_critical}")
    print(f"High: {total_high}")

if __name__ == '__main__':
    analyze_codebase(Path('src/'), Path('quality_report.json'))
```

## Advanced Usage

### Custom Thresholds

```python
from analyzer.constants import thresholds

# Override thresholds for your project
thresholds.CYCLOMATIC_COMPLEXITY_THRESHOLD = 10  # More strict
thresholds.MAINTAINABILITY_INDEX_THRESHOLD = 65  # Higher bar

# Use in analysis
from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge

bridge = RadonBridge()
result = bridge.run(Path('file.py'))

# Custom violation logic
for violation in result['violations']:
    if violation.severity in ['critical', 'high']:
        print(f"BLOCKING: {violation.description}")
```

### Custom Linter

```python
from pathlib import Path
from analyzer.linters.base_linter import BaseLinter
from analyzer.linters import linter_registry

class MyCustomLinter(BaseLinter):
    """Custom linter implementation"""

    def is_available(self) -> bool:
        # Check if linter tool is available
        return True

    def run(self, file_path: Path) -> dict:
        # Run analysis
        violations = []
        # ... your analysis logic ...

        return {
            'success': True,
            'violations': violations,
            'linter': 'custom'
        }

# Register custom linter
linter_registry.register_linter('custom', MyCustomLinter())

# Use it
results = linter_registry.run_all_linters(Path('file.py'))
```

### Parallel Execution (Future)

```python
from pathlib import Path
from analyzer.linters import linter_registry
from concurrent.futures import ThreadPoolExecutor

def analyze_file(file_path: Path):
    results = linter_registry.run_all_linters(file_path)
    violations = linter_registry.aggregate_violations(results)
    return file_path, len(violations)

source_dir = Path('src/')
files = list(source_dir.rglob('*.py'))

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(analyze_file, files))

for file, violation_count in results:
    print(f"{file.name}: {violation_count} violations")
```

## Troubleshooting

### Linter Not Found

**Symptom**: `linter_registry.get_available_linters()` returns `[]`

**Solutions**:
1. **Install linters**:
   ```bash
   pip install radon pylint
   ```

2. **Verify installation**:
   ```bash
   python -m radon --version
   python -m pylint --version
   ```

3. **Check availability**:
   ```python
   from analyzer.linters.radon_bridge import RadonBridge
   bridge = RadonBridge()
   print(bridge.is_available())  # Should be True
   ```

### Cross-Platform Issues

**Symptom**: Linters work in terminal but not via analyzer

**Solution**: Analyzer uses `python -m` pattern for cross-platform compatibility. Ensure linters are installed in the same Python environment:
```bash
# Check Python executable
import sys
print(sys.executable)

# Install to correct environment
python -m pip install radon pylint
```

### Slow Analysis

**Symptom**: Analysis takes >10s per file

**Solutions**:
1. **Run specific linter** (not all):
   ```python
   from analyzer.linters.radon_bridge import RadonBridge
   bridge = RadonBridge()
   result = bridge.run(Path('file.py'))  # Faster than registry
   ```

2. **Filter files** (skip tests):
   ```python
   for file in source_dir.rglob('*.py'):
       if 'test' not in file.parts:
           # analyze
   ```

3. **Use parallel execution** (see Advanced Usage)

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'analyzer'`

**Solutions**:
1. **Add to PYTHONPATH**:
   ```bash
   export PYTHONPATH=$PWD:$PYTHONPATH
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Verify module structure**:
   ```bash
   python -c "import analyzer; print(analyzer.__file__)"
   ```

### Astroid Warnings (Python 3.12)

**Symptom**: `AttributeError: 'TreeRebuilder' object has no attribute 'visit_typealias'`

**Explanation**: Python 3.12 introduced `type` statement (PEP 695) which older astroid versions don't support.

**Impact**: Non-blocking. Pylint still produces valid results despite warnings.

**Solution** (optional):
```bash
# Upgrade Pylint/astroid
pip install --upgrade pylint astroid
```

## Architecture Overview

### Component Diagram

See `.claude/processes/development/analyzer-architecture.dot` for complete architecture visualization.

**Key Components**:
1. **Linter Bridges** (radon_bridge.py, pylint_bridge.py)
   - Implement BaseLinter protocol
   - Execute external tools via subprocess
   - Convert results to unified Violation format

2. **Linter Registry** (linter_infrastructure.py)
   - Central coordination point
   - Lazy registration pattern
   - Multi-linter execution
   - Violation aggregation

3. **Core Orchestration** (engine.py, api.py)
   - High-level analysis workflows
   - File discovery
   - Result formatting

4. **Specialized Engines** (syntax_analyzer, pattern_detector, compliance_validator)
   - AST-based analysis
   - Pattern detection
   - NASA Rule 10 compliance

**Data Flow**:
1. User calls `linter_registry.run_all_linters(file_path)`
2. Registry checks available linters
3. For each linter:
   - Bridge executes subprocess (e.g., `python -m radon cc file.py`)
   - Parse JSON results
   - Convert to Violation objects
   - Extract metrics (if available)
4. Registry aggregates all violations
5. Return combined results to user

**Design Patterns**:
- **Bridge Pattern**: Decouple linter abstraction from implementation
- **Registry Pattern**: Central linter management with lazy registration
- **Facade Pattern**: Simple API over complex infrastructure
- **Strategy Pattern**: Interchangeable linters for different analysis needs

### Performance Characteristics

**Measured Performance** (Production Validation):
- **Radon**: ~1-2s per file
- **Pylint**: ~2-3s per file
- **Combined**: ~3.78s average per file
- **Scalability**: ~38s for 10 files, ~6.3 minutes for 100 files (sequential)

**Optimization Opportunities**:
1. Parallel execution (4x speedup with 4 workers)
2. File filtering (skip tests, skip known-good files)
3. Selective linter execution (run only needed linters)
4. Caching (cache results for unchanged files)

---

## Summary

**Status**: ✅ PRODUCTION-READY

**Quick Commands**:
```bash
# Get available linters
python -c "from analyzer.linters import linter_registry; print(linter_registry.get_available_linters())"

# Analyze file
python -c "from pathlib import Path; from analyzer.linters import linter_registry; print(len(linter_registry.aggregate_violations(linter_registry.run_all_linters(Path('file.py')))))"

# Run Radon
python -m radon cc file.py -j

# Run Pylint
python -m pylint file.py --output-format=json
```

**Resources**:
- Architecture: `.claude/processes/development/analyzer-architecture.dot`
- Usage Workflow: `.claude/processes/development/analyzer-usage-workflow.dot`
- Production Validation: `docs/PRODUCTION-VALIDATION-COMPLETE.md`
- Sprint Summaries: `docs/SPRINT-*.md`

**Support**:
- Issues: Track in project issue tracker
- Questions: See CLAUDE.md for project guidance

---

**Version**: 1.0
**Created**: 2025-10-19
**Author**: Claude Sonnet 4
**Status**: ✅ PRODUCTION-READY
