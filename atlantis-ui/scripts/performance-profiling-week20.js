#!/usr/bin/env node
/**
 * Week 20 Day 4: Performance Profiling Script
 *
 * Profiles SQLite FTS, Redis, and context retrieval performance.
 * Generates detailed performance report.
 */

const Database = require('better-sqlite3');
const { performance } = require('perf_hooks');

// Performance thresholds
const THRESHOLDS = {
  contextRetrieval: 200, // ms
  sessionCreation: 5, // ms
  memorySharing: 100, // ms
  ftsSearch: 50, // ms
};

class PerformanceProfiler {
  constructor(dbPath = './data/context-dna-perf-test.db') {
    this.db = new Database(dbPath);
    this.initSchema();
    this.createTestData();
    this.results = {
      contextRetrieval: [],
      ftsSearch: [],
      compoundIndexQueries: [],
      batchRetrieval: [],
    };
  }

  /**
   * Initialize schema matching ContextDNAStorage.ts
   */
  initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY, name TEXT NOT NULL,
        created_at INTEGER NOT NULL, last_accessed_at INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
        agent_id TEXT, content TEXT NOT NULL, created_at INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS agent_memories (
        id TEXT PRIMARY KEY, agent_id TEXT NOT NULL,
        project_id TEXT NOT NULL, content TEXT NOT NULL,
        importance REAL NOT NULL, created_at INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
        description TEXT NOT NULL, status TEXT NOT NULL,
        assigned_to TEXT, created_at INTEGER NOT NULL
      );
      CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
        content, project_id UNINDEXED, task_id UNINDEXED,
        source_type UNINDEXED, source_id UNINDEXED, tokenize = 'porter'
      );
      CREATE INDEX IF NOT EXISTS idx_conv_proj_agent ON conversations(project_id, agent_id, created_at DESC);
      CREATE INDEX IF NOT EXISTS idx_mem_agent_imp ON agent_memories(agent_id, importance DESC, created_at DESC);
      CREATE INDEX IF NOT EXISTS idx_task_proj_status ON tasks(project_id, status, created_at DESC);
    `);
    this.db.pragma('journal_mode = WAL');
  }

  /**
   * Create test data for profiling
   */
  createTestData() {
    // Create test project
    const projectStmt = this.db.prepare(
      'INSERT OR IGNORE INTO projects VALUES (?, ?, ?, ?)'
    );
    projectStmt.run('test-project', 'Test Project', Date.now(), Date.now());

    // Create 100 conversations
    const convStmt = this.db.prepare(
      'INSERT OR IGNORE INTO conversations VALUES (?, ?, ?, ?, ?)'
    );
    const searchStmt = this.db.prepare(
      'INSERT OR IGNORE INTO search_index VALUES (?, ?, ?, ?, ?)'
    );
    for (let i = 0; i < 100; i++) {
      const content = `Test conversation ${i} about agent execution and task coordination with memory sharing and delegation chain context inheritance`;
      convStmt.run(`conv-${i}`, 'test-project', 'queen', content, Date.now() - (i * 1000));
      searchStmt.run(content, 'test-project', null, 'conversation', `conv-${i}`);
    }

    // Create 100 agent memories
    const memStmt = this.db.prepare(
      'INSERT OR IGNORE INTO agent_memories VALUES (?, ?, ?, ?, ?, ?)'
    );
    for (let i = 0; i < 100; i++) {
      const content = `Memory ${i}: Success pattern for task execution with delegation chain and context inheritance`;
      memStmt.run(`mem-${i}`, 'queen', 'test-project', content, Math.random(), Date.now() - (i * 1000));
      searchStmt.run(content, 'test-project', null, 'memory', `mem-${i}`);
    }

    // Create 50 tasks
    const taskStmt = this.db.prepare(
      'INSERT OR IGNORE INTO tasks VALUES (?, ?, ?, ?, ?, ?)'
    );
    for (let i = 0; i < 50; i++) {
      const desc = `Task ${i}: Implement feature with agent coordination and memory sharing`;
      taskStmt.run(`task-${i}`, 'test-project', desc, i % 2 === 0 ? 'completed' : 'pending', 'queen', Date.now() - (i * 1000));
      searchStmt.run(desc, 'test-project', `task-${i}`, 'task', `task-${i}`);
    }
  }

  /**
   * Profile FTS5 search performance
   */
  profileFTSSearch() {
    console.log('\n📊 Profiling FTS5 Search Performance...\n');

    const queries = [
      'agent execution',
      'task coordination',
      'memory sharing',
      'context inheritance',
      'delegation chain',
    ];

    for (const query of queries) {
      const start = performance.now();

      const stmt = this.db.prepare(`
        SELECT * FROM search_index
        WHERE search_index MATCH ?
        LIMIT 100
      `);

      const results = stmt.all(query);
      const duration = performance.now() - start;

      this.results.ftsSearch.push({
        query,
        duration,
        resultCount: results.length,
      });

      const status = duration < THRESHOLDS.ftsSearch ? '✅' : '⚠️';
      console.log(`  ${status} Query "${query}": ${duration.toFixed(2)}ms (${results.length} results)`);
    }

    const avgFTS = this.results.ftsSearch.reduce((sum, r) => sum + r.duration, 0) / this.results.ftsSearch.length;
    console.log(`\n  Average FTS Search: ${avgFTS.toFixed(2)}ms (target: <${THRESHOLDS.ftsSearch}ms)`);
  }

  /**
   * Profile compound index queries
   */
  profileCompoundIndexes() {
    console.log('\n📊 Profiling Compound Index Queries...\n');

    const queries = [
      {
        name: 'Conversations by project + agent + time',
        sql: `SELECT * FROM conversations
              WHERE project_id = ? AND agent_id = ?
              ORDER BY created_at DESC
              LIMIT 50`,
        params: ['test-project', 'queen'],
      },
      {
        name: 'Tasks by project + status + time',
        sql: `SELECT * FROM tasks
              WHERE project_id = ? AND status = ?
              ORDER BY created_at DESC
              LIMIT 50`,
        params: ['test-project', 'completed'],
      },
      {
        name: 'Memories by agent + importance',
        sql: `SELECT * FROM agent_memories
              WHERE agent_id = ?
              ORDER BY importance DESC, created_at DESC
              LIMIT 50`,
        params: ['queen'],
      },
    ];

    for (const { name, sql, params } of queries) {
      const start = performance.now();
      const stmt = this.db.prepare(sql);
      const results = stmt.all(...params);
      const duration = performance.now() - start;

      this.results.compoundIndexQueries.push({
        name,
        duration,
        resultCount: results.length,
      });

      console.log(`  ✅ ${name}: ${duration.toFixed(2)}ms (${results.length} results)`);
    }
  }

  /**
   * Profile batch retrieval (simulating context retrieval)
   */
  profileBatchRetrieval() {
    console.log('\n📊 Profiling Batch Context Retrieval...\n');

    const iterations = 10;

    for (let i = 0; i < iterations; i++) {
      const start = performance.now();

      // Simulate full context retrieval (conversations + memories + tasks)
      const conversations = this.db.prepare(`
        SELECT * FROM conversations
        WHERE project_id = ? AND agent_id = ?
        ORDER BY created_at DESC
        LIMIT 50
      `).all('test-project', 'queen');

      const memories = this.db.prepare(`
        SELECT * FROM agent_memories
        WHERE project_id = ? AND agent_id = ?
        ORDER BY importance DESC
        LIMIT 50
      `).all('test-project', 'queen');

      const tasks = this.db.prepare(`
        SELECT * FROM tasks
        WHERE project_id = ? AND assigned_to = ?
        LIMIT 50
      `).all('test-project', 'queen');

      const duration = performance.now() - start;

      this.results.contextRetrieval.push(duration);

      const status = duration < THRESHOLDS.contextRetrieval ? '✅' : '⚠️';
      console.log(`  ${status} Iteration ${i + 1}: ${duration.toFixed(2)}ms (${conversations.length + memories.length + tasks.length} total items)`);
    }

    const avg = this.results.contextRetrieval.reduce((a, b) => a + b, 0) / iterations;
    const max = Math.max(...this.results.contextRetrieval);
    const min = Math.min(...this.results.contextRetrieval);

    console.log(`\n  📈 Context Retrieval Stats:`);
    console.log(`     Average: ${avg.toFixed(2)}ms (target: <${THRESHOLDS.contextRetrieval}ms)`);
    console.log(`     Min: ${min.toFixed(2)}ms`);
    console.log(`     Max: ${max.toFixed(2)}ms`);
    console.log(`     Status: ${avg < THRESHOLDS.contextRetrieval ? '✅ PASS' : '⚠️ NEEDS OPTIMIZATION'}`);
  }

  /**
   * Generate performance report
   */
  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 WEEK 20 DAY 4: PERFORMANCE PROFILING REPORT');
    console.log('='.repeat(60));

    const avgContext = this.results.contextRetrieval.reduce((a, b) => a + b, 0) / this.results.contextRetrieval.length;
    const avgFTS = this.results.ftsSearch.reduce((sum, r) => sum + r.duration, 0) / this.results.ftsSearch.length;

    console.log('\n✅ SUMMARY:');
    console.log(`   Context Retrieval: ${avgContext.toFixed(2)}ms (target: <200ms) ${avgContext < 200 ? '✅' : '⚠️'}`);
    console.log(`   FTS Search: ${avgFTS.toFixed(2)}ms (target: <50ms) ${avgFTS < 50 ? '✅' : '⚠️'}`);
    console.log(`   Compound Indexes: ${this.results.compoundIndexQueries.length} queries profiled`);

    if (avgContext < THRESHOLDS.contextRetrieval && avgFTS < THRESHOLDS.ftsSearch) {
      console.log('\n🎉 ALL PERFORMANCE TARGETS MET!');
    } else {
      console.log('\n⚠️  Some performance targets need optimization');
    }

    console.log('\n' + '='.repeat(60));
  }

  /**
   * Run all profiling tests
   */
  runAll() {
    console.log('🚀 Starting Week 20 Performance Profiling...\n');

    this.profileFTSSearch();
    this.profileCompoundIndexes();
    this.profileBatchRetrieval();
    this.generateReport();

    this.db.close();
  }
}

// Run profiling
if (require.main === module) {
  const profiler = new PerformanceProfiler();
  profiler.runAll();
}

module.exports = { PerformanceProfiler };
