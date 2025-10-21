/**
 * Pinecone Vector Store
 *
 * Provides semantic search and vector storage for project embeddings.
 * Supports incremental indexing with git diff detection.
 *
 * Features:
 * - Project embedding storage
 * - Semantic similarity search
 * - Metadata filtering
 * - Incremental updates
 * - <200ms search latency target
 */

import { Pinecone } from '@pinecone-database/pinecone';

export interface VectorMetadata {
  projectId: string;
  filePath: string;
  chunkId: string;
  lineStart: number;
  lineEnd: number;
  fileType: string;
  gitHash?: string;
  timestamp: number;
  [key: string]: string | number | boolean | undefined;
}

export interface VectorSearchResult {
  id: string;
  score: number;
  metadata: VectorMetadata;
  text?: string;
}

export interface IndexStats {
  totalVectors: number;
  dimension: number;
  indexFullness: number;
}

export class PineconeVectorStore {
  private client: Pinecone | null = null;
  private indexName: string;
  private dimension: number;

  constructor(config: {
    apiKey?: string;
    indexName?: string;
    dimension?: number;
  } = {}) {
    this.indexName = config.indexName || process.env.PINECONE_INDEX || 'spek-projects';
    this.dimension = config.dimension || 1536; // OpenAI ada-002 dimension
  }

  /**
   * Initialize Pinecone client
   */
  async initialize(): Promise<void> {
    if (this.client) return;

    const apiKey = process.env.PINECONE_API_KEY;
    if (!apiKey) {
      throw new Error('PINECONE_API_KEY environment variable not set');
    }

    this.client = new Pinecone({
      apiKey,
    });

    // Ensure index exists
    await this.ensureIndex();
  }

  /**
   * Ensure index exists, create if needed
   */
  private async ensureIndex(): Promise<void> {
    if (!this.client) throw new Error('Client not initialized');

    try {
      const indexes = await this.client.listIndexes();
      const indexExists = indexes.indexes?.some((idx) => idx.name === this.indexName);

      if (!indexExists) {
        console.log(`Creating Pinecone index: ${this.indexName}`);
        await this.client.createIndex({
          name: this.indexName,
          dimension: this.dimension,
          metric: 'cosine',
          spec: {
            serverless: {
              cloud: 'aws',
              region: 'us-east-1',
            },
          },
        });

        // Wait for index to be ready
        await this.waitForIndexReady();
      }
    } catch (_error) {
      console.error('Error ensuring Pinecone index:', error);
      throw error;
    }
  }

  /**
   * Wait for index to be ready
   */
  private async waitForIndexReady(maxAttempts = 30): Promise<void> {
    if (!this.client) throw new Error('Client not initialized');

    for (let i = 0; i < maxAttempts; i++) {
      const description = await this.client.describeIndex(this.indexName);
      if (description.status?.ready) {
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 2000)); // Wait 2s
    }

