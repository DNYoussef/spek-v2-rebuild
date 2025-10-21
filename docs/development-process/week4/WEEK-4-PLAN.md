# Week 4 Implementation Plan - Non-Negotiable Infrastructure

**Week**: 4 (Infrastructure Foundation)
**Timeline**: 5 days
**Focus**: Redis adapter, Parallel vectorization, Docker sandbox, Caching layer
**Status**: PLANNING COMPLETE - Ready for implementation

---

## Executive Summary

Week 4 delivers **4 non-negotiable infrastructure components** identified in PLAN-v8-FINAL as critical for production scalability and performance:

1. **Redis Pub/Sub Adapter** - WebSocket horizontal scaling (200+ concurrent users)
2. **Parallel Vectorization** - Pinecone indexing with 10x speedup
3. **Docker Sandbox** - Secure code execution (512MB RAM, 30s timeout, network isolated)
4. **Redis Caching Layer** - 30-day TTL for git fingerprints and embeddings

**Success Criteria**:
- ✅ WebSocket scaling: 200+ concurrent users with Redis adapter
- ✅ Vectorization: 10K files indexed in <60s (10x faster than baseline)
- ✅ Sandbox security: Network isolated, resource limited, non-root execution
- ✅ Cache hit rate: >80% for repeat project loads

**Risk Mitigation**:
- Week 4 eliminates 3 of top 5 P1 risks from PREMORTEM-v8-FINAL
- Estimated risk reduction: 420 points (973 → 553, 43% reduction)

---

## 📋 Week 4 Overview

### Timeline

| Day | Component | LOC Est. | Tests Est. | Priority |
|-----|-----------|----------|------------|----------|
| **Day 1** | Redis Pub/Sub Adapter + WebSocket Server | 400 | 15 | P0 (NON-NEGOTIABLE) |
| **Day 2** | Parallel Vectorization + Incremental Indexing | 600 | 20 | P0 (NON-NEGOTIABLE) |
| **Day 3** | Docker Sandbox + Security Constraints | 500 | 18 | P0 (NON-NEGOTIABLE) |
| **Day 4** | Redis Caching Layer + Invalidation | 350 | 12 | P0 (NON-NEGOTIABLE) |
| **Day 5** | Integration Testing + Week 4 Audit | 400 | 10 | P1 |
| **Total** | **5 components** | **~2,250 LOC** | **~75 tests** | **4 P0 + 1 P1** |

### Dependencies

**External Libraries** (Install Week 4 Day 1):
```bash
# WebSocket + Redis
npm install socket.io @socket.io/redis-adapter redis

# Vectorization
pip install pinecone-client openai langchain-pinecone

# Docker
pip install docker python-dotenv

# Testing
npm install --save-dev @types/socket.io
pip install pytest-asyncio pytest-docker
```

**From Week 3**:
- ✅ AgentContract interface (Day 1)
- ✅ EnhancedLightweightProtocol (Day 2)

---

## 🚀 Day 1: Redis Pub/Sub Adapter + WebSocket Server

### Objective
Implement horizontal WebSocket scaling with Redis Pub/Sub adapter to support 200+ concurrent users.

### Research Backing (RESEARCH-v7-ATLANTIS.md)

**Finding**: Socket.io Redis adapter enables horizontal scaling by broadcasting events across multiple server instances.

**Performance Target**:
- Concurrent users: 100+ Phase 1, 200+ Phase 2
- Message latency: <50ms (p95)
- Connection reliability: 99% uptime

**Architecture**:
```typescript
import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const io = new Server(httpServer);

// Redis adapter for horizontal scaling
const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await pubClient.connect();
await subClient.connect();
io.adapter(createAdapter(pubClient, subClient));
```

### Implementation Tasks

