# SPEK Platform v2 - Implementation Plan v7 DRAFT

**Version**: 7.0 DRAFT
**Date**: 2025-10-08
**Status**: Draft - Atlantis UI Integration Plan
**Project**: C:\Users\17175\Desktop\spek-v2-rebuild

**Changes from v6**:
- ✅ Atlantis UI (Next.js 14 + Three.js 3D visualizations)
- ✅ 3-Loop System (Loop 1: Research, Loop 2: Execution, Loop 3: Quality)
- ✅ Princess Hive delegation model (multi-layer agent coordination)
- ✅ 3-Stage Audit Pipeline (Theater → Production → Quality)
- ✅ Project Vectorization Service (embeddings + caching)
- ✅ UI Validation System (Playwright screenshot comparison)
- ✅ Documentation Cleanup Automation (markdown organization)
- ✅ Extended timeline (24 weeks vs 12 weeks Phase 1)
- ✅ Enhanced GitHub integration (Projects, Issues, CI/CD generation)
- ✅ Real-time WebSocket updates (agent activity streaming)

---

## Executive Summary

### Strategic Vision: Autonomous AI Platform with Visual Interface

This plan delivers a **production-ready AI agent platform with visual UI** enabling autonomous project creation, execution, and quality assurance through 3 distinct refinement loops.

**Atlantis UI** provides elegant 3D visualizations of:
- Loop 1: Research and pre-mortem failure analysis (orbital ring visualization)
- Loop 2: Phase-based execution with Princess Hive delegation (village/hive visualization)
- Loop 3: Final quality scans and GitHub integration (concentric circles visualization)

**Timeline**: 24 weeks (single continuous phase)
**Budget**: $150/month operational cost (Gemini + Claude + Pinecone + Redis + Docker)
**Team**: 10 developers (4 parallel teams)
**Target**: 70-75% SWE-Bench solve rate, <5% failure rate in Loop 1

### Core Innovation: 3-Loop Quality System

**Loop 1 - Research & Pre-mortem** (Weeks 7-8):
- GitHub code search + academic paper research
- Multi-agent pre-mortem analysis (failure prediction)
- Iterative refinement until failure rate <5%
- Visual: 3D orbital ring with failure rate gauge

**Loop 2 - Execution** (Weeks 9-10):
- MECE phase division (Mutually Exclusive, Collectively Exhaustive)
- Princess Hive delegation (Monarch → Princesses → Drones)
- 3-Stage audit per task (Theater → Production → Quality)
- Visual: Execution village with animated task flows

**Loop 3 - Finalization** (Weeks 11-12):
- Full project quality scan (100% pass required)
- GitHub repo creation + CI/CD setup
- Documentation cleanup + UI screenshots
- Export to GitHub or local folder
- Visual: Concentric circles expanding outward

### Critical Success Factors

**Technical Gates** (ALL required for production):
1. ✅ Zero P0/P1 risks remaining
2. ✅ System performance >=0.68 (68% SWE-Bench solve rate)
3. ✅ Monthly cost <=$150
4. ✅ All 22 agents functional
5. ✅ Atlantis UI 9 pages deployed
6. ✅ 3D visualizations operational (Three.js)
7. ✅ Real-time WebSocket updates (<100ms latency)
8. ✅ Project vectorization <60s for 10k LOC
9. ✅ Sandbox validation <20s per task
10. ✅ >=92% NASA Rule 10 compliance
11. ✅ Analyzer self-analysis <10% theater score
12. ✅ UI screenshot validation system functional
13. ✅ Documentation cleanup automation working

**Quality Gates**:
- Loop 1: Failure rate <5% within 10 iterations
- Loop 2: Audit pass rate >95% (first attempt)
- Loop 3: Final quality score 100%
- UI: Visual diff approval rate >90%

---

## Timeline Overview

```
WEEKS 1-2: Analyzer Refactoring (COMPLETE)
├─ God object splitting (70 → <10 files)
├─ Import management simplification
├─ Test infrastructure buildout (30% → 80% coverage)
└─ API consolidation + documentation

WEEKS 3-4: Core System + Atlantis Backend
├─ AgentContract, EnhancedLightweightProtocol, GovernanceDecisionEngine
├─ tRPC API routes (9 endpoints)
├─ WebSocket server (Socket.io)
├─ Project vectorization service (Pinecone)
├─ Task queue (BullMQ)
└─ Redis caching layer

WEEKS 5-6: Atlantis UI Foundation
├─ Next.js 14 setup (App Router)
├─ Page routing (9 pages)
├─ shadcn/ui component library
├─ Basic 2D layouts (before 3D)
├─ Monarch chat interface
└─ Project selector component

WEEKS 7-8: Loop 1 Implementation
├─ Research agent (GitHub + academic search)
├─ Pre-mortem multi-agent system (failure analysis)
├─ Failure rate calculation engine
├─ Loop 1 visualizer (2D first, 3D later)
├─ Agent thoughts streaming (WebSocket)
└─ Pause/inject thoughts feature

WEEKS 9-10: Loop 2 Execution System
├─ MECE phase division algorithm
├─ Princess Hive delegation (Monarch → Princess → Drone)
├─ Task execution pipeline
├─ 3-Stage audit system (Theater → Production → Quality)
├─ GitHub Projects integration (task tracking)
└─ Execution village visualizer (2D first)

WEEKS 11-12: Loop 3 Quality System
├─ Full project audit orchestration
├─ GitHub repo creation wizard
├─ CI/CD pipeline generation (GitHub Actions)
├─ Documentation cleanup automation
├─ Export system (GitHub vs folder)
└─ Loop 3 visualizer (2D first)

WEEKS 13-14: 3D Visualizations
├─ Three.js + React Three Fiber integration
├─ Loop 1: Orbital ring (failure rate center, research satellites)
├─ Loop 2: Execution village (buildings = princesses, bees = drones)
├─ Loop 3: Concentric circles (scan → GitHub → docs → export)
├─ Performance optimization (LOD rendering)
└─ Camera controls + interaction

WEEKS 15-16: UI Validation + Polish
├─ Playwright screenshot system
├─ Visual diff comparison engine
├─ User approval workflow
├─ UI polish + animations (Framer Motion)
├─ Responsive design (desktop, tablet, mobile)
└─ Performance optimization (<3s page load)

WEEKS 17-18: 22 Agents Implementation
├─ Core agents (5): queen, coder, researcher, tester, reviewer
├─ Swarm coordinators (4): princess-dev, princess-quality, princess-coordination, queen
├─ Specialized agents (13): architect, pseudocode-writer, spec-writer, etc.
├─ Agent2Agent protocol integration
└─ Context DNA cross-agent memory

WEEKS 19-20: Context DNA + Storage
├─ SQLite Context DNA (30-day retention)
├─ Redis caching (project indexing)
├─ Pinecone vectors (project embeddings)
├─ Cross-agent memory system
├─ Artifact reference storage
└─ Search optimization (<200ms)

WEEKS 21-22: DSPy Optimization
├─ Selective optimization (8 critical agents)
├─ Performance tuning (0.68-0.73 target)
├─ Cost optimization (<$150/month)
├─ Prompt engineering refinement
└─ Evaluation benchmark creation

WEEKS 23-24: Production Validation
├─ End-to-end testing (full 3-loop workflow)
├─ Performance benchmarks (10 real projects)
├─ Security audit (Bandit + Semgrep)
├─ Load testing (concurrent users)
├─ Documentation finalization
└─ GO/NO-GO decision
```

---

## Resource Allocation

### Team Structure

**Team A - Backend & Core** (3 developers):
- Core system implementation (Weeks 3-4)
- Agent implementation (Weeks 17-18)
- Context DNA + storage (Weeks 19-20)
- Lead: Senior Backend Engineer

**Team B - Frontend & UI** (3 developers):
- Atlantis UI foundation (Weeks 5-6)
- 3D visualizations (Weeks 13-14)
- UI validation + polish (Weeks 15-16)
- Lead: Senior Frontend Engineer

**Team C - Loop Systems** (2 developers):
- Loop 1 implementation (Weeks 7-8)
- Loop 2 implementation (Weeks 9-10)
- Loop 3 implementation (Weeks 11-12)
- Lead: Full Stack Engineer

