/**
 * App Router - Main tRPC router
 *
 * Combines all sub-routers:
 * - project: Project CRUD operations
 * - agent: Agent execution and management
 * - task: Task status and progress tracking
 * - loop1: Loop 1 Research & Pre-mortem
 * - loop2: Loop 2 Execution & Audit
 *
 * Week 8 Day 1 + Week 9
 * Version: 8.0.0
 */

import { createTRPCRouter } from '../trpc';
import { projectRouter } from './project';
import { agentRouter } from './agent';
import { taskRouter } from './task';
import { loop1Router } from './loop1Router';
import { loop2Router } from './loop2Router';

// ============================================================================
// App Router
// ============================================================================

/**
 * Main tRPC router combining all sub-routers.
 *
 * Structure:
 * - /api/trpc/project.*
 * - /api/trpc/agent.*
 * - /api/trpc/task.*
 * - /api/trpc/loop1.*
 * - /api/trpc/loop2.*
 */
export const appRouter = createTRPCRouter({
  project: projectRouter,
  agent: agentRouter,
  task: taskRouter,
  loop1: loop1Router,
  loop2: loop2Router,
});

// Export AppRouter type for frontend
export type AppRouter = typeof appRouter;
