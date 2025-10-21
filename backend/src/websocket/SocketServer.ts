/**
 * SocketServer - WebSocket server with Redis Pub/Sub adapter
 *
 * Enables horizontal scaling to 200+ concurrent users by broadcasting
 * events across multiple server instances via Redis.
 *
 * Performance Targets:
 * - Concurrent users: 100+ Phase 1, 200+ Phase 2
 * - Message latency: <50ms (p95)
 * - Event throttling: 10 updates/sec per user
 * - Connection reliability: 99% uptime
 *
 * Week 4 Day 1
 * Version: 8.0.0
 */

import { Server, Socket } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient, RedisClientType } from 'redis';
import type { Server as HTTPServer } from 'http';

// ============================================================================
// Types
// ============================================================================

export interface SocketServerConfig {
  redisUrl: string;
  port?: number;
  corsOrigin?: string | string[];
  maxConnections?: number;
  pingInterval?: number;  // ms
  pingTimeout?: number;   // ms
}

export interface AgentThought {
  agentId: string;
  thought: string;
  timestamp: number;
  taskId?: string;
}

export interface TaskUpdate {
  taskId: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress?: number;  // 0-100
  message?: string;
  timestamp: number;
}

export interface ConnectionMetrics {
  totalConnections: number;
  activeConnections: number;
  peakConnections: number;
  messagesSent: number;
  messagesReceived: number;
  averageLatency: number;
}

// ============================================================================
// SocketServer Class
// ============================================================================

export class SocketServer {
  private io: Server | null = null;
  private pubClient: RedisClientType | null = null;
  private subClient: RedisClientType | null = null;
  private config: SocketServerConfig;
  private metrics: ConnectionMetrics;
  private connectionMap: Map<string, Socket>;

  constructor(config: SocketServerConfig) {
    this.config = {
      port: 3001,
      corsOrigin: '*',
      maxConnections: 1000,
      pingInterval: 25000,
      pingTimeout: 20000,
      ...config
    };

    this.metrics = {
      totalConnections: 0,
      activeConnections: 0,
      peakConnections: 0,
      messagesSent: 0,
      messagesReceived: 0,
      averageLatency: 0
    };

    this.connectionMap = new Map();
  }

  /**
   * Initialize WebSocket server with Redis adapter.
   *
   * Sets up:
   * - Socket.io server
   * - Redis pub/sub clients
   * - Redis adapter for horizontal scaling
   * - Event handlers
   */
  async initialize(httpServer: HTTPServer): Promise<void> {
    // Create Socket.io server
    this.io = new Server(httpServer, {
      cors: {
        origin: this.config.corsOrigin,
        methods: ['GET', 'POST']
      },
      pingInterval: this.config.pingInterval,
      pingTimeout: this.config.pingTimeout,
      maxHttpBufferSize: 1e6  // 1MB max message size
    });

    // Setup Redis clients for adapter
    await this.setupRedisAdapter();

    // Setup event handlers
    this.setupEventHandlers();

    console.log(`✅ SocketServer initialized on port ${this.config.port}`);
  }

  /**
   * Setup Redis Pub/Sub adapter for horizontal scaling.
   *
   * Creates two Redis clients:
   * - pubClient: Publishes messages to other server instances
   * - subClient: Subscribes to messages from other instances
   */
  private async setupRedisAdapter(): Promise<void> {
    // Skip Redis if URL is empty (development mode)
    if (!this.config.redisUrl) {
      console.warn('⚠️  Redis disabled - running in single-server mode');
      console.warn('   Set REDIS_URL environment variable for horizontal scaling');
      return;
    }

    try {
      // Create pub/sub clients
      this.pubClient = createClient({ url: this.config.redisUrl });
      this.subClient = this.pubClient.duplicate();

      // Add error handlers before connecting
      this.pubClient.on('error', (err) => {
        console.warn('⚠️  Redis pub client error:', err.message);
      });
      this.subClient.on('error', (err) => {
        console.warn('⚠️  Redis sub client error:', err.message);
      });

      // Connect clients
      await this.pubClient.connect();
      await this.subClient.connect();

      // Attach Redis adapter to Socket.io
      if (this.io) {
        this.io.adapter(createAdapter(this.pubClient, this.subClient));
      }

      console.log('✅ Redis adapter connected');
    } catch (error) {
      console.warn('⚠️  Redis adapter failed, running in single-server mode:', error instanceof Error ? error.message : error);
      console.warn('   Horizontal scaling disabled (this is OK for development/testing)');
      // Don't throw - allow server to continue without Redis
      this.pubClient = null;
      this.subClient = null;
    }
  }

