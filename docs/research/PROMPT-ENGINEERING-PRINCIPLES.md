# Prompt Engineering Principles for DSPy Integration

**COMPREHENSIVE GUIDE**: Best Practices for Effective DSPy Optimization

---

## Executive Summary

This document outlines **26 proven prompt engineering principles** and demonstrates how to apply them within DSPy signatures for the SPEK Platform v8 agent optimization.

**Key Insight**: DSPy automates prompt engineering, but **starting with well-designed signatures dramatically improves optimization results**.

---

## Core Prompt Engineering Principles

### 1. Clarity & Specificity

**Principle**: Be explicit about what you want, avoiding ambiguity.

**Bad Example**:
```python
class TaskDecomposition(dspy.Signature):
    task = dspy.InputField()
    result = dspy.OutputField()
```

**Good Example (DSPy)**:
```python
class TaskDecomposition(dspy.Signature):
    """Break down a complex software development task into specific,
    actionable subtasks with clear agent assignments and execution order."""

    task_description: str = dspy.InputField(
        desc="Detailed description of the complex task to decompose, "
             "including requirements, constraints, and expected outcomes"
    )
    project_context: str = dspy.InputField(
        desc="Relevant project context: tech stack, existing architecture, "
             "team capabilities, and timeline constraints"
    )

    subtasks: list[dict] = dspy.OutputField(
        desc="Ordered list of subtasks, each with: "
             "{'agent': str, 'task_type': str, 'description': str, "
             "'dependencies': list[str], 'estimated_minutes': int}"
    )
```

### 2. Role Assignment (Persona)

**Principle**: Assign a specific role/expertise to guide behavior.

**DSPy Implementation**:
```python
class CodeReview(dspy.Signature):
    """You are a senior software engineer with 10+ years of experience
    in Python, security best practices, and code quality standards.
    Your specialty is identifying subtle bugs, security vulnerabilities,
    and architectural issues that junior developers might miss.

    Review the provided code with the rigor of a production deployment,
    focusing on: security, correctness, maintainability, and performance."""

    code_snippet: str = dspy.InputField(
        desc="Python code to review (may include security vulnerabilities)"
    )
    context: str = dspy.InputField(
        desc="Purpose of this code and how it fits in the larger system"
    )

    issues: list[dict] = dspy.OutputField(
        desc="List of issues found, each with: "
             "{'severity': 'critical'|'high'|'medium'|'low', "
             "'type': 'security'|'correctness'|'style'|'performance', "
             "'line': int, 'description': str, 'fix_suggestion': str}"
    )
    security_score: int = dspy.OutputField(
        desc="Security rating from 0-100 (100 = no vulnerabilities)"
    )
```

### 3. Step-by-Step Reasoning (Chain of Thought)

**Principle**: Request explicit reasoning steps before final answer.

**DSPy Implementation** (Built-in with ChainOfThought):
```python
class TestGeneration(dspy.Signature):
    """Generate comprehensive test cases for a given function.

    Think through this step-by-step:
    1. Analyze the function signature and understand inputs/outputs
    2. Identify the happy path (expected normal usage)
    3. Consider edge cases (empty inputs, boundary values, special chars)
    4. Think about error cases (invalid inputs, exceptions)
    5. Consider security implications (injection, overflow, etc.)
    6. Generate test cases covering all scenarios"""

    function_code: str = dspy.InputField()
    function_name: str = dspy.InputField()

    test_cases: list[dict] = dspy.OutputField(
        desc="Test cases with: {'name': str, 'type': 'happy'|'edge'|'error'|'security', "
             "'input': dict, 'expected_output': any, 'rationale': str}"
    )

# Use ChainOfThought to enforce reasoning
tester = dspy.ChainOfThought(TestGeneration)
```

### 4. Examples (Few-Shot Learning)

**Principle**: Provide concrete examples of desired behavior.

