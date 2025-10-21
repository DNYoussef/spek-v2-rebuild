/**
 * Memory Coordinator
 *
 * Orchestrates cross-agent memory sharing using Context DNA,
 * Redis cache, and Pinecone vectors.
 *
 * Features:
 * - Unified context retrieval across all storage layers
 * - Smart caching with git-based invalidation
 * - Semantic search with vector embeddings
 * - <200ms total retrieval time
 */

import { getContextDNAStorage } from '../../services/context-dna/ContextDNAStorage';
import { getMemoryRetrieval } from '../../services/context-dna/MemoryRetrieval';
import { getRedisCacheManager } from '../../services/cache/RedisCacheManager';
import { getPineconeVectorStore } from '../../services/vectors/PineconeVectorStore';
import { GitHashUtil } from '../../services/cache/GitHashUtil';
import type { Task, AgentMemory, Conversation } from '../../services/context-dna/types';

export interface MemoryContext {
  projectId: string;
  agentId: string;
  taskDescription?: string;
  relevantTasks: Task[];
  relevantMemories: AgentMemory[];
  relevantConversations: Conversation[];
  successPatterns: AgentMemory[];
  failurePatterns: AgentMemory[];
  semanticMatches?: Array<{ text: string; score: number }>;
  retrievalTimeMs: number;
  cacheHit: boolean;
}

export class MemoryCoordinator {
  private contextDNA = getContextDNAStorage();
  private memoryRetrieval = getMemoryRetrieval();
  private redis = getRedisCacheManager();
  private pinecone = getPineconeVectorStore();

  /**
   * Retrieve comprehensive context for an agent task
   * Target: <200ms total time
   */
  async getContextForTask(
    projectId: string,
    agentId: string,
    taskDescription: string,
    options: {
      includeSemanticSearch?: boolean;
      projectPath?: string;
    } = {}
  ): Promise<MemoryContext> {
    const startTime = performance.now();
    let cacheHit = false;

    // Check Redis cache first
    const cachedContext = await this.getCachedContext(
      projectId,
      agentId,
      taskDescription
    );

    if (cachedContext) {
      cacheHit = true;
      return {
        ...cachedContext,
        retrievalTimeMs: performance.now() - startTime,
        cacheHit: true,
      };
    }

    // Cache miss - retrieve from Context DNA
    const [
      retrievalResult,
      successPatterns,
      failurePatterns,
      semanticMatches
    ] = await Promise.all([
      this.memoryRetrieval.retrieveContext(taskDescription, {
        projectId,
        agentId,
        limit: 20,
      }),
      this.memoryRetrieval.getSuccessPatterns(agentId, projectId, 10),
      this.memoryRetrieval.getFailurePatterns(agentId, projectId, 10),
      options.includeSemanticSearch && options.projectPath
        ? this.getSemanticMatches(projectId, taskDescription)
        : Promise.resolve([]),
    ]);

    const context: MemoryContext = {
      projectId,
      agentId,
      taskDescription,
      relevantTasks: retrievalResult.tasks,
      relevantMemories: retrievalResult.memories,
      relevantConversations: retrievalResult.conversations,
      successPatterns,
      failurePatterns,
      semanticMatches: semanticMatches.length > 0 ? semanticMatches : undefined,
      retrievalTimeMs: performance.now() - startTime,
      cacheHit: false,
    };

    // Cache the result
    await this.cacheContext(projectId, agentId, taskDescription, context);

    return context;
  }

  /**
   * Get semantic matches using Pinecone vectors
   */
  private async getSemanticMatches(
    projectId: string,
    query: string
  ): Promise<Array<{ text: string; score: number }>> {
    try {
      // This would require embedding generation
      // For now, return empty array (to be implemented with OpenAI)
      return [];
    } catch (error) {
      console.error('Semantic search failed:', error);
      return [];
    }
  }

  /**
   * Get cached context from Redis
   */
  private async getCachedContext(
    projectId: string,
    agentId: string,
    taskDescription: string
  ): Promise<MemoryContext | null> {
    try {
      await this.redis.connect();

      // Generate cache key
      const cacheKey = this.generateCacheKey(projectId, agentId, taskDescription);
      const cached = await this.redis.getProjectMetadata(cacheKey);

      if (cached && cached.metadata) {
        return cached.metadata as unknown as MemoryContext;
      }

      return null;
    } catch (error) {
      console.error('Cache retrieval failed:', error);
      return null;
    }
  }

