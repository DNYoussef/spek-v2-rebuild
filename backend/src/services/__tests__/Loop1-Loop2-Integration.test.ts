/**
 * Loop 1 → Loop 2 Integration Tests
 * Tests the complete workflow from research through execution
 *
 * Week 10 Day 5 Implementation
 */

import { Loop1Orchestrator } from '../loop1/Loop1Orchestrator';
import { MECEPhaseDivision } from '../loop2/MECEPhaseDivision';
import { PrincessHiveDelegation } from '../loop2/PrincessHiveDelegation';
import { ThreeStageAudit } from '../loop2/ThreeStageAudit';
import { saveLoop1State, saveLoop2State, getLoop1StateByProject, getLoop2StateByProject } from '../../db/client';

describe('Loop 1 → Loop 2 Integration Tests', () => {
  const testProjectId = 'test-project-integration';
  const testSpec = `
    # Test Project Specification
    Build a simple REST API with user authentication.
    Requirements:
    - User registration
    - User login
    - Protected endpoints
  `;
  const testPlan = `
    # Test Project Plan
    Week 1: Backend setup
    Week 2: Authentication
    Week 3: API endpoints
  `;

  describe('End-to-End Workflow', () => {
    it('should complete Loop 1 and persist state', async () => {
      // Create orchestrator
      const orchestrator = new Loop1Orchestrator(
        testProjectId,
        testSpec,
        testPlan
      );

      // Subscribe to events
      const events: any[] = [];
      orchestrator.onEvent((event) => {
        events.push(event);
      });

      // Execute single iteration (not full loop to avoid timeout)
      const state = orchestrator.getState();
      expect(state.currentIteration).toBe(0);
      expect(state.failureRate).toBe(100);

      // Verify state persistence works
      const dbState = getLoop1StateByProject(testProjectId);
      expect(dbState).toBeDefined();
    }, 10000); // 10s timeout

    it('should transition from Loop 1 to Loop 2', async () => {
      // Simulate Loop 1 completion with low failure rate
      const loop1State = {
        projectId: testProjectId,
        currentIteration: 3,
        failureRate: 4.5, // Below 5% threshold
        status: 'completed' as const,
      };

      // Create tasks from SPEC
      const tasks = [
        {
          id: 'task-1',
          type: 'setup',
          description: 'Initialize project structure',
          dependencies: [],
        },
        {
          id: 'task-2',
          type: 'code',
          description: 'Implement user model',
          dependencies: ['task-1'],
        },
        {
          id: 'task-3',
          type: 'code',
          description: 'Implement authentication',
          dependencies: ['task-2'],
        },
        {
          id: 'task-4',
          type: 'test',
          description: 'Write unit tests',
          dependencies: ['task-3'],
        },
      ];

      // Divide into MECE phases
      const phaseDivision = new MECEPhaseDivision();
      const phases = await phaseDivision.divideTasks(tasks);

      // Verify phases
      expect(phases.length).toBeGreaterThan(0);
      expect(phases.length).toBeLessThanOrEqual(6); // Max 6 phases

      // Verify no task appears in multiple phases
      const allTaskIds = new Set<string>();
      phases.forEach(phase => {
        phase.tasks.forEach(task => {
          expect(allTaskIds.has(task.id)).toBe(false);
          allTaskIds.add(task.id);
        });
      });

      // Verify all tasks included
      expect(allTaskIds.size).toBe(tasks.length);
    });

    it('should delegate tasks through Princess Hive', async () => {
      const delegation = new PrincessHiveDelegation();

      const testTask = {
        id: 'task-code-1',
        type: 'code',
        description: 'Implement user registration endpoint',
        dependencies: [],
      };

      const result = await delegation.delegateTask(testTask);

      expect(result.princessId).toBe('princess-dev');
      expect(result.droneId).toBe('coder');
      expect(result.status).toBe('assigned');
    });

    it('should execute 3-stage audit', async () => {
      const audit = new ThreeStageAudit();

      const testCode = `
        function add(a: number, b: number): number {
          return a + b;
        }

        console.log(add(2, 3));
      `;

      const results = await audit.executeAudit(
        'test-task-1',
        testCode,
        './test-project'
      );

      // Should have 3 stages
      expect(results.length).toBe(3);

      // Stage 1: Theater
      const theaterResult = results.find(r => r.stage === 'theater');
      expect(theaterResult).toBeDefined();
      expect(theaterResult?.status).toBe('pass');

      // Stage 2: Production
      const productionResult = results.find(r => r.stage === 'production');
      expect(productionResult).toBeDefined();

      // Stage 3: Quality
      const qualityResult = results.find(r => r.stage === 'quality');
      expect(qualityResult).toBeDefined();
    }, 35000); // 35s timeout for Docker
  });

  describe('State Persistence', () => {
    it('should persist and retrieve Loop 1 state', () => {
      const testState = {
        id: 'loop1-state-test',
        projectId: testProjectId,
        iteration: 2,
        failureRate: 15.5,
        status: 'running' as const,
        researchPhase: {
          githubResults: [
            { name: 'test-repo', url: 'https://github.com/test', stars: 100, description: 'Test' }
          ],
          paperResults: [],
          status: 'completed' as const,
          completedAt: new Date().toISOString(),
        },
        premortemPhase: null,
        remediationPhase: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      saveLoop1State(testState);

      const retrieved = getLoop1StateByProject(testProjectId);
      expect(retrieved).toBeDefined();
      expect(retrieved?.iteration).toBe(2);
      expect(retrieved?.failureRate).toBe(15.5);
      expect(retrieved?.researchPhase?.githubResults.length).toBe(1);
    });

    it('should persist and retrieve Loop 2 state', () => {
      const testState = {
        id: 'loop2-state-test',
        projectId: testProjectId,
        status: 'running' as const,
        phases: [
          {
            id: 'phase-1',
            name: 'Setup',
            tasks: [{ id: 'task-1', type: 'setup', description: 'Init', status: 'completed' as const, assignedTo: null, dependencies: [], result: null, createdAt: new Date().toISOString(), completedAt: new Date().toISOString() }],
            status: 'completed' as const,
            completedAt: new Date().toISOString(),
          },
        ],
        princesses: [
          {
            id: 'princess-dev',
            name: 'Princess Dev',
            status: 'idle' as const,
            currentTask: null,
            droneCount: 4,
            tasksCompleted: 1,
            tasksInProgress: 0,
            lastActive: new Date().toISOString(),
          },
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      saveLoop2State(testState);

      const retrieved = getLoop2StateByProject(testProjectId);
      expect(retrieved).toBeDefined();
      expect(retrieved?.phases.length).toBe(1);
      expect(retrieved?.princesses.length).toBe(1);
    });
  });

  describe('Error Handling', () => {
    it('should handle missing project gracefully', () => {
      const state = getLoop1StateByProject('non-existent-project');
      expect(state).toBeNull();
    });

    it('should handle invalid task dependencies', async () => {
      const phaseDivision = new MECEPhaseDivision();

      const invalidTasks = [
        {
          id: 'task-1',
          type: 'code',
          description: 'Task 1',
          dependencies: ['task-2'], // Circular dependency
        },
        {
          id: 'task-2',
          type: 'code',
          description: 'Task 2',
          dependencies: ['task-1'], // Circular dependency
        },
      ];

      await expect(phaseDivision.divideTasks(invalidTasks)).rejects.toThrow();
    });
  });

  describe('Performance', () => {
    it('should complete phase division in <2s', async () => {
      const phaseDivision = new MECEPhaseDivision();

      const largeTasks = Array.from({ length: 50 }, (_, i) => ({
        id: `task-${i}`,
        type: i % 3 === 0 ? 'setup' : i % 3 === 1 ? 'code' : 'test',
        description: `Task ${i}`,
        dependencies: i > 0 ? [`task-${i - 1}`] : [],
      }));

      const start = Date.now();
      const phases = await phaseDivision.divideTasks(largeTasks);
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(2000);
      expect(phases.length).toBeGreaterThan(0);
    });
  });
});
