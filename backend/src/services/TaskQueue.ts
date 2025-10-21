/**
 * Task Queue Service - BullMQ Integration
 *
 * Handles async agent task execution with:
 * - Priority queue (P0/P1/P2)
 * - Retry logic with exponential backoff
 * - Job monitoring and progress tracking
 * - WebSocket progress updates
 *
 * Week 8 Day 4
 * Version: 8.0.0
 */

import { Queue, Worker, Job } from 'bullmq';
import { Redis } from 'ioredis';
import type { WebSocketBroadcaster } from './WebSocketBroadcaster';

// ============================================================================
// Types
// ============================================================================

export interface AgentTask {
  taskId: string;
  agentId: string;
  projectId?: string;
  task: string;
  params?: Record<string, unknown>;
  priority: 'P0' | 'P1' | 'P2';
  retryCount?: number;
  maxRetries?: number;
}

export interface TaskResult {
  taskId: string;
  status: 'completed' | 'failed';
  result?: unknown;
  error?: string;
  executionTime: number;
}

export interface TaskProgress {
  taskId: string;
  progress: number;  // 0-100
  message?: string;
  timestamp: number;
}

// ============================================================================
// Task Queue Service
// ============================================================================

export class TaskQueue {
  private queue: Queue<AgentTask>;
  private worker: Worker<AgentTask, TaskResult>;
  private broadcaster?: WebSocketBroadcaster;
  private redis: Redis;

  constructor(
    redisUrl: string,
    broadcaster?: WebSocketBroadcaster
  ) {
    this.redis = new Redis(redisUrl);
    this.broadcaster = broadcaster;

    // Create queue
    this.queue = new Queue<AgentTask>('agent-tasks', {
      connection: this.redis,
      defaultJobOptions: {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 1000,  // 1s, 2s, 4s
        },
        removeOnComplete: 100,  // Keep last 100 completed
        removeOnFail: 500,      // Keep last 500 failed
      },
    });

    // Create worker
    this.worker = new Worker<AgentTask, TaskResult>(
      'agent-tasks',
      async (job) => this.processTask(job),
      {
        connection: this.redis,
        concurrency: 10,  // 10 concurrent tasks
      }
    );

    this.setupWorkerEvents();
  }

  /**
   * Add task to queue.
   *
   * Returns job ID for tracking.
   */
  async addTask(task: AgentTask): Promise<string> {
    const priority = this.getPriorityNumber(task.priority);

    const job = await this.queue.add(
      task.agentId,
      task,
      {
        priority,
        jobId: task.taskId,
      }
    );

    // Broadcast task queued event
    if (this.broadcaster) {
      await this.broadcaster.broadcastTaskProgress({
        taskId: task.taskId,
        agentId: task.agentId,
        projectId: task.projectId,
        status: 'queued',
        progress: 0,
        message: 'Task queued for execution',
        timestamp: Date.now(),
      });
    }

    return job.id!;
  }

  /**
   * Process agent task.
   *
   * Executes task and broadcasts progress updates.
   */
  private async processTask(job: Job<AgentTask>): Promise<TaskResult> {
    const startTime = Date.now();
    const { taskId, agentId, projectId, task, params } = job.data;

    try {
      // Broadcast task started
      if (this.broadcaster) {
        await this.broadcaster.broadcastTaskProgress({
          taskId,
          agentId,
          projectId,
          status: 'running',
          progress: 10,
          message: `${agentId} started processing task`,
          timestamp: Date.now(),
        });
      }

      // Simulate task execution (replace with actual agent execution)
      // TODO: Integrate with actual agent system
      await this.executeAgentTask(job, agentId, task, params);

      // Broadcast task completed
      if (this.broadcaster) {
        await this.broadcaster.broadcastTaskProgress({
          taskId,
          agentId,
          projectId,
          status: 'completed',
          progress: 100,
          message: `${agentId} completed task successfully`,
          timestamp: Date.now(),
        });
      }

      return {
        taskId,
        status: 'completed',
        result: { success: true, message: 'Task completed' },
        executionTime: Date.now() - startTime,
      };
    } catch (error) {
      // Broadcast task failed
      if (this.broadcaster) {
        await this.broadcaster.broadcastTaskProgress({
          taskId,
          agentId,
          projectId,
          status: 'failed',
          progress: 0,
          message: `${agentId} failed: ${(error as Error).message}`,
          timestamp: Date.now(),
        });
      }

      throw error;
    }
  }

  /**
   * Execute agent task (placeholder).
   *
   * TODO: Replace with actual agent coordination system.
   */
  private async executeAgentTask(
    job: Job<AgentTask>,
    agentId: string,
    task: string,
    params?: Record<string, unknown>
  ): Promise<void> {
    // Simulate work with progress updates
    const steps = 5;
    for (let i = 1; i <= steps; i++) {
      await new Promise(resolve => setTimeout(resolve, 500));

      const progress = Math.round((i / steps) * 90) + 10;
      await job.updateProgress(progress);

      // Broadcast progress
      if (this.broadcaster) {
        await this.broadcaster.broadcastTaskProgress({
          taskId: job.data.taskId,
          agentId,
          projectId: job.data.projectId,
          status: 'running',
          progress,
          message: `${agentId} processing (${progress}%)`,
          timestamp: Date.now(),
        });
      }
    }
  }

  /**
   * Setup worker event listeners.
   */
  private setupWorkerEvents(): void {
    this.worker.on('completed', (job, result) => {
      console.log(`✅ Task ${job.id} completed in ${result.executionTime}ms`);
    });

    this.worker.on('failed', (job, error) => {
      console.error(`❌ Task ${job?.id} failed:`, error.message);
    });

    this.worker.on('progress', (job, progress) => {
      console.log(`📊 Task ${job.id} progress: ${progress}%`);
    });
  }

  /**
   * Get task status.
   */
  async getTaskStatus(taskId: string): Promise<{
    status: string;
    progress?: number;
    result?: TaskResult;
  } | null> {
    const job = await this.queue.getJob(taskId);

    if (!job) return null;

    const state = await job.getState();
    const progress = job.progress as number;

    return {
      status: state,
      progress,
      result: state === 'completed' ? job.returnvalue : undefined,
    };
  }

  /**
   * Cancel task.
   */
  async cancelTask(taskId: string): Promise<boolean> {
    const job = await this.queue.getJob(taskId);

    if (!job) return false;

    await job.remove();
    return true;
  }

  /**
   * Get queue metrics.
   */
  async getMetrics(): Promise<{
    waiting: number;
    active: number;
    completed: number;
    failed: number;
  }> {
    const [waiting, active, completed, failed] = await Promise.all([
      this.queue.getWaitingCount(),
      this.queue.getActiveCount(),
      this.queue.getCompletedCount(),
      this.queue.getFailedCount(),
    ]);

    return { waiting, active, completed, failed };
  }

  /**
   * Shutdown queue gracefully.
   */
  async shutdown(): Promise<void> {
    await this.worker.close();
    await this.queue.close();
    await this.redis.quit();
  }

  /**
   * Convert priority to number (lower = higher priority).
   */
  private getPriorityNumber(priority: 'P0' | 'P1' | 'P2'): number {
    switch (priority) {
      case 'P0': return 1;
      case 'P1': return 2;
      case 'P2': return 3;
    }
  }
}

/**
 * Factory function to create TaskQueue.
 */
export function createTaskQueue(
  redisUrl: string,
  broadcaster?: WebSocketBroadcaster
): TaskQueue {
  return new TaskQueue(redisUrl, broadcaster);
}
