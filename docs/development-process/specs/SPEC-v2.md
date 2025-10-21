# SPEK Platform v2 - Requirements Specification v2

**Version**: 2.0
**Date**: 2025-10-08
**Status**: Active - Iteration 2
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild

**Changes from v1**: Incorporates pre-mortem risk mitigations, FSM decision matrix, phased rollout, sandbox validation, and cost tracking

---

## 1. Project Overview

### 1.1 Purpose
Rebuild SPEK (Specification, Research, Planning, Execution, Knowledge) platform from ground up with:
- **Risk-mitigated FSM-first architecture** (decision matrix prevents over-engineering)
- Multi-AI platform optimization with circuit breakers and fallback chains
- Queen-Princess-Drone swarm coordination with event-driven async communication
- Production-ready quality gates with sandbox validation and immutable evidence
- Zero technical debt with pragmatic NASA compliance

### 1.2 Scope
**In Scope**:
- Complete type system rewrite (TypeScript strict mode)
- **Phased agent implementation**: 5 core → 4 swarm → 13 specialized (22 total, not 85)
- 15+ containerized MCP servers with gVisor security
- 3-loop development system (Planning, Development, Quality)
- Theater detection with 6-factor scoring and sandbox validation
- NASA POT10 compliance automation (pragmatic, not dogmatic)
- GitHub integration (SPEC KIT, CI/CD, PRs)
- Cost tracking with daily/monthly budgets

**Out of Scope** (Future Phases):
- Remaining 63 agent implementations (deferred)
- Web UI dashboard
- Multi-user collaboration features
- Cloud deployment infrastructure
- Enterprise SSO integration

### 1.3 Success Criteria
- Zero TypeScript compilation errors
- 100% command success rate (30/30 commands functional)
- >=92% NASA compliance (with pragmatic exceptions)
- >=30% FSM coverage (not 90%, decision matrix prevents over-engineering)
- >=80% test coverage
- <60 theater detection score (genuine work only)
- **NEW**: 22 agents functional (5 core + 4 swarm + 13 specialized)
- **NEW**: Sandbox validation operational with gVisor
- **NEW**: Cost tracking within budget ($50/day, $1,500/month)

---

## 2. Functional Requirements

### 2.1 FSM-First Architecture with Decision Matrix

**REQ-FSM-001**: FSM Decision Matrix MUST determine when to use FSMs
```typescript
interface FSMDecisionCriteria {
  hasMultipleStates: boolean;        // >=3 distinct states
  hasComplexTransitions: boolean;    // >=5 possible transitions
  needsErrorRecovery: boolean;       // Requires rollback capability
  requiresAuditTrail: boolean;       // Compliance/governance need
}

// Use FSM if >=3 criteria are true
// Otherwise use simple functions/classes
```

**REQ-FSM-002**: Features requiring FSMs (Complex State Management)
- User authentication flows (login, logout, password reset)
- Multi-step workflows (3-loop system, swarm deployment)
- Agent lifecycle management (idle, executing, monitoring, error)
- Network connection handling (connecting, connected, reconnecting, disconnected)
- Queen orchestrator coordination
- Princess domain management

**REQ-FSM-003**: Features NOT requiring FSMs (Simple Operations)
- Utility functions (string formatting, math operations)
- Data transformations (map, filter, reduce)
- Configuration loading
- Logging and monitoring
- File operations (read, write, copy)

**REQ-FSM-004**: State contracts for FSM implementations
```typescript
interface StateContract {
  init(): Promise<void>;
  update(event: Event): Promise<TransitionResult>;
  shutdown(): Promise<void>;
  checkInvariants(): Promise<boolean>;
}
```

**REQ-FSM-005**: FSM implementation rules
- States defined as enums (NO string states)
- Events defined as enums (NO string events)
- One file per state (max 200 LOC per file)
- Centralized TransitionHub for all state changes
- Event-driven communication only
- No cross-state global variables

**Mitigation**: Prevents Pre-mortem Failure #1 (FSM Over-Engineering, Risk Score 684)

### 2.2 NASA Rule 10 Compliance (Pragmatic)

**REQ-NASA-001**: Functions MUST be <=60 lines (ESLint enforced)
- Exception process for rare cases requiring explicit justification
- Approved exceptions documented with reviewer and date

