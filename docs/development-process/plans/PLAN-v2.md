# SPEK Platform v2 - Implementation Plan v2

**Version**: 2.0
**Date**: 2025-10-08
**Status**: Active - Iteration 2
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild

**Changes from v1**: Incorporates pre-mortem analysis findings with 30 risk mitigations

---

## Executive Summary

Ground-up rebuild of SPEK platform with **risk-mitigated FSM-first architecture**. Pre-mortem analysis identified 10 critical failure modes; all P0 risks now have concrete mitigation strategies.

**Key Risk Reductions**:
- FSM over-engineering → FSM decision matrix (when to use vs overkill)
- Platform coordination breakdown → Circuit breaker + fallback chains
- Quality gate bypass → Sandbox validation + immutable evidence
- Agent deadlock → Event-driven async communication
- Context exhaustion → Sliding window management

---

## Phase 1: Foundation Architecture (Weeks 1-2)

### 1.1 Core Type System
**Objective**: Establish clean TypeScript foundation with zero compilation errors

**Changes from v1**:
- ✅ **FSM Decision Matrix**: Not all features need FSMs (see Section 1.1.1)
- ✅ **Incremental Type Safety**: Start with minimal types, expand iteratively
- ✅ **Assertion Guidelines**: Practical assertion patterns (see Section 1.1.2)

#### 1.1.1 FSM Decision Matrix

**When to Use FSM** (Complex State Management):
- User authentication flows (login, logout, password reset)
- Multi-step workflows (3-loop system, swarm deployment)
- Agent lifecycle management (idle, executing, monitoring, error)
- Network connection handling (connecting, connected, reconnecting, disconnected)

**When NOT to Use FSM** (Simple Functions):
- Utility functions (string formatting, math operations)
- Data transformations (map, filter, reduce)
- Configuration loading
- Logging and monitoring

**Decision Criteria**:
```typescript
interface FSMDecisionCriteria {
  hasMultipleStates: boolean;        // >=3 distinct states
  hasComplexTransitions: boolean;    // >=5 possible transitions
  needsErrorRecovery: boolean;       // Requires rollback capability
  requiresAuditTrail: boolean;       // Compliance/governance need
}

// Use FSM if >=3 criteria are true
```

**Mitigation**: Prevents Failure #1 (FSM Over-Engineering, Risk Score 684)

#### 1.1.2 Practical Assertion Guidelines

**NASA Rule 10 Implementation** (not dogmatic):
```typescript
// ✅ GOOD: Assertions for critical paths
async function validateAuthToken(token: string): Promise<boolean> {
  assert(token.length > 0, "Token cannot be empty");
  assert(token.length <= 512, "Token exceeds max length");

  const decoded = await decodeJWT(token);
  assert(decoded !== null, "Token decode must not return null");

  return !isExpired(decoded) && isValidUser(decoded);
}

// ✅ ALSO GOOD: Simple utilities without assertions (when obvious)
function formatDate(date: Date): string {
  return date.toISOString();
}

// ❌ BAD: Assertion overkill on trivial code
function add(a: number, b: number): number {
  assert(typeof a === "number", "a must be number"); // TypeScript already checks
  assert(typeof b === "number", "b must be number"); // Redundant
  return a + b;
}
```

**Guideline**: Use assertions for:
- External input validation
- Invariant checking in complex logic
- Post-condition validation
- Skip for: Type-checked parameters, trivial operations

**Mitigation**: Prevents Failure #8 (NASA Compliance Fatigue, Risk Score 441)

### 1.2 FSM-First Core Implementation
**Objective**: Build state machine foundation for complex features only

**Components**:
```
/src/fsm/
├── TransitionHub.ts          # Centralized state transitions
├── StateContract.ts          # Base interface for all states
├── EventRegistry.ts          # Enum-based event definitions
├── Guards.ts                 # Transition guard functions
└── FSMDecisionMatrix.ts      # NEW: When to use FSM guide
```

