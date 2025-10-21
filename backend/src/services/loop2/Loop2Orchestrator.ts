/**
 * Loop 2 Orchestrator - Implementation Phase
 * Coordinates MECE phase division, Princess Hive delegation, and Three-Stage Audit
 *
 * Week 9 - Loop 2 Implementation
 * Week 16 - Stub completion
 * NASA Compliance: ≤60 LOC per function
 */

import * as db from '../../db/client';
import type { Loop2State, Phase as DbPhase, Task as DbTask, PrincessState } from '../../db/schema';
import { MECEPhaseDivision, type Task, type Phase, type DependencyGraph } from './MECEPhaseDivision';
import { PrincessHiveDelegation, type A2ARequest, type A2AResponse } from './PrincessHiveDelegation';
import { ThreeStageAudit, type AuditResult } from './ThreeStageAudit';
import { getWebSocketEmitter } from '../WebSocketEventEmitter';
import { v4 as uuidv4 } from 'uuid';

export interface Loop2Event {
  type: 'phase_started' | 'phase_completed' | 'task_started' | 'task_completed' |
        'audit_started' | 'audit_completed' | 'loop2_completed' | 'error';
  data: any;
  timestamp: number;
}

export class Loop2Orchestrator {
  private meceService: MECEPhaseDivision;
  private princessHive: PrincessHiveDelegation;
  private auditService: ThreeStageAudit;
  private dependencyGraph: DependencyGraph | null = null;
  private auditResults: AuditResult[] = [];

  constructor(private projectId: string) {
    this.meceService = new MECEPhaseDivision();
    this.princessHive = new PrincessHiveDelegation();
    this.auditService = new ThreeStageAudit();
  }

