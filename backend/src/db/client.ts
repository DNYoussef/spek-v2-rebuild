/**
 * SQLite Database Client
 * Provides persistent storage for Loop 1 & Loop 2 state
 *
 * Week 10 Day 1 Implementation
 */

import Database from 'better-sqlite3';
import { SCHEMA_SQL, type Loop1State, type Loop2State, type Loop3State, type AuditResult } from './schema';
import * as path from 'path';
import * as fs from 'fs';

const DB_PATH = path.join(process.cwd(), 'data', 'spek.db');

// Ensure data directory exists
const ensureDataDir = (): void => {
  const dataDir = path.dirname(DB_PATH);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
};

// Initialize database with schema
export const initDatabase = (): Database.Database => {
  ensureDataDir();
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL'); // Write-Ahead Logging for performance
  db.exec(SCHEMA_SQL);
  return db;
};

// Singleton database instance
let dbInstance: Database.Database | null = null;

export const getDatabase = (): Database.Database => {
  if (!dbInstance) {
    dbInstance = initDatabase();
  }
  return dbInstance;
};

/**
 * Loop 1 State Operations
 */

export const saveLoop1State = (state: Loop1State): void => {
  const db = getDatabase();
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO loop1_state
    (id, project_id, iteration, failure_rate, status, research_phase, premortem_phase, remediation_phase, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  `);

  stmt.run(
    state.id,
    state.projectId,
    state.iteration,
    state.failureRate,
    state.status,
    state.researchPhase ? JSON.stringify(state.researchPhase) : null,
    state.premortemPhase ? JSON.stringify(state.premortemPhase) : null,
    state.remediationPhase ? JSON.stringify(state.remediationPhase) : null
  );
};

export const getLoop1State = (id: string): Loop1State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop1_state WHERE id = ?');
  const row = stmt.get(id) as any;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.project_id,
    iteration: row.iteration,
    failureRate: row.failure_rate,
    status: row.status,
    researchPhase: row.research_phase ? JSON.parse(row.research_phase) : null,
    premortemPhase: row.premortem_phase ? JSON.parse(row.premortem_phase) : null,
    remediationPhase: row.remediation_phase ? JSON.parse(row.remediation_phase) : null,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
};

export const getLoop1StateByProject = (projectId: string): Loop1State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop1_state WHERE project_id = ? ORDER BY created_at DESC LIMIT 1');
  const row = stmt.get(projectId) as any;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.project_id,
    iteration: row.iteration,
    failureRate: row.failure_rate,
    status: row.status,
    researchPhase: row.research_phase ? JSON.parse(row.research_phase) : null,
    premortemPhase: row.premortem_phase ? JSON.parse(row.premortem_phase) : null,
    remediationPhase: row.remediation_phase ? JSON.parse(row.remediation_phase) : null,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
};

/**
 * Loop 2 State Operations
 */

export const saveLoop2State = (state: Loop2State): void => {
  const db = getDatabase();
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO loop2_state
    (id, project_id, status, phases, princesses, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  `);

  stmt.run(
    state.id,
    state.projectId,
    state.status,
    JSON.stringify(state.phases),
    JSON.stringify(state.princesses)
  );
};

export const getLoop2State = (id: string): Loop2State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop2_state WHERE id = ?');
  const row = stmt.get(id) as any;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.project_id,
    status: row.status,
    phases: JSON.parse(row.phases),
    princesses: JSON.parse(row.princesses),
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
};

export const getLoop2StateByProject = (projectId: string): Loop2State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop2_state WHERE project_id = ? ORDER BY created_at DESC LIMIT 1');
  const row = stmt.get(projectId) as any;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.project_id,
    status: row.status,
    phases: JSON.parse(row.phases),
    princesses: JSON.parse(row.princesses),
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
};

/**
 * Audit Results Operations
 */

export const saveAuditResult = (result: AuditResult): void => {
  const db = getDatabase();
  const stmt = db.prepare(`
    INSERT INTO audit_results
    (id, project_id, task_id, stage, status, issues, execution_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    result.id,
    result.projectId,
    result.taskId,
    result.stage,
    result.status,
    JSON.stringify(result.issues),
    result.executionTime
  );
};

export const getAuditResults = (taskId: string): AuditResult[] => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM audit_results WHERE task_id = ? ORDER BY created_at DESC');
  const rows = stmt.all(taskId) as any[];

  return rows.map(row => ({
    id: row.id,
    projectId: row.project_id,
    taskId: row.task_id,
    stage: row.stage,
    status: row.status,
    issues: JSON.parse(row.issues),
    executionTime: row.execution_time,
    createdAt: row.created_at,
  }));
};

export const getAuditResultsByProject = (projectId: string): AuditResult[] => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM audit_results WHERE project_id = ? ORDER BY created_at DESC LIMIT 100');
  const rows = stmt.all(projectId) as any[];

  return rows.map(row => ({
    id: row.id,
    projectId: row.project_id,
    taskId: row.task_id,
    stage: row.stage,
    status: row.status,
    issues: JSON.parse(row.issues),
    executionTime: row.execution_time,
    createdAt: row.created_at,
  }));
};

/**
 * Loop 3 State Operations
 */

export const getLoop3State = (id: string): Loop3State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop3_state WHERE id = ?');
  const row = stmt.get(id) as any;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.project_id,
    status: row.status,
    currentStep: row.current_step,
    auditResults: row.audit_results,
    github: row.github,
    cicd: row.cicd,
    docs: row.docs,
    export: row.export,
    startedAt: row.started_at,
    completedAt: row.completed_at,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
};

export const getLoop3StateByProject = (projectId: string): Loop3State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop3_state WHERE project_id = ? ORDER BY created_at DESC LIMIT 1');
  const row = stmt.get(projectId) as any;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.project_id,
    status: row.status,
    currentStep: row.current_step,
    auditResults: row.audit_results,
    github: row.github,
    cicd: row.cicd,
    docs: row.docs,
    export: row.export,
    startedAt: row.started_at,
    completedAt: row.completed_at,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
};

export const saveLoop3State = (state: Loop3State): void => {
  const db = getDatabase();
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO loop3_state (
      id, project_id, status, current_step, audit_results, github, cicd, docs, export,
      started_at, completed_at, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    state.id,
    state.projectId,
    state.status,
    state.currentStep,
    state.auditResults,
    state.github,
    state.cicd,
    state.docs,
    state.export,
    state.startedAt,
    state.completedAt,
    state.createdAt,
    state.updatedAt
  );
};

/**
 * Cleanup Operations
 */

export const deleteOldRecords = (days: number = 30): void => {
  const db = getDatabase();
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  const cutoffStr = cutoffDate.toISOString();

  db.prepare('DELETE FROM audit_results WHERE created_at < ?').run(cutoffStr);
  // Keep Loop 1/2 state indefinitely (users may resume projects)
};

export const closeDatabase = (): void => {
  if (dbInstance) {
    dbInstance.close();
    dbInstance = null;
  }
};