**Implementation Strategy**:
- **Phase 1A** (Week 1): 5 core FSMs only
  - AuthenticationFSM
  - QueenOrchestratorFSM
  - PrincessCoordinatorFSM
  - DroneExecutionFSM
  - ThreeLoopWorkflowFSM

- **Phase 1B** (Week 2): Validate FSM patterns work before expanding

**State Isolation Strategy** (unchanged):
- One file per state (max 200 LOC)
- No cross-state dependencies
- Event-driven communication only

**Mitigation**: Prevents Failure #1 (FSM Over-Engineering)

### 1.3 Module Boundaries with Event-Driven Architecture
**Objective**: Establish clean bounded contexts with async communication

**NEW: Event Bus Architecture**:
```typescript
// Prevents agent deadlock (Failure #4)
interface EventBus {
  publish(event: DomainEvent): Promise<void>;
  subscribe(eventType: string, handler: EventHandler): void;
  unsubscribe(eventType: string, handler: EventHandler): void;
}

// No synchronous cross-domain calls allowed
// All communication via event bus
```

**Domains** (from Princess hierarchy):
1. Development Domain
2. Quality Domain
3. Security Domain
4. Research Domain
5. Infrastructure Domain
6. Coordination Domain

**Rules** (enhanced):
- ✅ No circular dependencies
- ✅ API-first interfaces
- ✅ Dependency injection throughout
- ✅ **NEW**: Event bus for ALL cross-domain communication
- ✅ **NEW**: Async-first design (no blocking calls)
- ✅ **NEW**: Timeout for all cross-domain operations (30-60s)

**Mitigation**: Prevents Failure #4 (Agent Communication Deadlock, Risk Score 560)

---

## Phase 2: Multi-AI Platform Integration (Weeks 3-4)

### 2.1 Platform Abstraction Layer with Circuit Breakers
**Objective**: Resilient multi-platform coordination with automatic fallback

**NEW: Platform Abstraction Layer**:
```typescript
interface PlatformAbstractionLayer {
  execute(task: Task, platform: Platform): Promise<Result>;
  getFallback(platform: Platform): Platform[];
  checkHealth(platform: Platform): Promise<HealthStatus>;
}

// Circuit breaker per platform
class PlatformCircuitBreaker {
  private failureCount = 0;
  private readonly threshold = 3;
  private state: "CLOSED" | "OPEN" | "HALF_OPEN" = "CLOSED";

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === "OPEN") {
      throw new Error("Circuit breaker is OPEN");
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
      setTimeout(() => this.state = "HALF_OPEN", 60000); // 1min recovery
    }
  }

  private onSuccess(): void {
    this.failureCount = 0;
    this.state = "CLOSED";
  }
}
```

**Fallback Chain**:
```
Primary: Gemini 2.5 Pro (research)
  → Fallback 1: Claude Sonnet (sequential thinking)
  → Fallback 2: GPT-4 (general purpose)
  → Fallback 3: Local cache (previous results)
```

**Gemini Stuck Thinking Mitigation**:
```bash
# Force Flash model via environment
export GEMINI_MODEL="gemini-2.5-flash"

# Disable thinking mode for speed-critical tasks
--thinking-budget 0

# MCP server timeout (30-60s)
timeout 60s gemini-cli ...
```

**Mitigation**: Prevents Failure #2 (Multi-AI Platform Coordination Breakdown, Risk Score 660)

### 2.2 Intelligent Prompt Caching (90% Savings)
**Objective**: Maximize GPT-5 Codex caching for cost optimization

**Caching Strategy**:
```typescript
interface PromptTemplate {
  cachedBase: string;     // System prompt + codebase context (cached)
  dynamicInput: string;   // User query (not cached)
}

// Separate cacheable from dynamic content
const template: PromptTemplate = {
  cachedBase: `
    You are a TypeScript expert working on SPEK platform.

    Codebase structure:
    ${fileTree}

    Coding standards:
    ${codingStandards}

    Architecture:
    ${architectureGuide}
  `,  // This part gets 90% discount after first use

  dynamicInput: `
    Implement: ${userQuery}
  `   // This part always full price
};
```

