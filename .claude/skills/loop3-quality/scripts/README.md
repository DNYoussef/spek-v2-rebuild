# Loop 3 Quality Scripts - Production-Ready Helper Suite

**Version**: 1.0.0
**Phase**: Loop 3 (Quality Validation)
**Total Scripts**: 5
**Total LOC**: 1,631

## Overview

Production-ready Python scripts for Loop 3 quality validation phase. Each script implements NASA Rule 10 compliance, 100% type hints, comprehensive error handling, and returns structured JSON results.

## Scripts Summary

| Script | LOC | Purpose | Key Features |
|--------|-----|---------|-------------|
| `quality_gate.py` | 331 | 47-point validation checklist | Quality scoring, category breakdown, GO/NO-GO decision |
| `integration_tester.py` | 270 | E2E test orchestration | Framework detection (Playwright/Cypress/pytest), multi-suite execution |
| `rewrite_coordinator.py` | 282 | Failure analysis & coordination | Drone selection, task generation, severity assessment |
| `deployment_approver.py` | 316 | Final deployment gate | 8-point validation, approval decision, rollback verification |
| `escalation_manager.py` | 311 | Loop 3→Loop 1 escalations | Trigger detection, context generation, rework estimation |

## 1. Quality Gate (`quality_gate.py`)

### Purpose
Validates project against 47-point quality checklist across 5 categories.

### Usage
```bash
# Run validation
python quality_gate.py --target src/

# With custom project root
python quality_gate.py --target src/ --project-root /path/to/project
```

### Output Structure
```json
{
  "success": true,
  "total_score": 92.5,
  "max_score": 100,
  "percentage": 92.5,
  "decision": "GO",
  "categories": {
    "functionality": {"score": 35, "max_score": 35, "passed_all": true},
    "code_quality": {"score": 22.5, "max_score": 25, "passed_all": false},
    "security": {"score": 15, "max_score": 15, "passed_all": true},
    "deployment": {"score": 15, "max_score": 15, "passed_all": true},
    "documentation": {"score": 10, "max_score": 10, "passed_all": true}
  },
  "timestamp": "2025-10-17T20:30:00Z"
}
```

### Categories & Weights
- **Functionality (35%)**: Tests passing, features complete, performance
- **Code Quality (25%)**: NASA compliance, linting, type hints, documentation
- **Security (15%)**: Vulnerability scans, authentication, input validation
- **Deployment (15%)**: Build success, configs, migrations, rollback plan
- **Documentation (10%)**: README, API docs, deployment guide, architecture

### Thresholds
- **GO**: ≥90% overall score
- **NO-GO**: <90% overall score

---

## 2. Integration Tester (`integration_tester.py`)

### Purpose
Orchestrates E2E and integration testing with automatic framework detection.

### Usage
```bash
# Auto-detect and run tests
python integration_tester.py --suite e2e

# Specify framework
python integration_tester.py --suite e2e --framework playwright

# Run integration tests only
python integration_tester.py --suite integration

# Run all test suites
python integration_tester.py --suite all
```

### Supported Frameworks
- **Playwright** (detected via `playwright.config.ts`)
- **Cypress** (detected via `cypress.config.ts`)
- **Pytest** (detected via `pytest.ini`)

### Output Structure
```json
{
  "success": true,
  "all_passed": true,
  "e2e": {
    "framework": "playwright",
    "passed": true,
    "return_code": 0
  },
  "integration": {
    "framework": "pytest",
    "passed": true,
    "tests_passed": 120,
    "tests_failed": 0
  },
  "timestamp": "2025-10-17T20:30:00Z"
}
```

### Integration with CI/CD
```yaml
# Example GitHub Actions usage
- name: Run E2E Tests
  run: python .claude/skills/loop3-quality/scripts/integration_tester.py --suite all
```

---

## 3. Rewrite Coordinator (`rewrite_coordinator.py`)

### Purpose
Analyzes audit failures, selects appropriate Drones, and generates rewrite task instructions.

### Usage
```bash
# Coordinate rewrites from audit results
python rewrite_coordinator.py --audit-results .claude/quality/audit_results.json

# With custom output directory
python rewrite_coordinator.py --audit-results audit.json --output-dir .claude/rewrites
```

### Failure→Drone Mapping
| Failure Type | Primary Drone | Backup Drones |
|-------------|---------------|---------------|
| Functionality | `debugger` | `coder`, `tester` |
| Style | `reviewer` | `coder` |
| Theater | `coder` | `reviewer` |
| Security | `security-manager` | `coder` |
| Performance | `performance-engineer` | `coder` |

