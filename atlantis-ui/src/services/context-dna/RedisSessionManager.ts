/**
 * Redis Session Manager
 *
 * Manages agent execution sessions using Redis for caching and state.
 * Provides fast session lookup and automatic expiration.
 *
 * Week 20 Day 1
 * Version: 8.0.0
 */

import { Redis } from 'ioredis';
import { AgentExecutionContext } from './AgentContextIntegration';

/**
 * Session state stored in Redis
 */
export interface SessionState {
  sessionId: string;
  agentId: string;
  projectId: string;
  taskId?: string;
  parentAgentId?: string;
  status: 'active' | 'completed' | 'failed';
  startTime: string; // ISO timestamp
  lastActivity: string; // ISO timestamp
  thoughtCount: number;
  metadata?: Record<string, unknown>;
}

/**
 * Session statistics
 */
export interface SessionStats {
  totalSessions: number;
  activeSessions: number;
  completedSessions: number;
  failedSessions: number;
  averageDurationMs: number;
}

/**
 * RedisSessionManager
 *
 * Manages agent execution sessions in Redis.
 * Provides fast session state tracking and automatic cleanup.
 */
export class RedisSessionManager {
  private redis: Redis;
  private sessionTTL: number; // Session TTL in seconds (default: 24 hours)

  constructor(redis?: Redis, sessionTTL = 86400) {
    this.redis = redis || new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD,
      db: parseInt(process.env.REDIS_DB || '0'),
    });
    this.sessionTTL = sessionTTL;
  }

  /**
   * Create new session
   */
  async createSession(context: AgentExecutionContext): Promise<void> {
    const sessionKey = this.getSessionKey(context.sessionId);

    const state: SessionState = {
      sessionId: context.sessionId,
      agentId: context.agentId,
      projectId: context.projectId,
      taskId: context.taskId,
      parentAgentId: context.parentAgentId,
      status: 'active',
      startTime: context.startTime.toISOString(),
      lastActivity: new Date().toISOString(),
      thoughtCount: 0,
      metadata: context.metadata,
    };

    await this.redis.setex(
      sessionKey,
      this.sessionTTL,
      JSON.stringify(state)
    );

    // Add to active sessions set
    await this.redis.sadd('sessions:active', context.sessionId);

    // Index by agent ID
    await this.redis.sadd(
      `sessions:agent:${context.agentId}`,
      context.sessionId
    );

    // Index by project ID
    await this.redis.sadd(
      `sessions:project:${context.projectId}`,
      context.sessionId
    );
  }

  /**
   * Get session state
   */
  async getSession(sessionId: string): Promise<SessionState | null> {
    const sessionKey = this.getSessionKey(sessionId);
    const data = await this.redis.get(sessionKey);

    if (!data) {
      return null;
    }

    return JSON.parse(data);
  }

  /**
   * Update session activity
   */
  async updateActivity(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId);

    if (!session) {
      return;
    }

    session.lastActivity = new Date().toISOString();
    session.thoughtCount += 1;

    await this.redis.setex(
      this.getSessionKey(sessionId),
      this.sessionTTL,
      JSON.stringify(session)
    );
  }

  /**
   * Complete session
   */
  async completeSession(
    sessionId: string,
    success: boolean
  ): Promise<void> {
    const session = await this.getSession(sessionId);

    if (!session) {
      return;
    }

    session.status = success ? 'completed' : 'failed';
    session.lastActivity = new Date().toISOString();

    await this.redis.setex(
      this.getSessionKey(sessionId),
      this.sessionTTL,
      JSON.stringify(session)
    );

    // Move from active to completed/failed
    await this.redis.srem('sessions:active', sessionId);
    await this.redis.sadd(
      success ? 'sessions:completed' : 'sessions:failed',
      sessionId
    );
  }

  /**
   * Get sessions by agent ID
   */
  async getSessionsByAgent(agentId: string): Promise<string[]> {
    return await this.redis.smembers(`sessions:agent:${agentId}`);
  }

  /**
   * Get sessions by project ID
   */
  async getSessionsByProject(projectId: string): Promise<string[]> {
    return await this.redis.smembers(`sessions:project:${projectId}`);
  }

  /**
   * Get active sessions
   */
  async getActiveSessions(): Promise<string[]> {
    return await this.redis.smembers('sessions:active');
  }

  /**
   * Get session statistics
   */
  async getStats(): Promise<SessionStats> {
    const [active, completed, failed] = await Promise.all([
      this.redis.scard('sessions:active'),
      this.redis.scard('sessions:completed'),
      this.redis.scard('sessions:failed'),
    ]);

    const total = active + completed + failed;

    // Calculate average duration from completed sessions
    const completedSessions = await this.redis.smembers('sessions:completed');
    let totalDuration = 0;

    for (const sessionId of completedSessions.slice(0, 100)) {
      const session = await this.getSession(sessionId);
      if (session) {
        const startTime = new Date(session.startTime).getTime();
        const endTime = new Date(session.lastActivity).getTime();
        totalDuration += endTime - startTime;
      }
    }

    const averageDurationMs =
      completedSessions.length > 0
        ? totalDuration / Math.min(completedSessions.length, 100)
        : 0;

    return {
      totalSessions: total,
      activeSessions: active,
      completedSessions: completed,
      failedSessions: failed,
      averageDurationMs,
    };
  }

  /**
   * Cleanup expired sessions
   * Called periodically to remove orphaned entries
   */
  async cleanupExpiredSessions(): Promise<number> {
    const sets = [
      'sessions:active',
      'sessions:completed',
      'sessions:failed',
    ];

    let cleanedCount = 0;

    for (const set of sets) {
      const sessionIds = await this.redis.smembers(set);

      for (const sessionId of sessionIds) {
        const session = await this.getSession(sessionId);

        if (!session) {
          // Session expired, remove from set
          await this.redis.srem(set, sessionId);
          cleanedCount++;
        }
      }
    }

    return cleanedCount;
  }

  /**
   * Close Redis connection
   */
  async close(): Promise<void> {
    await this.redis.quit();
  }

  // Private helper methods
  private getSessionKey(sessionId: string): string {
    return `session:${sessionId}`;
  }
}

/**
 * Singleton instance
 */
let redisSessionManagerInstance: RedisSessionManager | null = null;

/**
 * Get or create RedisSessionManager singleton
 */
export function getRedisSessionManager(): RedisSessionManager {
  if (!redisSessionManagerInstance) {
    redisSessionManagerInstance = new RedisSessionManager();
  }
  return redisSessionManagerInstance;
}