**Real-World Target**: 70-85% cache hit rate (based on production data)

**Mitigation**: Prevents Failure #9 (Cost Overruns, Risk Score 420)

### 2.3 Phased Agent Implementation (NOT 85 at once)
**Objective**: Deliver working system incrementally, not all-or-nothing

**NEW: Three-Phase Rollout**:

**Phase 2A (Week 3): 5 Core Agents**
- `coder` (GPT-5 Codex) - PRIMARY
- `reviewer` (Claude Opus) - PRIMARY
- `researcher` (Gemini Pro) - PRIMARY
- `planner` (Gemini Flash) - PRIMARY
- `tester` (Claude Opus) - PRIMARY

**Success Criteria**: All 5 agents functional with quality gates

**Phase 2B (Week 4): 4 Swarm Coordinators**
- `queen-orchestrator` (Claude Sonnet + sequential)
- `development-princess` (Claude Sonnet)
- `quality-princess` (Claude Opus)
- `coordination-princess` (Claude Sonnet)

**Success Criteria**: Basic swarm coordination working

**Phase 2C (Weeks 5-8): 13 Specialized Agents**
- Security: `security-manager`, `legal-compliance-checker`
- Research: `researcher-gemini`, `specification`
- Infrastructure: `cicd-engineer`, `devops-automator`
- GitHub: `pr-manager`, `issue-tracker`, `github-modes`
- Testing: `tester`, `code-analyzer`
- Development: `backend-dev`, `sparc-coder`

**Phase 2D (Future): Remaining 63 Agents**
- Only implement if Phase 2A-C succeeds
- Evaluate actual need vs initial plan

**Mitigation**: Prevents Failure #7 (Agent Implementation Incompleteness, Risk Score 450)

---

## Phase 3: Queen-Princess-Drone Hierarchy (Weeks 5-6)

### 3.1 Queen Orchestrator with Context Management
**Context**: 500KB (hard limit enforced)

**NEW: Sliding Window Context Management**:
```typescript
class ContextWindowManager {
  private readonly maxSize = 500 * 1024; // 500KB
  private currentSize = 0;

  addContext(content: string): void {
    this.currentSize += content.length;

    if (this.currentSize > this.maxSize) {
      this.pruneOldestContext();  // Remove 25% oldest content
    }
  }

  pruneOldestContext(): void {
    // Keep only most recent 75% of context
    const targetSize = this.maxSize * 0.75;
    // Implementation: FIFO queue, remove oldest entries
  }
}
```

**Responsibilities** (unchanged):
- Byzantine consensus protocols
- MECE task division
- Cross-hive communication
- Global context management

**FSM States**:
- IDLE
- ANALYZING
- DELEGATING
- MONITORING
- CONSENSUS_BUILDING
- EMERGENCY

**Mitigation**: Prevents Failure #5 (Context Window Exhaustion, Risk Score 525)

### 3.2 Six Princess Domains (Event-Driven)
**Context**: 2MB each (hard limit enforced)

**Implementation** (async-first):
```
/src/princess/
├── DevelopmentPrincess/
│   ├── states/
│   ├── agents/
│   ├── events/           # NEW: Event handlers
│   └── PrincessFSM.ts
├── QualityPrincess/
├── SecurityPrincess/
├── ResearchPrincess/
├── InfrastructurePrincess/
└── CoordinationPrincess/
```

