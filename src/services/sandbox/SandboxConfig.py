"""
SandboxConfig - Docker sandbox security configuration

Defines resource limits and security constraints for safe code execution.

Security Constraints:
- Memory: 512MB limit (prevent DoS)
- CPU: 50% quota (prevent resource starvation)
- Network: Isolated (no outbound connections)
- Filesystem: Read-only root (prevent tampering)
- User: Non-root (least privilege)
- Timeout: 30s max (prevent infinite loops)

Week 4 Day 3
Version: 8.0.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


# ============================================================================
# Types
# ============================================================================

class SandboxLanguage(str, Enum):
    """Supported languages for sandbox execution."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"


@dataclass
class ResourceLimits:
    """Resource limit configuration."""
    memory_mb: int = 512          # 512MB RAM limit
    cpu_quota_percent: int = 50   # 50% CPU time
    disk_io_mb: int = 100         # 100MB max disk I/O
    network_enabled: bool = False # Network isolated by default


@dataclass
class SecurityConstraints:
    """Security constraint configuration."""
    readonly_rootfs: bool = True         # Read-only root filesystem
    no_new_privileges: bool = True       # Prevent privilege escalation
    drop_all_capabilities: bool = True   # Drop all Linux capabilities
    user: str = "node"                   # Non-root user (node for Node.js images)
    seccomp_profile: str = "default"     # Seccomp security profile


@dataclass
class TimeoutConfig:
    """Timeout configuration."""
    execution_timeout_seconds: int = 30  # 30s max execution time
    startup_timeout_seconds: int = 10    # 10s max container startup
    cleanup_timeout_seconds: int = 5     # 5s max cleanup time


@dataclass
class SandboxConfig:
    """
    Complete sandbox configuration.

    Provides defense-grade security for arbitrary code execution.
    """
    # Language
    language: SandboxLanguage = SandboxLanguage.PYTHON

    # Resource limits
    resources: ResourceLimits = field(default_factory=ResourceLimits)

    # Security constraints
    security: SecurityConstraints = field(default_factory=SecurityConstraints)

    # Timeouts
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)

    # Docker images
    allowed_images: Dict[SandboxLanguage, str] = field(default_factory=lambda: {
        SandboxLanguage.PYTHON: "python:3.11-alpine",
        SandboxLanguage.TYPESCRIPT: "node:18-alpine",
        SandboxLanguage.JAVASCRIPT: "node:18-alpine",
        SandboxLanguage.GO: "golang:1.21-alpine"
    })

    # Working directory inside container
    workdir: str = "/workspace"

    # Temporary file cleanup
    cleanup_on_exit: bool = True

    def get_docker_image(self) -> str:
        """Get Docker image for configured language."""
        return self.allowed_images.get(
            self.language,
            "python:3.11-alpine"  # Default to Python
        )

    def get_resource_config(self) -> Dict[str, Any]:
        """
        Get Docker resource configuration.

        Returns dict compatible with docker-py HostConfig.
        """
        return {
            'Memory': self.resources.memory_mb * 1024 * 1024,  # Convert to bytes
            'MemorySwap': self.resources.memory_mb * 1024 * 1024,  # No swap
            'CpuQuota': self.resources.cpu_quota_percent * 1000,  # CPU time quota
            'CpuPeriod': 100000,  # 100ms period
            'DiskQuota': self.resources.disk_io_mb * 1024 * 1024  # Disk I/O limit
        }

    def get_security_config(self) -> Dict[str, Any]:
        """
        Get Docker security configuration.

        Returns dict compatible with docker-py container creation.
        """
        config = {
            'User': self.security.user,
            'ReadonlyRootfs': self.security.readonly_rootfs
        }

        # Security options
        security_opts = []
        if self.security.no_new_privileges:
            security_opts.append('no-new-privileges')
        if self.security.seccomp_profile:
            security_opts.append(f'seccomp={self.security.seccomp_profile}')

        if security_opts:
            config['SecurityOpt'] = security_opts

        # Drop capabilities
        if self.security.drop_all_capabilities:
            config['CapDrop'] = ['ALL']

        return config

    def get_network_config(self) -> str:
        """
        Get Docker network mode.

        Returns 'none' for isolated, 'bridge' for enabled.
        """
        return 'bridge' if self.resources.network_enabled else 'none'

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        # Memory validation
        if self.resources.memory_mb < 128:
            errors.append("Memory limit too low (minimum 128MB)")
        if self.resources.memory_mb > 2048:
            errors.append("Memory limit too high (maximum 2GB)")

        # CPU validation
        if self.resources.cpu_quota_percent < 10:
            errors.append("CPU quota too low (minimum 10%)")
        if self.resources.cpu_quota_percent > 100:
            errors.append("CPU quota exceeds 100%")

        # Timeout validation
        if self.timeouts.execution_timeout_seconds < 1:
            errors.append("Execution timeout too low (minimum 1s)")
        if self.timeouts.execution_timeout_seconds > 300:
            errors.append("Execution timeout too high (maximum 300s)")

        # Security validation
        if not self.security.readonly_rootfs:
            errors.append("⚠️  Read-only rootfs disabled (security risk)")

        if not self.security.no_new_privileges:
            errors.append("⚠️  Privilege escalation allowed (security risk)")

        if self.resources.network_enabled:
            errors.append("⚠️  Network enabled (security risk)")

        return errors


def create_sandbox_config(
    language: SandboxLanguage = SandboxLanguage.PYTHON,
    memory_mb: int = 512,
    timeout_seconds: int = 30,
    network_enabled: bool = False
) -> SandboxConfig:
    """
    Factory function to create SandboxConfig.

    Args:
        language: Programming language
        memory_mb: Memory limit in MB
        timeout_seconds: Execution timeout
        network_enabled: Enable network access (NOT RECOMMENDED)

    Returns:
        SandboxConfig instance
    """
    resources = ResourceLimits(
        memory_mb=memory_mb,
        network_enabled=network_enabled
    )

    timeouts = TimeoutConfig(
        execution_timeout_seconds=timeout_seconds
    )

    return SandboxConfig(
        language=language,
        resources=resources,
        timeouts=timeouts
    )


def create_strict_sandbox_config() -> SandboxConfig:
    """
    Create strictest possible sandbox configuration.

    Maximum security, minimum resources.
    """
    resources = ResourceLimits(
        memory_mb=256,  # Minimal
        cpu_quota_percent=25,  # Minimal
        network_enabled=False  # Isolated
    )

    security = SecurityConstraints(
        readonly_rootfs=True,
        no_new_privileges=True,
        drop_all_capabilities=True,
        user="nobody"  # Most restricted user
    )

    timeouts = TimeoutConfig(
        execution_timeout_seconds=10,  # Minimal
        startup_timeout_seconds=5,
        cleanup_timeout_seconds=3
    )

    return SandboxConfig(
        resources=resources,
        security=security,
        timeouts=timeouts
    )