  /**
   * Setup Socket.io event handlers.
   *
   * Handles:
   * - New connections
   * - Disconnections
   * - Room subscriptions
   * - Message routing
   */
  private setupEventHandlers(): void {
    if (!this.io) return;

    this.io.on('connection', (socket: Socket) => {
      this.handleConnection(socket);
    });
  }

  /**
   * Handle new WebSocket connection.
   *
   * Tracks connection metrics and sets up client event listeners.
   */
  private handleConnection(socket: Socket): void {
    // Update metrics
    this.metrics.totalConnections++;
    this.metrics.activeConnections++;
    if (this.metrics.activeConnections > this.metrics.peakConnections) {
      this.metrics.peakConnections = this.metrics.activeConnections;
    }

    // Track connection
    this.connectionMap.set(socket.id, socket);

    console.log(`✅ Client connected: ${socket.id} (${this.metrics.activeConnections} active)`);

    // Handle room subscriptions
    socket.on('subscribe-agent', (agentId: string) => {
      socket.join(`agent:${agentId}`);
      console.log(`📡 ${socket.id} subscribed to agent:${agentId}`);
    });

    socket.on('subscribe-project', (projectId: string) => {
      socket.join(`project:${projectId}`);
      console.log(`📡 ${socket.id} subscribed to project:${projectId}`);
    });

    socket.on('subscribe-task', (taskId: string) => {
      socket.join(`task:${taskId}`);
      console.log(`📡 ${socket.id} subscribed to task:${taskId}`);
    });

    // Handle disconnection
    socket.on('disconnect', () => {
      this.handleDisconnection(socket.id);
    });

    // Handle errors
    socket.on('error', (error) => {
      console.error(`❌ Socket error ${socket.id}:`, error);
    });
  }

  /**
   * Handle client disconnection.
   *
   * Updates metrics and cleans up tracking.
   */
  private handleDisconnection(socketId: string): void {
    this.metrics.activeConnections--;
    this.connectionMap.delete(socketId);
    console.log(`👋 Client disconnected: ${socketId} (${this.metrics.activeConnections} active)`);
  }

  /**
   * Broadcast agent thought to all subscribers.
   *
   * Emits to room: agent:{agentId}
   * Latency target: <50ms (p95)
   */
  async broadcastAgentThought(agentThought: AgentThought): Promise<void> {
    if (!this.io) throw new Error('Server not initialized');

    const room = `agent:${agentThought.agentId}`;

    this.io.to(room).emit('agent-thought', agentThought);
    this.metrics.messagesSent++;
  }

  /**
   * Broadcast task update to all subscribers.
   *
   * Emits to room: task:{taskId}
   * Latency target: <50ms (p95)
   */
  async broadcastTaskUpdate(taskUpdate: TaskUpdate): Promise<void> {
    if (!this.io) throw new Error('Server not initialized');

    const room = `task:${taskUpdate.taskId}`;

    this.io.to(room).emit('task-update', taskUpdate);
    this.metrics.messagesSent++;
  }

  /**
   * Broadcast project event to all subscribers.
   *
   * Emits to room: project:{projectId}
   */
  async broadcastProjectEvent(
    projectId: string,
    event: string,
    data: any
  ): Promise<void> {
    if (!this.io) throw new Error('Server not initialized');

    const room = `project:${projectId}`;

    this.io.to(room).emit(event, data);
    this.metrics.messagesSent++;
  }

  /**
   * Get current connection metrics.
   */
  getMetrics(): ConnectionMetrics {
    return { ...this.metrics };
  }

  /**
   * Get active connection count.
   */
  getActiveConnections(): number {
    return this.metrics.activeConnections;
  }

  /**
   * Shutdown server gracefully.
   *
   * Closes all connections and Redis clients.
   */
  async shutdown(): Promise<void> {
    console.log('🛑 Shutting down SocketServer...');

    // Close Socket.io server
    if (this.io) {
      this.io.close();
      this.io = null;
    }

    // Close Redis clients
    if (this.pubClient) {
      await this.pubClient.quit();
      this.pubClient = null;
    }

    if (this.subClient) {
      await this.subClient.quit();
      this.subClient = null;
    }

    console.log('✅ SocketServer shutdown complete');
  }
}

/**
 * Factory function to create SocketServer instance.
 */
export function createSocketServer(config: SocketServerConfig): SocketServer {
  return new SocketServer(config);
}