**REQ-NASA-002**: Assertions required for critical paths only
```typescript
// ✅ GOOD: Assertions for complex validation
async function validateAuthToken(token: string): Promise<boolean> {
  assert(token.length > 0, "Token cannot be empty");
  assert(token.length <= 512, "Token exceeds max length");

  const decoded = await decodeJWT(token);
  assert(decoded !== null, "Token decode must not return null");

  return !isExpired(decoded) && isValidUser(decoded);
}

// ✅ ALSO GOOD: Simple utilities without assertions
function formatDate(date: Date): string {
  return date.toISOString();  // TypeScript type safety sufficient
}

// ❌ BAD: Assertion overkill on trivial code
function add(a: number, b: number): number {
  assert(typeof a === "number");  // TypeScript already validates
  assert(typeof b === "number");  // Redundant
  return a + b;
}
```

**REQ-NASA-003**: Use assertions for
- External input validation
- Invariant checking in complex logic
- Post-condition validation
- Pre-conditions for critical operations

**REQ-NASA-004**: Skip assertions for
- Type-checked parameters (TypeScript handles it)
- Trivial operations (formatting, simple math)
- Internal helper functions with controlled inputs

**REQ-NASA-005**: NO recursion allowed (ESLint enforced)
- Use iterative algorithms with explicit loop bounds

**REQ-NASA-006**: All loops MUST have fixed bounds
- NO `while(true)` or infinite loops
- Maximum iteration count defined at compile time

**REQ-NASA-007**: All non-void returns MUST be checked
- TypeScript strict mode + ESLint enforcement

**Mitigation**: Prevents Pre-mortem Failure #8 (NASA Compliance Fatigue, Risk Score 441)

### 2.3 Multi-AI Platform Integration with Resilience

**REQ-AI-001**: Platform Abstraction Layer MUST provide failover
```typescript
interface PlatformAbstractionLayer {
  execute(task: Task, platform: Platform): Promise<Result>;
  getFallback(platform: Platform): Platform[];
  checkHealth(platform: Platform): Promise<HealthStatus>;
}
```

**REQ-AI-002**: Circuit breaker per platform
```typescript
class PlatformCircuitBreaker {
  private failureCount = 0;
  private readonly threshold = 3;
  private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === "OPEN") {
      throw new Error("Circuit breaker is OPEN - using fallback");
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    if (this.failureCount >= this.threshold) {
      this.state = "OPEN";
      setTimeout(() => this.state = "HALF_OPEN", 60000);
    }
  }

  private onSuccess(): void {
    this.failureCount = 0;
    this.state = "CLOSED";
  }
}
```

**REQ-AI-003**: Fallback chain definitions
- **Research tasks**: Gemini Pro → Claude Sonnet → GPT-4 → Local cache
- **Coding tasks**: Codex → Claude Opus → GPT-5 → Local templates
- **Review tasks**: Claude Opus → Gemini Pro → GPT-4 → Static analysis
- **Coordination tasks**: Claude Sonnet → Gemini Flash → GPT-4

**REQ-AI-004**: Platform health checks
- Timeout: 30-60 seconds per operation
- Health check interval: Every 5 minutes
- Automatic fallback on 3 consecutive failures

**REQ-AI-005**: Gemini stuck thinking mitigation
```bash
# Force Flash model for speed-critical tasks
export GEMINI_MODEL="gemini-2.5-flash"

# Disable thinking mode
--thinking-budget 0

# MCP server timeout
timeout 60s gemini-cli ...
```

**REQ-AI-006**: Platform distribution strategy
- **Gemini 2.5 Pro/Flash**: Research, planning, large-context (1M tokens, free tier)
- **GPT-5 Codex**: Autonomous coding, browser automation (7+ hours)
- **Claude Opus 4.1**: Quality analysis, code review (72.7% SWE-bench)
- **Claude Sonnet 4**: Coordination, sequential thinking

**REQ-AI-007**: Intelligent prompt caching (90% savings target)
```typescript
interface PromptTemplate {
  cachedBase: string;     // System prompt + codebase context (cached)
  dynamicInput: string;   // User query (not cached)
}

// Separate cacheable from dynamic content
const template: PromptTemplate = {
  cachedBase: `
    You are a TypeScript expert working on SPEK platform.

    Codebase structure: ${fileTree}
    Coding standards: ${codingStandards}
    Architecture: ${architectureGuide}
  `,  // This part gets 90% discount

  dynamicInput: `Implement: ${userQuery}`  // Full price
};
```

**REQ-AI-008**: Target cache hit rate: 70-85%

**Mitigation**: Prevents Pre-mortem Failure #2 (Platform Coordination Breakdown, Risk Score 660)

### 2.4 Queen-Princess-Drone Hierarchy with Event-Driven Communication

**REQ-SWARM-001**: Queen Orchestrator (500KB context, hard limit)
- Byzantine consensus protocols
- MECE task division (Mutually Exclusive, Collectively Exhaustive)
- Cross-hive communication
- **NEW**: Sliding window context management with automatic pruning
- Anti-degradation monitoring

