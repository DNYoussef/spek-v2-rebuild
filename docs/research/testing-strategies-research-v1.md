# Testing Strategies Research - SPEK v2

**Version**: 1.0
**Date**: 2025-10-08
**Status**: Complete
**Research Focus**: FSM Testing, Multi-Agent Coordination Testing, E2E Testing, Performance Benchmarking
**Priority**: P1 - Critical (Gap 9)

---

## Executive Summary

This research addresses Gap 9 from RESEARCH-GAPS-v1.md, providing comprehensive testing strategies for:
- **5 Core FSMs** (Queen, Princess, Drone, TransitionHub, Quality Gates)
- **22+ AI Agents** (Research, Coder, Tester, etc.)
- **3-Loop System** (Loop 1: Planning, Loop 2: Development, Loop 3: Quality)
- **gVisor Sandbox** integration for secure testing

### Key Findings

1. **FSM Testing**: XState with @xstate/test provides model-based test generation with 100% state coverage
2. **Multi-Agent Testing**: Microsoft Agent Framework and Google ADK offer enterprise-grade observability and evaluation
3. **E2E Testing**: Agentic workflows with Octomind and Checksum enable autonomous test generation
4. **Performance Benchmarking**: Grafana k6 (load testing) + Google Lighthouse (performance metrics) provide comprehensive benchmarking

---

## Part 1: FSM Testing Strategies

### 1.1 Overview of FSM Testing Approaches

Finite State Machine testing requires comprehensive coverage of:
- **All States**: Every state visited at least once (0-switch coverage)
- **All Transitions**: Every state-event pair triggered (1-switch coverage)
- **All Paths**: Sequences of transitions tested (2-switch coverage)
- **Guard Conditions**: Validation of transition guards
- **State Invariants**: Verification of state-specific rules
- **Error Recovery**: Testing rollback and error states

### 1.2 FSM Testing Tools (2025)

#### XState - Industry Standard for TypeScript FSMs

**Strengths**:
- Type-safe state machines with full TypeScript support
- Visual debugging and inspection tools
- Hierarchical states and parallel states
- Model-based test generation via @xstate/graph
- Built-in event streaming and logging

**Testing Pattern**:
```typescript
import { createMachine } from 'xstate';
import { createModel } from '@xstate/test';

// Define state machine
const authMachine = createMachine({
  id: 'auth',
  initial: 'idle',
  states: {
    idle: {
      on: { LOGIN_REQUEST: 'authenticating' }
    },
    authenticating: {
      on: {
        CREDENTIALS_VALID: 'authenticated',
        CREDENTIALS_INVALID: 'failed'
      }
    },
    authenticated: {
      on: { LOGOUT: 'idle' }
    },
    failed: {
      on: { RETRY: 'idle' }
    }
  }
});

// Generate test model
const authModel = createModel(authMachine).withEvents({
  LOGIN_REQUEST: { exec: async (context) => { /* trigger login */ } },
  CREDENTIALS_VALID: { exec: async (context) => { /* mock valid response */ } },
  CREDENTIALS_INVALID: { exec: async (context) => { /* mock invalid response */ } },
  LOGOUT: { exec: async (context) => { /* trigger logout */ } },
  RETRY: { exec: async (context) => { /* retry logic */ } }
});

// Generate test paths (covers all transitions)
describe('Auth FSM', () => {
  const testPlans = authModel.getSimplePathPlans();

  testPlans.forEach((plan) => {
    describe(plan.description, () => {
      plan.paths.forEach((path) => {
        it(path.description, async () => {
          await path.test({
            // Initial context
            userId: null,
            token: null
          });
        });
      });
    });
  });

  // Coverage check - fails if any state uncovered
  it('should have full coverage', () => {
    return authModel.testCoverage();
  });
});
```

**Coverage Metrics**:
- **testCoverage()** throws error if any state node missing from coverage
- Ensures 100% transition coverage automatically
- Detects unreachable states and deadlocks

#### Alternative FSM Testing Tools

**typescript-fsm**:
- Strongly typed FSM with async operations
- Zero dependencies
- Lightweight for simple state machines

**Robot**:
- Functional approach to state machines
- Excellent for immutable state transitions
- Smaller bundle size than XState

**GraphWalker**:
- Open-source model-based testing tool
- Generates tests from state diagrams
- Supports multiple programming languages

### 1.3 SPEK v2 FSM Testing Strategy

#### Core FSMs to Test

1. **Queen FSM** (Orchestration)
   - States: IDLE, COORDINATING, MONITORING, RECOVERING, FAILED
   - Events: SPAWN_PRINCESS, MONITOR_PROGRESS, HANDLE_FAILURE, SHUTDOWN
   - Critical Paths: Spawn → Monitor → Recover → Shutdown

2. **Princess FSM** (Domain Management)
   - States: IDLE, PLANNING, DELEGATING, COORDINATING, COMPLETED, FAILED
   - Events: RECEIVE_ORDER, PLAN_TASKS, SPAWN_DRONES, AGGREGATE_RESULTS
   - Critical Paths: Order → Plan → Delegate → Aggregate → Complete

3. **Drone FSM** (Task Execution)
   - States: IDLE, EXECUTING, REPORTING, COMPLETED, FAILED
   - Events: RECEIVE_TASK, EXECUTE, REPORT_PROGRESS, COMPLETE
   - Critical Paths: Task → Execute → Report → Complete

4. **TransitionHub** (Centralized Transitions)
   - States: N/A (manages transitions for all FSMs)
   - Events: All FSM events routed through hub
   - Critical Paths: Event validation → Guard checking → Transition execution

5. **Quality Gate FSM** (Validation)
   - States: IDLE, PLANNED, EXECUTING, MEASURING, SYNCHRONIZING, VALIDATED, FAILED
   - Events: PLAN_SEQUENCE, START_EXECUTION, MEASURE_CRITERIA, SYNCHRONIZE_GATES
   - Critical Paths: Plan → Execute → Measure → Synchronize → Validate

#### Test Organization Pattern

```typescript
// tests/fsm/[FSM_NAME]/
// ├── unit/
// │   ├── state-handlers.test.ts      # Test individual state logic
// │   ├── transition-guards.test.ts   # Test guard conditions
// │   └── invariants.test.ts          # Test state invariants
// ├── integration/
// │   ├── transition-coverage.test.ts # Test all state transitions
// │   ├── error-recovery.test.ts      # Test error states and recovery
// │   └── persistence.test.ts         # Test state persistence
// └── model/
//     └── fsm-model.test.ts           # XState model-based tests

// Example: tests/fsm/queen/unit/state-handlers.test.ts
import { QueenFSM } from '@/architecture/langgraph/queen/fsm/QueenFSM';
import { QueenState, QueenEvent } from '@/architecture/langgraph/queen/fsm/QueenFSMTypes';

describe('QueenFSM - State Handlers', () => {
  let queenFSM: QueenFSM;

  beforeEach(() => {
    queenFSM = new QueenFSM({ queenId: 'test-queen' });
  });

  describe('COORDINATING State', () => {
    it('should handle SPAWN_PRINCESS event', async () => {
      await queenFSM.transition(QueenEvent.SPAWN_PRINCESS, {
        domain: 'development',
        princessId: 'princess-1'
      });

      const state = queenFSM.getCurrentState();
      expect(state).toBe(QueenState.COORDINATING);
      expect(queenFSM.context.activePrincesses).toContain('princess-1');
    });

    it('should enforce invariant: max 10 princesses', async () => {
      // Spawn 10 princesses
      for (let i = 0; i < 10; i++) {
        await queenFSM.transition(QueenEvent.SPAWN_PRINCESS, {
          domain: 'test',
          princessId: `princess-${i}`
        });
      }

      // 11th should fail invariant check
      await expect(
        queenFSM.transition(QueenEvent.SPAWN_PRINCESS, {
          domain: 'test',
          princessId: 'princess-11'
        })
      ).rejects.toThrow('Invariant violation: Maximum 10 princesses');
    });
  });
});
```

