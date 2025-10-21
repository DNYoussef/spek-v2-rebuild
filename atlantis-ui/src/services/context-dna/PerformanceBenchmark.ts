/**
 * Performance Benchmark for Context DNA
 *
 * Tests Context DNA storage and retrieval performance.
 * Target: <200ms context lookup, <100ms full-text search.
 *
 * Features:
 * - Load testing with synthetic data
 * - Search performance measurement
 * - Memory usage tracking
 * - Detailed performance reports
 */

import { ContextDNAStorage } from './ContextDNAStorage';
import { MemoryRetrieval } from './MemoryRetrieval';
import { Project, Task, Conversation, AgentMemory } from './types';

export interface BenchmarkResult {
  testName: string;
  iterations: number;
  totalTimeMs: number;
  avgTimeMs: number;
  minTimeMs: number;
  maxTimeMs: number;
  p50TimeMs: number;
  p95TimeMs: number;
  p99TimeMs: number;
  success: boolean;
  target?: number;
}

export interface BenchmarkSuite {
  suiteName: string;
  results: BenchmarkResult[];
  totalTimeMs: number;
  passed: number;
  failed: number;
}

export class PerformanceBenchmark {
  private storage: ContextDNAStorage;
  private retrieval: MemoryRetrieval;

  constructor(storage: ContextDNAStorage) {
    this.storage = storage;
    this.retrieval = new MemoryRetrieval();
  }

  /**
   * Run complete benchmark suite
   */
  async runAll(): Promise<BenchmarkSuite> {
    const suiteStartTime = performance.now();
    const results: BenchmarkResult[] = [];

    // Setup test data
    await this.setupTestData(1000);

    // Run benchmarks
    results.push(await this.benchmarkProjectRetrieval());
    results.push(await this.benchmarkTaskRetrieval());
    results.push(await this.benchmarkFullTextSearch());
    results.push(await this.benchmarkContextRetrieval());
    results.push(await this.benchmarkAgentMemoryRetrieval());

    const totalTimeMs = performance.now() - suiteStartTime;
    const passed = results.filter((r) => r.success).length;
    const failed = results.filter((r) => !r.success).length;

    return {
      suiteName: 'Context DNA Performance Benchmark',
      results,
      totalTimeMs,
      passed,
      failed,
    };
  }

  /**
   * Benchmark project retrieval
   * Target: <50ms per project
   */
  async benchmarkProjectRetrieval(): Promise<BenchmarkResult> {
    const iterations = 100;
    const times: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const projectId = `bench-project-${Math.floor(Math.random() * 10)}`;
      const start = performance.now();
      this.storage.getProject(projectId);
      times.push(performance.now() - start);
    }

