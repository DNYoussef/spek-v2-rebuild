/**
 * Git Hash Utility
 *
 * Provides git commit hash fingerprinting for cache invalidation.
 * Detects when project state changes to invalidate caches.
 *
 * Features:
 * - Get current git commit hash
 * - Detect uncommitted changes
 * - Generate fingerprint for project state
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { createHash } from 'crypto';

const execAsync = promisify(exec);

export interface GitState {
  commitHash: string;
  hasUncommittedChanges: boolean;
  fingerprint: string;
  branch: string;
}

export class GitHashUtil {
  /**
   * Get current git commit hash
   */
  static async getCommitHash(projectPath: string): Promise<string | null> {
    try {
      const { stdout } = await execAsync('git rev-parse HEAD', {
        cwd: projectPath,
      });
      return stdout.trim();
    } catch (_error) {
      console.error('Failed to get git commit hash:', error);
      return null;
    }
  }

  /**
   * Get current git branch
   */
  static async getBranch(projectPath: string): Promise<string | null> {
    try {
      const { stdout } = await execAsync('git rev-parse --abbrev-ref HEAD', {
        cwd: projectPath,
      });
      return stdout.trim();
    } catch (_error) {
      console.error('Failed to get git branch:', error);
      return null;
    }
  }

  /**
   * Check if there are uncommitted changes
   */
  static async hasUncommittedChanges(projectPath: string): Promise<boolean> {
    try {
      const { stdout } = await execAsync('git status --porcelain', {
        cwd: projectPath,
      });
      return stdout.trim().length > 0;
    } catch (_error) {
      console.error('Failed to check git status:', error);
      return false;
    }
  }

  /**
   * Get list of uncommitted files
   */
  static async getUncommittedFiles(
    projectPath: string
  ): Promise<string[]> {
    try {
      const { stdout } = await execAsync('git status --porcelain', {
        cwd: projectPath,
      });

      return stdout
        .split('\n')
        .filter((line) => line.trim().length > 0)
        .map((line) => line.substring(3).trim());
    } catch (_error) {
      console.error('Failed to get uncommitted files:', error);
      return [];
    }
  }

  /**
   * Get git diff for uncommitted changes
   */
  static async getDiff(projectPath: string): Promise<string | null> {
    try {
      const { stdout } = await execAsync('git diff', {
        cwd: projectPath,
      });
      return stdout;
    } catch (_error) {
      console.error('Failed to get git diff:', error);
      return null;
    }
  }

  /**
   * Generate fingerprint for project state
   * Combines commit hash + uncommitted changes hash
   */
  static async generateFingerprint(
    projectPath: string
  ): Promise<string> {
    const commitHash = await this.getCommitHash(projectPath);
    const hasChanges = await this.hasUncommittedChanges(projectPath);

    if (!commitHash) {
      // No git repo, use timestamp as fingerprint
      return `no-git-${Date.now()}`;
    }

    if (!hasChanges) {
      // No changes, just use commit hash
      return commitHash;
    }

    // Include uncommitted changes in fingerprint
    const diff = await this.getDiff(projectPath);
    const diffHash = createHash('sha256')
      .update(diff || '')
      .digest('hex')
      .substring(0, 8);

    return `${commitHash}-dirty-${diffHash}`;
  }

  /**
   * Get complete git state
   */
  static async getGitState(projectPath: string): Promise<GitState> {
    const commitHash = (await this.getCommitHash(projectPath)) || 'no-git';
    const branch = (await this.getBranch(projectPath)) || 'unknown';
    const hasUncommittedChanges = await this.hasUncommittedChanges(
      projectPath
    );
    const fingerprint = await this.generateFingerprint(projectPath);

    return {
      commitHash,
      hasUncommittedChanges,
      fingerprint,
      branch,
    };
  }

  /**
   * Get changed files between commits
   */
  static async getChangedFiles(
    projectPath: string,
    fromCommit: string,
    toCommit: string = 'HEAD'
  ): Promise<string[]> {
    try {
      const { stdout } = await execAsync(
        `git diff --name-only ${fromCommit} ${toCommit}`,
        { cwd: projectPath }
      );

      return stdout
        .split('\n')
        .filter((line) => line.trim().length > 0)
        .map((line) => line.trim());
    } catch (_error) {
      console.error('Failed to get changed files:', error);
      return [];
    }
  }

  /**
   * Check if git repository exists
   */
  static async isGitRepo(projectPath: string): Promise<boolean> {
    try {
      await execAsync('git rev-parse --git-dir', {
        cwd: projectPath,
      });
      return true;
    } catch (_error) {
      return false;
    }
  }
}
