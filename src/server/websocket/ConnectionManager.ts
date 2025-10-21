/**
 * ConnectionManager - Manages WebSocket client connections and state
 *
 * Tracks all active connections, manages room subscriptions, and handles
 * state reconciliation when clients reconnect after network interruptions.
 *
 * Features:
 * - Connection tracking with metadata
 * - Room subscription management
 * - State reconciliation on reconnect
 * - Connection health monitoring
 *
 * Week 4 Day 1
 * Version: 8.0.0
 */

import type { Socket } from 'socket.io';

// ============================================================================
// Types
// ============================================================================

export interface ConnectionInfo {
  socketId: string;
  userId?: string;
  projectId?: string;
  connectedAt: number;
  lastActivity: number;
  rooms: Set<string>;
  metadata: Record<string, any>;
}

export interface ReconnectionState {
  lastEventSequence: number;
  missedEvents: any[];
  rooms: string[];
}

// ============================================================================
// ConnectionManager Class
// ============================================================================

export class ConnectionManager {
  private connections: Map<string, ConnectionInfo>;
  private userSockets: Map<string, Set<string>>;  // userId -> socketIds
  private reconnectionState: Map<string, ReconnectionState>;

  constructor() {
    this.connections = new Map();
    this.userSockets = new Map();
    this.reconnectionState = new Map();
  }

  /**
   * Handle new WebSocket connection.
   *
   * Tracks connection metadata and sets up event listeners.
   */
  handleConnection(socket: Socket, userId?: string): void {
    const connectionInfo: ConnectionInfo = {
      socketId: socket.id,
      userId,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
      rooms: new Set(),
      metadata: {}
    };

    // Track connection
    this.connections.set(socket.id, connectionInfo);

    // Track user connections (multiple sockets per user possible)
    if (userId) {
      if (!this.userSockets.has(userId)) {
        this.userSockets.set(userId, new Set());
      }
      this.userSockets.get(userId)!.add(socket.id);
    }

    console.log(`📊 Connection tracked: ${socket.id} (user: ${userId || 'anonymous'})`);
  }

  /**
   * Handle client disconnection.
   *
   * Stores reconnection state for potential reconnect.
   */
  handleDisconnection(socketId: string): void {
    const connection = this.connections.get(socketId);
    if (!connection) return;

    // Store reconnection state (10 minute TTL)
    if (connection.userId) {
      this.storeReconnectionState(connection);

      // Remove from user sockets
      const userSockets = this.userSockets.get(connection.userId);
      if (userSockets) {
        userSockets.delete(socketId);
        if (userSockets.size === 0) {
          this.userSockets.delete(connection.userId);
        }
      }
    }

    // Remove connection
    this.connections.delete(socketId);

    console.log(`📊 Connection removed: ${socketId}`);
  }

  /**
   * Store reconnection state for later recovery.
   *
   * Allows client to resume from last known state after reconnect.
   */
  private storeReconnectionState(connection: ConnectionInfo): void {
    if (!connection.userId) return;

    const state: ReconnectionState = {
      lastEventSequence: 0,  // TODO: Implement event sequencing
      missedEvents: [],
      rooms: Array.from(connection.rooms)
    };

    this.reconnectionState.set(connection.userId, state);

    // Auto-cleanup after 10 minutes
    setTimeout(() => {
      this.reconnectionState.delete(connection.userId!);
    }, 600000);
  }

  /**
   * Handle client reconnection.
   *
   * Restores previous state and resubscribes to rooms.
   */
  handleReconnection(socket: Socket, userId: string): ReconnectionState | null {
    const state = this.reconnectionState.get(userId);
    if (!state) return null;

    // Resubscribe to previous rooms
    state.rooms.forEach(room => {
      socket.join(room);
      this.joinRoom(socket.id, room);
    });

    // Clear reconnection state (consumed)
    this.reconnectionState.delete(userId);

    console.log(`🔄 Reconnection handled for user: ${userId} (${state.rooms.length} rooms restored)`);

    return state;
  }

  /**
   * Track room subscription.
   *
   * Updates connection metadata when client joins a room.
   */
  joinRoom(socketId: string, room: string): void {
    const connection = this.connections.get(socketId);
    if (!connection) return;

    connection.rooms.add(room);
    connection.lastActivity = Date.now();
  }

  /**
   * Track room unsubscription.
   *
   * Updates connection metadata when client leaves a room.
   */
  leaveRoom(socketId: string, room: string): void {
    const connection = this.connections.get(socketId);
    if (!connection) return;

    connection.rooms.delete(room);
    connection.lastActivity = Date.now();
  }

  /**
   * Update connection metadata.
   *
   * Stores arbitrary metadata for a connection (e.g., current project).
   */
  updateMetadata(
    socketId: string,
    metadata: Record<string, any>
  ): void {
    const connection = this.connections.get(socketId);
    if (!connection) return;

    connection.metadata = { ...connection.metadata, ...metadata };
    connection.lastActivity = Date.now();
  }

  /**
   * Get connection information.
   */
  getConnection(socketId: string): ConnectionInfo | undefined {
    return this.connections.get(socketId);
  }

  /**
   * Get all connections for a user.
   */
  getUserConnections(userId: string): ConnectionInfo[] {
    const socketIds = this.userSockets.get(userId);
    if (!socketIds) return [];

    return Array.from(socketIds)
      .map(id => this.connections.get(id))
      .filter((conn): conn is ConnectionInfo => conn !== undefined);
  }

  /**
   * Get total connection count.
   */
  getConnectionCount(): number {
    return this.connections.size;
  }

  /**
   * Get unique user count.
   */
  getUserCount(): number {
    return this.userSockets.size;
  }

  /**
   * Get connections in a specific room.
   */
  getRoomConnections(room: string): ConnectionInfo[] {
    return Array.from(this.connections.values())
      .filter(conn => conn.rooms.has(room));
  }

  /**
   * Check if connection is still active.
   *
   * Returns false if connection hasn't been active for >5 minutes.
   */
  isConnectionActive(socketId: string): boolean {
    const connection = this.connections.get(socketId);
    if (!connection) return false;

    const idleTime = Date.now() - connection.lastActivity;
    return idleTime < 300000;  // 5 minutes
  }

  /**
   * Clean up stale connections.
   *
   * Removes connections that haven't been active for >10 minutes.
   */
  cleanupStaleConnections(): number {
    let cleaned = 0;
    const now = Date.now();

    for (const [socketId, connection] of this.connections.entries()) {
      const idleTime = now - connection.lastActivity;
      if (idleTime > 600000) {  // 10 minutes
        this.handleDisconnection(socketId);
        cleaned++;
      }
    }

    if (cleaned > 0) {
      console.log(`🧹 Cleaned ${cleaned} stale connections`);
    }

    return cleaned;
  }
}

/**
 * Factory function to create ConnectionManager instance.
 */
export function createConnectionManager(): ConnectionManager {
  return new ConnectionManager();
}
