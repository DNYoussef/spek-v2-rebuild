/**
 * WebSocket Server Module
 *
 * Exports all WebSocket server components for Week 4 Day 1.
 *
 * Usage:
 *   import { SocketServer, ConnectionManager, EventThrottler } from './websocket';
 *
 * Version: 8.0.0
 */

export {
  SocketServer,
  createSocketServer,
  type SocketServerConfig,
  type AgentThought,
  type TaskUpdate,
  type ConnectionMetrics
} from './SocketServer.js';

export {
  ConnectionManager,
  createConnectionManager,
  type ConnectionInfo,
  type ReconnectionState
} from './ConnectionManager.js';

export {
  EventThrottler,
  createEventThrottler,
  type ThrottlerConfig,
  type QueuedEvent,
  type EventQueue
} from './EventThrottler.js';
