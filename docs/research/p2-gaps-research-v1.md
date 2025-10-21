# P2 Research Gaps - Practical Implementation Guide for SPEK v2

**Research Focus**: Bytebot Desktop Automation and Performance Optimization
**Priority Level**: P2 (Important - Implementation Enablers)
**Target Audience**: SPEK v2 Development Team
**Document Version**: 1.0.0
**Research Date**: 2025-10-08

---

## Executive Summary

This document provides targeted research findings for two critical P2 gaps in SPEK v2 development:

1. **Gap 3 - Bytebot Desktop Automation**: Docker compose setup, MCP bridge integration, screenshot automation, and security isolation
2. **Gap 7 - Performance Optimization**: Agent concurrency patterns, caching strategies, and context window management

**Key Recommendations**:
- Target 10-15 concurrent agents for SPEK v2 (Claude Flow supports up to 25, but practical limit is lower)
- Implement semantic caching with Redis for 31% query reduction and 3.2x faster response times
- Use Bytebot's bytebotd REST API on port 9990 for desktop automation with automatic screenshot evidence
- Apply sliding window context management with 60% memory compression
- Enforce Enhanced Container Isolation (ECI) for secure sandboxed execution

---

## Part 1: Bytebot Desktop Automation (Gap 3)

### 1.1 Docker Compose Setup with MCP Bridge

#### Overview
Bytebot is a self-hosted AI desktop agent that automates computer tasks through natural language commands, operating within a containerized Linux desktop environment. It provides REST and MCP APIs for precise control of mouse, keyboard, and screenshots.

#### Quick Start Configuration

**Prerequisites**:
- Docker and Docker Compose installed
- AI provider API key (Anthropic Claude, OpenAI GPT, or Google Gemini)

**Installation Steps**:

```bash
# Clone the repository
git clone https://github.com/bytebot-ai/bytebot.git
cd bytebot

# Configure environment
cd docker
cp .env.example .env

# Edit .env with your AI provider key
# ANTHROPIC_API_KEY=your-key-here
# or OPENAI_API_KEY=your-key-here
# or GOOGLE_AI_API_KEY=your-key-here

# Launch Bytebot
docker-compose -f docker-compose.yml up -d

# Access web interface
# http://localhost:9992
```

#### Docker Compose Architecture

**Key Components**:
1. **Base Image**: Ubuntu 22.04 with XFCE4 desktop environment
2. **Pre-installed Applications**:
   - VSCode (code editing)
   - Firefox (web browsing)
   - Thunderbird (email client)
3. **Automation Daemon**: bytebotd (NestJS service)
4. **Port Configuration**:
   - Port 9990: REST and MCP API endpoint (single port for all I/O)
   - Port 9991: Task management API
   - Port 9992: Web interface

**Example docker-compose.yml Structure**:

```yaml
version: '3.8'

services:
  bytebot:
    image: bytebot/bytebot:latest
    container_name: bytebot-desktop
    ports:
      - "9990:9990"  # bytebotd REST/MCP API
      - "9991:9991"  # Task management API
      - "9992:9992"  # Web interface
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
      - DISPLAY=:99
      - VNC_PASSWORD=bytebot
    volumes:
      - bytebot-home:/home/bytebot
      - bytebot-workspace:/workspace
    restart: unless-stopped
    security_opt:
      - seccomp:unconfined  # Required for desktop automation
    cap_add:
      - SYS_ADMIN  # Required for browser sandboxing

volumes:
  bytebot-home:
  bytebot-workspace:
```

#### MCP Bridge Integration

**bytebotd MCP Server**:
- Exposes both REST and MCP APIs on port 9990
- Allows language models to issue keyboard and mouse commands
- Provides structured interface for desktop automation

**MCP Client Configuration for SPEK v2**:

```json
{
  "mcpServers": {
    "bytebot": {
      "command": "npx",
      "args": [
        "-y",
        "@bytebot/mcp-server",
        "--api-url",
        "http://localhost:9990"
      ],
      "env": {
        "BYTEBOT_API_KEY": "your-api-key-if-required"
      }
    }
  }
}
```

**Available MCP Tools**:
- `bytebot_click`: Click at specific coordinates
- `bytebot_type`: Type text with keyboard
- `bytebot_screenshot`: Capture current screen
- `bytebot_move_mouse`: Move mouse to coordinates
- `bytebot_scroll`: Scroll page or window

### 1.2 Screenshot Capture Automation

#### Automatic Screenshot Evidence Collection

**Key Feature**: Bytebot automatically captures screenshots before and after every action for easy inspection and evidence collection.

#### REST API Screenshot Endpoint

**Capture Screenshot**:
```bash
# GET request to capture screenshot
curl http://localhost:9990/api/screenshot

# Response includes base64-encoded image
{
  "timestamp": "2025-10-08T14:30:00Z",
  "format": "png",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**MCP Screenshot Tool**:
```typescript
// Example MCP tool usage from SPEK v2 agent
const screenshot = await mcpClient.callTool('bytebot', 'bytebot_screenshot', {
  save_path: '/workspace/evidence/screenshot-001.png'
});

