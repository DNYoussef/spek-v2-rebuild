/**
 * Loop 1 Pre-mortem Multi-Agent System
 * Failure analysis and risk scoring
 *
 * Week 9 - Loop 1 Implementation
 * NASA Compliance: ≤60 LOC per function
 */

export interface FailureScenario {
  id: string;
  description: string;
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  likelihood: number; // 0-1
  impact: number; // 0-1
  mitigation?: string;
  agentId: string;
}

export interface PremortemResult {
  scenarios: FailureScenario[];
  failureRate: number; // 0-100%
  riskScore: number;
  iterationId: string;
  timestamp: number;
}

export interface AgentAnalysis {
  agentId: string;
  scenarios: FailureScenario[];
  confidence: number;
}

export class PremortemAgent {
  private readonly PRIORITY_WEIGHTS = {
    P0: 3,
    P1: 2,
    P2: 1,
    P3: 0.5,
  };

  /**
   * Execute multi-agent pre-mortem analysis
   * Uses researcher, planner, architect agents
   */
  async executePremortem(
    specDocument: string,
    planDocument: string,
    researchArtifacts: any[]
  ): Promise<PremortemResult> {
    const analyses = await Promise.all([
      this.analyzeWithResearcher(specDocument, researchArtifacts),
      this.analyzeWithPlanner(planDocument),
      this.analyzeWithArchitect(specDocument),
    ]);

    const allScenarios = this.mergeScenarios(analyses);
    const riskScore = this.calculateRiskScore(allScenarios);
    const failureRate = this.calculateFailureRate(riskScore);

    return {
      scenarios: allScenarios,
      failureRate,
      riskScore,
      iterationId: this.generateIterationId(),
      timestamp: Date.now(),
    };
  }

  /**
   * Researcher agent analysis
   * Compares spec against research artifacts
   */
  private async analyzeWithResearcher(
    spec: string,
    artifacts: any[]
  ): Promise<AgentAnalysis> {
    const scenarios: FailureScenario[] = [];

    // Check for missing patterns found in research
    if (artifacts.length < 5) {
      scenarios.push({
        id: this.generateScenarioId(),
        description: 'Insufficient research artifacts (target: ≥5)',
        priority: 'P1',
        likelihood: 0.7,
        impact: 0.6,
        agentId: 'researcher',
      });
    }

    // Check for novel approaches without precedent
    const hasNovelApproach = this.detectNovelApproach(spec);
    if (hasNovelApproach) {
      scenarios.push({
        id: this.generateScenarioId(),
        description: 'Novel approach with no proven implementation',
        priority: 'P0',
        likelihood: 0.8,
        impact: 0.9,
        agentId: 'researcher',
      });
    }

    return {
      agentId: 'researcher',
      scenarios,
      confidence: 0.85,
    };
  }

  /**
   * Planner agent analysis
   * Checks timeline and resource feasibility
   */
  private async analyzeWithPlanner(plan: string): Promise<AgentAnalysis> {
    const scenarios: FailureScenario[] = [];

    // Check for aggressive timeline
    const weekCount = this.extractWeekCount(plan);
    if (weekCount && weekCount < 12) {
      scenarios.push({
        id: this.generateScenarioId(),
        description: `Aggressive timeline (${weekCount} weeks < 12 weeks minimum)`,
        priority: 'P1',
        likelihood: 0.6,
        impact: 0.7,
        agentId: 'planner',
      });
    }

    // Check for missing buffer
    const hasBuffer = plan.toLowerCase().includes('buffer');
    if (!hasBuffer) {
      scenarios.push({
        id: this.generateScenarioId(),
        description: 'No contingency buffer in timeline',
        priority: 'P2',
        likelihood: 0.5,
        impact: 0.5,
        agentId: 'planner',
      });
    }

    return {
      agentId: 'planner',
      scenarios,
      confidence: 0.9,
    };
  }

  /**
   * Architect agent analysis
   * Checks technical architecture risks
   */
  private async analyzeWithArchitect(spec: string): Promise<AgentAnalysis> {
    const scenarios: FailureScenario[] = [];

    // Check for god objects
    const hasGodObject = spec.toLowerCase().includes('god object');
    if (hasGodObject) {
      scenarios.push({
        id: this.generateScenarioId(),
        description: 'God object anti-pattern detected in architecture',
        priority: 'P0',
        likelihood: 0.9,
        impact: 0.8,
        agentId: 'architect',
      });
    }

    // Check for missing error handling
    const hasErrorHandling = spec.toLowerCase().includes('error') ||
      spec.toLowerCase().includes('exception');
    if (!hasErrorHandling) {
      scenarios.push({
        id: this.generateScenarioId(),
        description: 'Insufficient error handling strategy',
        priority: 'P1',
        likelihood: 0.6,
        impact: 0.7,
        agentId: 'architect',
      });
    }

    return {
      agentId: 'architect',
      scenarios,
      confidence: 0.88,
    };
  }

  /**
   * Merge scenarios from multiple agents
   * Remove duplicates, prioritize higher severity
   */
  private mergeScenarios(analyses: AgentAnalysis[]): FailureScenario[] {
    const allScenarios = analyses.flatMap(a => a.scenarios);
    const uniqueScenarios = new Map<string, FailureScenario>();

    for (const scenario of allScenarios) {
      const key = scenario.description.toLowerCase();
      const existing = uniqueScenarios.get(key);

      if (!existing || this.comparePriority(scenario.priority, existing.priority) > 0) {
        uniqueScenarios.set(key, scenario);
      }
    }

    return Array.from(uniqueScenarios.values());
  }

  /**
   * Calculate weighted risk score
   * Formula: P0×3 + P1×2 + P2×1 + P3×0.5
   */
  private calculateRiskScore(scenarios: FailureScenario[]): number {
    return scenarios.reduce((total, scenario) => {
      const weight = this.PRIORITY_WEIGHTS[scenario.priority];
      const risk = scenario.likelihood * scenario.impact * weight * 100;
      return total + risk;
    }, 0);
  }

  /**
   * Calculate failure rate percentage
   * Risk score normalized to 0-100%
   */
  private calculateFailureRate(riskScore: number): number {
    const maxRisk = 1000;
    const rate = Math.min((riskScore / maxRisk) * 100, 100);
    return Number(rate.toFixed(2));
  }

  /**
   * Compare priority levels
   * Returns: 1 if a > b, -1 if a < b, 0 if equal
   */
  private comparePriority(a: string, b: string): number {
    const aWeight = this.PRIORITY_WEIGHTS[a as keyof typeof this.PRIORITY_WEIGHTS];
    const bWeight = this.PRIORITY_WEIGHTS[b as keyof typeof this.PRIORITY_WEIGHTS];
    return Math.sign(aWeight - bWeight);
  }

  private detectNovelApproach(spec: string): boolean {
    const novelKeywords = ['novel', 'innovative', 'unprecedented', 'new approach'];
    return novelKeywords.some(keyword => spec.toLowerCase().includes(keyword));
  }

  private extractWeekCount(plan: string): number | null {
    const match = plan.match(/(\d+)\s*weeks?/i);
    return match ? parseInt(match[1], 10) : null;
  }

  private generateScenarioId(): string {
    return `scenario_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateIterationId(): string {
    return `iteration_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