**1. WebSocket Server** (`src/server/websocket/SocketServer.ts` - 250 LOC):
```typescript
export class SocketServer {
  private io: Server;
  private redisAdapter: RedisAdapter;

  async initialize(httpServer: any, redisUrl: string): Promise<void> {
    // Setup Socket.io with Redis adapter
    // Event throttling (10 updates/sec max)
    // Room management (agent-specific, project-specific)
  }

  async broadcastAgentThought(agentId: string, thought: string): Promise<void> {
    // Throttled broadcast to agent room
  }

  async broadcastTaskUpdate(taskId: string, update: TaskUpdate): Promise<void> {
    // Real-time task status updates
  }
}
```

**2. Connection Manager** (`src/server/websocket/ConnectionManager.ts` - 150 LOC):
```typescript
export class ConnectionManager {
  private connections: Map<string, Socket>;
  private userRooms: Map<string, Set<string>>;

  async handleConnection(socket: Socket): Promise<void> {
    // Track connection
    // Setup event listeners
    // State reconciliation on reconnect
  }

  async handleDisconnection(socketId: string): Promise<void> {
    // Cleanup connection
    // Persist user state for reconnect
  }
}
```

**3. Event Throttler** (`src/server/websocket/EventThrottler.ts` - 100 LOC):
```typescript
export class EventThrottler {
  private eventQueues: Map<string, EventQueue>;
  private readonly MAX_EVENTS_PER_SEC = 10;

  throttle(userId: string, event: Event): void {
    // Queue event
    // Process at max 10/sec
    // Batch similar events
  }
}
```

### Test Plan (15 tests)

**Test File**: `tests/unit/test_websocket_server.ts`

1. **TestSocketServerInitialization** (3 tests):
   - Initialize with Redis adapter
   - Multiple server instances share state
   - Redis connection failure handling

2. **TestEventBroadcasting** (4 tests):
   - Broadcast to agent room
   - Broadcast to project room
   - Cross-server broadcast (Redis adapter)
   - Event throttling (max 10/sec)

3. **TestConnectionManagement** (4 tests):
   - Handle new connection
   - Handle disconnection
   - State reconciliation on reconnect
   - Concurrent connections (100+ users)

4. **TestPerformance** (4 tests):
   - Message latency <50ms (p95)
   - 200+ concurrent users
   - Event throughput (1000 events/sec)
   - Memory usage <500MB per server

### Quality Gates

- ✅ All 15 tests passing
- ✅ Latency <50ms (p95) with 200 users
- ✅ NASA compliance 100% (functions ≤60 LOC)
- ✅ 0 critical violations (analyzer scan)
- ✅ Redis failover handling (graceful degradation)

### Success Criteria

- 200+ concurrent WebSocket connections
- <50ms message latency (p95)
- 99% connection uptime
- Horizontal scaling validated (2+ server instances)

---

## 🔍 Day 2: Parallel Vectorization + Incremental Indexing

### Objective
Implement Pinecone vector indexing with parallel processing and git diff-based incremental updates (10x speedup).

### Research Backing (RESEARCH-v7-ATLANTIS.md)

**Finding**: Incremental indexing with git diff detection + parallel batch embedding reduces 10K file indexing from 15 minutes to <60 seconds.

**Performance Target**:
- Full indexing: 10K files in <60s
- Incremental: 100 changed files in <10s
- Cache hit: <1s (instant retrieval)

**Architecture**:
```typescript
// 1. Check cache (git commit hash)
const cached = await redis.get(`project:${projectId}:fingerprint`);
const current = await getGitCommitHash(projectPath);

if (cached === current) {
  return getCachedVectors(projectId); // <1s
}

// 2. Detect changed files (git diff)
const changedFiles = await gitDiff(cached, current);

// 3. Parallel embedding (batch size 64)
const embeddings = await embedBatch(changedFiles, { batchSize: 64 });

// 4. Upsert to Pinecone
await pinecone.upsert(embeddings);

// 5. Update cache
await redis.set(`project:${projectId}:fingerprint`, current, { EX: 2592000 });
```

### Implementation Tasks