**DSPy Implementation** (Automated via BootstrapFewShot):
```python
# Training examples with high-quality labels
examples = [
    dspy.Example(
        function_code='''
def login(email, password):
    user = db.query(f"SELECT * FROM users WHERE email='{email}'")
    return user.password == password
        ''',
        function_name="login",
        test_cases=[
            {
                "name": "test_sql_injection_attack",
                "type": "security",
                "input": {"email": "admin' OR '1'='1", "password": "anything"},
                "expected_output": "Should raise SecurityError or return False",
                "rationale": "Prevent SQL injection via email parameter"
            },
            {
                "name": "test_plaintext_password_comparison",
                "type": "security",
                "input": {"email": "user@test.com", "password": "pass123"},
                "expected_output": "Should use bcrypt.checkpw, not ==",
                "rationale": "Password should be hashed, not compared as plaintext"
            }
        ]
    ).with_inputs('function_code', 'function_name'),
    # More examples...
]

# BootstrapFewShot automatically selects best examples
optimizer = dspy.BootstrapFewShot(metric=test_quality_metric)
optimized_tester = optimizer.compile(tester, trainset=examples)
```

### 5. Output Format Specification

**Principle**: Explicitly define expected output structure.

**DSPy Implementation**:
```python
class CodeGeneration(dspy.Signature):
    """Generate production-ready Python code based on specification."""

    specification: str = dspy.InputField(
        desc="Detailed functional specification with requirements"
    )

    code: str = dspy.OutputField(
        desc="Complete Python code with:\n"
             "- Docstring describing function purpose\n"
             "- Type hints for all parameters and return value\n"
             "- Input validation with clear error messages\n"
             "- Proper error handling (try/except where appropriate)\n"
             "- No function longer than 60 lines (NASA Rule 10)\n"
             "- Comments explaining complex logic\n"
             "Example format:\n"
             "def function_name(param: str) -> bool:\n"
             "    '''Docstring here.'''\n"
             "    if not param:\n"
             "        raise ValueError('param required')\n"
             "    # Implementation\n"
             "    return True"
    )
    nasa_compliant: bool = dspy.OutputField(
        desc="True if all functions ≤60 lines, False otherwise"
    )
    type_safety_score: int = dspy.OutputField(
        desc="0-100 score for type hint coverage (100 = all params/returns typed)"
    )
```

### 6. Constraints & Boundaries

**Principle**: Set clear limits and requirements upfront.

**DSPy Implementation**:
```python
class WorkflowOrchestration(dspy.Signature):
    """Orchestrate multi-agent workflow for software development task.

    CONSTRAINTS:
    - Maximum 10 subtasks (if more needed, break into phases)
    - Each subtask must complete in ≤60 minutes
    - Total workflow duration ≤8 hours
    - No subtask can depend on more than 3 prior subtasks
    - Must include at least one quality gate (review or test)

    REQUIREMENTS:
    - All subtasks must have explicit agent assignments
    - Execution order must respect dependencies
    - Must include error handling strategy
    - Security review required for any auth/payment code"""

    task_description: str = dspy.InputField()
    urgency: str = dspy.InputField(desc="low|medium|high|critical")

    workflow: dict = dspy.OutputField(
        desc="{'subtasks': [...], 'total_duration_minutes': int, "
             "'quality_gates': [...], 'rollback_strategy': str}"
    )
```

### 7. Context Provision

**Principle**: Provide relevant background information.

**DSPy Implementation**:
```python
class ArchitectureDesign(dspy.Signature):
    """Design system architecture for a software feature.

    CONTEXT:
    - This is for a multi-tenant SaaS platform
    - Current stack: Python/FastAPI backend, React frontend, PostgreSQL
    - Traffic: ~100K requests/day, growing 20%/month
    - Team: 5 developers, 2 junior (need maintainable code)
    - Deployment: Kubernetes on AWS
    - Budget: Cost-conscious (prefer managed services)"""

    feature_specification: str = dspy.InputField()
    scale_requirements: dict = dspy.InputField(
        desc="{'users': int, 'requests_per_day': int, 'data_size_gb': int}"
    )

    architecture: dict = dspy.OutputField(
        desc="{'components': [...], 'data_flow': str, 'scalability_plan': str, "
             "'cost_estimate': str, 'deployment_strategy': str}"
    )
```

### 8. Error Prevention

**Principle**: Anticipate and prevent common mistakes.

**DSPy Implementation**:
```python
class BugFix(dspy.Signature):
    """Generate a bug fix for the provided code issue.

    COMMON MISTAKES TO AVOID:
    - Don't just suppress errors with try/except pass
    - Don't introduce new bugs while fixing the original issue
    - Don't break existing functionality (check for regressions)
    - Don't leave debug code (print statements, commented code)
    - Don't use hardcoded values (use config/constants)
    - Don't skip input validation

    VERIFICATION CHECKLIST:
    ✓ Fix addresses root cause (not just symptoms)
    ✓ Added test case to prevent regression
    ✓ No new security vulnerabilities introduced
    ✓ Code follows project style guide
    ✓ Function still ≤60 lines (NASA Rule 10)"""

    bug_description: str = dspy.InputField()
    existing_code: str = dspy.InputField()
    stack_trace: str = dspy.InputField(desc="Error stack trace if available")

    fixed_code: str = dspy.OutputField(desc="Corrected code")
    root_cause: str = dspy.OutputField(desc="Explanation of what caused the bug")
    regression_test: str = dspy.OutputField(desc="Test case to prevent this bug in future")
```

