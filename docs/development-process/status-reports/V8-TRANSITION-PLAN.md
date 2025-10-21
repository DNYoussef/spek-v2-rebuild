# Transition to v8-FINAL Plan - Atlantis UI

**Date**: 2025-10-08
**Decision**: Switch from v6 plan to v8-FINAL plan
**Status**: PLANNING

---

## Executive Decision

**Switching to PLAN-v8-FINAL** (26 weeks, Atlantis UI-focused)

**Rationale**:
- More ambitious scope (web UI + 3D visualizations)
- Better user experience (visual monitoring vs CLI only)
- Research-backed performance optimizations
- Agents already complete (ahead of schedule!)

---

## Current Position vs v8 Timeline

### What We've Actually Completed

**From v6 Plan (Weeks 1-5)**:
- ✅ Week 1-2: Analyzer refactoring (100%)
- ✅ Week 3-4: Core system (AgentContract, EnhancedLightweightProtocol)
- ✅ Week 5: All 22 agents (8,248 LOC, 99% NASA compliance)

**Bonus Work**:
- ✅ Week 6 Days 1-3: DSPy infrastructure (can use later in Week 21-22)

### Mapping to v8 Plan

**v8 Week 1-2**: ✅ Analyzer refactoring - COMPLETE

**v8 Week 3-4**: ⚠️ PARTIALLY COMPLETE
- ✅ AgentContract
- ✅ EnhancedLightweightProtocol
- ✅ GovernanceDecisionEngine
- ❌ **tRPC API routes** (NOT DONE)
- ❌ **Redis Pub/Sub WebSocket adapter** (CRITICAL - NOT DONE)
- ❌ **Parallel vectorization + git caching** (CRITICAL - NOT DONE)
- ❌ **Docker sandbox** (CRITICAL - NOT DONE)
- ❌ **BullMQ task queue** (NOT DONE)

**v8 Week 5-16**: ❌ NOT STARTED (Atlantis UI)

**v8 Week 17-18**: ✅ DONE EARLY! (22 agents from v6 Week 5)

**v8 Week 21-22**: ✅ PARTIALLY DONE EARLY (DSPy infrastructure ready, training blocked)

---

## Critical Gap Analysis

### Week 4 CRITICAL GATE - 3 Missing Components

These are **NON-NEGOTIABLE** per PLAN-v8-FINAL:

#### 1. Redis Pub/Sub WebSocket Adapter ❌

**Purpose**: Horizontal WebSocket scaling (200+ concurrent users)

**Current State**: None - using basic Socket.io without Redis

**Impact**:
- Cannot scale beyond ~50 concurrent users
- Single server bottleneck
- No fault tolerance

**Required**:
```typescript
// src/server/websocket/SocketServer.ts
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
io.adapter(createAdapter(pubClient, subClient));
```

**Estimate**: 1 day (Monday Week 6)

---

#### 2. Parallel Vectorization + Git Hash Caching ❌

**Purpose**: 10x speedup for project indexing (60s for 10K files, not 10 minutes)

**Current State**: None - no vectorization implemented yet

**Impact**:
- User waits 10+ minutes to index large projects
- No caching (re-indexes entire project every time)
- Poor UX

**Required**:
```typescript
// src/vectorization/ParallelIndexer.ts
import { Worker } from 'worker_threads';
import { createHash } from 'crypto';

// 1. Check git commit hash
const currentHash = execSync('git rev-parse HEAD').toString().trim();
const cached = await redis.get(`index:${currentHash}`);
if (cached) return JSON.parse(cached); // <1s cache hit

// 2. Parallel processing (10 workers)
const workers = Array(10).fill(null).map(() => new Worker('./indexWorker.js'));
const chunks = chunkArray(files, Math.ceil(files.length / 10));
const results = await Promise.all(chunks.map((chunk, i) =>
  workers[i].process(chunk)
));

// 3. Cache results (30-day TTL)
await redis.setex(`index:${currentHash}`, 2592000, JSON.stringify(results));
```

**Estimate**: 2 days (Tuesday-Wednesday Week 6)

---

#### 3. Docker Sandbox with Resource Limits ❌