    return this.calculateResult('Project Retrieval', times, 50);
  }

  /**
   * Benchmark task retrieval
   * Target: <100ms for 100 tasks
   */
  async benchmarkTaskRetrieval(): Promise<BenchmarkResult> {
    const iterations = 50;
    const times: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const projectId = `bench-project-${Math.floor(Math.random() * 10)}`;
      const start = performance.now();
      this.storage.getTasksForProject(projectId, 100);
      times.push(performance.now() - start);
    }

    return this.calculateResult('Task Retrieval (100 tasks)', times, 100);
  }

  /**
   * Benchmark full-text search
   * Target: <100ms
   */
  async benchmarkFullTextSearch(): Promise<BenchmarkResult> {
    const iterations = 50;
    const times: number[] = [];
    const queries = [
      'authentication',
      'implement feature',
      'bug fix',
      'performance optimization',
      'refactor code',
    ];

    for (let i = 0; i < iterations; i++) {
      const query = queries[i % queries.length];
      const start = performance.now();
      this.storage.search({ query, limit: 20 });
      times.push(performance.now() - start);
    }

    return this.calculateResult('Full-Text Search', times, 100);
  }

  /**
   * Benchmark context retrieval
   * Target: <200ms
   */
  async benchmarkContextRetrieval(): Promise<BenchmarkResult> {
    const iterations = 50;
    const times: number[] = [];
    const queries = [
      'implement authentication',
      'fix database bug',
      'optimize performance',
    ];

    for (let i = 0; i < iterations; i++) {
      const query = queries[i % queries.length];
      const projectId = `bench-project-${Math.floor(Math.random() * 10)}`;

      const start = performance.now();
      await this.retrieval.retrieveContext(query, { projectId, limit: 20 });
      times.push(performance.now() - start);
    }

    return this.calculateResult('Context Retrieval', times, 200);
  }

  /**
   * Benchmark agent memory retrieval
   * Target: <50ms
   */
  async benchmarkAgentMemoryRetrieval(): Promise<BenchmarkResult> {
    const iterations = 100;
    const times: number[] = [];
    const agentIds = ['queen', 'princess-dev', 'coder', 'tester'];

    for (let i = 0; i < iterations; i++) {
      const agentId = agentIds[i % agentIds.length];
      const projectId = `bench-project-${Math.floor(Math.random() * 10)}`;

      const start = performance.now();
      this.storage.getAgentMemories(agentId, projectId, 0.5, 50);
      times.push(performance.now() - start);
    }

    return this.calculateResult('Agent Memory Retrieval', times, 50);
  }

  /**
   * Calculate benchmark result statistics
   */
  private calculateResult(
    testName: string,
    times: number[],
    target: number
  ): BenchmarkResult {
    times.sort((a, b) => a - b);

    const totalTimeMs = times.reduce((sum, t) => sum + t, 0);
    const avgTimeMs = totalTimeMs / times.length;
    const minTimeMs = times[0];
    const maxTimeMs = times[times.length - 1];
    const p50TimeMs = times[Math.floor(times.length * 0.5)];
    const p95TimeMs = times[Math.floor(times.length * 0.95)];
    const p99TimeMs = times[Math.floor(times.length * 0.99)];

    const success = avgTimeMs <= target;

    return {
      testName,
      iterations: times.length,
      totalTimeMs,
      avgTimeMs,
      minTimeMs,
      maxTimeMs,
      p50TimeMs,
      p95TimeMs,
      p99TimeMs,
      success,
      target,
    };
  }

  /**
   * Setup test data for benchmarking
   */
  private async setupTestData(numTasks: number): Promise<void> {
    // Create 10 projects
    for (let i = 0; i < 10; i++) {
      const project: Project = {
        id: `bench-project-${i}`,
        name: `Benchmark Project ${i}`,
        description: `Test project for performance benchmarking`,
        createdAt: new Date(),
        lastAccessedAt: new Date(),
      };
      this.storage.saveProject(project);
    }

    // Create tasks distributed across projects
    for (let i = 0; i < numTasks; i++) {
      const projectId = `bench-project-${i % 10}`;
      const task: Task = {
        id: `bench-task-${i}`,
        projectId,
        description: this.generateTaskDescription(i),
        status: i % 2 === 0 ? 'completed' : 'pending',
        createdAt: new Date(Date.now() - i * 60000), // Stagger timestamps
      };
      this.storage.saveTask(task);
    }

    // Create conversations
    for (let i = 0; i < 500; i++) {
      const projectId = `bench-project-${i % 10}`;
      const conversation: Conversation = {
        id: `bench-conv-${i}`,
        projectId,
        role: i % 2 === 0 ? 'user' : 'agent',
        content: this.generateConversationContent(i),
        createdAt: new Date(Date.now() - i * 30000),
      };
      this.storage.saveConversation(conversation);
    }

    // Create agent memories
    for (let i = 0; i < 200; i++) {
      const agentIds = ['queen', 'princess-dev', 'coder', 'tester'];
      const projectId = `bench-project-${i % 10}`;
      const memory: AgentMemory = {
        id: `bench-memory-${i}`,
        agentId: agentIds[i % agentIds.length],
        projectId,
        memoryType: i % 2 === 0 ? 'success_pattern' : 'failure_pattern',
        content: this.generateMemoryContent(i),
        importance: Math.random(),
        createdAt: new Date(Date.now() - i * 120000),
        lastAccessedAt: new Date(),
        accessCount: Math.floor(Math.random() * 10),
      };
      this.storage.saveAgentMemory(memory);
    }
  }

  /**
   * Generate realistic task description
   */
  private generateTaskDescription(index: number): string {
    const descriptions = [
      'Implement user authentication with OAuth2',
      'Fix database connection pooling bug',
      'Optimize React component rendering performance',
      'Add input validation to registration form',
      'Refactor API error handling middleware',
      'Write integration tests for payment flow',
      'Update documentation for deployment process',
      'Implement caching layer with Redis',
      'Add logging and monitoring to production',
      'Review and merge pull request #',
    ];

    return descriptions[index % descriptions.length] + index;
  }

  /**
   * Generate realistic conversation content
   */
  private generateConversationContent(index: number): string {
    const contents = [
      'Can you help me implement this feature?',
      'I found a bug in the authentication system',
      'The tests are failing on CI',
      'How should we handle error cases?',
      'Let me review the code changes',
      'This looks good, approved',
      'We need to optimize this query',
      'The deployment completed successfully',
    ];

    return contents[index % contents.length];
  }

  /**
   * Generate realistic memory content
   */
  private generateMemoryContent(index: number): string {
    const contents = [
      'Breaking large tasks into smaller chunks improved success rate by 25%',
      'Using prepared SQL statements prevented injection attacks',
      'Caching frequently accessed data reduced API latency',
      'Writing tests before implementation caught 40% more bugs',
      'Code reviews found critical security issues',
      'Incremental deployments reduced downtime',
      'Monitoring alerts caught production issues early',
      'Documentation updates improved onboarding time',
    ];

    return contents[index % contents.length];
  }

  /**
   * Generate formatted benchmark report
   */
  formatReport(suite: BenchmarkSuite): string {
    let report = `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    report += `📊 ${suite.suiteName}\n`;
    report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    for (const result of suite.results) {
      const status = result.success ? '✅' : '❌';
      report += `${status} ${result.testName}\n`;
      report += `   Target: ${result.target}ms | Avg: ${result.avgTimeMs.toFixed(2)}ms\n`;
      report += `   Min: ${result.minTimeMs.toFixed(2)}ms | Max: ${result.maxTimeMs.toFixed(2)}ms\n`;
      report += `   P50: ${result.p50TimeMs.toFixed(2)}ms | P95: ${result.p95TimeMs.toFixed(2)}ms | P99: ${result.p99TimeMs.toFixed(2)}ms\n`;
      report += `   Iterations: ${result.iterations}\n\n`;
    }

    report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    report += `Summary: ${suite.passed}/${suite.results.length} tests passed\n`;
    report += `Total Time: ${suite.totalTimeMs.toFixed(2)}ms\n`;
    report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;

    return report;
  }
}

/**
 * Run benchmark from command line
 */
export async function runBenchmark(dbPath?: string): Promise<void> {
  const Database = await import('better-sqlite3');
  const storage = new ContextDNAStorage(dbPath || ':memory:');
  const benchmark = new PerformanceBenchmark(storage);

  console.log('Starting Context DNA performance benchmark...\n');

  const suite = await benchmark.runAll();
  const report = benchmark.formatReport(suite);

  console.log(report);

  storage.close();

  // Exit with error code if any tests failed
  process.exit(suite.failed > 0 ? 1 : 0);
}