### 1.4 Hierarchical State Machine Testing

SPEK v2 uses hierarchical FSMs (Queen → Princess → Drone). Testing approach:

**Strategy 1: Test Each Level Independently**
- Queen FSM tests mock Princess responses
- Princess FSM tests mock Drone responses
- Drone FSM tests use real implementations

**Strategy 2: Test Interaction Patterns**
- Integration tests verify message passing
- Use spy pattern (not mock) to observe actual behavior
- Validate event propagation through hierarchy

**Example**:
```typescript
describe('Queen-Princess Integration', () => {
  let queenFSM: QueenFSM;
  let princessFSM: PrincessFSM;
  let messageRouter: MessageRouter;

  beforeEach(() => {
    messageRouter = new MessageRouter();
    queenFSM = new QueenFSM({ router: messageRouter });
    princessFSM = new PrincessFSM({ router: messageRouter });
  });

  it('should propagate order from Queen to Princess', async () => {
    const orderSpy = jest.spyOn(princessFSM, 'receiveOrder');

    await queenFSM.transition(QueenEvent.ISSUE_ORDER, {
      domain: 'development',
      order: { task: 'implement-feature', priority: 'high' }
    });

    await waitForAsyncOperations();

    expect(orderSpy).toHaveBeenCalledWith({
      task: 'implement-feature',
      priority: 'high'
    });
    expect(princessFSM.getCurrentState()).toBe(PrincessState.PLANNING);
  });
});
```

### 1.5 Test Coverage Requirements

For SPEK v2 FSMs:
- **State Coverage**: 100% (all states visited)
- **Transition Coverage**: 100% (all state-event pairs tested)
- **Path Coverage**: >=80% (critical paths covered)
- **Guard Coverage**: 100% (all guard conditions tested)
- **Invariant Coverage**: 100% (all invariants validated)
- **Error Recovery**: 100% (all error states tested)

**Automated Coverage Enforcement**:
```typescript
// tests/fsm/coverage-check.test.ts
import { allFSMModels } from '@/fsm/models';

describe('FSM Coverage Check', () => {
  it('should have 100% state coverage across all FSMs', () => {
    allFSMModels.forEach((model, name) => {
      expect(() => model.testCoverage()).not.toThrow();
    });
  });

  it('should have 100% transition coverage', async () => {
    const coverage = await collectTransitionCoverage();
    expect(coverage.percentage).toBe(100);
  });
});
```

---

## Part 2: Multi-Agent Coordination Testing

### 2.1 Multi-Agent Testing Challenges (2025)

**MAST Taxonomy** (Multi-Agent System Failure):
- **Inter-Agent Misalignment**: Communication breakdowns, inconsistent goals
- **Memory Management Failures**: Context loss, incorrect state persistence
- **Coordination Protocol Violations**: Race conditions, deadlocks
- **Tool Invocation Errors**: Incorrect parameters, missing dependencies

### 2.2 Enterprise Testing Frameworks

#### Microsoft Agent Framework (Public Preview 2025)

**Features**:
- Multi-agent observability with OpenTelemetry integration
- Standardized tracing for agent workflows and tool invocations
- Durability and compliance for enterprise deployments

**Testing Pattern**:
```typescript
import { AgentFramework } from '@microsoft/agent-framework';
import { trace, context } from '@opentelemetry/api';

describe('Multi-Agent Coordination', () => {
  let framework: AgentFramework;
  let tracer: Tracer;

  beforeEach(() => {
    framework = new AgentFramework({
      observability: {
        enabled: true,
        tracingEndpoint: 'http://localhost:4318'
      }
    });
    tracer = trace.getTracer('test-tracer');
  });

  it('should coordinate Queen-Princess-Drone workflow', async () => {
    const span = tracer.startSpan('workflow-test');

    await framework.executeWorkflow({
      name: 'feature-implementation',
      agents: [
        { role: 'queen', agentId: 'queen-1' },
        { role: 'princess', agentId: 'princess-dev', domain: 'development' },
        { role: 'drone', agentId: 'drone-coder', capability: 'coding' }
      ]
    });

    const traces = await framework.getTraces(span.spanContext().traceId);

    // Verify agent coordination
    expect(traces).toContainAgentInteraction('queen-1', 'princess-dev', 'order');
    expect(traces).toContainAgentInteraction('princess-dev', 'drone-coder', 'task');
    expect(traces).toContainAgentInteraction('drone-coder', 'princess-dev', 'result');

    span.end();
  });
});
```

#### Google Agent Development Kit (ADK)

**Features**:
- Programmatic evaluation via `AgentEvaluator.evaluate()`
- Web UI for test visualization
- Command-line evaluation tool

**Testing Pattern**:
```typescript
import { AgentEvaluator } from '@google-cloud/agent-development-kit';

describe('Agent Quality Evaluation', () => {
  let evaluator: AgentEvaluator;

  beforeEach(() => {
    evaluator = new AgentEvaluator({
      projectId: 'spek-v2-testing',
      location: 'us-central1'
    });
  });

  it('should evaluate research agent performance', async () => {
    const result = await evaluator.evaluate({
      agentId: 'research-agent',
      testCases: [
        {
          input: 'Research FSM testing patterns',
          expectedOutput: {
            containsKeywords: ['XState', 'model-based testing', 'coverage'],
            minReferences: 5,
            maxResponseTime: 30000
          }
        }
      ]
    });

    expect(result.accuracy).toBeGreaterThanOrEqual(0.85);
    expect(result.latency.p95).toBeLessThan(30000);
  });
});
```

### 2.3 SPEK v2 Agent Testing Strategy

#### Agent Categories and Test Requirements

**Category 1: Research Agents** (Gemini 2.5 Pro)
- Agents: researcher, specification, architecture
- Test Focus: Large context handling (1M tokens), accuracy, reference quality
- Metrics: Factuality score >=0.92, citation count >=5, response time <30s

**Category 2: Development Agents** (GPT-5 Codex)
- Agents: coder, sparc-coder, frontend-developer
- Test Focus: Code quality, syntax correctness, test pass rate
- Metrics: Compilation success 100%, test pass rate >=90%, code coverage >=80%

**Category 3: Quality Agents** (Claude Opus 4.1)
- Agents: reviewer, tester, production-validator
- Test Focus: Bug detection, test coverage, security scanning
- Metrics: Bug detection rate >=95%, false positive rate <5%, security score >=95%

