# SPEK Analyzer

**Version**: 1.0 (Production-Ready)
**Status**: ✅ PRODUCTION-READY
**Test Coverage**: 125 tests (119 unit + 6 integration), 100% passing
**Performance**: <5s per file average (3.78s validated)

## Overview

The SPEK Analyzer is a production-ready code quality analysis tool with support for multiple linters (Radon + Pylint). It provides:

- **Cyclomatic complexity** metrics via Radon
- **Maintainability index** metrics via Radon
- **Logic errors and style violations** via Pylint
- **Unified interface** via linter registry pattern
- **Cross-platform compatibility** (Windows/Linux/macOS)

## Quick Start

### Installation

```bash
# Install required linters
pip install radon pylint

# Verify installation
python -m radon --version
python -m pylint --version
```

### Basic Usage

```bash
# Analyze a single file
python -c "
from pathlib import Path
from analyzer.linters import linter_registry

results = linter_registry.run_all_linters(Path('file.py'))
violations = linter_registry.aggregate_violations(results)
print(f'Violations: {len(violations)}')
"

# Run Radon complexity analysis
python -m radon cc file.py -j

# Run Pylint logic/style checks
python -m pylint file.py --output-format=json
```

## Architecture

```
analyzer/
├── core/               # Core orchestration
│   ├── api.py         # High-level API
│   ├── engine.py      # Analysis engine
│   ├── cli.py         # Command-line interface
│   ├── import_manager.py  # Module loading
│   └── fallback.py    # Graceful degradation
├── linters/           # Linter bridges (Bridge Pattern)
│   ├── base_linter.py           # Base protocol
│   ├── linter_infrastructure.py # Registry pattern
│   ├── radon_bridge.py          # Radon integration
│   └── pylint_bridge.py         # Pylint integration
├── engines/           # Specialized analyzers
│   ├── syntax_analyzer.py       # AST-based analysis
│   ├── pattern_detector.py      # Pattern detection
│   └── compliance_validator.py  # NASA Rule 10
└── constants/         # Configuration
    ├── thresholds.py            # Quality thresholds
    ├── nasa_rules.py            # NASA Rule 10 config
    ├── quality_standards.py     # File patterns
    └── ...
```

## Components

### Linter Bridges

**Radon Bridge** (`linters/radon_bridge.py`):
- Cyclomatic complexity (CC) analysis
- Maintainability index (MI) metrics
- Rank mapping (A-F scale)
- Severity conversion (critical/high/medium/low)

**Pylint Bridge** (`linters/pylint_bridge.py`):
- Logic error detection
- Style violation checking
- Fatal/error/warning classification
- PEP8-adjacent conventions

**Base Linter Protocol** (`linters/base_linter.py`):
```python
class BaseLinter(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if linter tool is available"""

    @abstractmethod
    def run(self, file_path: Path) -> dict:
        """Run linter on file, return results"""

    @abstractmethod
    def convert_to_violations(self, results: dict) -> list:
        """Convert results to Violation objects"""
```

### Linter Registry

**Registry Pattern** (`linters/linter_infrastructure.py`):
- Central linter coordination
- Lazy registration
- Multi-linter execution
- Violation aggregation

**Key Methods**:
```python
from analyzer.linters import linter_registry

# Get available linters
available = linter_registry.get_available_linters()
# Returns: ['radon', 'pylint']

# Run all linters
results = linter_registry.run_all_linters(Path('file.py'))
# Returns: {'radon': {...}, 'pylint': {...}}

# Aggregate violations
violations = linter_registry.aggregate_violations(results)
# Returns: [Violation(...), Violation(...), ...]
```

### Specialized Engines

**Syntax Analyzer** (`engines/syntax_analyzer.py`):
- AST-based function length checking (NASA Rule 10)
- Import validation
- Structure analysis

**Pattern Detector** (`engines/pattern_detector.py`):
- God object detection
- Anti-pattern identification
- Design pattern recognition

**Compliance Validator** (`engines/compliance_validator.py`):
- NASA Rule 10 compliance checking
- Custom rule validation
- Quality gate enforcement

## Design Patterns

1. **Bridge Pattern**: Decouples linter abstraction from implementation
2. **Registry Pattern**: Central linter management with lazy registration
3. **Facade Pattern**: Simple API over complex infrastructure
4. **Strategy Pattern**: Interchangeable linters for different analysis needs

## Usage Examples

### Example 1: Basic Analysis

