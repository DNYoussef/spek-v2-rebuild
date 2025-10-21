/**
 * Retention Manager
 *
 * Manages automatic cleanup of old Context DNA entries.
 * Implements 30-day retention policy with configurable cleanup.
 *
 * Features:
 * - Automatic scheduled cleanup
 * - Manual cleanup triggers
 * - Retention policy configuration
 * - Cleanup statistics and reporting
 */

import { getContextDNAStorage } from './ContextDNAStorage';
import { RetentionPolicy } from './types';

export interface RetentionConfig {
  retentionDays: number;
  autoCleanup: boolean;
  cleanupIntervalHours: number;
  cleanupCallback?: (stats: CleanupStats) => void;
}

export interface CleanupStats {
  deletedProjects: number;
  deletedTasks: number;
  deletedConversations: number;
  deletedArtifacts: number;
  deletedMemories: number;
  totalDeleted: number;
  cleanupTimeMs: number;
  freedBytes: number;
}

export class RetentionManager {
  private config: RetentionConfig;
  private cleanupTimer: NodeJS.Timeout | null = null;
  private lastCleanup: Date | null = null;

  constructor(config: Partial<RetentionConfig> = {}) {
    this.config = {
      retentionDays: config.retentionDays || 30,
      autoCleanup: config.autoCleanup !== undefined ? config.autoCleanup : true,
      cleanupIntervalHours: config.cleanupIntervalHours || 24,
      cleanupCallback: config.cleanupCallback,
    };

    if (this.config.autoCleanup) {
      this.startAutoCleanup();
    }
  }

  /**
   * Start automatic cleanup on schedule
   */
  startAutoCleanup(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }

    const intervalMs = this.config.cleanupIntervalHours * 60 * 60 * 1000;

    this.cleanupTimer = setInterval(() => {
      this.performCleanup().catch((error) => {
        console.error('Automatic cleanup failed:', error);
      });
    }, intervalMs);

    // Run initial cleanup
    this.performCleanup().catch((error) => {
      console.error('Initial cleanup failed:', error);
    });
  }

  /**
   * Stop automatic cleanup
   */
  stopAutoCleanup(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
  }

  /**
   * Manually trigger cleanup
   */
  async performCleanup(): Promise<CleanupStats> {
    const startTime = performance.now();
    const storage = getContextDNAStorage();

    // Get storage size before cleanup
    const statsBefore = storage.getStats();
    const bytesBefore = statsBefore.storageBytes;

    // Perform cleanup
    const result = storage.cleanupOldEntries();

    // Get storage size after cleanup
    const statsAfter = storage.getStats();
    const bytesAfter = statsAfter.storageBytes;

    const cleanupTimeMs = performance.now() - startTime;
    const freedBytes = bytesBefore - bytesAfter;

    const stats: CleanupStats = {
      deletedProjects: 0, // Storage doesn't track per-table deletes
      deletedTasks: 0,
      deletedConversations: 0,
      deletedArtifacts: 0,
      deletedMemories: 0,
      totalDeleted: result.deleted,
      cleanupTimeMs,
      freedBytes,
    };

    this.lastCleanup = new Date();

    // Call callback if provided
    if (this.config.cleanupCallback) {
      this.config.cleanupCallback(stats);
    }

    return stats;
  }

  /**
   * Get retention policy information
   */
  getRetentionPolicy(): RetentionPolicy {
    const deleteAfter = new Date();
    deleteAfter.setDate(deleteAfter.getDate() - this.config.retentionDays);

    return {
      retentionDays: this.config.retentionDays,
      deleteAfter,
    };
  }

  /**
   * Get cleanup statistics
   */
  getCleanupInfo(): {
    lastCleanup: Date | null;
    nextCleanup: Date | null;
    retentionPolicy: RetentionPolicy;
  } {
    const nextCleanup = this.lastCleanup
      ? new Date(
          this.lastCleanup.getTime() +
            this.config.cleanupIntervalHours * 60 * 60 * 1000
        )
      : null;

    return {
      lastCleanup: this.lastCleanup,
      nextCleanup,
      retentionPolicy: this.getRetentionPolicy(),
    };
  }

  /**
   * Update retention configuration
   */
  updateConfig(config: Partial<RetentionConfig>): void {
    const oldAutoCleanup = this.config.autoCleanup;

    this.config = {
      ...this.config,
      ...config,
    };

    // Restart auto cleanup if settings changed
    if (oldAutoCleanup !== this.config.autoCleanup) {
      if (this.config.autoCleanup) {
        this.startAutoCleanup();
      } else {
        this.stopAutoCleanup();
      }
    }
  }

  /**
   * Test retention policy with mock data
   */
  async testRetentionPolicy(daysOld: number): Promise<{
    shouldDelete: boolean;
    age: number;
    policy: RetentionPolicy;
  }> {
    const policy = this.getRetentionPolicy();
    const testDate = new Date();
    testDate.setDate(testDate.getDate() - daysOld);

    const shouldDelete = testDate < policy.deleteAfter;
    const age = daysOld;

    return {
      shouldDelete,
      age,
      policy,
    };
  }

  /**
   * Cleanup and stop manager
   */
  shutdown(): void {
    this.stopAutoCleanup();
  }
}

/**
 * Singleton instance
 */
let instance: RetentionManager | null = null;

export function getRetentionManager(): RetentionManager {
  if (!instance) {
    instance = new RetentionManager();
  }
  return instance;
}