**Team D - Quality & DevOps** (2 developers):
- Audit system implementation (Weeks 9-10)
- DSPy optimization (Weeks 21-22)
- Production validation (Weeks 23-24)
- Lead: DevOps/QA Engineer

### Budget Breakdown

**Monthly Operational Cost**: $150/month
- Gemini Flash 2.0: $15/month (primary inference)
- Claude Sonnet 4.5: $60/month (complex tasks, cached)
- Pinecone: $25/month (100k vectors, project embeddings)
- Redis Cloud: $10/month (2GB cache, project indexing)
- Docker Hub: $5/month (sandbox images)
- GitHub: $0 (free tier, 500MB storage)
- Vercel: $20/month (Next.js hosting, serverless functions)
- Misc: $15/month (monitoring, logs)

**Development Cost** (One-time):
- 10 developers × 24 weeks × 40 hours/week = 9,600 hours
- Assumed handled by client's existing team budget

**Total First Year**: $150 × 12 = $1,800 operational cost

---

## WEEKS 3-4: Core System + Atlantis Backend

### Overview

**Goal**: Implement core SPEK platform components + Atlantis backend API layer.

**Team Assignment**:
- **Team A** (3 devs): AgentContract, Protocol, GovernanceEngine
- **Team B** (3 devs): tRPC API, WebSocket server
- **Team C** (2 devs): Project vectorization, task queue
- **Team D** (2 devs): Redis caching, sandbox setup

---

### Week 3 Objectives

**MONDAY - Core Interfaces**:
- [ ] **Team A** - Implement `AgentContract` interface (8 hours)
  - File: `src/agents/base/AgentContract.ts`
  - Methods: `validate()`, `execute()`, `getMetadata()`
  - Type definitions for `Task`, `Result`, `AgentMetadata`
  - Unit tests: 20 tests covering all contract methods
  - Documentation: JSDoc comments + README

- [ ] **Team A** - Implement `EnhancedLightweightProtocol` (8 hours)
  - File: `src/protocols/EnhancedLightweightProtocol.ts`
  - Features: Direct task assignment, health checks, task tracking
  - Target: <100ms coordination latency
  - Unit tests: 15 tests covering all protocol features
  - Performance benchmark: Measure latency under load

- [ ] **Team B** - Setup Next.js 14 project structure (8 hours)
  - Initialize Next.js with App Router
  - Configure TypeScript (strict mode)
  - Setup tRPC server + client
  - Install dependencies: zod, react-query, socket.io
  - Create `.env.example` with all required variables

- [ ] **Team C** - Design project vectorization architecture (8 hours)
  - Document: `docs/vectorization-architecture.md`
  - AST parsing strategy (TypeScript, Python, JavaScript)
  - Embedding model selection (text-embedding-3-small)
  - Chunking strategy (file-level vs function-level)
  - Dependency graph generation (NetworkX)
  - Caching strategy (Redis keys, TTL)

**TUESDAY - Implementation Day 1**:
- [ ] **Team A** - Implement `GovernanceDecisionEngine` (8 hours)
  - File: `src/governance/GovernanceDecisionEngine.ts`
  - Parse Constitution.md + SPEK CLAUDE.md
  - Decision resolution algorithm (strategic vs tactical)
  - FSM decision matrix validator (>=3 criteria check)
  - Unit tests: 25 tests covering all decision paths
  - Integration test: Resolve sample conflicts

- [ ] **Team B** - Create tRPC API routes (8 hours)
  - Files:
    - `src/server/api/routers/monarch.ts` (chat, clarify)
    - `src/server/api/routers/project.ts` (index, graph, select)
    - `src/server/api/routers/loop1.ts` (research, premortem, remediate)
  - Input validation: Zod schemas for all endpoints
  - Error handling: Custom error types
  - Rate limiting: 100 req/min per user
  - Unit tests: 30 tests covering all routes

- [ ] **Team C** - Implement AST parser (8 hours)
  - File: `src/services/vectorization/ASTParser.ts`
  - Support: TypeScript, Python, JavaScript
  - Extract: Functions, classes, imports, exports
  - Generate: Dependency graph (directed acyclic)
  - Unit tests: 20 tests with sample code files
  - Performance: <5s for 10k LOC file

- [ ] **Team D** - Setup Redis caching layer (8 hours)
  - File: `src/services/cache/RedisCache.ts`
  - Connection management (connection pooling)
  - Cache strategies: LRU, TTL-based expiration
  - Key patterns: `project:{id}:vectors`, `project:{id}:graph`
  - Invalidation: On project update
  - Unit tests: 15 tests covering all cache operations
  - Integration test: Redis Cloud connection

**WEDNESDAY - Implementation Day 2**:
- [ ] **Team A** - Create base agent implementations (8 hours)
  - Files:
    - `src/agents/core/QueenAgent.ts`
    - `src/agents/core/CoderAgent.ts`
    - `src/agents/core/ResearcherAgent.ts`
  - Implement `AgentContract` interface
  - Basic execute logic (placeholders for now)
  - Metadata definitions (capabilities, cost, latency)
  - Unit tests: 10 tests per agent (30 total)

- [ ] **Team B** - Implement WebSocket server (8 hours)
  - File: `src/server/websocket/SocketServer.ts`
  - Setup Socket.io with Redis adapter (horizontal scaling)
  - Events: `agent:activity`, `task:update`, `loop:progress`
  - Authentication: JWT token validation
  - Room management: Per-project isolation
  - Unit tests: 20 tests covering all events
  - Load test: 100 concurrent connections

- [ ] **Team C** - Implement embedding service (8 hours)
  - File: `src/services/vectorization/EmbeddingService.ts`
  - OpenAI `text-embedding-3-small` integration
  - Batch processing (1000 chunks at a time)
  - Pinecone upsert (chunked uploads)
  - Retry logic (exponential backoff)
  - Unit tests: 15 tests with mock embeddings
  - Integration test: Pinecone connection

- [ ] **Team D** - Setup BullMQ task queue (8 hours)
  - File: `src/services/queue/TaskQueue.ts`
  - Queues: `vectorization`, `analysis`, `execution`
  - Job priorities: High, Medium, Low
  - Retry strategies: 3 attempts with backoff
  - Job progress tracking (WebSocket updates)
  - Unit tests: 20 tests covering all queue operations
  - Integration test: Redis queue connection

**THURSDAY - Integration Day**:
- [ ] **Team A + B** - Integrate agents with tRPC (8 hours)
  - Connect `QueenAgent` to `/api/monarch/chat`
  - Connect `ResearcherAgent` to `/api/loop1/research`
  - Test end-to-end: User request → Agent execution → Response
  - Error handling: Agent failures, timeouts
  - Integration tests: 15 tests covering all flows

- [ ] **Team C + D** - Integrate vectorization pipeline (8 hours)
  - Flow: File upload → AST parse → Embed → Cache → Pinecone
  - Job queue: Submit vectorization job → Process → Update status
  - WebSocket: Real-time progress updates
  - Error handling: Parse failures, embedding errors
  - Integration tests: 10 tests with sample projects

- [ ] **All Teams** - Code review + refactoring (8 hours)
  - Review all PRs from Week 3
  - Refactor duplications
  - Add missing tests (target: 80% coverage)
  - Update documentation (API docs, architecture diagrams)
  - Fix linting errors (ESLint strict mode)

**FRIDAY - Testing + Documentation**:
- [ ] **All Teams** - Comprehensive testing (6 hours)
  - Unit tests: 200+ tests total
  - Integration tests: 35+ tests total
  - End-to-end tests: 5 critical flows
  - Coverage report: >=80% target
  - Performance benchmarks: Document latencies

- [ ] **Team B** - API documentation (2 hours)
  - Generate tRPC API docs (auto-generated from schemas)
  - Write usage examples for each endpoint
  - Document WebSocket events
  - Create Postman collection

---

### Week 4 Objectives