**REQ-SWARM-002**: Sliding window context management
```typescript
class ContextWindowManager {
  private readonly maxSize = 500 * 1024; // 500KB
  private currentSize = 0;

  addContext(content: string): void {
    this.currentSize += content.length;

    if (this.currentSize > this.maxSize) {
      this.pruneOldestContext();  // Remove 25% oldest
    }
  }

  pruneOldestContext(): void {
    // Keep only most recent 75% of context
    const targetSize = this.maxSize * 0.75;
    // FIFO queue, remove oldest entries
  }
}
```

**REQ-SWARM-003**: Six Princess Domains (2MB context each, hard limit)
1. **Development Princess**: Code implementation, refactoring
2. **Quality Princess**: Testing, review, compliance validation
3. **Security Princess**: Vulnerability scanning, audit trails
4. **Research Princess**: Information gathering, solution discovery
5. **Infrastructure Princess**: CI/CD, deployment, monitoring
6. **Coordination Princess**: Task orchestration, resource allocation

**REQ-SWARM-004**: Event-driven communication protocol
```typescript
// NO synchronous cross-Princess calls allowed
interface EventBus {
  publish(event: DomainEvent): Promise<void>;
  subscribe(eventType: string, handler: EventHandler): void;
  unsubscribe(eventType: string, handler: EventHandler): void;
}

// ❌ BAD: Synchronous cross-Princess call
await qualityPrincess.validateCode(code);

// ✅ GOOD: Async event-driven
eventBus.publish({
  type: "CODE_VALIDATION_REQUESTED",
  payload: { code, requestor: "DevelopmentPrincess" }
});

// QualityPrincess subscribes and responds asynchronously
eventBus.subscribe("CODE_VALIDATION_REQUESTED", async (event) => {
  const result = await this.validate(event.payload.code);
  eventBus.publish({
    type: "CODE_VALIDATION_COMPLETED",
    payload: { result, requestId: event.id }
  });
});
```

**REQ-SWARM-005**: Communication rules
- All cross-domain communication via event bus
- Async-first design (no blocking calls)
- Timeout for all cross-domain operations: 30-60 seconds
- No circular dependencies

**REQ-SWARM-006**: Phased agent implementation (NOT 85 at once)

**Phase 2A - 5 Core Agents** (Week 3):
- `coder` (GPT-5 Codex) - Code implementation
- `reviewer` (Claude Opus) - Code review
- `researcher` (Gemini Pro) - Research
- `planner` (Gemini Flash) - Planning
- `tester` (Claude Opus) - Testing

**Phase 2B - 4 Swarm Coordinators** (Week 4):
- `queen-orchestrator` (Claude Sonnet + sequential)
- `development-princess` (Claude Sonnet)
- `quality-princess` (Claude Opus)
- `coordination-princess` (Claude Sonnet)

**Phase 2C - 13 Specialized Agents** (Weeks 5-8):
- Security: `security-manager`, `legal-compliance-checker`
- Research: `researcher-gemini`, `specification`
- Infrastructure: `cicd-engineer`, `devops-automator`
- GitHub: `pr-manager`, `issue-tracker`, `github-modes`
- Testing: `code-analyzer`
- Development: `backend-dev`, `sparc-coder`

**Phase 2D - Remaining 63 Agents** (Future):
- Only implement if Phase 2A-C succeeds
- Evaluate actual need vs initial plan

**REQ-SWARM-007**: Agent implementation requirements
- Full implementation (not facades)
- Real execution logic
- Complete error handling
- Evidence collection
- Agent2Agent (A2A) protocol with Context DNA

**Mitigation**: Prevents Pre-mortem Failure #4 (Agent Communication Deadlock, Risk Score 560) and Failure #7 (Agent Implementation Incompleteness, Risk Score 450)

### 2.5 Quality Gates with Sandbox Validation

**REQ-QUALITY-001**: gVisor sandbox validation MUST prevent fake work
```yaml
# docker-compose-sandbox.yml
version: '3.8'

services:
  sandbox:
    image: spek-sandbox:latest
    runtime: runsc  # gVisor runtime
    security_opt:
      - seccomp:seccomp-profile.json
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,nodev,size=100m
    volumes:
      - ./test-code:/code:ro  # Read-only code
      - ./test-results:/results  # Write-only results
    user: "1001:1001"  # Non-root
    cap_drop:
      - ALL
    networks:
      - isolated
    mem_limit: 512m
    cpus: 1.0
```