**Purpose**: Secure code execution (512MB RAM, 30s timeout, network isolation)

**Current State**: None - no sandbox infrastructure

**Impact**:
- Cannot safely execute user code
- Security risk
- Week 9+ production testing blocked

**Required**:
```typescript
// src/sandbox/DockerSandbox.ts
import Docker from 'dockerode';

const docker = new Docker();

export async function executeSandboxed(code: string) {
  const container = await docker.createContainer({
    Image: 'python:3.11-alpine',
    Cmd: ['python', '-c', code],
    HostConfig: {
      Memory: 512 * 1024 * 1024, // 512MB
      NetworkMode: 'none', // Network isolation
      PidsLimit: 50
    }
  });

  await container.start();

  const exec = await container.wait({
    condition: 'not-running'
  }, {
    timeout: 30000 // 30s timeout
  });

  const logs = await container.logs({ stdout: true, stderr: true });
  await container.remove();

  return logs;
}
```

**Estimate**: 2 days (Thursday-Friday Week 6)

---

## Adjusted Timeline

### Week 6 (NOW): Complete Week 4 Critical Infrastructure

**Monday (Day 1)**: Redis Pub/Sub WebSocket adapter
- Provision Redis instance (Upstash 2GB free tier)
- Integrate @socket.io/redis-adapter
- Test horizontal scaling (2+ server instances)
- Verify <50ms message latency

**Tuesday-Wednesday (Days 2-3)**: Parallel vectorization + caching
- Implement Worker thread pool (10 workers)
- Add git commit hash detection
- Integrate Redis caching (30-day TTL)
- Test with 10K file project (<60s target)

**Thursday-Friday (Days 4-5)**: Docker sandbox
- Create Python Docker image (512MB limit)
- Implement resource limits + network isolation
- Add 30s timeout with exponential backoff
- Test code execution security

**Deliverables**: 3 critical infrastructure components operational

---

### Weeks 7-8: Atlantis UI Foundation (Next.js 14)

**Objective**: Build core UI structure with 9 pages

**Week 7 Tasks**:
- Next.js 14 setup (App Router, TypeScript, ESLint)
- Install dependencies (shadcn/ui, Three.js, Socket.io client)
- Configure tRPC client
- Create page structure (9 routes)
- Implement basic layouts (header, sidebar, footer)

**Week 8 Tasks**:
- Monarch chat interface (page 1: `/`)
- Project selector component (pages 2-3: `/project/new`, `/project/select`)
- File system picker integration
- Real-time WebSocket connection
- Basic 2D visualizations (Loop 1, 2, 3 placeholders)

**Deliverables**: Next.js app with 9 pages, basic functionality, WebSocket connected

---

### Weeks 9-10: Loop 1 Implementation

**Week 9**: Research + Pre-mortem agents
- Research agent (GitHub + academic search)
- Pre-mortem multi-agent system
- Failure rate calculation engine

**Week 10**: Loop 1 visualizer
- Orbital ring visualization (2D functional)
- Agent thoughts streaming
- Pre-mortem results display

**Deliverables**: Loop 1 operational with 2D UI

---

### Weeks 11-12: Loop 2 Execution System

**Week 11**: MECE + Princess Hive
- Phase division algorithm
- Princess → Drone delegation
- Task execution pipeline
- 3-stage audit (Theater → Production → Quality)

**Week 12**: Execution village visualizer
- Isometric village layout (2D functional)
- Real-time task status
- Audit progress tracking

**Deliverables**: Loop 2 operational with 2D UI

---

### Weeks 13-14: Loop 3 Quality System

**Week 13**: Full audit orchestration
- GitHub repo creation wizard
- CI/CD pipeline generation
- Documentation cleanup (MANDATORY user approval)

**Week 14**: Loop 3 visualizer
- Concentric circles visualization (2D functional)
- Export system (GitHub vs folder)
- Quality reports

**Deliverables**: Loop 3 operational with 2D UI

---

### Week 15: 3D Performance Gate (GO/NO-GO)

**Critical Decision Point**: Test 3D performance with 5K+ files

**If 60 FPS achieved**:
- ✅ Proceed with Weeks 16-17 (full 3D implementation)