console.log('Screenshot saved:', screenshot.path);
```

#### Evidence Collection Pattern for SPEK v2

**Recommended Structure**:

```typescript
// SPEK v2 Evidence Collection Module
class BytebotEvidenceCollector {
  constructor(bytebotApiUrl = 'http://localhost:9990') {
    this.apiUrl = bytebotApiUrl;
    this.evidenceDir = '.claude/.artifacts/evidence';
  }

  async captureActionEvidence(actionName, beforeAction, afterAction) {
    // Capture before screenshot
    const beforeScreenshot = await this.captureScreenshot(
      `${actionName}-before-${Date.now()}.png`
    );

    // Execute action
    const result = await beforeAction();

    // Capture after screenshot
    const afterScreenshot = await this.captureScreenshot(
      `${actionName}-after-${Date.now()}.png`
    );

    // Return evidence package
    return {
      action: actionName,
      result: result,
      evidence: {
        before: beforeScreenshot,
        after: afterScreenshot
      }
    };
  }

  async captureScreenshot(filename) {
    const response = await fetch(`${this.apiUrl}/api/screenshot`);
    const data = await response.json();

    const filepath = path.join(this.evidenceDir, filename);
    await fs.writeFile(filepath, data.data, 'base64');

    return filepath;
  }
}
```

**Usage in SPEK v2 Quality Gates**:

```javascript
// Example: Theater detection with visual evidence
const evidence = await collector.captureActionEvidence(
  'npm-test-execution',
  async () => await exec('npm test'),
  null
);

// Evidence now includes:
// - evidence.before: screenshot before test
// - evidence.after: screenshot after test
// - evidence.result: test execution output
```

### 1.3 Security Best Practices for Sandboxed Desktop Automation

#### Docker Enhanced Container Isolation (ECI)

**Key Security Features**:
1. **Linux User Namespaces**: All containers leverage user namespaces for stronger isolation
2. **Sysbox Runtime**: Security-enhanced fork of standard OCI runc runtime
3. **Privileged Container Safety**: --privileged flag works but only accesses container-assigned resources
4. **Kernel Isolation**: Cannot access global kernel resources from privileged containers

**Enable ECI in Docker Desktop**:

```bash
# Docker Desktop settings.json
{
  "enhancedContainerIsolation": {
    "value": true,
    "locked": false
  }
}
```

**Security Configuration for Bytebot**:

```yaml
# docker-compose.yml with security hardening
services:
  bytebot:
    image: bytebot/bytebot:latest
    security_opt:
      - no-new-privileges:true
      - seccomp:unconfined  # Required for desktop automation
    cap_drop:
      - ALL
    cap_add:
      - SYS_ADMIN  # Only for browser sandboxing
      - NET_ADMIN  # Only if network control needed
    read_only: true  # Root filesystem read-only
    tmpfs:
      - /tmp:noexec,nosuid,size=1g
      - /var/tmp:noexec,nosuid,size=512m
    volumes:
      - bytebot-workspace:/workspace:rw  # Only workspace writable
    networks:
      - bytebot-isolated
    ulimits:
      nproc: 512  # Limit process count
      nofile: 1024  # Limit file descriptors

networks:
  bytebot-isolated:
    driver: bridge
    internal: false  # Set to true if no external access needed
```

#### MCP Security Best Practices

**1. Authentication and Authorization**:

```javascript
// Implement API gateway for MCP requests
class MCPSecurityGateway {
  async validateRequest(request, userContext) {
    // Check user permissions
    if (!this.hasPermission(userContext, request.tool)) {
      throw new Error('Insufficient permissions');
    }

    // Validate request parameters
    this.sanitizeParameters(request.params);

    // Check for prompt injection patterns
    if (this.detectInjection(request.prompt)) {
      throw new Error('Potential prompt injection detected');
    }

    return true;
  }

  detectInjection(prompt) {
    const injectionPatterns = [
      /ignore previous instructions/i,
      /system:\s*you are now/i,
      /forget all prior context/i
    ];

    return injectionPatterns.some(pattern => pattern.test(prompt));
  }
}
```

**2. Server Allowlist Configuration**:

```json
{
  "mcpSecurity": {
    "allowedServers": [
      "bytebot",
      "claude-flow",
      "memory",
      "github"
    ],
    "blockedServers": [
      "*"  // Block all others by default
    ],
    "requireSignedServers": true
  }
}
```

**3. Logging and Monitoring**:

```javascript
// Comprehensive MCP activity logging
class MCPAuditLogger {
  logToolCall(agentId, toolName, params, result) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      agent: agentId,
      tool: toolName,
      params: this.sanitizeForLogging(params),
      result: result.success ? 'SUCCESS' : 'FAILURE',
      suspicious: this.detectSuspicious(params)
    };

    // Write to centralized logging
    this.writeToSIEM(logEntry);

    // Alert on suspicious patterns
    if (logEntry.suspicious) {
      this.alertSecurityTeam(logEntry);
    }
  }

  detectSuspicious(params) {
    // Check for sensitive data patterns
    const sensitivePatterns = [
      /-----BEGIN (RSA|EC) PRIVATE KEY-----/,
      /sk-[a-zA-Z0-9]{48}/,  // OpenAI API key pattern
      /ghp_[a-zA-Z0-9]{36}/  // GitHub token pattern
    ];

    return sensitivePatterns.some(pattern =>
      JSON.stringify(params).match(pattern)
    );
  }
}
```

**4. Network Segmentation**:

```yaml
# Isolated network for MCP servers
services:
  bytebot:
    networks:
      - mcp-internal
      - workspace-access

  spek-agent:
    networks:
      - mcp-internal

