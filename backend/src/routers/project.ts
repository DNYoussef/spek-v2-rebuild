/**
 * Project Router - CRUD operations for projects
 *
 * Handles:
 * - List projects
 * - Get project by ID
 * - Create new project
 * - Update project
 * - Delete project
 * - Vectorize project (with incremental indexing)
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

export interface Project {
  id: string;
  name: string;
  path: string;
  description?: string;
  lastModified: string;
  status: 'active' | 'completed' | 'archived';
  createdAt: string;
  updatedAt: string;
}

// In-memory storage (temporary - will be replaced with database)
const projects = new Map<string, Project>();

// ============================================================================
// Input Schemas
// ============================================================================

const createProjectSchema = z.object({
  name: z.string().min(1).max(255),
  path: z.string().min(1),
  description: z.string().optional(),
});

const getProjectSchema = z.object({
  id: z.string().uuid(),
});

const updateProjectSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(255).optional(),
  description: z.string().optional(),
  status: z.enum(['active', 'completed', 'archived']).optional(),
});

const deleteProjectSchema = z.object({
  id: z.string().uuid(),
});

// ============================================================================
// Project Router
// ============================================================================

export const projectRouter = createTRPCRouter({
  /**
   * List all projects
   *
   * Returns array of all projects sorted by lastModified (desc)
   */
  list: publicProcedure
    .output(z.array(z.custom<Project>()))
    .query(async () => {
      const allProjects = Array.from(projects.values());

      // Sort by lastModified (newest first)
      return allProjects.sort((a, b) =>
        new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
      );
    }),

  /**
   * Get project by ID
   *
   * Returns single project or null if not found
   */
  get: publicProcedure
    .input(getProjectSchema)
    .output(z.custom<Project>().nullable())
    .query(async ({ input }) => {
      const project = projects.get(input.id);
      return project || null;
    }),

  /**
   * Create new project
   *
   * Generates UUID, timestamps, and default status
   */
  create: publicProcedure
    .input(createProjectSchema)
    .output(z.custom<Project>())
    .mutation(async ({ input }) => {
      const now = new Date().toISOString();

      const project: Project = {
        id: crypto.randomUUID(),
        name: input.name,
        path: input.path,
        description: input.description,
        lastModified: now,
        status: 'active',
        createdAt: now,
        updatedAt: now,
      };

      projects.set(project.id, project);

      return project;
    }),

  /**
   * Update project
   *
   * Updates specified fields and refreshes updatedAt timestamp
   */
  update: publicProcedure
    .input(updateProjectSchema)
    .output(z.custom<Project>())
    .mutation(async ({ input }) => {
      const existing = projects.get(input.id);

      if (!existing) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: `Project ${input.id} not found`,
        });
      }

      const updated: Project = {
        ...existing,
        name: input.name ?? existing.name,
        description: input.description ?? existing.description,
        status: input.status ?? existing.status,
        lastModified: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      projects.set(input.id, updated);

      return updated;
    }),

  /**
   * Delete project
   *
   * Removes project from storage (soft delete could be added later)
   */
  delete: publicProcedure
    .input(deleteProjectSchema)
    .output(z.object({ success: z.boolean() }))
    .mutation(async ({ input }) => {
      const exists = projects.has(input.id);

      if (!exists) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: `Project ${input.id} not found`,
        });
      }

      projects.delete(input.id);

      return { success: true };
    }),

  /**
   * Vectorize project
   *
   * Triggers incremental vectorization with git diff detection
   * (Actual implementation in separate service)
   */
  vectorize: publicProcedure
    .input(z.object({
      projectId: z.string().uuid(),
      forceFullIndex: z.boolean().optional(),
    }))
    .output(z.object({
      taskId: z.string(),
      status: z.enum(['queued', 'running']),
    }))
    .mutation(async ({ input }) => {
      const project = projects.get(input.projectId);

      if (!project) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: `Project ${input.projectId} not found`,
        });
      }

      // TODO: Implement actual vectorization service
      // For now, return mock task ID
      const taskId = crypto.randomUUID();

      return {
        taskId,
        status: 'queued',
      };
    }),
});