**Category 4: Coordination Agents** (Claude Sonnet 4)
- Agents: sparc-coord, hierarchical-coordinator, task-orchestrator
- Test Focus: Task distribution, deadlock prevention, resource optimization
- Metrics: Task completion rate 100%, coordination overhead <10%, no deadlocks

#### Multi-Agent Test Patterns

**Pattern 1: Unit Testing Individual Agents**
```typescript
describe('Research Agent', () => {
  let researchAgent: ResearchAgent;

  beforeEach(() => {
    researchAgent = new ResearchAgent({
      model: 'gemini-2.5-pro',
      mcpServers: ['deepwiki', 'firecrawl', 'ref']
    });
  });

  it('should research FSM patterns with citations', async () => {
    const result = await researchAgent.execute({
      query: 'FSM testing best practices TypeScript',
      minReferences: 5
    });

    expect(result.citations.length).toBeGreaterThanOrEqual(5);
    expect(result.content).toContain('XState');
    expect(result.factualityScore).toBeGreaterThanOrEqual(0.92);
  });
});
```

**Pattern 2: Integration Testing Agent Coordination**
```typescript
describe('Queen-Princess-Drone Coordination', () => {
  let queen: QueenAgent;
  let developmentPrincess: DevelopmentPrincess;
  let coderDrone: CoderDrone;

  beforeEach(async () => {
    queen = await QueenAgent.spawn({ queenId: 'test-queen' });
    developmentPrincess = await queen.spawnPrincess({
      domain: 'development',
      princessId: 'princess-dev'
    });
    coderDrone = await developmentPrincess.spawnDrone({
      capability: 'coding',
      droneId: 'drone-coder'
    });
  });

  it('should coordinate feature implementation workflow', async () => {
    // Queen issues order
    const order = await queen.issueOrder({
      domain: 'development',
      task: 'Implement authentication FSM',
      requirements: {
        states: ['IDLE', 'AUTHENTICATING', 'AUTHENTICATED', 'FAILED'],
        events: ['LOGIN', 'LOGOUT', 'ERROR']
      }
    });

    // Princess plans and delegates
    const plan = await developmentPrincess.planTasks(order);
    expect(plan.subtasks.length).toBeGreaterThan(0);

    // Drone executes
    const result = await coderDrone.executeTask(plan.subtasks[0]);
    expect(result.status).toBe('COMPLETED');
    expect(result.artifacts).toContainFilesMatching('**/AuthFSM.ts');

    // Verify coordination flow
    const trace = await queen.getExecutionTrace();
    expect(trace).toMatchWorkflow([
      { agent: 'queen', action: 'ISSUE_ORDER' },
      { agent: 'princess', action: 'PLAN_TASKS' },
      { agent: 'drone', action: 'EXECUTE_TASK' },
      { agent: 'drone', action: 'REPORT_RESULT' },
      { agent: 'princess', action: 'AGGREGATE_RESULTS' },
      { agent: 'queen', action: 'VALIDATE_COMPLETION' }
    ]);
  });
});
```

**Pattern 3: Swarm Testing (Multiple Agents in Parallel)**
```typescript
describe('Development Swarm', () => {
  it('should coordinate 10 drones in parallel', async () => {
    const princess = await DevelopmentPrincess.spawn({
      princessId: 'princess-dev',
      maxDrones: 10
    });

    const tasks = Array.from({ length: 10 }, (_, i) => ({
      taskId: `task-${i}`,
      description: `Implement feature ${i}`,
      capability: 'coding'
    }));

    const results = await princess.executeTasks(tasks, {
      parallelism: 10,
      timeout: 60000
    });

    expect(results.filter(r => r.status === 'COMPLETED').length).toBe(10);
    expect(results.some(r => r.status === 'FAILED')).toBe(false);

    // Verify no race conditions
    const fileWrites = results.flatMap(r => r.filesModified);
    const duplicates = findDuplicates(fileWrites);
    expect(duplicates.length).toBe(0);
  });
});
```

### 2.4 Coordination Testing Metrics

**Performance Metrics**:
- **Throughput**: Tasks completed per minute
- **Latency**: Time from task assignment to completion (p50, p95, p99)
- **Coordination Overhead**: Time spent on agent communication vs execution
- **Resource Utilization**: CPU, memory, API calls per task

**Quality Metrics**:
- **Task Success Rate**: Percentage of tasks completed successfully
- **Coordination Accuracy**: Correct task routing rate
- **Error Recovery Rate**: Percentage of failures recovered automatically
- **Deadlock Detection**: Zero deadlocks allowed

**Test Implementation**:
```typescript
describe('Coordination Metrics', () => {
  it('should achieve target performance metrics', async () => {
    const metrics = await runCoordinationBenchmark({
      agents: 22,
      tasksPerAgent: 100,
      duration: 300000 // 5 minutes
    });

    expect(metrics.throughput).toBeGreaterThanOrEqual(10); // 10 tasks/min
    expect(metrics.latency.p95).toBeLessThan(60000); // 60s at p95
    expect(metrics.coordinationOverhead).toBeLessThan(0.10); // <10%
    expect(metrics.taskSuccessRate).toBeGreaterThanOrEqual(0.95); // 95%
    expect(metrics.deadlockCount).toBe(0);
  });
});
```

---

## Part 3: End-to-End Testing for 3-Loop System

### 3.1 3-Loop System Architecture

**Loop 1: Planning** (spec → research → premortem → plan)
- Agents: researcher, specification, architecture
- Output: Validated plan with risk mitigation

**Loop 2: Development** (swarm → MECE → deploy → theater)
- Agents: 22 agents (coder, tester, reviewer, etc.)
- Output: Implemented features with quality validation

**Loop 3: Quality** (analysis → root cause → fixes → validation)
- Agents: production-validator, code-analyzer, security-manager
- Output: Zero critical issues, all tests passing

### 3.2 E2E Testing Tools (2025)

#### Octomind - AI-Powered E2E Testing

**Features**:
- Agentic test generation from user flows
- Auto-fixing for flaky tests
- Playwright-based deterministic execution
- Full lifecycle support (build, run, fix)

