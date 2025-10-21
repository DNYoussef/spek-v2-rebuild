/**
 * Redis Cache Manager
 *
 * Provides caching layer for project metadata, vectorization,
 * and git commit hash fingerprinting.
 *
 * Features:
 * - Git hash-based cache invalidation
 * - 30-day TTL for project metadata
 * - Vector embedding caching
 * - >80% cache hit rate target
 */

import { createClient, RedisClientType } from 'redis';

export interface CacheConfig {
  url?: string;
  ttlSeconds?: number;
  keyPrefix?: string;
}

export interface ProjectCacheEntry {
  projectId: string;
  gitHash: string;
  metadata: Record<string, unknown>;
  vectorized: boolean;
  cachedAt: Date;
}

export interface VectorCacheEntry {
  chunkId: string;
  embedding: number[];
  text: string;
  metadata: Record<string, unknown>;
}

export class RedisCacheManager {
  private client: RedisClientType | null = null;
  private config: CacheConfig;
  private connected: boolean = false;

  constructor(config: CacheConfig = {}) {
    this.config = {
      url: config.url || process.env.REDIS_URL || 'redis://localhost:6379',
      ttlSeconds: config.ttlSeconds || 30 * 24 * 60 * 60, // 30 days
      keyPrefix: config.keyPrefix || 'spek:',
    };
  }

  /**
   * Connect to Redis
   */
  async connect(): Promise<void> {
    if (this.connected) return;

    this.client = createClient({
      url: this.config.url,
    });

    this.client.on('error', (err) => {
      console.error('Redis Client Error:', err);
    });

    await this.client.connect();
    this.connected = true;
  }

  /**
   * Disconnect from Redis
   */
  async disconnect(): Promise<void> {
    if (this.client && this.connected) {
      await this.client.quit();
      this.connected = false;
    }
  }

  /**
   * Generate cache key with prefix
   */
  private key(suffix: string): string {
    return `${this.config.keyPrefix}${suffix}`;
  }

  /**
   * Get git commit hash for project
   */
  async getGitHash(projectPath: string): Promise<string | null> {
    if (!this.client) await this.connect();

    const key = this.key(`git:hash:${projectPath}`);
    return await this.client!.get(key);
  }

  /**
   * Set git commit hash for project
   */
  async setGitHash(
    projectPath: string,
    gitHash: string,
    ttl?: number
  ): Promise<void> {
    if (!this.client) await this.connect();

    const key = this.key(`git:hash:${projectPath}`);
    const ttlSeconds = ttl || this.config.ttlSeconds!;

    await this.client!.set(key, gitHash, {
      EX: ttlSeconds,
    });
  }

  /**
   * Get project metadata cache
   */
  async getProjectMetadata(
    projectId: string
  ): Promise<ProjectCacheEntry | null> {
    if (!this.client) await this.connect();

    const key = this.key(`project:${projectId}`);
    const data = await this.client!.get(key);

    if (!data) return null;

    const entry = JSON.parse(data);
    entry.cachedAt = new Date(entry.cachedAt);
    return entry;
  }

  /**
   * Set project metadata cache
   */
  async setProjectMetadata(
    projectId: string,
    entry: Omit<ProjectCacheEntry, 'cachedAt'>
  ): Promise<void> {
    if (!this.client) await this.connect();

    const key = this.key(`project:${projectId}`);
    const cacheEntry: ProjectCacheEntry = {
      ...entry,
      cachedAt: new Date(),
    };

    await this.client!.set(key, JSON.stringify(cacheEntry), {
      EX: this.config.ttlSeconds!,
    });
  }

  /**
   * Invalidate project cache by git hash change
   */
  async invalidateProjectIfHashChanged(
    projectId: string,
    projectPath: string,
    currentGitHash: string
  ): Promise<boolean> {
    if (!this.client) await this.connect();

    const cachedHash = await this.getGitHash(projectPath);

    if (cachedHash && cachedHash !== currentGitHash) {
      // Hash changed, invalidate cache
      const projectKey = this.key(`project:${projectId}`);
      const vectorKey = this.key(`vectors:${projectId}:*`);

      await this.client!.del(projectKey);
      // Delete all vector keys for this project
      const keys = await this.client!.keys(this.key(`vectors:${projectId}:*`));
      if (keys.length > 0) {
        await this.client!.del(keys);
      }

      // Update git hash
      await this.setGitHash(projectPath, currentGitHash);

      return true; // Cache invalidated
    }

    // No change or first time
    if (!cachedHash) {
      await this.setGitHash(projectPath, currentGitHash);
    }

    return false; // Cache still valid
  }

