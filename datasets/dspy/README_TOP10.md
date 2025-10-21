# DSPy Top 10 Examples - Quick Reference

## Overview

This directory contains the **top 10 examples** selected from each of the three DSPy training datasets (300 total examples → 30 selected at 10% rate) for use as demonstrations in DSPy BootstrapFewShot optimization.

## Files

| File | Size | Examples | Avg Score | Purpose |
|------|------|----------|-----------|---------|
| `queen_to_princess_dev_top10.json` | 19KB | 10 | 71.6 | Development task decomposition |
| `queen_to_princess_quality_top10.json` | 14KB | 10 | 75.7 | Quality assurance task decomposition |
| `queen_to_princess_coordination_top10.json` | 15KB | 10 | 71.0 | Coordination task decomposition |
| `SELECTION_REPORT.md` | 17KB | - | - | Detailed selection analysis |
| `VALIDATION_SUMMARY.txt` | 8KB | - | - | Validation results summary |

**Total**: 30 high-quality examples ready for DSPy training

## Selection Criteria

Examples were scored out of 100 points based on:

1. **Diversity (40%)**: Coverage of underrepresented categories
2. **Quality (25%)**: Clear tasks, realistic time estimates (15-60 min), valid dependencies
3. **Real-world (20%)**: Common patterns (OAuth, payments, migrations, APIs)
4. **Teaching (10%)**: Best practices, edge cases, security, compliance
5. **Completeness (5%)**: All required fields present

## Category Coverage

### Development Dataset (queen_to_princess_dev_top10)
- Backend systems: 4 examples (40%)
- Web development: 3 examples (30%)
- Infrastructure: 2 examples (20%)
- Security: 1 example (10%)

**Top Example**: ID 67 - CI/CD pipeline with GitHub Actions (Score: 82.0)

### Quality Dataset (queen_to_princess_quality_top10)
- Integration testing: 3 examples (30%)
- Security: 2 examples (20%)
- Unit testing: 2 examples (20%)
- Performance: 2 examples (20%)
- Compliance: 1 example (10%)

**Top Example**: ID 11 - API authentication security audit (Score: 86.0)

### Coordination Dataset (queen_to_princess_coordination_top10)
- Strategic planning: 5 examples (50%)
- Resource optimization: 3 examples (30%)
- Workflow orchestration: 1 example (10%)
- Risk management: 1 example (10%)

**Top Example**: ID 6 - CI/CD for 50-service microservices (Score: 82.0)

## Key Patterns in Top Examples

### Common Characteristics
- **Optimal complexity**: 3-5 subtasks per example
- **Realistic estimates**: All tasks 15-60 minutes
- **Dependency chains**: Logical ordering (design → code → test → review)
- **Production patterns**: OAuth, caching, migrations, security audits

### High-Value Topics
- Authentication/OAuth (appears in 6 examples across datasets)
- CI/CD and deployment (4 examples)
- Performance optimization (4 examples)
- Security audits (4 examples)
- Database operations (3 examples)

## Usage for DSPy Training

```python
import json
import dspy

# Load top 10 examples for a specific dataset
with open('datasets/dspy/queen_to_princess_dev_top10.json') as f:
    dev_top10 = json.load(f)

# Extract examples for BootstrapFewShot
demonstrations = [
    dspy.Example(
        task_description=ex['task_description'],
        objective=ex['objective'],
        expected_subtasks=ex['expected_subtasks']
    ).with_inputs('task_description', 'objective')
    for ex in dev_top10['examples']
]

# Use in BootstrapFewShot training
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(
    metric=queen_decomposition_metric,
    max_bootstrapped_demos=10,
    max_labeled_demos=10
)

optimized_queen = optimizer.compile(
    QueenAgent(),
    trainset=demonstrations
)
```

## Expected Improvements

After DSPy optimization with these demonstrations:
- **10-20%** better task decomposition quality
- **More realistic** time estimates
- **Improved** dependency ordering
- **Better** category selection for subtasks

## Next Steps

1. **Review** `SELECTION_REPORT.md` for detailed analysis of each example
2. **Load** top10 datasets into DSPy training pipeline
3. **Run** BootstrapFewShot with these demonstrations
4. **Validate** optimized agent on held-out test examples
5. **Monitor** performance on underrepresented categories

## Validation Status

✅ All 3 datasets processed successfully
✅ 30 total examples selected (10 per dataset)
✅ All examples have required fields
✅ All scores calculated and documented
✅ Category coverage meets diversity targets
✅ Selection report generated

## Quick Stats

| Metric | Value |
|--------|-------|
| Total examples analyzed | 300 |
| Total examples selected | 30 |
| Selection rate | 10% |
| Average score (dev) | 71.6 |
| Average score (quality) | 75.7 |
| Average score (coordination) | 71.0 |
| Highest score | 86.0 (Quality ID 11) |
| Lowest score | 55.1 (Coordination ID 28) |
| Unique categories covered | 13 |

---

**Generated**: 2025-10-10
**Selection Algorithm**: Weighted scoring with diversity optimization
**Ready for**: DSPy BootstrapFewShot training