**Testing Pattern**:
```typescript
import { OctomindAgent } from 'octomind';

describe('3-Loop E2E - Feature Implementation', () => {
  let octomind: OctomindAgent;

  beforeEach(() => {
    octomind = new OctomindAgent({
      baseUrl: 'http://localhost:3000',
      testFramework: 'playwright'
    });
  });

  it('should complete full 3-loop workflow for auth feature', async () => {
    // Loop 1: Planning
    const planningResult = await octomind.testUserFlow({
      flow: 'Loop 1: Planning',
      steps: [
        { action: 'navigate', url: '/spec/new' },
        { action: 'input', selector: '#feature-name', value: 'Authentication' },
        { action: 'click', selector: '#research-web' },
        { action: 'wait', selector: '.research-results' },
        { action: 'click', selector: '#run-premortem' },
        { action: 'wait', selector: '.premortem-complete' },
        { action: 'click', selector: '#generate-plan' },
        { action: 'assert', selector: '.plan-validated', exists: true }
      ],
      assertions: [
        { type: 'quality-gate', metric: 'specCompleteness', threshold: 0.90 },
        { type: 'quality-gate', metric: 'riskMitigation', threshold: 0.80 }
      ]
    });

    expect(planningResult.passed).toBe(true);

    // Loop 2: Development
    const developmentResult = await octomind.testUserFlow({
      flow: 'Loop 2: Development',
      steps: [
        { action: 'navigate', url: '/dev/swarm' },
        { action: 'click', selector: '#spawn-agents' },
        { action: 'wait', selector: '.agents-active', count: 22 },
        { action: 'click', selector: '#execute-tasks' },
        { action: 'wait', selector: '.deployment-complete', timeout: 300000 },
        { action: 'assert', selector: '.theater-score', value: '<60' }
      ],
      assertions: [
        { type: 'quality-gate', metric: 'testCoverage', threshold: 0.80 },
        { type: 'quality-gate', metric: 'theaterScore', threshold: 60, operator: '<' }
      ]
    });

    expect(developmentResult.passed).toBe(true);

    // Loop 3: Quality
    const qualityResult = await octomind.testUserFlow({
      flow: 'Loop 3: Quality',
      steps: [
        { action: 'navigate', url: '/quality/analysis' },
        { action: 'click', selector: '#run-comprehensive-analysis' },
        { action: 'wait', selector: '.analysis-complete' },
        { action: 'assert', selector: '.critical-issues', value: '0' },
        { action: 'assert', selector: '.test-pass-rate', value: '100%' }
      ],
      assertions: [
        { type: 'quality-gate', metric: 'criticalIssues', threshold: 0 },
        { type: 'quality-gate', metric: 'testPassRate', threshold: 1.0 }
      ]
    });

    expect(qualityResult.passed).toBe(true);
  });
});
```

#### Checksum - Session-Based E2E Testing

**Features**:
- Generates tests from user sessions
- Supports Playwright and Cypress
- Automatic test maintenance
- Real-world user flow capture

**Testing Pattern**:
```typescript
import { ChecksumRecorder } from 'checksum';

describe('3-Loop System - Session Recording', () => {
  it('should record and replay full development session', async () => {
    const recorder = new ChecksumRecorder({
      sessionId: 'auth-feature-session',
      outputFormat: 'playwright'
    });

    // Record actual user session
    await recorder.startRecording();

    // User executes full 3-loop workflow manually
    // Checksum captures all interactions

    await recorder.stopRecording();

    // Generate test from recording
    const test = await recorder.generateTest({
      name: 'Auth Feature - Full 3-Loop',
      assertions: 'auto' // AI-generated assertions
    });

    // Replay test
    const result = await test.run();
    expect(result.passed).toBe(true);
  });
});
```

### 3.3 SPEK v2 E2E Test Suite

#### Test 1: Complete Feature Implementation
```typescript
describe('E2E: Authentication Feature', () => {
  it('should complete all 3 loops for auth feature', async () => {
    const session = await startE2ESession({
      feature: 'authentication',
      timeout: 600000 // 10 minutes
    });

    // Loop 1: Planning
    const loop1 = await session.executeLoop1({
      researchQueries: ['OAuth 2.0 best practices', 'FSM auth patterns'],
      specRequirements: {
        states: 4,
        events: 4,
        guards: 2
      },
      premortemChecks: ['security', 'performance', 'scalability']
    });

    expect(loop1.quality.specCompleteness).toBeGreaterThanOrEqual(0.90);
    expect(loop1.quality.riskMitigation).toBeGreaterThanOrEqual(0.80);
    expect(loop1.artifacts).toContainFile('SPEC.md');
    expect(loop1.artifacts).toContainFile('PLAN.json');

    // Loop 2: Development
    const loop2 = await session.executeLoop2({
      agents: {
        coder: 5,
        tester: 3,
        reviewer: 2
      },
      parallelism: 10,
      qualityGates: {
        compilation: true,
        tests: true,
        lint: true,
        theater: true
      }
    });

    expect(loop2.quality.testCoverage).toBeGreaterThanOrEqual(0.80);
    expect(loop2.quality.theaterScore).toBeLessThan(60);
    expect(loop2.artifacts).toContainFile('src/auth/AuthFSM.ts');
    expect(loop2.artifacts).toContainFile('tests/auth/AuthFSM.test.ts');

    // Loop 3: Quality
    const loop3 = await session.executeLoop3({
      analyzers: ['nasa-pot10', 'connascence', 'security', 'theater'],
      autoFix: true,
      maxIterations: 3
    });

    expect(loop3.quality.criticalIssues).toBe(0);
    expect(loop3.quality.nasaCompliance).toBeGreaterThanOrEqual(0.92);
    expect(loop3.quality.testPassRate).toBe(1.0);
  });
});
```

#### Test 2: Error Recovery and Convergence
```typescript
describe('E2E: Error Recovery', () => {
  it('should recover from failures and converge to quality', async () => {
    const session = await startE2ESession({
      feature: 'payment-processing',
      injectFailures: true // Simulate failures
    });

    // Loop 2: Development with failures
    const loop2 = await session.executeLoop2({
      agents: { coder: 3 },
      failureRate: 0.30 // 30% task failure rate
    });

    expect(loop2.failures.length).toBeGreaterThan(0);

    // Loop 3: Should recover and fix all failures
    const loop3 = await session.executeLoop3({
      maxIterations: 10,
      convergenceCriteria: {
        qualityImprovement: 0.05,
        maxIterations: 10
      }
    });

    expect(loop3.converged).toBe(true);
    expect(loop3.quality.testPassRate).toBe(1.0);
    expect(loop3.iterationsRequired).toBeLessThanOrEqual(10);
  });
});
```

### 3.4 E2E Testing in gVisor Sandbox

**Security Isolation**:
```typescript
describe('E2E: gVisor Sandbox', () => {
  let sandbox: GVisorSandbox;

  beforeEach(async () => {
    sandbox = await GVisorSandbox.create({
      runtime: 'runsc',
      network: 'none', // No internet access
      filesystem: {
        allowed: ['/workspace', '/tmp'],
        readonly: ['/usr', '/bin', '/lib']
      }
    });
  });

  afterEach(async () => {
    await sandbox.destroy();
  });

  it('should execute 3-loop system in isolated sandbox', async () => {
    const result = await sandbox.execute({
      command: 'npm run 3-loop:forward',
      environment: {
        NODE_ENV: 'test',
        SPEK_MODE: 'sandbox'
      },
      timeout: 600000
    });

    expect(result.exitCode).toBe(0);
    expect(result.violations).toHaveLength(0); // No security violations
    expect(result.networkCalls).toHaveLength(0); // No external network access
  });

  it('should detect and block malicious code execution', async () => {
    const result = await sandbox.execute({
      command: 'node malicious-script.js',
      timeout: 10000
    });

    expect(result.blocked).toBe(true);
    expect(result.reason).toContain('syscall violation');
  });
});
```

---

## Part 4: Performance Benchmarking

### 4.1 Performance Benchmarking Tools

#### Grafana k6 - Load Testing