**1. Incremental Indexer** (`src/services/vectorization/IncrementalIndexer.ts` - 300 LOC):
```typescript
export class IncrementalIndexer {
  private pinecone: PineconeClient;
  private redis: RedisClient;
  private embeddings: OpenAIEmbeddings;

  async incrementalVectorize(
    projectId: string,
    projectPath: string
  ): Promise<VectorizationResult> {
    // 1. Check cache (git fingerprint)
    // 2. Detect changed files (git diff)
    // 3. Parallel embedding (batch 64)
    // 4. Upsert to Pinecone
    // 5. Update cache (30-day TTL)
  }

  private async detectChangedFiles(
    projectPath: string,
    lastFingerprint: string
  ): Promise<string[]> {
    // git diff --name-only <lastFingerprint> HEAD
    // Filter to relevant extensions (.ts, .py, .md, etc.)
  }
}
```

**2. Parallel Embedder** (`src/services/vectorization/ParallelEmbedder.ts` - 200 LOC):
```typescript
export class ParallelEmbedder {
  private readonly BATCH_SIZE = 64;
  private readonly PARALLEL_TASKS = 10;

  async embedFiles(files: string[]): Promise<Embedding[]> {
    // Chunk files into batches of 64
    // Process 10 batches in parallel
    // Progress streaming (ETA calculation)
  }

  private async embedBatch(batch: string[]): Promise<Embedding[]> {
    // OpenAI text-embedding-3-small
    // Batch API call (64 texts at once)
  }
}
```

**3. Git Fingerprint Manager** (`src/services/vectorization/GitFingerprintManager.ts` - 100 LOC):
```typescript
export class GitFingerprintManager {
  async getCurrentFingerprint(projectPath: string): Promise<string> {
    // git rev-parse HEAD
    // Return commit hash as fingerprint
  }

  async getCachedFingerprint(projectId: string): Promise<string | null> {
    // Redis lookup
    return await redis.get(`project:${projectId}:fingerprint`);
  }

  async updateFingerprint(projectId: string, fingerprint: string): Promise<void> {
    // Redis update with 30-day TTL
    await redis.set(`project:${projectId}:fingerprint`, fingerprint, { EX: 2592000 });
  }
}
```

### Test Plan (20 tests)

**Test File**: `tests/unit/test_incremental_indexer.ts`

1. **TestGitFingerprinting** (4 tests):
   - Get current fingerprint (commit hash)
   - Cache hit (fingerprint match)
   - Cache miss (fingerprint mismatch)
   - No git repo fallback

2. **TestIncrementalIndexing** (6 tests):
   - Full indexing (10K files <60s)
   - Incremental indexing (100 files <10s)
   - Cache hit (<1s retrieval)
   - Git diff detection accuracy
   - File filtering (only relevant extensions)
   - Empty diff handling

3. **TestParallelEmbedding** (5 tests):
   - Batch size 64 validation
   - Parallel task count (10 concurrent)
   - Progress streaming (ETA accuracy)
   - Error handling (API rate limits)
   - Retry logic (transient failures)

4. **TestPineconeIntegration** (5 tests):
   - Upsert vectors to Pinecone
   - Query similarity search
   - Update existing vectors
   - Delete old vectors
   - Namespace management

### Quality Gates

- ✅ All 20 tests passing
- ✅ 10K files indexed in <60s (10x faster)
- ✅ Incremental indexing <10s for 100 files
- ✅ NASA compliance 100%
- ✅ 0 critical violations

### Success Criteria

- 10x speedup validated (10K files: 15min → <60s)
- Cache hit rate >80% for repeat loads
- OpenAI API rate limits respected (350 RPM)
- 30-day cache retention working

---

## 🐳 Day 3: Docker Sandbox + Security Constraints

### Objective
Implement secure Docker sandbox for production testing with resource limits and network isolation.

### Research Backing (RESEARCH-v7-ATLANTIS.md)

**Finding**: Docker sandbox with 512MB RAM, 30s timeout, network isolation, and non-root user provides defense-grade security for arbitrary code execution.

**Security Constraints**:
- Memory: 512MB limit (prevent DoS)
- CPU: 50% quota (prevent resource starvation)
- Network: Isolated (no outbound connections)
- Filesystem: Read-only root (prevent tampering)
- User: Non-root (least privilege)
- Timeout: 30s max (prevent infinite loops)