### 9. Incremental Prompting

**Principle**: Break complex tasks into smaller steps.

**DSPy Implementation** (Multi-stage pipeline):
```python
# Stage 1: Understand requirements
class RequirementAnalysis(dspy.Signature):
    """Analyze and clarify software requirements."""
    raw_requirements: str = dspy.InputField()
    clarified_requirements: dict = dspy.OutputField()

# Stage 2: Design solution
class SolutionDesign(dspy.Signature):
    """Design solution based on clarified requirements."""
    requirements: dict = dspy.InputField()
    design: dict = dspy.OutputField()

# Stage 3: Generate code
class CodeImplementation(dspy.Signature):
    """Implement code based on design."""
    design: dict = dspy.InputField()
    code: str = dspy.OutputField()

# Pipeline
class FeatureImplementationPipeline(dspy.Module):
    def __init__(self):
        self.analyze = dspy.ChainOfThought(RequirementAnalysis)
        self.design = dspy.ChainOfThought(SolutionDesign)
        self.implement = dspy.ChainOfThought(CodeImplementation)

    def forward(self, raw_requirements):
        requirements = self.analyze(raw_requirements=raw_requirements)
        design = self.design(requirements=requirements.clarified_requirements)
        code = self.implement(design=design.design)
        return code
```

### 10. Avoid Leading Questions

**Principle**: Don't bias the model toward a specific answer.

**Bad Example**:
```python
class SecurityAudit(dspy.Signature):
    """This code looks secure, right? Just confirm it's safe."""
    code: str = dspy.InputField()
    is_secure: bool = dspy.OutputField()  # Biased toward True
```

**Good Example**:
```python
class SecurityAudit(dspy.Signature):
    """Perform objective security audit of the provided code.
    Identify ALL vulnerabilities regardless of severity.
    Be thorough and critical - assume code is insecure until proven otherwise."""

    code: str = dspy.InputField()
    vulnerabilities: list[dict] = dspy.OutputField(
        desc="All vulnerabilities found (empty list if none)"
    )
    overall_rating: str = dspy.OutputField(
        desc="'secure'|'moderate_risk'|'high_risk'|'critical_risk'"
    )
```

### 11-26: Additional Principles

#### 11. Positive Instructions
✅ **Do**: "Generate type-safe code with hints"
❌ **Don't**: "Don't forget type hints"

#### 12. Prioritization
Specify what's most important: "Prioritize security over performance"

#### 13. Edge Case Handling
Explicitly request edge case consideration

#### 14. Consistency
Use consistent terminology across all signatures

#### 15. Domain Knowledge
Embed domain-specific knowledge in docstrings

#### 16. Reasoning Transparency
Ask for explanations: "Explain why you chose this approach"

#### 17. Self-Correction
"Review your output and identify potential improvements"

#### 18. Comparative Analysis
"Compare option A vs option B, list pros/cons"

#### 19. Uncertainty Acknowledgment
"If uncertain, state assumptions and confidence level"

#### 20. Versioning
"Generate backward-compatible code (support Python 3.9+)"

#### 21. Performance Awareness
"Optimize for O(n) complexity, avoid O(n²)"

#### 22. Resource Limits
"Solution must use <1GB RAM and complete in <5s"

#### 23. Regulatory Compliance
"Code must comply with GDPR, log all data access"

#### 24. Testing Requirements
"Include unit tests with ≥80% coverage"

#### 25. Documentation
"Add docstrings following Google Python Style Guide"

#### 26. Accessibility
"Ensure output is human-readable and maintainable"

---

## Applied DSPy Examples with All Principles

### Complete Queen Agent Example