networks:
  mcp-internal:
    driver: bridge
    internal: true  # No external internet access
  workspace-access:
    driver: bridge
    internal: false  # Limited external access
```

#### Security Checklist for SPEK v2 Integration

**Pre-Deployment**:
- [ ] Enable Docker Enhanced Container Isolation (ECI)
- [ ] Configure MCP server allowlist (only trusted servers)
- [ ] Implement API gateway with request validation
- [ ] Set up centralized logging to SIEM
- [ ] Enable network segmentation for MCP traffic
- [ ] Sign MCP server containers with developer keys

**Runtime Security**:
- [ ] Monitor for prompt injection patterns
- [ ] Scan tool call parameters for secrets
- [ ] Enforce least privilege for container capabilities
- [ ] Limit file system access (read-only root, writable workspace only)
- [ ] Set resource limits (CPU, memory, file descriptors, processes)
- [ ] Log all automation actions with before/after screenshots

**Compliance and Auditing**:
- [ ] Implement NASA POT10 assertion checks (>=2 per function)
- [ ] Store full audit trail in `.claude/.artifacts/audit/`
- [ ] Generate compliance reports for security reviews
- [ ] Track model attribution with transcript mode (Ctrl+R)
- [ ] Regular security testing (quarterly red team exercises)

---

## Part 2: Performance Optimization (Gap 7)

### 2.1 Optimal Agent Concurrency for SPEK v2

#### Claude Flow Concurrency Capabilities

**Maximum Limits**:
- **Claude Flow Max**: Up to 25 concurrent agents
- **Documented**: 10 concurrent agents for standard deployments
- **Enterprise**: 64-agent system for large-scale orchestration

**SPEK v2 Recommendations**:
- **Target**: 10-15 concurrent agents (optimal balance)
- **Minimum**: 5 agents (development/testing)
- **Maximum**: 20 agents (high-priority tasks)

#### Worker Pool Pattern for Agent Management

**Architecture**:

```typescript
// SPEK v2 Agent Pool Manager
class AgentPoolManager {
  constructor(config = {}) {
    this.poolSize = config.poolSize || 12;  // Default 12 workers
    this.workers = [];
    this.taskQueue = [];
    this.activeWorkers = 0;
  }

  async initialize() {
    // Create worker pool
    for (let i = 0; i < this.poolSize; i++) {
      const worker = new AgentWorker({
        id: `worker-${i}`,
        type: this.assignWorkerType(i)
      });

      this.workers.push(worker);
    }

    console.log(`Initialized ${this.poolSize} agent workers`);
  }

  assignWorkerType(index) {
    // Distribute agent types across pool
    const types = [
      'researcher',     // 2 workers
      'planner',        // 2 workers
      'coder',          // 4 workers
      'tester',         // 2 workers
      'reviewer'        // 2 workers
    ];

    return types[index % types.length];
  }

  async submitTask(task) {
    // Find available worker
    const worker = this.workers.find(w => !w.busy);

    if (worker) {
      this.activeWorkers++;
      await worker.execute(task);
      this.activeWorkers--;
    } else {
      // Queue task if all workers busy
      this.taskQueue.push(task);
    }
  }

  getMetrics() {
    return {
      poolSize: this.poolSize,
      activeWorkers: this.activeWorkers,
      queuedTasks: this.taskQueue.length,
      utilization: (this.activeWorkers / this.poolSize) * 100
    };
  }
}
```

#### Concurrency Optimization Strategies

**1. Dynamic Pool Sizing**:

```javascript
class DynamicAgentPool extends AgentPoolManager {
  adjustPoolSize() {
    const metrics = this.getMetrics();

    // Scale up if high utilization and queue backlog
    if (metrics.utilization > 80 && metrics.queuedTasks > 5) {
      this.scaleUp();
    }

    // Scale down if low utilization
    if (metrics.utilization < 30 && this.poolSize > 5) {
      this.scaleDown();
    }
  }

  scaleUp() {
    const maxSize = 20;  // SPEK v2 max
    if (this.poolSize < maxSize) {
      this.poolSize = Math.min(this.poolSize + 3, maxSize);
      console.log(`Scaled up to ${this.poolSize} workers`);
    }
  }

  scaleDown() {
    const minSize = 5;  // SPEK v2 min
    if (this.poolSize > minSize) {
      this.poolSize = Math.max(this.poolSize - 2, minSize);
      console.log(`Scaled down to ${this.poolSize} workers`);
    }
  }
}
```

**2. Task Prioritization**:

```javascript
class PriorityTaskQueue {
  constructor() {
    this.queues = {
      critical: [],   // P0 tasks
      high: [],       // P1 tasks
      medium: [],     // P2 tasks
      low: []         // P3 tasks
    };
  }

