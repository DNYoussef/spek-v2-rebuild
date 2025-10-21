/**
 * Agent Context Integration
 *
 * Integrates Context DNA storage with agent execution pipeline.
 * Provides automatic context persistence for all agent operations.
 *
 * Week 20 Day 1
 * Version: 8.0.0
 */

import { ContextDNAStorage, getContextDNAStorage } from './ContextDNAStorage';
import { MemoryRetrieval, getMemoryRetrieval } from './MemoryRetrieval';
import { ArtifactManager, getArtifactManager } from './ArtifactManager';
import { RedisSessionManager, getRedisSessionManager } from './RedisSessionManager';
import {
  Task,
  Conversation,
  AgentMemory,
  ArtifactReference,
  SearchQuery,
  SearchResult,
} from './types';

/**
 * Agent execution context
 */
export interface AgentExecutionContext {
  agentId: string;
  projectId: string;
  taskId?: string;
  parentAgentId?: string; // Delegation chain
  sessionId: string;
  startTime: Date;
  metadata?: Record<string, unknown>;
}

/**
 * Agent context persistence result
 */
export interface ContextPersistenceResult {
  success: boolean;
  contextId?: string;
  error?: string;
  performanceMs: number;
}

/**
 * Agent memory query options
 */
export interface AgentMemoryQueryOptions {
  projectId?: string;
  agentId?: string;
  taskId?: string;
  memoryType?: AgentMemory['memoryType'];
  limit?: number;
  minImportance?: number;
}

/**
 * AgentContextManager
 *
 * Manages context persistence and retrieval for agent operations.
 * Integrates with Context DNA storage system.
 */
export class AgentContextManager {
  private storage: ContextDNAStorage;
  private memoryRetrieval: MemoryRetrieval;
  private artifactManager: ArtifactManager;
  private sessionManager: RedisSessionManager;

  constructor(
    storage?: ContextDNAStorage,
    memoryRetrieval?: MemoryRetrieval,
    artifactManager?: ArtifactManager,
    sessionManager?: RedisSessionManager
  ) {
    this.storage = storage || getContextDNAStorage();
    this.memoryRetrieval = memoryRetrieval || getMemoryRetrieval();
    this.artifactManager = artifactManager || getArtifactManager();
    this.sessionManager = sessionManager || getRedisSessionManager();
  }

  /**
   * Initialize agent execution context
   * Call at the start of agent.execute()
   */
  async initializeContext(context: AgentExecutionContext): Promise<void> {
    // Create Redis session
    await this.sessionManager.createSession(context);

    // Ensure project exists
    await this.ensureProjectExists(context.projectId);

    // Ensure task exists (if taskId provided)
    if (context.taskId) {
      await this.ensureTaskExists(context.taskId, context.projectId);
    }

    // Store session start
    await this.storeConversation({
      id: `${context.sessionId}-start`,
      projectId: context.projectId,
      taskId: context.taskId,
      role: 'system',
      agentId: context.agentId,
      content: `Agent ${context.agentId} session started`,
      createdAt: context.startTime,
      metadata: {
        sessionId: context.sessionId,
        parentAgentId: context.parentAgentId,
        ...context.metadata,
      },
    });
  }

  /**
   * Store agent thought/action during execution
   * Call during agent.execute() to log progress
   */
  async storeAgentThought(
    context: AgentExecutionContext,
    thought: string,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    // Update Redis session activity
    await this.sessionManager.updateActivity(context.sessionId);

    await this.storeConversation({
      id: `${context.sessionId}-thought-${Date.now()}`,
      projectId: context.projectId,
      taskId: context.taskId,
      role: 'agent',
      agentId: context.agentId,
      content: thought,
      createdAt: new Date(),
      metadata: {
        sessionId: context.sessionId,
        ...metadata,
      },
    });
  }