    throw new Error('Pinecone index not ready after 60 seconds');
  }

  /**
   * Upsert vectors (insert or update)
   */
  async upsertVectors(
    vectors: Array<{
      id: string;
      values: number[];
      metadata: VectorMetadata;
    }>
  ): Promise<void> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    // Batch upsert (Pinecone limit: 100 vectors per request)
    const batchSize = 100;
    for (let i = 0; i < vectors.length; i += batchSize) {
      const batch = vectors.slice(i, i + batchSize);
      // Cast metadata to any to bypass Pinecone strict typing
      await index.upsert(batch as any);
    }
  }

  /**
   * Delete vectors by IDs
   */
  async deleteVectors(ids: string[]): Promise<void> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    // Batch delete (100 IDs per request)
    const batchSize = 100;
    for (let i = 0; i < ids.length; i += batchSize) {
      const batch = ids.slice(i, i + batchSize);
      await index.deleteMany(batch);
    }
  }

  /**
   * Delete all vectors for a project
   */
  async deleteProject(projectId: string): Promise<void> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    await index.deleteMany({
      filter: {
        projectId: { $eq: projectId },
      },
    });
  }

  /**
   * Semantic search with metadata filtering
   */
  async search(
    queryVector: number[],
    options: {
      topK?: number;
      projectId?: string;
      fileType?: string;
      minScore?: number;
      includeMetadata?: boolean;
    } = {}
  ): Promise<VectorSearchResult[]> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    const filter: Record<string, unknown> = {};
    if (options.projectId) {
      filter.projectId = { $eq: options.projectId };
    }
    if (options.fileType) {
      filter.fileType = { $eq: options.fileType };
    }

    const queryResponse = await index.query({
      vector: queryVector,
      topK: options.topK || 10,
      filter: Object.keys(filter).length > 0 ? filter : undefined,
      includeMetadata: options.includeMetadata !== false,
    });

    const results: VectorSearchResult[] = [];

    for (const match of queryResponse.matches || []) {
      if (options.minScore && match.score! < options.minScore) {
        continue;
      }

      results.push({
        id: match.id,
        score: match.score!,
        metadata: match.metadata as VectorMetadata,
      });
    }

    return results;
  }

  /**
   * Hybrid search: vector + keyword filtering
   */
  async hybridSearch(
    queryVector: number[],
    keywords: string[],
    options: {
      topK?: number;
      projectId?: string;
    } = {}
  ): Promise<VectorSearchResult[]> {
    // First, do vector search
    const vectorResults = await this.search(queryVector, {
      topK: (options.topK || 20) * 2, // Get more results for filtering
      projectId: options.projectId,
    });

    // Filter by keywords in metadata
    const keywordFiltered = vectorResults.filter((result) => {
      const metadataText = JSON.stringify(result.metadata).toLowerCase();
      return keywords.some((keyword) =>
        metadataText.includes(keyword.toLowerCase())
      );
    });

    // Return top K
    return keywordFiltered.slice(0, options.topK || 20);
  }

  /**
   * Get vector by ID
   */
  async getVector(id: string): Promise<{
    id: string;
    values: number[];
    metadata: VectorMetadata;
  } | null> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    const response = await index.fetch([id]);
    const vector = response.records?.[id];

    if (!vector) return null;

    return {
      id: vector.id,
      values: vector.values || [],
      metadata: vector.metadata as VectorMetadata,
    };
  }

  /**
   * Update vector metadata
   */
  async updateMetadata(
    id: string,
    metadata: Partial<VectorMetadata>
  ): Promise<void> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    // Cast to any to bypass Pinecone's strict typing for metadata
    await index.update({
      id,
      metadata: metadata as any,
    });
  }

  /**
   * Get index statistics
   */
  async getIndexStats(): Promise<IndexStats> {
    if (!this.client) await this.initialize();

    const description = await this.client!.describeIndex(this.indexName);
    const stats = await this.client!.index(this.indexName).describeIndexStats();

    return {
      totalVectors: stats.totalRecordCount || 0,
      dimension: description.dimension || this.dimension,
      indexFullness: stats.indexFullness || 0,
    };
  }

  /**
   * List all vectors for a project (paginated)
   */
  async listProjectVectors(
    projectId: string,
    options: {
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<VectorSearchResult[]> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    // Use a dummy vector for listing (we only care about metadata)
    const dummyVector = new Array(this.dimension).fill(0);

    const response = await index.query({
      vector: dummyVector,
      topK: options.limit || 100,
      filter: {
        projectId: { $eq: projectId },
      },
      includeMetadata: true,
    });

    return (
      response.matches?.map((match) => ({
        id: match.id,
        score: match.score!,
        metadata: match.metadata as VectorMetadata,
      })) || []
    );
  }

  /**
   * Count vectors for a project
   */
  async countProjectVectors(projectId: string): Promise<number> {
    if (!this.client) await this.initialize();

    const index = this.client!.index(this.indexName);

    // describeIndexStats doesn't accept filter parameter in latest Pinecone SDK
    // Use query with dummy vector to count matches instead
    const dummyVector = new Array(this.dimension).fill(0);
    const response = await index.query({
      vector: dummyVector,
      topK: 10000, // Max limit to get accurate count
      filter: {
        projectId: { $eq: projectId },
      },
      includeMetadata: false,
    });

    return response.matches?.length || 0;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    latencyMs: number;
    indexReady: boolean;
  }> {
    if (!this.client) {
      return { status: 'unhealthy', latencyMs: -1, indexReady: false };
    }

    const start = performance.now();
    try {
      const description = await this.client.describeIndex(this.indexName);
      const latencyMs = performance.now() - start;

      return {
        status: 'healthy',
        latencyMs,
        indexReady: description.status?.ready || false,
      };
    } catch (_error) {
      return { status: 'unhealthy', latencyMs: -1, indexReady: false };
    }
  }
}

/**
 * Singleton instance
 */
let instance: PineconeVectorStore | null = null;

export function getPineconeVectorStore(): PineconeVectorStore {
  if (!instance) {
    instance = new PineconeVectorStore();
  }
  return instance;
}
