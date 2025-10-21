# Context DNA Usage Guide

**Week 20 Day 7 Documentation**

Complete guide for integrating Context DNA storage into agent workflows.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Agent Integration](#agent-integration)
4. [Memory Coordination](#memory-coordination)
5. [Artifact Management](#artifact-management)
6. [Performance Optimization](#performance-optimization)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

---

## Quick Start

### Installation

Context DNA is built into Atlantis UI (Week 20+). No additional installation required.

### Basic Usage

```typescript
import { AgentContextIntegration } from '@/services/context-dna/AgentContextIntegration';

const contextIntegration = new AgentContextIntegration();

// Start agent execution
const context = {
  sessionId: 'session-abc123',
  agentId: 'queen',
  projectId: 'project-123',
  startTime: new Date(),
};

await contextIntegration.startAgentExecution(context);

// Store conversation
await contextIntegration.storeConversation(context, {
  role: 'agent',
  content: 'Agent execution started',
});

// Store agent result
await contextIntegration.storeAgentResult(context, {
  success: true,
  output: 'Task completed',
  artifacts: [],
});
```

---

## Core Concepts

### 1. Context DNA Storage

**Purpose**: 30-day retention of project context, task history, and agent conversations.

**Components**:
- **SQLite**: Primary storage with FTS5 full-text search
- **Redis**: Session management (<5ms operations)
- **S3**: Artifact storage (references only, not full files)

**Key Features**:
- ✅ <200ms context retrieval
- ✅ 30-day automatic retention
- ✅ Cross-agent memory sharing
- ✅ 99.4% storage optimization (S3 references)

### 2. Agent Execution Context

Every agent execution requires a context:

```typescript
interface AgentExecutionContext {
  sessionId: string;        // Unique session identifier
  agentId: string;          // Agent performing the task
  projectId: string;        // Project being worked on
  taskId?: string;          // Optional task identifier
  parentAgentId?: string;   // For delegation chains
  startTime: Date;          // Execution start timestamp
}
```

### 3. Memory Types

Agents store four types of memories:

1. **success_pattern**: Successful approaches and patterns
2. **failure_pattern**: Failed attempts and lessons learned
3. **optimization**: Performance improvements and optimizations
4. **context**: General project context and insights

### 4. Delegation Chains

Queen → Princess → Drone hierarchy tracked automatically:

```typescript
// Queen delegates to Princess
await contextInheritance.delegateWithContext(queenContext, 'princess-dev', taskId);

// Princess inherits Queen's context
const inherited = await memoryCoordinator.inheritContext({
  projectId: 'project-123',
  parentAgentId: 'queen',
  childAgentId: 'princess-dev',
  inheritMemories: true,
  inheritConversations: true,
});
```

---

## Agent Integration

### Step 1: Initialize Context Integration

```typescript
import { AgentContextIntegration } from '@/services/context-dna/AgentContextIntegration';

class YourAgent {
  private contextIntegration = new AgentContextIntegration();

  async execute(task: Task) {
    const context = {
      sessionId: `session-${Date.now()}`,
      agentId: this.agentId,
      projectId: task.projectId,
      taskId: task.id,
      startTime: new Date(),
    };

    // Start execution
    await this.contextIntegration.startAgentExecution(context);

    try {
      // Your agent logic here
      const result = await this.performTask(task);

      // Store result
      await this.contextIntegration.storeAgentResult(context, {
        success: true,
        output: result,
        artifacts: [],
      });
    } catch (error) {
      // Store failure
      await this.contextIntegration.storeAgentResult(context, {
        success: false,
        error: error.message,
        artifacts: [],
      });
    }
  }
}
```

### Step 2: Store Conversations

```typescript
// User message
await contextIntegration.storeConversation(context, {
  role: 'user',
  content: 'Please implement the login feature',
});

// Agent response
await contextIntegration.storeConversation(context, {
  role: 'agent',
  content: 'I will implement the login feature using OAuth2',
});

// System message
await contextIntegration.storeConversation(context, {
  role: 'system',
  content: 'Task assigned to agent: coder',
});
```

### Step 3: Store Agent Memories

```typescript
// Success pattern
await contextIntegration.storeMemory(context, {
  memoryType: 'success_pattern',
  content: 'Breaking complex tasks into 3-5 subtasks improved success rate',
  importance: 0.9,
});

// Failure pattern
await contextIntegration.storeMemory(context, {
  memoryType: 'failure_pattern',
  content: 'Attempting to implement without specification led to rework',
  importance: 0.8,
});

// Optimization
await contextIntegration.storeMemory(context, {
  memoryType: 'optimization',
  content: 'Using TypeScript strict mode caught 15 bugs early',
  importance: 0.85,
});
```

### Step 4: Retrieve Context Before Execution

```typescript
// Retrieve relevant context before starting work
const retrieved = await contextIntegration.retrieveContext({
  query: 'authentication implementation OAuth2',
  projectId: context.projectId,
  agentId: context.agentId,
  limit: 50,
});

console.log(`Found ${retrieved.conversations.length} relevant conversations`);
console.log(`Found ${retrieved.memories.length} relevant memories`);
console.log(`Found ${retrieved.tasks.length} related tasks`);
```

---

## Memory Coordination

### Cross-Agent Memory Sharing

Share memories between agents:

```typescript
import { MemoryCoordinator } from '@/services/context-dna/MemoryCoordinator';

const coordinator = new MemoryCoordinator();

// Share Queen's success patterns with Princess-Dev
const shared = await coordinator.shareMemories({
  projectId: 'project-123',
  sourceAgentId: 'queen',
  targetAgentId: 'princess-dev',
  memoryTypes: ['success_pattern', 'optimization'],
  minImportance: 0.7,
  limit: 20,
});

console.log(`Shared ${shared.shared} memories`);
```

### Context Inheritance

Inherit context when delegating:

```typescript
// Queen delegates to Princess with context inheritance
const inheritResult = await coordinator.inheritContext({
  projectId: 'project-123',
  parentAgentId: 'queen',
  childAgentId: 'princess-dev',
  inheritMemories: true,
  inheritConversations: true,
  limit: 50,
});

console.log(`Inherited ${inheritResult.memoriesInherited} memories`);
console.log(`Inherited ${inheritResult.conversationsInherited} conversations`);
```

### Search Across All Agents

```typescript
// Find all relevant context across all agents
const searchResult = await coordinator.searchContext('authentication OAuth2', {
  projectId: 'project-123',
  memoryTypes: ['success_pattern'],
  importance: { min: 0.7 },
  dateRange: {
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // Last 7 days
  },
});

console.log(`Found ${searchResult.totalResults} results`);
```

---

## Artifact Management

### Register Artifact References

**Important**: Store S3 references, NOT full files (99.4% storage reduction)

```typescript
import { ArtifactManager } from '@/services/context-dna/ArtifactManager';

const artifactManager = new ArtifactManager();

// Register specification artifact
const registered = await artifactManager.registerArtifact({
  projectId: 'project-123',
  artifactType: 'specification',
  artifactName: 'SPEC-v8-FINAL.md',
  s3Path: 's3://spek-artifacts/project-123/spec-v8-final.md',
  metadata: {
    version: 'v8',
    author: 'spec-writer',
    wordCount: 12500,
  },
});
```

### Upload to S3

```typescript
import { S3ArtifactStore } from '@/services/context-dna/S3ArtifactStore';

const s3Store = new S3ArtifactStore({
  bucket: 'spek-artifacts',
  region: 'us-east-1',
  useFallback: false, // Set to true for local fallback
});

// Upload artifact
const uploadResult = await s3Store.upload(
  '/path/to/local/file.md',
  'artifact-123',
  'project-123'
);

if (uploadResult.success) {
  console.log(`Uploaded ${uploadResult.sizeBytes} bytes to ${uploadResult.s3Path}`);

  // Register the reference in Context DNA
  await artifactManager.registerArtifact({
    projectId: 'project-123',
    artifactType: 'specification',
    artifactName: 'file.md',
    s3Path: uploadResult.s3Path,
    metadata: { uploadedAt: new Date() },
  });
}
```

### Download from S3

```typescript
// Download artifact
const downloadResult = await s3Store.download(
  's3://spek-artifacts/project-123/spec-v8-final.md',
  '/path/to/local/destination.md'
);

if (downloadResult.success) {
  console.log(`Downloaded ${downloadResult.sizeBytes} bytes`);
}
```

### Generate Presigned URLs

```typescript
// Generate presigned URL for browser download (1 hour expiry)
const urlResult = await s3Store.getPresignedUrl(
  's3://spek-artifacts/project-123/spec-v8-final.md',
  3600 // 1 hour
);

if (urlResult.success) {
  console.log(`Download URL: ${urlResult.url}`);
  console.log(`Expires at: ${urlResult.expiresAt}`);
}
```

---

## Performance Optimization

### 1. Use Compound Indexes

Context DNA includes compound indexes for <200ms retrieval:

```sql
-- Conversations: project + agent + time
CREATE INDEX idx_conversations_project_agent_time
  ON conversations(project_id, agent_id, created_at DESC);

-- Tasks: project + status + time
CREATE INDEX idx_tasks_project_status_time
  ON tasks(project_id, status, created_at DESC);

-- Memories: agent + importance + time
CREATE INDEX idx_memories_agent_importance_time
  ON agent_memories(agent_id, importance DESC, created_at DESC);
```

**Performance**: 0.18ms average query time (555x faster than 100ms target)

### 2. Limit Result Sets

Always specify limits to prevent large result sets:

```typescript
// Good: Limited results
const context = await contextIntegration.retrieveContext({
  query: 'authentication',
  projectId: 'project-123',
  limit: 50, // ← Always specify
});

// Bad: Unbounded query (may return thousands)
const context = await contextIntegration.retrieveContext({
  query: 'authentication',
  projectId: 'project-123',
  // No limit!
});
```

### 3. Use Redis for Session State

Redis provides <5ms session operations:

```typescript
import { RedisSessionManager } from '@/services/context-dna/RedisSessionManager';

const sessionManager = new RedisSessionManager();

// Create session
await sessionManager.createSession(context);

// Update session (fast)
await sessionManager.updateThoughtCount(context.sessionId, 5);

// Get session state (<5ms)
const state = await sessionManager.getSessionState(context.sessionId);
```

### 4. Batch Operations

Batch multiple operations to reduce overhead:

```typescript
// Good: Batch storage
for (const conv of conversations) {
  await contextIntegration.storeConversation(context, conv);
}

// Better: Use database transactions (future enhancement)
```

---

## Best Practices

### 1. Always Provide Context

```typescript
// ✅ Good
const context = {
  sessionId: `session-${Date.now()}`,
  agentId: 'queen',
  projectId: 'project-123',
  taskId: 'task-456',
  startTime: new Date(),
};

// ❌ Bad
const context = {
  sessionId: 'session', // Too generic
  agentId: 'queen',
  // Missing projectId!
};
```

### 2. Store High-Quality Memories

```typescript
// ✅ Good: Specific, actionable memory
await contextIntegration.storeMemory(context, {
  memoryType: 'success_pattern',
  content: 'Using TypeScript strict mode caught 15 type errors before runtime',
  importance: 0.9,
});

// ❌ Bad: Vague, low-value memory
await contextIntegration.storeMemory(context, {
  memoryType: 'context',
  content: 'Did something',
  importance: 0.1,
});
```

### 3. Use Semantic Query Strings

```typescript
// ✅ Good: Descriptive query
const context = await contextIntegration.retrieveContext({
  query: 'authentication OAuth2 login implementation',
  projectId: 'project-123',
});

// ❌ Bad: Too generic
const context = await contextIntegration.retrieveContext({
  query: 'auth',
  projectId: 'project-123',
});
```

### 4. Clean Up Sessions

```typescript
// Cleanup old sessions (automated via RetentionPolicyEnforcer)
import { RetentionPolicyEnforcer } from '@/services/context-dna/RetentionPolicyEnforcer';

const enforcer = new RetentionPolicyEnforcer();
const result = await enforcer.enforceRetentionPolicy();

console.log(`Deleted ${result.deleted} old entries`);
console.log(`Freed ${result.freedBytes} bytes`);
```

### 5. Handle Errors Gracefully

```typescript
try {
  await contextIntegration.startAgentExecution(context);
} catch (error) {
  console.error('Failed to start agent execution:', error);
  // Fallback: Continue without context storage
}
```

---

## API Reference

### AgentContextIntegration

#### `startAgentExecution(context: AgentExecutionContext): Promise<{success: boolean}>`

Initialize agent execution session.

#### `storeConversation(context, message: {role, content}): Promise<void>`

Store conversation message.

#### `storeMemory(context, memory: {memoryType, content, importance}): Promise<void>`

Store agent memory.

#### `storeAgentResult(context, result: {success, output?, error?, artifacts?}): Promise<{success: boolean}>`

Store agent execution result.

#### `retrieveContext(query: SearchQuery): Promise<{conversations, memories, tasks, performanceMs}>`

Retrieve relevant context for agent execution.

### MemoryCoordinator

#### `shareMemories(options: MemorySharingOptions): Promise<{shared: number, memories: AgentMemory[]}>`

Share memories between agents.

#### `inheritContext(options: ContextInheritanceOptions): Promise<InheritanceResult>`

Inherit context from parent agent.

#### `searchContext(query: string, filters?: SearchFilters): Promise<{conversations, memories, tasks, totalResults}>`

Search across all context types.

### ArtifactManager

#### `registerArtifact(options: {projectId, artifactType, artifactName, s3Path, metadata?}): Promise<{success: boolean}>`

Register artifact reference in Context DNA.

#### `getArtifactsByProject(projectId: string): ArtifactReference[]`

Get all artifacts for a project.

### S3ArtifactStore

#### `upload(localPath: string, artifactId: string, projectId: string): Promise<UploadResult>`

Upload artifact to S3.

#### `download(s3Path: string, localPath: string): Promise<DownloadResult>`

Download artifact from S3.

#### `getPresignedUrl(s3Path: string, expirySeconds: number): Promise<PresignedUrlResult>`

Generate presigned download URL.

---

## Example: Complete Agent Workflow

```typescript
import { AgentContextIntegration } from '@/services/context-dna/AgentContextIntegration';
import { MemoryCoordinator } from '@/services/context-dna/MemoryCoordinator';

class CodeGenerationAgent {
  private contextIntegration = new AgentContextIntegration();
  private memoryCoordinator = new MemoryCoordinator();

  async generateCode(task: Task) {
    // 1. Create execution context
    const context = {
      sessionId: `session-${Date.now()}`,
      agentId: 'coder',
      projectId: task.projectId,
      taskId: task.id,
      parentAgentId: 'princess-dev', // Delegated from Princess
      startTime: new Date(),
    };

    // 2. Start execution
    await this.contextIntegration.startAgentExecution(context);

    // 3. Retrieve relevant context
    const retrieved = await this.contextIntegration.retrieveContext({
      query: task.description,
      projectId: task.projectId,
      agentId: 'coder',
      limit: 30,
    });

    console.log(`Found ${retrieved.memories.length} relevant memories`);

    // 4. Inherit context from parent (Princess)
    const inherited = await this.memoryCoordinator.inheritContext({
      projectId: task.projectId,
      parentAgentId: 'princess-dev',
      childAgentId: 'coder',
      inheritMemories: true,
      limit: 20,
    });

    console.log(`Inherited ${inherited.memoriesInherited} memories from Princess`);

    // 5. Store conversation
    await this.contextIntegration.storeConversation(context, {
      role: 'agent',
      content: 'Starting code generation for login feature',
    });

    try {
      // 6. Generate code
      const code = await this.generateCodeImplementation(task, retrieved);

      // 7. Store success memory
      await this.contextIntegration.storeMemory(context, {
        memoryType: 'success_pattern',
        content: `Generated ${code.linesOfCode} lines of TypeScript code with 100% type safety`,
        importance: 0.85,
      });

      // 8. Store result
      await this.contextIntegration.storeAgentResult(context, {
        success: true,
        output: code.filePath,
        artifacts: [{ type: 'code', path: code.filePath }],
      });

      return code;
    } catch (error) {
      // 9. Store failure memory
      await this.contextIntegration.storeMemory(context, {
        memoryType: 'failure_pattern',
        content: `Failed to generate code: ${error.message}`,
        importance: 0.9,
      });

      // 10. Store failure result
      await this.contextIntegration.storeAgentResult(context, {
        success: false,
        error: error.message,
        artifacts: [],
      });

      throw error;
    }
  }
}
```

---

## Performance Benchmarks

**Context DNA Week 20 Performance** (verified Day 6):

| Metric | Target | Actual | Performance |
|--------|--------|--------|-------------|
| **Context Retrieval** | <200ms | 0.51ms | ✅ 392x faster |
| **FTS Search** | <50ms | 0.69ms | ✅ 72x faster |
| **Compound Queries** | <100ms | 0.18ms | ✅ 555x faster |
| **Redis Session** | <5ms | <1ms | ✅ 5x+ faster |

**Storage Optimization**:
- Artifact references: 600 bytes (vs 50 MB full file)
- **99.4% storage reduction** verified

---

## Support

For issues or questions:
1. Check [WEEK-20-COMPLETE.md](WEEK-20-COMPLETE.md) for implementation details
2. Review [STORAGE-INTEGRATION-PATTERNS.md](STORAGE-INTEGRATION-PATTERNS.md) for patterns
3. See [WEEK-20-FINAL-AUDIT.md](WEEK-20-FINAL-AUDIT.md) for validation results

---

**Generated**: 2025-10-10
**Version**: Week 20 Day 7
**Status**: ✅ COMPLETE
