/**
 * Loop 2 Integration Tests
 * Tests MECE, Princess Hive, and 3-Stage Audit
 *
 * Week 9 - Integration Testing
 */

import { MECEPhaseDivision, Task } from '../MECEPhaseDivision';
import { PrincessHiveDelegation } from '../PrincessHiveDelegation';
import { ThreeStageAudit } from '../ThreeStageAudit';

describe('Loop 2 Integration', () => {
  describe('MECEPhaseDivision', () => {
    it('should divide tasks into MECE phases', async () => {
      const division = new MECEPhaseDivision();

      const tasks: Task[] = [
        { id: '1', description: 'Task 1', dependencies: [], estimatedHours: 2, agentType: 'coder' },
        { id: '2', description: 'Task 2', dependencies: ['1'], estimatedHours: 3, agentType: 'coder' },
        { id: '3', description: 'Task 3', dependencies: ['1'], estimatedHours: 2, agentType: 'tester' },
        { id: '4', description: 'Task 4', dependencies: ['2', '3'], estimatedHours: 4, agentType: 'reviewer' },
      ];

      const result = await division.divideTasks(tasks);

      expect(result.nodes).toHaveLength(4);
      expect(result.phases).toBeDefined();
      expect(result.phases.length).toBeGreaterThan(0);
      expect(result.phases.length).toBeLessThanOrEqual(6);
    });

    it('should perform topological sort correctly', async () => {
      const division = new MECEPhaseDivision();

      const tasks: Task[] = [
        { id: 'C', description: 'Task C', dependencies: ['A', 'B'], estimatedHours: 1, agentType: 'coder' },
        { id: 'B', description: 'Task B', dependencies: ['A'], estimatedHours: 1, agentType: 'coder' },
        { id: 'A', description: 'Task A', dependencies: [], estimatedHours: 1, agentType: 'coder' },
      ];

      const result = await division.divideTasks(tasks);

      // A should come before B, B before C
      const aIndex = result.nodes.findIndex(t => t.id === 'A');
      const bIndex = result.nodes.findIndex(t => t.id === 'B');
      const cIndex = result.nodes.findIndex(t => t.id === 'C');

      expect(aIndex).toBeLessThan(bIndex);
      expect(bIndex).toBeLessThan(cIndex);
    });

    it('should identify bottleneck tasks', async () => {
      const division = new MECEPhaseDivision();

      const tasks: Task[] = [
        { id: 'bottleneck', description: 'Bottleneck', dependencies: [], estimatedHours: 1, agentType: 'coder' },
        { id: 'task1', description: 'Task 1', dependencies: ['bottleneck'], estimatedHours: 1, agentType: 'coder' },
        { id: 'task2', description: 'Task 2', dependencies: ['bottleneck'], estimatedHours: 1, agentType: 'coder' },
        { id: 'task3', description: 'Task 3', dependencies: ['bottleneck'], estimatedHours: 1, agentType: 'coder' },
      ];

      const bottlenecks = division.identifyBottlenecks(tasks);

      expect(bottlenecks).toContain('bottleneck');
      expect(bottlenecks.length).toBeGreaterThan(0);
    });
  });

  describe('PrincessHiveDelegation', () => {
    it('should initialize all Princess agents', () => {
      const hive = new PrincessHiveDelegation();
      const princesses = hive.getAllPrincesses();

      expect(princesses).toHaveLength(4);
      expect(princesses.map(p => p.id)).toContain('princess-dev');
      expect(princesses.map(p => p.id)).toContain('princess-quality');
      expect(princesses.map(p => p.id)).toContain('princess-coordination');
      expect(princesses.map(p => p.id)).toContain('princess-documentation');
    });

    it('should delegate Queen to Princess correctly', () => {
      const hive = new PrincessHiveDelegation();

      expect(hive.queenToPrincess('code')).toBe('princess-dev');
      expect(hive.queenToPrincess('test')).toBe('princess-quality');
      expect(hive.queenToPrincess('document')).toBe('princess-documentation');
      expect(hive.queenToPrincess('plan')).toBe('princess-coordination');
    });

    it('should delegate Princess to Drone correctly', () => {
      const hive = new PrincessHiveDelegation();

      expect(hive.princessToDrone('princess-dev', 'code')).toBe('coder');
      expect(hive.princessToDrone('princess-dev', 'review')).toBe('reviewer');
      expect(hive.princessToDrone('princess-quality', 'test')).toBe('tester');
      expect(hive.princessToDrone('princess-quality', 'enforce')).toBe('nasa-enforcer');
    });

    it('should execute A2A request successfully', async () => {
      const hive = new PrincessHiveDelegation();
      const session = hive.createSession('queen', undefined, {
        pwd: '/test',
        projectId: 'test-project',
        taskId: 'test-task',
        todoList: [],
        artifacts: [],
      });

      const response = await hive.executeA2A({
        targetAgentId: 'princess-dev',
        taskId: 'test-task',
        taskType: 'code',
        parameters: { session },
        timeout: 30000,
        requester: 'queen',
      });

      expect(response.status).toBe('completed');
      expect(response.taskId).toBe('test-task');
      expect(response.executionTimeMs).toBeGreaterThan(0);
    });
  });

  describe('ThreeStageAudit', () => {
    it('should execute complete 3-stage audit', async () => {
      const audit = new ThreeStageAudit();

      const code = `
        function add(a, b) {
          return a + b;
        }
      `;

      const results = await audit.executeAudit('test-task', code, '/test/path');

      expect(results).toBeDefined();
      expect(results.length).toBeGreaterThan(0);
      expect(results.length).toBeLessThanOrEqual(3);

      const stages = results.map(r => r.stage);
      expect(stages).toContain('theater');
    });

    it('should detect theater patterns', async () => {
      const audit = new ThreeStageAudit();

      const codeWithTheater = `
        function test() {
          // TODO: Implement this
          raise NotImplementedError("Coming soon")
          return mock_result
        }
      `;

      const results = await audit.executeAudit('test-task', codeWithTheater, '/test/path');
      const theaterResult = results.find(r => r.stage === 'theater');

      expect(theaterResult).toBeDefined();
      expect(theaterResult?.details).toHaveProperty('patterns');
    });

    it('should retry on failure', async () => {
      const audit = new ThreeStageAudit();

      const code = `
        function broken() {
          // This will fail theater detection
          // TODO: Fix this
        }
      `;

      const results = await audit.executeWithRetry('test-task', code, '/test/path');

      expect(results).toBeDefined();
      expect(results.length).toBeGreaterThan(0);
    });
  });
});