```python
import dspy

class TaskDecompositionSignature(dspy.Signature):
    """You are an expert software project manager with 15+ years of experience
    leading agile development teams. Your specialty is breaking down complex
    software projects into clear, actionable work items that can be executed
    by specialized team members.

    ROLE: Senior Engineering Manager
    EXPERTISE: Agile, SDLC, Team Coordination, Risk Management

    TASK: Decompose a complex software development task into specific subtasks
    with clear agent assignments, proper sequencing, and realistic time estimates.

    REASONING PROCESS (think through step-by-step):
    1. Understand the overall objective and success criteria
    2. Identify all required capabilities (coding, testing, review, deployment)
    3. Determine dependencies between subtasks
    4. Assign appropriate agent to each subtask based on expertise
    5. Estimate realistic duration considering complexity and dependencies
    6. Add quality gates (review, testing, security validation)
    7. Plan for error handling and rollback

    CONSTRAINTS:
    - Maximum 10 subtasks (break into phases if more needed)
    - Each subtask: 15-60 minutes duration
    - Total workflow: ≤8 hours
    - Maximum 3 dependencies per subtask
    - Must include ≥1 quality gate (review OR test)
    - Must include error handling strategy
    - Security review required for auth/payment/data-access code

    OUTPUT REQUIREMENTS:
    - Clear, specific task descriptions (not vague like "implement feature")
    - Realistic time estimates based on complexity
    - Explicit dependency declarations
    - Appropriate agent selection (don't assign testing to coder)

    COMMON MISTAKES TO AVOID:
    - Skipping validation/testing phases
    - Underestimating time for complex tasks
    - Circular dependencies
    - Missing security considerations
    - Assigning wrong agent type to task
    - No rollback/error recovery plan

    QUALITY CHECKLIST:
    ✓ All subtasks have clear, measurable outcomes
    ✓ Dependencies are acyclic (no circular deps)
    ✓ Time estimates sum to realistic total
    ✓ Quality gates included (≥1)
    ✓ Error handling strategy defined
    ✓ Security review for sensitive code"""

    # INPUTS
    task_description: str = dspy.InputField(
        desc="Detailed description of the complex task, including:\n"
             "- What needs to be built/fixed\n"
             "- Success criteria (how do we know it's done?)\n"
             "- Constraints (performance, security, compatibility)\n"
             "- Context (existing system, tech stack, team)"
    )

    project_context: dict = dspy.InputField(
        desc="Project metadata:\n"
             "{'tech_stack': ['Python', 'FastAPI', 'React'],\n"
             " 'team_size': 5,\n"
             " 'urgency': 'high'|'medium'|'low',\n"
             " 'existing_components': [...],\n"
             " 'constraints': {'budget': str, 'timeline': str}}"
    )

    available_agents: list[str] = dspy.InputField(
        desc="List of available agent types:\n"
             "['spec-writer', 'architect', 'coder', 'tester', 'reviewer',\n"
             " 'debugger', 'security-manager', 'devops', 'integration-engineer']"
    )

    # OUTPUTS
    subtasks: list[dict] = dspy.OutputField(
        desc="Ordered list of subtasks to execute. Each subtask MUST have:\n"
             "{\n"
             "  'id': str,  # Unique identifier like 'task-001'\n"
             "  'agent': str,  # From available_agents list\n"
             "  'task_type': str,  # E.g., 'write-spec', 'implement', 'test', 'review'\n"
             "  'description': str,  # Specific, actionable description (not vague!)\n"
             "  'dependencies': list[str],  # IDs of tasks that must complete first\n"
             "  'estimated_minutes': int,  # Realistic estimate (15-60)\n"
             "  'success_criteria': str,  # How do we verify this is done?\n"
             "  'risk_level': 'low'|'medium'|'high'  # Complexity/uncertainty\n"
             "}\n"
             "Example:\n"
             "{\n"
             "  'id': 'task-003',\n"
             "  'agent': 'coder',\n"
             "  'task_type': 'implement',\n"
             "  'description': 'Implement JWT token generation with 1-hour expiry',\n"
             "  'dependencies': ['task-001', 'task-002'],  # Spec and design\n"
             "  'estimated_minutes': 45,\n"
             "  'success_criteria': 'Function generates valid JWT, expires after 1hr',\n"
             "  'risk_level': 'medium'\n"
             "}"
    )

    quality_gates: list[dict] = dspy.OutputField(
        desc="Quality checkpoints (minimum 1 required). Each gate:\n"
             "{\n"
             "  'type': 'code_review'|'testing'|'security_audit'|'integration_test',\n"
             "  'agent': str,  # E.g., 'reviewer', 'tester', 'security-manager'\n"
             "  'after_task': str,  # Task ID this gate follows\n"
             "  'acceptance_criteria': str  # What must pass?\n"
             "}"
    )

    error_handling: dict = dspy.OutputField(
        desc="Error handling and rollback strategy:\n"
             "{\n"
             "  'rollback_plan': str,  # How to revert if deployment fails\n"
             "  'monitoring': str,  # What metrics to watch\n"
             "  'alerts': str,  # When to alert team\n"
             "  'fallback_option': str  # Alternative approach if primary fails\n"
             "}"
    )

    metadata: dict = dspy.OutputField(
        desc="Workflow metadata:\n"
             "{\n"
             "  'total_duration_minutes': int,  # Sum of all subtask estimates\n"
             "  'critical_path': list[str],  # Task IDs on longest dependency chain\n"
             "  'parallelizable_tasks': list[list[str]],  # Groups that can run in parallel\n"
             "  'confidence': 'high'|'medium'|'low',  # Confidence in estimates\n"
             "  'assumptions': list[str]  # Key assumptions made\n"
             "}"
    )


class QueenModule(dspy.Module):
    """Queen agent orchestration with chain-of-thought reasoning."""

    def __init__(self):
        super().__init__()
        # ChainOfThought enforces step-by-step reasoning
        self.decompose = dspy.ChainOfThought(TaskDecompositionSignature)

    def forward(self, task_description, project_context, available_agents):
        """
        Decompose complex task into subtasks.

        Returns:
            Prediction with: subtasks, quality_gates, error_handling, metadata
        """
        result = self.decompose(
            task_description=task_description,
            project_context=project_context,
            available_agents=available_agents
        )

        return result


# Evaluation metric with prompt engineering principles
def task_decomposition_metric(example, prediction, trace=None):
    """
    Evaluate quality of task decomposition.

    Criteria:
    1. Agent selection accuracy (30%): Correct agent for each subtask
    2. Dependency correctness (25%): No circular deps, valid task IDs
    3. Completeness (25%): All necessary subtasks present
    4. Time estimate realism (10%): Neither too optimistic nor pessimistic
    5. Quality gates present (10%): At least one quality checkpoint

    Returns:
        float: Score from 0.0 to 1.0
    """
    gold = example.subtasks
    pred = prediction.subtasks

    # 1. Agent selection accuracy (30%)
    correct_agents = 0
    for g, p in zip(gold, pred):
        if g.get('agent') == p.get('agent'):
            correct_agents += 1
    agent_accuracy = (correct_agents / len(gold)) * 0.30 if gold else 0

    # 2. Dependency correctness (25%)
    # Check no circular dependencies
    has_circular = False
    task_ids = {t['id'] for t in pred}
    for task in pred:
        deps = task.get('dependencies', [])
        # Simple circular check: task can't depend on itself
        if task['id'] in deps:
            has_circular = True
            break
        # All dependencies must be valid task IDs
        if not all(dep in task_ids for dep in deps):
            has_circular = True
            break

    dependency_score = 0.0 if has_circular else 0.25

    # 3. Completeness (25%)
    # Prediction should have at least as many tasks as gold
    completeness = min(len(pred) / len(gold), 1.0) * 0.25 if gold else 0

    # 4. Quality gates (10%)
    has_quality_gates = len(prediction.quality_gates) >= 1
    quality_gate_score = 0.10 if has_quality_gates else 0.0

    # 5. Error handling (10%)
    has_error_handling = bool(prediction.error_handling.get('rollback_plan'))
    error_handling_score = 0.10 if has_error_handling else 0.0

    # Total score
    total = (
        agent_accuracy +
        dependency_score +
        completeness +
        quality_gate_score +
        error_handling_score
    )

    return total


# Training example with high-quality annotation
def create_queen_training_examples():
    """Create training examples with all prompt engineering principles."""

    example1 = dspy.Example(
        task_description=(
            "Implement a user authentication system with email/password login, "
            "session management, and password reset functionality. "
            "MUST be secure (no SQL injection, passwords hashed with bcrypt, "
            "rate limiting on login attempts). "
            "Success criteria: Users can register, login, logout, and reset password. "
            "Constraints: <100ms login latency, GDPR compliant (log all auth events)."
        ),
        project_context={
            'tech_stack': ['Python', 'FastAPI', 'PostgreSQL', 'Redis'],
            'team_size': 5,
            'urgency': 'high',
            'existing_components': ['user_model', 'database_connection'],
            'constraints': {'budget': 'cost-conscious', 'timeline': '3 days'}
        },
        available_agents=[
            'spec-writer', 'architect', 'coder', 'tester',
            'reviewer', 'security-manager', 'devops'
        ],
        # GOLD LABELS (expected output)
        subtasks=[
            {
                'id': 'task-001',
                'agent': 'spec-writer',
                'task_type': 'write-spec',
                'description': 'Document authentication requirements: registration flow, login flow, password reset flow, security requirements (bcrypt, rate limiting, GDPR logging)',
                'dependencies': [],
                'estimated_minutes': 30,
                'success_criteria': 'Complete spec document with all user stories and security requirements',
                'risk_level': 'low'
            },
            {
                'id': 'task-002',
                'agent': 'architect',
                'task_type': 'design',
                'description': 'Design authentication architecture: database schema (users, sessions, password_resets tables), API endpoints, Redis session storage, rate limiting strategy',
                'dependencies': ['task-001'],
                'estimated_minutes': 45,
                'success_criteria': 'Architecture diagram and data model approved by tech lead',
                'risk_level': 'medium'
            },
            {
                'id': 'task-003',
                'agent': 'coder',
                'task_type': 'implement',
                'description': 'Implement user registration endpoint with email validation, bcrypt password hashing (12 rounds), duplicate email check, GDPR compliance logging',
                'dependencies': ['task-002'],
                'estimated_minutes': 60,
                'success_criteria': 'Endpoint accepts valid registrations, rejects duplicates, passwords properly hashed',
                'risk_level': 'medium'
            },
            {
                'id': 'task-004',
                'agent': 'coder',
                'task_type': 'implement',
                'description': 'Implement login endpoint with rate limiting (5 attempts per 15min), session creation in Redis (1hr TTL), bcrypt password verification',
                'dependencies': ['task-003'],
                'estimated_minutes': 60,
                'success_criteria': 'Login works, rate limiting enforced, sessions created in Redis',
                'risk_level': 'high'  # Complex: rate limiting + session management
            },
            {
                'id': 'task-005',
                'agent': 'security-manager',
                'task_type': 'security-scan',
                'description': 'Security audit of authentication code: check for SQL injection, verify bcrypt usage, validate rate limiting, ensure GDPR logging, test session management',
                'dependencies': ['task-004'],
                'estimated_minutes': 30,
                'success_criteria': 'No critical or high severity vulnerabilities found',
                'risk_level': 'low'
            },
            {
                'id': 'task-006',
                'agent': 'tester',
                'task_type': 'test',
                'description': 'Create comprehensive test suite: happy path (valid registration/login), edge cases (empty email, weak password), error cases (duplicate user, invalid password), security tests (SQL injection attempts, rate limit enforcement)',
                'dependencies': ['task-005'],
                'estimated_minutes': 45,
                'success_criteria': '≥90% code coverage, all test cases pass',
                'risk_level': 'low'
            },
            {
                'id': 'task-007',
                'agent': 'reviewer',
                'task_type': 'review',
                'description': 'Code review for code quality: check NASA Rule 10 compliance (≤60 LOC/function), verify type hints, validate error handling, confirm GDPR logging complete',
                'dependencies': ['task-006'],
                'estimated_minutes': 30,
                'success_criteria': 'Code review approved, no blocking issues',
                'risk_level': 'low'
            }
        ],
        quality_gates=[
            {
                'type': 'security_audit',
                'agent': 'security-manager',
                'after_task': 'task-004',
                'acceptance_criteria': 'Zero critical/high vulnerabilities, bcrypt verified, rate limiting tested'
            },
            {
                'type': 'testing',
                'agent': 'tester',
                'after_task': 'task-005',
                'acceptance_criteria': '≥90% coverage, all tests pass, edge cases covered'
            },
            {
                'type': 'code_review',
                'agent': 'reviewer',
                'after_task': 'task-006',
                'acceptance_criteria': 'NASA compliant, type-safe, well-documented'
            }
        ],
        error_handling={
            'rollback_plan': 'Revert to previous auth system, redirect users to legacy login',
            'monitoring': 'Track login success rate, session creation rate, rate limit triggers',
            'alerts': 'Alert if login success rate <95% or if >10 rate limit triggers/minute',
            'fallback_option': 'Disable rate limiting temporarily if false positives detected'
        },
        metadata={
            'total_duration_minutes': 300,  # 5 hours
            'critical_path': ['task-001', 'task-002', 'task-003', 'task-004', 'task-005', 'task-006', 'task-007'],
            'parallelizable_tasks': [],  # All sequential in this example
            'confidence': 'high',
            'assumptions': [
                'bcrypt library already in dependencies',
                'Redis instance available for sessions',
                'Database migrations handled separately'
            ]
        }
    ).with_inputs('task_description', 'project_context', 'available_agents')

    return [example1]  # Add more examples...
```

