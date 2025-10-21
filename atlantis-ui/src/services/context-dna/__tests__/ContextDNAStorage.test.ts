/**
 * Context DNA Storage Tests
 *
 * Integration tests for Context DNA storage and retrieval.
 */

import { ContextDNAStorage } from '../ContextDNAStorage';
import { MemoryRetrieval } from '../MemoryRetrieval';
import { Project, Task, Conversation, AgentMemory } from '../types';
import { join } from 'path';
import { existsSync, unlinkSync } from 'fs';

describe('ContextDNAStorage', () => {
  let storage: ContextDNAStorage;
  const testDbPath = join(__dirname, 'test-context-dna.db');

  beforeEach(() => {
    // Clean up previous test database
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
    storage = new ContextDNAStorage(testDbPath);
  });

  afterEach(() => {
    storage.close();
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
  });

  describe('Project Storage', () => {
    it('should save and retrieve a project', () => {
      const project: Project = {
        id: 'proj-1',
        name: 'Test Project',
        description: 'A test project',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };

      storage.saveProject(project);
      const retrieved = storage.getProject('proj-1');

      expect(retrieved).toBeTruthy();
      expect(retrieved?.name).toBe('Test Project');
    });
  });

  describe('Task Storage', () => {
    it('should save and retrieve tasks', () => {
      // Save project first
      const project: Project = {
        id: 'proj-1',
        name: 'Test Project',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };
      storage.saveProject(project);

      // Save task
      const task: Task = {
        id: 'task-1',
        projectId: 'proj-1',
        description: 'Implement feature X',
        status: 'pending',
        createdAt: new Date(),
      };

      storage.saveTask(task);
      const tasks = storage.getTasksForProject('proj-1');

      expect(tasks).toHaveLength(1);
      expect(tasks[0].description).toBe('Implement feature X');
    });

    it('should support task search', () => {
      const project: Project = {
        id: 'proj-1',
        name: 'Test',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };
      storage.saveProject(project);

      const task: Task = {
        id: 'task-1',
        projectId: 'proj-1',
        description: 'Implement authentication system',
        status: 'pending',
        createdAt: new Date(),
      };

      storage.saveTask(task);

      const results = storage.search({
        query: 'authentication',
        projectId: 'proj-1',
      });

      expect(results.length).toBeGreaterThan(0);
    });
  });

  describe('Conversation Storage', () => {
    it('should save and retrieve conversations', () => {
      const project: Project = {
        id: 'proj-1',
        name: 'Test',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };
      storage.saveProject(project);

      const conversation: Conversation = {
        id: 'conv-1',
        projectId: 'proj-1',
        role: 'user',
        content: 'Please implement feature X',
        createdAt: new Date(),
      };

      storage.saveConversation(conversation);
      const conversations = storage.getConversationsForProject('proj-1');

      expect(conversations).toHaveLength(1);
      expect(conversations[0].content).toBe('Please implement feature X');
    });
  });

  describe('Agent Memory', () => {
    it('should save and retrieve agent memories', () => {
      const project: Project = {
        id: 'proj-1',
        name: 'Test',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };
      storage.saveProject(project);

      const memory: AgentMemory = {
        id: 'mem-1',
        agentId: 'queen',
        projectId: 'proj-1',
        memoryType: 'success_pattern',
        content: 'Breaking tasks into smaller chunks improved success rate',
        importance: 0.9,
        createdAt: new Date(),
        lastAccessedAt: new Date(),
        accessCount: 0,
      };

      storage.saveAgentMemory(memory);
      const memories = storage.getAgentMemories('queen', 'proj-1', 0.5);

      expect(memories).toHaveLength(1);
      expect(memories[0].memoryType).toBe('success_pattern');
    });
  });

  describe('Retention Policy', () => {
    it('should clean up old entries', () => {
      // Create old project (35 days ago)
      const oldDate = new Date();
      oldDate.setDate(oldDate.getDate() - 35);

      const oldProject: Project = {
        id: 'old-proj',
        name: 'Old Project',
        createdAt: oldDate,
        lastAccessedAt: oldDate,
      };

      storage.saveProject(oldProject);

      // Create recent project
      const newProject: Project = {
        id: 'new-proj',
        name: 'New Project',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };

      storage.saveProject(newProject);

      // Clean up
      const result = storage.cleanupOldEntries();

      expect(result.deleted).toBeGreaterThan(0);

      // Verify old project is gone
      const retrieved = storage.getProject('old-proj');
      expect(retrieved).toBeNull();

      // Verify new project still exists
      const stillExists = storage.getProject('new-proj');
      expect(stillExists).toBeTruthy();
    });
  });

  describe('Statistics', () => {
    it('should return accurate statistics', () => {
      const project: Project = {
        id: 'proj-1',
        name: 'Test',
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };
      storage.saveProject(project);

      const task: Task = {
        id: 'task-1',
        projectId: 'proj-1',
        description: 'Test task',
        status: 'pending',
        createdAt: new Date(),
      };
      storage.saveTask(task);

      const stats = storage.getStats();

      expect(stats.totalProjects).toBe(1);
      expect(stats.totalTasks).toBe(1);
    });
  });
});

describe('MemoryRetrieval', () => {
  let storage: ContextDNAStorage;
  let retrieval: MemoryRetrieval;
  const testDbPath = join(__dirname, 'test-memory.db');

  beforeEach(() => {
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
    storage = new ContextDNAStorage(testDbPath);
    retrieval = new MemoryRetrieval();
  });

  afterEach(() => {
    storage.close();
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
  });

  it('should retrieve context within 200ms', async () => {
    const project: Project = {
      id: 'proj-1',
      name: 'Test',
      createdAt: new Date(),
      lastAccessedAt: new Date(),
    };
    storage.saveProject(project);

    const task: Task = {
      id: 'task-1',
      projectId: 'proj-1',
      description: 'Implement authentication with OAuth2',
      status: 'pending',
      createdAt: new Date(),
    };
    storage.saveTask(task);

    const result = await retrieval.retrieveContext('authentication', {
      projectId: 'proj-1',
    });

    expect(result.retrievalTimeMs).toBeLessThan(200);
    expect(result.tasks.length).toBeGreaterThan(0);
  });

  it('should find success patterns', async () => {
    const project: Project = {
      id: 'proj-1',
      name: 'Test',
      createdAt: new Date(),
      lastAccessedAt: new Date(),
    };
    storage.saveProject(project);

    await retrieval.storeAgentMemory(
      'queen',
      'proj-1',
      'success_pattern',
      'Breaking large tasks into smaller chunks improved success',
      0.9
    );

    const patterns = await retrieval.getSuccessPatterns('queen', 'proj-1');

    expect(patterns.length).toBeGreaterThan(0);
    expect(patterns[0].importance).toBe(0.9);
  });
});