**MONDAY - Advanced Features**:
- [ ] **Team A** - Implement platform abstraction layer (8 hours)
  - File: `src/platforms/PlatformAdapter.ts`
  - Support: Gemini Flash 2.0, Claude Sonnet 4.5
  - Unified interface: `generateText()`, `generateEmbedding()`
  - Cost tracking: Per-request token counts
  - Failover: Primary → fallback platform
  - Unit tests: 25 tests covering all platforms
  - Integration tests: Real API calls (small inputs)

- [ ] **Team B** - Create project graph visualizer API (8 hours)
  - File: `src/server/api/routers/graph.ts`
  - Endpoint: `/api/project/graph` (returns D3.js compatible JSON)
  - Graph data: Nodes (files), edges (dependencies), clusters (modules)
  - Layout algorithm: Force-directed (D3.js)
  - Filtering: By file type, dependency depth
  - Unit tests: 15 tests with sample graphs

- [ ] **Team C** - Implement incremental indexing (8 hours)
  - File: `src/services/vectorization/IncrementalIndexer.ts`
  - Detect changes: Git diff, file timestamps
  - Index only changed files (avoid re-indexing entire project)
  - Cache invalidation: Selective (changed files only)
  - Performance: 10x faster for incremental updates
  - Unit tests: 20 tests with mock projects

- [ ] **Team D** - Setup Docker sandbox (8 hours)
  - File: `src/services/sandbox/DockerSandbox.ts`
  - Base images: Node.js, Python, Multi-language
  - Resource limits: 1GB RAM, 1 CPU, 30s timeout
  - Network isolation: No external network access
  - File system: Ephemeral, deleted after run
  - Unit tests: 10 tests with sample code execution
  - Security test: Attempt malicious code (should fail)

**TUESDAY - Quality Gates**:
- [ ] **Team A** - Implement NASA Rule 10 validator (8 hours)
  - File: `src/quality/NASARuleValidator.ts`
  - Rules: Function length (<=60 LOC), assertions (>=2), etc.
  - Integration with analyzer (call existing analyzer)
  - Automated refactoring suggestions
  - Unit tests: 15 tests per rule (90 total)

- [ ] **Team B** - Create theater detection API (8 hours)
  - File: `src/server/api/routers/theater.ts`
  - Endpoint: `/api/audit/theater` (scan code for mock patterns)
  - Integration with analyzer (theater detection)
  - Scoring: 0-100 (0 = no theater, 100 = all theater)
  - Threshold: <10 score required to pass
  - Unit tests: 20 tests with mock code samples

- [ ] **Team C** - Implement production sandbox runner (8 hours)
  - File: `src/services/sandbox/SandboxRunner.ts`
  - Execute tests in Docker container
  - Capture stdout, stderr, exit code
  - Timeout handling (30s max)
  - Retry logic (3 attempts on timeout)
  - Unit tests: 15 tests with sample test suites

- [ ] **Team D** - Create quality audit orchestrator (8 hours)
  - File: `src/services/audit/AuditOrchestrator.ts`
  - 3-Stage pipeline: Theater → Production → Quality
  - Sequential execution (fail-fast on errors)
  - Retry logic (return to drone on failure)
  - WebSocket updates (real-time progress)
  - Unit tests: 20 tests covering all stages

**WEDNESDAY - GitHub Integration**:
- [ ] **Team A + B** - Implement GitHub API client (8 hours)
  - File: `src/services/github/GitHubClient.ts`
  - Octokit integration (REST + GraphQL)
  - Features: Create repo, create project, create issue, push code
  - Authentication: GitHub App (OAuth flow)
  - Rate limiting: Respect GitHub limits (5000 req/hour)
  - Unit tests: 25 tests with mock GitHub responses
  - Integration test: Create test repo (delete after)

- [ ] **Team C + D** - Implement GitHub Projects integration (8 hours)
  - File: `src/services/github/ProjectsIntegration.ts`
  - Create project board (columns: To Do, In Progress, Done)
  - Sync tasks (SPEK tasks → GitHub issues)
  - Update status (WebSocket → GitHub Projects)
  - Bottleneck visualization (blocked tasks highlighted)
  - Unit tests: 15 tests with mock project data

**THURSDAY - Performance Optimization**:
- [ ] **Team A** - Optimize agent coordination latency (8 hours)
  - Profile: Measure current latency (baseline)
  - Optimize: Remove bottlenecks (<100ms target)
  - Caching: Memoize agent metadata lookups
  - Parallel execution: Run independent agents concurrently
  - Benchmark: 100 requests/sec sustained load
  - Documentation: Performance report

- [ ] **Team B** - Optimize tRPC response times (8 hours)
  - Profile: Measure current response times (baseline)
  - Optimize: Database queries, caching, serialization
  - Compression: Enable gzip for large responses
  - CDN: Cache static assets (Vercel CDN)
  - Benchmark: <200ms p95 response time
  - Documentation: Performance report

- [ ] **Team C** - Optimize vectorization speed (8 hours)
  - Profile: Measure current vectorization time (baseline)
  - Optimize: Parallel AST parsing, batch embeddings
  - Target: <60s for 10k LOC project
  - Incremental indexing: <10s for changed files
  - Benchmark: 10 real projects
  - Documentation: Performance report

- [ ] **Team D** - Optimize sandbox startup time (8 hours)
  - Profile: Measure current startup time (baseline)
  - Optimize: Docker layer caching, pre-built images
  - Target: <20s validation time (v4 goal)
  - Parallel execution: Run multiple sandboxes concurrently
  - Benchmark: 50 sandboxes in parallel
  - Documentation: Performance report

**FRIDAY - Week 3-4 Integration Testing**:
- [ ] **All Teams** - End-to-end testing (6 hours)
  - Test flow: User chat → Project indexing → Graph visualization
  - Test flow: Agent coordination → Task execution → Results
  - Test flow: Audit pipeline → GitHub sync → Export
  - Performance tests: Load testing (100 concurrent users)
  - Security tests: Authentication, authorization, injection attacks
  - Coverage report: >=80% maintained

- [ ] **All Teams** - Documentation + review (2 hours)
  - Update architecture diagrams (core system)
  - Update API documentation (all endpoints)
  - Code review: Refactor god objects (if any)
  - Prepare demo: Core system walkthrough

### Week 3-4 Deliverables

**Code**:
- ✅ AgentContract interface (100% implemented)
- ✅ EnhancedLightweightProtocol (100% implemented)
- ✅ GovernanceDecisionEngine (100% implemented)
- ✅ tRPC API (9 routers, 30+ endpoints)
- ✅ WebSocket server (3 events, Redis adapter)
- ✅ Project vectorization service (AST + embeddings + Pinecone)
- ✅ Task queue (BullMQ, 3 queues)
- ✅ Redis caching layer (LRU + TTL strategies)
- ✅ Docker sandbox (Node.js + Python images)
- ✅ Platform abstraction (Gemini + Claude)
- ✅ GitHub integration (Octokit client)

**Tests**:
- ✅ 200+ unit tests
- ✅ 35+ integration tests
- ✅ 5+ end-to-end tests
- ✅ 80%+ code coverage

**Documentation**:
- ✅ API documentation (all endpoints)
- ✅ Architecture diagrams (core system)
- ✅ Performance benchmarks (latency, throughput)
- ✅ Security audit report

**Acceptance Criteria**:
- [ ] All agents implement AgentContract interface
- [ ] Agent coordination latency <100ms (p95)
- [ ] Project vectorization <60s for 10k LOC
- [ ] Sandbox validation <20s per task
- [ ] tRPC response time <200ms (p95)
- [ ] WebSocket latency <100ms (event delivery)
- [ ] All tests passing (0 failures)
- [ ] Code coverage >=80%
- [ ] Zero critical security vulnerabilities
- [ ] Documentation complete and accurate

---

## WEEKS 5-6: Atlantis UI Foundation

### Overview

**Goal**: Build Next.js 14 frontend with 9 pages, shadcn/ui components, basic 2D layouts (3D in Weeks 13-14).

**Team Assignment**:
- **Team B** (3 devs): Primary UI development
- **Team A** (1 dev): tRPC client integration
- **Team C** (1 dev): State management (Zustand)

---

### Week 5 Objectives

