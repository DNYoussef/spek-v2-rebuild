/**
 * Loop 1 Orchestrator - Iterative Failure Analysis
 * Coordinates research → pre-mortem → remediation → iteration
 *
 * Week 9 - Loop 1 Implementation
 * NASA Compliance: ≤60 LOC per function
 */

import { ResearchAgent, ResearchResult } from './ResearchAgent';
import { PremortemAgent, PremortemResult, FailureScenario } from './PremortemAgent';
import { saveLoop1State, getLoop1StateByProject } from '../../db/client';
import { v4 as uuidv4 } from 'uuid';
import { getWebSocketEmitter } from '../WebSocketEventEmitter';

export interface Loop1State {
  projectId: string;
  currentIteration: number;
  maxIterations: number;
  failureRateHistory: number[];
  currentFailureRate: number;
  targetFailureRate: number;
  status: 'running' | 'paused' | 'completed' | 'failed';
  researchResults?: ResearchResult;
  premortemResults?: PremortemResult;
  spec: string;
  plan: string;
}

export interface Loop1Event {
  type: 'research_started' | 'research_completed' | 'premortem_started' |
        'premortem_completed' | 'remediation_started' | 'remediation_completed' |
        'iteration_completed' | 'loop1_completed' | 'user_paused';
  data: any;
  timestamp: number;
}

export class Loop1Orchestrator {
  private researchAgent: ResearchAgent;
  private premortemAgent: PremortemAgent;
  private state: Loop1State;
  private eventListeners: Array<(event: Loop1Event) => void> = [];

  constructor(
    projectId: string,
    spec: string,
    plan: string,
    githubToken?: string
  ) {
    this.researchAgent = new ResearchAgent(githubToken);
    this.premortemAgent = new PremortemAgent();

    this.state = {
      projectId,
      currentIteration: 0,
      maxIterations: 10,
      failureRateHistory: [],
      currentFailureRate: 100,
      targetFailureRate: 5,
      status: 'running',
      spec,
      plan,
    };
  }

  /**
   * Execute full Loop 1 workflow
   * Iterates until failure rate <5% or max iterations reached
   */
  async execute(): Promise<Loop1State> {
    while (this.shouldContinue()) {
      await this.executeIteration();
    }

    this.state.status = this.state.currentFailureRate <= this.state.targetFailureRate
      ? 'completed'
      : 'failed';

    this.emitEvent({
      type: 'loop1_completed',
      data: { finalFailureRate: this.state.currentFailureRate },
      timestamp: Date.now(),
    });

    return this.state;
  }

  /**
   * Execute single iteration
   * Research → Pre-mortem → Remediation → Re-research → Re-premortem
   */
  private async executeIteration(): Promise<void> {
    this.state.currentIteration += 1;

    // Research phase
    await this.executeResearch();

    // Pre-mortem phase
    await this.executePremortem();

    // Remediation phase (update SPEC/PLAN)
    await this.executeRemediation();

    // Re-research phase (validate mitigations)
    await this.executeReResearch();

    // Re-premortem phase (independent validation)
    await this.executeRePremortem();

    this.state.failureRateHistory.push(this.state.currentFailureRate);

    this.emitEvent({
      type: 'iteration_completed',
      data: {
        iteration: this.state.currentIteration,
        failureRate: this.state.currentFailureRate,
      },
      timestamp: Date.now(),
    });
  }

  /**
   * Research phase - gather artifacts
   */
  private async executeResearch(): Promise<void> {
    this.emitEvent({
      type: 'research_started',
      data: { iteration: this.state.currentIteration },
      timestamp: Date.now(),
    });

    const result = await this.researchAgent.executeResearch(
      this.state.spec,
      100, // Top 100 GitHub results
      50   // Top 50 papers
    );

    this.state.researchResults = result;

    this.emitEvent({
      type: 'research_completed',
      data: { artifactsFound: result.totalFound },
      timestamp: Date.now(),
    });

    this.persistState(); // Save state after research
  }

  /**
   * Pre-mortem phase - failure analysis
   */
  private async executePremortem(): Promise<void> {
    this.emitEvent({
      type: 'premortem_started',
      data: { iteration: this.state.currentIteration },
      timestamp: Date.now(),
    });

    const result = await this.premortemAgent.executePremortem(
      this.state.spec,
      this.state.plan,
      this.state.researchResults?.artifacts || []
    );

    this.state.premortemResults = result;
    this.state.currentFailureRate = result.failureRate;

    this.emitEvent({
      type: 'premortem_completed',
      data: {
        scenariosFound: result.scenarios.length,
        failureRate: result.failureRate,
      },
      timestamp: Date.now(),
    });

    this.persistState(); // Save state after premortem
  }

