# Agent Usage Examples

**Version**: 1.0
**Date**: 2025-10-10

Practical examples for using all 6 new specialized agents in real-world scenarios.

---

## Frontend Development Agent Examples

### Example 1: Building a User Profile Page

**Scenario**: Create a complete user profile page with multiple components.

```python
from src.agents.specialized.FrontendDevAgent import create_frontend_dev_agent
from src.core.types import Task

agent = create_frontend_dev_agent()

# Step 1: Create main profile component
profile_task = Task(
    task_id="profile-001",
    task_type="implement-component",
    description="Create user profile container component",
    payload={
        "component_name": "UserProfile",
        "component_type": "functional",
        "props": ["userId"],
        "has_state": True,
        "styling": "tailwind"
    }
)

profile_result = await agent.execute(profile_task)
print(profile_result.data["code"])

# Step 2: Create avatar component
avatar_task = Task(
    task_id="profile-002",
    task_type="implement-component",
    description="Create user avatar with upload",
    payload={
        "component_name": "UserAvatar",
        "props": ["imageUrl", "onUpload", "size"],
        "styling": "tailwind"
    }
)

avatar_result = await agent.execute(avatar_task)

# Step 3: Optimize rendering for large friend lists
optimize_task = Task(
    task_id="profile-003",
    task_type="optimize-rendering",
    description="Virtualize friends list",
    payload={
        "component_name": "FriendsList",
        "optimization_type": "virtualization",
        "performance_target": {
            "render_time_ms": 50,
            "memory_mb": 20
        }
    }
)

optimize_result = await agent.execute(optimize_task)
print(f"Expected improvement: {optimize_result.data['expected_improvement']}")
```

---

### Example 2: Implementing a Dashboard UI

```python
# Create complete dashboard layout
dashboard_task = Task(
    task_id="dash-001",
    task_type="implement-ui",
    description="Create analytics dashboard",
    payload={
        "ui_name": "AnalyticsDashboard",
        "layout_type": "responsive",
        "sections": [
            "header",
            "navigation",
            "metrics-cards",
            "charts-grid",
            "activity-feed",
            "footer"
        ],
        "accessibility": True,
        "responsive_breakpoints": ["sm", "md", "lg", "xl", "2xl"]
    }
)

dashboard_result = await agent.execute(dashboard_task)

# The result includes:
# - Complete dashboard layout code
# - All sub-components
# - Responsive styles
# - Accessibility features (ARIA labels, keyboard navigation)
```

---

## Backend Development Agent Examples

### Example 3: Building a RESTful API

**Scenario**: Create a complete user management API with CRUD operations.

```python
from src.agents.specialized.BackendDevAgent import create_backend_dev_agent

agent = create_backend_dev_agent()

# Step 1: Create database schema
schema_task = Task(
    task_id="api-001",
    task_type="implement-database",
    description="Create users table",
    payload={
        "table_name": "users",
        "database_type": "postgresql",
        "columns": {
            "id": "UUID PRIMARY KEY DEFAULT gen_random_uuid()",
            "email": "VARCHAR(255) UNIQUE NOT NULL",
            "name": "VARCHAR(100) NOT NULL",
            "password_hash": "VARCHAR(255) NOT NULL",
            "role": "VARCHAR(50) DEFAULT 'user'",
            "created_at": "TIMESTAMP DEFAULT NOW()",
            "updated_at": "TIMESTAMP DEFAULT NOW()"
        },
        "indexes": ["email", "created_at"]
    }
)

schema_result = await agent.execute(schema_task)
print(schema_result.data["schema"])
print(schema_result.data["orm_model"])

# Step 2: Create GET /users endpoint
get_users_task = Task(
    task_id="api-002",
    task_type="implement-api",
    description="List users with pagination",
    payload={
        "endpoint": "/api/v1/users",
        "method": "GET",
        "api_type": "rest",
        "authentication": True,
        "query_parameters": {
            "page": "integer",
            "limit": "integer",
            "search": "string"
        },
        "rate_limiting": {"requests_per_minute": 100}
    }
)

get_result = await agent.execute(get_users_task)

# Step 3: Create POST /users endpoint
create_user_task = Task(
    task_id="api-003",
    task_type="implement-api",
    description="Create new user",
    payload={
        "endpoint": "/api/v1/users",
        "method": "POST",
        "api_type": "rest",
        "request_body": {
            "email": "string",
            "name": "string",
            "password": "string",
            "role": "string"
        },
        "response_schema": {
            "id": "string",
            "email": "string",
            "name": "string",
            "role": "string",
            "created_at": "string"
        },
        "authentication": True
    }
)

create_result = await agent.execute(create_user_task)

# Step 4: Implement business logic for user registration
registration_logic_task = Task(
    task_id="api-004",
    task_type="implement-business-logic",
    description="User registration workflow",
    payload={
        "logic_name": "RegisterUser",
        "operations": [
            "validate_email_format",
            "check_email_uniqueness",
            "hash_password",
            "create_user_record",
            "send_welcome_email",
            "generate_auth_token"
        ],
        "validation_rules": [
            {"field": "email", "rule": "valid email format"},
            {"field": "password", "rule": "min 8 chars, 1 uppercase, 1 number"}
        ],
        "transaction_support": True
    }
)

logic_result = await agent.execute(registration_logic_task)
```

