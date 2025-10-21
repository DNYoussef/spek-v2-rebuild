/**
 * EventThrottler - Rate limits WebSocket events to prevent client overload
 *
 * Limits event broadcasting to max 10 events/sec per user to prevent
 * UI lag and reduce battery consumption on client devices.
 *
 * Features:
 * - Per-user event queuing
 * - Automatic batching of similar events
 * - Configurable rate limits
 * - Event priority support
 *
 * Week 4 Day 1
 * Version: 8.0.0
 */

// ============================================================================
// Types
// ============================================================================

export interface ThrottlerConfig {
  maxEventsPerSecond: number;
  batchSimilarEvents: boolean;
  eventPriority: boolean;
}

export interface QueuedEvent {
  type: string;
  data: any;
  timestamp: number;
  priority: number;  // 0-10, 10=highest
}

export interface EventQueue {
  userId: string;
  events: QueuedEvent[];
  lastFlush: number;
  eventsSent: number;
}

// ============================================================================
// EventThrottler Class
// ============================================================================

export class EventThrottler {
  private config: ThrottlerConfig;
  private queues: Map<string, EventQueue>;
  private flushInterval: NodeJS.Timeout | null;

  constructor(config?: Partial<ThrottlerConfig>) {
    this.config = {
      maxEventsPerSecond: 10,
      batchSimilarEvents: true,
      eventPriority: true,
      ...config
    };

    this.queues = new Map();
    this.flushInterval = null;

    // Start flush interval (100ms ticks)
    this.startFlushInterval();
  }

  /**
   * Add event to user's queue.
   *
   * Events are queued and flushed at max rate.
   */
  enqueue(
    userId: string,
    type: string,
    data: any,
    priority: number = 5
  ): void {
    // Get or create queue
    let queue = this.queues.get(userId);
    if (!queue) {
      queue = {
        userId,
        events: [],
        lastFlush: Date.now(),
        eventsSent: 0
      };
      this.queues.set(userId, queue);
    }

    // Create event
    const event: QueuedEvent = {
      type,
      data,
      timestamp: Date.now(),
      priority
    };

    // Check if we should batch with existing event
    if (this.config.batchSimilarEvents) {
      const batched = this.tryBatchEvent(queue, event);
      if (batched) return;
    }

    // Add to queue
    queue.events.push(event);

    // Sort by priority if enabled
    if (this.config.eventPriority) {
      this.sortQueueByPriority(queue);
    }
  }

  /**
   * Try to batch event with existing similar event.
   *
   * Returns true if batched, false if not.
   */
  private tryBatchEvent(queue: EventQueue, event: QueuedEvent): boolean {
    // Find similar event in queue
    const similar = queue.events.find(e => e.type === event.type);
    if (!similar) return false;

    // Batch similar events (e.g., multiple agent thoughts)
    if (event.type === 'agent-thought') {
      // Merge into single batch event
      if (!Array.isArray(similar.data)) {
        similar.data = [similar.data];
      }
      similar.data.push(event.data);
      similar.timestamp = event.timestamp;  // Update to latest
      return true;
    }

    // Batch task updates (keep only latest)
    if (event.type === 'task-update') {
      similar.data = event.data;  // Replace with latest
      similar.timestamp = event.timestamp;
      return true;
    }

    return false;
  }

  /**
   * Sort queue events by priority (highest first).
   */
  private sortQueueByPriority(queue: EventQueue): void {
    queue.events.sort((a, b) => b.priority - a.priority);
  }

  /**
   * Start flush interval.
   *
   * Flushes events every 100ms at configured rate.
   */
  private startFlushInterval(): void {
    this.flushInterval = setInterval(() => {
      this.flushAllQueues();
    }, 100);  // 100ms ticks
  }

  /**
   * Flush all user queues.
   *
   * Sends events at max configured rate per user.
   */
  private flushAllQueues(): void {
    const now = Date.now();

    for (const [userId, queue] of this.queues.entries()) {
      this.flushQueue(userId, queue, now);
    }

    // Cleanup empty queues
    this.cleanupEmptyQueues();
  }

  /**
   * Flush single user queue.
   *
   * Sends events at max rate (e.g., 10 events/sec = 1 per 100ms).
   */
  private flushQueue(userId: string, queue: EventQueue, now: number): void {
    if (queue.events.length === 0) return;

    // Calculate events to send this tick
    const timeSinceLastFlush = now - queue.lastFlush;
    const eventsPerTick = (this.config.maxEventsPerSecond / 10);  // 10 ticks/sec
    const eventsToSend = Math.floor(eventsPerTick);

    if (eventsToSend === 0) return;

    // Get events to send (highest priority first if enabled)
    const events = queue.events.splice(0, eventsToSend);

    // Emit events (handled by callback)
    events.forEach(event => {
      this.emitEvent(userId, event);
      queue.eventsSent++;
    });

    // Update last flush time
    queue.lastFlush = now;
  }

  /**
   * Emit event (to be overridden or handled via callback).
   *
   * In production, this would call SocketServer.emit()
   */
  private emitEvent(userId: string, event: QueuedEvent): void {
    // Placeholder - in real implementation, this would emit via Socket.io
    // console.log(`📤 [${userId}] ${event.type}:`, event.data);
  }

  /**
   * Set event emission callback.
   *
   * Allows SocketServer to handle actual emission.
   */
  onEmit(callback: (userId: string, event: QueuedEvent) => void): void {
    this.emitEvent = callback;
  }

  /**
   * Get queue for user.
   */
  getQueue(userId: string): EventQueue | undefined {
    return this.queues.get(userId);
  }

  /**
   * Get queue depth for user.
   */
  getQueueDepth(userId: string): number {
    const queue = this.queues.get(userId);
    return queue ? queue.events.length : 0;
  }

  /**
   * Get total events sent for user.
   */
  getEventsSent(userId: string): number {
    const queue = this.queues.get(userId);
    return queue ? queue.eventsSent : 0;
  }

  /**
   * Clear queue for user.
   */
  clearQueue(userId: string): void {
    this.queues.delete(userId);
  }

  /**
   * Cleanup empty queues.
   *
   * Removes queues with no pending events.
   */
  private cleanupEmptyQueues(): void {
    for (const [userId, queue] of this.queues.entries()) {
      if (queue.events.length === 0) {
        // Keep queue for 5 minutes after last activity
        const idleTime = Date.now() - queue.lastFlush;
        if (idleTime > 300000) {
          this.queues.delete(userId);
        }
      }
    }
  }

  /**
   * Shutdown throttler.
   *
   * Stops flush interval and clears queues.
   */
  shutdown(): void {
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
      this.flushInterval = null;
    }
    this.queues.clear();
  }
}

/**
 * Factory function to create EventThrottler instance.
 */
export function createEventThrottler(
  config?: Partial<ThrottlerConfig>
): EventThrottler {
  return new EventThrottler(config);
}