**Architecture**:
```python
from docker import DockerClient

container = await docker.createContainer({
  'Image': 'node:18-alpine',
  'HostConfig': {
    'Memory': 512 * 1024 * 1024,        # 512MB
    'CpuQuota': 50000,                   # 50% CPU
    'NetworkMode': 'none',               # Network isolated
    'ReadonlyRootfs': True,              # Read-only FS
    'SecurityOpt': ['no-new-privileges'],
    'CapDrop': ['ALL'],
  },
  'User': 'node',  # Non-root
})

# Timeout enforcement
timeout = asyncio.wait_for(container.wait(), timeout=30)
```

### Implementation Tasks

**1. Docker Sandbox Manager** (`src/services/sandbox/DockerSandbox.py` - 300 LOC):
```python
class DockerSandbox:
    def __init__(self, config: SandboxConfig):
        self.docker_client = docker.from_env()
        self.config = config

    async def execute_code(
        self,
        code: str,
        language: str,
        test_suite: Optional[str] = None
    ) -> SandboxResult:
        # 1. Create container with security constraints
        # 2. Copy code to container
        # 3. Execute with timeout (30s)
        # 4. Capture output
        # 5. Cleanup container
        pass

    async def run_tests(
        self,
        project_path: str,
        test_command: str
    ) -> TestResult:
        # Run test suite in sandbox
        # Parse test output (pytest, jest, etc.)
        # Return pass/fail with details
        pass

    def _create_secure_container(self, image: str) -> Container:
        # Security constraints enforcement
        # Resource limits
        # Network isolation
        pass
```

**2. Sandbox Configuration** (`src/services/sandbox/SandboxConfig.py` - 100 LOC):
```python
@dataclass
class SandboxConfig:
    memory_limit_mb: int = 512
    cpu_quota_percent: int = 50
    timeout_seconds: int = 30
    network_mode: str = "none"
    readonly_rootfs: bool = True
    user: str = "node"  # non-root
    allowed_images: List[str] = field(default_factory=lambda: [
        "node:18-alpine",
        "python:3.11-alpine",
        "golang:1.21-alpine"
    ])
```

**3. Security Validator** (`src/services/sandbox/SecurityValidator.py` - 100 LOC):
```python
class SecurityValidator:
    async def validate_pre_execution(self, code: str) -> SecurityCheckResult:
        # AST-based security checks
        # Block dangerous imports (os.system, subprocess, etc.)
        # Block file system access attempts
        # Block network access attempts
        pass

    async def validate_post_execution(self, container: Container) -> SecurityCheckResult:
        # Verify network isolation (no connections)
        # Verify filesystem unchanged (read-only enforced)
        # Verify resource limits respected
        pass
```

### Test Plan (18 tests)

**Test File**: `tests/unit/test_docker_sandbox.py`

1. **TestSandboxCreation** (3 tests):
   - Create container with security constraints
   - Verify resource limits (512MB RAM, 50% CPU)
   - Verify network isolation

2. **TestCodeExecution** (5 tests):
   - Execute Python code successfully
   - Execute TypeScript code successfully
   - Timeout enforcement (30s max)
   - Memory limit enforcement (fail >512MB)
   - CPU quota enforcement

3. **TestSecurityConstraints** (6 tests):
   - Network isolation (wget google.com fails)
   - Filesystem protection (chmod fails)
   - Non-root user enforcement
   - Dangerous import blocking (os.system)
   - Resource exhaustion protection
   - Infinite loop timeout

4. **TestTestSuiteExecution** (4 tests):
   - Run pytest test suite
   - Run jest test suite
   - Parse test output (pass/fail)
   - Handle test failures

### Quality Gates

- ✅ All 18 tests passing
- ✅ Security tests pass (network, filesystem, user)
- ✅ Resource limits enforced (512MB, 50% CPU, 30s)
- ✅ NASA compliance 100%
- ✅ 0 critical violations

### Success Criteria

- All security constraints validated
- 30s timeout enforced consistently
- No network access possible
- Filesystem tampering prevented
- Defense-grade security achieved

