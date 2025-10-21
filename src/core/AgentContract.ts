/**
 * AgentContract - Unified Agent Interface
 *
 * Defines the contract that all 22 agents in SPEK Platform v8 must implement.
 * Ensures consistent API, validation, execution, and metadata across all agents.
 *
 * Design Principles:
 * - Unified API for all agents (core, swarm, specialized)
 * - <5ms validation latency target
 * - Extensible metadata system
 * - Type-safe with TypeScript strict mode
 *
 * Version: 8.0.0 (Week 3 Day 1)
 */

/**
 * Task represents work to be performed by an agent.
 */
export interface Task {
  /** Unique task identifier (UUID v4) */
  id: string;

  /** Task type (e.g., "code", "test", "review", "research") */
  type: string;

  /** Task description (human-readable) */
  description: string;

  /** Task payload (type-specific data) */
  payload: Record<string, unknown>;

  /** Task priority (0-10, 10=highest) */
  priority: number;

  /** Task timeout in milliseconds (default: 300000 = 5 min) */
  timeout?: number;

  /** Task context (working directory, project info) */
  context?: TaskContext;

  /** Task metadata (custom fields) */
  metadata?: Record<string, unknown>;
}

/**
 * TaskContext provides execution context for a task.
 */
export interface TaskContext {
  /** Working directory (absolute path) */
  workingDirectory: string;

  /** Project root (absolute path with .project-boundary marker) */
  projectRoot: string;

  /** Project name */
  projectName?: string;

  /** Git commit hash (for caching) */
  gitCommitHash?: string;

  /** Previous task results (for chaining) */
  previousResults?: Result[];
}

/**
 * Result represents the outcome of task execution.
 */
export interface Result {
  /** Task ID this result corresponds to */
  taskId: string;

  /** Success indicator */
  success: boolean;

  /** Result data (type-specific) */
  data?: Record<string, unknown>;

  /** Error information (if success=false) */
  error?: ErrorInfo;

  /** Execution time in milliseconds */
  executionTime: number;

  /** Agent ID that produced this result */
  agentId: string;

  /** Result metadata */
  metadata?: ResultMetadata;
}

/**
 * ErrorInfo provides structured error details.
 */
export interface ErrorInfo {
  /** Error code (e.g., "VALIDATION_FAILED", "TIMEOUT") */
  code: string;

  /** Error message (human-readable) */
  message: string;

  /** Stack trace (for debugging) */
  stack?: string;

  /** Additional error context */
  context?: Record<string, unknown>;
}

/**
 * ResultMetadata provides additional result information.
 */
export interface ResultMetadata {
  /** Timestamp (ISO 8601) */
  timestamp: string;

  /** Retry count (if retried) */
  retryCount?: number;

  /** Resource usage */
  resourceUsage?: ResourceUsage;

  /** Artifacts produced (file paths) */
  artifacts?: string[];
}

/**
 * ResourceUsage tracks resource consumption.
 */
export interface ResourceUsage {
  /** CPU time in milliseconds */
  cpuTime?: number;

  /** Memory peak in bytes */
  memoryPeak?: number;

  /** Disk I/O in bytes */
  diskIO?: number;

  /** Network I/O in bytes */
  networkIO?: number;
}

/**
 * AgentMetadata describes an agent's capabilities and configuration.
 */
export interface AgentMetadata {
  /** Agent unique identifier */
  agentId: string;

  /** Agent name (human-readable) */
  name: string;

  /** Agent type (e.g., "core", "swarm", "specialized") */
  type: AgentType;

  /** Agent version (semantic versioning) */
  version: string;

  /** Supported task types */
  supportedTaskTypes: string[];

  /** Agent capabilities */
  capabilities: AgentCapability[];

  /** Agent status */
  status: AgentStatus;

  /** Agent configuration */
  config?: Record<string, unknown>;

  /** MCP tools available to this agent */
  mcpTools?: string[];
}

/**
 * AgentType categorizes agents by role.
 */
export enum AgentType {
  Core = "core",                  // queen, coder, researcher, tester, reviewer
  Swarm = "swarm",                // princess-dev, princess-quality, princess-coordination
  Specialized = "specialized"     // architect, debugger, docs-writer, etc.
}

/**
 * AgentCapability describes what an agent can do.
 */
export interface AgentCapability {
  /** Capability name */
  name: string;

  /** Capability description */
  description: string;

  /** Capability level (1-10, 10=expert) */
  level: number;
}

/**
 * AgentStatus indicates agent health and availability.
 */
export enum AgentStatus {
  Idle = "idle",
  Busy = "busy",
  Error = "error",
  Offline = "offline"
}

/**
 * ValidationResult indicates task validation outcome.
 */
export interface ValidationResult {
  /** Valid indicator */
  valid: boolean;

  /** Validation errors (if valid=false) */
  errors?: ValidationError[];

