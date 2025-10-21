/**
 * Loop 3 tRPC Router
 * API endpoints for Loop 3 Quality & Finalization system
 *
 * Week 12 Day 5 Implementation
 */

import { z } from 'zod';
import { publicProcedure, createTRPCRouter } from '../trpc';
import { Loop3Orchestrator } from '../services/loop3/Loop3Orchestrator';
import { GitHubIntegrationService } from '../services/loop3/GitHubIntegrationService';
import { ExportService } from '../services/loop3/ExportService';
import * as db from '../db/loop3Operations';

export const loop3Router = createTRPCRouter({
  /**
   * Start Loop 3 workflow
   */
  start: publicProcedure
    .input(z.object({ projectId: z.string() }))
    .mutation(async ({ input }) => {
      const orchestrator = new Loop3Orchestrator(input.projectId);
      const state = await orchestrator.start();
      return { success: true, state };
    }),

  /**
   * Get Loop 3 state
   */
  getState: publicProcedure
    .input(z.object({ projectId: z.string() }))
    .query(async ({ input }) => {
      const state = db.getLoop3StateByProject(input.projectId);
      return state;
    }),

  /**
   * Configure GitHub repository
   */
  configureGitHub: publicProcedure
    .input(z.object({
      projectId: z.string(),
      repoName: z.string().min(1).max(100),
      visibility: z.enum(['public', 'private']),
      description: z.string().min(1).max(350),
      license: z.string().optional()
    }))
    .mutation(async ({ input }) => {
      const githubService = new GitHubIntegrationService();

      // Validate repository name
      const validation = githubService.validateRepoName(input.repoName);
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      // Update orchestrator state
      const state = db.getLoop3StateByProject(input.projectId);
      if (!state) {
        throw new Error('Loop 3 state not found');
      }

      const orchestrator = new Loop3Orchestrator(input.projectId);
      await orchestrator.configureGitHub({
        repoName: input.repoName,
        visibility: input.visibility,
        description: input.description,
        license: input.license
      });

      return { success: true };
    }),

  /**
   * Approve documentation cleanup
   */
  approveDocsCleanup: publicProcedure
    .input(z.object({
      projectId: z.string(),
      approvedFiles: z.array(z.string())
    }))
    .mutation(async ({ input }) => {
      const state = db.getLoop3StateByProject(input.projectId);
      if (!state) {
        throw new Error('Loop 3 state not found');
      }

      const orchestrator = new Loop3Orchestrator(input.projectId);
      await orchestrator.approveDocsCleanup(input.approvedFiles);

      return { success: true };
    }),

  /**
   * Export project
   */
  export: publicProcedure
    .input(z.object({
      projectId: z.string(),
      projectPath: z.string(),
      method: z.enum(['github', 'zip']),
      github: z.object({
        repoName: z.string(),
        visibility: z.enum(['public', 'private']),
        description: z.string(),
        license: z.string().optional()
      }).optional(),
      zip: z.object({
        outputPath: z.string().optional(),
        includeNodeModules: z.boolean().optional(),
        includeDotFiles: z.boolean().optional()
      }).optional()
    }))
    .mutation(async ({ input }) => {
      const exportService = new ExportService();

      const result = await exportService.export({
        method: input.method,
        projectPath: input.projectPath,
        github: input.github,
        zip: input.zip
      });

      if (!result.success) {
        throw new Error(result.error || 'Export failed');
      }

      return result;
    }),

  /**
   * Scan for secrets (pre-flight check for GitHub export)
   */
  scanForSecrets: publicProcedure
    .input(z.object({ projectPath: z.string() }))
    .query(async ({ input }) => {
      const githubService = new GitHubIntegrationService();
      const scanResult = await githubService.scanForSecrets(input.projectPath);
      return scanResult;
    })
});
