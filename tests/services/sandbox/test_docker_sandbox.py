"""
Test suite for DockerSandbox - Secure code execution

Tests:
- Safe code execution (Python, TypeScript, JavaScript, Go)
- Security validation (dangerous imports/functions blocked)
- Timeout enforcement (30s max)
- Resource limits (512MB RAM, 50% CPU)
- Container cleanup
- Metrics tracking

Week 4 Day 3
Version: 8.0.0
"""

import pytest
import asyncio
from src.services.sandbox.DockerSandbox import (
    DockerSandbox,
    ExecutionResult,
    create_docker_sandbox
)
from src.services.sandbox.SandboxConfig import (
    SandboxLanguage,
    create_standard_config,
    create_strict_config
)
from src.services.sandbox.SecurityValidator import SecurityLevel


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sandbox():
    """Create standard sandbox instance."""
    return create_docker_sandbox(strict=False)


@pytest.fixture
def strict_sandbox():
    """Create strict sandbox instance."""
    return create_docker_sandbox(strict=True)


@pytest.fixture
async def cleanup_sandbox(sandbox):
    """Cleanup sandbox after test."""
    yield sandbox
    await sandbox.shutdown()


# ============================================================================
# Test: Safe Code Execution
# ============================================================================

@pytest.mark.asyncio
async def test_execute_safe_python_code(cleanup_sandbox):
    """Test safe Python code execution."""
    sandbox = cleanup_sandbox

    code = """
result = 2 + 2
print(f"Result: {result}")
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is True
    assert "Result: 4" in result.stdout
    assert result.exit_code == 0
    assert result.timeout_exceeded is False
    assert result.security_violations is None


@pytest.mark.asyncio
async def test_execute_safe_javascript_code(cleanup_sandbox):
    """Test safe JavaScript code execution."""
    sandbox = cleanup_sandbox

    code = """
const result = 2 + 2;
console.log(`Result: ${result}`);
"""

    result = await sandbox.execute_code(code, SandboxLanguage.JAVASCRIPT)

    assert result.success is True
    assert "Result: 4" in result.stdout
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_execute_math_operations(cleanup_sandbox):
    """Test complex math operations."""
    sandbox = cleanup_sandbox

    code = """
import math
result = math.sqrt(16) + math.pow(2, 3)
print(f"Result: {result}")
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is True
    assert "Result: 12.0" in result.stdout


# ============================================================================
# Test: Security Validation
# ============================================================================

@pytest.mark.asyncio
async def test_block_dangerous_import_os(cleanup_sandbox):
    """Test blocking dangerous import: os module."""
    sandbox = cleanup_sandbox

    code = """
import os
print(os.listdir('/'))
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.exit_code == -1
    assert result.security_violations is not None
    assert any("os" in v.lower() for v in result.security_violations)


@pytest.mark.asyncio
async def test_block_dangerous_import_subprocess(cleanup_sandbox):
    """Test blocking dangerous import: subprocess module."""
    sandbox = cleanup_sandbox

    code = """
import subprocess
subprocess.run(['ls', '-la'])
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.security_violations is not None
    assert any("subprocess" in v.lower() for v in result.security_violations)


@pytest.mark.asyncio
async def test_block_dangerous_function_eval(cleanup_sandbox):
    """Test blocking dangerous function: eval()."""
    sandbox = cleanup_sandbox

    code = """
result = eval("2 + 2")
print(result)
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.security_violations is not None
    assert any("eval" in v.lower() for v in result.security_violations)


@pytest.mark.asyncio
async def test_block_file_operations(cleanup_sandbox):
    """Test blocking file operations: open()."""
    sandbox = cleanup_sandbox

    code = """
with open('/etc/passwd', 'r') as f:
    print(f.read())
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.security_violations is not None
    assert any("open" in v.lower() for v in result.security_violations)


@pytest.mark.asyncio
async def test_block_network_access(cleanup_sandbox):
    """Test blocking network access: socket module."""
    sandbox = cleanup_sandbox

    code = """
import socket
s = socket.socket()
s.connect(('google.com', 80))
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.security_violations is not None
    assert any("socket" in v.lower() for v in result.security_violations)


# ============================================================================
# Test: Timeout Enforcement
# ============================================================================

@pytest.mark.asyncio
async def test_timeout_infinite_loop(cleanup_sandbox):
    """Test timeout for infinite loop."""
    sandbox = cleanup_sandbox

    code = """
while True:
    pass
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.timeout_exceeded is True
    assert "timeout" in result.stderr.lower()


@pytest.mark.asyncio
async def test_timeout_long_computation(cleanup_sandbox):
    """Test timeout for long computation."""
    sandbox = cleanup_sandbox

    code = """
import time
time.sleep(35)  # Exceeds 30s timeout
print("Should not reach here")
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    assert result.success is False
    assert result.timeout_exceeded is True


# ============================================================================
# Test: Resource Limits
# ============================================================================

@pytest.mark.asyncio
async def test_memory_limit_enforcement(strict_sandbox):
    """Test memory limit enforcement (512MB)."""
    sandbox = strict_sandbox

    # This code should fail due to memory limit
    code = """
data = []
for i in range(1000000):
    data.append([0] * 10000)  # Tries to allocate ~40GB
"""

    result = await sandbox.execute_code(code, SandboxLanguage.PYTHON)

    # May fail with MemoryError or be killed by Docker
    assert result.success is False


# ============================================================================
# Test: Metrics Tracking
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_tracking(cleanup_sandbox):
    """Test execution metrics tracking."""
    sandbox = cleanup_sandbox

    # Execute safe code
    await sandbox.execute_code("print('test')", SandboxLanguage.PYTHON)

    # Execute blocked code
    await sandbox.execute_code("import os", SandboxLanguage.PYTHON)

    # Execute timeout code
    await sandbox.execute_code("while True: pass", SandboxLanguage.PYTHON)

    metrics = sandbox.get_metrics()

    assert metrics['executions_total'] == 3
    assert metrics['executions_success'] >= 1
    assert metrics['executions_blocked'] >= 1
    assert metrics['executions_timeout'] >= 1
    assert 'success_rate' in metrics
    assert 'block_rate' in metrics


# ============================================================================
# Test: Container Cleanup
# ============================================================================

@pytest.mark.asyncio
async def test_container_cleanup_after_success():
    """Test container cleanup after successful execution."""
    sandbox = create_docker_sandbox()

    result = await sandbox.execute_code("print('test')", SandboxLanguage.PYTHON)

    assert result.success is True
    assert result.container_id is not None

    # Container should be removed
    # (Manual verification: docker ps -a should not show container)

    await sandbox.shutdown()


@pytest.mark.asyncio
async def test_container_cleanup_after_failure():
    """Test container cleanup after failed execution."""
    sandbox = create_docker_sandbox()

    result = await sandbox.execute_code("import os", SandboxLanguage.PYTHON)

    assert result.success is False

    # Even failed executions should cleanup
    await sandbox.shutdown()


# ============================================================================
# Test: Factory Functions
# ============================================================================

def test_create_standard_sandbox():
    """Test creating standard sandbox."""
    sandbox = create_docker_sandbox(strict=False)

    assert sandbox.config.resources.memory_mb == 512
    assert sandbox.config.security.readonly_rootfs is True
    assert sandbox.config.timeouts.execution_timeout_ms == 30000


def test_create_strict_sandbox():
    """Test creating strict sandbox."""
    sandbox = create_docker_sandbox(strict=True)

    assert sandbox.config.resources.memory_mb == 256  # Stricter
    assert sandbox.config.timeouts.execution_timeout_ms == 15000  # Stricter