  enqueue(task, priority = 'medium') {
    this.queues[priority].push(task);
  }

  dequeue() {
    // Dequeue from highest priority first
    for (const priority of ['critical', 'high', 'medium', 'low']) {
      if (this.queues[priority].length > 0) {
        return this.queues[priority].shift();
      }
    }
    return null;
  }
}
```

**3. Load Balancing**:

```javascript
class LoadBalancer {
  selectWorker(workers, task) {
    // Filter workers by task type
    const eligible = workers.filter(w =>
      w.capabilities.includes(task.type)
    );

    // Select least loaded worker
    return eligible.reduce((min, worker) =>
      worker.taskCount < min.taskCount ? worker : min
    );
  }
}
```

#### Performance Targets for SPEK v2

**Latency SLOs**:
- Cheap operations (research, planning): <=2.0s p95
- Heavy operations (coding, testing): <=8.0s p95
- Total task completion: <=60s p95

**Throughput Targets**:
- Task completion rate: 10-15 tasks/minute
- Agent utilization: 60-80% (optimal)
- Queue wait time: <5 seconds p95

**Cost Targets**:
- Cost per task: <=$0.60 p95
- Total daily cost: Monitor and alert if >$50/day

### 2.2 Caching Strategies for Repeated Operations

#### Redis Semantic Caching Architecture

**Overview**:
- **Cache Hit Rate**: 31% of LLM queries can be cached
- **Performance Gain**: 3.2x faster response times (389ms vs 1246ms)
- **Cost Reduction**: Significant API call reduction

**Redis Setup for SPEK v2**:

```bash
# docker-compose.yml - Add Redis service
services:
  redis:
    image: redis/redis-stack:latest
    container_name: spek-redis
    ports:
      - "6379:6379"  # Redis
      - "8001:8001"  # RedisInsight UI
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  redis-data:
```

#### Semantic Caching Implementation

**1. Basic Semantic Cache**:

```typescript
import { RedisSemanticCache } from '@langchain/redis';
import { OpenAIEmbeddings } from '@langchain/openai';
import { createClient } from 'redis';

class SPEKSemanticCache {
  constructor() {
    this.client = createClient({
      url: 'redis://localhost:6379'
    });

    this.embeddings = new OpenAIEmbeddings({
      modelName: 'text-embedding-3-small'
    });

    this.cache = new RedisSemanticCache({
      redisClient: this.client,
      embeddings: this.embeddings,
      similarityThreshold: 0.85  // Tune based on accuracy needs
    });
  }

  async initialize() {
    await this.client.connect();
    console.log('Redis semantic cache connected');
  }

  async getCachedResponse(query) {
    // Check semantic cache
    const cached = await this.cache.lookup(query);

    if (cached) {
      console.log('Cache HIT:', query.substring(0, 50));
      return cached;
    }

    console.log('Cache MISS:', query.substring(0, 50));
    return null;
  }

  async cacheResponse(query, response) {
    await this.cache.update(query, response);
  }
}
```

**2. Multi-Level Caching Strategy**:

```javascript
class MultiLevelCache {
  constructor() {
    this.l1Cache = new Map();  // In-memory (fast)
    this.l2Cache = new SPEKSemanticCache();  // Redis (persistent)
    this.l1MaxSize = 100;  // Limit in-memory cache size
  }

  async get(key) {
    // Check L1 (in-memory) first
    if (this.l1Cache.has(key)) {
      console.log('L1 cache HIT');
      return this.l1Cache.get(key);
    }

    // Check L2 (Redis) if L1 miss
    const cached = await this.l2Cache.getCachedResponse(key);
    if (cached) {
      console.log('L2 cache HIT');
      // Promote to L1
      this.setL1(key, cached);
      return cached;
    }

    return null;
  }

  async set(key, value) {
    // Store in both L1 and L2
    this.setL1(key, value);
    await this.l2Cache.cacheResponse(key, value);
  }

  setL1(key, value) {
    // Implement LRU eviction
    if (this.l1Cache.size >= this.l1MaxSize) {
      const firstKey = this.l1Cache.keys().next().value;
      this.l1Cache.delete(firstKey);
    }

    this.l1Cache.set(key, value);
  }
}
```

**3. LMCache Integration for KV Pairs**:

```typescript
// LMCache reduces redundant computation by caching key-value pairs
class LMCacheIntegration {
  constructor(redisClient) {
    this.redis = redisClient;
    this.cachePrefix = 'lmcache:kv:';
  }

  async cacheKVPairs(modelId, tokenChunk, kvPairs) {
    const key = `${this.cachePrefix}${modelId}:${tokenChunk}`;

    await this.redis.set(
      key,
      JSON.stringify(kvPairs),
      'EX',
      3600  // 1 hour TTL
    );
  }

  async getKVPairs(modelId, tokenChunk) {
    const key = `${this.cachePrefix}${modelId}:${tokenChunk}`;
    const cached = await this.redis.get(key);

    return cached ? JSON.parse(cached) : null;
  }
}
```

#### Cache Management Best Practices

**1. Similarity Threshold Tuning**:

```javascript
class CacheThresholdOptimizer {
  constructor() {
    this.metrics = {
      hits: 0,
      misses: 0,
      falsePositives: 0  // Cached but wrong response
    };
  }