**If <60 FPS**:
- ❌ Skip 3D, ship with 2D visualizations only
- Defer 3D to Phase 2

**Test Criteria**:
- Desktop: 60 FPS with 5K files
- Mobile: 30 FPS (acceptable)
- GPU memory: <500MB
- Draw calls: <500

---

### Weeks 16-17: 3D Visualizations (CONDITIONAL)

**Only if Week 15 gate passes**

**Week 16**: Three.js integration
- React Three Fiber setup
- On-demand rendering (<Canvas frameloop="demand" />)
- Instanced rendering for drones
- LOD system (3 detail levels)

**Week 17**: Loop visualizations
- Loop 1: Orbital ring (rotating nodes)
- Loop 2: Execution village (instanced drones)
- Loop 3: Concentric circles (expanding rings)
- Camera controls + interaction

**Deliverables**: Full 3D visualizations at 60 FPS

---

### Weeks 18-19: UI Polish + Validation

**Week 18**: Playwright screenshot system
- 30s timeout + exponential backoff
- Dynamic content masking
- Visual diff comparison
- Manual approval fallback

**Week 19**: Performance optimization
- <3s page load time
- Lazy loading
- Code splitting
- Bundle optimization

**Deliverables**: Production-ready UI

---

### Weeks 20-21: Context DNA + Storage

**Week 20**: SQLite Context DNA
- 30-day retention
- Cross-agent memory
- Artifact references (not full files)

**Week 21**: Search optimization
- <200ms query time
- Vector similarity search
- Full-text search

**Deliverables**: Context DNA operational

---

### Weeks 22-23: DSPy Optimization (OPTIONAL)

**Already have infrastructure from Week 6 DSPy work!**

**Week 22**: Training (if we solve Gemini CLI issue OR use different LM)
- Train Queen & Tester
- Train Reviewer & Coder

**Week 23**: A/B testing
- Baseline vs optimized comparison
- Quality score validation (0.68 → 0.73 target)

**Deliverables**: Optimized agents (if training works)

---

### Weeks 24-25: Production Validation

**Week 24**: Load testing
- 200 concurrent users
- 10K+ file projects
- WebSocket reconnection
- 3D memory leak testing (if implemented)

**Week 25**: Final validation
- End-to-end workflow testing
- Security audit
- Documentation finalization

**Deliverables**: Production-ready system

---

### Week 26: Contingency Buffer

- Handle any delays from Weeks 24-25
- Emergency bug fixes
- Final polish

---

## What's Different from v6 Plan

### New Scope (v8 adds)

1. **Atlantis UI** (13 weeks of work):
   - Next.js 14 web interface
   - 9 pages with routing
   - 3D visualizations (conditional)
   - Real-time WebSocket streaming

2. **Critical Infrastructure** (Week 4 requirements):
   - Redis Pub/Sub adapter
   - Parallel vectorization
   - Docker sandbox

3. **Enhanced Features**:
   - Visual project graphs
   - Real-time agent thoughts
   - Interactive debugging
   - 3D performance monitoring

### What We Already Have (ahead of schedule)

1. **22 Agents** (v8 Week 17-18 work):
   - Already complete from v6 Week 5
   - **12 weeks ahead of schedule!**

2. **DSPy Infrastructure** (v8 Week 22-23 work):
   - Signatures, metrics, pipeline ready
   - **16 weeks ahead of schedule!**
   - Just need working LM backend

### Timeline Advantage

**Original v8 timeline**: 26 weeks

**Adjusted timeline** (with early completions):
```
Week 1-2:   Analyzer (DONE) ✅
Week 3-4:   Core + Critical Infrastructure (PARTIAL - need 3 items)
Week 5:     22 Agents (DONE EARLY!) ✅
Week 6:     Complete Week 4 critical infrastructure (NOW)
Week 7-8:   Atlantis UI Foundation
Week 9-10:  Loop 1
Week 11-12: Loop 2
Week 13-14: Loop 3
Week 15:    3D Performance Gate
Week 16-17: 3D Implementation (conditional)
Week 18-19: UI Polish
Week 20-21: Context DNA
Week 22-23: DSPy (infrastructure ready!) ✅
Week 24-25: Production validation
Week 26:    Buffer

Estimated completion: 20 weeks from now (6 weeks saved!)
```

