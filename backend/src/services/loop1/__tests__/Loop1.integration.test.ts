/**
 * Loop 1 Integration Tests
 * Tests complete workflow from research to iteration
 *
 * Week 9 - Integration Testing
 */

import { Loop1Orchestrator } from '../Loop1Orchestrator';
import { ResearchAgent } from '../ResearchAgent';
import { PremortemAgent } from '../PremortemAgent';

describe('Loop 1 Integration', () => {
  describe('ResearchAgent', () => {
    it('should search GitHub and return artifacts', async () => {
      const agent = new ResearchAgent();
      const result = await agent.searchGitHub('react hooks', 10);

      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeLessThanOrEqual(10);

      if (result.length > 0) {
        expect(result[0]).toHaveProperty('id');
        expect(result[0]).toHaveProperty('type', 'github_repo');
        expect(result[0]).toHaveProperty('relevanceScore');
      }
    });

    it('should search papers and return artifacts', async () => {
      const agent = new ResearchAgent();
      const result = await agent.searchPapers('machine learning', 5);

      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeLessThanOrEqual(5);

      if (result.length > 0) {
        expect(result[0]).toHaveProperty('id');
        expect(result[0]).toHaveProperty('type', 'academic_paper');
        expect(result[0]).toHaveProperty('relevanceScore');
      }
    });
  });

  describe('PremortemAgent', () => {
    it('should execute pre-mortem and return failure scenarios', async () => {
      const agent = new PremortemAgent();

      const spec = `
        Build a web application with React and Node.js.
        Requirements: User authentication, real-time updates, data persistence.
      `;

      const plan = `
        Week 1: Setup infrastructure
        Week 2: Build authentication
        Week 3: Implement real-time features
        Week 4: Add data persistence
      `;

      const result = await agent.executePremortem(spec, plan, []);

      expect(result).toBeDefined();
      expect(result).toHaveProperty('scenarios');
      expect(result).toHaveProperty('failureRate');
      expect(result).toHaveProperty('riskScore');
      expect(result.failureRate).toBeGreaterThanOrEqual(0);
      expect(result.failureRate).toBeLessThanOrEqual(100);
    });

    it('should identify aggressive timeline risk', async () => {
      const agent = new PremortemAgent();

      const plan = `
        This project will be completed in 4 weeks.
        No contingency buffer included.
      `;

      const result = await agent.executePremortem('Test spec', plan, []);

      const timelineRisk = result.scenarios.find(s =>
        s.description.toLowerCase().includes('timeline')
      );

      expect(timelineRisk).toBeDefined();
      expect(timelineRisk?.priority).toMatch(/P1|P2/);
    });
  });

  describe('Loop1Orchestrator', () => {
    it('should create orchestrator with initial state', () => {
      const orchestrator = new Loop1Orchestrator(
        'test-project',
        'test spec',
        'test plan'
      );

      const state = orchestrator.getState();

      expect(state.projectId).toBe('test-project');
      expect(state.currentIteration).toBe(0);
      expect(state.maxIterations).toBe(10);
      expect(state.targetFailureRate).toBe(5);
      expect(state.status).toBe('running');
    });

    it('should emit events during execution', async () => {
      const orchestrator = new Loop1Orchestrator(
        'test-project',
        'test spec',
        'test plan'
      );

      const events: string[] = [];

      orchestrator.onEvent((event) => {
        events.push(event.type);
      });

      // Execute single iteration (will fail without real APIs)
      try {
        await orchestrator.execute();
      } catch (error) {
        // Expected to fail without real API keys
      }

      // Should have attempted to emit some events
      expect(events.length).toBeGreaterThan(0);
    });

    it('should pause and resume execution', () => {
      const orchestrator = new Loop1Orchestrator(
        'test-project',
        'test spec',
        'test plan'
      );

      orchestrator.pause();
      expect(orchestrator.getState().status).toBe('paused');

      orchestrator.resume();
      expect(orchestrator.getState().status).toBe('running');
    });
  });
});