### Training Script with Best Practices

```python
# src/dspy_optimization/train_queen.py
import dspy
from src.dspy_optimization.dspy_config import configure_dspy_lm
from src.dspy_optimization.queen_signature import (
    QueenModule,
    task_decomposition_metric,
    create_queen_training_examples
)

def train_queen_optimized():
    """
    Train Queen agent with all prompt engineering best practices.

    This training incorporates:
    1. Clear, specific signature definitions (Principle 1)
    2. Expert role assignment (Principle 2)
    3. Chain-of-thought reasoning (Principle 3)
    4. High-quality few-shot examples (Principle 4)
    5. Explicit output format specs (Principle 5)
    6. Constraints and boundaries (Principle 6)
    7. Rich context provision (Principle 7)
    8. Error prevention guidance (Principle 8)
    9. Incremental reasoning (Principle 9)
    10. Unbiased instructions (Principle 10)
    """

    print("Configuring DSPy with Gemini backend...")
    lm = configure_dspy_lm()

    print("Loading training examples...")
    trainset = create_queen_training_examples()

    print(f"Training set: {len(trainset)} examples")

    print("Creating Queen module...")
    queen = QueenModule()

    print("Configuring BootstrapFewShot optimizer...")
    optimizer = dspy.BootstrapFewShot(
        metric=task_decomposition_metric,
        max_bootstrapped_demos=5,  # Use best 5 examples
        max_labeled_demos=7,  # From available training examples
        max_rounds=3,  # 3 optimization rounds
        teacher_settings=dict(temperature=0.7)  # Slightly creative
    )

    print("Compiling (optimizing) Queen agent...")
    print("This will:")
    print("  1. Generate few-shot demonstrations from training examples")
    print("  2. Optimize instruction text for clarity")
    print("  3. Select best examples via bootstrap sampling")
    print("  4. Validate improvements on held-out examples")

    optimized_queen = optimizer.compile(
        queen,
        trainset=trainset
    )

    print("Saving optimized module...")
    optimized_queen.save('models/queen_optimized.json')

    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)
    print(f"Optimized module saved to: models/queen_optimized.json")
    print("\nNext steps:")
    print("1. Evaluate on validation set")
    print("2. Compare with baseline Queen agent")
    print("3. A/B test if improvement ≥10%")

    return optimized_queen

if __name__ == "__main__":
    train_queen_optimized()
```

