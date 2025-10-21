/**
 * WebSocket Event Emitter
 * Broadcasts real-time events for Loop 1 & Loop 2 to connected clients
 *
 * Week 10 Day 2 Implementation
 * Replaces polling with push-based updates
 */

import { Server as SocketIOServer } from 'socket.io';

export type EventType =
  // Loop 1 events
  | 'loop1:started'
  | 'loop1:research_started'
  | 'loop1:research_completed'
  | 'loop1:premortem_started'
  | 'loop1:premortem_completed'
  | 'loop1:remediation_started'
  | 'loop1:remediation_completed'
  | 'loop1:iteration_completed'
  | 'loop1:completed'
  | 'loop1:paused'
  | 'loop1:resumed'
  | 'loop1:failed'
  // Loop 2 events
  | 'loop2:started'
  | 'loop2:phase_started'
  | 'loop2:phase_completed'
  | 'loop2:task_assigned'
  | 'loop2:task_started'
  | 'loop2:task_completed'
  | 'loop2:task_failed'
  | 'loop2:audit_started'
  | 'loop2:audit_completed'
  | 'loop2:completed'
  | 'loop2:failed'
  // Loop 3 events
  | 'loop3:started'
  | 'loop3:audit_started'
  | 'loop3:audit_completed'
  | 'loop3:github_setup_started'
  | 'loop3:github_configured'
  | 'loop3:cicd_generation_started'
  | 'loop3:cicd_generation_completed'
  | 'loop3:docs_cleanup_started'
  | 'loop3:docs_scan_completed'
  | 'loop3:docs_cleanup_completed'
  | 'loop3:export_started'
  | 'loop3:export_completed'
  | 'loop3:completed'
  | 'loop3:failed';

export interface WebSocketEvent {
  type: EventType;
  projectId: string;
  data: any;
  timestamp: number;
}

/**
 * Singleton WebSocket event emitter
 * Manages Socket.IO server instance and event broadcasting
 */
export class WebSocketEventEmitter {
  private static instance: WebSocketEventEmitter | null = null;
  private io: SocketIOServer | null = null;

  private constructor() {}

  /**
   * Get singleton instance
   */
  static getInstance(): WebSocketEventEmitter {
    if (!WebSocketEventEmitter.instance) {
      WebSocketEventEmitter.instance = new WebSocketEventEmitter();
    }
    return WebSocketEventEmitter.instance;
  }

  /**
   * Initialize with Socket.IO server
   */
  initialize(io: SocketIOServer): void {
    this.io = io;
    this.setupEventHandlers();
  }

  /**
   * Setup Socket.IO event handlers
   */
  private setupEventHandlers(): void {
    if (!this.io) return;

    this.io.on('connection', (socket) => {
      console.log(`[WebSocket] Client connected: ${socket.id}`);

      // Handle project subscription
      socket.on('subscribe:project', (projectId: string) => {
        socket.join(`project:${projectId}`);
        console.log(`[WebSocket] Client ${socket.id} subscribed to project:${projectId}`);
      });

      // Handle project unsubscription
      socket.on('unsubscribe:project', (projectId: string) => {
        socket.leave(`project:${projectId}`);
        console.log(`[WebSocket] Client ${socket.id} unsubscribed from project:${projectId}`);
      });

      socket.on('disconnect', () => {
        console.log(`[WebSocket] Client disconnected: ${socket.id}`);
      });
    });
  }

  /**
   * Emit event to all clients subscribed to a project
   */
  emit(event: WebSocketEvent): void {
    if (!this.io) {
      console.warn('[WebSocket] Socket.IO not initialized, event not emitted:', event.type);
      return;
    }

    const room = `project:${event.projectId}`;
    this.io.to(room).emit(event.type, event);

    console.log(`[WebSocket] Emitted ${event.type} to ${room}`);
  }

  /**
   * Emit Loop 1 event
   */
  emitLoop1Event(
    projectId: string,
    type: EventType,
    data: any
  ): void {
    this.emit({
      type,
      projectId,
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Emit Loop 2 event
   */
  emitLoop2Event(
    projectId: string,
    type: EventType,
    data: any
  ): void {
    this.emit({
      type,
      projectId,
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Emit Loop 3 event
   */
  emitLoop3Event(
    projectId: string,
    type: string,
    data: any
  ): void {
    const eventType = `loop3:${type}` as EventType;
    this.emit({
      type: eventType,
      projectId,
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Check if WebSocket is initialized
   */
  isInitialized(): boolean {
    return this.io !== null;
  }
}

/**
 * Helper function to get emitter instance
 */
export const getWebSocketEmitter = (): WebSocketEventEmitter => {
  return WebSocketEventEmitter.getInstance();
};
