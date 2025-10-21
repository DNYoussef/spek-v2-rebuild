# SPEK Platform v2 - Requirements Specification v1

**Version**: 1.0
**Date**: 2025-10-08
**Status**: Draft - Iteration 1
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild

---

## 1. Project Overview

### 1.1 Purpose
Rebuild SPEK (Specification, Research, Planning, Execution, Knowledge) platform from ground up with:
- FSM-first architecture eliminating god objects
- Multi-AI platform optimization (Gemini, Codex, Claude)
- Queen-Princess-Drone swarm coordination
- Production-ready quality gates
- Zero technical debt

### 1.2 Scope
**In Scope**:
- Complete type system rewrite (TypeScript strict mode)
- 85+ fully implemented AI agents (not facades)
- 15+ containerized MCP servers
- 3-loop development system (Planning, Development, Quality)
- Theater detection and reality validation
- NASA POT10 compliance automation
- GitHub integration (SPEC KIT, CI/CD, PRs)

**Out of Scope** (Future Phases):
- Web UI dashboard
- Multi-user collaboration features
- Cloud deployment infrastructure
- Enterprise SSO integration

### 1.3 Success Criteria
- Zero TypeScript compilation errors
- 100% command success rate (30/30 commands functional)
- >=92% NASA compliance
- >=90% FSM coverage
- >=80% test coverage
- <60 theater detection score (genuine work only)

---

## 2. Functional Requirements

### 2.1 FSM-First Architecture

**REQ-FSM-001**: All features MUST be designed as explicit finite state machines
- States defined as enums (NO string states)
- Events defined as enums (NO string events)
- One file per state (max 200 LOC per file)
- Centralized TransitionHub for all state changes

**REQ-FSM-002**: State contracts MUST implement complete lifecycle
```typescript
interface StateContract {
  init(): Promise<void>;
  update(event: Event): Promise<TransitionResult>;
  shutdown(): Promise<void>;
  checkInvariants(): Promise<boolean>;
}
```

**REQ-FSM-003**: Transition guards MUST validate all state changes
- Pre-conditions checked before transition
- Post-conditions validated after transition
- Error recovery paths defined
- Rollback capability for failed transitions

**REQ-FSM-004**: State isolation MUST be enforced
- No cross-state global variables
- No direct state-to-state calls
- Event-driven communication only
- Dependency injection for shared resources

### 2.2 NASA Rule 10 Compliance

**REQ-NASA-001**: All functions MUST be <=60 lines
- Enforcement: ESLint rule with max-lines-per-function: 60
- Exception: None allowed
- Validation: Pre-commit hook blocks violations

**REQ-NASA-002**: All functions MUST have >=2 assertions
- Enforcement: Custom ESLint plugin
- Assertions check pre-conditions and post-conditions
- Example: `assert(input !== null, "Input cannot be null")`

**REQ-NASA-003**: NO recursion allowed
- Enforcement: ESLint no-restricted-syntax
- Alternative: Iterative algorithms with explicit loop bounds

**REQ-NASA-004**: All loops MUST have fixed bounds
- NO `while(true)` or infinite loops
- Maximum iteration count defined at compile time
- Example: `for (let i = 0; i < MAX_ITERATIONS; i++)`

**REQ-NASA-005**: All non-void returns MUST be checked
- Enforcement: TypeScript strict mode + ESLint
- NO ignored return values
- Example: `const result = await operation(); assert(result.success);`

### 2.3 Multi-AI Platform Integration

**REQ-AI-001**: Automatic model selection based on task characteristics
```typescript
interface ModelSelector {
  selectModel(task: Task): {
    model: AIModel;
    platform: Platform;
    mcpServers: MCPServer[];
    fallback: AIModel;
  };
}
```

**REQ-AI-002**: Platform distribution strategy
- **Gemini 2.5 Pro/Flash**: Research, planning, large-context analysis (1M tokens, free tier)
- **GPT-5 Codex**: Autonomous coding, browser automation, 7+ hour sessions
- **Claude Opus 4.1**: Quality analysis, code review (72.7% SWE-bench)
- **Claude Sonnet 4**: Coordination, sequential thinking

