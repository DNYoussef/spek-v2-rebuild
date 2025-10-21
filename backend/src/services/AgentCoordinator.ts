/**
 * Agent Coordinator - Princess Hive Delegation Model
 *
 * Implements hierarchical agent coordination:
 * Queen → Princess → Drone
 *
 * Coordinators:
 * - Princess-Dev (coder, reviewer, debugger, integration-engineer)
 * - Princess-Quality (tester, nasa-enforcer, theater-detector, fsm-analyzer)
 * - Princess-Coordination (orchestrator, planner, cost-tracker)
 * - Princess-Documentation (docs-writer, spec-writer, pseudocode-writer)
 *
 * Week 8 Day 4
 * Version: 8.0.0
 */

import type { TaskQueue, AgentTask } from './TaskQueue';
import type { WebSocketBroadcaster } from './WebSocketBroadcaster';

// ============================================================================
// Types
// ============================================================================

export interface AgentDelegation {
  from: string;      // Queen or Princess ID
  to: string;        // Princess or Drone ID
  taskId: string;
  task: string;
  priority: 'P0' | 'P1' | 'P2';
  context?: Record<string, unknown>;
}

export interface PrincessCoordinator {
  id: string;
  name: string;
  drones: string[];  // Drone agent IDs
  capabilities: string[];
}

// ============================================================================
// Agent Coordinator
// ============================================================================

export class AgentCoordinator {
  private taskQueue: TaskQueue;
  private broadcaster?: WebSocketBroadcaster;
  private princesses: Map<string, PrincessCoordinator>;

  constructor(
    taskQueue: TaskQueue,
    broadcaster?: WebSocketBroadcaster
  ) {
    this.taskQueue = taskQueue;
    this.broadcaster = broadcaster;
    this.princesses = this.initializePrincesses();
  }

  /**
   * Initialize Princess coordinators with their drones.
   */
  private initializePrincesses(): Map<string, PrincessCoordinator> {
    const princesses = new Map<string, PrincessCoordinator>();

    princesses.set('princess-dev', {
      id: 'princess-dev',
      name: 'Princess-Dev',
      drones: ['coder', 'reviewer', 'debugger', 'integration-engineer'],
      capabilities: ['development', 'code-review', 'debugging', 'integration'],
    });

    princesses.set('princess-quality', {
      id: 'princess-quality',
      name: 'Princess-Quality',
      drones: ['tester', 'nasa-enforcer', 'theater-detector', 'fsm-analyzer'],
      capabilities: ['testing', 'compliance', 'quality-assurance', 'validation'],
    });

    princesses.set('princess-coordination', {
      id: 'princess-coordination',
      name: 'Princess-Coordination',
      drones: ['orchestrator', 'planner', 'cost-tracker'],
      capabilities: ['orchestration', 'planning', 'cost-management'],
    });

    princesses.set('princess-documentation', {
      id: 'princess-documentation',
      name: 'Princess-Documentation',
      drones: ['docs-writer', 'spec-writer', 'pseudocode-writer'],
      capabilities: ['documentation', 'specification', 'design'],
    });

    return princesses;
  }

  /**
   * Queen delegates task to appropriate Princess.
   *
   * Decision logic:
   * - Code-related → Princess-Dev
   * - Quality/testing → Princess-Quality
   * - Planning/orchestration → Princess-Coordination
   * - Documentation → Princess-Documentation
   */
  async queenDelegate(delegation: Omit<AgentDelegation, 'to'>): Promise<string> {
    const princess = this.selectPrincess(delegation.task);

    if (!princess) {
      throw new Error('No suitable Princess found for task');
    }

    // Broadcast Queen → Princess delegation
    if (this.broadcaster) {
      await this.broadcaster.broadcastAgentThought({
        agentId: 'queen',
        agentName: 'Queen',
        thought: `Delegating to ${princess.name}: "${delegation.task.substring(0, 50)}..."`,
        taskId: delegation.taskId,
        timestamp: Date.now(),
      });
    }

    // Princess selects drone
    return this.princessDelegate({
      ...delegation,
      from: 'queen',
      to: princess.id,
    });
  }