**REQ-QUALITY-002**: Sandbox validation process
1. Agent claims completion
2. Code copied to sandbox (read-only)
3. All tests run in isolated gVisor container
4. Results collected (cannot be forged)
5. Evidence validated (screenshots, logs, hashes)

**REQ-QUALITY-003**: Immutable evidence logging
```typescript
interface EvidenceBlock {
  index: number;
  timestamp: number;
  data: Evidence;
  previousHash: string;
  hash: string;
}

class ImmutableAuditLog {
  private chain: EvidenceBlock[] = [];

  append(evidence: Evidence): void {
    const previousBlock = this.chain[this.chain.length - 1];
    const newBlock: EvidenceBlock = {
      index: this.chain.length,
      timestamp: Date.now(),
      data: evidence,
      previousHash: previousBlock ? previousBlock.hash : "0",
      hash: this.calculateHash(evidence)
    };

    this.chain.push(newBlock);
  }

  validate(): boolean {
    for (let i = 1; i < this.chain.length; i++) {
      const current = this.chain[i];
      const previous = this.chain[i - 1];

      // Verify hash chain
      if (current.previousHash !== previous.hash) {
        return false;  // Tampering detected
      }

      // Verify current hash
      if (current.hash !== this.calculateHash(current.data)) {
        return false;  // Tampering detected
      }
    }
    return true;
  }
}
```

**REQ-QUALITY-004**: Multi-dimensional theater detection
- Target: <60 score = theater, >=60 = genuine work

**6-Factor Scoring System**:
1. **Quality Metrics** (25 points): Tests pass, lint clean, types valid, security scan
2. **Evidence Validity** (20 points): Screenshot authenticity, log chronology, hash verification
3. **Change Impact** (15 points): LOC changed, files touched, complexity delta
4. **Test Authenticity** (15 points): Real test execution, coverage increase, edge cases
5. **Temporal Patterns** (15 points): Time distribution, work patterns, outlier detection
6. **Complexity** (10 points): Cognitive complexity, nesting depth, maintainability

```typescript
function calculateTheaterScore(evidence: Evidence): number {
  const qualityScore = assessQualityMetrics(evidence) * 0.25;
  const evidenceScore = validateEvidence(evidence) * 0.20;
  const impactScore = measureImpact(evidence) * 0.15;
  const testScore = validateTests(evidence) * 0.15;
  const temporalScore = analyzePatterns(evidence) * 0.15;
  const complexityScore = assessComplexity(evidence) * 0.10;

  return Math.round(
    qualityScore + evidenceScore + impactScore +
    testScore + temporalScore + complexityScore
  );
}
```

**REQ-QUALITY-005**: NASA compliance validation
- Target: >=92% compliance
- Automated scanning via ESLint plugins
- Pre-commit hooks block violations
- CI/CD pipeline enforcement
- Exception process for justified rare cases

**REQ-QUALITY-006**: Security scanning
- Zero critical vulnerabilities allowed
- <=5 high vulnerabilities allowed
- Bandit for Python
- Semgrep for TypeScript
- OWASP Top 10 compliance

**REQ-QUALITY-007**: Test coverage
- >=80% line coverage required
- >=90% branch coverage for critical paths
- 100% coverage for state transitions
- Jest for TypeScript, pytest for Python

**REQ-QUALITY-008**: FSM coverage
- >=30% of features as state machines (not 90%, decision matrix applied)
- All FSM transitions documented
- Guards implemented for complex transitions
- Error recovery paths defined

**Mitigation**: Prevents Pre-mortem Failure #3 (Quality Gate Bypass, Risk Score 630)

### 2.6 MCP Server Integration with Security

**REQ-MCP-001**: gVisor containerized deployment for all MCP servers
- Docker images for each server
- gVisor runtime (runsc)
- Non-root execution (UID 1001)
- Read-only filesystem
- Version pinning (no auto-updates)
- Vulnerability scanning in CI/CD

**REQ-MCP-002**: Required MCP servers (15+ total)
- **claude-flow**: 87 tools for swarm orchestration
- **memory**: Persistent knowledge graphs
- **sequential-thinking**: Enhanced reasoning for coordination
- **filesystem**: Secure file operations (restricted directories)
- **github**: Repository management, PR/issue tracking
- **playwright**: Browser automation and testing
- **puppeteer**: Advanced browser automation
- **eva**: Performance evaluation and quality metrics
- **figma**: Design system integration
- **deepwiki**: GitHub repo documentation
- **firecrawl**: Web scraping
- **ref**: Technical references
- **context7**: Live documentation
- **markitdown**: Markdown conversion
- **desktop-automation**: Bytebot bridge for desktop apps