**REQ-AI-003**: Cost optimization
- Use Gemini free tier for high-volume operations
- Prompt caching for repeated context (90% savings)
- Automatic fallback if primary platform unavailable

**REQ-AI-004**: Model assignment matrix
```typescript
const assignments = {
  research: "gemini-2.5-pro",        // 1M context
  planning: "gemini-2.5-flash",      // Cost-effective
  coding: "gpt-5-codex",             // 7+ hours autonomous
  review: "claude-opus-4.1",         // 72.7% SWE-bench
  coordination: "claude-sonnet-4"    // Sequential thinking
};
```

### 2.4 Queen-Princess-Drone Hierarchy

**REQ-SWARM-001**: Queen Orchestrator (500KB context)
- Byzantine consensus protocols
- MECE task division (Mutually Exclusive, Collectively Exhaustive)
- Cross-hive communication
- Global context management
- Anti-degradation monitoring

**REQ-SWARM-002**: Six Princess Domains (2MB context each)
1. **Development Princess**: Code implementation, refactoring
2. **Quality Princess**: Testing, review, compliance validation
3. **Security Princess**: Vulnerability scanning, audit trails
4. **Research Princess**: Information gathering, solution discovery
5. **Infrastructure Princess**: CI/CD, deployment, monitoring
6. **Coordination Princess**: Task orchestration, resource allocation

**REQ-SWARM-003**: 85+ Drone Agents (100KB context each)
- Full implementation (not facades)
- Optimal AI model assignment
- Specialized execution
- Evidence collection

**REQ-SWARM-004**: Communication protocol
- Agent2Agent (A2A) protocol with Context DNA
- DSPy optimization for prompts
- Bidirectional validation:
  - Queen -> Princess (validate orders)
  - Princess -> Drone (validate tasks)
  - Drone -> Princess -> Queen (validate outputs)

### 2.5 Quality Gates

**REQ-QUALITY-001**: Theater detection MUST prevent fake work
- Quality score 0-100 (threshold >=60)
- Evidence validation (screenshots, logs, test output)
- Sandbox testing (isolated validation)
- Reality checks (npm test, lint, audit actually run)

**REQ-QUALITY-002**: NASA compliance validation
- Target: >=92% compliance
- Automated scanning via ESLint plugins
- Pre-commit hooks block violations
- CI/CD pipeline enforcement

**REQ-QUALITY-003**: Security scanning
- Zero critical vulnerabilities allowed
- <=5 high vulnerabilities allowed
- Bandit for Python
- Semgrep for TypeScript
- OWASP Top 10 compliance

**REQ-QUALITY-004**: Test coverage
- >=80% line coverage required
- >=90% branch coverage for critical paths
- 100% coverage for state transitions
- Jest for TypeScript, pytest for Python

**REQ-QUALITY-005**: FSM coverage
- >=90% of features as state machines
- All transitions documented
- Guards implemented
- Error recovery paths defined

### 2.6 MCP Server Integration

**REQ-MCP-001**: Containerized deployment for all MCP servers
- Docker images for each server
- Non-root execution
- Version pinning (no auto-updates)
- Vulnerability scanning in CI/CD

**REQ-MCP-002**: Required MCP servers (15+ total)
- **claude-flow**: 87 tools for swarm orchestration
- **memory**: Persistent knowledge graphs
- **sequential-thinking**: Enhanced reasoning for coordination agents
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

### 2.7 3-Loop Development System

**REQ-LOOP-001**: Loop 1 - Planning & Research
- **Input**: Requirements, SPEC.md
- **Process**: Research -> Pre-mortem (4 iterations) -> Risk-mitigated plan
- **Output**: PLAN.md, risk register, research synthesis
- **Tools**: /research:web, /research:github, /pre-mortem-loop
- **AI**: Gemini 2.5 Pro (1M context for research)

**REQ-LOOP-002**: Loop 2 - Development & Implementation
- **Input**: PLAN.md, task definitions
- **Process**: Queen-Princess-Drone deployment -> MECE division -> Theater detection -> Sandbox validation
- **Output**: Implemented code, test suite, documentation
- **Tools**: /dev:swarm, 85+ agents, MECE task division
- **AI**: Multi-platform (Gemini, Codex, Claude based on task)