**MONDAY - Project Setup**:
- [ ] **Team B** - Initialize Next.js 14 UI project (8 hours)
  - Create new Next.js app with App Router
  - Configure TypeScript (strict mode)
  - Install dependencies:
    - shadcn/ui (component library)
    - Tailwind CSS (styling)
    - Framer Motion (animations)
    - Zustand (state management)
    - React Query (data fetching)
    - Socket.io-client (WebSocket)
  - Setup folder structure:
    ```
    src/app/                  (pages)
    src/components/           (reusable components)
    src/components/cards/     (card components)
    src/components/tabs/      (tab components)
    src/components/modals/    (modal components)
    src/lib/                  (utilities)
    src/hooks/                (custom hooks)
    src/stores/               (Zustand stores)
    ```
  - Configure Tailwind (custom theme, colors)
  - Setup ESLint + Prettier

**TUESDAY - Page Routing + Layouts**:
- [ ] **Team B** - Create 9 page routes (8 hours)
  - Files:
    - `src/app/page.tsx` - Home/Landing (Monarch chat)
    - `src/app/project/select/page.tsx` - Existing project
    - `src/app/project/new/page.tsx` - New project wizard
    - `src/app/loop1/page.tsx` - Research & pre-mortem
    - `src/app/loop2/page.tsx` - Execution village
    - `src/app/loop2/audit/page.tsx` - Audit detail view
    - `src/app/loop2/ui-review/page.tsx` - UI validation
    - `src/app/loop3/page.tsx` - Finalization
    - `src/app/dashboard/page.tsx` - Overall progress
  - Basic layouts (header, sidebar, main content)
  - Navigation menu (sidebar with icons)
  - Breadcrumbs (current page path)
  - Footer (version, links)

- [ ] **Team A** - Setup tRPC client (8 hours)
  - File: `src/lib/trpc.ts`
  - Configure tRPC client (HTTP + WebSocket links)
  - React Query integration
  - Type-safe hooks: `trpc.monarch.chat.useMutation()`
  - Error handling (toast notifications)
  - Loading states (skeleton components)
  - Unit tests: 10 tests with mock tRPC responses

**WEDNESDAY - shadcn/ui Components**:
- [ ] **Team B** - Install shadcn/ui components (8 hours)
  - Components needed:
    - Button, Input, Textarea (forms)
    - Card, Badge, Avatar (display)
    - Tabs, Accordion (layout)
    - Dialog, Sheet, Popover (overlays)
    - Progress, Spinner (loading)
    - Toast (notifications)
    - Table, Pagination (data)
  - Customize theme (colors, typography, spacing)
  - Create component storybook (document all components)
  - Unit tests: 15 tests (component rendering)

- [ ] **Team C** - Create Zustand stores (8 hours)
  - Files:
    - `src/stores/projectStore.ts` (project state)
    - `src/stores/loop1Store.ts` (Loop 1 state)
    - `src/stores/loop2Store.ts` (Loop 2 state)
    - `src/stores/loop3Store.ts` (Loop 3 state)
    - `src/stores/agentStore.ts` (agent activity)
  - State structure:
    ```typescript
    // projectStore.ts
    interface ProjectStore {
      currentProject: Project | null;
      setProject: (project: Project) => void;
      vectorizationProgress: number;
      setVectorizationProgress: (progress: number) => void;
    }
    ```
  - Persistence: LocalStorage for project state
  - Unit tests: 20 tests (state mutations)

**THURSDAY - Component Development**:
- [ ] **Team B** - Create reusable card components (8 hours)
  - Files:
    - `src/components/cards/AgentCard.tsx` (agent status, thoughts)
    - `src/components/cards/TaskCard.tsx` (task details, audit results)
    - `src/components/cards/PhaseCard.tsx` (phase summary, progress)
    - `src/components/cards/DocumentCard.tsx` (SPEC/PLAN preview)
    - `src/components/cards/ErrorCard.tsx` (error display with severity)
  - Props: Type-safe interfaces for each card
  - Variants: Different styles for different states
  - Responsive: Mobile, tablet, desktop layouts
  - Unit tests: 25 tests (rendering, props)

- [ ] **Team C** - Create custom hooks (8 hours)
  - Files:
    - `src/hooks/useWebSocket.ts` (WebSocket connection)
    - `src/hooks/useAgentActivity.ts` (real-time agent updates)
    - `src/hooks/useTaskStatus.ts` (task status updates)
    - `src/hooks/useLoopProgress.ts` (loop progress tracking)
  - WebSocket connection management (auto-reconnect)
  - Event handlers (typed events)
  - State synchronization (Zustand updates)
  - Unit tests: 15 tests (hook behavior)

**FRIDAY - Page Implementation (Part 1)**:
- [ ] **Team B** - Implement home page (Monarch chat) (8 hours)
  - File: `src/app/page.tsx`
  - Component: `<MonarchChat />` (chat interface)
  - Features:
    - Message list (scrollable, auto-scroll to bottom)
    - Input field (with send button)
    - Project selection buttons (New vs Existing)
    - Session persistence (LocalStorage)
  - API integration: `trpc.monarch.chat.useMutation()`
  - WebSocket: Real-time agent responses
  - Unit tests: 10 tests (rendering, user interactions)
  - E2E test: Full chat conversation flow

---

### Week 6 Objectives

**MONDAY - Page Implementation (Part 2)**:
- [ ] **Team B** - Implement project selector page (8 hours)
  - File: `src/app/project/select/page.tsx`
  - Component: `<ProjectSelector />` (file picker)
  - Features:
    - Folder browser (tree view)
    - Recent projects dropdown
    - File count indicator
    - Vectorization progress bar
  - API integration: `trpc.project.index.useMutation()`
  - WebSocket: Real-time vectorization progress
  - Component: `<ProjectGraph />` (2D graph, D3.js)
  - Unit tests: 15 tests
  - E2E test: Select project → Vectorize → View graph

**TUESDAY - Page Implementation (Part 3)**:
- [ ] **Team B** - Implement new project wizard (8 hours)
  - File: `src/app/project/new/page.tsx`
  - Component: `<ProjectWizard />` (multi-step form)
  - Steps:
    1. Project vision (textarea)
    2. Clarifying questions (Q&A interface)
    3. Technical preferences (dropdowns, either/or)
    4. Review SPEC/PLAN (document preview)
  - API integration: `trpc.monarch.clarify.useMutation()`
  - Progress indicator (step X of Y)
  - Back/Next navigation
  - Unit tests: 20 tests
  - E2E test: Complete wizard → Generate SPEC/PLAN

**WEDNESDAY - Page Implementation (Part 4)**:
- [ ] **Team B** - Implement Loop 1 page (8 hours)
  - File: `src/app/loop1/page.tsx`
  - Components:
    - `<Loop1Visualizer />` (2D loop animation, placeholder for 3D)
    - `<AgentThoughts />` (real-time log stream)
    - `<FailureRateGauge />` (percentage display, color-coded)
  - Features:
    - Iteration counter badge
    - Pause/inject thoughts button (opens modal)
    - Research artifacts list (GitHub repos, papers)
    - Pre-mortem reports (expandable cards)
  - API integration: `trpc.loop1.research.useMutation()`
  - WebSocket: Real-time agent activity
  - Unit tests: 15 tests
  - E2E test: Run Loop 1 → Reach <5% failure rate

**THURSDAY - Page Implementation (Part 5)**:
- [ ] **Team B** - Implement Loop 2 page (8 hours)
  - File: `src/app/loop2/page.tsx`
  - Components:
    - `<ExecutionVillage />` (2D village, placeholder for 3D)
    - `<PhaseColumn />` (MECE phases)
    - `<PrincessCard />` (princess + drone group)
    - `<TaskFlow />` (animated task delegation)
  - Features:
    - Phase tabs (switch between phases)
    - Task status indicators (pending/in-progress/complete)
    - Audit pipeline visualizer (3 stages)
    - Bottleneck warnings (red highlights)
  - API integration: `trpc.loop2.execute.useMutation()`
  - WebSocket: Task status updates
  - Unit tests: 20 tests
  - E2E test: Execute phase → Complete all tasks

