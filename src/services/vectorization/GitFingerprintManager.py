"""
GitFingerprintManager - Git commit hash fingerprinting for cache invalidation

Uses git commit hash as cache key to detect when project code has changed.
Enables incremental vectorization (only re-index changed files).

Performance Impact:
- Cache hit: <1s (instant retrieval)
- Cache miss: Triggers full/incremental vectorization
- Storage: ~50B per project fingerprint

Week 4 Day 2
Version: 8.0.0
"""

import subprocess
import os
from typing import Optional
from dataclasses import dataclass
import redis.asyncio as aioredis
from pathlib import Path


# ============================================================================
# Types
# ============================================================================

@dataclass
class FingerprintResult:
    """Git fingerprint result."""
    fingerprint: str
    is_git_repo: bool
    branch_name: Optional[str] = None
    commit_message: Optional[str] = None
    commit_timestamp: Optional[int] = None


# ============================================================================
# GitFingerprintManager Class
# ============================================================================

class GitFingerprintManager:
    """
    Manages git commit fingerprints for cache invalidation.

    Uses git commit hash as unique identifier for project state.
    When hash changes, cache is invalidated and vectorization reruns.
    """

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """
        Initialize fingerprint manager.

        Args:
            redis_client: Optional Redis client for caching
        """
        self.redis = redis_client
        self.ttl_seconds = 2592000  # 30 days

    async def get_current_fingerprint(
        self,
        project_path: str
    ) -> FingerprintResult:
        """
        Get current git commit fingerprint for project.

        Returns commit hash as fingerprint, or directory hash if not git repo.

        Args:
            project_path: Absolute path to project directory

        Returns:
            FingerprintResult with fingerprint and metadata
        """
        # Validate path
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")

        # Check if git repository
        is_git_repo = self._is_git_repository(project_path)

        if is_git_repo:
            return await self._get_git_fingerprint(project_path)
        else:
            return await self._get_directory_fingerprint(project_path)

    def _is_git_repository(self, project_path: str) -> bool:
        """Check if directory is a git repository."""
        git_dir = os.path.join(project_path, '.git')
        return os.path.isdir(git_dir)

    async def _get_git_fingerprint(
        self,
        project_path: str
    ) -> FingerprintResult:
        """
        Get git commit hash as fingerprint.

        Runs: git rev-parse HEAD
        """
        try:
            commit_hash = self._get_commit_hash(project_path)
            branch_name = self._get_branch_name(project_path)
            commit_message = self._get_commit_message(project_path)
            commit_timestamp = self._get_commit_timestamp(project_path)

            return FingerprintResult(
                fingerprint=commit_hash,
                is_git_repo=True,
                branch_name=branch_name,
                commit_message=commit_message,
                commit_timestamp=commit_timestamp
            )

        except subprocess.TimeoutExpired:
            raise RuntimeError("Git command timeout (>5s)")
        except Exception as e:
            raise RuntimeError(f"Failed to get git fingerprint: {e}")

    def _get_commit_hash(self, project_path: str) -> str:
        """Get current commit hash."""
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")

        return result.stdout.strip()

    def _get_branch_name(self, project_path: str) -> Optional[str]:
        """Get current branch name."""
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def _get_commit_message(self, project_path: str) -> Optional[str]:
        """Get last commit message."""
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def _get_commit_timestamp(self, project_path: str) -> Optional[int]:
        """Get last commit timestamp."""
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%ct'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        return int(result.stdout.strip()) if result.returncode == 0 else None

    async def _get_directory_fingerprint(
        self,
        project_path: str
    ) -> FingerprintResult:
        """
        Get directory hash as fingerprint (for non-git projects).

        Uses directory mtime + file count as simple fingerprint.
        """
        import hashlib

        try:
            # Get all file paths
            files = list(Path(project_path).rglob('*'))
            file_count = len([f for f in files if f.is_file()])

            # Get directory mtime
            dir_mtime = os.path.getmtime(project_path)

            # Create simple fingerprint
            fingerprint_str = f"{project_path}:{file_count}:{dir_mtime}"
            fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]

            return FingerprintResult(
                fingerprint=fingerprint,
                is_git_repo=False
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get directory fingerprint: {e}")

    async def get_cached_fingerprint(
        self,
        project_id: str
    ) -> Optional[str]:
        """
        Get cached fingerprint from Redis.

        Args:
            project_id: Unique project identifier

        Returns:
            Cached fingerprint or None if not found
        """
        if not self.redis:
            return None

        try:
            key = f"project:{project_id}:fingerprint"
            value = await self.redis.get(key)
            return value.decode('utf-8') if value else None

        except Exception as e:
            print(f"⚠️  Redis get failed: {e}")
            return None

    async def update_fingerprint(
        self,
        project_id: str,
        fingerprint: str
    ) -> bool:
        """
        Update cached fingerprint in Redis.

        Args:
            project_id: Unique project identifier
            fingerprint: Git commit hash or directory hash

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False

        try:
            key = f"project:{project_id}:fingerprint"
            await self.redis.set(key, fingerprint, ex=self.ttl_seconds)
            return True

        except Exception as e:
            print(f"⚠️  Redis set failed: {e}")
            return False

    async def invalidate_fingerprint(
        self,
        project_id: str
    ) -> bool:
        """
        Invalidate cached fingerprint.

        Forces next vectorization to reindex all files.

        Args:
            project_id: Unique project identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False

        try:
            key = f"project:{project_id}:fingerprint"
            await self.redis.delete(key)
            return True

        except Exception as e:
            print(f"⚠️  Redis delete failed: {e}")
            return False


def create_git_fingerprint_manager(
    redis_url: Optional[str] = None
) -> GitFingerprintManager:
    """
    Factory function to create GitFingerprintManager.

    Args:
        redis_url: Optional Redis connection URL

    Returns:
        GitFingerprintManager instance
    """
    redis_client = None
    if redis_url:
        redis_client = aioredis.from_url(redis_url)

    return GitFingerprintManager(redis_client=redis_client)
