#!/usr/bin/env node
/**
 * Context DNA Performance Benchmark Runner
 *
 * Runs performance benchmarks for Context DNA storage and retrieval.
 * Reports metrics for search, retrieval, and retention operations.
 *
 * Usage:
 *   node scripts/benchmark-context-dna.js [--db-path path/to/db]
 */

const { PerformanceBenchmark } = require('../dist/services/context-dna/PerformanceBenchmark');
const { ContextDNAStorage } = require('../dist/services/context-dna/ContextDNAStorage');

async function main() {
  const args = process.argv.slice(2);
  const dbPathIndex = args.indexOf('--db-path');
  const dbPath = dbPathIndex >= 0 ? args[dbPathIndex + 1] : ':memory:';

  console.log('🔬 Context DNA Performance Benchmark');
  console.log(`Database: ${dbPath === ':memory:' ? 'In-Memory' : dbPath}`);
  console.log('');

  try {
    const storage = new ContextDNAStorage(dbPath);
    const benchmark = new PerformanceBenchmark(storage);

    console.log('Setting up test data...');
    const suite = await benchmark.runAll();

    const report = benchmark.formatReport(suite);
    console.log(report);

    storage.close();

    // Exit with success/failure code
    process.exit(suite.failed > 0 ? 1 : 0);
  } catch (error) {
    console.error('❌ Benchmark failed:', error);
    process.exit(1);
  }
}

main();