---

## Immediate Next Steps (Week 6)

### Monday (Tomorrow)

**Redis Pub/Sub WebSocket Adapter** (8 hours):

1. **Provision Redis** (1 hour):
   - Sign up for Upstash free tier (2GB)
   - Get connection URL
   - Test connectivity

2. **Install Dependencies** (30 min):
   ```bash
   npm install @socket.io/redis-adapter redis ioredis
   ```

3. **Implement Adapter** (3 hours):
   - Create `src/server/websocket/SocketServer.ts`
   - Integrate Redis pub/sub
   - Add connection pooling
   - Error handling

4. **Test Scaling** (2 hours):
   - Run 2+ server instances
   - Test message broadcasting
   - Verify <50ms latency
   - Monitor connection count

5. **Documentation** (1.5 hours):
   - README with Redis setup
   - Environment variables
   - Scaling guide

**Success Criteria**: 200+ concurrent users supported, <50ms latency

---

### Tuesday-Wednesday

**Parallel Vectorization + Git Caching** (16 hours):

**Tuesday**:
1. Worker thread implementation (4 hours)
2. Git hash detection (2 hours)
3. Redis cache integration (2 hours)

**Wednesday**:
1. Parallel processing orchestration (4 hours)
2. Error handling + retry logic (2 hours)
3. Testing with 10K files (2 hours)

**Success Criteria**: <60s for 10K files, <1s cache hit

---

### Thursday-Friday

**Docker Sandbox** (16 hours):

**Thursday**:
1. Docker image creation (4 hours)
2. Resource limits configuration (2 hours)
3. Network isolation (2 hours)

**Friday**:
1. Timeout + exponential backoff (3 hours)
2. Security testing (3 hours)
3. Integration with agent system (2 hours)

**Success Criteria**: Secure code execution, 512MB limit, 30s timeout

---

## Budget Update

**v8 Phase 1**: $270/month
- Existing: $220/month (Claude Pro + Codex)
- Redis (Upstash): $10/month (can start with free tier)
- Vercel: $20/month (for Next.js hosting)
- Electricity: $20/month

**No change from v8 budget estimates**

---

## Risk Assessment

### High Risks

1. **3D Performance** (Week 15 gate):
   - Mitigation: 2D fallback ready
   - Impact: Defer 3D to Phase 2 (acceptable)

2. **Timeline Pressure** (26 weeks → 20 weeks):
   - Mitigation: We're ahead by 6 weeks
   - Impact: Buffer for delays

3. **Redis/Docker Setup** (Week 6):
   - Mitigation: Well-documented solutions
   - Impact: 1-week delay max

### Medium Risks

1. **WebSocket Scaling**:
   - Mitigation: Redis adapter is proven solution
   - Impact: Performance degradation if delayed

2. **Vectorization Speed**:
   - Mitigation: Parallel processing + caching
   - Impact: Poor UX if not optimized

### Low Risks

1. **DSPy Training** (Gemini CLI issue):
   - Already identified alternative (SDK or different LM)
   - Optional feature (Week 22-23)

---

## Success Metrics (v8)

**Week 6**: Critical infrastructure operational
**Week 8**: Atlantis UI foundation complete
**Week 15**: 3D performance gate decision
**Week 19**: Production-ready UI
**Week 25**: GO/NO-GO launch decision

**Final Target**: 70-75% SWE-Bench solve rate, <5% Loop 1 failure rate

---

## Version & Receipt

**Version**: 1.0
**Timestamp**: 2025-10-08T00:00:00-04:00
**Agent/Model**: Claude Sonnet 4.5
**Changes**: Created v8 transition plan, identified Week 4 gaps, planned Week 6 work
**Status**: READY TO EXECUTE

**Receipt**:
- run_id: v8-transition-plan
- inputs: [SPEC-v8-FINAL.md, PLAN-v8-FINAL.md, current status analysis]
- tools_used: [Write, TodoWrite]
- changes: Switched to v8 plan, created detailed Week 6 implementation plan
