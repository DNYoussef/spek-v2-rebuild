/**
 * WebSocket Broadcaster Service
 *
 * Integrates tRPC router with Socket.io WebSocket server.
 * Broadcasts real-time events for:
 * - Agent thoughts and status changes
 * - Task progress updates
 * - Project events
 * - Audit results
 *
 * Week 8 Day 2
 * Version: 8.0.0
 */

import type { SocketServer } from '../websocket/SocketServer';
import type { Agent } from '../routers/agent';
import type { Task } from '../routers/task';
import type { Project } from '../routers/project';

// ============================================================================
// Event Types
// ============================================================================

export interface AgentThoughtEvent {
  agentId: string;
  agentName: string;
  thought: string;
  taskId?: string;
  projectId?: string;
  timestamp: number;
}

export interface TaskProgressEvent {
  taskId: string;
  agentId: string;
  projectId?: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress?: number;  // 0-100
  message?: string;
  timestamp: number;
}

export interface AgentStatusEvent {
  agentId: string;
  agentName: string;
  status: 'idle' | 'active' | 'error';
  currentTaskId?: string;
  timestamp: number;
}

export interface ProjectEvent {
  projectId: string;
  projectName: string;
  event: 'created' | 'updated' | 'deleted' | 'vectorization-started' | 'vectorization-completed';
  data?: unknown;
  timestamp: number;
}

export interface AuditEvent {
  taskId: string;
  projectId: string;
  stage: 'theater' | 'production' | 'quality';
  status: 'started' | 'passed' | 'failed';
  result?: unknown;
  timestamp: number;
}

// ============================================================================
// WebSocket Broadcaster
// ============================================================================

export class WebSocketBroadcaster {
  private socketServer: SocketServer;
  private messageCount: number = 0;
  private startTime: number = Date.now();

  constructor(socketServer: SocketServer) {
    this.socketServer = socketServer;
  }

  /**
   * Broadcast agent thought to subscribers.
   *
   * Emits to room: agent:{agentId}
   * Also emits to project room if projectId provided
   */
  async broadcastAgentThought(event: AgentThoughtEvent): Promise<void> {
    this.messageCount++;

    // Emit to agent-specific room
    await this.socketServer.broadcastAgentThought({
      agentId: event.agentId,
      thought: event.thought,
      timestamp: event.timestamp,
      taskId: event.taskId,
    });

    // Also emit to project room if available
    if (event.projectId) {
      await this.socketServer.broadcastProjectEvent(
        event.projectId,
        'agent-thought',
        event
      );
    }
  }

  /**
   * Broadcast task progress update.
   *
   * Emits to room: task:{taskId}
   * Also emits to project room if projectId provided
   */
  async broadcastTaskProgress(event: TaskProgressEvent): Promise<void> {
    this.messageCount++;

    // Map status to TaskUpdate format
    const statusMap: Record<string, 'pending' | 'in_progress' | 'completed' | 'failed'> = {
      'queued': 'pending',
      'running': 'in_progress',
      'completed': 'completed',
      'failed': 'failed',
      'cancelled': 'failed',
    };

    // Emit to task-specific room
    await this.socketServer.broadcastTaskUpdate({
      taskId: event.taskId,
      status: statusMap[event.status] || 'pending',
      progress: event.progress,
      message: event.message,
      timestamp: event.timestamp,
    });

    // Also emit to project room if available
    if (event.projectId) {
      await this.socketServer.broadcastProjectEvent(
        event.projectId,
        'task-progress',
        event
      );
    }
  }

  /**
   * Broadcast agent status change.
   *
   * Emits to room: agent:{agentId}
   */
  async broadcastAgentStatus(event: AgentStatusEvent): Promise<void> {
    this.messageCount++;

    await this.socketServer.broadcastProjectEvent(
      `agent:${event.agentId}`,
      'agent-status',
      event
    );
  }

  /**
   * Broadcast project event.
   *
   * Emits to room: project:{projectId}
   */
  async broadcastProjectEvent(event: ProjectEvent): Promise<void> {
    this.messageCount++;

    await this.socketServer.broadcastProjectEvent(
      event.projectId,
      'project-event',
      event
    );
  }

  /**
   * Broadcast audit stage result.
   *
   * Emits to rooms: task:{taskId} and project:{projectId}
   */
  async broadcastAuditEvent(event: AuditEvent): Promise<void> {
    this.messageCount++;

    // Emit to task room
    await this.socketServer.broadcastProjectEvent(
      `task:${event.taskId}`,
      'audit-event',
      event
    );

    // Emit to project room
    await this.socketServer.broadcastProjectEvent(
      event.projectId,
      'audit-event',
      event
    );
  }

  /**
   * Get broadcaster metrics.
   */
  getMetrics(): {
    messageCount: number;
    uptime: number;
    messagesPerSecond: number;
  } {
    const uptime = Date.now() - this.startTime;
    const messagesPerSecond = this.messageCount / (uptime / 1000);

    return {
      messageCount: this.messageCount,
      uptime,
      messagesPerSecond,
    };
  }
}

/**
 * Factory function to create WebSocketBroadcaster.
 */
export function createWebSocketBroadcaster(
  socketServer: SocketServer
): WebSocketBroadcaster {
  return new WebSocketBroadcaster(socketServer);
}
