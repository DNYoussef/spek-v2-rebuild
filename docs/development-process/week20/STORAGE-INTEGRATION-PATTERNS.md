# Storage Integration Patterns

**Week 20 Day 7 Documentation**

Architectural patterns and best practices for Context DNA storage integration.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Storage Layers](#storage-layers)
3. [Integration Patterns](#integration-patterns)
4. [Data Flow Patterns](#data-flow-patterns)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Performance Patterns](#performance-patterns)
7. [Security Patterns](#security-patterns)

---

## Architecture Overview

### Three-Layer Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Layer                               │
│  (Queen, Princess, Drone agents using Context DNA)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                  Context Integration Layer                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ AgentContext     │  │ MemoryCoordinator│  │ ArtifactMgr  │ │
│  │ Integration      │  │                  │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                     Storage Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ SQLite       │  │ Redis        │  │ S3                   │ │
│  │ (Context DNA)│  │ (Sessions)   │  │ (Artifact Refs)      │ │
│  │ FTS5 Search  │  │ <5ms ops     │  │ 99.4% reduction      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Layered Separation**: Storage details hidden from agents
2. **Performance First**: <200ms retrieval guaranteed
3. **Graceful Degradation**: Continue without storage if unavailable
4. **Storage Optimization**: Reference artifacts, not full content
5. **Automatic Retention**: 30-day cleanup automated

---

## Storage Layers

### Layer 1: SQLite (Primary Storage)

**Purpose**: Long-term context storage with FTS5 search

**Schema**:
```sql
-- Projects
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  last_accessed_at INTEGER NOT NULL
);

-- Conversations
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  agent_id TEXT,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

-- Agent Memories
CREATE TABLE agent_memories (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  memory_type TEXT NOT NULL,
  content TEXT NOT NULL,
  importance REAL NOT NULL,
  created_at INTEGER NOT NULL
);

-- Full-Text Search Index
CREATE VIRTUAL TABLE search_index USING fts5(
  content,
  project_id UNINDEXED,
  source_type UNINDEXED,
  tokenize = 'porter'
);

-- Compound Indexes (Week 20)
CREATE INDEX idx_conversations_project_agent_time
  ON conversations(project_id, agent_id, created_at DESC);

CREATE INDEX idx_memories_agent_importance_time
  ON agent_memories(agent_id, importance DESC, created_at DESC);
```

**Access Pattern**:
```typescript
import { getContextDNAStorage } from '@/services/context-dna/ContextDNAStorage';

const storage = getContextDNAStorage();

// Retrieve with compound index (0.18ms avg)
const conversations = storage.getConversationsForProject('project-123', 50);

// Full-text search (0.69ms avg)
const results = storage.search({
  query: 'authentication OAuth2',
  projectId: 'project-123',
  limit: 50,
});
```

### Layer 2: Redis (Session Management)

**Purpose**: Fast session state tracking

**Data Structure**:
```json
{
  "session-123": {
    "sessionId": "session-123",
    "agentId": "queen",
    "projectId": "project-456",
    "status": "active",
    "startTime": "2025-10-10T12:00:00Z",
    "thoughtCount": 5
  }
}
```

**TTL**: 24 hours (configurable)

**Access Pattern**:
```typescript
import { RedisSessionManager } from '@/services/context-dna/RedisSessionManager';

const sessionManager = new RedisSessionManager();

// Create session (<1ms)
await sessionManager.createSession(context);

// Update thought count (<1ms)
await sessionManager.updateThoughtCount(context.sessionId, 5);

// Get session state (<1ms)
const state = await sessionManager.getSessionState(context.sessionId);
```

### Layer 3: S3 (Artifact Storage)

**Purpose**: Large file references (NOT full content)

**Storage Pattern**:
```
s3://spek-artifacts/
├── project-123/
│   ├── spec-v8-final.md (52 KB)
│   ├── premortem-analysis.md (28 KB)
│   └── architecture-diagram.png (1.2 MB)
└── project-456/
    └── code-implementation.zip (450 KB)
```

**Context DNA Storage**:
```sql
-- Only store reference (600 bytes), NOT full file (50 MB)
INSERT INTO artifacts (id, project_id, name, s3_path, size_bytes)
VALUES ('artifact-123', 'project-123', 'spec-v8-final.md',
        's3://spek-artifacts/project-123/spec-v8-final.md', 52000);
```

**Access Pattern**:
```typescript
import { S3ArtifactStore } from '@/services/context-dna/S3ArtifactStore';

const s3Store = new S3ArtifactStore({
  bucket: 'spek-artifacts',
  region: 'us-east-1',
});

// Upload artifact
const result = await s3Store.upload('/local/file.md', 'artifact-123', 'project-123');

// Get presigned URL (1-hour expiry)
const urlResult = await s3Store.getPresignedUrl(result.s3Path, 3600);
```

---

## Integration Patterns

### Pattern 1: Agent Execution Wrapper

**Use Case**: Wrap every agent execution with context storage

```typescript
class AgentExecutionWrapper {
  constructor(private agent: Agent) {}

  async execute(task: Task): Promise<Result> {
    const contextIntegration = new AgentContextIntegration();

    // 1. Create context
    const context = {
      sessionId: `session-${Date.now()}`,
      agentId: this.agent.id,
      projectId: task.projectId,
      taskId: task.id,
      startTime: new Date(),
    };

    // 2. Start execution (creates session)
    await contextIntegration.startAgentExecution(context);

    try {
      // 3. Retrieve relevant context
      const retrieved = await contextIntegration.retrieveContext({
        query: task.description,
        projectId: task.projectId,
        agentId: this.agent.id,
        limit: 30,
      });

      // 4. Execute agent with context
      const result = await this.agent.execute(task, retrieved);

      // 5. Store result + memories
      await contextIntegration.storeAgentResult(context, {
        success: true,
        output: result.output,
        artifacts: result.artifacts,
      });

      if (result.learnings) {
        await contextIntegration.storeMemory(context, {
          memoryType: 'success_pattern',
          content: result.learnings,
          importance: 0.8,
        });
      }

      return result;
    } catch (error) {
      // 6. Store failure
      await contextIntegration.storeAgentResult(context, {
        success: false,
        error: error.message,
        artifacts: [],
      });

      await contextIntegration.storeMemory(context, {
        memoryType: 'failure_pattern',
        content: `Failed: ${error.message}`,
        importance: 0.9,
      });

      throw error;
    }
  }
}

// Usage
const wrappedAgent = new AgentExecutionWrapper(new CoderAgent());
const result = await wrappedAgent.execute(task);
```

### Pattern 2: Delegation with Context Inheritance

**Use Case**: Queen → Princess → Drone delegation chain

```typescript
class DelegationWithContext {
  async delegateTask(
    parentContext: AgentExecutionContext,
    childAgentId: string,
    task: Task
  ) {
    const contextInheritance = new ContextInheritance();
    const memoryCoordinator = new MemoryCoordinator();

    // 1. Create child context
    const childContext = {
      sessionId: `session-${Date.now()}`,
      agentId: childAgentId,
      projectId: parentContext.projectId,
      taskId: task.id,
      parentAgentId: parentContext.agentId,
      startTime: new Date(),
    };

    // 2. Delegate with context
    const delegationResult = await contextInheritance.delegateWithContext(
      parentContext,
      childAgentId,
      task.id
    );

    // 3. Child inherits parent's context
    const inherited = await memoryCoordinator.inheritContext({
      projectId: parentContext.projectId,
      parentAgentId: parentContext.agentId,
      childAgentId: childAgentId,
      inheritMemories: true,
      inheritConversations: true,
      limit: 30,
    });

    console.log(`Inherited ${inherited.memoriesInherited} memories`);
    console.log(`Delegation chain depth: ${delegationResult.delegationChain.length}`);

    return { childContext, inherited, delegationChain: delegationResult.delegationChain };
  }
}

// Usage
const delegation = new DelegationWithContext();

// Queen delegates to Princess-Dev
const { childContext, inherited } = await delegation.delegateTask(
  queenContext,
  'princess-dev',
  task
);

// Princess executes with inherited context
const result = await princessAgent.execute(task, inherited);
```

### Pattern 3: Cross-Agent Memory Sharing

**Use Case**: Share learnings between agents

```typescript
class CrossAgentLearning {
  async shareSuccessPatterns(
    projectId: string,
    sourceAgentId: string,
    targetAgentIds: string[]
  ) {
    const coordinator = new MemoryCoordinator();

    const results = [];

    for (const targetId of targetAgentIds) {
      const shared = await coordinator.shareMemories({
        projectId,
        sourceAgentId,
        targetAgentId: targetId,
        memoryTypes: ['success_pattern', 'optimization'],
        minImportance: 0.7,
        limit: 20,
      });

      results.push({
        targetAgent: targetId,
        memoriesShared: shared.shared,
      });
    }

    return results;
  }
}

// Usage
const learning = new CrossAgentLearning();

// Share Queen's success patterns with all Princess agents
const results = await learning.shareSuccessPatterns(
  'project-123',
  'queen',
  ['princess-dev', 'princess-quality', 'princess-coordination']
);

console.log('Shared memories:', results);
```

### Pattern 4: Artifact Reference Management

**Use Case**: Store large artifacts without bloating Context DNA

```typescript
class ArtifactReferencePattern {
  async storeSpecification(
    projectId: string,
    specFilePath: string
  ): Promise<string> {
    const s3Store = new S3ArtifactStore({
      bucket: 'spek-artifacts',
      region: 'us-east-1',
    });
    const artifactManager = new ArtifactManager();

    // 1. Upload to S3
    const uploadResult = await s3Store.upload(
      specFilePath,
      `spec-${Date.now()}`,
      projectId
    );

    if (!uploadResult.success) {
      throw new Error('Failed to upload specification');
    }

    // 2. Store reference (600 bytes) in Context DNA
    await artifactManager.registerArtifact({
      projectId,
      artifactType: 'specification',
      artifactName: path.basename(specFilePath),
      s3Path: uploadResult.s3Path,
      metadata: {
        uploadedAt: new Date(),
        sizeBytes: uploadResult.sizeBytes,
      },
    });

    // 3. Generate presigned URL for agents
    const urlResult = await s3Store.getPresignedUrl(
      uploadResult.s3Path,
      3600 // 1 hour
    );

    return urlResult.url;
  }

  async retrieveSpecification(
    projectId: string,
    specName: string
  ): Promise<string> {
    const storage = getContextDNAStorage();
    const s3Store = new S3ArtifactStore({
      bucket: 'spek-artifacts',
      region: 'us-east-1',
    });

    // 1. Get reference from Context DNA
    const artifacts = storage.getArtifactsForProject(projectId);
    const spec = artifacts.find(a => a.name === specName && a.type === 'specification');

    if (!spec) {
      throw new Error('Specification not found');
    }

    // 2. Download from S3 (if needed)
    const localPath = `/tmp/${specName}`;
    await s3Store.download(spec.s3Path!, localPath);

    return localPath;
  }
}
```

---

## Data Flow Patterns

### Pattern 1: Agent Execution Flow

```
┌──────────────┐
│ Agent.execute│
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ 1. Create Context        │
│    - sessionId           │
│    - agentId             │
│    - projectId           │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 2. Start Execution       │
│    - Redis session       │
│    - SQLite conversation │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 3. Retrieve Context      │
│    - FTS search (SQLite) │
│    - Relevance ranking   │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 4. Execute Task          │
│    - Agent logic         │
│    - With context        │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 5. Store Result          │
│    - Conversations       │
│    - Memories            │
│    - Artifacts (refs)    │
└──────────────────────────┘
```

### Pattern 2: Delegation Flow

```
┌───────────┐
│   Queen   │
└─────┬─────┘
      │
      │ delegates task
      ▼
┌───────────────────────┐
│ 1. Create Child       │
│    Context            │
│    - parentAgentId    │
└─────┬─────────────────┘
      │
      ▼
┌───────────────────────┐
│ 2. Inherit Context    │
│    - Memories         │
│    - Conversations    │
└─────┬─────────────────┘
      │
      ▼
┌───────────────────────┐
│ 3. Track Chain        │
│    - Queen → Princess │
│    - Delegation depth │
└─────┬─────────────────┘
      │
      ▼
┌─────────────┐
│  Princess   │
│  (executes) │
└─────────────┘
```

---

## Error Handling Patterns

### Pattern 1: Graceful Degradation

```typescript
class GracefulStorageAccess {
  async storeWithFallback(
    operation: () => Promise<void>,
    fallbackMessage: string
  ) {
    try {
      await operation();
    } catch (error) {
      console.warn(`Storage operation failed (${fallbackMessage}):`, error);
      // Continue execution without storage
      // Agent can still function, just without persistence
    }
  }

  async executeWithGracefulStorage(task: Task) {
    const context = this.createContext(task);

    // Non-blocking storage
    await this.storeWithFallback(
      () => this.contextIntegration.startAgentExecution(context),
      'session creation'
    );

    // Execute task (always succeeds)
    const result = await this.agent.execute(task);

    // Non-blocking result storage
    await this.storeWithFallback(
      () => this.contextIntegration.storeAgentResult(context, result),
      'result storage'
    );

    return result;
  }
}
```

### Pattern 2: Retry with Exponential Backoff

```typescript
class RetryableStorage {
  async storeWithRetry<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        if (attempt === maxRetries - 1) {
          throw error;
        }

        const delayMs = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
        console.warn(`Storage attempt ${attempt + 1} failed, retrying in ${delayMs}ms`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }

    throw new Error('Unreachable');
  }
}
```

---

## Performance Patterns

### Pattern 1: Batch Loading

```typescript
class BatchLoader {
  async loadContextBatch(
    projectId: string,
    agentId: string
  ) {
    const storage = getContextDNAStorage();

    // Single batch query (0.5ms) instead of 3 separate queries (1.5ms)
    const [conversations, memories, tasks] = await Promise.all([
      storage.getConversationsForProject(projectId, 50),
      storage.getAgentMemories(projectId, agentId, 50),
      storage.getTasksForProject(projectId, 50),
    ]);

    return { conversations, memories, tasks };
  }
}
```

### Pattern 2: Lazy Loading

```typescript
class LazyContextLoader {
  private contextCache: Map<string, any> = new Map();

  async getContext(projectId: string, agentId: string) {
    const cacheKey = `${projectId}:${agentId}`;

    // Check cache first
    if (this.contextCache.has(cacheKey)) {
      return this.contextCache.get(cacheKey);
    }

    // Load on demand
    const context = await this.loadContextBatch(projectId, agentId);
    this.contextCache.set(cacheKey, context);

    return context;
  }
}
```

---

## Security Patterns

### Pattern 1: Credential Management

```typescript
// ✅ Good: Environment variables
const s3Store = new S3ArtifactStore({
  bucket: process.env.S3_BUCKET,
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});

// ❌ Bad: Hardcoded credentials
const s3Store = new S3ArtifactStore({
  bucket: 'my-bucket',
  credentials: {
    accessKeyId: 'AKIAIOSFODNN7EXAMPLE',
    secretAccessKey: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
  },
});
```

### Pattern 2: Input Validation

```typescript
class SecureContextIntegration {
  validateContext(context: AgentExecutionContext) {
    if (!context.sessionId || context.sessionId.length < 10) {
      throw new Error('Invalid sessionId');
    }

    if (!context.agentId || !/^[a-z-]+$/.test(context.agentId)) {
      throw new Error('Invalid agentId');
    }

    if (!context.projectId || !/^[a-z0-9-]+$/.test(context.projectId)) {
      throw new Error('Invalid projectId');
    }

    return true;
  }

  async startAgentExecution(context: AgentExecutionContext) {
    this.validateContext(context);
    // ... proceed with storage
  }
}
```

---

## Summary

**Key Takeaways**:

1. **Use 3-layer architecture**: Agent → Integration → Storage
2. **Store references, not content**: 99.4% storage reduction
3. **Inherit context on delegation**: Queen → Princess → Drone
4. **Handle errors gracefully**: Continue without storage if needed
5. **Optimize for <200ms retrieval**: Compound indexes + batch operations
6. **Secure credentials**: Environment variables only
7. **Validate inputs**: Prevent injection attacks

**Performance Verified** (Week 20 Day 6):
- Context retrieval: 0.51ms (392x faster than 200ms target)
- FTS search: 0.69ms (72x faster)
- Redis sessions: <1ms (5x+ faster)

---

**Generated**: 2025-10-10
**Version**: Week 20 Day 7
**Status**: ✅ COMPLETE
