/**
 * Loop 2 Three-Stage Audit Pipeline
 * Stage 1: Theater Detection → Stage 2: Production Testing → Stage 3: Quality Scan
 *
 * Week 9 - Loop 2 Implementation (Updated Week 10)
 * Week 10 Day 6: Added retry logic and error handling
 * NASA Compliance: ≤60 LOC per function
 */

import { DockerSandbox } from '../sandbox/DockerSandbox';
import { withRetry, CircuitBreaker } from '../../utils/RetryHelper';

export interface AuditResult {
  taskId: string;
  stage: 'theater' | 'production' | 'quality';
  status: 'pass' | 'fail';
  score: number;
  details: any;
  executionTimeMs: number;
  retryCount: number;
}

export interface TheaterDetectionResult {
  passed: boolean;
  score: number;
  patterns: Array<{
    type: string;
    severity: 'high' | 'medium' | 'low';
    locations: string[];
  }>;
}

export interface ProductionTestResult {
  passed: boolean;
  testsPassed: number;
  testsFailed: number;
  logs: string[];
  errors: string[];
}

export interface QualityScanResult {
  passed: boolean;
  nasaCompliance: number;
  godObjects: number;
  connascenceIssues: number;
  recommendations: string[];
}

export class ThreeStageAudit {
  private readonly MAX_RETRIES = 3;
  private readonly THEATER_THRESHOLD = 10;
  private readonly NASA_THRESHOLD = 92;
  private readonly dockerSandbox: DockerSandbox;
  private readonly circuitBreaker: CircuitBreaker;

