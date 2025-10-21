# Queen→Princess-Quality DSPy Training Dataset

## Overview
This dataset contains 100 training examples for optimizing how Queen decomposes quality assurance (QA) tasks for Princess-Quality coordination.

**File**: `queen_to_princess_quality.json`
**Total Examples**: 100
**Total Subtasks**: 312
**Parallel Tasks**: 306 (98.1%)
**Sequential Tasks**: 6 (1.9%)

## Dataset Structure

### Categories (100 examples)
- **Unit Testing** (30): Function tests, edge cases, mocking
- **Integration Testing** (25): API tests, E2E workflows, system integration
- **Compliance** (20): NASA rules, security standards, code quality
- **Performance** (15): Load tests, stress tests, profiling
- **Security** (10): Penetration tests, vulnerability scans

### Princess-Quality Drone Types
All subtasks delegate to `princess-quality` who manages these drones:
- **tester**: Test creation and validation (task_type: "test")
- **nasa-enforcer**: NASA Rule 10 compliance checking (task_type: "nasa-check")
- **theater-detector**: Mock code and TODO detection (task_type: "theater-detect")
- **fsm-analyzer**: FSM complexity validation (task_type: "fsm-analyze")

## Example Format

```json
{
  "id": 1,
  "category": "integration_testing",
  "task_description": "Validate OAuth2 implementation quality",
  "objective": "80% coverage, NASA compliant, zero mock code",
  "expected_subtasks": [
    {
      "princess": "princess-quality",
      "task_type": "test",
      "description": "Create auth integration tests with edge cases",
      "dependencies": [],
      "estimated_minutes": 35
    },
    {
      "princess": "princess-quality",
      "task_type": "nasa-check",
      "description": "Validate NASA Rule 10 for auth functions (≤60 LOC)",
      "dependencies": [],
      "estimated_minutes": 20
    },
    {
      "princess": "princess-quality",
      "task_type": "theater-detect",
      "description": "Scan for TODO comments and mock code",
      "dependencies": [],
      "estimated_minutes": 15
    }
  ]
}
```

## Key Patterns

### 1. Parallel Execution (98.1%)
Most tasks have empty dependencies `[]`, meaning they can run in parallel:
- Multiple test types simultaneously (unit + integration + performance)
- Compliance checks alongside functional tests
- Security scans concurrent with code validation

### 2. Sequential Dependencies (1.9%)
Few examples require sequential execution:
- Backup → Restore → Validate integrity
- Migration → Rollback → Data validation
- Recovery → RTO validation → Data loss measurement

### 3. Task Time Estimates
- **Quick tasks**: 15-25 minutes (scans, simple tests)
- **Medium tasks**: 25-40 minutes (complex tests, analysis)
- **Long tasks**: 40-60 minutes (stress tests, full system validation)

## Task Type Distribution

### Test Tasks (~60%)
- Unit testing: 30 examples
- Integration testing: 25 examples
- Performance testing: 15 examples
- Security testing: 10 examples

### Compliance Tasks (~30%)
- NASA Rule 10 checks: Throughout all categories
- Theater detection: Security and compliance categories
- FSM analysis: Compliance category
- Code quality audits: Compliance category

### Mixed Tasks (~10%)
- Combined testing + compliance
- Parallel security + performance
- Multi-phase validation workflows

## Usage for DSPy Optimization

### Training Objective
Teach Queen to:
1. **Recognize QA task patterns** from high-level descriptions
2. **Decompose into optimal subtasks** for Princess-Quality
3. **Identify parallel opportunities** (98% of tasks are parallelizable)
4. **Estimate accurate time budgets** (15-60 minute ranges)
5. **Select appropriate drone types** (test, nasa-check, theater-detect, fsm-analyze)

### Expected Improvements
- **Better task decomposition**: Recognize when to split vs combine QA tasks
- **Parallel optimization**: Maximize concurrent execution (target: >95% parallel)
- **Accurate estimation**: Better time budgets for QA workflows
- **Smart drone selection**: Choose optimal drone types for each subtask

### Evaluation Metrics
- **Decomposition accuracy**: Match expected subtask structure
- **Parallelization rate**: % of subtasks with empty dependencies
- **Time estimation error**: Difference from expected minutes
- **Drone type accuracy**: Correct task_type selection

## Common QA Workflows

### 1. Feature Quality Gate (3-5 subtasks)
```
- Unit tests (25-35 min, parallel)
- Integration tests (30-40 min, parallel)
- NASA compliance (15-25 min, parallel)
- Theater detection (15-20 min, parallel)
```

### 2. Security Audit (3-4 subtasks)
```
- Security tests (25-35 min, parallel)
- Vulnerability scan (20-30 min, parallel)
- Theater detection (15-20 min, parallel)
```

### 3. Performance Validation (3-4 subtasks)
```
- Load tests (35-50 min, parallel)
- Stress tests (40-60 min, parallel)
- NASA compliance (20-25 min, parallel)
```

### 4. Compliance Audit (4-6 subtasks)
```
- NASA checks (30-40 min, parallel)
- FSM analysis (20-30 min, parallel)
- Theater detection (20-25 min, parallel)
- Coverage validation (25-35 min, parallel)
```

## Integration with SPEK v2

### Princess-Quality Role
- **Coordinator**: Manages 4 specialized QA drones
- **Parallel executor**: Runs independent checks concurrently
- **Quality gatekeeper**: Ensures ≥80% coverage, ≥92% NASA compliance, zero theater

### Queen's Responsibilities
- **Task understanding**: Parse QA requirements from user input
- **Strategic decomposition**: Break down into optimal subtasks
- **Resource allocation**: Assign to princess-quality with accurate estimates
- **Success criteria**: Define clear objectives (coverage %, compliance %, etc.)

## Next Steps

1. **Train DSPy model** on this dataset
2. **Benchmark baseline** Queen→Princess-Quality communication
3. **Compare optimized vs baseline** decomposition quality
4. **Iterate on edge cases** based on real-world QA tasks
5. **Expand dataset** if specific patterns underperforming

---

**Version**: 1.0.0
**Created**: 2025-10-10
**Dataset**: 100 examples, 312 subtasks, 98.1% parallelizable
**Purpose**: DSPy optimization for Queen→Princess-Quality task decomposition