  /** Validation time in milliseconds */
  validationTime: number;
}

/**
 * ValidationError describes a validation failure.
 */
export interface ValidationError {
  /** Error field */
  field: string;

  /** Error message */
  message: string;

  /** Error severity (1-10, 10=critical) */
  severity: number;
}

/**
 * AgentContract - The core interface all agents must implement.
 *
 * Design: Abstract class (not pure interface) to provide common functionality.
 */
export abstract class AgentContract {
  /**
   * Agent metadata (must be set by implementing class)
   */
  abstract readonly metadata: AgentMetadata;

  /**
   * Validate a task before execution.
   *
   * Ensures task structure, payload, and context are valid.
   * Must complete in <5ms (p95 latency target).
   *
   * @param task - Task to validate
   * @returns ValidationResult with errors if invalid
   */
  abstract validate(task: Task): Promise<ValidationResult>;

  /**
   * Execute a validated task.
   *
   * Performs the actual work and returns a result.
   * Must handle timeouts gracefully.
   *
   * @param task - Task to execute (assumed valid)
   * @returns Result with success indicator and data/error
   */
  abstract execute(task: Task): Promise<Result>;

  /**
   * Get agent metadata.
   *
   * Returns current agent status, capabilities, and configuration.
   *
   * @returns AgentMetadata
   */
  getMetadata(): AgentMetadata {
    return this.metadata;
  }

  /**
   * Health check (optional, <10ms target).
   *
   * Verifies agent is responsive and healthy.
   * Default implementation returns true.
   *
   * @returns Promise<boolean> - true if healthy
   */
  async healthCheck(): Promise<boolean> {
    return true;
  }

  /**
   * Update agent status.
   *
   * Called by protocol to track agent availability.
   *
   * @param status - New agent status
   */
  updateStatus(status: AgentStatus): void {
    (this.metadata as { status: AgentStatus }).status = status;
  }

  /**
   * Validate task structure (common validation logic).
   *
   * Protected helper for implementing classes.
   *
   * @param task - Task to validate
   * @returns ValidationError[] if invalid, empty if valid
   */
  protected validateTaskStructure(task: Task): ValidationError[] {
    const errors: ValidationError[] = [];

    if (!task.id || typeof task.id !== 'string') {
      errors.push({
        field: 'id',
        message: 'Task ID must be a non-empty string',
        severity: 10
      });
    }

    if (!task.type || typeof task.type !== 'string') {
      errors.push({
        field: 'type',
        message: 'Task type must be a non-empty string',
        severity: 10
      });
    }

    if (!task.description || typeof task.description !== 'string') {
      errors.push({
        field: 'description',
        message: 'Task description must be a non-empty string',
        severity: 8
      });
    }

    if (!task.payload || typeof task.payload !== 'object') {
      errors.push({
        field: 'payload',
        message: 'Task payload must be an object',
        severity: 10
      });
    }

    if (typeof task.priority !== 'number' || task.priority < 0 || task.priority > 10) {
      errors.push({
        field: 'priority',
        message: 'Task priority must be a number between 0 and 10',
        severity: 6
      });
    }

    if (task.timeout && (typeof task.timeout !== 'number' || task.timeout <= 0)) {
      errors.push({
        field: 'timeout',
        message: 'Task timeout must be a positive number',
        severity: 6
      });
    }

    return errors;
  }

  /**
   * Validate task type (agent-specific).
   *
   * Protected helper for implementing classes.
   *
   * @param task - Task to validate
   * @returns ValidationError[] if type not supported
   */
  protected validateTaskType(task: Task): ValidationError[] {
    const errors: ValidationError[] = [];

    if (!this.metadata.supportedTaskTypes.includes(task.type)) {
      errors.push({
        field: 'type',
        message: `Task type '${task.type}' not supported by agent '${this.metadata.agentId}'`,
        severity: 10
      });
    }

    return errors;
  }

  /**
   * Build result object (common result construction).
   *
   * Protected helper for implementing classes.
   *
   * @param taskId - Task ID
   * @param success - Success indicator
   * @param data - Result data (optional)
   * @param error - Error info (optional)
   * @param executionTime - Execution time in ms
   * @returns Result object
   */
  protected buildResult(
    taskId: string,
    success: boolean,
    data?: Record<string, unknown>,
    error?: ErrorInfo,
    executionTime?: number
  ): Result {
    return {
      taskId,
      success,
      data,
      error,
      executionTime: executionTime ?? 0,
      agentId: this.metadata.agentId,
      metadata: {
        timestamp: new Date().toISOString()
      }
    };
  }
}

/**
 * Export all types for external use.
 */
export type {
  Task,
  TaskContext,
  Result,
  ErrorInfo,
  ResultMetadata,
  ResourceUsage,
  AgentMetadata,
  AgentCapability,
  ValidationResult,
  ValidationError
};

export {
  AgentType,
  AgentStatus
};