```python
from pathlib import Path
from analyzer.linters import linter_registry

# Analyze file
results = linter_registry.run_all_linters(Path('src/module.py'))

# Get violations
violations = linter_registry.aggregate_violations(results)

# Filter by severity
critical = [v for v in violations if v.severity == 'critical']
high = [v for v in violations if v.severity == 'high']

print(f"Critical: {len(critical)}")
print(f"High: {len(high)}")
```

### Example 2: Metrics Extraction

```python
from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge

bridge = RadonBridge()
result = bridge.run(Path('src/module.py'))

if result['success'] and 'metrics' in result:
    metrics = result['metrics']
    print(f"Functions: {metrics['total_functions']}")
    print(f"Avg Complexity: {metrics['average_complexity']:.1f}")
    print(f"Avg MI: {metrics['average_mi']:.1f}")
```

### Example 3: Directory Analysis

```python
from pathlib import Path
from analyzer.linters import linter_registry

all_violations = []
for file in Path('src/').rglob('*.py'):
    results = linter_registry.run_all_linters(file)
    violations = linter_registry.aggregate_violations(results)
    all_violations.extend(violations)

print(f"Total violations: {len(all_violations)}")
```

## Interpreting Results

### Radon Ranks

| Rank | CC Range | MI Range | Assessment |
|------|----------|----------|------------|
| A | 1-5 | 80-100 | ✅ Excellent |
| B | 6-10 | 60-80 | ⚠️ Good |
| C | 11-20 | 40-60 | 🔴 Fair (consider refactoring) |
| D | 21-30 | 20-40 | 🔴 Poor (refactor soon) |
| E | 30+ | 0-20 | 🔴 Critical (refactor immediately) |

**CC** = Cyclomatic Complexity
**MI** = Maintainability Index

### Pylint Severity

| Pylint Type | Severity | Description |
|-------------|----------|-------------|
| fatal | critical | Blocking errors (syntax, imports) |
| error | high | Logic errors (undefined vars, bad logic) |
| warning | medium | Potential issues (unused vars) |
| refactor | low | Code structure suggestions |
| convention | low | Style/PEP8 issues |
| info | low | Informational messages |

## Performance

**Measured Performance** (Production Validation):
- Radon: ~1-2s per file
- Pylint: ~2-3s per file
- Combined: ~3.78s average per file
- 10 files: ~38s (sequential)
- 100 files: ~6.3 minutes (sequential)

**Optimization**:
- Use parallel execution for large codebases
- Filter files (skip tests, skip known-good files)
- Run only needed linters (Radon OR Pylint, not both)

## Testing

### Test Coverage

- **Unit Tests**: 119 tests (syntax, patterns, compliance, linters)
- **Integration Tests**: 6 tests (real linters with actual executables)
- **Total**: 125 tests, 100% passing ✅

### Run Tests

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=analyzer tests/
```

### Test Files

```
tests/
├── unit/
│   ├── core/
│   │   └── test_api.py
│   ├── engines/
│   │   ├── test_syntax_analyzer.py
│   │   ├── test_pattern_detector.py
│   │   └── test_compliance_validator.py
│   └── linters/
│       ├── test_radon_bridge.py
│       ├── test_pylint_bridge.py
│       └── test_linter_infrastructure.py
├── integration/
│   ├── test_real_linters.py
│   └── test_files/
│       ├── test_simple_clean.py
│       ├── test_complex_function.py
│       └── test_god_function.py
└── conftest.py
```

## Troubleshooting

### Linter Not Found

**Problem**: `get_available_linters()` returns `[]`

**Solution**:
```bash
pip install radon pylint
python -m radon --version
python -m pylint --version
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'analyzer'`

**Solution**:
```bash
export PYTHONPATH=$PWD:$PYTHONPATH
# or
pip install -e .
```

### Cross-Platform Issues

**Problem**: Linters work in terminal but not via analyzer

**Solution**: Analyzer uses `python -m` pattern for cross-platform compatibility. Ensure linters installed in same Python environment:
```bash
python -m pip install radon pylint
```

### Slow Analysis

**Problem**: Analysis takes >10s per file

**Solutions**:
1. Run specific linter (not all via registry)
2. Filter files (skip tests)
3. Use parallel execution (future feature)

## Development

### Sprint History

- **Sprint 1.1-1.3**: Core module refactoring (16 modules)
- **Sprint 1.4**: Constants consolidation (-1,005 LOC god object)
- **Sprint 3.1**: Radon bridge implementation (56 tests)
- **Sprint 4.1**: Integration testing + cross-platform fixes (6 tests)

### NASA Rule 10 Compliance

**Current**: 97.8% compliance (≥92% target)

**Rules**:
- ≤60 lines per function ✅
- ≥2 assertions for critical paths ✅
- No recursion ✅
- Fixed loop bounds ✅

### Code Quality Metrics (Self-Analysis)

**Production Validation** (Oct 2025):
- Files analyzed: 4 (radon_bridge, pylint_bridge, api, engine)
- Average MI: 71.7 (Rank B, good maintainability)
- Average CC: 3.7 (Rank A, excellent complexity)
- Total violations: 7 (all low-severity)

## Resources

### Documentation

- **Quick Reference**: `../docs/ANALYZER-QUICK-REFERENCE.md`
- **Full Usage Guide**: `../docs/ANALYZER-USAGE-GUIDE.md`
- **Production Validation**: `../docs/PRODUCTION-VALIDATION-COMPLETE.md`
- **Sprint Summaries**: `../docs/SPRINT-*.md`

### GraphViz Diagrams

- **Architecture**: `../.claude/processes/development/analyzer-architecture.dot`
- **Usage Workflow**: `../.claude/processes/development/analyzer-usage-workflow.dot`
- **Decision Tree**: `../.claude/processes/development/analyzer-usage-decision.dot`

### Project Documentation

- **Project Guide**: `../CLAUDE.md` (Analyzer Usage Guidelines section)
- **Architecture TOC**: `../architecture/ARCHITECTURE-MASTER-TOC.md`

## API Reference

### Linter Registry

```python
from analyzer.linters import linter_registry