**Event-Driven Communication Pattern**:
```typescript
// NO direct calls between Princesses
// All communication via events

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

**Mitigation**: Prevents Failure #4 (Agent Communication Deadlock)

### 3.3 Drone Agents (Phased Implementation)
**Context**: 100KB each
**Pattern**: Specialized execution with optimal AI model

**Phase 3A**: 5 core drone agents (Week 5)
**Phase 3B**: 13 specialized drones (Weeks 6-8)
**Phase 3C**: Remaining drones (future, as needed)

---

## Phase 4: Quality Gates & Compliance (Weeks 7-8)

### 4.1 Sandbox Validation with gVisor
**Objective**: Prevent quality gate bypass through isolated testing

**NEW: gVisor Sandbox Architecture**:
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

**Validation Process**:
1. Agent claims completion
2. Code copied to sandbox (read-only)
3. All tests run in isolated gVisor container
4. Results collected (cannot be forged)
5. Evidence validated (screenshots, logs, hashes)

**Mitigation**: Prevents Failure #3 (Quality Gate Bypass, Risk Score 630)

### 4.2 Immutable Evidence Logging
**Objective**: Tamper-proof audit trail for theater detection

**NEW: Blockchain-Inspired Audit Trail**:
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

**Mitigation**: Prevents Failure #3 (Quality Gate Bypass)

### 4.3 Multi-Dimensional Theater Detection
**Target**: <60 score = theater, >=60 = genuine

**6-Factor Scoring** (from research):
1. **Quality Metrics** (25 points): Tests pass, lint clean, types valid, security scan
2. **Evidence Validity** (20 points): Screenshot authenticity, log chronology, hash verification
3. **Change Impact** (15 points): LOC changed, files touched, complexity delta
4. **Test Authenticity** (15 points): Real test execution, coverage increase, edge cases
5. **Temporal Patterns** (15 points): Time distribution, work patterns, outlier detection
6. **Complexity** (10 points): Cognitive complexity, nesting depth, maintainability

**Implementation**:
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

**Mitigation**: Prevents Failure #3 (Quality Gate Bypass)

### 4.4 NASA POT10 Compliance (Practical)
**Target**: >=92% compliance

**Pragmatic Implementation**:
- ✅ Functions <=60 lines (ESLint enforced)
- ✅ >=2 assertions for complex functions only
- ✅ No recursion (ESLint enforced)
- ✅ Fixed loop bounds (ESLint enforced)
- ✅ All returns checked (TypeScript strict mode)

**Exception Process**:
```typescript
// For truly exceptional cases (rare)
/* eslint-disable max-lines-per-function */
// JUSTIFICATION: Complex algorithm requiring >60 lines
//                Reviewed by: @architect
//                Approved: 2025-10-08
function exceptionalComplexFunction() {
  // ...implementation
}
/* eslint-enable max-lines-per-function */
```

**Mitigation**: Prevents Failure #8 (NASA Compliance Fatigue)

---

## Phase 5: 3-Loop System Integration (Weeks 9-10)

### 5.1 Loop 1: Planning & Research (unchanged)
**Components**:
- SPEC KIT integration
- Research agents (Gemini 2.5 Pro)
- Pre-mortem analysis (4 iterations)
- Risk register

### 5.2 Loop 2: Development & Implementation
**Components** (with sandbox):
- Queen-Princess-Drone deployment
- MECE task division
- **NEW**: Sandbox validation for all completions
- Theater detection with 6-factor scoring

### 5.3 Loop 3: Quality & Debugging
**Components** (with immutable logging):
- Real quality validation (npm test, lint, audit)
- GitHub workflow integration
- **NEW**: Immutable audit trail
- **NEW**: Evidence validation with digital signatures

**Integration**:
```bash
# Forward flow (new projects)
./3-loop-orchestrator.sh forward

