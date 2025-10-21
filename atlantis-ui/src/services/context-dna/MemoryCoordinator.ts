/**
 * Memory Coordinator
 *
 * Coordinates cross-agent memory sharing and context inheritance.
 * Enables agents to learn from each other's experiences.
 *
 * Week 20 Day 2
 * Version: 8.0.0
 */

import { ContextDNAStorage, getContextDNAStorage } from './ContextDNAStorage';
import { MemoryRetrieval, getMemoryRetrieval } from './MemoryRetrieval';
import { RedisSessionManager, getRedisSessionManager } from './RedisSessionManager';
import {
  AgentMemory,
  Conversation,
  Task,
  SearchQuery,
  SearchResult,
} from './types';

/**
 * Memory sharing options
 */
export interface MemorySharingOptions {
  sourceAgentId: string;
  targetAgentId: string;
  projectId: string;
  memoryTypes?: AgentMemory['memoryType'][];
  minImportance?: number;
  limit?: number;
}

/**
 * Context inheritance configuration
 */
export interface ContextInheritanceConfig {
  parentAgentId: string;
  childAgentId: string;
  projectId: string;
  taskId?: string;
  includeConversations?: boolean;
  includeMemories?: boolean;
  includeTasks?: boolean;
}

/**
 * Search filters for context queries
 */
export interface ContextSearchFilters {
  projectId?: string;
  agentId?: string;
  taskId?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  memoryType?: AgentMemory['memoryType'];
  importance?: {
    min?: number;
    max?: number;
  };
}

/**
 * MemoryCoordinator
 *
 * Manages cross-agent memory sharing and context inheritance.
 */
export class MemoryCoordinator {
  private storage: ContextDNAStorage;
  private memoryRetrieval: MemoryRetrieval;
  private sessionManager: RedisSessionManager;

  constructor(
    storage?: ContextDNAStorage,
    memoryRetrieval?: MemoryRetrieval,
    sessionManager?: RedisSessionManager
  ) {
    this.storage = storage || getContextDNAStorage();
    this.memoryRetrieval = memoryRetrieval || getMemoryRetrieval();
    this.sessionManager = sessionManager || getRedisSessionManager();
  }

  /**
   * Share memories from one agent to another
   * Useful for knowledge transfer between agents
   */
  async shareMemories(options: MemorySharingOptions): Promise<{
    shared: number;
    memories: AgentMemory[];
  }> {
    // Get memories from source agent
    const sourceMemories = this.storage.getAgentMemories(
      options.projectId,
      options.sourceAgentId,
      options.limit || 100
    );

    // Filter by type and importance
    const filteredMemories = sourceMemories.filter(memory => {
      // Filter by memory type if specified
      if (options.memoryTypes && options.memoryTypes.length > 0) {
        if (!options.memoryTypes.includes(memory.memoryType)) {
          return false;
        }
      }

      // Filter by importance if specified
      if (options.minImportance !== undefined) {
        if (memory.importance < options.minImportance) {
          return false;
        }
      }

      return true;
    });

    // Create new memories for target agent
    const sharedMemories: AgentMemory[] = [];

    for (const memory of filteredMemories) {
      const sharedMemory: AgentMemory = {
        ...memory,
        id: `${options.targetAgentId}-shared-${Date.now()}-${Math.random()}`,
        agentId: options.targetAgentId,
        createdAt: new Date(),
        lastAccessedAt: new Date(),
        accessCount: 0,
        metadata: {
          ...memory.metadata,
          sharedFrom: options.sourceAgentId,
          originalMemoryId: memory.id,
          sharedAt: new Date().toISOString(),
        },
      };

      this.storage.saveAgentMemory(sharedMemory);
      sharedMemories.push(sharedMemory);
    }

    return {
      shared: sharedMemories.length,
      memories: sharedMemories,
    };
  }