**FRIDAY - Page Implementation (Part 6)**:
- [ ] **Team B** - Implement Loop 3 page (8 hours)
  - File: `src/app/loop3/page.tsx`
  - Components:
    - `<Loop3Finalizer />` (final scan visualizer, 2D)
    - `<RepoWizard />` (GitHub setup wizard)
    - `<DocumentationCleanup />` (doc organizer)
  - Features:
    - Final quality score (100% target)
    - GitHub repo creation form
    - CI/CD pipeline preview
    - Export options (GitHub vs folder download)
  - API integration: `trpc.loop3.scan.useMutation()`
  - WebSocket: Scan progress updates
  - Unit tests: 15 tests
  - E2E test: Complete Loop 3 → Export to GitHub

- [ ] **Team B** - Implement dashboard page (4 hours)
  - File: `src/app/dashboard/page.tsx`
  - Components:
    - `<ProgressOverview />` (high-level status)
    - `<PhaseTimeline />` (Gantt chart)
  - Features:
    - Current loop indicator
    - Overall progress percentage
    - Time estimates (completion ETA)
  - Unit tests: 10 tests

### Week 5-6 Deliverables

**Code**:
- ✅ 9 pages implemented (routing + basic layouts)
- ✅ 15+ reusable components (cards, tabs, modals)
- ✅ 5 Zustand stores (state management)
- ✅ 4 custom hooks (WebSocket, agent activity)
- ✅ tRPC client integration (type-safe API calls)
- ✅ shadcn/ui component library (customized theme)

**Tests**:
- ✅ 150+ unit tests (components, hooks, stores)
- ✅ 6 end-to-end tests (critical user flows)

**Documentation**:
- ✅ Component storybook (all components documented)
- ✅ API integration guide (tRPC usage)
- ✅ State management guide (Zustand patterns)

**Acceptance Criteria**:
- [ ] All 9 pages accessible (routing working)
- [ ] tRPC client connected to backend (API calls working)
- [ ] WebSocket real-time updates working
- [ ] State management functional (Zustand stores)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Page load time <3s (initial load)
- [ ] All tests passing (0 failures)
- [ ] Code coverage >=80%

---

## WEEKS 7-8: Loop 1 Implementation

### Overview

**Goal**: Implement Loop 1 research, pre-mortem, and failure rate calculation system.

**Team Assignment**:
- **Team C** (2 devs): Loop 1 backend logic
- **Team A** (1 dev): Research agent implementation
- **Team D** (1 dev): Pre-mortem multi-agent system

---

### Week 7-8 Objectives

**Research Agent**:
- [ ] GitHub code search integration (Octokit)
- [ ] Academic paper search (Semantic Scholar API)
- [ ] Artifact collection and storage
- [ ] Relevance scoring (embeddings similarity)

**Pre-mortem Multi-Agent System**:
- [ ] Failure prediction algorithm
- [ ] Multi-agent consensus (3+ agents analyze independently)
- [ ] Remediation suggestion generation
- [ ] SPEC/PLAN update automation

**Failure Rate Calculation**:
- [ ] Risk scoring per pre-mortem iteration
- [ ] Trajectory tracking (failure rate over iterations)
- [ ] <5% threshold detection
- [ ] Automatic loop completion

**Visualizer (2D)**:
- [ ] Loop iteration counter
- [ ] Failure rate gauge (real-time updates)
- [ ] Agent thoughts stream (scrolling log)
- [ ] Pause/inject thoughts modal

### Week 7-8 Deliverables

**Code**:
- ✅ Research agent (GitHub + academic search)
- ✅ Pre-mortem multi-agent system
- ✅ Failure rate calculation engine
- ✅ Loop 1 visualizer (2D, placeholder for 3D)
- ✅ Agent thoughts streaming (WebSocket)

**Tests**:
- ✅ 50+ unit tests (research, pre-mortem, failure calc)
- ✅ 3 integration tests (full Loop 1 workflow)

**Acceptance Criteria**:
- [ ] Research agent finds relevant GitHub repos
- [ ] Pre-mortem system identifies >=10 failure modes
- [ ] Failure rate calculation converges to <5%
- [ ] Loop 1 completes within 10 iterations (average)
- [ ] Visualizer displays real-time updates

---

## WEEKS 9-10: Loop 2 Execution System

### Overview

**Goal**: Implement MECE phase division, Princess Hive delegation, 3-stage audit pipeline.

**Team Assignment**:
- **Team C** (2 devs): Loop 2 backend logic
- **Team A** (1 dev): MECE phase division algorithm
- **Team D** (2 devs): 3-stage audit system

---

### Week 9-10 Objectives

**MECE Phase Division**:
- [ ] Algorithm: Analyze PLAN → Identify phases (Mutually Exclusive, Collectively Exhaustive)
- [ ] Dependency graph generation (bottleneck identification)
- [ ] Princess specialization matching (assign phases to princesses)
- [ ] Task breakdown (phases → tasks → subtasks)

**Princess Hive Delegation**:
- [ ] Monarch → Princess task assignment
- [ ] Princess → Drone task delegation
- [ ] Communication protocol (Agent2Agent with path validation)
- [ ] Context DNA translation integrity

**3-Stage Audit System**:
- [ ] **Stage 1: Theater Detection** (analyzer integration)
  - Scan for: mock code, TODOs, NotImplementedError
  - Pass criteria: Zero theater indicators
  - Action: If fail → return to drone with notes
- [ ] **Stage 2: Production Testing** (sandbox execution)
  - Run code in Docker container
  - Execute tests (all must pass)
  - Debug loop (run → debug → run until 100%)
  - Pass criteria: All tests pass
- [ ] **Stage 3: Quality Scan** (analyzer integration)
  - Scan for: connascence, god objects, NASA violations, duplications
  - Generate JSON error report
  - Send to specialist drones for refactor
  - Re-scan after refactor
  - Pass criteria: 100% quality score

**GitHub Projects Integration**:
- [ ] Create project board (To Do, In Progress, Done)
- [ ] Sync tasks (SPEK → GitHub issues)
- [ ] Update status (real-time via WebSocket)
- [ ] Bottleneck visualization (blocked tasks highlighted)

**Execution Village Visualizer (2D)**:
- [ ] Phase columns (visual separation)
- [ ] Princess cards (with drone counts)
- [ ] Task flow animation (arrows between cards)
- [ ] Audit pipeline progress (3 stages per task)

### Week 9-10 Deliverables

**Code**:
- ✅ MECE phase division algorithm
- ✅ Princess Hive delegation system
- ✅ 3-stage audit pipeline (Theater → Production → Quality)
- ✅ GitHub Projects integration
- ✅ Execution village visualizer (2D)

**Tests**:
- ✅ 60+ unit tests (phase division, delegation, audit)
- ✅ 5 integration tests (full Loop 2 workflow)

**Acceptance Criteria**:
- [ ] MECE phase division produces valid phases (no overlap)
- [ ] Princess Hive delegation assigns tasks correctly
- [ ] 3-stage audit pipeline catches all violations
- [ ] Audit pass rate >95% (first attempt)
- [ ] GitHub Projects sync works (real-time updates)
- [ ] Execution village displays all tasks correctly

---

## WEEKS 11-12: Loop 3 Quality System

### Overview

**Goal**: Implement full project audit, GitHub repo creation, CI/CD generation, documentation cleanup.

**Team Assignment**:
- **Team C** (2 devs): Loop 3 backend logic
- **Team A** (1 dev): GitHub repo creation wizard
- **Team D** (1 dev): Documentation cleanup automation

---

### Week 11-12 Objectives

**Full Project Audit**:
- [ ] Theater scan (entire project, 100% pass required)
- [ ] Production test (run all tests, 100% pass required)
- [ ] Quality scan (entire project, 100% pass required)
- [ ] Failure handling (if any stage fails, re-run Loop 2)

**GitHub Repo Creation Wizard**:
- [ ] Create new repo (public/private option)
- [ ] Initialize with README (auto-generated from SPEC)
- [ ] Install analyzer hooks (pre-commit, pre-push)
- [ ] Setup branch protection (main branch)
- [ ] Configure quality gates (require passing tests)