  /**
   * Get vector embedding from cache
   */
  async getVectorEmbedding(
    projectId: string,
    chunkId: string
  ): Promise<VectorCacheEntry | null> {
    if (!this.client) await this.connect();

    const key = this.key(`vectors:${projectId}:${chunkId}`);
    const data = await this.client!.get(key);

    if (!data) return null;

    return JSON.parse(data);
  }

  /**
   * Set vector embedding in cache
   */
  async setVectorEmbedding(
    projectId: string,
    chunkId: string,
    entry: VectorCacheEntry
  ): Promise<void> {
    if (!this.client) await this.connect();

    const key = this.key(`vectors:${projectId}:${chunkId}`);

    await this.client!.set(key, JSON.stringify(entry), {
      EX: this.config.ttlSeconds!,
    });
  }

  /**
   * Get multiple vector embeddings (batch)
   */
  async getVectorEmbeddingsBatch(
    projectId: string,
    chunkIds: string[]
  ): Promise<Map<string, VectorCacheEntry>> {
    if (!this.client) await this.connect();

    const results = new Map<string, VectorCacheEntry>();

    // Use pipeline for batch GET
    const pipeline = this.client!.multi();

    for (const chunkId of chunkIds) {
      const key = this.key(`vectors:${projectId}:${chunkId}`);
      pipeline.get(key);
    }

    const responses = await pipeline.exec();

    for (let i = 0; i < chunkIds.length; i++) {
      const data = responses?.[i];
      if (data && typeof data === 'string') {
        results.set(chunkIds[i], JSON.parse(data));
      }
    }

    return results;
  }

  /**
   * Set multiple vector embeddings (batch)
   */
  async setVectorEmbeddingsBatch(
    projectId: string,
    entries: Map<string, VectorCacheEntry>
  ): Promise<void> {
    if (!this.client) await this.connect();

    const pipeline = this.client!.multi();

    for (const [chunkId, entry] of entries.entries()) {
      const key = this.key(`vectors:${projectId}:${chunkId}`);
      pipeline.set(key, JSON.stringify(entry), {
        EX: this.config.ttlSeconds!,
      });
    }

    await pipeline.exec();
  }

  /**
   * Get cache statistics
   */
  async getCacheStats(): Promise<{
    totalKeys: number;
    projectKeys: number;
    vectorKeys: number;
    gitHashKeys: number;
    memoryUsed: string;
  }> {
    if (!this.client) await this.connect();

    const allKeys = await this.client!.keys(this.key('*'));
    const projectKeys = await this.client!.keys(this.key('project:*'));
    const vectorKeys = await this.client!.keys(this.key('vectors:*'));
    const gitHashKeys = await this.client!.keys(this.key('git:hash:*'));

    const info = await this.client!.info('memory');
    const memoryMatch = info.match(/used_memory_human:(.+)/);
    const memoryUsed = memoryMatch ? memoryMatch[1].trim() : 'unknown';

    return {
      totalKeys: allKeys.length,
      projectKeys: projectKeys.length,
      vectorKeys: vectorKeys.length,
      gitHashKeys: gitHashKeys.length,
      memoryUsed,
    };
  }

  /**
   * Calculate cache hit rate
   */
  async calculateHitRate(
    hits: number,
    misses: number
  ): Promise<{ hitRate: number; totalRequests: number }> {
    const totalRequests = hits + misses;
    const hitRate = totalRequests > 0 ? (hits / totalRequests) * 100 : 0;

    return { hitRate, totalRequests };
  }

  /**
   * Clear all cache (use with caution)
   */
  async clearAll(): Promise<number> {
    if (!this.client) await this.connect();

    const keys = await this.client!.keys(this.key('*'));
    if (keys.length === 0) return 0;

    await this.client!.del(keys);
    return keys.length;
  }

  /**
   * Clear project-specific cache
   */
  async clearProject(projectId: string): Promise<number> {
    if (!this.client) await this.connect();

    const projectKey = this.key(`project:${projectId}`);
    const vectorKeys = await this.client!.keys(
      this.key(`vectors:${projectId}:*`)
    );

    const keysToDelete = [projectKey, ...vectorKeys];
    if (keysToDelete.length === 0) return 0;

    await this.client!.del(keysToDelete);
    return keysToDelete.length;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; latencyMs: number }> {
    if (!this.client) {
      return { status: 'unhealthy', latencyMs: -1 };
    }

    const start = performance.now();
    try {
      await this.client.ping();
      const latencyMs = performance.now() - start;
      return { status: 'healthy', latencyMs };
    } catch (_error) {
      return { status: 'unhealthy', latencyMs: -1 };
    }
  }
}

/**
 * Singleton instance
 */
let instance: RedisCacheManager | null = null;

export function getRedisCacheManager(): RedisCacheManager {
  if (!instance) {
    instance = new RedisCacheManager();
  }
  return instance;
}