**REQ-MCP-003**: Security requirements
- OAuth 2.0 Resource Server pattern (MCP Spec v2025-06-18)
- Allowed directories: /src, /tests, /docs, /config, /scripts, /examples
- No internet-exposed MCP servers without authentication
- Policy enforcement via Open Policy Agent (OPA)
- Network isolation (no internet access by default)
- Resource limits (CPU, memory, disk)

**REQ-MCP-004**: MCP server configuration
```yaml
security:
  user: "1001:1001"  # Non-root
  read_only_root_filesystem: true
  cap_drop:
    - ALL
  seccomp_profile: seccomp-mcp.json
  network_mode: isolated

resources:
  memory: 500m
  cpu: 0.5

volumes:
  - /allowed/paths:/data:ro  # Read-only allowed directories
```

**Mitigation**: Prevents Pre-mortem Failure #6 (MCP Server Security Breach, Risk Score 480)

### 2.7 3-Loop Development System

**REQ-LOOP-001**: Loop 1 - Planning & Research
- **Input**: Requirements, SPEC.md
- **Process**: Research → Pre-mortem (4 iterations) → Risk-mitigated plan
- **Output**: PLAN.md, risk register, research synthesis
- **Tools**: /research:web, /research:github, /pre-mortem-loop
- **AI**: Gemini 2.5 Pro (1M context for research)

**REQ-LOOP-002**: Loop 2 - Development & Implementation
- **Input**: PLAN.md, task definitions
- **Process**: Queen-Princess-Drone deployment → MECE division → Sandbox validation → Theater detection
- **Output**: Implemented code, test suite, documentation
- **Tools**: /dev:swarm, 22 agents (phased), MECE task division
- **AI**: Multi-platform (Gemini, Codex, Claude based on task)
- **NEW**: Sandbox validation with gVisor for all completions

**REQ-LOOP-003**: Loop 3 - Quality & Debugging
- **Input**: Implemented code
- **Process**: npm test, lint, typecheck, security scan → Failure analysis → Auto-remediation
- **Output**: Quality report, GitHub artifacts, 100% passing tests
- **Tools**: /qa:run, /theater:scan, /reality:check
- **AI**: Claude Opus (quality validation)
- **NEW**: Immutable audit trail with digital signatures

**REQ-LOOP-004**: Flow patterns
- **Forward flow**: Loop 1 → Loop 2 → Loop 3 (new projects)
- **Reverse flow**: Loop 3 → Loop 1 → Loop 2 → Loop 3 (existing codebases)
- **Convergence**: Automatic detection when quality goals met

### 2.8 Command System

**REQ-CMD-001**: 30 slash commands MUST be functional
- Success rate: 100% (vs 23% in v1)
- Real script execution (not templates)
- Evidence validation
- Rollback on failure with max 3 retries

**REQ-CMD-002**: Command categories
- Research & Discovery (5 commands)
- Planning & Architecture (6 commands)
- Implementation (3 commands)
- Quality Assurance (5 commands)
- Analysis & Architecture (5 commands)
- Project Management (2 commands)
- Memory & System (2 commands)

**REQ-CMD-003**: Command validation
- Pre-execution checks (permissions, dependencies)
- Post-execution validation (success criteria)
- Error recovery with exponential backoff
- Audit trail with evidence

### 2.9 GitHub Integration

**REQ-GITHUB-001**: SPEC KIT integration
- /specify command for SPEC.md generation
- /plan command for plan.json creation
- /tasks command for actionable task lists
- /implement command for execution

**REQ-GITHUB-002**: CI/CD integration
- GitHub Actions workflows for all quality gates
- Automatic PR creation with evidence packages
- Failure analysis and auto-remediation
- Status reporting via GitHub checks

**REQ-GITHUB-003**: Evidence packages
- Test results (npm test output)
- Lint reports (eslint output)
- Security scans (bandit, semgrep SARIF)
- Screenshot captures (Codex browser automation)
- Theater detection reports
- Immutable audit log excerpts

### 2.10 Cost Tracking and Budget Management

**REQ-COST-001**: Daily and monthly cost monitoring
```typescript
interface CostBudget {
  daily: number;    // $50/day
  monthly: number;  // $1,500/month
  alerts: {
    warning: number;  // 75% of budget
    critical: number; // 90% of budget
  };
}
```