  /**
   * Store agent result after execution
   * Call at the end of agent.execute()
   */
  async storeAgentResult(
    context: AgentExecutionContext,
    result: {
      success: boolean;
      output?: string;
      error?: string;
      artifacts?: ArtifactReference[];
      metrics?: Record<string, unknown>;
    }
  ): Promise<ContextPersistenceResult> {
    const startTime = Date.now();

    try {
      // Update task with result
      if (context.taskId) {
        const tasks = this.storage.getTasksForProject(context.projectId, 1000);
        const task = tasks.find(t => t.id === context.taskId);
        if (task) {
          // Update task with new status and result
          task.status = result.success ? 'completed' : 'failed';
          task.completedAt = new Date();
          task.result = {
            success: result.success,
            output: result.output,
            error: result.error,
            artifacts: result.artifacts,
            metrics: result.metrics,
          };
          this.storage.saveTask(task);
        }
      }

      // Store result conversation
      await this.storeConversation({
        id: `${context.sessionId}-result`,
        projectId: context.projectId,
        taskId: context.taskId,
        role: 'agent',
        agentId: context.agentId,
        content: result.success
          ? `Task completed successfully`
          : `Task failed: ${result.error || 'Unknown error'}`,
        createdAt: new Date(),
        metadata: {
          sessionId: context.sessionId,
          result: result,
        },
      });

      const performanceMs = Date.now() - startTime;

      return {
        success: true,
        contextId: context.sessionId,
        performanceMs,
      };
    } catch (error) {
      const performanceMs = Date.now() - startTime;

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        performanceMs,
      };
    }
  }

  /**
   * Retrieve relevant context for agent execution
   * Call before agent.execute() to load context
   */
  async retrieveContext(
    query: SearchQuery
  ): Promise<{
    conversations: SearchResult<Conversation>[];
    memories: SearchResult<AgentMemory>[];
    tasks: SearchResult<Task>[];
    performanceMs: number;
  }> {
    const startTime = Date.now();

    // Use MemoryRetrieval's retrieveContext method
    const context = await this.memoryRetrieval.retrieveContext(query.query, {
      projectId: query.projectId,
      taskId: query.taskId,
      agentId: query.agentId,
      limit: query.limit,
    });

    // Convert to SearchResult format
    const conversations: SearchResult<Conversation>[] = context.conversations.map(c => ({
      item: c,
      score: 1.0,
    }));
    const memories: SearchResult<AgentMemory>[] = context.memories.map(m => ({
      item: m,
      score: 1.0,
    }));
    const tasks: SearchResult<Task>[] = context.tasks.map(t => ({
      item: t,
      score: 1.0,
    }));

    const performanceMs = Date.now() - startTime;

    return {
      conversations,
      memories,
      tasks,
      performanceMs,
    };
  }

  /**
   * Store agent memory (success pattern, failure pattern, etc.)
   * Call after agent.execute() to record learnings
   */
  async storeAgentMemory(memory: Omit<AgentMemory, 'id' | 'createdAt' | 'lastAccessedAt' | 'accessCount'>): Promise<void> {
    this.storage.saveAgentMemory({
      ...memory,
      id: `${memory.agentId}-${Date.now()}`,
      createdAt: new Date(),
      lastAccessedAt: new Date(),
      accessCount: 0,
    });
  }

  /**
   * Query agent memories by criteria
   */
  async queryMemories(options: AgentMemoryQueryOptions): Promise<AgentMemory[]> {
    return this.storage.getAgentMemories(
      options.projectId || '',
      options.agentId,
      options.limit || 10
    );
  }

  /**
   * Finalize agent execution context
   * Call at the end of agent.execute()
   */
  async finalizeContext(
    context: AgentExecutionContext,
    success = true
  ): Promise<void> {
    // Complete Redis session
    await this.sessionManager.completeSession(context.sessionId, success);

    await this.storeConversation({
      id: `${context.sessionId}-end`,
      projectId: context.projectId,
      taskId: context.taskId,
      role: 'system',
      agentId: context.agentId,
      content: `Agent ${context.agentId} session ended`,
      createdAt: new Date(),
      metadata: {
        sessionId: context.sessionId,
        durationMs: Date.now() - context.startTime.getTime(),
        success,
      },
    });
  }

  // Private helper methods
  private async ensureProjectExists(projectId: string): Promise<void> {
    const existing = this.storage.getProject(projectId);
    if (!existing) {
      this.storage.saveProject({
        id: projectId,
        name: `Project ${projectId}`,
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      });
    }
  }

  private async ensureTaskExists(taskId: string, projectId: string): Promise<void> {
    const tasks = this.storage.getTasksForProject(projectId, 1000);
    const existing = tasks.find(t => t.id === taskId);
    if (!existing) {
      this.storage.saveTask({
        id: taskId,
        projectId,
        description: `Task ${taskId}`,
        status: 'pending',
        createdAt: new Date(),
      });
    }
  }

  private async storeConversation(conversation: Conversation): Promise<void> {
    this.storage.saveConversation(conversation);
  }
}

/**
 * Singleton instance
 */
let agentContextManagerInstance: AgentContextManager | null = null;

/**
 * Get or create AgentContextManager singleton
 */
export function getAgentContextManager(): AgentContextManager {
  if (!agentContextManagerInstance) {
    agentContextManagerInstance = new AgentContextManager();
  }
  return agentContextManagerInstance;
}

/**
 * Helper function for Python AgentBase integration
 * Wraps agent execution with automatic context persistence
 */
export async function withContextPersistence<T>(
  context: AgentExecutionContext,
  execution: () => Promise<T>
): Promise<T> {
  const manager = getAgentContextManager();

  // Initialize context
  await manager.initializeContext(context);

  try {
    // Execute agent logic
    const result = await execution();

    // Finalize context
    await manager.finalizeContext(context);

    return result;
  } catch (error) {
    // Store error
    await manager.storeAgentResult(context, {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    });

    // Finalize context
    await manager.finalizeContext(context);

    throw error;
  }
}