  /**
   * Princess delegates task to appropriate Drone.
   */
  async princessDelegate(delegation: AgentDelegation): Promise<string> {
    const princess = this.princesses.get(delegation.to);

    if (!princess) {
      throw new Error(`Princess ${delegation.to} not found`);
    }

    // Select best drone for task
    const drone = this.selectDrone(princess, delegation.task);

    // Broadcast Princess → Drone delegation
    if (this.broadcaster) {
      await this.broadcaster.broadcastAgentThought({
        agentId: delegation.to,
        agentName: princess.name,
        thought: `Assigning to ${drone}: "${delegation.task.substring(0, 50)}..."`,
        taskId: delegation.taskId,
        timestamp: Date.now(),
      });
    }

    // Queue task for drone execution
    const agentTask: AgentTask = {
      taskId: delegation.taskId,
      agentId: drone,
      task: delegation.task,
      priority: delegation.priority,
      params: delegation.context,
    };

    return this.taskQueue.addTask(agentTask);
  }

  /**
   * Select Princess based on task content.
   */
  private selectPrincess(task: string): PrincessCoordinator | null {
    const taskLower = task.toLowerCase();

    // Development keywords
    if (taskLower.includes('code') || taskLower.includes('implement') ||
        taskLower.includes('refactor') || taskLower.includes('debug')) {
      return this.princesses.get('princess-dev')!;
    }

    // Quality keywords
    if (taskLower.includes('test') || taskLower.includes('quality') ||
        taskLower.includes('validate') || taskLower.includes('compliance')) {
      return this.princesses.get('princess-quality')!;
    }

    // Documentation keywords
    if (taskLower.includes('document') || taskLower.includes('spec') ||
        taskLower.includes('write') || taskLower.includes('explain')) {
      return this.princesses.get('princess-documentation')!;
    }

    // Planning keywords
    if (taskLower.includes('plan') || taskLower.includes('orchestrate') ||
        taskLower.includes('coordinate') || taskLower.includes('cost')) {
      return this.princesses.get('princess-coordination')!;
    }

    // Default to Princess-Dev
    return this.princesses.get('princess-dev')!;
  }

  /**
   * Select Drone from Princess's team based on task.
   */
  private selectDrone(princess: PrincessCoordinator, task: string): string {
    const taskLower = task.toLowerCase();

    // Princess-Dev drone selection
    if (princess.id === 'princess-dev') {
      if (taskLower.includes('debug')) return 'debugger';
      if (taskLower.includes('review')) return 'reviewer';
      if (taskLower.includes('integrate')) return 'integration-engineer';
      return 'coder';  // Default
    }

    // Princess-Quality drone selection
    if (princess.id === 'princess-quality') {
      if (taskLower.includes('test')) return 'tester';
      if (taskLower.includes('nasa')) return 'nasa-enforcer';
      if (taskLower.includes('theater')) return 'theater-detector';
      if (taskLower.includes('fsm')) return 'fsm-analyzer';
      return 'tester';  // Default
    }

    // Princess-Coordination drone selection
    if (princess.id === 'princess-coordination') {
      if (taskLower.includes('plan')) return 'planner';
      if (taskLower.includes('cost')) return 'cost-tracker';
      return 'orchestrator';  // Default
    }

    // Princess-Documentation drone selection
    if (princess.id === 'princess-documentation') {
      if (taskLower.includes('spec')) return 'spec-writer';
      if (taskLower.includes('pseudocode')) return 'pseudocode-writer';
      return 'docs-writer';  // Default
    }

    // Fallback to first drone
    return princess.drones[0];
  }

  /**
   * Get Princess by ID.
   */
  getPrincess(princessId: string): PrincessCoordinator | undefined {
    return this.princesses.get(princessId);
  }

  /**
   * Get all Princesses.
   */
  getAllPrincesses(): PrincessCoordinator[] {
    return Array.from(this.princesses.values());
  }
}

/**
 * Factory function to create AgentCoordinator.
 */
export function createAgentCoordinator(
  taskQueue: TaskQueue,
  broadcaster?: WebSocketBroadcaster
): AgentCoordinator {
  return new AgentCoordinator(taskQueue, broadcaster);
}