  async evaluateThreshold(testQueries, threshold) {
    const cache = new SPEKSemanticCache();
    cache.cache.similarityThreshold = threshold;

    let accuracy = 0;

    for (const query of testQueries) {
      const cached = await cache.getCachedResponse(query.text);

      if (cached) {
        // Check if cached response is correct
        if (this.isCorrectResponse(cached, query.expected)) {
          this.metrics.hits++;
          accuracy++;
        } else {
          this.metrics.falsePositives++;
        }
      } else {
        this.metrics.misses++;
      }
    }

    return {
      threshold,
      accuracy: accuracy / testQueries.length,
      hitRate: this.metrics.hits / testQueries.length,
      falsePositiveRate: this.metrics.falsePositives / testQueries.length
    };
  }
}

// Recommended thresholds:
// - 0.90+: High accuracy, lower cache hits
// - 0.85: Balanced (recommended for SPEK v2)
// - <0.80: Higher cache hits, risk of false positives
```

**2. Cache Invalidation Strategy**:

```javascript
class CacheInvalidator {
  async invalidateByPattern(pattern) {
    // Invalidate caches when source code changes
    const keys = await this.redis.keys(`cache:${pattern}:*`);

    if (keys.length > 0) {
      await this.redis.del(...keys);
      console.log(`Invalidated ${keys.length} cache entries`);
    }
  }

  async invalidateOnFileChange(filepath) {
    // Invalidate related caches when file modified
    const pattern = filepath.replace(/\//g, ':');
    await this.invalidateByPattern(pattern);
  }

  setupFileWatcher() {
    // Watch for file changes
    const watcher = chokidar.watch('src/**/*.{ts,js}', {
      ignored: /node_modules/,
      persistent: true
    });

    watcher.on('change', async (filepath) => {
      console.log(`File changed: ${filepath}`);
      await this.invalidateOnFileChange(filepath);
    });
  }
}
```

**3. Cache Monitoring and Metrics**:

```javascript
class CacheMetrics {
  constructor(redis) {
    this.redis = redis;
  }

  async getStats() {
    const info = await this.redis.info('stats');

    // Parse Redis stats
    const stats = {};
    info.split('\r\n').forEach(line => {
      const [key, value] = line.split(':');
      if (key && value) stats[key] = value;
    });

    return {
      hits: parseInt(stats.keyspace_hits || 0),
      misses: parseInt(stats.keyspace_misses || 0),
      hitRate: this.calculateHitRate(stats),
      memoryUsed: stats.used_memory_human,
      evictedKeys: parseInt(stats.evicted_keys || 0)
    };
  }

  calculateHitRate(stats) {
    const hits = parseInt(stats.keyspace_hits || 0);
    const misses = parseInt(stats.keyspace_misses || 0);
    const total = hits + misses;

    return total > 0 ? (hits / total) * 100 : 0;
  }

  async logMetrics() {
    const stats = await this.getStats();

    console.log('Cache Performance Metrics:');
    console.log(`  Hit Rate: ${stats.hitRate.toFixed(2)}%`);
    console.log(`  Total Hits: ${stats.hits}`);
    console.log(`  Total Misses: ${stats.misses}`);
    console.log(`  Memory Used: ${stats.memoryUsed}`);
    console.log(`  Evicted Keys: ${stats.evictedKeys}`);
  }
}
```

### 2.3 Context Window Management and Sliding Window Implementation

#### Context Window Challenges

**Key Problems**:
1. **Context Bloat**: Filling context window with too much information degrades performance
2. **Token Limits**: Most models have 4K-128K token limits
3. **Cost**: Larger context windows cost more per request
4. **Performance**: Models struggle to differentiate important vs. unimportant information

**SPEK v2 Context Limits**:
- Claude Sonnet 4: 200K tokens (~150K words)
- GPT-5: 128K tokens (~96K words)
- Gemini 2.5 Pro: 1M tokens (~750K words)

#### Sliding Window Implementation

**1. Basic Sliding Window**:

```typescript
class SlidingWindowContext {
  constructor(config = {}) {
    this.maxTokens = config.maxTokens || 8000;  // Conservative limit
    this.windowSize = config.windowSize || 20;  // Keep last 20 messages
    this.messages = [];
  }

  addMessage(message) {
    this.messages.push(message);

    // Slide window if exceeds size
    if (this.messages.length > this.windowSize) {
      this.messages.shift();  // Remove oldest message
    }

    // Check token count
    const totalTokens = this.estimateTokens();
    if (totalTokens > this.maxTokens) {
      this.compressOldMessages();
    }
  }

  estimateTokens() {
    // Rough estimate: 1 token ≈ 4 characters
    const totalChars = this.messages.reduce((sum, msg) =>
      sum + (msg.content?.length || 0), 0
    );

    return Math.ceil(totalChars / 4);
  }

  compressOldMessages() {
    // Keep first message (system prompt) and recent messages
    const systemPrompt = this.messages[0];
    const recentMessages = this.messages.slice(-10);

    // Summarize middle messages
    const middleMessages = this.messages.slice(1, -10);
    const summary = this.summarizeMessages(middleMessages);

    this.messages = [systemPrompt, summary, ...recentMessages];
  }