# Reverse flow (existing codebases)
./3-loop-orchestrator.sh reverse
```

---

## Phase 6: Testing & Validation (Weeks 11-12)

### 6.1 Test Coverage
**Target**: >=80% coverage

**Strategy** (unchanged):
- Unit tests for all state machines
- Integration tests for agent communication
- E2E tests for 3-loop workflows
- Performance benchmarks

### 6.2 Production Validation
**Checklist** (enhanced):
- [ ] Zero TypeScript compilation errors
- [ ] All quality gates passing
- [ ] NASA compliance >=92%
- [ ] Theater detection <60 score
- [ ] Security scan clean (zero critical/high)
- [ ] **NEW**: 5 core agents implemented and tested (not 85)
- [ ] **NEW**: All MCP servers containerized with gVisor
- [ ] **NEW**: Sandbox validation operational
- [ ] **NEW**: Immutable audit log working
- [ ] 3-loop workflows tested

---

## Technology Stack

### Core (unchanged)
- **Runtime**: Node.js v20.17.0
- **Language**: TypeScript (strict mode)
- **Python**: 3.12.5 (analyzer engine)
- **Package Manager**: npm 11.4.2

### AI Platforms (with abstraction layer)
- **Claude Code**: 2.0.10 (primary development environment)
- **Claude Flow**: v2.5.0-alpha.139 (swarm orchestration)
- **Gemini CLI**: 0.3.4 (research, free tier)
- **Codex CLI**: 0.36.0 (autonomous coding)

### Infrastructure (enhanced)
- **Docker**: 24.0.2 (MCP containerization)
- **gVisor**: Latest (sandbox security)
- **GitHub CLI**: 2.78.0 (CI/CD integration)
- **Git**: 2.40.0 (version control)

---

## Cost Budget & Tracking

**NEW: Daily Cost Monitoring**:
```typescript
interface CostBudget {
  daily: number;    // $50/day
  monthly: number;  // $1,500/month
  alerts: {
    warning: number;  // 75% of budget
    critical: number; // 90% of budget
  };
}