---

## 💾 Day 4: Redis Caching Layer + Invalidation

### Objective
Implement Redis caching layer with 30-day TTL for git fingerprints, embeddings, and session state.

### Research Backing (RESEARCH-v7-ATLANTIS.md)

**Finding**: Redis caching with 30-day TTL reduces storage growth to 50MB/month and provides <1s cache hits for repeat project loads.

**Cache Strategy**:
- Git fingerprints: 30-day TTL (project versions)
- Embeddings: 30-day TTL (vector cache)
- Session state: 24h TTL (ephemeral)
- Cleanup: Automatic expiration (TTL-based)

**Architecture**:
```typescript
// Cache keys
const keys = {
  fingerprint: `project:${projectId}:fingerprint`,
  vectors: `project:${projectId}:vectors`,
  session: `session:${sessionId}`,
};

// Set with TTL
await redis.set(keys.fingerprint, gitHash, { EX: 2592000 }); // 30 days
await redis.set(keys.vectors, JSON.stringify(vectors), { EX: 2592000 });
await redis.set(keys.session, JSON.stringify(state), { EX: 86400 }); // 24h

// Get with fallback
const cached = await redis.get(keys.fingerprint);
if (!cached) {
  // Cache miss - recompute
}
```

### Implementation Tasks

**1. Redis Cache Manager** (`src/services/cache/RedisCacheManager.ts` - 200 LOC):
```typescript
export class RedisCacheManager {
  private redis: RedisClient;
  private readonly TTL_30_DAYS = 2592000;
  private readonly TTL_24_HOURS = 86400;

  async setFingerprint(projectId: string, hash: string): Promise<void> {
    await this.redis.set(
      `project:${projectId}:fingerprint`,
      hash,
      { EX: this.TTL_30_DAYS }
    );
  }

  async getFingerprint(projectId: string): Promise<string | null> {
    return await this.redis.get(`project:${projectId}:fingerprint`);
  }

  async setVectors(projectId: string, vectors: Embedding[]): Promise<void> {
    await this.redis.set(
      `project:${projectId}:vectors`,
      JSON.stringify(vectors),
      { EX: this.TTL_30_DAYS }
    );
  }

  async invalidateProject(projectId: string): Promise<void> {
    // Delete all project-related keys
    await this.redis.del(`project:${projectId}:fingerprint`);
    await this.redis.del(`project:${projectId}:vectors`);
  }
}
```

**2. Cache Invalidation Strategy** (`src/services/cache/CacheInvalidationStrategy.ts` - 150 LOC):
```typescript
export class CacheInvalidationStrategy {
  async onGitCommit(projectId: string): Promise<void> {
    // Invalidate fingerprint + vectors on new commit
    await cacheManager.invalidateProject(projectId);
  }

  async onFileChange(projectId: string, files: string[]): Promise<void> {
    // Selective invalidation (only changed file vectors)
    // Keep fingerprint cache until git commit
  }

  async onProjectDelete(projectId: string): Promise<void> {
    // Full project cache cleanup
    await cacheManager.invalidateProject(projectId);
  }

  async getStorageMetrics(): Promise<CacheMetrics> {
    // Calculate cache size, hit rate, eviction count
    return {
      totalSize: await redis.dbsize(),
      hitRate: this.calculateHitRate(),
      evictionCount: await redis.info('stats').evicted_keys
    };
  }
}
```

### Test Plan (12 tests)

**Test File**: `tests/unit/test_redis_cache.ts`

1. **TestCacheOperations** (4 tests):
   - Set/get fingerprint with 30-day TTL
   - Set/get vectors with 30-day TTL
   - Set/get session with 24h TTL
   - TTL expiration validation

2. **TestCacheInvalidation** (4 tests):
   - Invalidate on git commit
   - Selective invalidation (file changes)
   - Full project invalidation (delete)
   - Multi-project isolation

3. **TestCacheMetrics** (4 tests):
   - Calculate hit rate (>80% target)
   - Storage size tracking (<100MB target)
   - Eviction monitoring
   - TTL cleanup validation