---

### Example 4: Query Optimization

```python
# Optimize slow search query
optimize_query_task = Task(
    task_id="opt-001",
    task_type="optimize-queries",
    description="Optimize user search with filters",
    payload={
        "query_type": "select",
        "table": "users",
        "current_query": """
            SELECT * FROM users
            WHERE name LIKE '%{search}%'
               OR email LIKE '%{search}%'
            ORDER BY created_at DESC
            LIMIT 50
        """,
        "performance_issues": [
            "full table scan on LIKE queries",
            "no index usage",
            "slow with large datasets"
        ],
        "target_improvement": "80% faster"
    }
)

result = await agent.execute(optimize_query_task)

print("Optimized query:", result.data["optimized_query"])
print("Index suggestions:", result.data["index_suggestions"])
# Output might include:
# - Add GIN index for full-text search
# - Use to_tsvector for text search
# - Implement result caching
```

---

## Code Analyzer Agent Examples

### Example 5: Comprehensive Code Analysis

```python
from src.agents.specialized.CodeAnalyzerAgent import create_code_analyzer_agent

agent = create_code_analyzer_agent()

# Analyze entire module
analysis_task = Task(
    task_id="analyze-001",
    task_type="analyze-code",
    description="Analyze user service module",
    payload={
        "file_path": "src/services/user_service.py",
        "language": "python",
        "analysis_types": ["quality", "security", "performance"]
    }
)

result = await agent.execute(analysis_task)

# Result includes:
# - Overall quality score
# - Issues by severity
# - Security vulnerabilities
# - Performance bottlenecks
# - Code metrics (LOC, complexity, etc.)

for issue in result.data["analysis"]["issues"]:
    print(f"{issue['severity']}: Line {issue['line']}: {issue['message']}")
    if issue.get("fix_suggestion"):
        print(f"  Suggestion: {issue['fix_suggestion']}")
```

---

### Example 6: Detecting Code Complexity

```python
# Find high-complexity functions
complexity_task = Task(
    task_id="complex-001",
    task_type="detect-complexity",
    description="Find functions exceeding complexity threshold",
    payload={
        "file_path": "src/utils/data_processor.py",
        "threshold": 10  # NASA standard
    }
)

result = await agent.execute(complexity_task)

print(f"Total functions: {result.data['summary']['total_functions']}")
print(f"Average complexity: {result.data['summary']['avg_complexity']}")
print(f"Violations: {result.data['summary']['violations']}")

for metric in result.data["complexity_metrics"]:
    if metric["exceeds_threshold"]:
        print(f"\n{metric['function_name']} (line {metric['line_number']})")
        print(f"  Complexity: {metric['complexity']}")
        print(f"  Suggestion: {metric['refactoring_suggestion']}")
```

---

### Example 7: Finding Duplicate Code

```python
# Detect code duplication
duplicate_task = Task(
    task_id="dup-001",
    task_type="detect-duplicates",
    description="Find duplicate code across service layer",
    payload={
        "file_path": "src/services/*.py",
        "similarity_threshold": 0.85,
        "min_lines": 6
    }
)

result = await agent.execute(duplicate_task)

for dup in result.data["duplicates"]:
    print(f"Similarity: {dup['similarity'] * 100:.1f}%")
    print("Locations:")
    for loc in dup["locations"]:
        print(f"  {loc['file']}:{loc['start_line']}-{loc['end_line']}")
    print(f"Refactoring: {dup['refactoring_suggestion']}\n")
```

