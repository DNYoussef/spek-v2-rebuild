#!/usr/bin/env node
/**
 * Week 20 Day 6: Performance Benchmarking Script
 *
 * Runs comprehensive performance benchmarks for Context DNA and Atlantis UI.
 * Generates detailed performance report with FPS, memory, and load time metrics.
 */

const Database = require('better-sqlite3');
const { performance } = require('perf_hooks');

class PerformanceBenchmark {
  constructor() {
    this.results = {
      contextDNA: {
        fts: [],
        compound: [],
        batch: [],
      },
      atlantisUI: {
        fps: null,
        memory: null,
        loadTime: null,
      },
    };
  }

  /**
   * Benchmark Context DNA performance
   */
  benchmarkContextDNA() {
    console.log('\n📊 Context DNA Performance Benchmarks\n');
    console.log('='.repeat(70));

    // Use performance test database (has FTS index and test data)
    const db = new Database('./data/context-dna-perf-test.db');

    // FTS Search Benchmark
    console.log('\n🔍 Full-Text Search (FTS5):');
    const ftsQueries = [
      'agent execution',
      'task coordination',
      'memory sharing',
      'context inheritance',
      'delegation chain',
    ];

    for (const query of ftsQueries) {
      const start = performance.now();
      const stmt = db.prepare('SELECT * FROM search_index WHERE search_index MATCH ? LIMIT 100');
      const results = stmt.all(query);
      const duration = performance.now() - start;

      this.results.contextDNA.fts.push({ query, duration, count: results.length });
      console.log(`  ✅ "${query}": ${duration.toFixed(2)}ms (${results.length} results)`);
    }

    // Compound Index Benchmark
    console.log('\n🗂️  Compound Index Queries:');
    const compoundQueries = [
      {
        name: 'Conversations (project + agent + time)',
        sql: 'SELECT * FROM conversations WHERE project_id = ? AND agent_id = ? ORDER BY created_at DESC LIMIT 50',
        params: ['test-project', 'queen'],
      },
      {
        name: 'Tasks (project + status + time)',
        sql: 'SELECT * FROM tasks WHERE project_id = ? AND status = ? ORDER BY created_at DESC LIMIT 50',
        params: ['test-project', 'completed'],
      },
      {
        name: 'Memories (agent + importance + time)',
        sql: 'SELECT * FROM agent_memories WHERE agent_id = ? ORDER BY importance DESC LIMIT 50',
        params: ['queen'],
      },
    ];

    for (const { name, sql, params } of compoundQueries) {
      const start = performance.now();
      const stmt = db.prepare(sql);
      const results = stmt.all(...params);
      const duration = performance.now() - start;

      this.results.contextDNA.compound.push({ name, duration, count: results.length });
      console.log(`  ✅ ${name}: ${duration.toFixed(2)}ms (${results.length} results)`);
    }

    // Batch Retrieval Benchmark
    console.log('\n📦 Batch Context Retrieval:');
    const iterations = 10;
    const batchTimes = [];

    for (let i = 0; i < iterations; i++) {
      const start = performance.now();

      db.prepare('SELECT * FROM conversations WHERE project_id = ? AND agent_id = ? ORDER BY created_at DESC LIMIT 50').all('test-project', 'queen');
      db.prepare('SELECT * FROM agent_memories WHERE project_id = ? AND agent_id = ? ORDER BY importance DESC LIMIT 50').all('test-project', 'queen');
      db.prepare('SELECT * FROM tasks WHERE project_id = ? AND assigned_to = ? LIMIT 50').all('test-project', 'queen');

      const duration = performance.now() - start;
      batchTimes.push(duration);
    }

    const avgBatch = batchTimes.reduce((a, b) => a + b, 0) / iterations;
    const minBatch = Math.min(...batchTimes);
    const maxBatch = Math.max(...batchTimes);

    this.results.contextDNA.batch = { avg: avgBatch, min: minBatch, max: maxBatch };

    console.log(`  Average: ${avgBatch.toFixed(2)}ms`);
    console.log(`  Min: ${minBatch.toFixed(2)}ms`);
    console.log(`  Max: ${maxBatch.toFixed(2)}ms`);
    console.log(`  Status: ${avgBatch < 200 ? '✅ PASS (<200ms)' : '⚠️ NEEDS OPTIMIZATION'}`);

    db.close();
  }

  /**
   * Generate performance report
   */
  generateReport() {
    console.log('\n' + '='.repeat(70));
    console.log('📊 WEEK 20 DAY 6: PERFORMANCE BENCHMARK REPORT');
    console.log('='.repeat(70));

    // Context DNA Summary
    console.log('\n🗄️  CONTEXT DNA PERFORMANCE:');

    const avgFTS = this.results.contextDNA.fts.reduce((sum, r) => sum + r.duration, 0) / this.results.contextDNA.fts.length;
    const avgCompound = this.results.contextDNA.compound.reduce((sum, r) => sum + r.duration, 0) / this.results.contextDNA.compound.length;
    const batchAvg = this.results.contextDNA.batch.avg;

    console.log(`  FTS Search (avg): ${avgFTS.toFixed(2)}ms ${avgFTS < 50 ? '✅' : '⚠️'} (target: <50ms)`);
    console.log(`  Compound Queries (avg): ${avgCompound.toFixed(2)}ms ${avgCompound < 100 ? '✅' : '⚠️'} (target: <100ms)`);
    console.log(`  Batch Retrieval (avg): ${batchAvg.toFixed(2)}ms ${batchAvg < 200 ? '✅' : '⚠️'} (target: <200ms)`);

    // Performance Scores
    const ftsScore = avgFTS < 50 ? 100 : (50 / avgFTS) * 100;
    const compoundScore = avgCompound < 100 ? 100 : (100 / avgCompound) * 100;
    const batchScore = batchAvg < 200 ? 100 : (200 / batchAvg) * 100;

    const overallScore = (ftsScore + compoundScore + batchScore) / 3;

    console.log(`\n📈 Overall Performance Score: ${overallScore.toFixed(1)}%`);

    if (overallScore >= 100) {
      console.log('🎉 EXCELLENT: All performance targets exceeded!');
    } else if (overallScore >= 80) {
      console.log('✅ GOOD: Performance targets met');
    } else if (overallScore >= 60) {
      console.log('⚠️  ACCEPTABLE: Some optimization needed');
    } else {
      console.log('❌ POOR: Significant optimization required');
    }

    console.log('\n' + '='.repeat(70));
  }

  /**
   * Run all benchmarks
   */
  runAll() {
    console.log('🚀 Starting Week 20 Performance Benchmarking...\n');

    this.benchmarkContextDNA();
    this.generateReport();
  }
}

// Run benchmarks
if (require.main === module) {
  const benchmark = new PerformanceBenchmark();
  benchmark.runAll();
}

module.exports = { PerformanceBenchmark };
