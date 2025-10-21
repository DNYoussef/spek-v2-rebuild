"""
Unit Tests - EnhancedLightweightProtocol

Tests for EnhancedLightweightProtocol covering:
- Message serialization (<1KB target)
- Latency measurement (<100ms target)
- Retry logic (exponential backoff)
- Circuit breaker pattern
- Health checks (optional)
- Task tracking (optional)

Target: 20 tests
Version: 8.0.0 (Week 3 Day 2-3)
"""

import pytest
import time
import asyncio
from src.protocols.EnhancedLightweightProtocol import (
    EnhancedLightweightProtocol,
    ProtocolConfig,
    ProtocolMessage,
    MessageType,
    CircuitBreakerState,
    create_protocol,
)


@pytest.fixture
def default_protocol():
    """Create protocol with default config."""
    return EnhancedLightweightProtocol()


@pytest.fixture
def custom_config():
    """Create custom protocol configuration."""
    return ProtocolConfig(
        max_retries=2,
        retry_delay_ms=50,
        timeout_ms=1000,
        health_check_enabled=True,
        task_tracking_enabled=True,
        compression_enabled=True
    )


@pytest.fixture
def protocol_with_tracking(custom_config):
    """Create protocol with task tracking enabled."""
    return EnhancedLightweightProtocol(custom_config)


class TestProtocolInitialization:
    """Test protocol initialization and configuration."""

    def test_protocol_initialization_default(self, default_protocol):
        """Test protocol initializes with default config."""
        assert default_protocol.config is not None
        assert default_protocol.config.max_retries == 3
        assert default_protocol.config.timeout_ms == 5000

    def test_protocol_initialization_custom(self, custom_config):
        """Test protocol initializes with custom config."""
        protocol = EnhancedLightweightProtocol(custom_config)
        assert protocol.config.max_retries == 2
        assert protocol.config.retry_delay_ms == 50

    def test_factory_function(self):
        """Test create_protocol factory function."""
        protocol = create_protocol()
        assert isinstance(protocol, EnhancedLightweightProtocol)


class TestMessageSerialization:
    """Test message serialization and deserialization."""

    def test_serialize_message(self, default_protocol):
        """Test message serialization to bytes."""
        message = ProtocolMessage(
            message_id="msg-001",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="agent-a",
            receiver_id="agent-b",
            payload={"task": "test"}
        )

        serialized = default_protocol.serialize_message(message)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

    def test_deserialize_message(self, default_protocol):
        """Test message deserialization from bytes."""
        message = ProtocolMessage(
            message_id="msg-002",
            message_type=MessageType.TASK_RESULT,
            sender_id="agent-c",
            receiver_id="agent-d",
            payload={"result": "success"}
        )

        serialized = default_protocol.serialize_message(message)
        deserialized = default_protocol.deserialize_message(serialized)

        assert deserialized.message_id == message.message_id
        assert deserialized.message_type == message.message_type
        assert deserialized.sender_id == message.sender_id
        assert deserialized.receiver_id == message.receiver_id

    def test_message_size_under_1kb(self, default_protocol):
        """Test message size is <1KB."""
        message = ProtocolMessage(
            message_id="msg-003",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="agent-e",
            receiver_id="agent-f",
            payload={"data": "x" * 100}  # 100 bytes payload
        )

        serialized = default_protocol.serialize_message(message)
        assert len(serialized) < 1024  # <1KB

    def test_compression_enabled(self):
        """Test compression for large messages."""
        config = ProtocolConfig(compression_enabled=True)
        protocol = EnhancedLightweightProtocol(config)

        # Large payload
        message = ProtocolMessage(
            message_id="msg-004",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="agent-g",
            receiver_id="agent-h",
            payload={"data": "x" * 1000}  # 1000 bytes
        )

        serialized = protocol.serialize_message(message)
        # Compressed should be smaller than raw JSON
        assert len(serialized) < len(message.payload["data"])