**Strengths**:
- Hybrid load testing (protocol + browser)
- Distributed testing for Kubernetes
- Real-time metrics and dashboards
- Scripting with JavaScript

**Benchmarking Pattern**:
```javascript
// k6-benchmarks/3-loop-load-test.js
import http from 'k6/http';
import { check, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const loop1Duration = new Trend('loop1_duration');
const loop2Duration = new Trend('loop2_duration');
const loop3Duration = new Trend('loop3_duration');
const taskSuccessRate = new Rate('task_success_rate');

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 concurrent workflows
    { duration: '5m', target: 10 },   // Stay at 10 for 5 minutes
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<30000'], // 95% requests under 30s
    'loop1_duration': ['p(95)<60000'],    // Loop 1 under 60s at p95
    'loop2_duration': ['p(95)<300000'],   // Loop 2 under 5min at p95
    'loop3_duration': ['p(95)<120000'],   // Loop 3 under 2min at p95
    'task_success_rate': ['rate>0.95'],   // 95% success rate
  },
};

export default function () {
  group('Loop 1: Planning', function () {
    const startTime = Date.now();

    // Research phase
    let res = http.post('http://localhost:3000/api/research', {
      query: 'FSM testing patterns'
    });
    check(res, { 'research succeeded': (r) => r.status === 200 });

    // Spec generation
    res = http.post('http://localhost:3000/api/spec/generate', {
      feature: 'test-feature'
    });
    check(res, { 'spec generated': (r) => r.status === 200 });

    // Premortem
    res = http.post('http://localhost:3000/api/premortem', {
      specId: res.json('specId')
    });
    check(res, { 'premortem completed': (r) => r.status === 200 });

    loop1Duration.add(Date.now() - startTime);
  });

  group('Loop 2: Development', function () {
    const startTime = Date.now();

    // Spawn agents
    let res = http.post('http://localhost:3000/api/agents/spawn', {
      count: 22
    });
    check(res, { 'agents spawned': (r) => r.status === 200 });

    // Execute tasks
    res = http.post('http://localhost:3000/api/tasks/execute', {
      workflowId: res.json('workflowId')
    });
    check(res, { 'tasks executed': (r) => r.status === 200 });

    taskSuccessRate.add(res.json('successRate') > 0.95);
    loop2Duration.add(Date.now() - startTime);
  });

  group('Loop 3: Quality', function () {
    const startTime = Date.now();

    // Run analysis
    let res = http.post('http://localhost:3000/api/quality/analyze');
    check(res, { 'analysis completed': (r) => r.status === 200 });

    // Auto-fix issues
    res = http.post('http://localhost:3000/api/quality/auto-fix', {
      analysisId: res.json('analysisId')
    });
    check(res, { 'fixes applied': (r) => r.status === 200 });

    loop3Duration.add(Date.now() - startTime);
  });
}
```

**Running Benchmarks**:
```bash
# Local load test
k6 run k6-benchmarks/3-loop-load-test.js

# Distributed load test (Kubernetes)
k6 cloud run k6-benchmarks/3-loop-load-test.js

# Results analysis
k6 inspect k6-benchmarks/3-loop-load-test.js
```

#### Google Lighthouse - Performance Metrics

**Strengths**:
- Web Vitals measurement (LCP, FID, CLS)
- Performance scoring (0-100)
- Accessibility and SEO audits
- CI/CD integration

**Benchmarking Pattern**:
```typescript
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';

describe('Performance Benchmarks - Lighthouse', () => {
  it('should meet performance thresholds for dashboard', async () => {
    const chrome = await chromeLauncher.launch({
      chromeFlags: ['--headless']
    });

    const options = {
      logLevel: 'info',
      output: 'json',
      port: chrome.port,
      onlyCategories: ['performance']
    };

    const runnerResult = await lighthouse(
      'http://localhost:3000/dashboard',
      options
    );

    const { lhr } = runnerResult;

    // Performance score
    expect(lhr.categories.performance.score).toBeGreaterThanOrEqual(0.90);

    // Web Vitals
    expect(lhr.audits['largest-contentful-paint'].numericValue).toBeLessThan(2500);
    expect(lhr.audits['first-input-delay'].numericValue).toBeLessThan(100);
    expect(lhr.audits['cumulative-layout-shift'].numericValue).toBeLessThan(0.1);

    // Resource optimization
    expect(lhr.audits['total-byte-weight'].numericValue).toBeLessThan(1000000); // <1MB

    await chrome.kill();
  });
});
```

### 4.2 SPEK v2 Performance Benchmarks

#### Benchmark 1: Agent Spawn Time
```typescript
describe('Performance: Agent Spawning', () => {
  it('should spawn 22 agents under 5 seconds', async () => {
    const startTime = performance.now();

    const agents = await Promise.all([
      spawnAgent('researcher'),
      spawnAgent('coder-1'),
      spawnAgent('coder-2'),
      spawnAgent('coder-3'),
      spawnAgent('coder-4'),
      spawnAgent('coder-5'),
      spawnAgent('tester-1'),
      spawnAgent('tester-2'),
      spawnAgent('tester-3'),
      spawnAgent('reviewer-1'),
      spawnAgent('reviewer-2'),
      // ... 11 more agents
    ]);

    const duration = performance.now() - startTime;

    expect(agents.length).toBe(22);
    expect(duration).toBeLessThan(5000); // 5 seconds
  });
});
```

#### Benchmark 2: FSM Transition Performance
```typescript
describe('Performance: FSM Transitions', () => {
  it('should handle 1000 transitions per second', async () => {
    const fsm = new QueenFSM({ queenId: 'perf-test' });
    const transitionCount = 1000;
    const startTime = performance.now();

    for (let i = 0; i < transitionCount; i++) {
      await fsm.transition(QueenEvent.MONITOR_PROGRESS, {
        princessId: `princess-${i % 10}`
      });
    }

    const duration = performance.now() - startTime;
    const throughput = (transitionCount / duration) * 1000; // per second

    expect(throughput).toBeGreaterThanOrEqual(1000);
  });
});
```

#### Benchmark 3: 3-Loop System End-to-End
```typescript
describe('Performance: 3-Loop E2E', () => {
  it('should complete 3-loop workflow under 10 minutes', async () => {
    const benchmark = new E2EBenchmark({
      feature: 'sample-feature',
      complexity: 'medium'
    });

    const result = await benchmark.run({
      loop1: { timeout: 60000 },   // 1 minute
      loop2: { timeout: 420000 },  // 7 minutes
      loop3: { timeout: 120000 }   // 2 minutes
    });

    expect(result.totalDuration).toBeLessThan(600000); // 10 minutes
    expect(result.loop1Duration).toBeLessThan(60000);
    expect(result.loop2Duration).toBeLessThan(420000);
    expect(result.loop3Duration).toBeLessThan(120000);
  });
});
```

### 4.3 Performance Metrics Dashboard