---

## Infrastructure Operations Agent Examples

### Example 8: Kubernetes Deployment

```python
from src.agents.specialized.InfrastructureOpsAgent import create_infrastructure_ops_agent

agent = create_infrastructure_ops_agent()

# Deploy microservice to Kubernetes
deploy_task = Task(
    task_id="k8s-001",
    task_type="deploy-infrastructure",
    description="Deploy user service to K8s",
    payload={
        "platform": "kubernetes",
        "app_name": "user-service",
        "image": "myregistry/user-service:v1.0.0",
        "replicas": 3,
        "port": 8080,
        "environment_variables": {
            "DATABASE_URL": "postgresql://...",
            "REDIS_URL": "redis://...",
            "LOG_LEVEL": "info"
        },
        "resources": {
            "cpu": "500m",
            "memory": "512Mi"
        }
    }
)

result = await agent.execute(deploy_task)

# Get generated manifests
deployment_yaml = result.data["manifests"]["Deployment"]
service_yaml = result.data["manifests"]["Service"]

# Save to files and apply
with open("deployment.yaml", "w") as f:
    f.write(deployment_yaml)
with open("service.yaml", "w") as f:
    f.write(service_yaml)

# Apply with kubectl
for cmd in result.data["deployment_commands"]:
    print(f"Execute: {cmd}")
```

---

### Example 9: Auto-Scaling Setup

```python
# Configure horizontal pod autoscaling
scale_task = Task(
    task_id="scale-001",
    task_type="scale-infrastructure",
    description="Setup HPA for API service",
    payload={
        "resource": "deployment/api-service",
        "auto_scaling": {
            "min_replicas": 2,
            "max_replicas": 10,
            "cpu_threshold": 70,
            "memory_threshold": 80
        },
        "platform": "kubernetes"
    }
)

result = await agent.execute(scale_task)

# Get HPA configuration
hpa_config = result.data["config"]
print("HPA Configuration:\n", hpa_config)
```

---

### Example 10: Monitoring Setup

```python
# Setup Prometheus monitoring
monitor_task = Task(
    task_id="monitor-001",
    task_type="monitor-infrastructure",
    description="Configure monitoring stack",
    payload={
        "monitoring_type": "prometheus",
        "targets": ["api-service", "user-service", "database"],
        "metrics": [
            "cpu",
            "memory",
            "request_rate",
            "error_rate",
            "response_time"
        ],
        "alerts": [
            {"metric": "error_rate", "threshold": 5, "severity": "critical"},
            {"metric": "response_time", "threshold": 1000, "severity": "warning"},
            {"metric": "cpu", "threshold": 85, "severity": "warning"}
        ]
    }
)

result = await agent.execute(monitor_task)

# Setup includes:
# - Prometheus configuration
# - Grafana dashboards
# - Alert rules
# - Installation steps
```

---

## Release Manager Agent Examples

### Example 11: Complete Release Workflow