### Quality Gates

- ✅ All 12 tests passing
- ✅ Cache hit rate >80%
- ✅ Storage growth <50MB/month
- ✅ NASA compliance 100%
- ✅ 0 critical violations

### Success Criteria

- 30-day TTL enforced automatically
- Cache hit rate >80% for repeat loads
- Storage growth <50MB/month validated
- Invalidation strategy working correctly

---

## 🧪 Day 5: Integration Testing + Week 4 Audit

### Objective
Validate all Week 4 components work together and create comprehensive audit.

### Integration Test Scenarios

**1. End-to-End Vectorization Flow** (5 tests):
```typescript
async test_full_vectorization_flow() {
  // 1. First load (cache miss)
  const result1 = await incrementalIndexer.vectorize(projectId, projectPath);
  assert(result1.cacheHit === false);
  assert(result1.duration < 60000); // <60s for 10K files

  // 2. Second load (cache hit)
  const result2 = await incrementalIndexer.vectorize(projectId, projectPath);
  assert(result2.cacheHit === true);
  assert(result2.duration < 1000); // <1s cache hit

  // 3. File change + incremental update
  await modifyFiles(projectPath, 100);
  const result3 = await incrementalIndexer.vectorize(projectId, projectPath);
  assert(result3.duration < 10000); // <10s incremental
}
```

**2. WebSocket + Redis Scalability** (3 tests):
```typescript
async test_websocket_horizontal_scaling() {
  // 1. Start 2 WebSocket servers with Redis adapter
  const server1 = await createSocketServer(3001, redisUrl);
  const server2 = await createSocketServer(3002, redisUrl);

  // 2. Connect 200 clients across both servers
  const clients = await createClients(200, [server1, server2]);

  // 3. Broadcast event from server1
  await server1.broadcast('agent-thought', { agentId: 'coder', thought: 'Hello' });

  // 4. Verify all 200 clients receive event (cross-server)
  await waitForAllClients(clients);
  assert(allClientsReceived());
}
```

**3. Docker Sandbox + Cache Integration** (2 tests):
```typescript
async test_sandbox_with_caching() {
  // 1. Execute code in sandbox
  const result1 = await dockerSandbox.execute(code, 'python');
  assert(result1.success);

  // 2. Cache execution result
  await cacheManager.set(`exec:${codeHash}`, result1, { EX: 3600 });

  // 3. Repeat execution (cache hit)
  const result2 = await cacheManager.get(`exec:${codeHash}`);
  assert(result2 !== null);
}
```

### Week 4 Audit Document

**Structure**:
1. Executive Summary
2. Component Deliverables (Days 1-4)
3. Test Results (75+ tests total)
4. Quality Metrics (NASA compliance, analyzer scans)
5. Performance Validation (benchmarks)
6. Risk Reduction (420 points from Week 4)
7. Integration Success
8. Next Steps (Week 5)

---

## 📊 Week 4 Success Metrics

### Performance Targets

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| WebSocket concurrent users | 200+ | Load testing with artillery.io |
| WebSocket latency (p95) | <50ms | Performance test suite |
| Vectorization (10K files) | <60s | Benchmark test |
| Incremental indexing (100 files) | <10s | Benchmark test |
| Cache hit rate | >80% | Redis metrics |
| Sandbox timeout enforcement | 30s | Security test suite |
| Sandbox memory limit | 512MB | Docker stats validation |

### Quality Gates

- ✅ All 75+ tests passing (100% pass rate)
- ✅ NASA compliance ≥92% (target 100%)
- ✅ 0 critical violations (analyzer scans)
- ✅ Connascence level LOW (all components)
- ✅ Enterprise quality EXCELLENT (all components)
- ✅ Security tests pass (sandbox constraints)

### Risk Reduction

**Week 4 Mitigates 3 P1 Risks**:

1. **WebSocket Scalability** (Probability: 0.50 → 0.05):
   - Before: 200+ users untested, potential failure
   - After: Redis adapter implemented, load tested, validated
   - Risk Reduction: -180 points