**Key Metrics to Track**:
```typescript
interface PerformanceMetrics {
  // Agent Metrics
  agentSpawnTime: {
    p50: number;
    p95: number;
    p99: number;
  };
  agentTaskDuration: {
    p50: number;
    p95: number;
    p99: number;
  };

  // FSM Metrics
  fsmTransitionLatency: {
    p50: number;
    p95: number;
    p99: number;
  };
  fsmStateChanges: number;

  // 3-Loop Metrics
  loop1Duration: { p50: number; p95: number; p99: number };
  loop2Duration: { p50: number; p95: number; p99: number };
  loop3Duration: { p50: number; p95: number; p99: number };

  // Resource Metrics
  cpuUsage: { avg: number; max: number };
  memoryUsage: { avg: number; max: number };
  apiCalls: { total: number; cached: number };

  // Quality Metrics
  taskSuccessRate: number;
  testPassRate: number;
  deploymentSuccessRate: number;
}
```

**Grafana Dashboard Configuration**:
```yaml
# grafana/dashboards/spek-v2-performance.json
{
  "dashboard": {
    "title": "SPEK v2 Performance",
    "panels": [
      {
        "title": "Agent Spawn Time (p95)",
        "targets": [{ "expr": "histogram_quantile(0.95, agent_spawn_duration_seconds)" }],
        "thresholds": [{ "value": 5, "color": "red" }]
      },
      {
        "title": "3-Loop Duration",
        "targets": [
          { "expr": "loop1_duration_seconds", "legendFormat": "Loop 1" },
          { "expr": "loop2_duration_seconds", "legendFormat": "Loop 2" },
          { "expr": "loop3_duration_seconds", "legendFormat": "Loop 3" }
        ]
      },
      {
        "title": "Task Success Rate",
        "targets": [{ "expr": "task_success_rate" }],
        "thresholds": [{ "value": 0.95, "color": "red" }]
      }
    ]
  }
}
```

---

## Part 5: Implementation Recommendations

### 5.1 Test Infrastructure Setup

**Directory Structure**:
```
tests/
├── unit/                           # Unit tests for individual components
│   ├── fsm/                        # FSM state handlers, guards, invariants
│   ├── agents/                     # Individual agent logic
│   └── utils/                      # Utility functions
├── integration/                    # Integration tests for component interaction
│   ├── fsm/                        # FSM transition coverage, error recovery
│   ├── coordination/               # Multi-agent coordination
│   └── queen-princess-drone/      # Hierarchy integration
├── e2e/                            # End-to-end tests for full workflows
│   ├── 3-loop/                     # Complete 3-loop workflows
│   ├── feature-implementation/    # Feature development flows
│   └── sandbox/                    # gVisor sandbox tests
├── performance/                    # Performance benchmarks
│   ├── k6/                         # k6 load tests
│   ├── lighthouse/                 # Lighthouse performance tests
│   └── benchmarks/                 # Custom benchmarks
└── fixtures/                       # Test data and mocks
    ├── agents/                     # Mock agent responses
    ├── fsm/                        # FSM test scenarios
    └── workflows/                  # Workflow test data
```

**Test Configuration**:
```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts'
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    // FSM-specific thresholds
    'src/fsm/**/*.ts': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  testTimeout: 30000,
  maxWorkers: '50%'
};
```

### 5.2 CI/CD Integration

**GitHub Actions Workflow**:
```yaml
# .github/workflows/test-suite.yml
name: SPEK v2 Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3

  fsm-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:fsm
      - name: Check FSM Coverage
        run: |
          coverage=$(npm run test:fsm:coverage --silent | grep -oP '\d+(?=%)')
          if [ $coverage -lt 100 ]; then
            echo "FSM coverage $coverage% is below 100% requirement"
            exit 1
          fi

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - run: npm run start:test &
      - run: npm run test:e2e

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: grafana/k6-action@v0.3.0
        with:
          filename: k6-benchmarks/3-loop-load-test.js
      - name: Check performance thresholds
        run: |
          npm run test:performance
          npm run benchmark:analyze

  sandbox-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install gVisor
        run: |
          wget https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc
          chmod +x runsc
          sudo mv runsc /usr/local/bin/
      - run: npm ci
      - run: npm run test:sandbox
```

### 5.3 Test Data Management

**Fixture Strategy**:
```typescript
// tests/fixtures/fsm-scenarios.ts
export const FSMTestScenarios = {
  queen: {
    normalFlow: {
      initialState: 'IDLE',
      events: [
        { event: 'SPAWN_PRINCESS', data: { domain: 'development' } },
        { event: 'MONITOR_PROGRESS', data: { princessId: 'princess-1' } },
        { event: 'VALIDATE_COMPLETION', data: { workflowId: 'wf-1' } },
        { event: 'SHUTDOWN', data: {} }
      ],
      expectedStates: ['IDLE', 'COORDINATING', 'MONITORING', 'VALIDATING', 'IDLE']
    },
    errorRecovery: {
      initialState: 'COORDINATING',
      events: [
        { event: 'HANDLE_FAILURE', data: { error: 'Princess timeout' } },
        { event: 'RECOVER', data: { strategy: 'respawn' } },
        { event: 'SHUTDOWN', data: {} }
      ],
      expectedStates: ['COORDINATING', 'RECOVERING', 'IDLE']
    }
  },
  princess: {
    normalFlow: {
      initialState: 'IDLE',
      events: [
        { event: 'RECEIVE_ORDER', data: { task: 'implement-feature' } },
        { event: 'PLAN_TASKS', data: {} },
        { event: 'SPAWN_DRONES', data: { count: 5 } },
        { event: 'AGGREGATE_RESULTS', data: {} },
        { event: 'COMPLETE', data: {} }
      ],
      expectedStates: ['IDLE', 'PLANNING', 'DELEGATING', 'COORDINATING', 'COMPLETED']
    }
  },
  drone: {
    normalFlow: {
      initialState: 'IDLE',
      events: [
        { event: 'RECEIVE_TASK', data: { taskId: 'task-1' } },
        { event: 'EXECUTE', data: {} },
        { event: 'REPORT_PROGRESS', data: { progress: 0.5 } },
        { event: 'COMPLETE', data: { result: 'success' } }
      ],
      expectedStates: ['IDLE', 'EXECUTING', 'REPORTING', 'COMPLETED']
    }
  }
};
```

### 5.4 Recommended Testing Tools

**Essential Tools**:
1. **XState** - FSM implementation and testing
2. **Jest** - Unit and integration testing framework
3. **Microsoft Agent Framework** - Multi-agent observability
4. **Octomind** - E2E agentic testing
5. **Grafana k6** - Load testing
6. **Google Lighthouse** - Performance audits
7. **gVisor** - Sandbox isolation

**Optional Tools**:
8. **Google ADK** - Agent evaluation framework
9. **Checksum** - Session-based E2E testing
10. **Playwright** - Browser automation (for UI testing)
11. **Cypress** - Alternative E2E framework

### 5.5 Quality Gates Integration