```python
from src.agents.specialized.ReleaseManagerAgent import create_release_manager_agent

agent = create_release_manager_agent()

# Step 1: Prepare release
prepare_task = Task(
    task_id="release-001",
    task_type="prepare-release",
    description="Prepare v2.0.0 major release",
    payload={
        "current_version": "1.5.3",
        "release_type": "major"
    }
)

prepare_result = await agent.execute(prepare_task)
new_version = prepare_result.data["new_version"]  # "2.0.0"

# Step 2: Generate changelog
changelog_task = Task(
    task_id="release-002",
    task_type="generate-changelog",
    description="Generate changelog from git history",
    payload={
        "from_version": "1.5.3",
        "to_version": new_version,
        "commits": [
            {"message": "feat: add user authentication", "hash": "abc123"},
            {"message": "feat: implement dashboard", "hash": "def456"},
            {"message": "fix: resolve memory leak", "hash": "ghi789"},
            {"message": "BREAKING CHANGE: rename API endpoints", "hash": "jkl012"},
            {"message": "docs: update API documentation", "hash": "mno345"}
        ],
        "format": "keepachangelog"
    }
)

changelog_result = await agent.execute(changelog_task)
changelog = changelog_result.data["changelog"]

# Step 3: Create git tag
tag_task = Task(
    task_id="release-003",
    task_type="tag-release",
    description="Tag release in git",
    payload={
        "version": new_version,
        "message": f"Release version {new_version}\\n\\n{changelog}",
        "signed": True,
        "push": True
    }
)

tag_result = await agent.execute(tag_task)

# Step 4: Coordinate deployment
deploy_task = Task(
    task_id="release-004",
    task_type="coordinate-deployment",
    description="Deploy to staging and production",
    payload={
        "version": new_version,
        "environments": ["staging", "production"],
        "strategy": "blue-green",
        "rollback_plan": True,
        "approval_required": True
    }
)

deploy_result = await agent.execute(deploy_task)

# Execute deployment plan
plan = deploy_result.data["deployment_plan"]
for stage in plan["stages"]:
    print(f"Environment: {stage['environment']}")
    print(f"Estimated duration: {stage['estimated_duration']}")
    for step in stage["steps"]:
        print(f"  - {step}")
```

---

## Performance Engineer Agent Examples

### Example 12: Performance Investigation

```python
from src.agents.specialized.PerformanceEngineerAgent import create_performance_engineer_agent

agent = create_performance_engineer_agent()

# Step 1: Profile the slow endpoint
profile_task = Task(
    task_id="perf-001",
    task_type="profile-performance",
    description="Profile user search endpoint",
    payload={
        "target": "api/v1/users/search",
        "metrics": ["cpu", "memory", "io", "network"],
        "duration_seconds": 60,
        "detail_level": "high"
    }
)

profile_result = await agent.execute(profile_task)

# Analyze hot spots
for hot_spot in profile_result.data["profile_results"]["hot_spots"]:
    print(f"{hot_spot['function']}:{hot_spot['line']}")
    print(f"  Time: {hot_spot['time_ms']}ms ({hot_spot['percentage']}%)")

# Step 2: Detect specific bottlenecks
bottleneck_task = Task(
    task_id="perf-002",
    task_type="detect-bottlenecks",
    description="Identify performance bottlenecks",
    payload={
        "system": "search_service",
        "metrics": {
            "response_time": 1200,  # Current: 1.2s
            "cpu_usage": 85,
            "memory_usage": 90,
            "cache_hit_rate": 30
        },
        "analysis_period": "24h"
    }
)

bottleneck_result = await agent.execute(bottleneck_task)

# Priority bottlenecks
for bottleneck in bottleneck_result.data["bottlenecks"]:
    if bottleneck["severity"] == "critical":
        print(f"CRITICAL: {bottleneck['component']}")
        print(f"  {bottleneck['description']}")
        print(f"  Impact: {bottleneck['impact']}")

# Step 3: Get optimization recommendations
optimize_task = Task(
    task_id="perf-003",
    task_type="optimize-performance",
    description="Optimize search performance",
    payload={
        "target": "user_search",
        "current_performance": {
            "metric": "response_time",
            "value": 1200
        },
        "target_performance": {
            "metric": "response_time",
            "value": 200
        },
        "bottleneck_type": "database"
    }
)

optimize_result = await agent.execute(optimize_task)

# Implement optimizations in priority order
for optimization in optimize_result.data["optimizations"]:
    print(f"\nStrategy: {optimization['strategy']}")
    print(f"Expected improvement: {optimization['expected_improvement']}")
    print(f"Effort: {optimization['implementation_effort']}")
    if optimization.get("code_example"):
        print(f"Example:\n{optimization['code_example']}")
```

---

### Example 13: Benchmarking