2. **Vectorization Time** (Probability: 0.45 → 0.10):
   - Before: 15min baseline unacceptable for UX
   - After: Incremental indexing with 10x speedup validated
   - Risk Reduction: -140 points

3. **Docker Sandbox Security** (Probability: 0.40 → 0.05):
   - Before: Arbitrary code execution security uncertain
   - After: Defense-grade constraints implemented and tested
   - Risk Reduction: -100 points

**Total Risk Reduction**: 420 points (973 → 553, 43% reduction)

---

## 📁 Week 4 Deliverables

### Source Code (Estimated 2,250 LOC)

**Day 1 - WebSocket + Redis** (~400 LOC):
- `src/server/websocket/SocketServer.ts`
- `src/server/websocket/ConnectionManager.ts`
- `src/server/websocket/EventThrottler.ts`

**Day 2 - Vectorization** (~600 LOC):
- `src/services/vectorization/IncrementalIndexer.ts`
- `src/services/vectorization/ParallelEmbedder.ts`
- `src/services/vectorization/GitFingerprintManager.ts`

**Day 3 - Docker Sandbox** (~500 LOC):
- `src/services/sandbox/DockerSandbox.py`
- `src/services/sandbox/SandboxConfig.py`
- `src/services/sandbox/SecurityValidator.py`

**Day 4 - Redis Cache** (~350 LOC):
- `src/services/cache/RedisCacheManager.ts`
- `src/services/cache/CacheInvalidationStrategy.ts`

**Day 5 - Integration** (~400 LOC):
- `tests/integration/test_week4_integration.ts`
- `docs/WEEK-4-COMPLETE-AUDIT.md`

### Test Files (Estimated ~75 tests)

- `tests/unit/test_websocket_server.ts` (15 tests)
- `tests/unit/test_incremental_indexer.ts` (20 tests)
- `tests/unit/test_docker_sandbox.py` (18 tests)
- `tests/unit/test_redis_cache.ts` (12 tests)
- `tests/integration/test_week4_integration.ts` (10 tests)

### Documentation

- `docs/WEEK-4-PLAN.md` (This document)
- `docs/WEEK-4-DAY-1-AUDIT.md`
- `docs/WEEK-4-DAY-2-AUDIT.md`
- `docs/WEEK-4-DAY-3-AUDIT.md`
- `docs/WEEK-4-DAY-4-AUDIT.md`
- `docs/WEEK-4-COMPLETE-AUDIT.md`

---

## 🎯 Week 4 Dependencies

### External Services Required

1. **Redis** (for WebSocket adapter + caching):
   ```bash
   # Local development
   docker run -d -p 6379:6379 redis:7-alpine

   # Production (cloud)
   # Upstash Redis (free tier: 10K commands/day)
   # OR Redis Cloud (free tier: 30MB)
   ```

2. **Pinecone** (for vector storage):
   ```bash
   # Free tier: 1 index, 100K vectors
   # Requires API key from https://www.pinecone.io
   ```

3. **Docker** (for sandbox):
   ```bash
   # Docker Engine must be running
   # Alpine images: node:18-alpine, python:3.11-alpine
   ```

4. **OpenAI** (for embeddings):
   ```bash
   # text-embedding-3-small: $0.02 / 1M tokens
   # Requires API key from https://platform.openai.com
   ```

### Environment Variables

```bash
# Week 4 .env configuration
REDIS_URL=redis://localhost:6379
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=gcp-starter
OPENAI_API_KEY=your_openai_key
DOCKER_HOST=unix:///var/run/docker.sock

# Optional
REDIS_TTL_30_DAYS=2592000
REDIS_TTL_24_HOURS=86400
SANDBOX_TIMEOUT_MS=30000
SANDBOX_MEMORY_MB=512
```

---

## 🚧 Week 4 Risks & Mitigations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Redis connection failure | 0.20 | Medium | Graceful degradation (in-memory fallback) |
| Pinecone rate limits | 0.30 | Medium | Batch size optimization, retry with backoff |
| Docker daemon unavailable | 0.15 | High | Pre-flight check, clear error messages |
| OpenAI API timeout | 0.25 | Medium | Retry logic, timeout handling |

### Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Docker sandbox complexity | 0.40 | High | Allocate 1.5 days instead of 1 day |
| Pinecone learning curve | 0.35 | Medium | Research completed in v7, examples ready |
| Integration testing delays | 0.30 | Medium | Automated test suite, parallel execution |

---

## 📅 Week 4 Timeline

### Day-by-Day Breakdown

**Monday (Day 1)**: Redis Pub/Sub Adapter + WebSocket Server
- 08:00-12:00: Implement SocketServer + ConnectionManager
- 12:00-14:00: Implement EventThrottler
- 14:00-16:00: Write 15 unit tests
- 16:00-17:00: Analyzer scan + Day 1 audit
- **Deliverable**: WebSocket server with Redis adapter (400 LOC, 15 tests)

**Tuesday (Day 2)**: Parallel Vectorization + Incremental Indexing
- 08:00-11:00: Implement IncrementalIndexer + GitFingerprintManager
- 11:00-13:00: Implement ParallelEmbedder
- 13:00-16:00: Write 20 unit tests + benchmarks
- 16:00-17:00: Analyzer scan + Day 2 audit
- **Deliverable**: Vectorization with 10x speedup (600 LOC, 20 tests)

**Wednesday (Day 3)**: Docker Sandbox + Security Constraints
- 08:00-11:00: Implement DockerSandbox + SandboxConfig
- 11:00-13:00: Implement SecurityValidator
- 13:00-16:00: Write 18 security tests
- 16:00-17:00: Analyzer scan + Day 3 audit
- **Deliverable**: Secure sandbox (500 LOC, 18 tests)

**Thursday (Day 4)**: Redis Caching Layer + Invalidation
- 08:00-11:00: Implement RedisCacheManager
- 11:00-13:00: Implement CacheInvalidationStrategy
- 13:00-16:00: Write 12 unit tests
- 16:00-17:00: Analyzer scan + Day 4 audit
- **Deliverable**: Caching layer (350 LOC, 12 tests)

**Friday (Day 5)**: Integration Testing + Week 4 Audit
- 08:00-12:00: Write 10 integration tests
- 12:00-14:00: Run full test suite (75+ tests)
- 14:00-16:00: Performance benchmarking
- 16:00-18:00: Create comprehensive Week 4 audit
- **Deliverable**: Week 4 complete audit + integration validation

---

## ✅ Week 4 Sign-Off Criteria

### Must-Have (P0)

- ✅ Redis Pub/Sub adapter working with 200+ concurrent users
- ✅ Parallel vectorization achieving 10x speedup (<60s for 10K files)
- ✅ Docker sandbox with all security constraints validated
- ✅ Redis caching with 30-day TTL and >80% hit rate
- ✅ All 75+ tests passing (100% pass rate)
- ✅ NASA compliance 100% (all components)
- ✅ 0 critical violations (all analyzer scans)

### Nice-to-Have (P1)

- 🔄 WebSocket stress testing (1000+ users)
- 🔄 Pinecone namespace optimization
- 🔄 Docker multi-language support (Python, TypeScript, Go)
- 🔄 Advanced cache warming strategies

### Documentation (P1)

- ✅ Individual day audits (Days 1-4)
- ✅ Comprehensive Week 4 audit
- ✅ Architecture updates (ARCHITECTURE-MASTER-TOC.md)
- ✅ Integration test documentation

---

**Plan Version**: 4.0.0
**Created**: 2025-10-08
**Status**: READY FOR IMPLEMENTATION
**Estimated Effort**: 5 days (40 hours)
**Risk Level**: MEDIUM (mitigated with research and Week 3 foundation)

**Approval**: RECOMMENDED FOR WEEK 4 EXECUTION

---

**Generated**: 2025-10-08T17:30:00-04:00
**Model**: Claude Sonnet 4
**Document Type**: Implementation Plan
**Evidence Base**: PLAN-v8-FINAL + RESEARCH-v7-ATLANTIS + Week 3 foundation
