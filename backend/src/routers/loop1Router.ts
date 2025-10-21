/**
 * Loop 1 tRPC Router
 * Research → Pre-mortem → Remediation endpoints
 *
 * Week 9 - Loop 1 Implementation
 */

import { z } from 'zod';
import { publicProcedure, createTRPCRouter } from '../trpc';
import { Loop1Orchestrator } from '../services/loop1/Loop1Orchestrator';
import { ResearchAgent } from '../services/loop1/ResearchAgent';

// In-memory storage for demo (replace with database)
const loop1Sessions = new Map<string, Loop1Orchestrator>();

export const loop1Router = createTRPCRouter({
  /**
   * Start Loop 1 workflow
   */
  start: publicProcedure
    .input(z.object({
      projectId: z.string(),
      spec: z.string(),
      plan: z.string(),
      githubToken: z.string().optional(),
    }))
    .mutation(async ({ input }) => {
      const orchestrator = new Loop1Orchestrator(
        input.projectId,
        input.spec,
        input.plan,
        input.githubToken
      );

      loop1Sessions.set(input.projectId, orchestrator);

      // Start execution in background
      orchestrator.execute().catch(console.error);

      return {
        projectId: input.projectId,
        status: 'started',
        timestamp: Date.now(),
      };
    }),

  /**
   * Get Loop 1 status
   */
  getStatus: publicProcedure
    .input(z.object({
      projectId: z.string(),
    }))
    .query(async ({ input }) => {
      const orchestrator = loop1Sessions.get(input.projectId);

      if (!orchestrator) {
        throw new Error(`Loop 1 session not found: ${input.projectId}`);
      }

      return orchestrator.getState();
    }),

  /**
   * Pause Loop 1
   */
  pause: publicProcedure
    .input(z.object({
      projectId: z.string(),
    }))
    .mutation(async ({ input }) => {
      const orchestrator = loop1Sessions.get(input.projectId);

      if (!orchestrator) {
        throw new Error(`Loop 1 session not found: ${input.projectId}`);
      }

      orchestrator.pause();

      return {
        projectId: input.projectId,
        status: 'paused',
        timestamp: Date.now(),
      };
    }),

  /**
   * Resume Loop 1
   */
  resume: publicProcedure
    .input(z.object({
      projectId: z.string(),
    }))
    .mutation(async ({ input }) => {
      const orchestrator = loop1Sessions.get(input.projectId);

      if (!orchestrator) {
        throw new Error(`Loop 1 session not found: ${input.projectId}`);
      }

      orchestrator.resume();

      // Continue execution
      orchestrator.execute().catch(console.error);

      return {
        projectId: input.projectId,
        status: 'resumed',
        timestamp: Date.now(),
      };
    }),

  /**
   * Execute research phase only
   */
  executeResearch: publicProcedure
    .input(z.object({
      projectDescription: z.string(),
      githubToken: z.string().optional(),
      githubLimit: z.number().optional().default(100),
      paperLimit: z.number().optional().default(50),
    }))
    .mutation(async ({ input }) => {
      const researchAgent = new ResearchAgent(input.githubToken);

      const result = await researchAgent.executeResearch(
        input.projectDescription,
        input.githubLimit,
        input.paperLimit
      );

      return result;
    }),

  /**
   * Get failure rate history
   */
  getFailureRateHistory: publicProcedure
    .input(z.object({
      projectId: z.string(),
    }))
    .query(async ({ input }) => {
      const orchestrator = loop1Sessions.get(input.projectId);

      if (!orchestrator) {
        throw new Error(`Loop 1 session not found: ${input.projectId}`);
      }

      const state = orchestrator.getState();

      return {
        history: state.failureRateHistory,
        currentRate: state.currentFailureRate,
        targetRate: state.targetFailureRate,
        currentIteration: state.currentIteration,
        maxIterations: state.maxIterations,
      };
    }),
});
