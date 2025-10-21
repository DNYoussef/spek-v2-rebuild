/**
 * Memory Retrieval Service
 *
 * Provides semantic search and context retrieval for agents.
 * Enables cross-agent memory sharing with <200ms lookup target.
 *
 * Features:
 * - Semantic similarity search
 * - Context ranking by relevance + recency
 * - Cross-agent pattern recognition
 * - Performance-optimized queries
 */

import { getContextDNAStorage } from './ContextDNAStorage';
import {
  SearchQuery,
  SearchResult,
  Task,
  Conversation,
  AgentMemory,
  Project,
} from './types';

export interface ContextRetrievalOptions {
  projectId?: string;
  taskId?: string;
  agentId?: string;
  limit?: number;
  includeRelated?: boolean;
  minRelevance?: number;
}

export interface RetrievedContext {
  tasks: Task[];
  conversations: Conversation[];
  memories: AgentMemory[];
  relevanceScore: number;
  retrievalTimeMs: number;
}

export class MemoryRetrieval {
  private storage = getContextDNAStorage();

  /**
   * Retrieve relevant context for a query
   * Target: <200ms total retrieval time
   */
  async retrieveContext(
    query: string,
    options: ContextRetrievalOptions = {}
  ): Promise<RetrievedContext> {
    const startTime = performance.now();

    // Search across all indexed content
    const searchResults = this.storage.search({
      query,
      projectId: options.projectId,
      taskId: options.taskId,
      limit: options.limit || 20,
    });

    // Separate results by type
    const tasks: Task[] = [];
    const conversations: Conversation[] = [];
    const memories: AgentMemory[] = [];

    for (const result of searchResults) {
      if ('status' in result.item && 'description' in result.item) {
        tasks.push(result.item as Task);
      } else if ('role' in result.item && 'content' in result.item) {
        conversations.push(result.item as Conversation);
      } else if ('memoryType' in result.item && 'importance' in result.item) {
        memories.push(result.item as AgentMemory);
      }
    }

    // Calculate overall relevance score
    const relevanceScore = this.calculateRelevance(searchResults);

    const retrievalTimeMs = performance.now() - startTime;

    return {
      tasks,
      conversations,
      memories,
      relevanceScore,
      retrievalTimeMs,
    };
  }

  /**
   * Get similar past tasks for pattern recognition
   */
  async getSimilarTasks(
    task: Task,
    limit = 10
  ): Promise<SearchResult<Task>[]> {
    const results = this.storage.search({
      query: task.description,
      projectId: task.projectId,
      limit,
    });

    return results
      .filter((r) => 'status' in r.item)
      .filter((r) => (r.item as Task).id !== task.id)
      .map((r) => ({
        item: r.item as Task,
        score: r.score,
        snippet: r.snippet,
      }));
  }

  /**
   * Get agent's successful patterns
   */
  async getSuccessPatterns(
    agentId: string,
    projectId?: string,
    limit = 20
  ): Promise<AgentMemory[]> {
    return this.storage.getAgentMemories(agentId, projectId, 0.7, limit)
      .filter((m) => m.memoryType === 'success_pattern')
      .sort((a, b) => b.importance - a.importance);
  }

  /**
   * Get agent's failure patterns to avoid
   */
  async getFailurePatterns(
    agentId: string,
    projectId?: string,
    limit = 20
  ): Promise<AgentMemory[]> {
    return this.storage.getAgentMemories(agentId, projectId, 0.5, limit)
      .filter((m) => m.memoryType === 'failure_pattern')
      .sort((a, b) => b.importance - a.importance);
  }

  /**
   * Get project timeline (all tasks + conversations)
   */
  async getProjectTimeline(
    projectId: string,
    limit = 100
  ): Promise<{ tasks: Task[]; conversations: Conversation[] }> {
    const tasks = this.storage.getTasksForProject(projectId, limit);
    const conversations = this.storage.getConversationsForProject(projectId, limit);

    return { tasks, conversations };
  }

  /**
   * Get context for a specific task
   */
  async getTaskContext(taskId: string): Promise<{
    task: Task | null;
    relatedConversations: Conversation[];
    relatedMemories: AgentMemory[];
  }> {
    // Find the task
    const task = this.findTaskById(taskId);
    if (!task) {
      return {
        task: null,
        relatedConversations: [],
        relatedMemories: [],
      };
    }

    // Get related conversations
    const allConversations = this.storage.getConversationsForProject(
      task.projectId,
      100
    );
    const relatedConversations = allConversations.filter(
      (c) => c.taskId === taskId
    );

    // Get related agent memories
    const relatedMemories: AgentMemory[] = [];
    if (task.assignedTo) {
      const memories = this.storage.getAgentMemories(
        task.assignedTo,
        task.projectId,
        0.5,
        50
      );
      relatedMemories.push(...memories);
    }

    return {
      task,
      relatedConversations,
      relatedMemories,
    };
  }

  /**
   * Store a new memory for an agent
   */
  async storeAgentMemory(
    agentId: string,
    projectId: string,
    memoryType: AgentMemory['memoryType'],
    content: string,
    importance: number,
    taskId?: string
  ): Promise<void> {
    const memory: AgentMemory = {
      id: this.generateId(),
      agentId,
      projectId,
      taskId,
      memoryType,
      content,
      importance,
      createdAt: new Date(),
      lastAccessedAt: new Date(),
      accessCount: 0,
    };

    this.storage.saveAgentMemory(memory);
  }

  /**
   * Calculate overall relevance score from search results
   */
  private calculateRelevance(results: SearchResult<any>[]): number {
    if (results.length === 0) return 0;

    // Weighted average of top results
    const weights = [1.0, 0.8, 0.6, 0.4, 0.2];
    let weightedScore = 0;
    let totalWeight = 0;

    results.slice(0, 5).forEach((result, index) => {
      const weight = weights[index] || 0.1;
      weightedScore += result.score * weight;
      totalWeight += weight;
    });

    return weightedScore / totalWeight;
  }

  /**
   * Find task by ID across all projects
   */
  private findTaskById(taskId: string): Task | null {
    // This is a simplified implementation
    // In production, you'd want an index or more efficient lookup
    const allProjects = this.getAllProjects();

    for (const project of allProjects) {
      const tasks = this.storage.getTasksForProject(project.id, 1000);
      const found = tasks.find((t) => t.id === taskId);
      if (found) return found;
    }

    return null;
  }

  /**
   * Get all projects (for task lookup)
   */
  private getAllProjects(): Project[] {
    // This would be better with a dedicated method in ContextDNAStorage
    // For now, return empty array (to be implemented)
    return [];
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}

/**
 * Singleton instance
 */
let instance: MemoryRetrieval | null = null;

export function getMemoryRetrieval(): MemoryRetrieval {
  if (!instance) {
    instance = new MemoryRetrieval();
  }
  return instance;
}
