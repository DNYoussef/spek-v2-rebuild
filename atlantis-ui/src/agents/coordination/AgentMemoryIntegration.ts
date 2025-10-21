/**
 * Agent Memory Integration
 *
 * Helper utilities for integrating Memory Coordinator with agents.
 * Provides easy-to-use wrappers for Queen and Princess agents.
 */

import { getMemoryCoordinator, MemoryContext } from './MemoryCoordinator';
import type { Task } from '../../services/context-dna/types';

export interface AgentTaskContext {
  task: Task;
  memory: MemoryContext;
  recommendations: string[];
}

export class AgentMemoryIntegration {
  private coordinator = getMemoryCoordinator();

  /**
   * Get enhanced context for Queen agent task orchestration
   */
  async getQueenContext(
    projectId: string,
    taskDescription: string,
    projectPath?: string
  ): Promise<AgentTaskContext> {
    const memory = await this.coordinator.getContextForTask(
      projectId,
      'queen',
      taskDescription,
      {
        includeSemanticSearch: true,
        projectPath,
      }
    );

    const recommendations = this.generateQueenRecommendations(memory);

    return {
      task: {
        id: `task-${Date.now()}`,
        projectId,
        description: taskDescription,
        status: 'pending',
        createdAt: new Date(),
      },
      memory,
      recommendations,
    };
  }

  /**
   * Get enhanced context for Princess agent coordination
   */
  async getPrincessContext(
    princessId: 'princess-dev' | 'princess-quality' | 'princess-coordination',
    projectId: string,
    taskDescription: string
  ): Promise<AgentTaskContext> {
    const memory = await this.coordinator.getContextForTask(
      projectId,
      princessId,
      taskDescription
    );

    const recommendations = this.generatePrincessRecommendations(
      princessId,
      memory
    );

    return {
      task: {
        id: `task-${Date.now()}`,
        projectId,
        description: taskDescription,
        status: 'pending',
        assignedTo: princessId,
        createdAt: new Date(),
      },
      memory,
      recommendations,
    };
  }

  /**
   * Record task success for learning
   */
  async recordSuccess(
    agentId: string,
    projectId: string,
    taskId: string,
    learnings: string
  ): Promise<void> {
    await this.coordinator.storeAgentLearning(agentId, projectId, {
      type: 'success',
      content: learnings,
      taskId,
      importance: 0.8,
    });
  }

  /**
   * Record task failure for learning
   */
  async recordFailure(
    agentId: string,
    projectId: string,
    taskId: string,
    error: string
  ): Promise<void> {
    await this.coordinator.storeAgentLearning(agentId, projectId, {
      type: 'failure',
      content: `Failed: ${error}`,
      taskId,
      importance: 0.9, // Failures are highly important to remember
    });
  }

  /**
   * Generate recommendations for Queen agent
   */
  private generateQueenRecommendations(memory: MemoryContext): string[] {
    const recommendations: string[] = [];

    // Check success patterns
    if (memory.successPatterns.length > 0) {
      const topPattern = memory.successPatterns[0];
      recommendations.push(
        `Success pattern: ${topPattern.content.substring(0, 100)}`
      );
    }

    // Check failure patterns
    if (memory.failurePatterns.length > 0) {
      const topFailure = memory.failurePatterns[0];
      recommendations.push(
        `Avoid: ${topFailure.content.substring(0, 100)}`
      );
    }

    // Check similar tasks
    if (memory.relevantTasks.length > 0) {
      recommendations.push(
        `${memory.relevantTasks.length} similar tasks found in history`
      );
    }

    // Performance warning
    if (memory.retrievalTimeMs > 150) {
      recommendations.push(
        `Note: Context retrieval took ${memory.retrievalTimeMs.toFixed(0)}ms`
      );
    }

    return recommendations;
  }

  /**
   * Generate recommendations for Princess agents
   */
  private generatePrincessRecommendations(
    princessId: string,
    memory: MemoryContext
  ): string[] {
    const recommendations: string[] = [];

    // Princess-specific recommendations
    switch (princessId) {
      case 'princess-dev':
        if (memory.relevantMemories.length > 0) {
          recommendations.push(
            `${memory.relevantMemories.length} relevant development patterns found`
          );
        }
        break;

      case 'princess-quality':
        if (memory.failurePatterns.length > 0) {
          recommendations.push(
            `${memory.failurePatterns.length} quality issues to watch for`
          );
        }
        break;

      case 'princess-coordination':
        if (memory.relevantTasks.length > 0) {
          recommendations.push(
            `${memory.relevantTasks.length} similar coordination tasks in history`
          );
        }
        break;
    }

    return recommendations;
  }

  /**
   * Invalidate cache when project changes
   */
  async invalidateCache(projectId: string, projectPath: string): Promise<void> {
    await this.coordinator.invalidateProjectCache(projectId, projectPath);
  }
}

/**
 * Singleton instance
 */
let instance: AgentMemoryIntegration | null = null;

export function getAgentMemoryIntegration(): AgentMemoryIntegration {
  if (!instance) {
    instance = new AgentMemoryIntegration();
  }
  return instance;
}