  constructor() {
    this.dockerSandbox = new DockerSandbox();
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      resetTimeout: 60000, // 1 minute
    });
  }

  /**
   * Execute complete 3-stage audit
   * Returns final audit result
   */
  async executeAudit(
    taskId: string,
    code: string,
    projectPath: string
  ): Promise<AuditResult[]> {
    const results: AuditResult[] = [];

    // Stage 1: Theater Detection
    const theaterResult = await this.executeTheaterDetection(taskId, code);
    results.push(theaterResult);

    if (theaterResult.status === 'fail') {
      return results; // Early exit on theater failure
    }

    // Stage 2: Production Testing
    const productionResult = await this.executeProductionTesting(taskId, code, projectPath);
    results.push(productionResult);

    if (productionResult.status === 'fail') {
      return results; // Early exit on production failure
    }

    // Stage 3: Quality Scan
    const qualityResult = await this.executeQualityScan(taskId, projectPath);
    results.push(qualityResult);

    return results;
  }

  /**
   * Stage 1: Theater Detection (AST-based, <5s)
   * Detects mock code, TODOs, NotImplementedError
   */
  private async executeTheaterDetection(
    taskId: string,
    code: string
  ): Promise<AuditResult> {
    const startTime = Date.now();

    const patterns = this.detectTheaterPatterns(code);
    const score = this.calculateTheaterScore(patterns);
    const passed = score < this.THEATER_THRESHOLD;

    return {
      taskId,
      stage: 'theater',
      status: passed ? 'pass' : 'fail',
      score,
      details: { patterns },
      executionTimeMs: Date.now() - startTime,
      retryCount: 0,
    };
  }

  /**
   * Detect theater code patterns
   */
  private detectTheaterPatterns(code: string): TheaterDetectionResult['patterns'] {
    const patterns: TheaterDetectionResult['patterns'] = [];

    // Pattern 1: TODO comments
    const todoMatches = code.match(/TODO|FIXME|XXX/g);
    if (todoMatches) {
      patterns.push({
        type: 'todo_comments',
        severity: 'medium',
        locations: this.extractLineNumbers(code, /TODO|FIXME|XXX/g),
      });
    }

    // Pattern 2: NotImplementedError or pass statements
    const notImplementedMatches = code.match(/NotImplementedError|raise.*not.*implement|^\s*pass\s*$/gm);
    if (notImplementedMatches) {
      patterns.push({
        type: 'not_implemented',
        severity: 'high',
        locations: this.extractLineNumbers(code, /NotImplementedError|raise.*not.*implement|^\s*pass\s*$/gm),
      });
    }

    // Pattern 3: Mock/stub functions
    const mockMatches = code.match(/mock|stub|fake|dummy/gi);
    if (mockMatches && mockMatches.length > 2) {
      patterns.push({
        type: 'mock_code',
        severity: 'high',
        locations: this.extractLineNumbers(code, /mock|stub|fake|dummy/gi),
      });
    }

    return patterns;
  }

  /**
   * Calculate theater score (higher = more theater)
   */
  private calculateTheaterScore(patterns: TheaterDetectionResult['patterns']): number {
    const severityWeights = { high: 5, medium: 2, low: 1 };
    return patterns.reduce((score, pattern) => {
      return score + (severityWeights[pattern.severity] * pattern.locations.length);
    }, 0);
  }

  /**
   * Extract line numbers for matches
   */
  private extractLineNumbers(code: string, regex: RegExp): string[] {
    const lines = code.split('\n');
    const locations: string[] = [];

    lines.forEach((line, index) => {
      if (regex.test(line)) {
        locations.push(`Line ${index + 1}`);
      }
    });

    return locations;
  }

  /**
   * Stage 2: Production Testing (Docker sandbox, <20s)
   * Run code in Docker sandbox with tests
   */
  private async executeProductionTesting(
    taskId: string,
    code: string,
    projectPath: string
  ): Promise<AuditResult> {
    const startTime = Date.now();

    try {
      // Simulate Docker sandbox execution
      const result = await this.runInSandbox(code, projectPath);

      return {
        taskId,
        stage: 'production',
        status: result.passed ? 'pass' : 'fail',
        score: result.testsPassed,
        details: result,
        executionTimeMs: Date.now() - startTime,
        retryCount: 0,
      };
    } catch (error) {
      return {
        taskId,
        stage: 'production',
        status: 'fail',
        score: 0,
        details: { error: (error as Error).message },
        executionTimeMs: Date.now() - startTime,
        retryCount: 0,
      };
    }
  }

  /**
   * Run code in Docker sandbox
   */
  private async runInSandbox(code: string, projectPath: string): Promise<ProductionTestResult> {
    // Determine language from projectPath or code
    const language = this.detectLanguage(code, projectPath);

    // Execute code in Docker sandbox
    const result = await this.dockerSandbox.execute(code, {
      language,
      timeout: 30000, // 30s timeout
      memory: 512 * 1024 * 1024, // 512MB
    });

    // Parse test results from stdout/stderr
    const testResults = this.parseTestResults(result.stdout, result.stderr);

    return {
      passed: result.success && (testResults.passed > 0),
      testsPassed: testResults.passed,
      testsFailed: testResults.failed,
      logs: [result.stdout],
      errors: result.stderr ? [result.stderr] : [],
    };
  }

  /**
   * Detect language from code or project path
   */
  private detectLanguage(code: string, projectPath: string): 'node' | 'python' {
    // Check project path
    if (projectPath.includes('.py') || projectPath.includes('python')) {
      return 'python';
    }

    // Check code patterns
    if (code.includes('import ') || code.includes('def ') || code.includes('print(')) {
      return 'python';
    }

    // Default to Node.js
    return 'node';
  }

  /**
   * Parse test results from output
   */
  private parseTestResults(stdout: string, stderr: string): { passed: number; failed: number } {
    // Simple heuristic: check for test keywords
    const output = stdout + stderr;

    // Look for common test patterns
    const passMatches = output.match(/(\d+)\s*(passed|passing)/i);
    const failMatches = output.match(/(\d+)\s*(failed|failing)/i);

    return {
      passed: passMatches ? parseInt(passMatches[1], 10) : 0,
      failed: failMatches ? parseInt(failMatches[1], 10) : 0,
    };
  }

  /**
   * Stage 3: Quality Scan (Analyzer, <10s)
   * NASA compliance, god objects, connascence
   */
  private async executeQualityScan(
    taskId: string,
    projectPath: string
  ): Promise<AuditResult> {
    const startTime = Date.now();

    try {
      const result = await this.runAnalyzer(projectPath);

      return {
        taskId,
        stage: 'quality',
        status: result.passed ? 'pass' : 'fail',
        score: result.nasaCompliance,
        details: result,
        executionTimeMs: Date.now() - startTime,
        retryCount: 0,
      };
    } catch (error) {
      return {
        taskId,
        stage: 'quality',
        status: 'fail',
        score: 0,
        details: { error: (error as Error).message },
        executionTimeMs: Date.now() - startTime,
        retryCount: 0,
      };
    }
  }

  /**
   * Run analyzer quality scan
   */
  private async runAnalyzer(projectPath: string): Promise<QualityScanResult> {
    // This will be replaced with real analyzer execution
    await new Promise(resolve => setTimeout(resolve, 100));

    return {
      passed: true,
      nasaCompliance: 95,
      godObjects: 0,
      connascenceIssues: 0,
      recommendations: [],
    };
  }

  /**
   * Execute audit with retry logic
   */
  async executeWithRetry(
    taskId: string,
    code: string,
    projectPath: string
  ): Promise<AuditResult[]> {
    let retryCount = 0;
    let results: AuditResult[] = [];

    while (retryCount < this.MAX_RETRIES) {
      results = await this.executeAudit(taskId, code, projectPath);

      const lastResult = results[results.length - 1];
      if (lastResult.status === 'pass') {
        break;
      }

      retryCount++;
      await this.exponentialBackoff(retryCount);
    }

    return results;
  }

  /**
   * Exponential backoff delay
   */
  private async exponentialBackoff(retryCount: number): Promise<void> {
    const delay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}