  /**
   * Cache context in Redis
   */
  private async cacheContext(
    projectId: string,
    agentId: string,
    taskDescription: string,
    context: MemoryContext
  ): Promise<void> {
    try {
      await this.redis.connect();

      const cacheKey = this.generateCacheKey(projectId, agentId, taskDescription);

      await this.redis.setProjectMetadata(cacheKey, {
        projectId: cacheKey,
        gitHash: 'unknown', // Would be set with actual git hash
        metadata: context as unknown as Record<string, unknown>,
        vectorized: false,
      });
    } catch (error) {
      console.error('Context caching failed:', error);
    }
  }

  /**
   * Generate cache key for context
   */
  private generateCacheKey(
    projectId: string,
    agentId: string,
    taskDescription: string
  ): string {
    const hash = require('crypto')
      .createHash('md5')
      .update(taskDescription)
      .digest('hex')
      .substring(0, 8);

    return `context:${projectId}:${agentId}:${hash}`;
  }

  /**
   * Invalidate context cache when project changes
   */
  async invalidateProjectCache(
    projectId: string,
    projectPath: string
  ): Promise<{ invalidated: boolean; reason: string }> {
    try {
      const gitState = await GitHashUtil.getGitState(projectPath);

      const invalidated = await this.redis.invalidateProjectIfHashChanged(
        projectId,
        projectPath,
        gitState.fingerprint
      );

      return {
        invalidated,
        reason: invalidated
          ? `Git state changed: ${gitState.fingerprint}`
          : 'Cache still valid',
      };
    } catch (error) {
      console.error('Cache invalidation failed:', error);
      return {
        invalidated: false,
        reason: `Error: ${error}`,
      };
    }
  }

  /**
   * Store agent learning as memory
   */
  async storeAgentLearning(
    agentId: string,
    projectId: string,
    learning: {
      type: 'success' | 'failure' | 'optimization';
      content: string;
      taskId?: string;
      importance: number;
    }
  ): Promise<void> {
    const memoryType =
      learning.type === 'success'
        ? 'success_pattern'
        : learning.type === 'failure'
        ? 'failure_pattern'
        : 'optimization';

    await this.memoryRetrieval.storeAgentMemory(
      agentId,
      projectId,
      memoryType,
      learning.content,
      learning.importance,
      learning.taskId
    );
  }

  /**
   * Get similar past tasks for pattern recognition
   */
  async getSimilarTasks(task: Task, limit = 10): Promise<Task[]> {
    const similarResults = await this.memoryRetrieval.getSimilarTasks(
      task,
      limit
    );

    return similarResults.map((result) => result.item);
  }

  /**
   * Get project timeline for context
   */
  async getProjectHistory(
    projectId: string,
    limit = 100
  ): Promise<{
    tasks: Task[];
    conversations: Conversation[];
  }> {
    return await this.memoryRetrieval.getProjectTimeline(projectId, limit);
  }

  /**
   * Get cache statistics
   */
  async getCacheStats(): Promise<{
    redis: {
      totalKeys: number;
      memoryUsed: string;
    };
    contextDNA: {
      totalProjects: number;
      totalTasks: number;
      totalMemories: number;
    };
  }> {
    const [redisStats, dnaStats] = await Promise.all([
      this.redis.getCacheStats(),
      this.contextDNA.getStats(),
    ]);

    return {
      redis: {
        totalKeys: redisStats.totalKeys,
        memoryUsed: redisStats.memoryUsed,
      },
      contextDNA: {
        totalProjects: dnaStats.totalProjects,
        totalTasks: dnaStats.totalTasks,
        totalMemories: dnaStats.totalAgentMemories,
      },
    };
  }
}

/**
 * Singleton instance
 */
let instance: MemoryCoordinator | null = null;

export function getMemoryCoordinator(): MemoryCoordinator {
  if (!instance) {
    instance = new MemoryCoordinator();
  }
  return instance;
}