**REQ-LOOP-003**: Loop 3 - Quality & Debugging
- **Input**: Implemented code
- **Process**: npm test, lint, typecheck, security scan -> Failure analysis -> Auto-remediation
- **Output**: Quality report, GitHub artifacts, 100% passing tests
- **Tools**: /qa:run, /theater:scan, /reality:check
- **AI**: Claude Opus (quality validation)

**REQ-LOOP-004**: Flow patterns
- **Forward flow**: Loop 1 -> Loop 2 -> Loop 3 (new projects)
- **Reverse flow**: Loop 3 -> Loop 1 -> Loop 2 -> Loop 3 (existing codebases)
- **Convergence**: Automatic detection when quality goals met

### 2.8 Agent Registry

**REQ-AGENT-001**: 85+ agents MUST be fully implemented
- NO facade patterns
- Real execution logic
- Complete error handling
- Evidence collection

**REQ-AGENT-002**: Agent categories (current framework)
- Core Development (11 agents)
- Architecture & System Design (6 agents)
- Swarm Coordination & Orchestration (15 agents)
- SPARC/SPEK Methodology (6 agents)
- Quality Assurance & Testing (8 agents)
- GitHub & DevOps Integration (17 agents)
- Specialized Development (8 agents)
- Documentation & API (4 agents)
- Consensus & Distributed Systems (7 agents)
- Performance & Benchmarking (3 agents)

**REQ-AGENT-003**: Agent implementation pattern
```typescript
class AgentImplementation implements AgentContract {
  readonly model: AIModel;
  readonly mcpServers: MCPServer[];
  readonly capabilities: Capability[];

  async execute(task: Task): Promise<Result> {
    // Real implementation with validation
    const validated = await this.validate(task);
    const result = await this.runTask(validated);
    const evidence = await this.collectEvidence(result);
    return { result, evidence };
  }
}
```

### 2.9 Command System

**REQ-CMD-001**: 30 slash commands MUST be functional
- Success rate: 100% (vs 23% in v1)
- Real script execution (not templates)
- Evidence validation
- Rollback on failure

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
- Error recovery with max 3 retries
- Audit trail with evidence

### 2.10 GitHub Integration

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

---

## 3. Non-Functional Requirements

### 3.1 Performance

**REQ-PERF-001**: Response time requirements
- Simple operations: <=2 seconds
- Complex single-agent tasks: <=30 seconds
- Multi-agent coordination: <=60 seconds
- Full 3-loop iteration: <=10 minutes

**REQ-PERF-002**: Parallelization
- Target: 2.8-4.4x speed improvement (vs sequential)
- Implementation: Parallel swarm execution
- Constraint: Max 25 concurrent agents (Claude Flow limit)

**REQ-PERF-003**: Resource optimization
- Queen context: 500KB max
- Princess context: 2MB max
- Drone context: 100KB max
- MCP server memory: <500MB per container

### 3.2 Reliability

**REQ-REL-001**: Error recovery
- All operations MUST have rollback capability
- Max 3 retry attempts with exponential backoff
- Circuit breaker for failing external services
- Graceful degradation if AI platform unavailable

**REQ-REL-002**: Byzantine fault tolerance
- Queen consensus protocols handle Byzantine failures
- Princess validation gates catch malicious outputs
- Drone sandboxing prevents system contamination

**REQ-REL-003**: Data persistence
- All state changes logged to filesystem
- MCP memory server for cross-session knowledge
- Version footers on all files (SHA-256 hashing)
- Audit trail for compliance

### 3.3 Maintainability

**REQ-MAINT-001**: Code organization
- Single Responsibility Principle
- Dependency injection throughout
- Event-driven communication
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
- Container isolation for all servers
- Non-root execution
- Network policies (no internet access by default)
- Secrets management via environment variables

**REQ-SEC-002**: Code scanning
- Bandit for Python (OWASP compliance)
- Semgrep for TypeScript (OWASP Top 10)
- Dependency scanning (npm audit, safety)
- SARIF output for GitHub Security tab

