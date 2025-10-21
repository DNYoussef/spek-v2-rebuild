/**
 * Agent Router - Agent execution and management
 *
 * Handles:
 * - List agents (22 agents in Phase 1)
 * - Execute agent task
 * - Get agent status
 * - Stream agent thoughts (via WebSocket)
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

export interface Agent {
  id: string;
  type: 'core' | 'swarm' | 'specialized';
  name: string;
  role: string;
  status: 'idle' | 'active' | 'error';
  capabilities: string[];
  currentTaskId?: string;
}

// ============================================================================
// Agent Registry (22 Agents from Week 5)
// ============================================================================

const agentRegistry: Agent[] = [
  // Core Agents (5)
  {
    id: 'queen',
    type: 'core',
    name: 'Queen',
    role: 'Top-level coordinator',
    status: 'idle',
    capabilities: ['orchestration', 'delegation', 'decision-making'],
  },
  {
    id: 'coder',
    type: 'core',
    name: 'Coder',
    role: 'Code implementation',
    status: 'idle',
    capabilities: ['coding', 'refactoring', 'implementation'],
  },
  {
    id: 'researcher',
    type: 'core',
    name: 'Researcher',
    role: 'Research and analysis',
    status: 'idle',
    capabilities: ['research', 'analysis', 'documentation-review'],
  },
  {
    id: 'tester',
    type: 'core',
    name: 'Tester',
    role: 'Test creation and validation',
    status: 'idle',
    capabilities: ['testing', 'validation', 'qa'],
  },
  {
    id: 'reviewer',
    type: 'core',
    name: 'Reviewer',
    role: 'Code review and quality',
    status: 'idle',
    capabilities: ['review', 'quality-assurance', 'best-practices'],
  },

  // Swarm Coordinators (3)
  {
    id: 'princess-dev',
    type: 'swarm',
    name: 'Princess-Dev',
    role: 'Development coordination',
    status: 'idle',
    capabilities: ['dev-coordination', 'task-delegation'],
  },
  {
    id: 'princess-quality',
    type: 'swarm',
    name: 'Princess-Quality',
    role: 'Quality assurance coordination',
    status: 'idle',
    capabilities: ['qa-coordination', 'audit-oversight'],
  },
  {
    id: 'princess-coordination',
    type: 'swarm',
    name: 'Princess-Coordination',
    role: 'Task coordination',
    status: 'idle',
    capabilities: ['task-coordination', 'workflow-management'],
  },

  // Specialized Agents (14) - subset shown for brevity
  {
    id: 'architect',
    type: 'specialized',
    name: 'Architect',
    role: 'System architecture',
    status: 'idle',
    capabilities: ['architecture', 'design', 'patterns'],
  },
  {
    id: 'debugger',
    type: 'specialized',
    name: 'Debugger',
    role: 'Bug fixing and debugging',
    status: 'idle',
    capabilities: ['debugging', 'troubleshooting', 'root-cause-analysis'],
  },
  {
    id: 'docs-writer',
    type: 'specialized',
    name: 'Docs-Writer',
    role: 'Documentation generation',
    status: 'idle',
    capabilities: ['documentation', 'technical-writing', 'api-docs'],
  },
  {
    id: 'security-manager',
    type: 'specialized',
    name: 'Security-Manager',
    role: 'Security validation',
    status: 'idle',
    capabilities: ['security-audit', 'vulnerability-scanning', 'compliance'],
  },
  {
    id: 'cost-tracker',
    type: 'specialized',
    name: 'Cost-Tracker',
    role: 'Budget monitoring',
    status: 'idle',
    capabilities: ['cost-tracking', 'budget-analysis', 'optimization'],
  },
  {
    id: 'theater-detector',
    type: 'specialized',
    name: 'Theater-Detector',
    role: 'Mock code detection',
    status: 'idle',
    capabilities: ['theater-detection', 'code-quality', 'ast-analysis'],
  },
  {
    id: 'nasa-enforcer',
    type: 'specialized',
    name: 'NASA-Enforcer',
    role: 'NASA Rule 10 compliance',
    status: 'idle',
    capabilities: ['nasa-compliance', 'code-standards', 'enforcement'],
  },
];

// ============================================================================
// Input Schemas
// ============================================================================

const executeAgentSchema = z.object({
  agentId: z.string(),
  task: z.string().min(1),
  params: z.record(z.unknown()).optional(),
  projectId: z.string().uuid().optional(),
});

const getAgentStatusSchema = z.object({
  agentId: z.string(),
});

// ============================================================================
// Agent Router
// ============================================================================

export const agentRouter = createTRPCRouter({
  /**
   * List all agents
   *
   * Returns array of all 22 agents with current status
   */
  list: publicProcedure
    .output(z.array(z.custom<Agent>()))
    .query(async () => {
      return agentRegistry;
    }),

  /**
   * Get agent by ID
   *
   * Returns specific agent details
   */
  get: publicProcedure
    .input(getAgentStatusSchema)
    .output(z.custom<Agent>().nullable())
    .query(async ({ input }) => {
      const agent = agentRegistry.find((a) => a.id === input.agentId);
      return agent || null;
    }),

  /**
   * Execute agent task
   *
   * Queues task for execution and returns task ID
   * Actual execution happens via BullMQ task queue
   */
  execute: publicProcedure
    .input(executeAgentSchema)
    .output(z.object({
      taskId: z.string().uuid(),
      status: z.enum(['queued', 'running']),
      agentId: z.string(),
    }))
    .mutation(async ({ input }) => {
      const agent = agentRegistry.find((a) => a.id === input.agentId);

      if (!agent) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: `Agent ${input.agentId} not found`,
        });
      }

      // TODO: Queue task in BullMQ
      // For now, generate mock task ID
      const taskId = crypto.randomUUID();

      // Update agent status (in-memory for now)
      agent.status = 'active';
      agent.currentTaskId = taskId;

      return {
        taskId,
        status: 'queued',
        agentId: input.agentId,
      };
    }),

  /**
   * List agents by type
   *
   * Returns agents filtered by type (core, swarm, specialized)
   */
  listByType: publicProcedure
    .input(z.object({
      type: z.enum(['core', 'swarm', 'specialized']),
    }))
    .output(z.array(z.custom<Agent>()))
    .query(async ({ input }) => {
      return agentRegistry.filter((agent) => agent.type === input.type);
    }),

  /**
   * Get active agents
   *
   * Returns all agents currently executing tasks
   */
  getActive: publicProcedure
    .output(z.array(z.custom<Agent>()))
    .query(async () => {
      return agentRegistry.filter((agent) => agent.status === 'active');
    }),
});
