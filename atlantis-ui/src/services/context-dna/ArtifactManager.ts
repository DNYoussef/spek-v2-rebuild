/**
 * Artifact Manager
 *
 * Manages artifact storage with S3 paths (NOT full file content).
 * Provides upload/download utilities for artifact references.
 *
 * Features:
 * - S3 path generation and validation
 * - Local file upload to S3
 * - Artifact metadata tracking
 * - Storage optimization (references only)
 */

import { getContextDNAStorage } from './ContextDNAStorage';
import { ArtifactReference } from './types';
import { join } from 'path';
import { existsSync, statSync } from 'fs';

export interface ArtifactUploadOptions {
  projectId: string;
  taskId?: string;
  type: ArtifactReference['type'];
  name: string;
  localPath?: string;
  url?: string;
  metadata?: Record<string, unknown>;
}

export interface ArtifactStorageConfig {
  s3Bucket?: string;
  s3Region?: string;
  s3Prefix?: string;
  localStoragePath?: string;
}

export class ArtifactManager {
  private config: ArtifactStorageConfig;
  private storage = getContextDNAStorage();

  constructor(config: ArtifactStorageConfig = {}) {
    this.config = {
      s3Bucket: config.s3Bucket || process.env.S3_ARTIFACT_BUCKET,
      s3Region: config.s3Region || process.env.S3_REGION || 'us-east-1',
      s3Prefix: config.s3Prefix || 'artifacts',
      localStoragePath:
        config.localStoragePath || join(process.cwd(), 'data', 'artifacts'),
    };
  }

  /**
   * Register an artifact reference (does NOT upload file)
   */
  registerArtifact(options: ArtifactUploadOptions): ArtifactReference {
    const artifact: ArtifactReference = {
      id: this.generateArtifactId(),
      projectId: options.projectId,
      taskId: options.taskId,
      type: options.type,
      name: options.name,
      createdAt: new Date(),
      metadata: options.metadata,
    };

    // Add S3 path if we have S3 configured
    if (this.config.s3Bucket) {
      artifact.s3Path = this.generateS3Path(artifact);
    }

    // Add local path if provided
    if (options.localPath) {
      artifact.localPath = options.localPath;

      // Get file size if local file exists
      if (existsSync(options.localPath)) {
        const stats = statSync(options.localPath);
        artifact.sizeBytes = stats.size;
      }
    }

    // Add URL if provided
    if (options.url) {
      artifact.url = options.url;
    }

    // Save to Context DNA
    this.storage.saveArtifact(artifact);

    return artifact;
  }

  /**
   * Get artifact by ID
   */
  getArtifact(_artifactId: string): ArtifactReference | null {
    // This would require adding getArtifactById to ContextDNAStorage
    // For now, we'll return null (to be implemented in storage)
    return null;
  }

  /**
   * Get all artifacts for a project
   */
  getProjectArtifacts(projectId: string, limit = 100): ArtifactReference[] {
    return this.storage.getArtifactsForProject(projectId, limit);
  }

  /**
   * Get artifacts by type
   */
  getArtifactsByType(
    projectId: string,
    type: ArtifactReference['type']
  ): ArtifactReference[] {
    const allArtifacts = this.storage.getArtifactsForProject(projectId, 1000);
    return allArtifacts.filter((a) => a.type === type);
  }

  /**
   * Get artifact URL (S3 or local or external)
   */
  getArtifactUrl(artifact: ArtifactReference): string | null {
    // Priority: S3 path > local path > external URL
    if (artifact.s3Path && this.config.s3Bucket) {
      return this.buildS3Url(artifact.s3Path);
    }

    if (artifact.localPath) {
      return `file://${artifact.localPath}`;
    }

    if (artifact.url) {
      return artifact.url;
    }

    return null;
  }

  /**
   * Upload artifact to S3 (placeholder - requires AWS SDK)
   */
  async uploadToS3(
    localPath: string,
    _artifactId: string
  ): Promise<{ s3Path: string; uploadedBytes: number }> {
    // This is a placeholder implementation
    // In production, would use AWS SDK S3 client:
    //
    // const s3 = new S3Client({ region: this.config.s3Region });
    // const fileBuffer = await fs.readFile(localPath);
    // const command = new PutObjectCommand({
    //   Bucket: this.config.s3Bucket,
    //   Key: s3Path,
    //   Body: fileBuffer,
    // });
    // await s3.send(command);

    const stats = existsSync(localPath) ? statSync(localPath) : { size: 0 };

    return {
      s3Path: `s3://${this.config.s3Bucket}/${this.config.s3Prefix}/${artifactId}`,
      uploadedBytes: stats.size,
    };
  }

  /**
   * Download artifact from S3 (placeholder - requires AWS SDK)
   */
  async downloadFromS3(
    _s3Path: string,
    _destinationPath: string
  ): Promise<{ downloadedBytes: number }> {
    // Placeholder implementation
    // In production, would use AWS SDK S3 client:
    //
    // const s3 = new S3Client({ region: this.config.s3Region });
    // const command = new GetObjectCommand({
    //   Bucket: this.config.s3Bucket,
    //   Key: key,
    // });
    // const response = await s3.send(command);
    // await fs.writeFile(destinationPath, response.Body);

    return {
      downloadedBytes: 0,
    };
  }

  /**
   * Delete artifact (removes reference, NOT S3 file)
   */
  deleteArtifactReference(_artifactId: string): boolean {
    // Would require deleteArtifact method in ContextDNAStorage
    // For now, return false (to be implemented)
    return false;
  }

  /**
   * Get storage statistics
   */
  getStorageStats(projectId?: string): {
    totalArtifacts: number;
    totalBytes: number;
    byType: Record<string, { count: number; bytes: number }>;
  } {
    const artifacts = projectId
      ? this.storage.getArtifactsForProject(projectId, 10000)
      : []; // Would need getAllArtifacts() method

    const byType: Record<string, { count: number; bytes: number }> = {};
    let totalBytes = 0;

    for (const artifact of artifacts) {
      const size = artifact.sizeBytes || 0;
      totalBytes += size;

      if (!byType[artifact.type]) {
        byType[artifact.type] = { count: 0, bytes: 0 };
      }

      byType[artifact.type].count++;
      byType[artifact.type].bytes += size;
    }

    return {
      totalArtifacts: artifacts.length,
      totalBytes,
      byType,
    };
  }

  /**
   * Generate unique artifact ID
   */
  private generateArtifactId(): string {
    return `artifact-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  /**
   * Generate S3 path for artifact
   */
  private generateS3Path(artifact: ArtifactReference): string {
    const date = artifact.createdAt.toISOString().split('T')[0];
    const filename = artifact.name.replace(/[^a-zA-Z0-9.-]/g, '_');

    return `${this.config.s3Prefix}/${artifact.projectId}/${date}/${artifact.id}-${filename}`;
  }

  /**
   * Build full S3 URL
   */
  private buildS3Url(s3Path: string): string {
    return `https://${this.config.s3Bucket}.s3.${this.config.s3Region}.amazonaws.com/${s3Path}`;
  }
}

/**
 * Singleton instance
 */
let instance: ArtifactManager | null = null;

export function getArtifactManager(): ArtifactManager {
  if (!instance) {
    instance = new ArtifactManager();
  }
  return instance;
}