**CI/CD Pipeline Generation**:
- [ ] Generate GitHub Actions workflow (`.github/workflows/ci.yml`)
- [ ] Jobs: lint, test, build, deploy
- [ ] Triggers: push to main, pull requests
- [ ] Notifications: Slack, email (configurable)
- [ ] SARIF upload (Security tab integration)

**Documentation Cleanup**:
- [ ] List all markdown files (recursive scan)
- [ ] Organize by code module (create `docs/` subdirectories)
- [ ] Delete outdated docs (compare timestamps, ask user)
- [ ] Update docs to match code (LLM-based validation)
- [ ] Add UI screenshots (if applicable, Playwright captures)

**Export System**:
- [ ] **GitHub**: Push code → Setup complete → Return repo URL
- [ ] **Folder**: Download ZIP with analyzer, local hooks, README

**Loop 3 Visualizer (2D)**:
- [ ] Concentric circles (scan → GitHub → docs → export)
- [ ] Progress indicator per ring
- [ ] Final quality score (100% target)
- [ ] Export button (GitHub vs folder)

### Week 11-12 Deliverables

**Code**:
- ✅ Full project audit orchestration
- ✅ GitHub repo creation wizard
- ✅ CI/CD pipeline generation (GitHub Actions)
- ✅ Documentation cleanup automation
- ✅ Export system (GitHub vs folder)
- ✅ Loop 3 visualizer (2D)

**Tests**:
- ✅ 40+ unit tests (audit, repo creation, docs cleanup)
- ✅ 3 integration tests (full Loop 3 workflow)

**Acceptance Criteria**:
- [ ] Full project audit achieves 100% pass rate
- [ ] GitHub repo creation works (test repo created)
- [ ] CI/CD pipeline generates valid workflow file
- [ ] Documentation cleanup organizes all docs correctly
- [ ] Export to GitHub works (code pushed, hooks installed)
- [ ] Export to folder works (ZIP download with all files)

---

## WEEKS 13-14: 3D Visualizations

### Overview

**Goal**: Upgrade 2D visualizers to 3D using Three.js + React Three Fiber.

**Team Assignment**:
- **Team B** (3 devs): Primary 3D development
- **Team A** (1 dev): Performance optimization (LOD rendering)

---

### Week 13-14 Objectives

**Three.js Setup**:
- [ ] Install dependencies: three, @react-three/fiber, @react-three/drei
- [ ] Configure 3D canvas (lighting, camera, controls)
- [ ] Setup OrbitControls (user camera manipulation)
- [ ] Performance optimization (LOD rendering, instancing)

**Loop 1: Orbital Ring Visualization**:
- [ ] Center: Failure rate percentage (3D text, color-coded)
- [ ] Ring: Iterations (nodes rotating around center)
- [ ] Satellites: Research artifacts (hoverable, clickable)
- [ ] Animation: Smooth rotation, pulsing effects
- [ ] Interaction: Click artifact → View details modal

**Loop 2: Execution Village Visualization**:
- [ ] Isometric village layout (3D buildings)
- [ ] Buildings: Princesses (size = drone count)
- [ ] Flying bees/drones: Agents (animated paths)
- [ ] Paths: Task delegation (lines connecting buildings)
- [ ] Color coding: Task status (pending = gray, in-progress = yellow, complete = green)
- [ ] Interaction: Click building → View princess details

**Loop 3: Concentric Circles Visualization**:
- [ ] Center: Project core (3D sphere)
- [ ] Rings: Scan → GitHub → Docs → Export (expanding outward)
- [ ] Progress: Fill ring segments as tasks complete
- [ ] Animation: Ripple effects on completion
- [ ] Interaction: Click ring → View stage details

**Performance Optimization**:
- [ ] LOD (Level of Detail) rendering (reduce geometry at distance)
- [ ] Instancing (reuse geometries for multiple objects)
- [ ] Frustum culling (hide objects outside camera view)
- [ ] 60 FPS target (smooth animations)
- [ ] Mobile support (lower detail on mobile devices)

### Week 13-14 Deliverables

**Code**:
- ✅ Three.js + React Three Fiber integration
- ✅ Loop 1: Orbital ring (3D visualization)
- ✅ Loop 2: Execution village (3D visualization)
- ✅ Loop 3: Concentric circles (3D visualization)
- ✅ Camera controls + interaction (OrbitControls)
- ✅ Performance optimization (LOD, instancing)

**Tests**:
- ✅ 20+ unit tests (3D component rendering)
- ✅ Performance tests (60 FPS target)

**Acceptance Criteria**:
- [ ] All 3 loop visualizers upgraded to 3D
- [ ] Smooth animations (60 FPS on desktop)
- [ ] User interaction working (click, hover)
- [ ] Mobile support (30 FPS minimum)
- [ ] No performance regressions (<3s page load)

---

## WEEKS 15-16: UI Validation + Polish

### Overview

**Goal**: Implement Playwright screenshot system, visual diff comparison, UI polish.

**Team Assignment**:
- **Team B** (3 devs): UI polish + animations
- **Team A** (1 dev): Playwright screenshot system
- **Team C** (1 dev): Visual diff comparison

---

### Week 15-16 Objectives

**Playwright Screenshot System**:
- [ ] Playwright integration (headless browser)
- [ ] Screenshot capture (full page, specific elements)
- [ ] Chrome MCP server integration (if available)
- [ ] Storage: Screenshots stored in database (base64 encoded)
- [ ] API: `/api/ui/screenshot` (capture current UI state)

**Visual Diff Comparison**:
- [ ] Image comparison algorithm (pixel-by-pixel diff)
- [ ] Highlight differences (red overlay)
- [ ] Side-by-side view (expected vs actual)
- [ ] Approval workflow (user approves or requests changes)
- [ ] API: `/api/ui/compare` (compare two screenshots)

**UI Polish**:
- [ ] Animations: Framer Motion (page transitions, hover effects)
- [ ] Loading states: Skeleton loaders (consistent across app)
- [ ] Error states: Toast notifications (user-friendly messages)
- [ ] Empty states: Helpful messages (e.g., "No projects yet")
- [ ] Accessibility: ARIA labels, keyboard navigation
- [ ] Responsive design: Mobile, tablet, desktop (tested on all)

**Performance Optimization**:
- [ ] Code splitting (lazy load routes)
- [ ] Image optimization (Next.js Image component)
- [ ] Font optimization (Vercel font loading)
- [ ] Bundle size reduction (<500KB target)
- [ ] Lighthouse score: 90+ (Performance, Accessibility, Best Practices)

### Week 15-16 Deliverables

**Code**:
- ✅ Playwright screenshot system
- ✅ Visual diff comparison engine
- ✅ User approval workflow
- ✅ UI polish + animations (Framer Motion)
- ✅ Performance optimization (code splitting, image optimization)

**Tests**:
- ✅ 30+ unit tests (screenshot system, visual diff)
- ✅ 5 E2E tests (UI validation workflow)

**Acceptance Criteria**:
- [ ] Playwright screenshot system captures UI correctly
- [ ] Visual diff comparison highlights differences accurately
- [ ] User approval workflow functional (approve/reject)
- [ ] UI polish complete (animations, loading states, errors)
- [ ] Performance optimized (page load <3s, Lighthouse 90+)
- [ ] Accessibility compliant (ARIA labels, keyboard navigation)
- [ ] Responsive design working (mobile, tablet, desktop)

---

## WEEKS 17-18: 22 Agents Implementation

### Overview

**Goal**: Implement all 22 agents with AgentContract interface.

**Team Assignment**:
- **Team A** (3 devs): Core agents (5) + Swarm coordinators (4)
- **Team C** (2 devs): Specialized agents (13)

---

### Week 17-18 Objectives

**Core Agents (5)**:
- [ ] `queen` - Top-level coordinator (Monarch)
- [ ] `coder` - Code implementation
- [ ] `researcher` - Research and analysis
- [ ] `tester` - Test creation and validation
- [ ] `reviewer` - Code review and quality

**Swarm Coordinators (4)**:
- [ ] `princess-dev` - Development coordination
- [ ] `princess-quality` - Quality assurance coordination
- [ ] `princess-coordination` - Task coordination
- [ ] `queen` (also serves coordination role)

