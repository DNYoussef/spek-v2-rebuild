# Agent API Reference - Week 8-9 New Agents

**Version**: 1.0
**Date**: 2025-10-10
**Status**: Complete

This document provides complete API reference for all 24 new task types introduced with the 6 new specialized agents.

---

## Table of Contents

1. [Frontend Development Agent](#frontend-development-agent)
2. [Backend Development Agent](#backend-development-agent)
3. [Code Analyzer Agent](#code-analyzer-agent)
4. [Infrastructure Operations Agent](#infrastructure-operations-agent)
5. [Release Manager Agent](#release-manager-agent)
6. [Performance Engineer Agent](#performance-engineer-agent)

---

## Frontend Development Agent

**Agent ID**: `frontend-dev`
**Princess**: Princess-Dev
**Keywords**: `ui`, `component`, `react`, `frontend`, `typescript`

### Task Type 1: implement-component

Create React/TypeScript components with full functionality.

**Payload Schema**:
```typescript
{
  component_name: string;          // Required: Component name (PascalCase)
  component_type?: 'functional' | 'class';  // Default: 'functional'
  props?: string[];                // List of prop names
  has_state?: boolean;             // Whether component needs state
  styling?: 'css-in-js' | 'tailwind' | 'styled-components';
}
```

**Example Request**:
```python
task = Task(
    task_id="fe-001",
    task_type="implement-component",
    description="Create user profile card component",
    payload={
        "component_name": "UserProfileCard",
        "component_type": "functional",
        "props": ["userId", "onEdit", "isEditable"],
        "has_state": True,
        "styling": "tailwind"
    }
)
```

**Response Schema**:
```typescript
{
  code: string;                    // Generated TypeScript/React code
  language: 'typescript';
  component_type: string;
  file_name: string;               // Suggested filename
  imports: string[];               // Required imports
  tests?: string;                  // Suggested tests
}
```

**Validation Rules**:
- `component_name` must be PascalCase
- If `props` provided, must be array of strings
- `component_type` defaults to 'functional'

---

### Task Type 2: implement-ui

Implement complete UI layouts with multiple sections.

**Payload Schema**:
```typescript
{
  ui_name: string;                 // Required: UI page/layout name
  layout_type: 'responsive' | 'fixed' | 'centered' | 'sidebar';
  sections: string[];              // List of UI sections
  accessibility?: boolean;         // Include WCAG 2.1 features (default: true)
  responsive_breakpoints?: string[];
}
```

**Example Request**:
```python
task = Task(
    task_id="fe-002",
    task_type="implement-ui",
    description="Create dashboard layout with sidebar",
    payload={
        "ui_name": "Dashboard",
        "layout_type": "sidebar",
        "sections": ["header", "sidebar", "main-content", "footer"],
        "accessibility": True,
        "responsive_breakpoints": ["sm", "md", "lg", "xl"]
    }
)
```

**Response Schema**:
```typescript
{
  code: string;                    // Complete UI layout code
  language: 'typescript';
  layout_components: string[];     // List of sub-components
  styles: string;                  // CSS/Tailwind styles
  accessibility_notes: string;
}
```

---

### Task Type 3: optimize-rendering

Optimize React component rendering performance.

**Payload Schema**:
```typescript
{
  component_name: string;          // Required: Component to optimize
  optimization_type: 'memoization' | 'lazy-loading' | 'virtualization' | 'comprehensive';
  current_code?: string;           // Optional: Current implementation
  performance_target?: {
    render_time_ms: number;
    memory_mb: number;
  };
}
```

**Example Request**:
```python
task = Task(
    task_id="fe-003",
    task_type="optimize-rendering",
    description="Optimize ProductList with virtualization",
    payload={
        "component_name": "ProductList",
        "optimization_type": "virtualization",
        "performance_target": {
            "render_time_ms": 50,
            "memory_mb": 20
        }
    }
)
```

**Response Schema**:
```typescript
{
  recommendations: string[];       // List of optimization strategies
  code_changes?: string;           // Suggested code modifications
  expected_improvement: {
    render_time_reduction: string; // e.g., "40% faster"
    memory_reduction: string;
  };
  implementation_notes: string;
}
```

---

### Task Type 4: implement-styles

Create component styling with chosen CSS framework.

**Payload Schema**:
```typescript
{
  component_name: string;          // Required: Component to style
  style_system: 'tailwind' | 'css-in-js' | 'styled-components' | 'css-modules';
  theme?: {
    colors?: Record<string, string>;
    spacing?: Record<string, string>;
    typography?: Record<string, string>;
  };
  responsive?: boolean;            // Default: true
}
```

**Example Request**:
```python
task = Task(
    task_id="fe-004",
    task_type="implement-styles",
    description="Create button styles with variants",
    payload={
        "component_name": "Button",
        "style_system": "tailwind",
        "theme": {
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#6B7280"
            }
        },
        "responsive": True
    }
)
```

**Response Schema**:
```typescript
{
  styles: string;                  // Generated styles
  variants: string[];              // Style variants (primary, secondary, etc.)
  usage_examples: string;          // How to apply styles
  theme_tokens?: string;           // Design tokens
}
```

---

## Backend Development Agent

**Agent ID**: `backend-dev`
**Princess**: Princess-Dev
**Keywords**: `api`, `database`, `endpoint`, `backend`, `server`

### Task Type 5: implement-api

Create RESTful or GraphQL API endpoints.

**Payload Schema**:
```typescript
{
  endpoint: string;                // Required: API endpoint path
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  api_type: 'rest' | 'graphql';
  request_body?: Record<string, string>;  // For POST/PUT/PATCH
  response_schema?: Record<string, string>;
  authentication?: boolean;        // Default: true
  rate_limiting?: {
    requests_per_minute: number;
  };
}
```

**Example Request**:
```python
task = Task(
    task_id="be-001",
    task_type="implement-api",
    description="Create user management API endpoint",
    payload={
        "endpoint": "/api/v1/users",
        "method": "POST",
        "api_type": "rest",
        "request_body": {
            "name": "string",
            "email": "string",
            "role": "string"
        },
        "authentication": True,
        "rate_limiting": {
            "requests_per_minute": 60
        }
    }
)
```

**Response Schema**:
```typescript
{
  code: string;                    // FastAPI/Express endpoint code
  language: 'python' | 'typescript';
  models: string;                  // Pydantic/TypeORM models
  validation: string;              // Input validation logic
  tests: string;                   // Suggested tests
  documentation: string;           // API documentation
}
```

---

### Task Type 6: implement-database

Design and create database schemas.

**Payload Schema**:
```typescript
{
  table_name: string;              // Required: Table/collection name
  database_type: 'postgresql' | 'mysql' | 'mongodb' | 'sqlite';
  columns?: Record<string, string>;  // For SQL databases
  fields?: Record<string, string>;   // For NoSQL databases
  relationships?: Array<{
    type: 'one-to-one' | 'one-to-many' | 'many-to-many';
    target_table: string;
  }>;
  indexes?: string[];              // Fields to index
}
```

**Example Request**:
```python
task = Task(
    task_id="be-002",
    task_type="implement-database",
    description="Create users table with relationships",
    payload={
        "table_name": "users",
        "database_type": "postgresql",
        "columns": {
            "id": "SERIAL PRIMARY KEY",
            "email": "VARCHAR(255) UNIQUE NOT NULL",
            "password_hash": "VARCHAR(255) NOT NULL",
            "created_at": "TIMESTAMP DEFAULT NOW()"
        },
        "relationships": [
            {
                "type": "one-to-many",
                "target_table": "posts"
            }
        ],
        "indexes": ["email"]
    }
)
```

**Response Schema**:
```typescript
{
  schema: string;                  // SQL CREATE TABLE or NoSQL schema
  migration: string;               // Database migration script
  orm_model: string;               // ORM model code (SQLAlchemy/TypeORM)
  relationships_code: string;
}
```

---

### Task Type 7: implement-business-logic

Implement complex business logic and workflows.

**Payload Schema**:
```typescript
{
  logic_name: string;              // Required: Function/class name
  operations: string[];            // List of operations to perform
  validation_rules?: Array<{
    field: string;
    rule: string;
  }>;
  error_handling?: boolean;        // Default: true
  transaction_support?: boolean;   // For database operations
}
```

**Example Request**:
```python
task = Task(
    task_id="be-003",
    task_type="implement-business-logic",
    description="Implement order processing workflow",
    payload={
        "logic_name": "ProcessOrder",
        "operations": [
            "validate_inventory",
            "calculate_total",
            "process_payment",
            "update_inventory",
            "send_confirmation"
        ],
        "validation_rules": [
            {"field": "quantity", "rule": "must be positive"},
            {"field": "payment_method", "rule": "must be valid"}
        ],
        "transaction_support": True
    }
)
```

**Response Schema**:
```typescript
{
  code: string;                    // Business logic implementation
  language: 'python' | 'typescript';
  validation_functions: string;
  error_cases: string[];           // Handled error scenarios
  tests: string;
}
```

---

### Task Type 8: optimize-queries

Optimize database queries for performance.

**Payload Schema**:
```typescript
{
  query_type: 'select' | 'insert' | 'update' | 'delete' | 'join';
  table: string;                   // Primary table
  current_query?: string;          // Current query (optional)
  performance_issues?: string[];   // Known issues
  target_improvement?: string;     // e.g., "50% faster"
}
```

**Example Request**:
```python
task = Task(
    task_id="be-004",
    task_type="optimize-queries",
    description="Optimize user search with filters",
    payload={
        "query_type": "select",
        "table": "users",
        "current_query": "SELECT * FROM users WHERE name LIKE '%search%'",
        "performance_issues": ["full table scan", "slow wildcard search"],
        "target_improvement": "80% faster"
    }
)
```

**Response Schema**:
```typescript
{
  optimized_query: string;
  recommendations: string[];
  index_suggestions: string[];
  expected_improvement: string;
  explanation: string;
}
```

---

## Code Analyzer Agent

**Agent ID**: `code-analyzer`
**Princess**: Princess-Quality
**Keywords**: `analyze`, `complexity`, `duplicate`, `quality`

### Task Type 9: analyze-code

Perform comprehensive static code analysis.

**Payload Schema**:
```typescript
{
  file_path?: string;              // File to analyze
  code?: string;                   // Or direct code string
  language?: 'python' | 'typescript' | 'javascript';
  analysis_types?: string[];       // ['quality', 'security', 'performance']
}
```

**Example Request**:
```python
task = Task(
    task_id="ca-001",
    task_type="analyze-code",
    description="Analyze module for code quality",
    payload={
        "file_path": "src/services/user_service.py",
        "language": "python",
        "analysis_types": ["quality", "security", "performance"]
    }
)
```

**Response Schema**:
```typescript
{
  analysis: {
    quality_score: number;         // 0-100
    issues: Array<{
      severity: 'critical' | 'warning' | 'info';
      line: number;
      message: string;
      fix_suggestion?: string;
    }>;
    metrics: {
      loc: number;
      functions: number;
      classes: number;
      avg_complexity: number;
    };
  };
}
```

---

### Task Type 10: detect-complexity

Calculate cyclomatic complexity of functions.

**Payload Schema**:
```typescript
{
  file_path?: string;
  code?: string;
  threshold?: number;              // Default: 10 (NASA: ≤10)
}
```

**Example Request**:
```python
task = Task(
    task_id="ca-002",
    task_type="detect-complexity",
    description="Find high-complexity functions",
    payload={
        "file_path": "src/utils/data_processor.py",
        "threshold": 10
    }
)
```

**Response Schema**:
```typescript
{
  complexity_metrics: Array<{
    function_name: string;
    complexity: number;
    line_number: number;
    exceeds_threshold: boolean;
    refactoring_suggestion?: string;
  }>;
  summary: {
    total_functions: number;
    avg_complexity: number;
    violations: number;
  };
}
```

---

### Task Type 11: detect-duplicates

Find duplicate code blocks using AST analysis.

**Payload Schema**:
```typescript
{
  file_path?: string;
  code?: string;
  similarity_threshold?: number;   // Default: 0.8 (80% similar)
  min_lines?: number;              // Minimum lines to consider (default: 5)
}
```

**Example Request**:
```python
task = Task(
    task_id="ca-003",
    task_type="detect-duplicates",
    description="Find duplicate code in service layer",
    payload={
        "file_path": "src/services/*.py",
        "similarity_threshold": 0.85,
        "min_lines": 6
    }
)
```

**Response Schema**:
```typescript
{
  duplicates: Array<{
    locations: Array<{
      file: string;
      start_line: number;
      end_line: number;
    }>;
    similarity: number;
    code_snippet: string;
    refactoring_suggestion: string;
  }>;
  total_duplicates: number;
}
```

---

### Task Type 12: analyze-dependencies

Analyze import dependencies and circular references.

**Payload Schema**:
```typescript
{
  file_path?: string;
  code?: string;
  check_circular?: boolean;        // Default: true
  check_unused?: boolean;          // Default: true
}
```

**Example Request**:
```python
task = Task(
    task_id="ca-004",
    task_type="analyze-dependencies",
    description="Check for circular imports",
    payload={
        "file_path": "src/",
        "check_circular": True,
        "check_unused": True
    }
)
```

**Response Schema**:
```typescript
{
  dependencies: {
    direct: string[];
    indirect: string[];
    circular: Array<{
      cycle: string[];
      severity: 'critical' | 'warning';
    }>;
    unused: string[];
  };
  dependency_graph: string;        // DOT format graph
}
```

---

## Infrastructure Operations Agent

**Agent ID**: `infrastructure-ops`
**Princess**: Princess-Coordination
**Keywords**: `kubernetes`, `k8s`, `docker`, `cloud`, `deploy`, `infrastructure`

### Task Type 13: deploy-infrastructure

Deploy applications to cloud infrastructure.

**Payload Schema**:
```typescript
{
  platform: 'kubernetes' | 'docker' | 'aws' | 'gcp' | 'azure';
  app_name: string;                // Required
  image?: string;                  // Docker image
  replicas?: number;               // For K8s (default: 3)
  port?: number;
  environment_variables?: Record<string, string>;
  resources?: {
    cpu: string;                   // e.g., "500m"
    memory: string;                // e.g., "256Mi"
  };
}
```

**Example Request**:
```python
task = Task(
    task_id="io-001",
    task_type="deploy-infrastructure",
    description="Deploy web app to Kubernetes",
    payload={
        "platform": "kubernetes",
        "app_name": "web-app",
        "image": "myregistry/web-app:v1.2.0",
        "replicas": 3,
        "port": 8080,
        "environment_variables": {
            "DATABASE_URL": "postgres://...",
            "REDIS_URL": "redis://..."
        },
        "resources": {
            "cpu": "500m",
            "memory": "512Mi"
        }
    }
)
```

**Response Schema**:
```typescript
{
  manifests: Record<string, string>;  // K8s YAML manifests
  deployment_commands: string[];
  service_url?: string;
  monitoring_setup?: string;
}
```

---

### Task Type 14: scale-infrastructure

Scale existing deployments.

**Payload Schema**:
```typescript
{
  resource: string;                // Resource to scale (deployment/statefulset)
  replicas?: number;               // Target replica count
  auto_scaling?: {
    min_replicas: number;
    max_replicas: number;
    cpu_threshold: number;
    memory_threshold: number;
  };
  platform: 'kubernetes' | 'docker-swarm';
}
```

**Example Request**:
```python
task = Task(
    task_id="io-002",
    task_type="scale-infrastructure",
    description="Setup autoscaling for API",
    payload={
        "resource": "deployment/api-server",
        "auto_scaling": {
            "min_replicas": 2,
            "max_replicas": 10,
            "cpu_threshold": 70,
            "memory_threshold": 80
        },
        "platform": "kubernetes"
    }
)
```

**Response Schema**:
```typescript
{
  commands: string[];
  config: string;                  // HPA/autoscaling config
  monitoring_metrics: string[];
}
```

---

### Task Type 15: monitor-infrastructure

Setup infrastructure monitoring.

**Payload Schema**:
```typescript
{
  monitoring_type: 'prometheus' | 'grafana' | 'cloudwatch' | 'datadog';
  targets: string[];               // Services to monitor
  metrics?: string[];              // Specific metrics
  alerts?: Array<{
    metric: string;
    threshold: number;
    severity: 'critical' | 'warning';
  }>;
}
```

**Example Request**:
```python
task = Task(
    task_id="io-003",
    task_type="monitor-infrastructure",
    description="Setup Prometheus monitoring",
    payload={
        "monitoring_type": "prometheus",
        "targets": ["web-app", "api-server", "database"],
        "metrics": ["cpu", "memory", "request_rate", "error_rate"],
        "alerts": [
            {"metric": "error_rate", "threshold": 5, "severity": "critical"},
            {"metric": "cpu", "threshold": 85, "severity": "warning"}
        ]
    }
)
```

**Response Schema**:
```typescript
{
  config: string;                  // Prometheus config
  dashboards?: string;             // Grafana dashboards
  alert_rules: string;
  installation_steps: string[];
}
```

---

### Task Type 16: configure-infrastructure

Configure infrastructure settings.

**Payload Schema**:
```typescript
{
  config_type: 'network' | 'security' | 'storage' | 'compute';
  platform: string;
  settings: Record<string, any>;
}
```

**Example Request**:
```python
task = Task(
    task_id="io-004",
    task_type="configure-infrastructure",
    description="Configure network policies",
    payload={
        "config_type": "network",
        "platform": "kubernetes",
        "settings": {
            "allow_ingress": ["web-app"],
            "deny_egress": ["database"],
            "service_mesh": "istio"
        }
    }
)
```

**Response Schema**:
```typescript
{
  config_files: Record<string, string>;
  apply_commands: string[];
  validation_steps: string[];
}
```

---

## Release Manager Agent

**Agent ID**: `release-manager`
**Princess**: Princess-Coordination
**Keywords**: `release`, `version`, `changelog`, `tag`, `deploy`

### Task Type 17: prepare-release

Prepare a new release with version bumping.

**Payload Schema**:
```typescript
{
  current_version?: string;
  release_type: 'major' | 'minor' | 'patch';
  version?: string;                // Or specify exact version
  pre_release?: boolean;           // Alpha/beta release
}
```

**Example Request**:
```python
task = Task(
    task_id="rm-001",
    task_type="prepare-release",
    description="Prepare minor release",
    payload={
        "current_version": "1.5.3",
        "release_type": "minor"
    }
)
```

**Response Schema**:
```typescript
{
  new_version: string;             // e.g., "1.6.0"
  release_notes_template: string;
  checklist: string[];             // Pre-release checklist
  files_to_update: string[];
}
```

---

### Task Type 18: generate-changelog

Generate changelog from commit history.

**Payload Schema**:
```typescript
{
  from_version?: string;
  to_version?: string;
  commits?: Array<{
    message: string;
    hash: string;
    author?: string;
    date?: string;
  }>;
  format?: 'markdown' | 'keepachangelog' | 'conventional';
}
```

**Example Request**:
```python
task = Task(
    task_id="rm-002",
    task_type="generate-changelog",
    description="Generate changelog for v2.0.0",
    payload={
        "from_version": "1.5.0",
        "to_version": "2.0.0",
        "commits": [
            {"message": "feat: add user authentication", "hash": "abc123"},
            {"message": "fix: resolve memory leak", "hash": "def456"},
            {"message": "docs: update API documentation", "hash": "ghi789"}
        ],
        "format": "keepachangelog"
    }
)
```

**Response Schema**:
```typescript
{
  changelog: string;               // Formatted changelog
  categories: {
    features: string[];
    bug_fixes: string[];
    breaking_changes: string[];
    documentation: string[];
  };
}
```

---

### Task Type 19: tag-release

Create and push git release tags.

**Payload Schema**:
```typescript
{
  version: string;                 // Required: Version to tag
  message?: string;                // Tag message
  signed?: boolean;                // GPG sign tag (default: false)
  push?: boolean;                  // Push to remote (default: false)
}
```

**Example Request**:
```python
task = Task(
    task_id="rm-003",
    task_type="tag-release",
    description="Tag v2.0.0 release",
    payload={
        "version": "2.0.0",
        "message": "Release version 2.0.0 - Major update with new features",
        "signed": True,
        "push": True
    }
)
```

**Response Schema**:
```typescript
{
  tag_command: string;
  push_command?: string;
  tag_name: string;
  success_message: string;
}
```

---

### Task Type 20: coordinate-deployment

Coordinate multi-environment deployments.

**Payload Schema**:
```typescript
{
  version: string;
  environments: string[];          // ['staging', 'production']
  strategy: 'blue-green' | 'rolling' | 'canary';
  rollback_plan?: boolean;         // Default: true
  approval_required?: boolean;
}
```

**Example Request**:
```python
task = Task(
    task_id="rm-004",
    task_type="coordinate-deployment",
    description="Deploy v2.0.0 with canary strategy",
    payload={
        "version": "2.0.0",
        "environments": ["staging", "production"],
        "strategy": "canary",
        "rollback_plan": True,
        "approval_required": True
    }
)
```

**Response Schema**:
```typescript
{
  deployment_plan: {
    stages: Array<{
      environment: string;
      steps: string[];
      estimated_duration: string;
    }>;
  };
  rollback_procedure: string;
  verification_steps: string[];
}
```

---

## Performance Engineer Agent

**Agent ID**: `performance-engineer`
**Princess**: Princess-Coordination
**Keywords**: `performance`, `profiling`, `optimize`, `benchmark`, `bottleneck`

### Task Type 21: profile-performance

Profile application/function performance.

**Payload Schema**:
```typescript
{
  target: string;                  // Function/endpoint to profile
  metrics: string[];               // ['cpu', 'memory', 'io', 'network']
  duration_seconds?: number;       // Profiling duration
  detail_level?: 'high' | 'medium' | 'low';
}
```

**Example Request**:
```python
task = Task(
    task_id="pe-001",
    task_type="profile-performance",
    description="Profile API endpoint performance",
    payload={
        "target": "api/v1/users",
        "metrics": ["cpu", "memory", "io"],
        "duration_seconds": 60,
        "detail_level": "high"
    }
)
```

**Response Schema**:
```typescript
{
  profile_results: {
    duration_ms: number;
    cpu_time_ms: number;
    memory_mb: number;
    io_operations: number;
    hot_spots: Array<{
      function: string;
      line: number;
      time_ms: number;
      percentage: number;
    }>;
  };
  visualization?: string;          // Flame graph data
}
```

---

### Task Type 22: detect-bottlenecks

Identify performance bottlenecks.

**Payload Schema**:
```typescript
{
  system: string;                  // System/service to analyze
  metrics?: {
    response_time?: number;
    throughput?: number;
    error_rate?: number;
    cpu_usage?: number;
    memory_usage?: number;
  };
  analysis_period?: string;        // e.g., "1h", "24h"
}
```

**Example Request**:
```python
task = Task(
    task_id="pe-002",
    task_type="detect-bottlenecks",
    description="Find database query bottlenecks",
    payload={
        "system": "database_layer",
        "metrics": {
            "response_time": 500,
            "cpu_usage": 85,
            "memory_usage": 90
        },
        "analysis_period": "24h"
    }
)
```

**Response Schema**:
```typescript
{
  bottlenecks: Array<{
    component: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    description: string;
    impact: string;
    affected_metrics: string[];
  }>;
  priority_ranking: string[];
}
```

---

### Task Type 23: optimize-performance

Provide optimization recommendations.

**Payload Schema**:
```typescript
{
  target: string;                  // What to optimize
  current_performance: {
    metric: string;
    value: number;
  };
  target_performance?: {
    metric: string;
    value: number;
  };
  bottleneck_type?: 'cpu' | 'memory' | 'io' | 'network';
}
```

**Example Request**:
```python
task = Task(
    task_id="pe-003",
    task_type="optimize-performance",
    description="Optimize slow data processing",
    payload={
        "target": "data_processor",
        "current_performance": {
            "metric": "execution_time",
            "value": 5000  # 5 seconds
        },
        "target_performance": {
            "metric": "execution_time",
            "value": 1000  # 1 second
        },
        "bottleneck_type": "cpu"
    }
)
```

**Response Schema**:
```typescript
{
  optimizations: Array<{
    strategy: string;
    description: string;
    expected_improvement: string;  // e.g., "60% faster"
    implementation_effort: 'low' | 'medium' | 'high';
    code_example?: string;
  }>;
  priority_order: string[];
}
```

---

### Task Type 24: benchmark-system

Run performance benchmarks.

**Payload Schema**:
```typescript
{
  system: string;
  test_cases: Array<{
    name: string;
    endpoint?: string;
    method?: string;
    load?: number;                 // Concurrent requests
  }>;
  baseline?: Record<string, number>;  // Compare against baseline
  duration_seconds?: number;
}
```

**Example Request**:
```python
task = Task(
    task_id="pe-004",
    task_type="benchmark-system",
    description="Benchmark API under load",
    payload={
        "system": "rest_api",
        "test_cases": [
            {"name": "get_users", "endpoint": "/api/users", "method": "GET", "load": 100},
            {"name": "create_user", "endpoint": "/api/users", "method": "POST", "load": 50}
        ],
        "baseline": {
            "avg_response_ms": 100,
            "p95_response_ms": 150,
            "throughput_rps": 500
        },
        "duration_seconds": 300
    }
)
```

**Response Schema**:
```typescript
{
  benchmark_results: {
    test_cases: Array<{
      name: string;
      avg_response_ms: number;
      p50_response_ms: number;
      p95_response_ms: number;
      p99_response_ms: number;
      throughput_rps: number;
      error_rate: number;
    }>;
  };
  comparison?: {
    regression: boolean;
    changes: Record<string, string>;
  };
  recommendations: string[];
}
```

---

## Common Response Fields

All task executions return a `Result` object with:

```typescript
{
  success: boolean;
  data: any;                       // Task-specific data
  message: string;
  execution_time_ms: number;
  metadata: {
    agent_id: string;
    task_id: string;
    timestamp: string;
  };
}
```

## Error Handling

All agents handle errors gracefully and return:

```typescript
{
  success: false;
  message: string;                 // Error description
  error_type: string;              // 'validation' | 'execution' | 'system'
  recovery_suggestion?: string;
}
```

---

**Version**: 1.0
**Last Updated**: 2025-10-10
**Total Task Types**: 24
**Total Agents**: 6