**REQ-SEC-003**: Audit trails
- All agent actions logged with timestamps
- Model attribution (which AI made which change)
- Evidence collection (screenshots, logs, output)
- Immutable logging (append-only)

### 3.5 Scalability

**REQ-SCALE-001**: Agent scaling
- Support for 85+ concurrent drone agents
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
| FSM Coverage | 0% | >=90% | P1 |
| Test Coverage | Unknown | >=80% | P1 |
| Agent Implementation | Facades only | 100% complete | P0 |
| Theater Detection | Basic | <60 score | P1 |

### 5.2 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Simple Operation Response | <=2s | End-to-end latency |
| Multi-Agent Coordination | <=60s | Full swarm deployment |
| Build Time | <=30s | npm run build |
| Test Suite Execution | <=2min | npm test |
| Parallel Speedup | 2.8-4.4x | vs sequential execution |

### 5.3 Quality Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Security Critical Vulnerabilities | 0 | Bandit + Semgrep |
| Security High Vulnerabilities | <=5 | Bandit + Semgrep |
| Code Duplication | <=5% | SonarQube analysis |
| Cyclomatic Complexity | <=10 per function | ESLint plugin |
| God Objects | 0 | Architectural review |

---

## 6. Acceptance Criteria

### Phase 1 Completion
- [ ] Zero TypeScript compilation errors
- [ ] All base interfaces defined
- [ ] TransitionHub implemented
- [ ] FSM state contracts established
- [ ] NASA Rule 10 ESLint rules active

### Phase 2 Completion
- [ ] Model selector implemented
- [ ] 15+ MCP servers containerized
- [ ] 85+ agents fully implemented (not facades)
- [ ] Agent registry complete with tests

### Phase 3 Completion
- [ ] Queen orchestrator functional
- [ ] Six Princess domains implemented
- [ ] 85+ Drone agents deployed
- [ ] Agent2Agent protocol validated

### Phase 4 Completion
- [ ] Theater detection operational
- [ ] NASA compliance >=92%
- [ ] FSM coverage >=90%
- [ ] Security scans clean

### Phase 5 Completion
- [ ] Loop 1 (Planning) functional
- [ ] Loop 2 (Development) functional
- [ ] Loop 3 (Quality) functional
- [ ] Forward and reverse flows tested

### Phase 6 Completion
- [ ] >=80% test coverage
- [ ] All quality gates passing
- [ ] Production validation complete
- [ ] Documentation finalized

---

## 7. Open Questions & Research Gaps

### Identified Gaps (Iteration 1)

1. **AI Platform Integration**
   - How to handle Gemini CLI stuck thinking bug (Issue #2025)?
   - What's the optimal prompt caching strategy for GPT-5 Codex?
   - How to integrate Bytebot desktop automation with MCP bridge?

2. **Development Tools**
   - How does GitHub SPEC KIT v0.0.57 integrate with multiple AI CLIs?
   - What's the DSPy optimization strategy for Agent2Agent prompts?
   - How to implement Context DNA for cross-session persistence?

3. **FSM Architecture**
   - What's the optimal TransitionHub implementation pattern?
   - How to handle error recovery in complex state machines?
   - What guard patterns work best for multi-agent coordination?

4. **Quality Enforcement**
   - How to detect theater patterns beyond simple quality scoring?
   - What's the best sandbox testing strategy?
   - How to enforce immutable validation layers?

5. **Performance Optimization**
   - What's the optimal agent concurrency limit?
   - How to balance context size vs response time?
   - What caching strategies work for repeated operations?

**Action**: These gaps will be filled in Iteration 1 research phase

---

## 8. Version & Run Log

| Version | Timestamp | Agent/Model | Change Summary | Status |
|--------:|-----------|-------------|----------------|--------|
| 1.0     | 2025-10-08T09:30:00-04:00 | Claude Sonnet 4 | Initial spec draft | DRAFT |

### Receipt
- status: PARTIAL (iteration 1 of 4)
- reason: Awaiting research gap analysis and pre-mortem feedback
- run_id: spec-v1-iteration-1
- inputs: ["PLAN-v1.md", "research-claude-ecosystem.md"]
- tools_used: ["analysis", "specification", "requirements"]