**Test-Based Quality Gates**:
```typescript
// src/orchestration/quality/TestGate.ts
export class TestGate implements QualityGate {
  async evaluate(): Promise<GateResult> {
    const results = await Promise.all([
      this.runUnitTests(),
      this.runFSMTests(),
      this.runIntegrationTests(),
      this.runE2ETests(),
      this.runPerformanceTests()
    ]);

    const metrics = {
      unitTestPassRate: results[0].passRate,
      fsmCoverage: results[1].coverage,
      integrationTestPassRate: results[2].passRate,
      e2eTestPassRate: results[3].passRate,
      performanceScore: results[4].score
    };

    const passed =
      metrics.unitTestPassRate >= 0.95 &&
      metrics.fsmCoverage === 1.0 &&
      metrics.integrationTestPassRate >= 0.90 &&
      metrics.e2eTestPassRate >= 0.85 &&
      metrics.performanceScore >= 0.80;

    return {
      passed,
      metrics,
      details: results
    };
  }
}
```

---

## Part 6: Testing for Specific SPEK v2 Components

### 6.1 Testing 5 Core FSMs

**Queen FSM Testing**:
```typescript
// tests/fsm/queen/model.test.ts
import { createModel } from '@xstate/test';
import { queenMachine } from '@/architecture/langgraph/queen/fsm/QueenFSM';

const queenModel = createModel(queenMachine).withEvents({
  SPAWN_PRINCESS: {
    exec: async ({ context }) => {
      await context.spawnPrincess('development');
    },
    cases: [
      { domain: 'development' },
      { domain: 'infrastructure' },
      { domain: 'security' }
    ]
  },
  MONITOR_PROGRESS: {
    exec: async ({ context }) => {
      await context.monitorProgress();
    }
  },
  HANDLE_FAILURE: {
    exec: async ({ context }) => {
      await context.handleFailure(new Error('Test failure'));
    }
  },
  SHUTDOWN: {
    exec: async ({ context }) => {
      await context.shutdown();
    }
  }
});

describe('Queen FSM - Model-Based Tests', () => {
  const testPlans = queenModel.getSimplePathPlans();

  testPlans.forEach((plan) => {
    describe(plan.description, () => {
      plan.paths.forEach((path) => {
        it(path.description, async () => {
          await path.test({
            queenId: 'test-queen',
            activePrincesses: [],
            workflows: []
          });
        });
      });
    });
  });

  it('should have full coverage', () => {
    return queenModel.testCoverage();
  });
});
```

**TransitionHub Testing**:
```typescript
// tests/fsm/transition-hub/integration.test.ts
describe('TransitionHub - Centralized Transitions', () => {
  let hub: TransitionHub;

  beforeEach(() => {
    hub = new TransitionHub();
  });

  it('should route events to correct FSMs', async () => {
    const queenFSM = new QueenFSM({ hub });
    const princessFSM = new PrincessFSM({ hub });

    // Register FSMs with hub
    hub.register('queen', queenFSM);
    hub.register('princess-dev', princessFSM);

    // Emit event
    await hub.emit('queen', QueenEvent.SPAWN_PRINCESS, {
      domain: 'development',
      princessId: 'princess-dev'
    });

    // Verify cascade
    expect(queenFSM.getCurrentState()).toBe(QueenState.COORDINATING);
    expect(princessFSM.getCurrentState()).toBe(PrincessState.IDLE);

    // Princess receives order
    await hub.emit('princess-dev', PrincessEvent.RECEIVE_ORDER, {
      task: 'implement-feature'
    });

    expect(princessFSM.getCurrentState()).toBe(PrincessState.PLANNING);
  });

  it('should enforce transition guards globally', async () => {
    const queenFSM = new QueenFSM({ hub });
    hub.register('queen', queenFSM);

    // Add global guard: max 10 princesses
    hub.addGlobalGuard('SPAWN_PRINCESS', (event, context) => {
      return context.activePrincesses.length < 10;
    });

    // Spawn 10 princesses
    for (let i = 0; i < 10; i++) {
      await hub.emit('queen', QueenEvent.SPAWN_PRINCESS, {
        domain: 'test',
        princessId: `princess-${i}`
      });
    }

    // 11th should be blocked by guard
    await expect(
      hub.emit('queen', QueenEvent.SPAWN_PRINCESS, {
        domain: 'test',
        princessId: 'princess-11'
      })
    ).rejects.toThrow('Guard failed');
  });
});
```

### 6.2 Testing 22 Agents

**Agent Test Matrix**:
```typescript
// tests/agents/agent-test-matrix.ts
const AGENT_TEST_MATRIX = [
  // Research Agents (Gemini 2.5 Pro)
  {
    agentId: 'researcher',
    model: 'gemini-2.5-pro',
    testCases: [
      {
        input: 'Research FSM testing patterns',
        expectedOutput: {
          minReferences: 5,
          containsKeywords: ['XState', 'model-based'],
          factualityScore: 0.92
        }
      }
    ]
  },
  // Development Agents (GPT-5 Codex)
  {
    agentId: 'coder',
    model: 'gpt-5-codex',
    testCases: [
      {
        input: 'Implement auth FSM',
        expectedOutput: {
          compilationSuccess: true,
          testPassRate: 0.90,
          codeCoverage: 0.80
        }
      }
    ]
  },
  // Quality Agents (Claude Opus 4.1)
  {
    agentId: 'reviewer',
    model: 'claude-opus-4.1',
    testCases: [
      {
        input: 'Review code for security issues',
        expectedOutput: {
          bugDetectionRate: 0.95,
          falsePositiveRate: 0.05,
          securityScore: 0.95
        }
      }
    ]
  }
  // ... 19 more agents
];

describe('Agent Test Matrix', () => {
  AGENT_TEST_MATRIX.forEach((agentConfig) => {
    describe(`Agent: ${agentConfig.agentId}`, () => {
      let agent: Agent;

      beforeEach(async () => {
        agent = await spawnAgent(agentConfig.agentId, {
          model: agentConfig.model
        });
      });

      agentConfig.testCases.forEach((testCase, index) => {
        it(`should handle test case ${index + 1}`, async () => {
          const result = await agent.execute(testCase.input);

          // Validate output
          for (const [key, expectedValue] of Object.entries(testCase.expectedOutput)) {
            if (typeof expectedValue === 'number') {
              expect(result[key]).toBeGreaterThanOrEqual(expectedValue);
            } else if (typeof expectedValue === 'boolean') {
              expect(result[key]).toBe(expectedValue);
            } else if (Array.isArray(expectedValue)) {
              expectedValue.forEach((keyword) => {
                expect(result.content).toContain(keyword);
              });
            }
          }
        });
      });
    });
  });
});
```

### 6.3 Testing 3-Loop System

**Loop 1: Planning Tests**:
```typescript
describe('Loop 1: Planning', () => {
  it('should generate validated plan with risk mitigation', async () => {
    const loop1 = new Loop1Orchestrator({
      agents: {
        researcher: 'gemini-2.5-pro',
        specification: 'gemini-2.5-pro'
      }
    });

    const result = await loop1.execute({
      feature: 'payment-processing',
      requirements: {
        security: 'PCI-DSS compliant',
        performance: '<100ms latency',
        scalability: '10k TPS'
      }
    });

    expect(result.spec).toBeDefined();
    expect(result.plan).toBeDefined();
    expect(result.premortem).toBeDefined();

    expect(result.quality.specCompleteness).toBeGreaterThanOrEqual(0.90);
    expect(result.quality.riskMitigation).toBeGreaterThanOrEqual(0.80);
    expect(result.artifacts).toContainFile('SPEC.md');
    expect(result.artifacts).toContainFile('PLAN.json');
    expect(result.artifacts).toContainFile('PREMORTEM.md');
  });
});
```