**Specialized Agents (13)**:
- [ ] `architect` - System design
- [ ] `pseudocode-writer` - Algorithm design
- [ ] `spec-writer` - Requirements writing
- [ ] `integration-engineer` - System integration
- [ ] `debugger` - Bug fixing
- [ ] `docs-writer` - Documentation writing
- [ ] `devops` - Deployment automation
- [ ] `security-manager` - Security auditing
- [ ] `cost-tracker` - Cost monitoring
- [ ] `theater-detector` - Mock code detection
- [ ] `nasa-enforcer` - NASA Rule 10 compliance
- [ ] `fsm-analyzer` - FSM decision matrix validation
- [ ] `orchestrator` - Multi-agent orchestration

**Agent2Agent Protocol Integration**:
- [ ] Context establishment (pwd, TodoWrite with absolute path)
- [ ] `.project-boundary` marker creation
- [ ] Path validation (all paths absolute)
- [ ] Context DNA translation integrity

### Week 17-18 Deliverables

**Code**:
- ✅ 22 agents implemented (AgentContract interface)
- ✅ Agent2Agent protocol integration
- ✅ Context DNA cross-agent memory

**Tests**:
- ✅ 110+ unit tests (5 tests per agent × 22 agents)
- ✅ 10 integration tests (multi-agent workflows)

**Acceptance Criteria**:
- [ ] All 22 agents implement AgentContract interface
- [ ] Agent2Agent protocol working (context translation)
- [ ] Context DNA cross-agent memory functional
- [ ] All agents functional (basic execute logic)
- [ ] Agent coordination latency <100ms (maintained)

---

## WEEKS 19-20: Context DNA + Storage

### Overview

**Goal**: Implement SQLite Context DNA, Redis caching, Pinecone vectors, cross-agent memory.

**Team Assignment**:
- **Team A** (2 devs): SQLite Context DNA + search
- **Team C** (2 devs): Redis caching + Pinecone vectors

---

### Week 19-20 Objectives

**SQLite Context DNA**:
- [ ] Schema: `context_entries` (id, agent_id, task_id, context_text, timestamp, artifacts)
- [ ] FTS (Full-Text Search) index (search by keywords)
- [ ] Vector similarity search (embeddings)
- [ ] 30-day retention policy (auto-delete old entries)
- [ ] Artifact references (file paths, not full files)

**Redis Caching**:
- [ ] Project indexing cache (avoid re-indexing)
- [ ] Agent metadata cache (capabilities, cost, latency)
- [ ] Task queue cache (job status, progress)
- [ ] TTL-based expiration (configurable per key)
- [ ] Invalidation on project update

**Pinecone Vectors**:
- [ ] Project embeddings (file-level chunks)
- [ ] Context DNA embeddings (search by semantic similarity)
- [ ] Metadata filtering (by agent, task, timestamp)
- [ ] Hybrid search (keyword + vector similarity)

**Cross-Agent Memory**:
- [ ] Memory retrieval API (search Context DNA)
- [ ] Memory storage API (save context entries)
- [ ] Memory sharing (agents access shared context)
- [ ] Search optimization (<200ms target)

### Week 19-20 Deliverables

**Code**:
- ✅ SQLite Context DNA (30-day retention)
- ✅ Redis caching layer (LRU + TTL)
- ✅ Pinecone vectors (project + context embeddings)
- ✅ Cross-agent memory system
- ✅ Search optimization (<200ms)

**Tests**:
- ✅ 40+ unit tests (Context DNA, caching, vectors)
- ✅ 5 integration tests (cross-agent memory)

**Acceptance Criteria**:
- [ ] Context DNA stores 30-day history
- [ ] Search latency <200ms (p95)
- [ ] Redis caching reduces re-indexing by 90%
- [ ] Pinecone vectors enable semantic search
- [ ] Cross-agent memory working (agents share context)

---

## WEEKS 21-22: DSPy Optimization

### Overview

**Goal**: Selective DSPy optimization for 8 critical agents (performance tuning).

**Team Assignment**:
- **Team D** (2 devs): DSPy optimization
- **Team A** (1 dev): Evaluation benchmark creation

---

### Week 21-22 Objectives

**8 Critical Agents for DSPy Optimization**:
- [ ] `queen` (Monarch coordinator)
- [ ] `coder` (code implementation)
- [ ] `researcher` (research agent)
- [ ] `tester` (test creation)
- [ ] `princess-dev` (development coordinator)
- [ ] `spec-writer` (requirements writing)
- [ ] `architect` (system design)
- [ ] `debugger` (bug fixing)

**DSPy Optimization Process**:
- [ ] Create training dataset (100+ examples per agent)
- [ ] Define evaluation metrics (accuracy, latency, cost)
- [ ] Run DSPy optimization (BootstrapFewShot)
- [ ] Validate performance (test on holdout set)
- [ ] Deploy optimized prompts (replace default prompts)

**Performance Tuning**:
- [ ] Target: 0.68-0.73 system performance (68-73% SWE-Bench)
- [ ] Latency optimization (reduce unnecessary tokens)
- [ ] Cost optimization (<$150/month)
- [ ] A/B testing (compare optimized vs default)

**Evaluation Benchmark**:
- [ ] Create benchmark dataset (10 real projects)
- [ ] Metrics: Task completion rate, audit pass rate, time to completion
- [ ] Automated evaluation (CI/CD integration)

### Week 21-22 Deliverables

**Code**:
- ✅ DSPy optimization for 8 agents
- ✅ Evaluation benchmark (10 projects)
- ✅ Performance tuning (0.68-0.73 target)

**Tests**:
- ✅ 20+ unit tests (DSPy prompts)
- ✅ Evaluation benchmark (10 projects)

**Acceptance Criteria**:
- [ ] 8 agents optimized with DSPy
- [ ] System performance 0.68-0.73 (validated on benchmark)
- [ ] Monthly cost <$150 (maintained)
- [ ] Latency <100ms (agent coordination, maintained)

---

## WEEKS 23-24: Production Validation

### Overview

**Goal**: End-to-end testing, performance benchmarks, security audit, GO/NO-GO decision.

**Team Assignment**:
- **All Teams** (10 devs): Production validation

---

### Week 23-24 Objectives

**End-to-End Testing**:
- [ ] Test full 3-loop workflow (10 real projects)
- [ ] Test all 9 pages (UI validation)
- [ ] Test all 22 agents (functionality)
- [ ] Test all API endpoints (30+ routes)
- [ ] Test all WebSocket events (real-time updates)

**Performance Benchmarks**:
- [ ] Load testing (100 concurrent users)
- [ ] Vectorization speed (<60s for 10k LOC)
- [ ] Sandbox validation (<20s per task)
- [ ] Agent coordination latency (<100ms)
- [ ] tRPC response time (<200ms p95)
- [ ] WebSocket latency (<100ms)
- [ ] Context search (<200ms)

**Security Audit**:
- [ ] Bandit scan (Python code)
- [ ] Semgrep scan (all code)
- [ ] Dependency audit (npm audit, pip-audit)
- [ ] Authentication testing (JWT validation)
- [ ] Authorization testing (role-based access)
- [ ] Injection attacks (SQL, XSS, CSRF)
- [ ] Docker sandbox security (isolation, resource limits)

**Documentation Finalization**:
- [ ] User guide (how to use Atlantis UI)
- [ ] Developer guide (how to extend agents)
- [ ] API documentation (all endpoints)
- [ ] Architecture diagrams (final versions)
- [ ] Deployment guide (Vercel, Docker, Redis, Pinecone)

**GO/NO-GO Decision**:
- [ ] Review all acceptance criteria (Weeks 1-24)
- [ ] Review all technical gates (13 gates)
- [ ] Review all quality gates (4 gates)
- [ ] Review all performance benchmarks (7 benchmarks)
- [ ] Review security audit results (zero critical vulnerabilities)
- [ ] Executive approval (stakeholder sign-off)

### Week 23-24 Deliverables

**Code**:
- ✅ Production-ready codebase (all features complete)
- ✅ Zero critical bugs (all P0/P1 fixed)
- ✅ Zero critical security vulnerabilities

