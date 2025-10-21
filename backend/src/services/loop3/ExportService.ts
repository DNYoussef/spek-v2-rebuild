/**
 * Export Service
 * Handles project export to GitHub or ZIP file
 *
 * Week 11 Day 5 Implementation
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import archiver from 'archiver';
import { GitHubIntegrationService } from './GitHubIntegrationService';

export interface ExportOptions {
  method: 'github' | 'zip';
  projectPath: string;

  // GitHub-specific options
  github?: {
    repoName: string;
    visibility: 'public' | 'private';
    description: string;
    license?: string;
  };

  // ZIP-specific options
  zip?: {
    outputPath?: string;
    includeNodeModules?: boolean;
    includeDotFiles?: boolean;
  };
}

export interface ExportResult {
  success: boolean;
  method: 'github' | 'zip';
  output?: string; // GitHub URL or ZIP file path
  size?: number; // File size in bytes (for ZIP)
  error?: string;
  warnings: string[];
}

export class ExportService {
  private githubService: GitHubIntegrationService;

  constructor() {
    this.githubService = new GitHubIntegrationService();
  }

  /**
   * Export project to GitHub or ZIP
   */
  async export(options: ExportOptions): Promise<ExportResult> {
    if (options.method === 'github') {
      return await this.exportToGitHub(options);
    } else {
      return await this.exportToZIP(options);
    }
  }

  /**
   * Export project to GitHub repository
   */
  private async exportToGitHub(options: ExportOptions): Promise<ExportResult> {
    const warnings: string[] = [];

    if (!options.github) {
      return {
        success: false,
        method: 'github',
        error: 'GitHub configuration missing',
        warnings
      };
    }

    try {
      // Step 1: Secret scanning (pre-flight check)
      const secretScan = await this.githubService.scanForSecrets(
        options.projectPath
      );

      if (secretScan.found) {
        return {
          success: false,
          method: 'github',
          error: `Found ${secretScan.secrets.length} secrets in project. Please remove before pushing.`,
          warnings: secretScan.secrets.map(
            s => `${s.type} in ${s.file}:${s.line}`
          )
        };
      }

      // Step 2: Create GitHub repository
      const repoResult = await this.githubService.createRepository(
        options.github
      );

      if (!repoResult.success) {
        return {
          success: false,
          method: 'github',
          error: repoResult.error,
          warnings: [...warnings, ...repoResult.warnings]
        };
      }

      // Step 3: Push to GitHub
      const pushResult = await this.githubService.pushToGitHub(
        options.projectPath,
        repoResult.repoUrl!
      );

      if (!pushResult.success) {
        return {
          success: false,
          method: 'github',
          error: pushResult.error,
          warnings: [...warnings, ...pushResult.warnings]
        };
      }

      return {
        success: true,
        method: 'github',
        output: pushResult.repoUrl,
        warnings: [...warnings, ...pushResult.warnings]
      };
    } catch (error) {
      return {
        success: false,
        method: 'github',
        error: error instanceof Error ? error.message : String(error),
        warnings
      };
    }
  }

  /**
   * Export project to ZIP file
   */
  private async exportToZIP(options: ExportOptions): Promise<ExportResult> {
    const warnings: string[] = [];

    const zipOptions = options.zip || {};
    const outputPath =
      zipOptions.outputPath ||
      path.join('/tmp', `${path.basename(options.projectPath)}.zip`);

    try {
      const size = await this.createZIPArchive(
        options.projectPath,
        outputPath,
        {
          includeNodeModules: zipOptions.includeNodeModules || false,
          includeDotFiles: zipOptions.includeDotFiles || false
        }
      );

      return {
        success: true,
        method: 'zip',
        output: outputPath,
        size,
        warnings
      };
    } catch (error) {
      return {
        success: false,
        method: 'zip',
        error: error instanceof Error ? error.message : String(error),
        warnings
      };
    }
  }

  /**
   * Create ZIP archive of project
   */
  private async createZIPArchive(
    projectPath: string,
    outputPath: string,
    options: {
      includeNodeModules: boolean;
      includeDotFiles: boolean;
    }
  ): Promise<number> {
    return new Promise((resolve, reject) => {
      const output = require('fs').createWriteStream(outputPath);
      const archive = archiver('zip', { zlib: { level: 9 } });

      let finalSize = 0;

      output.on('close', () => {
        finalSize = archive.pointer();
        resolve(finalSize);
      });

      archive.on('error', (err: Error) => {
        reject(err);
      });

      archive.pipe(output);

      // Add files to archive
      archive.glob(
        '**/*',
        {
          cwd: projectPath,
          ignore: this.getIgnorePatterns(options)
        },
        {}
      );

      archive.finalize();
    });
  }

  /**
   * Get ignore patterns for ZIP archive
   */
  private getIgnorePatterns(options: {
    includeNodeModules: boolean;
    includeDotFiles: boolean;
  }): string[] {
    const ignore: string[] = [];

    if (!options.includeNodeModules) {
      ignore.push('**/node_modules/**');
      ignore.push('**/venv/**');
      ignore.push('**/__pycache__/**');
    }

    if (!options.includeDotFiles) {
      ignore.push('**/.*'); // Exclude all dotfiles
      ignore.push('**/.git/**'); // Explicitly exclude .git
    }

    // Always exclude these
    ignore.push('**/.DS_Store');
    ignore.push('**/Thumbs.db');
    ignore.push('**/*.log');

    return ignore;
  }
}