**REQ-COST-002**: Cost tracking by platform
```typescript
class CostTracker {
  async getDailySpend(): Promise<PlatformSpend[]> {
    return [
      { platform: "Gemini", cost: 0 },      // Free tier
      { platform: "Codex", cost: 25 },      // Subscription
      { platform: "Claude", cost: 15 },     // API usage
    ];
  }

  async checkBudget(): Promise<BudgetStatus> {
    const spend = await this.getTotalSpend();
    if (spend > this.budget.alerts.critical) {
      this.sendAlert("CRITICAL: 90% budget exceeded");
      this.enableCostSavingMode();  // Switch to free tier when possible
    }
  }
}
```

**REQ-COST-003**: Cost optimization strategies
- Maximize Gemini free tier usage
- Prompt caching for repeated context (90% savings target)
- Automatic fallback to cheaper models when appropriate
- Alert thresholds: 75% warning, 90% critical

**REQ-COST-004**: Target metrics
- Cost per agent task: $0.10
- Cache hit rate: 70-85%
- Daily spend: <$50
- Monthly spend: <$1,500

**Mitigation**: Prevents Pre-mortem Failure #9 (Cost Overruns, Risk Score 420)

---

## 3. Non-Functional Requirements

### 3.1 Performance

**REQ-PERF-001**: Response time requirements
- Simple operations: <=2 seconds
- Complex single-agent tasks: <=30 seconds
- Multi-agent coordination: <=60 seconds
- Full 3-loop iteration: <=10 minutes
- **NEW**: Platform failover time: <=5 seconds

**REQ-PERF-002**: Parallelization
- Target: 2.8-4.4x speed improvement (vs sequential)
- Implementation: Parallel swarm execution
- Constraint: Max 25 concurrent agents (Claude Flow limit)

**REQ-PERF-003**: Resource optimization
- Queen context: 500KB max (hard limit, automatic pruning)
- Princess context: 2MB max (hard limit, automatic pruning)
- Drone context: 100KB max
- MCP server memory: <500MB per container

**REQ-PERF-004**: Context management
- Sliding window with FIFO pruning
- Automatic context pruning at 100% capacity
- Keep 75% most recent content after pruning

**Mitigation**: Prevents Pre-mortem Failure #5 (Context Window Exhaustion, Risk Score 525)

### 3.2 Reliability

**REQ-REL-001**: Error recovery
- All operations MUST have rollback capability
- Max 3 retry attempts with exponential backoff
- Circuit breaker for failing external services (3 consecutive failures)
- Graceful degradation if AI platform unavailable
- **NEW**: Platform abstraction layer with fallback chains

**REQ-REL-002**: Byzantine fault tolerance
- Queen consensus protocols handle Byzantine failures
- Princess validation gates catch malicious outputs
- Drone sandboxing prevents system contamination
- gVisor isolation for all untrusted code execution

**REQ-REL-003**: Data persistence
- All state changes logged to filesystem
- MCP memory server for cross-session knowledge
- Version footers on all files (SHA-256 hashing)
- **NEW**: Immutable audit trail with tamper detection

### 3.3 Maintainability

**REQ-MAINT-001**: Code organization
- Single Responsibility Principle
- Dependency injection throughout
- **NEW**: Event-driven communication (no synchronous cross-domain)
- Clear bounded contexts

**REQ-MAINT-002**: Documentation requirements
- All functions have JSDoc comments
- Architecture decision records (ADRs)
- README.md in every major directory
- API documentation generated from TypeScript

**REQ-MAINT-003**: Testing requirements
- Unit tests for all state machines
- Integration tests for agent communication
- E2E tests for 3-loop workflows
- Performance benchmarks tracked over time

### 3.4 Security

**REQ-SEC-001**: MCP server security
- gVisor container isolation for all servers
- Non-root execution (UID 1001)
- Network policies (no internet access by default)
- Secrets management via environment variables
- Read-only filesystem
- Resource limits enforced

**REQ-SEC-002**: Code scanning
- Bandit for Python (OWASP compliance)
- Semgrep for TypeScript (OWASP Top 10)
- Dependency scanning (npm audit, safety)
- SARIF output for GitHub Security tab

**REQ-SEC-003**: Audit trails
- All agent actions logged with timestamps
- Model attribution (which AI made which change)
- Evidence collection (screenshots, logs, output)
- **NEW**: Immutable logging with blockchain-inspired hash chains

### 3.5 Scalability

**REQ-SCALE-001**: Agent scaling
- Support for 22 concurrent agents (phased rollout)
- Dynamic agent spawning based on workload
- Resource pooling for MCP servers
- Load balancing across AI platforms

**REQ-SCALE-002**: Project scaling
- Support codebases up to 1M LOC
- Efficient context windowing (1M tokens for Gemini)
- Incremental processing for large files
- Parallel analysis across domains

---

## 4. Technical Constraints

### 4.1 Language & Runtime