class TestLatencyTracking:
    """Test latency measurement and metrics."""

    def test_record_latency(self, default_protocol):
        """Test latency recording."""
        default_protocol._record_latency(50.0)
        default_protocol._record_latency(75.0)
        default_protocol._record_latency(100.0)

        assert len(default_protocol.latency_metrics.samples) == 3

    def test_get_latency_metrics(self, default_protocol):
        """Test latency metrics calculation."""
        # Record samples
        for i in range(100):
            default_protocol._record_latency(float(i))

        metrics = default_protocol.get_latency_metrics()

        assert metrics.count == 100
        assert metrics.p50 >= 0
        assert metrics.p95 >= metrics.p50
        assert metrics.p99 >= metrics.p95
        assert metrics.max == 99.0

    def test_latency_samples_limited_to_1000(self, default_protocol):
        """Test latency samples limited to last 1000."""
        # Record 1500 samples
        for i in range(1500):
            default_protocol._record_latency(float(i))

        assert len(default_protocol.latency_metrics.samples) == 1000


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_breaker_initial_state(self, default_protocol):
        """Test circuit breaker starts in CLOSED state."""
        assert default_protocol._check_circuit_breaker("agent-x") is True

    def test_circuit_breaker_opens_on_failures(self, default_protocol):
        """Test circuit breaker opens after threshold failures."""
        agent_id = "agent-y"

        # Record 5 failures (threshold)
        for _ in range(5):
            default_protocol._record_failure(agent_id)

        breaker = default_protocol.circuit_breakers[agent_id]
        assert breaker.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_blocks_requests_when_open(self, default_protocol):
        """Test circuit breaker blocks requests when OPEN."""
        agent_id = "agent-z"

        # Open circuit breaker
        for _ in range(5):
            default_protocol._record_failure(agent_id)

        assert default_protocol._check_circuit_breaker(agent_id) is False

    def test_circuit_breaker_half_open_after_timeout(self, default_protocol):
        """Test circuit breaker enters HALF_OPEN after timeout."""
        agent_id = "agent-recovery"

        # Open circuit breaker
        for _ in range(5):
            default_protocol._record_failure(agent_id)

        breaker = default_protocol.circuit_breakers[agent_id]
        assert breaker.state == CircuitBreakerState.OPEN

        # Simulate timeout passage (set last_failure_time in past)
        breaker.last_failure_time = time.time() - 61  # 61 seconds ago

        # Should allow request (HALF_OPEN)
        assert default_protocol._check_circuit_breaker(agent_id) is True
        assert breaker.state == CircuitBreakerState.HALF_OPEN

    def test_circuit_breaker_closes_after_success(self, default_protocol):
        """Test circuit breaker closes after successful recovery."""
        agent_id = "agent-recover"

        # Open circuit breaker
        for _ in range(5):
            default_protocol._record_failure(agent_id)

        # Trigger HALF_OPEN
        breaker = default_protocol.circuit_breakers[agent_id]
        breaker.last_failure_time = time.time() - 61
        default_protocol._check_circuit_breaker(agent_id)

        # Record successes to close
        default_protocol._record_success(agent_id)
        default_protocol._record_success(agent_id)

        assert breaker.state == CircuitBreakerState.CLOSED


class TestTaskTracking:
    """Test task tracking functionality."""

    def test_track_task(self, protocol_with_tracking):
        """Test task tracking when enabled."""
        message = ProtocolMessage(
            message_id="msg-track-001",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="agent-sender",
            receiver_id="agent-receiver",
            payload={"id": "task-001"}
        )

        protocol_with_tracking._track_task(message)

        assert "task-001" in protocol_with_tracking.task_registry
        assert protocol_with_tracking.task_registry["task-001"]["status"] == "pending"

    def test_untrack_task(self, protocol_with_tracking):
        """Test task untracking."""
        message = ProtocolMessage(
            message_id="msg-track-002",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="agent-sender",
            receiver_id="agent-receiver",
            payload={"id": "task-002"}
        )

        protocol_with_tracking._track_task(message)
        assert "task-002" in protocol_with_tracking.task_registry

        protocol_with_tracking._untrack_task("task-002")
        assert "task-002" not in protocol_with_tracking.task_registry


class TestHealthCheck:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_disabled_by_default(self, default_protocol):
        """Test health check disabled returns True."""
        healthy = await default_protocol.health_check("agent-health")
        assert healthy is True

    @pytest.mark.asyncio
    async def test_health_check_enabled(self, protocol_with_tracking):
        """Test health check when enabled."""
        # This will timeout in mock implementation
        healthy = await protocol_with_tracking.health_check("agent-check")
        # Mock implementation times out
        assert healthy is False


class TestAsyncOperations:
    """Test async send operations."""

    @pytest.mark.asyncio
    async def test_send_task_creates_message(self, default_protocol):
        """Test send_task creates proper message."""
        task = {"id": "task-async-001", "type": "test"}

        # Override _send_message to capture
        async def mock_send(msg):
            assert msg.message_type == MessageType.TASK_ASSIGN
            assert msg.payload == task
            return {"status": "ok"}

        default_protocol._send_message = mock_send

        result = await default_protocol.send_task("agent-a", "agent-b", task)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_send_result_creates_message(self, default_protocol):
        """Test send_result creates proper message."""
        result_data = {"success": True}

        # Override _send_message
        async def mock_send(msg):
            assert msg.message_type == MessageType.TASK_RESULT
            return None

        default_protocol._send_message = mock_send

        await default_protocol.send_result("agent-c", "agent-d", "task-001", result_data)


class TestErrorHandling:
    """Test error handling and retries."""

    @pytest.mark.asyncio
    async def test_send_with_retry_on_timeout(self, default_protocol):
        """Test retry logic on timeout."""
        call_count = 0

        async def failing_send(msg):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise asyncio.TimeoutError()
            return {"status": "ok"}

        default_protocol._send_message = failing_send

        message = ProtocolMessage(
            message_id="msg-retry",
            message_type=MessageType.TASK_ASSIGN,
            sender_id="a",
            receiver_id="b",
            payload={}
        )

        result = await default_protocol._send_with_retry(message)
        assert call_count == 2  # Failed once, succeeded on retry
        assert result["status"] == "ok"