**Loop 2: Development Tests**:
```typescript
describe('Loop 2: Development', () => {
  it('should implement feature with theater detection', async () => {
    const loop2 = new Loop2Orchestrator({
      agents: {
        coder: 5,
        tester: 3,
        reviewer: 2
      }
    });

    const result = await loop2.execute({
      plan: await loadPlan('payment-processing-plan.json'),
      parallelism: 10
    });

    expect(result.quality.testCoverage).toBeGreaterThanOrEqual(0.80);
    expect(result.quality.theaterScore).toBeLessThan(60);
    expect(result.quality.compilationSuccess).toBe(true);

    expect(result.artifacts).toContainFile('src/payment/PaymentFSM.ts');
    expect(result.artifacts).toContainFile('tests/payment/PaymentFSM.test.ts');
  });
});
```

**Loop 3: Quality Tests**:
```typescript
describe('Loop 3: Quality', () => {
  it('should converge to zero critical issues', async () => {
    const loop3 = new Loop3Orchestrator({
      analyzers: ['nasa-pot10', 'connascence', 'security', 'theater'],
      maxIterations: 10
    });

    const result = await loop3.execute({
      codebase: './src',
      convergenceCriteria: {
        qualityImprovement: 0.05,
        maxIterations: 10
      }
    });

    expect(result.converged).toBe(true);
    expect(result.quality.criticalIssues).toBe(0);
    expect(result.quality.nasaCompliance).toBeGreaterThanOrEqual(0.92);
    expect(result.quality.testPassRate).toBe(1.0);
    expect(result.iterationsRequired).toBeLessThanOrEqual(10);
  });
});
```

---

## Part 7: Conclusion and Next Steps

### 7.1 Key Takeaways

1. **FSM Testing**: Use XState with model-based test generation for 100% coverage
2. **Multi-Agent Testing**: Leverage Microsoft Agent Framework and Google ADK for observability
3. **E2E Testing**: Implement agentic testing with Octomind for autonomous test maintenance
4. **Performance**: Use k6 for load testing and Lighthouse for performance metrics
5. **Sandbox**: Integrate gVisor for secure test isolation

### 7.2 Implementation Roadmap

**Phase 1: Foundation (Weeks 1-2)**
- [ ] Set up XState for FSM testing
- [ ] Create FSM test models for 5 core FSMs
- [ ] Establish unit test infrastructure with Jest
- [ ] Configure coverage thresholds (FSM: 100%, overall: 80%)

**Phase 2: Multi-Agent Testing (Weeks 3-4)**
- [ ] Integrate Microsoft Agent Framework for observability
- [ ] Create agent test matrix for 22 agents
- [ ] Implement coordination tests for Queen-Princess-Drone
- [ ] Set up performance metrics tracking

**Phase 3: E2E Testing (Weeks 5-6)**
- [ ] Integrate Octomind for agentic E2E tests
- [ ] Create 3-loop workflow tests
- [ ] Implement error recovery and convergence tests
- [ ] Set up gVisor sandbox for secure testing

**Phase 4: Performance Benchmarking (Week 7)**
- [ ] Set up Grafana k6 for load testing
- [ ] Configure Lighthouse for performance audits
- [ ] Create performance benchmarks dashboard
- [ ] Establish performance regression detection

**Phase 5: CI/CD Integration (Week 8)**
- [ ] Configure GitHub Actions workflows
- [ ] Integrate quality gates with tests
- [ ] Set up automated performance testing
- [ ] Create test reporting dashboard

### 7.3 Success Metrics

**Coverage Targets**:
- FSM Coverage: 100%
- Agent Coverage: >=85%
- Integration Coverage: >=90%
- E2E Coverage: >=80%
- Overall Code Coverage: >=80%

**Performance Targets**:
- Agent Spawn Time: <5s for 22 agents
- FSM Transition Latency: <10ms (p95)
- Loop 1 Duration: <60s (p95)
- Loop 2 Duration: <300s (p95)
- Loop 3 Duration: <120s (p95)

**Quality Targets**:
- Unit Test Pass Rate: 100%
- Integration Test Pass Rate: >=95%
- E2E Test Pass Rate: >=90%
- Performance Score: >=80/100
- Zero Critical Issues

### 7.4 Risks and Mitigations

**Risk 1: FSM Test Complexity**
- Mitigation: Use XState model-based testing for automatic test generation
- Mitigation: Create reusable test fixtures for common FSM scenarios

**Risk 2: Multi-Agent Test Flakiness**
- Mitigation: Implement retries with exponential backoff
- Mitigation: Use deterministic test data and mocks
- Mitigation: Isolate tests with fresh agent spawns

**Risk 3: E2E Test Maintenance**
- Mitigation: Use Octomind for autonomous test maintenance
- Mitigation: Keep tests focused on critical user flows
- Mitigation: Regular test health monitoring

**Risk 4: Performance Test Consistency**
- Mitigation: Use dedicated CI runners for performance tests
- Mitigation: Establish baseline metrics before changes
- Mitigation: Run performance tests in isolation

### 7.5 References

1. XState Documentation: https://xstate.js.org/docs/
2. Microsoft Agent Framework: https://azure.microsoft.com/en-us/blog/introducing-microsoft-agent-framework/
3. Google ADK: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/
4. Octomind: https://octomind.dev/
5. Grafana k6: https://k6.io/docs/
6. Google Lighthouse: https://developer.chrome.com/docs/lighthouse/
7. gVisor: https://gvisor.dev/docs/
8. MAST Taxonomy: Multi-Agent System Failure research (2025)
9. State Transition Testing: https://www.tmap.net/wiki/state-transition-testing/
10. Agentic AI Testing: https://medium.com/transforming-testing-with-generative-ai/

---

<!-- AGENT FOOTER BEGIN: DO NOT EDIT ABOVE THIS LINE -->
## Version & Run Log

| Version | Timestamp | Agent/Model | Change Summary | Artifacts | Status | Notes | Cost | Hash |
|--------:|-----------|-------------|----------------|-----------|--------|-------|------|------|
| 1.0.0   | 2025-10-08T10:30:00-04:00 | research-agent@claude-sonnet-4 | Comprehensive testing strategies research for Gap 9 | testing-strategies-research-v1.md | OK | Research complete with 10 web searches, FSM examples, multi-agent patterns, E2E strategies, performance benchmarking | 0.00 | a7f3c9d |

### Receipt
- status: OK
- reason: Research complete for Gap 9 - Testing Strategies
- run_id: research-gap-9-testing-v1
- inputs: ["RESEARCH-GAPS-v1.md", "web search results", "existing FSM tests", "QueenFSMTypes.ts"]
- tools_used: ["WebSearch", "Read", "Glob", "Write"]
- versions: {"model":"claude-sonnet-4","research-iteration":"1"}
<!-- AGENT FOOTER END: DO NOT EDIT BELOW THIS LINE -->