**CONSTRAINT-TECH-001**: TypeScript strict mode
- `strict: true` in tsconfig.json
- No `any` types without explicit annotation
- Null safety enforced
- Readonly properties where applicable

**CONSTRAINT-TECH-002**: Node.js version
- Minimum: v20.17.0
- Target: LTS releases only
- No experimental features

**CONSTRAINT-TECH-003**: Python version
- Minimum: 3.12.5
- Type hints required for all functions
- Black formatting enforced

### 4.2 File Organization

**CONSTRAINT-FILE-001**: NO files in project root
- All code in /src
- All tests in /tests
- All docs in /docs
- All scripts in /scripts

**CONSTRAINT-FILE-002**: ASCII only (NO Unicode)
- No emojis in code or comments
- ASCII art for diagrams where needed
- UTF-8 encoding for internationalization strings only

**CONSTRAINT-FILE-003**: File size limits
- TypeScript files: <=200 LOC
- Python files: <=300 LOC
- Markdown files: No limit
- Exception: Generated files

### 4.3 Dependency Management

**CONSTRAINT-DEP-001**: Version pinning
- Exact versions in package.json (no ^ or ~)
- Lock files committed (package-lock.json, poetry.lock)
- Security scanning on all dependencies

**CONSTRAINT-DEP-002**: Minimal dependencies
- Justify every dependency
- Prefer standard library where possible
- NO unused dependencies

### 4.4 Quality Standards

**CONSTRAINT-QUAL-001**: NO TODOs or placeholders
- All code production-ready
- NO "implement later" comments
- NO mock implementations

**CONSTRAINT-QUAL-002**: Version footers mandatory
- All files MUST have Version & Run Log footer
- SHA-256 content hash (first 7 chars, exclude footer)
- Agent/model attribution
- Change summary with timestamp

---

## 5. Success Metrics

### 5.1 Technical Metrics

| Metric | Current (v1) | Target (v2) | Priority |
|--------|-------------|-------------|----------|
| TypeScript Errors | 951 | 0 | P0 |
| Command Success Rate | 23% | 100% | P0 |
| NASA Compliance | Unknown | >=92% | P0 |
| FSM Coverage | 0% | >=30% | P1 |
| Test Coverage | Unknown | >=80% | P1 |
| Core Agents | 0 | 5 functional | P0 |
| Swarm Coordinators | 0 | 4 functional | P0 |
| Specialized Agents | Facades | 13 functional | P1 |
| Theater Detection | Basic | <60 score | P1 |

### 5.2 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Simple Operation Response | <=2s | End-to-end latency |
| Multi-Agent Coordination | <=60s | Full swarm deployment |
| Build Time | <=30s | npm run build |
| Test Suite Execution | <=2min | npm test |
| Parallel Speedup | 2.8-4.4x | vs sequential execution |
| Platform Failover Time | <=5s | Circuit breaker activation |

### 5.3 Quality Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Security Critical Vulnerabilities | 0 | Bandit + Semgrep |
| Security High Vulnerabilities | <=5 | Bandit + Semgrep |
| Code Duplication | <=5% | SonarQube analysis |
| Cyclomatic Complexity | <=10 per function | ESLint plugin |
| God Objects | 0 | Architectural review |

### 5.4 Cost Metrics (NEW)

| Metric | Budget | Measurement |
|--------|--------|-------------|
| Daily Spend | $50 | Cost tracker |
| Monthly Spend | $1,500 | Cost tracker |
| Cost Per Agent Task | $0.10 | Per-task tracking |
| Cache Hit Rate | 70-85% | Prompt caching stats |

---

## 6. Acceptance Criteria

### Phase 1 Completion (Weeks 1-2)
- [ ] Zero TypeScript compilation errors
- [ ] FSM decision matrix implemented
- [ ] 5 core FSMs implemented (auth, Queen, Princess, Drone, 3-loop)
- [ ] TransitionHub operational
- [ ] NASA Rule 10 ESLint rules active with exception process

### Phase 2 Completion (Weeks 3-4)
- [ ] Platform abstraction layer with circuit breakers
- [ ] 5 core agents implemented (coder, reviewer, researcher, planner, tester)
- [ ] 4 swarm coordinators functional (Queen, dev Princess, quality Princess, coordination Princess)
- [ ] Event bus architecture operational
- [ ] Prompt caching achieving 70-85% hit rate

### Phase 3 Completion (Weeks 5-6)
- [ ] gVisor sandbox validation operational
- [ ] Immutable audit log with tamper detection
- [ ] Context window management with automatic pruning
- [ ] 13 specialized agents deployed