  summarizeMessages(messages) {
    return {
      role: 'system',
      content: `[Summary of ${messages.length} messages]: ${
        this.generateSummary(messages)
      }`
    };
  }
}
```

**2. Advanced Sliding Window with Semantic Importance**:

```typescript
class SemanticSlidingWindow extends SlidingWindowContext {
  constructor(config) {
    super(config);
    this.importanceScorer = new MessageImportanceScorer();
  }

  async compressOldMessages() {
    // Score all messages by importance
    const scored = await Promise.all(
      this.messages.map(async (msg, idx) => ({
        message: msg,
        index: idx,
        score: await this.importanceScorer.score(msg)
      }))
    );

    // Sort by importance
    scored.sort((a, b) => b.score - a.score);

    // Keep high-importance messages + recent messages
    const keep = new Set();

    // Keep top 10 most important
    scored.slice(0, 10).forEach(s => keep.add(s.index));

    // Keep last 10 messages
    for (let i = this.messages.length - 10; i < this.messages.length; i++) {
      keep.add(i);
    }

    // Filter messages
    this.messages = this.messages.filter((_, idx) => keep.has(idx));
  }
}

class MessageImportanceScorer {
  async score(message) {
    let score = 0;

    // Code blocks are important
    if (message.content?.includes('```')) score += 5;

    // Error messages are important
    if (message.content?.match(/error|exception|failed/i)) score += 4;

    // Decisions and conclusions are important
    if (message.content?.match(/decision|conclusion|summary/i)) score += 3;

    // Questions are moderately important
    if (message.content?.includes('?')) score += 2;

    // Longer messages might be more important
    score += Math.min(message.content?.length / 1000, 3);

    return score;
  }
}
```

**3. Context Pruning with Memory Compression**:

```javascript
class MemoryCompressor {
  constructor() {
    this.compressionRatio = 0.6;  // Target 60% compression
  }

  async compress(messages) {
    const original = JSON.stringify(messages);
    const originalSize = Buffer.byteLength(original, 'utf8');

    // Extract key information
    const compressed = {
      summary: await this.generateSummary(messages),
      keyDecisions: this.extractDecisions(messages),
      codeSnippets: this.extractCode(messages),
      errors: this.extractErrors(messages)
    };

    const compressedSize = Buffer.byteLength(
      JSON.stringify(compressed),
      'utf8'
    );

    console.log(`Compressed ${originalSize} bytes to ${compressedSize} bytes`);
    console.log(`Compression ratio: ${
      (compressedSize / originalSize * 100).toFixed(1)
    }%`);

    return compressed;
  }

  async generateSummary(messages) {
    // Use LLM to generate concise summary
    const text = messages.map(m => m.content).join('\n\n');

    return await this.llm.summarize(text, {
      maxLength: 500,
      focus: 'key decisions and actions taken'
    });
  }

  extractDecisions(messages) {
    return messages
      .map(m => m.content)
      .filter(content =>
        content?.match(/decided|chosen|selected|approved/i)
      )
      .slice(0, 5);  // Keep top 5 decisions
  }

  extractCode(messages) {
    const codeBlocks = [];

    messages.forEach(msg => {
      const matches = msg.content?.matchAll(/```[\s\S]*?```/g);
      if (matches) {
        codeBlocks.push(...Array.from(matches));
      }
    });

    return codeBlocks.slice(-10);  // Keep last 10 code blocks
  }

  extractErrors(messages) {
    return messages
      .map(m => m.content)
      .filter(content =>
        content?.match(/error|exception|failed|rejected/i)
      );
  }
}
```

#### Context Management Best Practices for SPEK v2

**1. Context Budget Allocation**:

```javascript
const CONTEXT_BUDGET = {
  systemPrompt: 2000,      // 25% - Core instructions
  recentHistory: 3000,     // 37.5% - Last 10 messages
  relevantContext: 2000,   // 25% - Retrieved relevant info
  workingMemory: 1000,     // 12.5% - Current task context
  total: 8000              // Conservative limit
};
```

**2. Automatic Context Cleanup**:

```javascript
class ContextManager {
  async cleanup() {
    const currentTokens = this.estimateTokens();

    if (currentTokens > CONTEXT_BUDGET.total * 0.8) {
      console.log('Context approaching limit, cleaning up...');

      // Compress old messages
      await this.compressOldMessages();

      // Clear working memory if needed
      if (this.estimateTokens() > CONTEXT_BUDGET.total * 0.9) {
        this.clearWorkingMemory();
      }
    }
  }
}
```

**3. Retrieval-Augmented Context**:

```javascript
class RAGContextManager extends ContextManager {
  constructor(vectorStore) {
    super();
    this.vectorStore = vectorStore;  // For semantic search
  }

