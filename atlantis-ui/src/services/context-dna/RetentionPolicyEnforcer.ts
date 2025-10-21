/**
 * Retention Policy Enforcer
 *
 * Enforces 30-day retention policy for Context DNA.
 * Automatically cleans up old entries and manages storage.
 *
 * Week 20 Day 2
 * Version: 8.0.0
 */

import { ContextDNAStorage, getContextDNAStorage } from './ContextDNAStorage';
import { RedisSessionManager, getRedisSessionManager } from './RedisSessionManager';

/**
 * Retention policy configuration
 */
export interface RetentionPolicyConfig {
  retentionDays: number;
  enableAutomaticCleanup: boolean;
  cleanupIntervalHours: number;
}

/**
 * Cleanup result
 */
export interface CleanupResult {
  deleted: number;
  freedBytes: number;
  duration: number;
  timestamp: Date;
}

/**
 * RetentionPolicyEnforcer
 *
 * Manages automatic cleanup of old Context DNA entries.
 */
export class RetentionPolicyEnforcer {
  private storage: ContextDNAStorage;
  private sessionManager: RedisSessionManager;
  private config: RetentionPolicyConfig;
  private cleanupTimer?: NodeJS.Timeout;

  constructor(
    config?: Partial<RetentionPolicyConfig>,
    storage?: ContextDNAStorage,
    sessionManager?: RedisSessionManager
  ) {
    this.storage = storage || getContextDNAStorage();
    this.sessionManager = sessionManager || getRedisSessionManager();
    this.config = {
      retentionDays: config?.retentionDays || 30,
      enableAutomaticCleanup: config?.enableAutomaticCleanup ?? true,
      cleanupIntervalHours: config?.cleanupIntervalHours || 24,
    };

    if (this.config.enableAutomaticCleanup) {
      this.startAutomaticCleanup();
    }
  }

  /**
   * Start automatic cleanup scheduler
   */
  startAutomaticCleanup(): void {
    if (this.cleanupTimer) {
      return; // Already started
    }

    const intervalMs = this.config.cleanupIntervalHours * 60 * 60 * 1000;

    this.cleanupTimer = setInterval(async () => {
      await this.enforceRetentionPolicy();
    }, intervalMs);

    // Run cleanup immediately on start
    this.enforceRetentionPolicy();
  }

  /**
   * Stop automatic cleanup scheduler
   */
  stopAutomaticCleanup(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = undefined;
    }
  }

  /**
   * Enforce retention policy (delete old entries)
   */
  async enforceRetentionPolicy(): Promise<CleanupResult> {
    const startTime = Date.now();

    // Clean up Context DNA storage (SQLite)
    const stats = this.storage.getStats();
    const beforeSize = stats.storageBytes;

    const sqliteResult = this.storage.cleanupOldEntries();

    // Clean up Redis sessions
    const redisDeleted = await this.sessionManager.cleanupExpiredSessions();

    // Calculate freed space
    const afterStats = this.storage.getStats();
    const afterSize = afterStats.storageBytes;
    const freedBytes = Math.max(0, beforeSize - afterSize);

    const duration = Date.now() - startTime;

    return {
      deleted: sqliteResult.deleted + redisDeleted,
      freedBytes,
      duration,
      timestamp: new Date(),
    };
  }

  /**
   * Get retention policy configuration
   */
  getConfig(): RetentionPolicyConfig {
    return { ...this.config };
  }

  /**
   * Update retention policy configuration
   */
  updateConfig(config: Partial<RetentionPolicyConfig>): void {
    this.config = {
      ...this.config,
      ...config,
    };

    // Restart cleanup if enabled state changed
    if (config.enableAutomaticCleanup !== undefined) {
      this.stopAutomaticCleanup();
      if (config.enableAutomaticCleanup) {
        this.startAutomaticCleanup();
      }
    }
  }

  /**
   * Close and cleanup resources
   */
  close(): void {
    this.stopAutomaticCleanup();
  }
}

/**
 * Singleton instance
 */
let retentionPolicyEnforcerInstance: RetentionPolicyEnforcer | null = null;

/**
 * Get or create RetentionPolicyEnforcer singleton
 */
export function getRetentionPolicyEnforcer(): RetentionPolicyEnforcer {
  if (!retentionPolicyEnforcerInstance) {
    retentionPolicyEnforcerInstance = new RetentionPolicyEnforcer();
  }
  return retentionPolicyEnforcerInstance;
}