**Tests**:
- ✅ 600+ unit tests (all components)
- ✅ 100+ integration tests (all workflows)
- ✅ 20+ end-to-end tests (critical flows)
- ✅ 80%+ code coverage (maintained)

**Documentation**:
- ✅ User guide (complete)
- ✅ Developer guide (complete)
- ✅ API documentation (complete)
- ✅ Architecture diagrams (final)
- ✅ Deployment guide (complete)

**Acceptance Criteria**:
- [ ] All 13 technical gates passed
- [ ] All 4 quality gates passed
- [ ] All 7 performance benchmarks met
- [ ] Zero critical security vulnerabilities
- [ ] All 600+ tests passing
- [ ] Code coverage >=80%
- [ ] Documentation complete and accurate
- [ ] Executive approval obtained

---

## Risk Mitigation

### Timeline Risks

**Risk**: 24-week timeline too aggressive
**Mitigation**:
- Parallel teams (4 teams working concurrently)
- Weekly checkpoints (identify delays early)
- Buffer weeks (2 weeks built into production validation)
- Scope reduction option (remove optional features if behind)

**Risk**: 3D visualizations take longer than expected
**Mitigation**:
- 2D visualizers implemented first (Weeks 7-12)
- 3D upgrade separate phase (Weeks 13-14)
- Can ship with 2D if 3D blocked (quality gate: functional, not 3D)

**Risk**: DSPy optimization doesn't improve performance
**Mitigation**:
- Optional optimization (Week 21-22, can skip if no ROI)
- Baseline performance already acceptable (68% target)
- A/B testing validates improvement (rollback if worse)

### Dependency Risks

**Risk**: Pinecone service downtime
**Mitigation**:
- Fallback: In-memory vector search (slower, but functional)
- Graceful degradation (project indexing still works)
- Alternative: Weaviate self-hosted (open-source)

**Risk**: GitHub API rate limits exceeded
**Mitigation**:
- Aggressive caching (Redis)
- Batch operations (reduce API calls)
- GraphQL (fetch exactly what's needed)
- Fallback: Manual GitHub setup (skip automation)

**Risk**: Docker sandbox security vulnerability
**Mitigation**:
- Regular security updates (Docker images)
- Network isolation (no external access)
- Resource limits (prevent DoS)
- Alternative: Cloud sandboxes (e.g., CodeSandbox API)

### Technical Risks

**Risk**: Real-time WebSocket scaling issues
**Mitigation**:
- Redis adapter (horizontal scaling)
- Connection pooling (limit concurrent connections)
- Fallback: Polling (slower, but works)
- Load testing (Week 23-24 identifies bottlenecks)

**Risk**: Project vectorization too slow for large codebases
**Mitigation**:
- Incremental indexing (only changed files)
- Parallel AST parsing (multi-threading)
- Progress updates (user sees activity)
- Timeout: Skip vectorization if >5 minutes (manual fallback)

**Risk**: 3-stage audit too slow (blocks task completion)
**Mitigation**:
- Parallel audit execution (run stages concurrently where possible)
- Caching: Skip re-audit if code unchanged
- Timeout: Skip quality scan if >60s (log warning, continue)
- Performance tuning (Week 4, <20s target)

---

## Success Metrics

### Per-Week KPIs

**Weeks 1-2** (Analyzer Refactoring):
- [ ] God objects: 70 → <10
- [ ] Test coverage: 30% → 80%
- [ ] Self-analysis: Fallback mode → Production mode
- [ ] Theater score: >30% → <10%

**Weeks 3-4** (Core System):
- [ ] Agent coordination latency: <100ms
- [ ] Project vectorization: <60s (10k LOC)
- [ ] Sandbox validation: <20s
- [ ] tRPC response time: <200ms (p95)
- [ ] Code coverage: >=80%

**Weeks 5-6** (Atlantis UI):
- [ ] 9 pages implemented
- [ ] Page load time: <3s
- [ ] WebSocket latency: <100ms
- [ ] Component tests: 150+
- [ ] Responsive design: Mobile, tablet, desktop

**Weeks 7-8** (Loop 1):
- [ ] Failure rate convergence: <5% within 10 iterations
- [ ] Research artifacts: >=10 per project
- [ ] Pre-mortem quality: >=10 failure modes identified
- [ ] Loop 1 completion time: <30 minutes

**Weeks 9-10** (Loop 2):
- [ ] MECE phase division: No overlapping phases
- [ ] Audit pass rate: >95% (first attempt)
- [ ] Task completion time: <10 minutes average
- [ ] GitHub Projects sync: Real-time updates

**Weeks 11-12** (Loop 3):
- [ ] Final quality score: 100%
- [ ] GitHub repo creation: 100% success rate
- [ ] CI/CD generation: Valid workflow file
- [ ] Documentation accuracy: 100%

**Weeks 13-14** (3D Visualizations):
- [ ] 60 FPS (desktop)
- [ ] 30 FPS (mobile)
- [ ] User interaction: Click, hover, camera controls
- [ ] No performance regressions

**Weeks 15-16** (UI Validation):
- [ ] Visual diff accuracy: >=90%
- [ ] User approval rate: >=90%
- [ ] Lighthouse score: 90+
- [ ] Accessibility: WCAG 2.1 AA compliance

**Weeks 17-18** (22 Agents):
- [ ] All agents implement AgentContract
- [ ] Agent coordination latency: <100ms (maintained)
- [ ] Context DNA working: Cross-agent memory functional

**Weeks 19-20** (Context DNA):
- [ ] Search latency: <200ms (p95)
- [ ] 30-day retention: Working
- [ ] Redis cache hit rate: >90%

**Weeks 21-22** (DSPy Optimization):
- [ ] System performance: 0.68-0.73
- [ ] Monthly cost: <$150
- [ ] Latency: <100ms (maintained)

**Weeks 23-24** (Production Validation):
- [ ] All technical gates: 13/13 passed
- [ ] All quality gates: 4/4 passed
- [ ] All performance benchmarks: 7/7 met
- [ ] Security vulnerabilities: 0 critical
- [ ] Executive approval: Obtained

---

## Conclusion

This 24-week plan delivers a **production-ready AI agent platform with Atlantis UI**, enabling autonomous project creation through 3 distinct refinement loops:

1. **Loop 1**: Research & pre-mortem (failure rate <5%)
2. **Loop 2**: Execution with Princess Hive delegation (audit pass rate >95%)
3. **Loop 3**: Final quality scan + GitHub export (100% quality score)

**Key Innovations**:
- 3D visualizations (orbital ring, execution village, concentric circles)
- Real-time WebSocket updates (agent activity streaming)
- Project vectorization (embeddings + caching)
- 3-stage audit pipeline (theater → production → quality)
- UI validation system (Playwright screenshot comparison)
- Documentation cleanup automation

**Total Investment**:
- 24 weeks (10 developers)
- $150/month operational cost
- $1,800 first-year operational cost

**Expected Outcomes**:
- 70-75% SWE-Bench solve rate
- <5% Loop 1 failure rate
- >95% Loop 2 audit pass rate
- 100% Loop 3 quality score
- Production-ready platform (GO decision)

---

**Version**: 7.0-DRAFT
**Timestamp**: 2025-10-08T20:00:00-04:00
**Agent/Model**: Claude Sonnet 4.5
**Status**: DRAFT - Awaiting SPEC-v7-DRAFT review

**Receipt**:
- Run ID: plan-v7-draft-001
- Inputs: USER-STORY-BREAKDOWN.md, PLAN-v6-FINAL.md
- Tools Used: Read (3), Write (1)
- Changes: Created PLAN-v7-DRAFT.md (24-week Atlantis UI plan)
- Lines: 1,100+ lines (comprehensive weekly breakdown)

---

**Next Steps**:
1. Review SPEC-v7-DRAFT.md (once created)
2. Align PLAN-v7 with SPEC-v7 requirements
3. Pre-mortem v7 (identify new risks from Atlantis UI)
4. Research v7 (investigate identified technical challenges)
5. Create v8 SPEC/PLAN incorporating research findings