---

## Summary: Prompt Engineering → DSPy Integration

### Key Takeaways

1. **DSPy Automates**, But Quality Matters
   - DSPy optimizes prompts automatically
   - But garbage in = garbage out
   - Well-designed signatures → better optimization results

2. **26 Principles Embedded**
   - Clarity (Principle 1) → Detailed InputField descriptions
   - Role assignment (Principle 2) → Signature docstrings
   - Chain-of-thought (Principle 3) → dspy.ChainOfThought()
   - Examples (Principle 4) → BootstrapFewShot training data
   - Output format (Principle 5) → Structured OutputField specs
   - ... and 21 more

3. **Our Approach**
   - Start with expert-crafted signatures (all 26 principles)
   - Let DSPy optimize from this strong foundation
   - Measure results vs baseline
   - Iterate if needed (MIPRO for aggressive optimization)

4. **Expected Results**
   - Baseline: 66.7% Queen quality (manual prompting)
   - With principles: ~70% (good manual prompts)
   - With DSPy + principles: ≥75% (10%+ improvement target)

---

**Version**: 8.0.0
**Document**: PROMPT-ENGINEERING-PRINCIPLES.md
**Timestamp**: 2025-10-08T23:30:00-05:00
**Status**: PRODUCTION-READY GUIDE

**References**:
- OpenAI Prompt Engineering Guide
- Anthropic Claude Prompt Engineering
- Google PaLM Best Practices
- DSPy Documentation
- SPEK Platform v8 DSPy Integration Strategy