```python
# Run comprehensive benchmark
benchmark_task = Task(
    task_id="bench-001",
    task_type="benchmark-system",
    description="Benchmark API under load",
    payload={
        "system": "rest_api",
        "test_cases": [
            {
                "name": "list_users",
                "endpoint": "/api/v1/users",
                "method": "GET",
                "load": 100  # 100 concurrent requests
            },
            {
                "name": "get_user",
                "endpoint": "/api/v1/users/{id}",
                "method": "GET",
                "load": 200
            },
            {
                "name": "create_user",
                "endpoint": "/api/v1/users",
                "method": "POST",
                "load": 50
            }
        ],
        "baseline": {
            "avg_response_ms": 100,
            "p95_response_ms": 150,
            "throughput_rps": 500
        },
        "duration_seconds": 300
    }
)

benchmark_result = await agent.execute(benchmark_task)

# Check for regressions
if benchmark_result.data.get("comparison", {}).get("regression"):
    print("REGRESSION DETECTED!")
    for metric, change in benchmark_result.data["comparison"]["changes"].items():
        print(f"  {metric}: {change}")

# Print detailed results
for test_case in benchmark_result.data["benchmark_results"]["test_cases"]:
    print(f"\nTest: {test_case['name']}")
    print(f"  Avg response: {test_case['avg_response_ms']}ms")
    print(f"  P95: {test_case['p95_response_ms']}ms")
    print(f"  P99: {test_case['p99_response_ms']}ms")
    print(f"  Throughput: {test_case['throughput_rps']} req/s")
    print(f"  Error rate: {test_case['error_rate']}%")
```

---

## End-to-End Scenario: Building a Feature

### Example 14: Complete Feature Implementation

```python
"""
Scenario: Implement a new "User Dashboard" feature with:
- Frontend UI components
- Backend API endpoints
- Database schema
- Deployment configuration
- Performance optimization
- Release preparation
"""

# 1. Design database schema (Backend Dev)
backend_agent = create_backend_dev_agent()

schema_task = Task(
    task_id="feature-001",
    task_type="implement-database",
    description="Create dashboard_data table",
    payload={
        "table_name": "dashboard_data",
        "database_type": "postgresql",
        "columns": {
            "id": "UUID PRIMARY KEY",
            "user_id": "UUID REFERENCES users(id)",
            "metrics": "JSONB",
            "updated_at": "TIMESTAMP"
        }
    }
)

await backend_agent.execute(schema_task)

# 2. Implement API endpoint (Backend Dev)
api_task = Task(
    task_id="feature-002",
    task_type="implement-api",
    description="Create dashboard data API",
    payload={
        "endpoint": "/api/v1/dashboard",
        "method": "GET",
        "api_type": "rest",
        "authentication": True
    }
)

await backend_agent.execute(api_task)

# 3. Build frontend component (Frontend Dev)
frontend_agent = create_frontend_dev_agent()

ui_task = Task(
    task_id="feature-003",
    task_type="implement-ui",
    description="Create dashboard UI",
    payload={
        "ui_name": "Dashboard",
        "layout_type": "responsive",
        "sections": ["header", "metrics", "charts"]
    }
)

await frontend_agent.execute(ui_task)

# 4. Analyze code quality (Code Analyzer)
analyzer_agent = create_code_analyzer_agent()

analysis_task = Task(
    task_id="feature-004",
    task_type="analyze-code",
    description="Analyze dashboard code",
    payload={
        "file_path": "src/dashboard/",
        "analysis_types": ["quality", "complexity"]
    }
)

await analyzer_agent.execute(analysis_task)

# 5. Profile performance (Performance Engineer)
perf_agent = create_performance_engineer_agent()

profile_task = Task(
    task_id="feature-005",
    task_type="profile-performance",
    description="Profile dashboard loading",
    payload={
        "target": "dashboard_render",
        "metrics": ["cpu", "memory"]
    }
)

await perf_agent.execute(profile_task)

# 6. Deploy to staging (Infrastructure Ops)
infra_agent = create_infrastructure_ops_agent()

deploy_task = Task(
    task_id="feature-006",
    task_type="deploy-infrastructure",
    description="Deploy dashboard to staging",
    payload={
        "platform": "kubernetes",
        "app_name": "dashboard",
        "replicas": 2
    }
)

await infra_agent.execute(deploy_task)

# 7. Prepare release (Release Manager)
release_agent = create_release_manager_agent()

release_task = Task(
    task_id="feature-007",
    task_type="prepare-release",
    description="Prepare v1.6.0 with dashboard",
    payload={
        "current_version": "1.5.0",
        "release_type": "minor"
    }
)

await release_agent.execute(release_task)
```

---

**Version**: 1.0
**Last Updated**: 2025-10-10
**Examples**: 14 complete scenarios
**Agents Covered**: All 6 specialized agents
