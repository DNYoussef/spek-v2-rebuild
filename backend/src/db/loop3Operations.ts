/**
 * Loop 3 Database Operations
 * Week 11 Day 1 Implementation
 */

import { getDatabase } from './client';
import type { Loop3State as Loop3StateImport } from './schema';

// Re-export the Loop3State type with the correct shape
export interface Loop3StateDB {
  id: string;
  projectId: string;
  status: string;
  currentStep: string;
  auditResults: string;
  github: string | null;
  cicd: string | null;
  docs: string | null;
  export: string | null;
  startedAt: string;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Loop3State {
  id: string;
  projectId: string;
  status: 'not_started' | 'audit_running' | 'audit_complete' | 'github_setup' | 'cicd_setup' | 'docs_cleanup' | 'export' | 'completed' | 'failed';
  currentStep: 'audit' | 'github' | 'cicd' | 'docs' | 'export' | 'complete';
  startedAt: number;
  completedAt?: number;

  auditResults: {
    theater: { passed: number; failed: number; total: number };
    production: { passed: number; failed: number; total: number };
    quality: { passed: number; failed: number; total: number };
    overallScore: number;
  };

  github?: {
    repoName: string;
    visibility: 'public' | 'private';
    description: string;
    license?: string;
    createdUrl?: string;
  };

  cicd?: {
    enabled: boolean;
    workflowGenerated: boolean;
    testCommand?: string;
    buildCommand?: string;
    deployCommand?: string;
  };

  docs?: {
    filesScanned: number;
    outdatedDocs: number;
    userApproved: boolean;
    cleanupComplete: boolean;
  };

  export?: {
    method: 'github' | 'zip';
    path?: string;
    size?: number;
  };
}

export const saveLoop3State = (state: Loop3State): void => {
  const db = getDatabase();
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO loop3_state
    (id, project_id, status, current_step, audit_results, github, cicd, docs, export, started_at, completed_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  `);

  stmt.run(
    state.id,
    state.projectId,
    state.status,
    state.currentStep,
    JSON.stringify(state.auditResults),
    state.github ? JSON.stringify(state.github) : null,
    state.cicd ? JSON.stringify(state.cicd) : null,
    state.docs ? JSON.stringify(state.docs) : null,
    state.export ? JSON.stringify(state.export) : null,
    new Date(state.startedAt).toISOString(),
    state.completedAt ? new Date(state.completedAt).toISOString() : null
  );
};

export const getLoop3State = (id: string): Loop3State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop3_state WHERE id = ?');
  const row = stmt.get(id) as Loop3StateDB | undefined;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.projectId,
    status: row.status as Loop3State['status'],
    currentStep: row.currentStep as Loop3State['currentStep'],
    auditResults: JSON.parse(row.auditResults),
    github: row.github ? JSON.parse(row.github) : undefined,
    cicd: row.cicd ? JSON.parse(row.cicd) : undefined,
    docs: row.docs ? JSON.parse(row.docs) : undefined,
    export: row.export ? JSON.parse(row.export) : undefined,
    startedAt: new Date(row.startedAt).getTime(),
    completedAt: row.completedAt ? new Date(row.completedAt).getTime() : undefined
  };
};

export const getLoop3StateByProject = (projectId: string): Loop3State | null => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop3_state WHERE project_id = ? ORDER BY created_at DESC LIMIT 1');
  const row = stmt.get(projectId) as Loop3StateDB | undefined;

  if (!row) return null;

  return {
    id: row.id,
    projectId: row.projectId,
    status: row.status as Loop3State['status'],
    currentStep: row.currentStep as Loop3State['currentStep'],
    auditResults: JSON.parse(row.auditResults),
    github: row.github ? JSON.parse(row.github) : undefined,
    cicd: row.cicd ? JSON.parse(row.cicd) : undefined,
    docs: row.docs ? JSON.parse(row.docs) : undefined,
    export: row.export ? JSON.parse(row.export) : undefined,
    startedAt: new Date(row.startedAt).getTime(),
    completedAt: row.completedAt ? new Date(row.completedAt).getTime() : undefined
  };
};

export const deleteLoop3State = (id: string): void => {
  const db = getDatabase();
  const stmt = db.prepare('DELETE FROM loop3_state WHERE id = ?');
  stmt.run(id);
};

export const getAllLoop3States = (): Loop3State[] => {
  const db = getDatabase();
  const stmt = db.prepare('SELECT * FROM loop3_state ORDER BY created_at DESC');
  const rows = stmt.all() as Loop3StateDB[];

  return rows.map(row => ({
    id: row.id,
    projectId: row.projectId,
    status: row.status as Loop3State['status'],
    currentStep: row.currentStep as Loop3State['currentStep'],
    auditResults: JSON.parse(row.auditResults),
    github: row.github ? JSON.parse(row.github) : undefined,
    cicd: row.cicd ? JSON.parse(row.cicd) : undefined,
    docs: row.docs ? JSON.parse(row.docs) : undefined,
    export: row.export ? JSON.parse(row.export) : undefined,
    startedAt: new Date(row.startedAt).getTime(),
    completedAt: row.completedAt ? new Date(row.completedAt).getTime() : undefined
  }));
};