### Output Structure
```json
{
  "success": true,
  "coordination": {
    "failure_analysis": {
      "failures": [
        {"type": "functionality", "severity": "critical"},
        {"type": "style", "severity": "medium"}
      ],
      "failure_count": 2,
      "requires_rewrites": true
    },
    "drone_selection": {
      "assignments": [
        {"primary_drone": "debugger", "estimated_hours": 8},
        {"primary_drone": "reviewer", "estimated_hours": 2}
      ]
    },
    "rewrite_tasks": {
      "tasks_file": ".claude/rewrites/rewrite_tasks.json",
      "total_tasks": 2
    }
  },
  "requires_action": true,
  "message": "2 rewrite tasks created"
}
```

### Severity Levels
- **Critical**: Functionality, Security (8 hours estimate)
- **High**: Performance (4 hours estimate)
- **Medium**: Style, Theater (2 hours estimate)
- **Low**: Other (1 hour estimate)

---

## 4. Deployment Approver (`deployment_approver.py`)

### Purpose
Final validation gate before production deployment with 8-point checklist.

### Usage
```bash
# Run full validation
python deployment_approver.py --validate-all

# With custom quality/test results
python deployment_approver.py \
  --quality-results .claude/quality/quality_gate_report.json \
  --test-results test-results/integration.json
```

### Validation Requirements
1. **Quality Gate**: ≥90% score
2. **All Tests**: 100% pass rate
3. **Security Scan**: Zero critical vulnerabilities
4. **Production Build**: Successful build artifacts
5. **Documentation**: Complete deployment docs
6. **Rollback Plan**: Documented procedure
7. **Monitoring**: Configured and tested
8. **Environment**: Validated configuration

### Output Structure
```json
{
  "success": true,
  "decision": "APPROVED",
  "all_passed": true,
  "passed_count": 8,
  "total_count": 8,
  "percentage": 100,
  "validations": {
    "quality_gate": {"passed": true, "score": 95},
    "all_tests": {"passed": true},
    "security_scan": {"passed": true, "critical_issues": 0},
    "production_build": {"passed": true},
    "documentation": {"passed": true, "missing": []},
    "rollback_plan": {"passed": true},
    "monitoring": {"passed": true},
    "environment": {"passed": true}
  },
  "timestamp": "2025-10-17T20:30:00Z"
}
```

### Decisions
- **APPROVED**: All 8 validations passed
- **REJECTED**: Any validation failed

---

## 5. Escalation Manager (`escalation_manager.py`)

### Purpose
Manages critical escalations from Loop 3 (validation) back to Loop 1 (planning) with 3-strike rule.

### Usage
```bash
# Check escalation triggers
python escalation_manager.py --failure-data .claude/quality/validation_data.json

# Create escalation
python escalation_manager.py --create-escalation --validation-data validation.json
```

### Escalation Triggers
| Trigger | Threshold | Severity |
|---------|-----------|----------|
| Quality Gate Critical Failure | <50% score | Critical |
| Security Vulnerabilities | ≥1 critical | Critical |
| Architecture Issues | ≥3 major | High |
| Performance Failures | ≥5 regressions | High |
| Test Failures Persistent | ≥10% failing | Medium |

### Output Structure
```json
{
  "success": true,
  "requires_escalation": true,
  "escalation": {
    "escalation_id": "ESC20251017203000",
    "timestamp": "2025-10-17T20:30:00Z",
    "from_loop": 3,
    "to_loop": 1,
    "severity": "critical",
    "triggers": [
      {"trigger": "quality_gate_critical_failure", "value": 45, "threshold": 50}
    ],
    "required_actions": [
      "Re-evaluate quality standards and requirements",
      "Revise implementation plan to improve quality"
    ],
    "estimated_rework": "Moderate rework (2-4 weeks)"
  },
  "escalation_file": ".claude/escalations/escalation_ESC20251017203000.json",
  "loop1_instruction": "ESCALATION FROM LOOP 3 TO LOOP 1\n..."
}
```

### Rework Estimates
- **Major**: 4-8 weeks (≥2 critical triggers)
- **Moderate**: 2-4 weeks (1 critical trigger)
- **Minor**: 1-2 weeks (no critical triggers)

---

## Complete Workflow Example

### 1. Run Quality Gate
```bash
python quality_gate.py --target src/
# Output: .claude/quality/quality_gate_report.md
```

### 2. Run Integration Tests
```bash
python integration_tester.py --suite all
# Output: test-results/integration.json
```

### 3. Check Deployment Approval
```bash
python deployment_approver.py --validate-all
# Output: .claude/approvals/deployment_approval.json
```

### 4. If Failures, Coordinate Rewrites
```bash
python rewrite_coordinator.py --audit-results .claude/quality/audit_results.json
# Output: .claude/rewrites/rewrite_tasks.json
```

### 5. If Critical Failures, Escalate
```bash
python escalation_manager.py --create-escalation --validation-data validation.json
# Output: .claude/escalations/escalation_*.json
```

---

## Integration Points