  /**
   * Inherit context from parent agent to child agent
   * Used during delegation (Queen → Princess → Drone)
   */
  async inheritContext(config: ContextInheritanceConfig): Promise<{
    conversations: number;
    memories: number;
    tasks: number;
  }> {
    let conversationCount = 0;
    let memoryCount = 0;
    let taskCount = 0;

    // Inherit conversations if enabled
    if (config.includeConversations !== false) {
      const conversations = this.storage.getConversationsForProject(
        config.projectId,
        1000
      );

      // Filter conversations from parent agent
      const parentConversations = conversations.filter(
        conv => conv.agentId === config.parentAgentId
      );

      // Create reference conversations for child
      for (const conv of parentConversations) {
        const inheritedConv: Conversation = {
          id: `${config.childAgentId}-inherited-${Date.now()}-${Math.random()}`,
          projectId: config.projectId,
          taskId: config.taskId || conv.taskId,
          role: 'system',
          agentId: config.childAgentId,
          content: `[Inherited from ${config.parentAgentId}] ${conv.content}`,
          createdAt: new Date(),
          metadata: {
            inheritedFrom: config.parentAgentId,
            originalConversationId: conv.id,
            inheritedAt: new Date().toISOString(),
          },
        };

        this.storage.saveConversation(inheritedConv);
        conversationCount++;
      }
    }

    // Inherit memories if enabled
    if (config.includeMemories !== false) {
      const result = await this.shareMemories({
        sourceAgentId: config.parentAgentId,
        targetAgentId: config.childAgentId,
        projectId: config.projectId,
        minImportance: 0.5, // Only share important memories
      });
      memoryCount = result.shared;
    }

    // Inherit tasks if enabled
    if (config.includeTasks !== false) {
      const tasks = this.storage.getTasksForProject(config.projectId, 1000);

      // Filter tasks assigned to parent
      const parentTasks = tasks.filter(
        task => task.assignedTo === config.parentAgentId
      );

      // Create reference for child to be aware of parent's tasks
      taskCount = parentTasks.length;
    }

    return {
      conversations: conversationCount,
      memories: memoryCount,
      tasks: taskCount,
    };
  }

  /**
   * Search context by multiple criteria
   * Supports filtering by agent, task, project, date range, etc.
   */
  async searchContext(
    query: string,
    filters: ContextSearchFilters
  ): Promise<{
    conversations: SearchResult<Conversation>[];
    memories: SearchResult<AgentMemory>[];
    tasks: SearchResult<Task>[];
    totalResults: number;
  }> {
    // Build search query
    // Execute search using MemoryRetrieval
    const context = await this.memoryRetrieval.retrieveContext(query, {
      projectId: filters.projectId,
      agentId: filters.agentId,
      taskId: filters.taskId,
      limit: 100,
    });

    // Convert to SearchResult format
    const conversations: SearchResult<Conversation>[] = context.conversations.map(c => ({
      item: c,
      score: 1.0,
    }));
    const tasks: SearchResult<Task>[] = context.tasks.map(t => ({
      item: t,
      score: 1.0,
    }));

    // Apply memory type and importance filters
    const memories: SearchResult<AgentMemory>[] = context.memories
      .filter(memory => {
        if (filters.memoryType && memory.memoryType !== filters.memoryType) {
          return false;
        }
        if (filters.importance) {
          const importance = memory.importance;
          if (filters.importance.min !== undefined && importance < filters.importance.min) {
            return false;
          }
          if (filters.importance.max !== undefined && importance > filters.importance.max) {
            return false;
          }
        }
        return true;
      })
      .map(m => ({
        item: m,
        score: 1.0,
      }));

    return {
      conversations,
      memories,
      tasks,
      totalResults: conversations.length + memories.length + tasks.length,
    };
  }

  /**
   * Get context for specific agent on specific project
   * Optimized for fast agent startup
   */
  async getAgentContext(
    agentId: string,
    projectId: string,
    limit = 50
  ): Promise<{
    recentConversations: Conversation[];
    relevantMemories: AgentMemory[];
    assignedTasks: Task[];
  }> {
    // Get recent conversations
    const allConversations = this.storage.getConversationsForProject(
      projectId,
      1000
    );
    const recentConversations = allConversations
      .filter(conv => conv.agentId === agentId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);

    // Get relevant memories (high importance)
    const allMemories = this.storage.getAgentMemories(
      projectId,
      agentId,
      1000
    );
    const relevantMemories = allMemories
      .filter(mem => mem.importance >= 0.5)
      .sort((a, b) => b.importance - a.importance)
      .slice(0, limit);

    // Get assigned tasks
    const allTasks = this.storage.getTasksForProject(projectId, 1000);
    const assignedTasks = allTasks.filter(task => task.assignedTo === agentId);

    return {
      recentConversations,
      relevantMemories,
      assignedTasks,
    };
  }

  /**
   * Get active sessions for agent
   */
  async getActiveSessionsForAgent(agentId: string): Promise<string[]> {
    return await this.sessionManager.getSessionsByAgent(agentId);
  }

  /**
   * Get active sessions for project
   */
  async getActiveSessionsForProject(projectId: string): Promise<string[]> {
    return await this.sessionManager.getSessionsByProject(projectId);
  }
}

/**
 * Singleton instance
 */
let memoryCoordinatorInstance: MemoryCoordinator | null = null;

/**
 * Get or create MemoryCoordinator singleton
 */
export function getMemoryCoordinator(): MemoryCoordinator {
  if (!memoryCoordinatorInstance) {
    memoryCoordinatorInstance = new MemoryCoordinator();
  }
  return memoryCoordinatorInstance;
}