# Get available linters
linters: list[str] = linter_registry.get_available_linters()

# Get linter info
info: dict = linter_registry.get_linter_info()

# Run all linters
results: dict = linter_registry.run_all_linters(file_path: Path)

# Run specific linter
result: dict = linter_registry.run_linter(name: str, file_path: Path)

# Aggregate violations
violations: list[Violation] = linter_registry.aggregate_violations(results: dict)
```

### Radon Bridge

```python
from analyzer.linters.radon_bridge import RadonBridge

bridge = RadonBridge()

# Check availability
available: bool = bridge.is_available()

# Run analysis
result: dict = bridge.run(file_path: Path)
# Returns: {'success': bool, 'violations': list, 'metrics': dict, 'linter': 'radon'}

# Convert to violations
violations: list = bridge.convert_to_violations(radon_results: dict)
```

### Pylint Bridge

```python
from analyzer.linters.pylint_bridge import PylintBridge

bridge = PylintBridge()

# Check availability
available: bool = bridge.is_available()

# Run analysis
result: dict = bridge.run(file_path: Path)
# Returns: {'success': bool, 'violations': list, 'linter': 'pylint'}

# Convert to violations
violations: list = bridge.convert_to_violations(pylint_results: list)
```

### Violation Model

```python
from analyzer.linters.base_linter import Violation

violation = Violation(
    severity='critical',        # 'critical', 'high', 'medium', 'low'
    description='High cyclomatic complexity (CC=15)',
    line_number=42,
    source='radon',            # Linter name
    recommendation='Consider refactoring to reduce complexity'
)
```

## Contributing

### Adding a New Linter

1. **Implement BaseLinter**:
   ```python
   from analyzer.linters.base_linter import BaseLinter
   from pathlib import Path

   class MyLinter(BaseLinter):
       def is_available(self) -> bool:
           # Check if linter tool is available
           pass

       def run(self, file_path: Path) -> dict:
           # Run linter, return results
           pass

       def convert_to_violations(self, results: dict) -> list:
           # Convert to Violation objects
           pass
   ```

2. **Register in Registry** (add to `linters/__init__.py`):
   ```python
   from .my_linter import MyLinter
   linter_registry.register_linter('mylinter', MyLinter())
   ```

3. **Add Tests**:
   - Unit tests: `tests/unit/linters/test_my_linter.py`
   - Integration tests: `tests/integration/test_real_linters.py`

### Testing Guidelines

- Write tests before implementation (TDD)
- Mock external tools for unit tests
- Use real tools for integration tests
- Aim for ≥80% coverage (≥90% for critical paths)
- Follow NASA Rule 10 (≤60 LOC per function)

## License

Part of the SPEK Platform v2 project. See main project LICENSE.

---

**Version**: 1.0
**Created**: 2025-10-19
**Status**: ✅ PRODUCTION-READY
**Maintainer**: SPEK Development Team