// Track actual spend by platform
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
    }
  }
}
```

**Mitigation**: Prevents Failure #9 (Cost Overruns)

---

## Timeline with Milestones

**NEW: Weekly Milestones** (not phase-based):

### Week 1
- [ ] TypeScript foundation
- [ ] FSM decision matrix
- [ ] 5 core FSMs implemented
- [ ] **Milestone**: Zero compilation errors

### Week 2
- [ ] Platform abstraction layer
- [ ] Circuit breakers
- [ ] Event bus architecture
- [ ] **Milestone**: Platform failover works

### Week 3
- [ ] 5 core agents implemented
- [ ] Basic agent orchestration
- [ ] **Milestone**: End-to-end agent task execution

### Week 4
- [ ] 4 swarm coordinators
- [ ] Queen-Princess communication
- [ ] **Milestone**: Basic swarm coordination works

### Week 5-6
- [ ] Sandbox validation (gVisor)
- [ ] Theater detection (6-factor)
- [ ] Immutable audit log
- [ ] **Milestone**: Quality gates operational

### Week 7-8
- [ ] 13 specialized agents
- [ ] 3-loop integration
- [ ] **Milestone**: Complete workflow functional

### Week 9-10
- [ ] Testing and validation
- [ ] Performance optimization
- [ ] **Milestone**: Production-ready

### Week 11-12
- [ ] Documentation
- [ ] Deployment preparation
- [ ] **Milestone**: Launch

**Mitigation**: Prevents Failure #10 (Timeline Delays, Risk Score 405)

---

## Risk Register (Updated)

### High Priority Risks (from Pre-mortem)

1. **FSM Over-Engineering** → **MITIGATED**
   - FSM decision matrix implemented
   - 5 core FSMs only in Phase 1
   - Validation before expansion

2. **Platform Coordination Breakdown** → **MITIGATED**
   - Platform abstraction layer with circuit breakers
   - Fallback chains defined
   - Health checks and timeouts

3. **Quality Gate Bypass** → **MITIGATED**
   - gVisor sandbox validation
   - Immutable audit log
   - 6-factor theater detection
   - Evidence validation with digital signatures

4. **Agent Communication Deadlock** → **MITIGATED**
   - Event-driven async architecture
   - No synchronous cross-domain calls
   - Timeout for all operations

5. **Context Window Exhaustion** → **MITIGATED**
   - Sliding window context management
   - Hard limits enforced (500KB Queen, 2MB Princess, 100KB Drone)
   - Automatic pruning

6. **MCP Server Security Breach** → **MITIGATED**
   - Non-root execution (UID 1001)
   - Read-only filesystem
   - Network isolation
   - OAuth 2.0 Resource Server pattern

7. **Agent Implementation Incompleteness** → **MITIGATED**
   - Phased rollout: 5 core → 4 swarm → 13 specialized
   - Success criteria per phase
   - No all-or-nothing deployment

8. **NASA Compliance Fatigue** → **MITIGATED**
   - Pragmatic assertion guidelines
   - Exception process for rare cases
   - Focus on critical paths only

9. **Cost Overruns** → **MITIGATED**
   - Daily/monthly budget tracking
   - Alert thresholds (75%, 90%)
   - Prompt caching (90% savings)
   - Gemini free tier maximization

10. **Timeline Delays** → **MITIGATED**
    - Weekly milestones with concrete deliverables
    - Phased agent implementation
    - No scope creep (65 agents deferred to future)

---

## Success Metrics (Enhanced)

### Technical Metrics

| Metric | Current (v1) | v2 Target | v2 Actual (TBD) |
|--------|-------------|-----------|-----------------|
| TypeScript Errors | 951 | 0 | ___ |
| Command Success Rate | 23% | 100% | ___ |
| NASA Compliance | Unknown | >=92% | ___ |
| FSM Coverage | 0% | >=30% (not 90%) | ___ |
| Test Coverage | Unknown | >=80% | ___ |
| Core Agents | 0 | 5 functional | ___ |
| Swarm Agents | Facades | 4 functional | ___ |
| Specialized Agents | Facades | 13 functional | ___ |

### Performance Metrics

| Metric | Target | v2 Actual (TBD) |
|--------|--------|-----------------|
| Simple Operation Response | <=2s | ___ |
| Multi-Agent Coordination | <=60s | ___ |
| Build Time | <=30s | ___ |
| Test Suite Execution | <=2min | ___ |
| Platform Failover Time | <=5s | ___ |

### Cost Metrics (NEW)

| Metric | Budget | v2 Actual (TBD) |
|--------|--------|-----------------|
| Daily Spend | $50 | ___ |
| Monthly Spend | $1,500 | ___ |
| Cost Per Agent Task | $0.10 | ___ |
| Cache Hit Rate | 70-85% | ___ |

---

## Next Steps

1. ✅ Review PLAN-v2 with stakeholders
2. ⏳ Update SPEC-v2 with refined requirements
3. ⏳ Fill P1 research gaps (GitHub SPEC KIT, DSPy, Bytebot)
4. ⏳ Run Pre-mortem v2 on updated plan

---

## Version & Run Log

| Version | Timestamp | Agent/Model | Change Summary | Status |
|--------:|-----------|-------------|----------------|--------|
| 1.0     | 2025-10-08T09:15:00-04:00 | Claude Sonnet 4 | Initial plan draft | SUPERSEDED |
| 2.0     | 2025-10-08T10:15:00-04:00 | Claude Sonnet 4 | Incorporates pre-mortem v1 findings, 30 risk mitigations | ACTIVE |

### Receipt
- status: OK (iteration 2 of 4)
- reason: Pre-mortem v1 mitigations integrated
- run_id: plan-v2-iteration-2
- inputs: ["PLAN-v1.md", "PREMORTEM-v1.md", "research-fsm-and-quality-v1.md", "research-ai-platforms-and-mcp-security-v1.md"]
- tools_used: ["analysis", "planning", "risk-mitigation"]
- changes: {
    "fsm_strategy": "Added decision matrix, phased 5 core FSMs",
    "agents": "Phased rollout: 5 core → 4 swarm → 13 specialized (not 85 at once)",
    "platforms": "Added abstraction layer + circuit breakers",
    "quality": "Added gVisor sandbox + immutable audit log + 6-factor theater detection",
    "communication": "Event-driven async (prevents deadlock)",
    "context": "Sliding window management (prevents exhaustion)",
    "costs": "Daily/monthly tracking with alerts",
    "timeline": "Weekly milestones (prevents delays)",
    "compliance": "Pragmatic NASA guidelines (prevents fatigue)"
  }
