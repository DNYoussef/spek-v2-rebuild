/**
 * Task Router - Task status and progress tracking
 *
 * Handles:
 * - Get task status
 * - Get task result
 * - Cancel task
 * - List tasks by project
 * - Stream task updates (via WebSocket)
 *
 * Week 8 Day 1
 * Version: 8.0.0
 */

import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '../trpc';
import { TRPCError } from '@trpc/server';

// ============================================================================
// Types
// ============================================================================

export interface Task {
  taskId: string;
  agentId: string;
  projectId?: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress?: number;  // 0-100
  result?: unknown;
  error?: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
}

// In-memory task storage (temporary - will use BullMQ later)
const tasks = new Map<string, Task>();

// ============================================================================
// Input Schemas
// ============================================================================

const getTaskStatusSchema = z.object({
  taskId: z.string().uuid(),
});

const cancelTaskSchema = z.object({
  taskId: z.string().uuid(),
});

const listTasksByProjectSchema = z.object({
  projectId: z.string().uuid(),
  status: z.enum(['queued', 'running', 'completed', 'failed', 'cancelled']).optional(),
});

// ============================================================================
// Task Router
// ============================================================================

export const taskRouter = createTRPCRouter({
  /**
   * Get task status
   *
   * Returns current status, progress, and result
   */
  status: publicProcedure
    .input(getTaskStatusSchema)
    .output(z.custom<Task>().nullable())
    .query(async ({ input }) => {
      const task = tasks.get(input.taskId);
      return task || null;
    }),

  /**
   * Cancel task
   *
   * Marks task as cancelled (best effort, may not stop running task)
   */
  cancel: publicProcedure
    .input(cancelTaskSchema)
    .output(z.object({ success: z.boolean() }))
    .mutation(async ({ input }) => {
      const task = tasks.get(input.taskId);

      if (!task) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: `Task ${input.taskId} not found`,
        });
      }

      if (task.status === 'completed' || task.status === 'failed') {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: `Cannot cancel ${task.status} task`,
        });
      }

      task.status = 'cancelled';
      task.completedAt = new Date().toISOString();

      tasks.set(input.taskId, task);

      return { success: true };
    }),

  /**
   * List tasks by project
   *
   * Returns all tasks for a project, optionally filtered by status
   */
  listByProject: publicProcedure
    .input(listTasksByProjectSchema)
    .output(z.array(z.custom<Task>()))
    .query(async ({ input }) => {
      const allTasks = Array.from(tasks.values());

      let filtered = allTasks.filter((task) => task.projectId === input.projectId);

      if (input.status) {
        filtered = filtered.filter((task) => task.status === input.status);
      }

      // Sort by createdAt (newest first)
      return filtered.sort((a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
    }),

  /**
   * Get active tasks
   *
   * Returns all tasks currently queued or running
   */
  getActive: publicProcedure
    .output(z.array(z.custom<Task>()))
    .query(async () => {
      const allTasks = Array.from(tasks.values());
      return allTasks.filter(
        (task) => task.status === 'queued' || task.status === 'running'
      );
    }),

  /**
   * Get task result
   *
   * Returns task result if completed, throws error if failed
   */
  getResult: publicProcedure
    .input(getTaskStatusSchema)
    .output(z.unknown())
    .query(async ({ input }) => {
      const task = tasks.get(input.taskId);

      if (!task) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: `Task ${input.taskId} not found`,
        });
      }

      if (task.status === 'failed') {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: task.error || 'Task failed',
        });
      }

      if (task.status !== 'completed') {
        throw new TRPCError({
          code: 'BAD_REQUEST',
          message: `Task is ${task.status}, not completed`,
        });
      }

      return task.result;
    }),
});

/**
 * Helper: Create task entry
 *
 * Used by agent router when executing tasks
 */
export function createTask(params: {
  taskId: string;
  agentId: string;
  projectId?: string;
}): Task {
  const task: Task = {
    ...params,
    status: 'queued',
    createdAt: new Date().toISOString(),
  };

  tasks.set(task.taskId, task);
  return task;
}

/**
 * Helper: Update task status
 *
 * Used by task execution service to update progress
 */
export function updateTask(
  taskId: string,
  updates: Partial<Omit<Task, 'taskId' | 'agentId' | 'createdAt'>>
): Task {
  const task = tasks.get(taskId);

  if (!task) {
    throw new Error(`Task ${taskId} not found`);
  }

  const updated = { ...task, ...updates };
  tasks.set(taskId, updated);

  return updated;
}