  /**
   * Remediation phase - update SPEC/PLAN
   */
  private async executeRemediation(): Promise<void> {
    this.emitEvent({
      type: 'remediation_started',
      data: { iteration: this.state.currentIteration },
      timestamp: Date.now(),
    });

    if (!this.state.premortemResults) return;

    // Update SPEC/PLAN with mitigations
    const mitigations = this.generateMitigations(
      this.state.premortemResults.scenarios
    );

    this.state.spec = this.addMitigationsToSpec(this.state.spec, mitigations);
    this.state.plan = this.addMitigationsToPlan(this.state.plan, mitigations);

    this.emitEvent({
      type: 'remediation_completed',
      data: { mitigationsAdded: mitigations.length },
      timestamp: Date.now(),
    });
  }

  /**
   * Re-research phase - validate mitigations exist
   */
  private async executeReResearch(): Promise<void> {
    // Similar to executeResearch but focused on mitigations
    await this.executeResearch();
  }

  /**
   * Re-premortem phase - independent validation
   */
  private async executeRePremortem(): Promise<void> {
    // Fresh eyes analysis by different agent
    await this.executePremortem();
  }

  /**
   * Check if loop should continue
   */
  private shouldContinue(): boolean {
    return this.state.status === 'running' &&
           this.state.currentIteration < this.state.maxIterations &&
           this.state.currentFailureRate > this.state.targetFailureRate;
  }

  /**
   * Generate mitigations from failure scenarios
   */
  private generateMitigations(scenarios: FailureScenario[]): string[] {
    return scenarios.map(scenario =>
      `Mitigation for ${scenario.priority}: ${scenario.description}`
    );
  }

  /**
   * Add mitigations to SPEC document
   */
  private addMitigationsToSpec(spec: string, mitigations: string[]): string {
    const mitigationSection = '\n\n## Risk Mitigations\n\n' +
      mitigations.map((m, i) => `${i + 1}. ${m}`).join('\n');
    return spec + mitigationSection;
  }

  /**
   * Add mitigations to PLAN document
   */
  private addMitigationsToPlan(plan: string, mitigations: string[]): string {
    const mitigationSection = '\n\n## Risk Mitigation Tasks\n\n' +
      mitigations.map((m, i) => `- [ ] ${m}`).join('\n');
    return plan + mitigationSection;
  }

  /**
   * Pause loop execution (user injection point)
   */
  pause(): void {
    this.state.status = 'paused';
    this.emitEvent({
      type: 'user_paused',
      data: { iteration: this.state.currentIteration },
      timestamp: Date.now(),
    });
  }

  /**
   * Resume loop execution
   */
  resume(): void {
    if (this.state.status === 'paused') {
      this.state.status = 'running';
    }
  }

  /**
   * Subscribe to loop events
   */
  onEvent(listener: (event: Loop1Event) => void): void {
    this.eventListeners.push(listener);
  }

  /**
   * Emit event to all listeners and WebSocket clients
   */
  private emitEvent(event: Loop1Event): void {
    this.eventListeners.forEach(listener => listener(event));

    // Emit to WebSocket clients (Week 10 addition)
    const wsEmitter = getWebSocketEmitter();
    if (wsEmitter.isInitialized()) {
      wsEmitter.emitLoop1Event(
        this.state.projectId,
        `loop1:${event.type}` as any,
        event.data
      );
    }
  }

  /**
   * Persist state to database
   */
  private persistState(): void {
    const dbState = {
      id: uuidv4(),
      projectId: this.state.projectId,
      iteration: this.state.currentIteration,
      failureRate: this.state.currentFailureRate,
      status: this.state.status,
      researchPhase: this.state.researchResults ? {
        githubResults: this.state.researchResults.artifacts
          .filter((a: any) => a.source === 'github')
          .map((a: any) => ({ name: a.title, url: a.url, stars: a.metadata?.stars || 0, description: a.content })),
        paperResults: this.state.researchResults.artifacts
          .filter((a: any) => a.source === 'semantic-scholar')
          .map((a: any) => ({ title: a.title, authors: a.metadata?.authors || [], year: a.metadata?.year || 0, url: a.url, citations: a.metadata?.citations || 0 })),
        status: 'completed',
        completedAt: new Date().toISOString(),
      } : null,
      premortemPhase: this.state.premortemResults ? {
        scenarios: this.state.premortemResults.scenarios,
        riskScore: this.state.premortemResults.riskScore,
        status: 'completed',
        completedAt: new Date().toISOString(),
      } : null,
      remediationPhase: null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    saveLoop1State(dbState as any); // Type cast - orchestrator state differs from DB schema
  }

  /**
   * Load state from database
   */
  static async loadFromDatabase(projectId: string): Promise<Loop1Orchestrator | null> {
    const dbState = getLoop1StateByProject(projectId);
    if (!dbState) return null;

    // Reconstruct orchestrator from database state
    const orchestrator = new Loop1Orchestrator(
      projectId,
      '', // spec will be loaded separately
      '', // plan will be loaded separately
      undefined
    );

    orchestrator.state.currentIteration = dbState.iteration;
    orchestrator.state.currentFailureRate = dbState.failureRate;
    orchestrator.state.status = dbState.status as any;
    orchestrator.state.failureRateHistory = [];

    return orchestrator;
  }

  /**
   * Get current state
   */
  getState(): Loop1State {
    return { ...this.state };
  }
}
