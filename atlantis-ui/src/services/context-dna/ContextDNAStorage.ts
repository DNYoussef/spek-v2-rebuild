/**
 * Context DNA Storage Service
 *
 * SQLite-based storage for 30-day project context retention.
 * Provides fast full-text search, cross-agent memory sharing,
 * and automatic cleanup of old entries.
 *
 * Features:
 * - 30-day automatic retention policy
 * - Full-text search with FTS5
 * - Artifact S3 path references (not full files)
 * - Cross-agent memory coordination
 * - <200ms context lookup target
 */

import Database from 'better-sqlite3';
import { join } from 'path';
import {
  Project,
  Task,
  Conversation,
  ArtifactReference,
  AgentMemory,
  SearchQuery,
  SearchResult,
  ContextDNAStats,
  RetentionPolicy,
} from './types';

export class ContextDNAStorage {
  private db: Database.Database;
  private readonly retentionDays: number = 30;

  constructor(dbPath?: string) {
    const path = dbPath || join(process.cwd(), 'data', 'context-dna.db');
    this.db = new Database(path);
    this.initializeSchema();
    this.enableWAL();
  }

  /**
   * Initialize database schema with FTS5 for full-text search
   */
  private initializeSchema(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        repository_url TEXT,
        created_at INTEGER NOT NULL,
        last_accessed_at INTEGER NOT NULL,
        metadata TEXT
      );

      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_to TEXT,
        princess_id TEXT,
        drone_id TEXT,
        created_at INTEGER NOT NULL,
        completed_at INTEGER,
        result TEXT,
        metadata TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
      );

      CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT,
        role TEXT NOT NULL,
        agent_id TEXT,
        content TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        metadata TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(task_id) REFERENCES tasks(id)
      );

      CREATE TABLE IF NOT EXISTS artifacts (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        s3_path TEXT,
        local_path TEXT,
        url TEXT,
        size_bytes INTEGER,
        created_at INTEGER NOT NULL,
        metadata TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(task_id) REFERENCES tasks(id)
      );

      CREATE TABLE IF NOT EXISTS agent_memories (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        task_id TEXT,
        memory_type TEXT NOT NULL,
        content TEXT NOT NULL,
        importance REAL NOT NULL,
        created_at INTEGER NOT NULL,
        last_accessed_at INTEGER NOT NULL,
        access_count INTEGER DEFAULT 0,
        metadata TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(task_id) REFERENCES tasks(id)
      );

      CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
        content,
        project_id UNINDEXED,
        task_id UNINDEXED,
        source_type UNINDEXED,
        source_id UNINDEXED,
        tokenize = 'porter'
      );

      CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
      CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_id);
      CREATE INDEX IF NOT EXISTS idx_artifacts_project ON artifacts(project_id);
      CREATE INDEX IF NOT EXISTS idx_agent_memories_project ON agent_memories(project_id);
      CREATE INDEX IF NOT EXISTS idx_agent_memories_agent ON agent_memories(agent_id);

      -- Week 20 Day 4: Compound indexes for <200ms retrieval optimization
      CREATE INDEX IF NOT EXISTS idx_conversations_project_agent_time
        ON conversations(project_id, agent_id, created_at DESC);

      CREATE INDEX IF NOT EXISTS idx_tasks_project_status_time
        ON tasks(project_id, status, created_at DESC);

      CREATE INDEX IF NOT EXISTS idx_memories_agent_importance_time
        ON agent_memories(agent_id, importance DESC, created_at DESC);

      CREATE INDEX IF NOT EXISTS idx_memories_project_type_importance
        ON agent_memories(project_id, memory_type, importance DESC);
    `);
  }

  /**
   * Enable Write-Ahead Logging for better concurrency
   */
  private enableWAL(): void {
    this.db.pragma('journal_mode = WAL');
  }

  /**
   * Store a project in Context DNA
   */
  saveProject(project: Project): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO projects (
        id, name, description, repository_url,
        created_at, last_accessed_at, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      project.id,
      project.name,
      project.description || null,
      project.repositoryUrl || null,
      project.createdAt.getTime(),
      project.lastAccessedAt.getTime(),
      JSON.stringify(project.metadata || {})
    );
  }

  /**
   * Get a project by ID
   */
  getProject(projectId: string): Project | null {
    const stmt = this.db.prepare('SELECT * FROM projects WHERE id = ?');
    const row = stmt.get(projectId) as any;

    if (!row) return null;

    return {
      id: row.id,
      name: row.name,
      description: row.description,
      repositoryUrl: row.repository_url,
      createdAt: new Date(row.created_at),
      lastAccessedAt: new Date(row.last_accessed_at),
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
    };
  }

  /**
   * Store a task in Context DNA
   */
  saveTask(task: Task): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO tasks (
        id, project_id, description, status,
        assigned_to, princess_id, drone_id,
        created_at, completed_at, result, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      task.id,
      task.projectId,
      task.description,
      task.status,
      task.assignedTo || null,
      task.princessId || null,
      task.droneId || null,
      task.createdAt.getTime(),
      task.completedAt?.getTime() || null,
      task.result ? JSON.stringify(task.result) : null,
      JSON.stringify(task.metadata || {})
    );

    // Index in FTS5 for search
    this.indexContent(task.id, task.projectId, task.description, 'task');
  }

  /**
   * Get tasks for a project
   */
  getTasksForProject(projectId: string, limit = 100): Task[] {
    const stmt = this.db.prepare(`
      SELECT * FROM tasks
      WHERE project_id = ?
      ORDER BY created_at DESC
      LIMIT ?
    `);

    const rows = stmt.all(projectId, limit) as any[];

    return rows.map((row) => this.rowToTask(row));
  }

  /**
   * Store a conversation message
   */
  saveConversation(conversation: Conversation): void {
    const stmt = this.db.prepare(`
      INSERT INTO conversations (
        id, project_id, task_id, role, agent_id,
        content, created_at, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      conversation.id,
      conversation.projectId,
      conversation.taskId || null,
      conversation.role,
      conversation.agentId || null,
      conversation.content,
      conversation.createdAt.getTime(),
      JSON.stringify(conversation.metadata || {})
    );

    // Index in FTS5
    const source = conversation.taskId || conversation.projectId;
    this.indexContent(conversation.id, conversation.projectId, conversation.content, 'conversation');
  }

  /**
   * Get conversation history for a project
   */
  getConversationsForProject(projectId: string, limit = 100): Conversation[] {
    const stmt = this.db.prepare(`
      SELECT * FROM conversations
      WHERE project_id = ?
      ORDER BY created_at DESC
      LIMIT ?
    `);

    const rows = stmt.all(projectId, limit) as any[];

    return rows.map((row) => this.rowToConversation(row));
  }

  /**
   * Store an artifact reference (S3 path, NOT full file)
   */
  saveArtifact(artifact: ArtifactReference): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO artifacts (
        id, project_id, task_id, type, name,
        s3_path, local_path, url, size_bytes,
        created_at, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      artifact.id,
      artifact.projectId,
      artifact.taskId || null,
      artifact.type,
      artifact.name,
      artifact.s3Path || null,
      artifact.localPath || null,
      artifact.url || null,
      artifact.sizeBytes || null,
      artifact.createdAt.getTime(),
      JSON.stringify(artifact.metadata || {})
    );
  }

  /**
   * Get artifacts for a project
   */
  getArtifactsForProject(projectId: string, limit = 100): ArtifactReference[] {
    const stmt = this.db.prepare(`
      SELECT * FROM artifacts
      WHERE project_id = ?
      ORDER BY created_at DESC
      LIMIT ?
    `);

    const rows = stmt.all(projectId, limit) as any[];

    return rows.map((row) => this.rowToArtifact(row));
  }

  /**
   * Store agent memory (success/failure patterns, optimizations)
   */
  saveAgentMemory(memory: AgentMemory): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO agent_memories (
        id, agent_id, project_id, task_id, memory_type,
        content, importance, created_at, last_accessed_at,
        access_count, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      memory.id,
      memory.agentId,
      memory.projectId,
      memory.taskId || null,
      memory.memoryType,
      memory.content,
      memory.importance,
      memory.createdAt.getTime(),
      memory.lastAccessedAt.getTime(),
      memory.accessCount,
      JSON.stringify(memory.metadata || {})
    );

    // Index for search
    this.indexContent(memory.id, memory.projectId, memory.content, 'memory');
  }

  /**
   * Get agent memories with importance threshold
   */
  getAgentMemories(
    agentId: string,
    projectId?: string,
    minImportance = 0.5,
    limit = 50
  ): AgentMemory[] {
    const stmt = this.db.prepare(`
      SELECT * FROM agent_memories
      WHERE agent_id = ?
        AND (? IS NULL OR project_id = ?)
        AND importance >= ?
      ORDER BY importance DESC, last_accessed_at DESC
      LIMIT ?
    `);

    const rows = stmt.all(agentId, projectId, projectId, minImportance, limit) as any[];

    return rows.map((row) => this.rowToAgentMemory(row));
  }

  /**
   * Full-text search across all content
   */
  search(query: SearchQuery): SearchResult<Conversation | Task | AgentMemory>[] {
    const conditions: string[] = [];
    const params: any[] = [];

    if (query.projectId) {
      conditions.push('project_id = ?');
      params.push(query.projectId);
    }

    if (query.taskId) {
      conditions.push('task_id = ?');
      params.push(query.taskId);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const stmt = this.db.prepare(`
      SELECT
        source_id, source_type, content,
        rank as score
      FROM search_index
      ${whereClause}
        AND search_index MATCH ?
      ORDER BY rank
      LIMIT ?
    `);

    params.push(query.query);
    params.push(query.limit || 20);

    const rows = stmt.all(...params) as any[];

    return rows.map((row) => ({
      item: this.loadSourceItem(row.source_id, row.source_type),
      score: -row.score, // FTS5 ranks are negative
      snippet: this.extractSnippet(row.content, query.query),
    })) as SearchResult<any>[];
  }

  /**
   * Clean up entries older than retention period
   */
  cleanupOldEntries(): { deleted: number } {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - this.retentionDays);
    const cutoffTimestamp = cutoffDate.getTime();

    const deletedProjects = this.db.prepare(`
      DELETE FROM projects WHERE created_at < ?
    `).run(cutoffTimestamp);

    const deletedTasks = this.db.prepare(`
      DELETE FROM tasks WHERE created_at < ?
    `).run(cutoffTimestamp);

    const deletedConversations = this.db.prepare(`
      DELETE FROM conversations WHERE created_at < ?
    `).run(cutoffTimestamp);

    const deletedArtifacts = this.db.prepare(`
      DELETE FROM artifacts WHERE created_at < ?
    `).run(cutoffTimestamp);

    const deletedMemories = this.db.prepare(`
      DELETE FROM agent_memories WHERE created_at < ?
    `).run(cutoffTimestamp);

    const total =
      deletedProjects.changes +
      deletedTasks.changes +
      deletedConversations.changes +
      deletedArtifacts.changes +
      deletedMemories.changes;

    return { deleted: total };
  }

  /**
   * Get storage statistics
   */
  getStats(): ContextDNAStats {
    const stats = this.db.prepare(`
      SELECT
        (SELECT COUNT(*) FROM projects) as total_projects,
        (SELECT COUNT(*) FROM tasks) as total_tasks,
        (SELECT COUNT(*) FROM conversations) as total_conversations,
        (SELECT COUNT(*) FROM artifacts) as total_artifacts,
        (SELECT COUNT(*) FROM agent_memories) as total_memories,
        (SELECT MIN(created_at) FROM projects) as oldest,
        (SELECT MAX(created_at) FROM projects) as newest
    `).get() as any;

    return {
      totalProjects: stats.total_projects || 0,
      totalTasks: stats.total_tasks || 0,
      totalConversations: stats.total_conversations || 0,
      totalArtifacts: stats.total_artifacts || 0,
      totalAgentMemories: stats.total_memories || 0,
      oldestEntry: stats.oldest ? new Date(stats.oldest) : new Date(),
      newestEntry: stats.newest ? new Date(stats.newest) : new Date(),
      storageBytes: this.getDatabaseSize(),
    };
  }

  /**
   * Get database file size in bytes
   */
  private getDatabaseSize(): number {
    const result = this.db.prepare(`SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()`).get() as any;
    return result?.size || 0;
  }

  /**
   * Index content in FTS5 table
   */
  private indexContent(
    sourceId: string,
    projectId: string,
    content: string,
    sourceType: string
  ): void {
    const stmt = this.db.prepare(`
      INSERT INTO search_index (content, project_id, task_id, source_type, source_id)
      VALUES (?, ?, NULL, ?, ?)
    `);

    stmt.run(content, projectId, sourceType, sourceId);
  }

  /**
   * Load source item by ID and type
   */
  private loadSourceItem(sourceId: string, sourceType: string): any {
    switch (sourceType) {
      case 'task':
        return this.rowToTask(
          this.db.prepare('SELECT * FROM tasks WHERE id = ?').get(sourceId)
        );
      case 'conversation':
        return this.rowToConversation(
          this.db.prepare('SELECT * FROM conversations WHERE id = ?').get(sourceId)
        );
      case 'memory':
        return this.rowToAgentMemory(
          this.db.prepare('SELECT * FROM agent_memories WHERE id = ?').get(sourceId)
        );
      default:
        return null;
    }
  }

  /**
   * Extract snippet around search query
   */
  private extractSnippet(content: string, query: string, contextLength = 100): string {
    const index = content.toLowerCase().indexOf(query.toLowerCase());
    if (index === -1) return content.substring(0, contextLength);

    const start = Math.max(0, index - contextLength / 2);
    const end = Math.min(content.length, index + query.length + contextLength / 2);

    let snippet = content.substring(start, end);
    if (start > 0) snippet = '...' + snippet;
    if (end < content.length) snippet = snippet + '...';

    return snippet;
  }

  /**
   * Convert database row to Task object
   */
  private rowToTask(row: any): Task {
    return {
      id: row.id,
      projectId: row.project_id,
      description: row.description,
      status: row.status,
      assignedTo: row.assigned_to,
      princessId: row.princess_id,
      droneId: row.drone_id,
      createdAt: new Date(row.created_at),
      completedAt: row.completed_at ? new Date(row.completed_at) : undefined,
      result: row.result ? JSON.parse(row.result) : undefined,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
    };
  }

  /**
   * Convert database row to Conversation object
   */
  private rowToConversation(row: any): Conversation {
    return {
      id: row.id,
      projectId: row.project_id,
      taskId: row.task_id,
      role: row.role,
      agentId: row.agent_id,
      content: row.content,
      createdAt: new Date(row.created_at),
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
    };
  }

  /**
   * Convert database row to ArtifactReference object
   */
  private rowToArtifact(row: any): ArtifactReference {
    return {
      id: row.id,
      projectId: row.project_id,
      taskId: row.task_id,
      type: row.type,
      name: row.name,
      s3Path: row.s3_path,
      localPath: row.local_path,
      url: row.url,
      sizeBytes: row.size_bytes,
      createdAt: new Date(row.created_at),
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
    };
  }

  /**
   * Convert database row to AgentMemory object
   */
  private rowToAgentMemory(row: any): AgentMemory {
    return {
      id: row.id,
      agentId: row.agent_id,
      projectId: row.project_id,
      taskId: row.task_id,
      memoryType: row.memory_type,
      content: row.content,
      importance: row.importance,
      createdAt: new Date(row.created_at),
      lastAccessedAt: new Date(row.last_accessed_at),
      accessCount: row.access_count,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
    };
  }

  /**
   * Close database connection
   */
  close(): void {
    this.db.close();
  }
}

/**
 * Singleton instance
 */
let instance: ContextDNAStorage | null = null;

export function getContextDNAStorage(): ContextDNAStorage {
  if (!instance) {
    instance = new ContextDNAStorage();
  }
  return instance;
}