  /**
   * Start Loop 2 workflow
   * Initialize MECE phase division
   */
  async start(): Promise<Loop2State> {
    const state: Loop2State = {
      id: `loop2-${this.projectId}`,
      projectId: this.projectId,
      status: 'running',
      phases: [],
      princesses: this.initializePrincesses(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    db.saveLoop2State(state);
    this.emitEvent({ type: 'phase_started', data: { phase: 'initialization' }, timestamp: Date.now() });

    return state;
  }

  /**
   * Execute full Loop 2 workflow
   * MECE → Princess Hive → Three-Stage Audit
   */
  async execute(tasks: Task[]): Promise<Loop2State> {
    const state = await this.getState();
    if (!state) throw new Error('Loop2 not started');

    // Step 1: MECE Phase Division
    await this.executeMECEDivision(tasks);

    // Step 2: Execute phases with Princess Hive delegation
    await this.executePhases();

    // Step 3: Run Three-Stage Audit
    await this.executeAudit();

    // Mark as completed
    return this.complete();
  }

  /**
   * Execute MECE phase division
   */
  private async executeMECEDivision(tasks: Task[]): Promise<void> {
    this.emitEvent({
      type: 'phase_started',
      data: { phase: 'mece_division', taskCount: tasks.length },
      timestamp: Date.now()
    });

    this.dependencyGraph = await this.meceService.divideTasks(tasks);

    // Convert to database format and save
    const state = await this.getState();
    if (state) {
      state.phases = this.dependencyGraph.phases.map(phase => this.convertPhaseToDb(phase));
      state.updatedAt = new Date().toISOString();
      db.saveLoop2State(state);
    }

    this.emitEvent({
      type: 'phase_completed',
      data: {
        phase: 'mece_division',
        phaseCount: this.dependencyGraph.phases.length,
        bottlenecks: this.meceService.identifyBottlenecks(tasks)
      },
      timestamp: Date.now()
    });
  }

  /**
   * Execute all phases with Princess Hive delegation
   */
  private async executePhases(): Promise<void> {
    if (!this.dependencyGraph) {
      throw new Error('MECE division not executed');
    }

    for (const phase of this.dependencyGraph.phases) {
      await this.executePhase(phase);
    }
  }

  /**
   * Execute single phase
   */
  private async executePhase(phase: Phase): Promise<void> {
    this.emitEvent({
      type: 'phase_started',
      data: { phaseId: phase.id, phaseName: phase.name },
      timestamp: Date.now()
    });

    // Update phase status
    phase.status = 'in_progress';
    await this.updatePhaseInDb(phase);

    // Execute tasks in parallel (no dependencies within phase)
    const taskPromises = phase.tasks.map(task => this.executeTask(task, phase.id));
    await Promise.all(taskPromises);

    // Mark phase as completed
    phase.status = 'completed';
    await this.updatePhaseInDb(phase);

    this.emitEvent({
      type: 'phase_completed',
      data: { phaseId: phase.id, tasksCompleted: phase.tasks.length },
      timestamp: Date.now()
    });
  }

  /**
   * Execute single task via Princess Hive
   */
  private async executeTask(task: Task, phaseId: number): Promise<void> {
    this.emitEvent({
      type: 'task_started',
      data: { taskId: task.id, agentType: task.agentType },
      timestamp: Date.now()
    });

    // Queen → Princess delegation
    const princessId = this.princessHive.queenToPrincess(task.agentType);

    // Princess → Drone delegation
    const droneId = this.princessHive.princessToDrone(princessId, task.agentType);

    // Create A2A request
    const request: A2ARequest = {
      targetAgentId: droneId,
      taskId: task.id,
      taskType: task.agentType,
      parameters: {
        session: this.princessHive.createSession(droneId, princessId, {
          pwd: process.cwd(),
          projectId: this.projectId,
          taskId: task.id,
          todoList: [],
          artifacts: [],
        }),
      },
      timeout: 300000, // 5 minutes
      requester: princessId,
    };

    // Execute via A2A
    const response: A2AResponse = await this.princessHive.executeA2A(request);

    if (response.status === 'failed') {
      throw new Error(`Task ${task.id} failed: ${response.error}`);
    }

    this.emitEvent({
      type: 'task_completed',
      data: {
        taskId: task.id,
        executionTimeMs: response.executionTimeMs,
        result: response.result
      },
      timestamp: Date.now()
    });
  }

  /**
   * Execute Three-Stage Audit pipeline
   */
  private async executeAudit(): Promise<void> {
    this.emitEvent({
      type: 'audit_started',
      data: { stages: ['theater', 'production', 'quality'] },
      timestamp: Date.now()
    });

    if (!this.dependencyGraph) {
      throw new Error('No phases to audit');
    }

    // Run audit for each task
    for (const phase of this.dependencyGraph.phases) {
      for (const task of phase.tasks) {
        const results = await this.auditService.executeAudit(task.id, '', '');
        this.auditResults.push(...results);

        // Save audit results to database
        for (const result of results) {
          db.saveAuditResult({
            id: uuidv4(),
            projectId: this.projectId,
            taskId: task.id,
            stage: result.stage,
            status: result.status,
            issues: [],
            executionTime: result.executionTimeMs,
            createdAt: new Date().toISOString(),
          });
        }
      }
    }

    const passedCount = this.auditResults.filter(r => r.status === 'pass').length;
    const failedCount = this.auditResults.filter(r => r.status === 'fail').length;

    this.emitEvent({
      type: 'audit_completed',
      data: {
        totalAudits: this.auditResults.length,
        passed: passedCount,
        failed: failedCount,
        passRate: (passedCount / this.auditResults.length) * 100
      },
      timestamp: Date.now()
    });

    // Fail if audit pass rate < 80%
    if (passedCount / this.auditResults.length < 0.8) {
      throw new Error(`Audit failed: ${failedCount} failures out of ${this.auditResults.length}`);
    }
  }

  /**
   * Get current state from database
   */
  async getState(): Promise<Loop2State | null> {
    return db.getLoop2StateByProject(this.projectId);
  }

  /**
   * Mark Loop 2 as completed
   */
  async complete(): Promise<Loop2State> {
    const state = await this.getState();
    if (!state) throw new Error('Loop2 state not found');

    state.status = 'completed';
    state.updatedAt = new Date().toISOString();

    db.saveLoop2State(state);

    this.emitEvent({
      type: 'loop2_completed',
      data: {
        phasesCompleted: state.phases.length,
        auditsRun: this.auditResults.length
      },
      timestamp: Date.now()
    });

    return state;
  }

  /**
   * Initialize Princess agents
   */
  private initializePrincesses(): PrincessState[] {
    const princesses = this.princessHive.getAllPrincesses();

    return princesses.map(p => ({
      id: p.id,
      name: p.name,
      status: 'idle',
      currentTask: null,
      droneCount: p.droneAgents.length,
      tasksCompleted: 0,
      tasksInProgress: 0,
      lastActive: new Date().toISOString(),
    }));
  }

  /**
   * Convert MECE Phase to database format
   */
  private convertPhaseToDb(phase: Phase): DbPhase {
    return {
      id: phase.id.toString(),
      name: phase.name,
      tasks: phase.tasks.map(t => this.convertTaskToDb(t)),
      status: phase.status,
      completedAt: phase.status === 'completed' ? new Date().toISOString() : null,
    };
  }

  /**
   * Convert MECE Task to database format
   */
  private convertTaskToDb(task: Task): DbTask {
    return {
      id: task.id,
      type: task.agentType,
      description: task.description,
      status: 'pending',
      assignedTo: null,
      dependencies: task.dependencies,
      result: null,
      createdAt: new Date().toISOString(),
      completedAt: null,
    };
  }

  /**
   * Update phase in database
   */
  private async updatePhaseInDb(phase: Phase): Promise<void> {
    const state = await this.getState();
    if (!state) return;

    const dbPhaseIndex = state.phases.findIndex(p => p.id === phase.id.toString());
    if (dbPhaseIndex >= 0) {
      state.phases[dbPhaseIndex] = this.convertPhaseToDb(phase);
      state.updatedAt = new Date().toISOString();
      db.saveLoop2State(state);
    }
  }

  /**
   * Emit event to WebSocket
   */
  private emitEvent(event: Loop2Event): void {
    const emitter = getWebSocketEmitter();
    if (emitter) {
      emitter.emit({
        type: event.type as any,
        projectId: this.projectId,
        data: event.data,
        timestamp: event.timestamp,
      });
    }
  }

  /**
   * Get audit results
   */
  getAuditResults(): AuditResult[] {
    return this.auditResults;
  }

  /**
   * Get dependency graph
   */
  getDependencyGraph(): DependencyGraph | null {
    return this.dependencyGraph;
  }
}