  async getRelevantContext(query) {
    // Retrieve only relevant information
    const relevant = await this.vectorStore.similaritySearch(
      query,
      k: 5  // Top 5 most relevant documents
    );

    // Add to context within budget
    const contextText = relevant
      .map(doc => doc.pageContent)
      .join('\n\n');

    if (this.estimateTokens(contextText) > CONTEXT_BUDGET.relevantContext) {
      // Truncate if exceeds budget
      return this.truncateToTokenLimit(
        contextText,
        CONTEXT_BUDGET.relevantContext
      );
    }

    return contextText;
  }
}
```

---

## Part 3: Integration Recommendations for SPEK v2

### 3.1 Combined Architecture

**Recommended SPEK v2 Stack**:

```yaml
# docker-compose.yml for SPEK v2
version: '3.8'

services:
  # Redis for caching
  redis:
    image: redis/redis-stack:latest
    ports:
      - "6379:6379"
      - "8001:8001"
    volumes:
      - redis-data:/data
    restart: unless-stopped

  # Bytebot for desktop automation
  bytebot:
    image: bytebot/bytebot:latest
    ports:
      - "9990:9990"
      - "9991:9991"
      - "9992:9992"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - bytebot-workspace:/workspace
      - ./evidence:/workspace/evidence
    security_opt:
      - no-new-privileges:true
      - seccomp:unconfined
    cap_drop:
      - ALL
    cap_add:
      - SYS_ADMIN
    networks:
      - spek-internal
    restart: unless-stopped

  # SPEK v2 orchestrator
  spek-orchestrator:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379
      - BYTEBOT_API_URL=http://bytebot:9990
      - AGENT_POOL_SIZE=12
    depends_on:
      - redis
      - bytebot
    networks:
      - spek-internal
    restart: unless-stopped

networks:
  spek-internal:
    driver: bridge

volumes:
  redis-data:
  bytebot-workspace:
```

### 3.2 Performance Monitoring

**Key Metrics to Track**:

```typescript
interface SPEKMetrics {
  agentPool: {
    activeWorkers: number;
    poolSize: number;
    queueDepth: number;
    utilization: number;
  };

  cache: {
    hitRate: number;
    missRate: number;
    size: number;
    evictions: number;
  };

  context: {
    averageTokens: number;
    compressionRatio: number;
    pruneCount: number;
  };

  bytebot: {
    screenshotCount: number;
    automationLatency: number;
    errorRate: number;
  };

  overall: {
    taskCompletionRate: number;
    averageLatency: number;
    costPerTask: number;
  };
}
```

**Monitoring Dashboard**:

```javascript
class SPEKMonitor {
  async collectMetrics() {
    const metrics = {
      timestamp: new Date().toISOString(),
      agentPool: await this.agentPool.getMetrics(),
      cache: await this.cache.getStats(),
      context: await this.contextManager.getStats(),
      bytebot: await this.bytebot.getStats(),
      overall: await this.calculateOverallMetrics()
    };

    // Store metrics
    await this.storeMetrics(metrics);

    // Check SLO violations
    await this.checkSLOs(metrics);

    return metrics;
  }

  async checkSLOs(metrics) {
    const violations = [];

    // Check agent pool utilization
    if (metrics.agentPool.utilization > 90) {
      violations.push('Agent pool over-utilized (>90%)');
    }

    // Check cache hit rate
    if (metrics.cache.hitRate < 25) {
      violations.push('Cache hit rate below target (<25%)');
    }

    // Check average latency
    if (metrics.overall.averageLatency > 8000) {
      violations.push('Average latency exceeds 8s');
    }

    if (violations.length > 0) {
      await this.alertTeam(violations);
    }
  }
}
```

### 3.3 Cost Optimization

**Cost Breakdown**:

```javascript
class CostTracker {
  async calculateCosts(metrics) {
    const costs = {
      // Model API costs
      claude: metrics.claudeCalls * 0.015,  // $0.015 per call
      gpt5: metrics.gpt5Calls * 0.03,       // $0.03 per call
      gemini: metrics.geminiCalls * 0.00075, // $0.00075 per call

      // Infrastructure costs (monthly, prorated)
      redis: 20 / 30 / 24,  // $20/month
      bytebot: 0,  // Self-hosted

      // Total
      total: 0
    };

    costs.total = costs.claude + costs.gpt5 + costs.gemini +
                  costs.redis + costs.bytebot;

    return costs;
  }