### With Loop3 Audit Runner
```python
from quality_gate import QualityGate
from integration_tester import IntegrationTester
from rewrite_coordinator import RewriteCoordinator
from deployment_approver import DeploymentApprover
from escalation_manager import EscalationManager

# Step 1: Quality Gate
gate = QualityGate()
quality_results = gate.run_full_validation(category_results)

# Step 2: Integration Tests
tester = IntegrationTester()
test_results = tester.run_all_tests()

# Step 3: Deployment Approval
approver = DeploymentApprover()
approval = approver.run_full_validation(quality_results, test_results)

# Step 4: Check for Escalation
if not approval["all_passed"]:
    manager = EscalationManager()
    escalation = manager.create_escalation(validation_data)

    if escalation["requires_escalation"]:
        print(escalation["loop1_instruction"])
```

### With CI/CD Pipeline
```yaml
name: Loop 3 Quality Validation

on: [push, pull_request]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Quality Gate
        run: python .claude/skills/loop3-quality/scripts/quality_gate.py --target src/

      - name: Run Integration Tests
        run: python .claude/skills/loop3-quality/scripts/integration_tester.py --suite all

      - name: Check Deployment Approval
        run: python .claude/skills/loop3-quality/scripts/deployment_approver.py --validate-all

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: quality-reports
          path: .claude/quality/
```

---

## File Structure

```
.claude/skills/loop3-quality/scripts/
├── quality_gate.py           # 331 LOC
├── integration_tester.py     # 270 LOC
├── rewrite_coordinator.py    # 282 LOC
├── deployment_approver.py    # 316 LOC
├── escalation_manager.py     # 311 LOC
└── README.md                 # This file

Generated outputs:
├── .claude/quality/
│   └── quality_gate_report.md
├── .claude/rewrites/
│   └── rewrite_tasks.json
├── .claude/approvals/
│   └── deployment_approval.json
└── .claude/escalations/
    └── escalation_*.json
```

---

## Requirements

### Python Dependencies
```txt
# No external dependencies required
# All scripts use Python 3.8+ standard library only
```

### System Requirements
- Python 3.8+
- Git (for version control checks)
- npm/npx (for E2E framework execution)
- pytest (for Python tests)

### Optional Tools
- Playwright (for E2E tests)
- Cypress (for E2E tests)
- mypy (for type checking)
- bandit (for security scanning)

---

## Quality Standards

### NASA Rule 10 Compliance
- ✅ All functions ≤60 LOC
- ✅ No recursion
- ✅ Fixed loop bounds
- ✅ ≥2 assertions per critical path

### Type Safety
- ✅ 100% type hints on all functions
- ✅ All return types declared
- ✅ Dict[str, Any] for complex structures

### Error Handling
- ✅ All exceptions caught and returned as structured errors
- ✅ Timeout protection on subprocess calls
- ✅ File existence validation before operations

### Documentation
- ✅ Full docstrings on all functions
- ✅ Usage examples in main blocks
- ✅ Comprehensive README (this file)

---

## Maintenance

### Adding New Checks
1. Extend checklist in `quality_gate.py::CHECKLIST`
2. Add validation method following pattern: `validate_<check_name>()`
3. Update `run_full_validation()` to include new check
4. Update this README with new check details

### Adding New Escalation Triggers
1. Add trigger to `escalation_manager.py::ESCALATION_TRIGGERS`
2. Implement detection logic in `check_escalation_triggers()`
3. Add action mapping in `_determine_required_actions()`
4. Update this README with trigger details

### Testing Scripts
```bash
# Unit test all scripts
pytest tests/test_loop3_scripts.py -v

# Integration test full workflow
python tests/integration/test_loop3_workflow.py
```

---

## Troubleshooting

### Quality Gate Reports NO-GO
1. Check individual category scores
2. Run failed checks manually for detailed output
3. Review `.claude/quality/quality_gate_report.md` for specifics
4. Coordinate rewrites using `rewrite_coordinator.py`

### Integration Tests Failing
1. Verify test framework installed (`npx playwright --version`)
2. Check test directory structure (`tests/e2e/`, `tests/integration/`)
3. Run tests manually: `npx playwright test` or `pytest tests/`
4. Review test output in `test-results/`

### Deployment Approval Rejected
1. Check which validation failed in approval results
2. Review logs for specific error details
3. Verify required files exist (docs, configs, builds)
4. Re-run individual validators for more detail

### Escalation Not Triggering
1. Verify validation data structure matches expected format
2. Check trigger thresholds in `ESCALATION_TRIGGERS`
3. Review severity levels of failures
4. Manually check triggers: `manager.check_escalation_triggers(data)`

---

## Support

**Issues**: Report to Queen agent via `.claude_messages/`
**Documentation**: See `docs/WEEK-26-FINAL-COMPLETION.md`
**Architecture**: See `architecture/ARCHITECTURE-MASTER-TOC.md`

---

**Last Updated**: 2025-10-17
**Status**: Production-Ready
**Version**: 1.0.0
**NASA Compliance**: 100%
**Type Coverage**: 100%
