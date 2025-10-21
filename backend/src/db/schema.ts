/**
 * SQLite Database Schema for SPEK Platform v2
 * Provides persistent state storage for Loop 1 & Loop 2
 *
 * Week 10 Day 1 Implementation
 */

export interface Loop1State {
  id: string;
  projectId: string;
  iteration: number;
  failureRate: number;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  researchPhase: ResearchPhaseData | null;
  premortemPhase: PremortemPhaseData | null;
  remediationPhase: RemediationPhaseData | null;
  createdAt: string;
  updatedAt: string;
}

export interface ResearchPhaseData {
  githubResults: GitHubResult[];
  paperResults: PaperResult[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  completedAt: string | null;
}

export interface GitHubResult {
  name: string;
  url: string;
  stars: number;
  description: string;
}

export interface PaperResult {
  title: string;
  authors: string[];
  year: number;
  url: string;
  citations: number;
}

export interface PremortemPhaseData {
  scenarios: FailureScenario[];
  riskScore: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  completedAt: string | null;
}

export interface FailureScenario {
  id: string;
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  description: string;
  likelihood: number; // 0-1
  impact: number; // 0-1
  prevention: string;
}

export interface RemediationPhaseData {
  updates: string[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  completedAt: string | null;
}

export interface Loop2State {
  id: string;
  projectId: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  phases: Phase[];
  princesses: PrincessState[];
  createdAt: string;
  updatedAt: string;
}

export interface Phase {
  id: string;
  name: string;
  tasks: Task[];
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  completedAt: string | null;
}

export interface Task {
  id: string;
  type: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedTo: string | null;
  dependencies: string[];
  result: TaskResult | null;
  createdAt: string;
  completedAt: string | null;
}

export interface TaskResult {
  success: boolean;
  output: string;
  errors: string[];
}

export interface PrincessState {
  id: string;
  name: string;
  status: 'idle' | 'busy' | 'error';
  currentTask: string | null;
  droneCount: number;
  tasksCompleted: number;
  tasksInProgress: number;
  lastActive: string;
}

export interface AuditResult {
  id: string;
  projectId: string;
  taskId: string;
  stage: 'theater' | 'production' | 'quality';
  status: 'pass' | 'fail';
  issues: AuditIssue[];
  executionTime: number;
  createdAt: string;
}

export interface AuditIssue {
  severity: 'critical' | 'warning' | 'info';
  message: string;
  file: string | null;
  line: number | null;
}

export interface Loop3State {
  id: string;
  projectId: string;
  status: 'not_started' | 'audit_running' | 'audit_complete' | 'github_setup' | 'cicd_setup' | 'docs_cleanup' | 'export' | 'completed' | 'failed';
  currentStep: 'audit' | 'github' | 'cicd' | 'docs' | 'export' | 'complete';
  auditResults: string; // JSON
  github: string | null; // JSON
  cicd: string | null; // JSON
  docs: string | null; // JSON
  export: string | null; // JSON
  startedAt: string;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

/**
 * Database initialization SQL
 */
export const SCHEMA_SQL = `
-- Loop 1 State Table
CREATE TABLE IF NOT EXISTS loop1_state (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  iteration INTEGER DEFAULT 0,
  failure_rate REAL DEFAULT 100.0,
  status TEXT DEFAULT 'pending',
  research_phase TEXT, -- JSON
  premortem_phase TEXT, -- JSON
  remediation_phase TEXT, -- JSON
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Loop 2 State Table
CREATE TABLE IF NOT EXISTS loop2_state (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  phases TEXT, -- JSON array
  princesses TEXT, -- JSON array
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Audit Results Table
CREATE TABLE IF NOT EXISTS audit_results (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  stage TEXT NOT NULL,
  status TEXT NOT NULL,
  issues TEXT, -- JSON array
  execution_time INTEGER NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Loop 3 State Table
CREATE TABLE IF NOT EXISTS loop3_state (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  status TEXT DEFAULT 'not_started',
  current_step TEXT DEFAULT 'audit',
  audit_results TEXT, -- JSON
  github TEXT, -- JSON (nullable)
  cicd TEXT, -- JSON (nullable)
  docs TEXT, -- JSON (nullable)
  export TEXT, -- JSON (nullable)
  started_at TEXT NOT NULL,
  completed_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_loop1_project ON loop1_state(project_id);
CREATE INDEX IF NOT EXISTS idx_loop2_project ON loop2_state(project_id);
CREATE INDEX IF NOT EXISTS idx_loop3_project ON loop3_state(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_project ON audit_results(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_task ON audit_results(task_id);
`;
