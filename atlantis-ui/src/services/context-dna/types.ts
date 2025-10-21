/**
 * Context DNA Types
 *
 * Type definitions for the Context DNA storage system.
 * Context DNA provides 30-day retention of project context,
 * task history, agent conversations, and artifact references.
 */

export interface Project {
  id: string;
  name: string;
  description?: string;
  repositoryUrl?: string;
  createdAt: Date;
  lastAccessedAt: Date;
  metadata?: Record<string, unknown>;
}

export interface Task {
  id: string;
  projectId: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedTo?: string; // Agent ID
  princessId?: string; // Princess coordinator
  droneId?: string; // Drone worker
  createdAt: Date;
  completedAt?: Date;
  result?: TaskResult;
  metadata?: Record<string, unknown>;
}

export interface TaskResult {
  success: boolean;
  output?: string;
  error?: string;
  artifacts?: ArtifactReference[];
  metrics?: {
    durationMs?: number;
    tokensUsed?: number;
    retryCount?: number;
  };
}

export interface Conversation {
  id: string;
  projectId: string;
  taskId?: string;
  role: 'user' | 'agent' | 'system';
  agentId?: string;
  content: string;
  createdAt: Date;
  metadata?: Record<string, unknown>;
}

export interface ArtifactReference {
  id: string;
  projectId: string;
  taskId?: string;
  type: 'specification' | 'premortem' | 'research' | 'code' | 'test' | 'documentation' | 'screenshot';
  name: string;
  s3Path?: string; // S3 storage path (NOT full file content)
  localPath?: string; // Local filesystem path
  url?: string; // External URL
  sizeBytes?: number;
  createdAt: Date;
  metadata?: Record<string, unknown>;
}

export interface AgentMemory {
  id: string;
  agentId: string;
  projectId: string;
  taskId?: string;
  memoryType: 'success_pattern' | 'failure_pattern' | 'optimization' | 'context';
  content: string;
  importance: number; // 0-1 score
  createdAt: Date;
  lastAccessedAt: Date;
  accessCount: number;
  metadata?: Record<string, unknown>;
}

export interface SearchQuery {
  projectId?: string;
  taskId?: string;
  agentId?: string;
  query: string;
  limit?: number;
  before?: Date;
  after?: Date;
}

export interface SearchResult<T> {
  item: T;
  score: number;
  snippet?: string;
}

export interface RetentionPolicy {
  retentionDays: number;
  deleteAfter: Date;
}

export interface ContextDNAStats {
  totalProjects: number;
  totalTasks: number;
  totalConversations: number;
  totalArtifacts: number;
  totalAgentMemories: number;
  oldestEntry: Date;
  newestEntry: Date;
  storageBytes: number;
}
