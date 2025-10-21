"""
DockerSandbox - Secure code execution in isolated Docker containers

Main orchestrator for sandbox execution:
- Create containers with security constraints
- Pre-execution security validation
- Timeout enforcement (30s max)
- Result capture (stdout, stderr, exit code)
- Post-execution validation
- Container cleanup

Week 4 Day 3
Version: 8.0.0
"""

import asyncio
import docker
from docker.models.containers import Container
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time

from .SandboxConfig import (
    SandboxConfig,
    SandboxLanguage,
    create_sandbox_config,
    create_strict_sandbox_config
)
from .SecurityValidator import (
    SecurityValidator,
    SecurityCheckResult,
    create_security_validator
)


# ============================================================================
# Types
# ============================================================================

@dataclass
class ExecutionResult:
    """Result of code execution in sandbox."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    timeout_exceeded: bool
    security_violations: list = None
    container_id: Optional[str] = None


# ============================================================================
# DockerSandbox Class
# ============================================================================

class DockerSandbox:
    """
    Secure code execution sandbox using Docker.

    Security layers:
    1. Pre-execution AST validation (blocks dangerous code)
    2. Docker container isolation (network, filesystem, resources)
    3. Timeout enforcement (kills runaway processes)
    4. Post-execution validation (verifies constraints)

    Usage:
        sandbox = DockerSandbox()
        result = await sandbox.execute_code(
            code="print('hello')",
            language=SandboxLanguage.PYTHON
        )
    """

    def __init__(
        self,
        config: Optional[SandboxConfig] = None,
        validator: Optional[SecurityValidator] = None
    ):
        """
        Initialize Docker sandbox.

        Args:
            config: Sandbox configuration (uses standard_config if None)
            validator: Security validator (creates default if None)
        """
        self.config = config or create_sandbox_config()
        self.validator = validator or create_security_validator()
        self.docker_client = docker.from_env()

        # Metrics
        self.executions_total = 0
        self.executions_failed = 0
        self.executions_timeout = 0
        self.executions_blocked = 0

    async def execute_code(
        self,
        code: str,
        language: Optional[SandboxLanguage] = None
    ) -> ExecutionResult:
        """
        Execute code in secure Docker sandbox.

        Args:
            code: Source code to execute
            language: Programming language (uses config default if None)

        Returns:
            ExecutionResult with stdout, stderr, exit code, timing
        """
        start_time = time.time()
        self.executions_total += 1

        lang = language or self.config.language
        lang_str = lang.value if isinstance(lang, SandboxLanguage) else str(lang)

        # Step 1: Pre-execution security validation
        security_check = await self.validator.validate_pre_execution(
            code=code,
            language=lang_str
        )

        if security_check.blocked:
            return self._create_blocked_result(security_check)

        # Step 2-4: Create, execute, validate
        container = None
        try:
            container = await self._create_container(code, lang)
            result = await self._execute_with_timeout(container)
            await self._post_validate(container, result)
            return result

        except asyncio.TimeoutError:
            return self._create_timeout_result(start_time, container)

        except Exception as e:
            return self._create_error_result(start_time, e)

        finally:
            if container:
                await self._cleanup_container(container)

    def _create_blocked_result(
        self,
        security_check: 'SecurityCheckResult'
    ) -> ExecutionResult:
        """Create result for blocked execution."""
        self.executions_blocked += 1
        return ExecutionResult(
            success=False,
            stdout="",
            stderr="Code blocked by security validator",
            exit_code=-1,
            execution_time_ms=0,
            timeout_exceeded=False,
            security_violations=[
                issue.message for issue in security_check.issues
            ]
        )

    def _create_timeout_result(
        self,
        start_time: float,
        container: Optional[Container]
    ) -> ExecutionResult:
        """Create result for timeout."""
        self.executions_timeout += 1
        return ExecutionResult(
            success=False,
            stdout="",
            stderr="Execution timeout exceeded",
            exit_code=-1,
            execution_time_ms=int((time.time() - start_time) * 1000),
            timeout_exceeded=True,
            container_id=container.id if container else None
        )

    def _create_error_result(
        self,
        start_time: float,
        error: Exception
    ) -> ExecutionResult:
        """Create result for execution error."""
        self.executions_failed += 1
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=f"Execution error: {str(error)}",
            exit_code=-1,
            execution_time_ms=int((time.time() - start_time) * 1000),
            timeout_exceeded=False
        )

    async def _post_validate(
        self,
        container: Container,
        result: ExecutionResult
    ) -> None:
        """Post-execution security validation."""
        container_stats = container.attrs
        post_check = await self.validator.validate_post_execution(
            container_stats
        )

        if post_check.issues:
            result.security_violations = [
                issue.message for issue in post_check.issues
            ]

    async def _create_container(
        self,
        code: str,
        language: SandboxLanguage
    ) -> Container:
        """
        Create Docker container with security constraints.

        Args:
            code: Source code to execute
            language: Programming language

        Returns:
            Docker container (not started yet)
        """
        image = self.config.get_docker_image()

        # Prepare command based on language
        if language == SandboxLanguage.PYTHON:
            command = ["python", "-c", code]
        elif language == SandboxLanguage.TYPESCRIPT:
            command = ["tsx", "-e", code]
        elif language == SandboxLanguage.JAVASCRIPT:
            command = ["node", "-e", code]
        elif language == SandboxLanguage.GO:
            # Go requires file-based execution
            command = ["sh", "-c", f"echo '{code}' > /tmp/main.go && go run /tmp/main.go"]
        else:
            raise ValueError(f"Unsupported language: {language}")

        # Get resource and security configs
        resource_config = self.config.get_resource_config()

        # Create container with security constraints
        container = self.docker_client.containers.create(
            image=image,
            command=command,
            detach=True,
            network_mode='none',  # Network isolation
            read_only=self.config.security.readonly_rootfs,
            user=self.config.security.user,
            mem_limit=resource_config['Memory'],
            cpu_quota=resource_config['CpuQuota'],
            security_opt=['no-new-privileges:true'] if self.config.security.no_new_privileges else [],
            cap_drop=['ALL'] if self.config.security.drop_all_capabilities else [],
            tmpfs={'/tmp': 'size=10M,mode=1777'}  # Small writable tmpfs
        )

        return container

    async def _execute_with_timeout(self, container: Container) -> ExecutionResult:
        """
        Execute container with timeout enforcement.

        Args:
            container: Docker container to execute

        Returns:
            ExecutionResult with stdout, stderr, timing

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
        """
        start_time = time.time()

        # Start container
        container.start()

        # Wait for completion with timeout
        timeout_seconds = self.config.timeouts.execution_timeout_ms / 1000

        try:
            await asyncio.wait_for(
                self._wait_for_container(container),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            # Kill container on timeout
            container.kill()
            raise

        # Get execution results
        exit_code = container.wait()['StatusCode']
        stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

        execution_time_ms = int((time.time() - start_time) * 1000)

        return ExecutionResult(
            success=(exit_code == 0),
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            execution_time_ms=execution_time_ms,
            timeout_exceeded=False,
            container_id=container.id
        )

    async def _wait_for_container(self, container: Container) -> None:
        """
        Async wait for container to complete.

        Args:
            container: Docker container to wait for
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, container.wait)

    async def _cleanup_container(self, container: Container) -> None:
        """
        Clean up container resources.

        Args:
            container: Docker container to remove
        """
        try:
            # Stop if still running
            if container.status == 'running':
                container.stop(timeout=2)

            # Remove container
            container.remove(force=True)

        except Exception as e:
            # Log cleanup errors but don't raise
            print(f"Container cleanup warning: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get sandbox execution metrics.

        Returns:
            Dictionary with execution statistics
        """
        total = max(self.executions_total, 1)  # Avoid division by zero

        return {
            'executions_total': self.executions_total,
            'executions_success': total - self.executions_failed - self.executions_blocked,
            'executions_failed': self.executions_failed,
            'executions_timeout': self.executions_timeout,
            'executions_blocked': self.executions_blocked,
            'success_rate': ((total - self.executions_failed - self.executions_blocked) / total) * 100,
            'block_rate': (self.executions_blocked / total) * 100,
            'timeout_rate': (self.executions_timeout / total) * 100
        }

    async def shutdown(self) -> None:
        """
        Shutdown sandbox and cleanup resources.
        """
        # Close Docker client
        self.docker_client.close()


# ============================================================================
# Factory Functions
# ============================================================================

def create_docker_sandbox(
    strict: bool = False,
    config: Optional[SandboxConfig] = None
) -> DockerSandbox:
    """
    Factory function to create DockerSandbox.

    Args:
        strict: Use strict security config (tighter constraints)
        config: Custom config (overrides strict parameter)

    Returns:
        DockerSandbox instance
    """
    if config is None:
        config = create_strict_sandbox_config() if strict else create_sandbox_config()

    return DockerSandbox(config=config)