### Phase 4 Completion (Weeks 7-8)
- [ ] Theater detection operational (6-factor scoring)
- [ ] NASA compliance >=92%
- [ ] FSM coverage >=30%
- [ ] Security scans clean
- [ ] Cost tracking within budget

### Phase 5 Completion (Weeks 9-10)
- [ ] Loop 1 (Planning) functional
- [ ] Loop 2 (Development) functional with sandbox
- [ ] Loop 3 (Quality) functional with immutable logging
- [ ] Forward and reverse flows tested

### Phase 6 Completion (Weeks 11-12)
- [ ] >=80% test coverage
- [ ] All quality gates passing
- [ ] Production validation complete
- [ ] Documentation finalized

---

## 7. Risk Mitigation Summary

### Addressed Pre-mortem Failures

1. **FSM Over-Engineering** (Risk 684) → **MITIGATED**
   - FSM decision matrix with clear criteria
   - 5 core FSMs only in Phase 1
   - Validation before expansion

2. **Platform Coordination Breakdown** (Risk 660) → **MITIGATED**
   - Platform abstraction layer with circuit breakers
   - Fallback chains for all platforms
   - Health checks and timeouts

3. **Quality Gate Bypass** (Risk 630) → **MITIGATED**
   - gVisor sandbox validation
   - Immutable audit log with hash chains
   - 6-factor theater detection
   - Evidence cannot be forged

4. **Agent Communication Deadlock** (Risk 560) → **MITIGATED**
   - Event-driven async architecture
   - No synchronous cross-domain calls
   - Timeout for all operations

5. **Context Window Exhaustion** (Risk 525) → **MITIGATED**
   - Sliding window context management
   - Hard limits enforced
   - Automatic pruning at 100% capacity

6. **MCP Server Security Breach** (Risk 480) → **MITIGATED**
   - gVisor container isolation
   - Non-root execution
   - Read-only filesystem
   - Network isolation

7. **Agent Implementation Incompleteness** (Risk 450) → **MITIGATED**
   - Phased rollout: 5 core → 4 swarm → 13 specialized
   - Success criteria per phase
   - No all-or-nothing deployment

8. **NASA Compliance Fatigue** (Risk 441) → **MITIGATED**
   - Pragmatic assertion guidelines
   - Exception process for rare cases
   - Focus on critical paths only

9. **Cost Overruns** (Risk 420) → **MITIGATED**
   - Daily/monthly budget tracking
   - Alert thresholds (75%, 90%)
   - Prompt caching (90% savings)
   - Gemini free tier maximization

10. **Timeline Delays** (Risk 405) → **MITIGATED**
    - Weekly milestones with concrete deliverables
    - Phased agent implementation
    - 63 agents deferred to future

---

## 8. Version & Run Log

| Version | Timestamp | Agent/Model | Change Summary | Status |
|--------:|-----------|-------------|----------------|--------|
| 1.0     | 2025-10-08T09:30:00-04:00 | Claude Sonnet 4 | Initial spec draft | SUPERSEDED |
| 2.0     | 2025-10-08T10:30:00-04:00 | Claude Sonnet 4 | Pre-mortem mitigations integrated | ACTIVE |

### Receipt
- status: OK (iteration 2 of 4)
- reason: Pre-mortem risk mitigations integrated into requirements
- run_id: spec-v2-iteration-2
- inputs: ["SPEC-v1.md", "PLAN-v2.md", "PREMORTEM-v1.md"]
- tools_used: ["analysis", "specification", "requirements", "risk-mitigation"]
- changes: {
    "fsm_requirements": "Added FSM decision matrix (REQ-FSM-001), when to use vs not use",
    "nasa_compliance": "Pragmatic assertions (REQ-NASA-002-007), exception process",
    "platform_integration": "Circuit breakers (REQ-AI-002), fallback chains, health checks, caching strategy",
    "agent_rollout": "Phased implementation (REQ-SWARM-006): 5 core → 4 swarm → 13 specialized",
    "communication": "Event-driven architecture (REQ-SWARM-004), no synchronous cross-domain",
    "context_management": "Sliding window (REQ-SWARM-002), automatic pruning",
    "quality_gates": "gVisor sandbox (REQ-QUALITY-001), immutable audit log (REQ-QUALITY-003), 6-factor theater (REQ-QUALITY-004)",
    "security": "gVisor containerization (REQ-MCP-001), security hardening (REQ-MCP-004)",
    "cost_tracking": "Budget management (REQ-COST-001-004), daily/monthly limits, alert thresholds",
    "metrics": "Updated targets (30% FSM coverage, 22 agents, cost metrics)",
    "acceptance_criteria": "Weekly milestones, phased validation"
  }
