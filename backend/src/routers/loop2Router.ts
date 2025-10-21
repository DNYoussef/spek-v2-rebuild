/**
 * Loop 2 tRPC Router
 * MECE → Princess Hive → 3-Stage Audit endpoints
 *
 * Week 9 - Loop 2 Implementation
 */

import { z } from 'zod';
import { publicProcedure, createTRPCRouter } from '../trpc';
import { MECEPhaseDivision, Task } from '../services/loop2/MECEPhaseDivision';
import { PrincessHiveDelegation } from '../services/loop2/PrincessHiveDelegation';
import { ThreeStageAudit } from '../services/loop2/ThreeStageAudit';

const meceDivision = new MECEPhaseDivision();
const princessHive = new PrincessHiveDelegation();
const threeStageAudit = new ThreeStageAudit();

export const loop2Router = createTRPCRouter({
  /**
   * Divide tasks into MECE phases
   */
  divideTasks: publicProcedure
    .input(z.object({
      tasks: z.array(z.object({
        id: z.string(),
        description: z.string(),
        dependencies: z.array(z.string()),
        estimatedHours: z.number(),
        agentType: z.string(),
      })),
    }))
    .mutation(async ({ input }) => {
      const graph = await meceDivision.divideTasks(input.tasks);
      const bottlenecks = meceDivision.identifyBottlenecks(input.tasks);

      return {
        graph,
        bottlenecks,
        totalPhases: graph.phases.length,
        totalTasks: graph.nodes.length,
      };
    }),

  /**
   * Delegate task to Princess
   */
  delegateTask: publicProcedure
    .input(z.object({
      taskId: z.string(),
      taskType: z.string(),
      context: z.object({
        pwd: z.string(),
        projectId: z.string(),
        taskId: z.string(),
        todoList: z.array(z.any()),
        artifacts: z.array(z.any()),
      }),
    }))
    .mutation(async ({ input }) => {
      // Queen → Princess delegation
      const princessId = princessHive.queenToPrincess(input.taskType);

      // Princess → Drone delegation
      const droneId = princessHive.princessToDrone(princessId, input.taskType);

      // Create session
      const session = princessHive.createSession('queen', undefined, input.context);

      // Execute A2A request
      const response = await princessHive.executeA2A({
        targetAgentId: droneId,
        taskId: input.taskId,
        taskType: input.taskType,
        parameters: { session },
        timeout: 30000,
        requester: 'queen',
      });

      return {
        princessId,
        droneId,
        response,
      };
    }),

  /**
   * Execute 3-stage audit
   */
  executeAudit: publicProcedure
    .input(z.object({
      taskId: z.string(),
      code: z.string(),
      projectPath: z.string(),
      withRetry: z.boolean().optional().default(false),
    }))
    .mutation(async ({ input }) => {
      const results = input.withRetry
        ? await threeStageAudit.executeWithRetry(input.taskId, input.code, input.projectPath)
        : await threeStageAudit.executeAudit(input.taskId, input.code, input.projectPath);

      const finalResult = results[results.length - 1];

      return {
        results,
        finalStatus: finalResult.status,
        totalStages: results.length,
        totalExecutionTimeMs: results.reduce((sum, r) => sum + r.executionTimeMs, 0),
      };
    }),

  /**
   * Get Princess status
   */
  getPrincessStatus: publicProcedure
    .input(z.object({
      princessId: z.string(),
    }))
    .query(async ({ input }) => {
      const status = princessHive.getPrincessStatus(input.princessId);

      if (!status) {
        throw new Error(`Princess not found: ${input.princessId}`);
      }

      return status;
    }),

  /**
   * Get all Princesses
   */
  getAllPrincesses: publicProcedure
    .query(async () => {
      return princessHive.getAllPrincesses();
    }),

  /**
   * Get phase progress
   */
  getPhaseProgress: publicProcedure
    .input(z.object({
      projectId: z.string(),
    }))
    .query(async ({ input }) => {
      // This would query database for real implementation
      return {
        projectId: input.projectId,
        phases: [
          { id: 0, name: 'Phase 1', status: 'completed', progress: 100 },
          { id: 1, name: 'Phase 2', status: 'in_progress', progress: 60 },
          { id: 2, name: 'Phase 3', status: 'pending', progress: 0 },
        ],
        overallProgress: 53,
      };
    }),
});