  async optimizeCosts() {
    // Use cache to reduce API calls
    const cacheSavings = this.cache.hitRate * 0.31 *
                         this.averageCallsPerDay * 0.015;

    // Use cheaper models when possible
    const modelOptimization = this.routeToOptimalModel();

    console.log(`Daily cost savings from caching: $${cacheSavings.toFixed(2)}`);
  }
}
```

---

## Part 4: Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Set up Redis for caching
- [ ] Deploy Bytebot with Docker Compose
- [ ] Configure MCP bridge integration
- [ ] Implement basic agent pool (5 workers)

### Phase 2: Caching Layer (Week 2)
- [ ] Implement semantic caching with Redis
- [ ] Add multi-level cache (L1 + L2)
- [ ] Set up cache invalidation on file changes
- [ ] Configure cache monitoring and metrics

### Phase 3: Context Management (Week 2-3)
- [ ] Implement sliding window context
- [ ] Add semantic importance scoring
- [ ] Build memory compression system
- [ ] Integrate RAG for relevant context retrieval

### Phase 4: Agent Concurrency (Week 3)
- [ ] Expand agent pool to 12 workers
- [ ] Implement dynamic pool scaling
- [ ] Add task prioritization
- [ ] Configure load balancing

### Phase 5: Security Hardening (Week 4)
- [ ] Enable Docker Enhanced Container Isolation
- [ ] Implement MCP security gateway
- [ ] Set up comprehensive logging and monitoring
- [ ] Configure network segmentation

### Phase 6: Performance Optimization (Week 4)
- [ ] Tune cache similarity thresholds
- [ ] Optimize context pruning strategies
- [ ] Implement performance monitoring dashboard
- [ ] Run load tests and adjust configurations

### Phase 7: Production Readiness (Week 5)
- [ ] Complete security checklist
- [ ] Set up SLO monitoring and alerts
- [ ] Implement cost tracking and optimization
- [ ] Document operational procedures

---

## Part 5: Quick Reference

### Key Configuration Values

| Component | Parameter | Recommended Value |
|-----------|-----------|-------------------|
| Agent Pool | Pool Size | 12 workers |
| Agent Pool | Min Size | 5 workers |
| Agent Pool | Max Size | 20 workers |
| Agent Pool | Scale Up Threshold | >80% utilization |
| Agent Pool | Scale Down Threshold | <30% utilization |
| Cache | Similarity Threshold | 0.85 |
| Cache | L1 Max Size | 100 entries |
| Cache | TTL | 3600s (1 hour) |
| Cache | Target Hit Rate | >25% |
| Context | Max Tokens | 8000 tokens |
| Context | Window Size | 20 messages |
| Context | Compression Ratio | 60% |
| Bytebot | API Port | 9990 |
| Bytebot | Web UI Port | 9992 |
| Performance | P95 Latency (cheap) | <2.0s |
| Performance | P95 Latency (heavy) | <8.0s |
| Cost | Per Task Target | <$0.60 |

### Essential Commands

```bash
# Start SPEK v2 stack
docker-compose up -d

# Check agent pool status
curl http://localhost:3000/api/metrics/agent-pool

# Check cache performance
curl http://localhost:3000/api/metrics/cache

# Capture screenshot via Bytebot
curl http://localhost:9990/api/screenshot

# Monitor Redis cache
redis-cli info stats

# Scale agent pool
curl -X POST http://localhost:3000/api/agent-pool/scale \
  -H "Content-Type: application/json" \
  -d '{"poolSize": 15}'
```

### Troubleshooting Guide

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| High latency | Agent pool saturated | Scale up pool size |
| Low cache hit rate | Threshold too strict | Lower to 0.80-0.85 |
| Context overflow | Too much history | Increase compression |
| Bytebot connection failed | Port not exposed | Check docker-compose ports |
| Memory exhaustion | L1 cache too large | Reduce L1 max size |
| Cost overruns | Too many API calls | Increase cache usage |

---

## Conclusion

This research provides practical, implementation-focused guidance for integrating Bytebot desktop automation and performance optimization into SPEK v2. Key takeaways:

**Bytebot Integration**:
- Use Docker Compose with port 9990 for REST/MCP API
- Automatic screenshot evidence collection for all actions
- Enhanced Container Isolation (ECI) for security
- MCP bridge provides structured desktop automation

**Performance Optimization**:
- Target 10-15 concurrent agents (pool-based architecture)
- Redis semantic caching for 31% query reduction and 3.2x speedup
- Sliding window context management with 60% compression
- Multi-level caching (L1 in-memory + L2 Redis)

**Next Steps**:
1. Follow Phase 1-7 implementation roadmap
2. Start with 5-agent pool, scale to 12 based on load
3. Monitor key metrics: utilization, cache hit rate, latency, cost
4. Iterate on cache thresholds and pool sizing based on real usage

This completes the P2 research gaps analysis. The implementation guidance is actionable and sized appropriately for SPEK v2 requirements.

---

<!-- AGENT FOOTER BEGIN: DO NOT EDIT ABOVE THIS LINE -->
## Version & Run Log
| Version | Timestamp | Agent/Model | Change Summary | Artifacts | Status | Notes | Cost | Hash |
|--------:|-----------|-------------|----------------|-----------|--------|-------|------|------|
| 1.0.0   | 2025-10-08T15:42:00-04:00 | researcher@Claude-Sonnet-4.5 | Initial P2 research on Bytebot automation and performance optimization | p2-gaps-research-v1.md | OK | Practical implementation guide | 0.00 | a7f9e2c |

### Receipt
- status: OK
- reason_if_blocked: --
- run_id: p2-research-20251008-154200
- inputs: ["WebSearch: Bytebot Docker", "WebSearch: Claude Flow concurrency", "WebSearch: MCP security", "WebSearch: context management", "WebSearch: Redis caching", "WebSearch: agent concurrency", "WebSearch: Bytebot API"]
- tools_used: ["WebSearch", "Write"]
- versions: {"model":"Claude-Sonnet-4.5","prompt":"researcher-agent-v1"}
<!-- AGENT FOOTER END: DO NOT EDIT BELOW THIS LINE -->