"""
EnhancedLightweightProtocol - Lightweight Agent Coordination

Fast, direct agent-to-agent coordination protocol with <100ms latency.
No message queue overhead, optional health checks, optional task tracking.

Design Principles:
- Direct task assignment (no A2A library overhead)
- <100ms coordination latency (p95 target)
- <1KB message size (compressed JSON)
- Optional health checks (lightweight, non-intrusive)
- Optional task tracking (opt-in for debugging)
- Zero message loss (with retries)

Version: 8.0.0 (Week 3 Day 2)
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Message types for protocol communication."""
    TASK_ASSIGN = "task_assign"
    TASK_RESULT = "task_result"
    HEALTH_CHECK = "health_check"
    HEALTH_RESPONSE = "health_response"
    STATUS_UPDATE = "status_update"


@dataclass
class ProtocolMessage:
    """Protocol message structure."""
    message_id: str
    message_type: MessageType
    sender_id: str
    receiver_id: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0


@dataclass
class ProtocolConfig:
    """Protocol configuration."""
    max_retries: int = 3
    retry_delay_ms: int = 100  # exponential backoff base
    timeout_ms: int = 5000
    health_check_enabled: bool = False
    health_check_interval_ms: int = 30000  # 30 seconds
    task_tracking_enabled: bool = False
    compression_enabled: bool = True
    latency_p95_target_ms: float = 100.0


@dataclass
class LatencyMetrics:
    """Latency tracking metrics."""
    samples: List[float] = field(default_factory=list)
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    max: float = 0.0
    count: int = 0


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    success_count: int = 0
    success_threshold: int = 2
    last_failure_time: float = 0.0
    timeout_ms: int = 60000  # 1 minute


class EnhancedLightweightProtocol:
    """
    Lightweight agent coordination protocol.

    Provides fast, direct communication between agents with:
    - <100ms coordination latency
    - <1KB message size
    - Zero message loss (with retries)
    - Optional health checks
    - Optional task tracking
    - Circuit breaker pattern
    """

    def __init__(self, config: Optional[ProtocolConfig] = None):
        """
        Initialize protocol with configuration.

        Args:
            config: Protocol configuration (optional, uses defaults)
        """
        self.config = config or ProtocolConfig()
        self.latency_metrics = LatencyMetrics()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.task_registry: Dict[str, Dict[str, Any]] = {}
        self.health_status: Dict[str, bool] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}

        # Register default handlers
        self._register_default_handlers()

    async def send_task(
        self,
        sender_id: str,
        receiver_id: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send task to agent with retry logic.

        Implements <100ms latency target with exponential backoff.

        Args:
            sender_id: Sender agent ID
            receiver_id: Receiver agent ID
            task: Task payload

        Returns:
            Result from receiver

        Raises:
            TimeoutError: If task times out
            RuntimeError: If circuit breaker is open
        """
        start_time = time.time()

        # Check circuit breaker
        if not self._check_circuit_breaker(receiver_id):
            raise RuntimeError(f"Circuit breaker OPEN for {receiver_id}")

        # Create message
        message = ProtocolMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.TASK_ASSIGN,
            sender_id=sender_id,
            receiver_id=receiver_id,
            payload=task
        )

        # Track task if enabled
        if self.config.task_tracking_enabled:
            self._track_task(message)

        # Send with retries
        result = await self._send_with_retry(message)

        # Record latency
        latency_ms = (time.time() - start_time) * 1000
        self._record_latency(latency_ms)

        # Update circuit breaker
        self._record_success(receiver_id)

        return result

    async def send_result(
        self,
        sender_id: str,
        receiver_id: str,
        task_id: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Send task result back to requester.

        Args:
            sender_id: Sender agent ID
            receiver_id: Receiver agent ID
            task_id: Original task ID
            result: Task result payload
        """
        message = ProtocolMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.TASK_RESULT,
            sender_id=sender_id,
            receiver_id=receiver_id,
            payload={"task_id": task_id, "result": result}
        )

        await self._send_message(message)

        # Untrack task if enabled
        if self.config.task_tracking_enabled:
            self._untrack_task(task_id)

    async def health_check(self, agent_id: str) -> bool:
        """
        Perform health check on agent.

        Optional, lightweight check <10ms target.

        Args:
            agent_id: Agent to check

        Returns:
            bool: True if healthy
        """
        if not self.config.health_check_enabled:
            return True

        message = ProtocolMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.HEALTH_CHECK,
            sender_id="protocol",
            receiver_id=agent_id,
            payload={}
        )

        try:
            response = await asyncio.wait_for(
                self._send_message(message),
                timeout=0.01  # 10ms timeout
            )
            healthy = response.get("healthy", False)
            self.health_status[agent_id] = healthy
            return healthy
        except asyncio.TimeoutError:
            self.health_status[agent_id] = False
            return False

    def get_latency_metrics(self) -> LatencyMetrics:
        """
        Get latency metrics (p50, p95, p99).

        Returns:
            LatencyMetrics with percentiles
        """
        if not self.latency_metrics.samples:
            return self.latency_metrics

        samples = sorted(self.latency_metrics.samples)
        count = len(samples)

        self.latency_metrics.count = count
        self.latency_metrics.p50 = samples[int(count * 0.50)]
        self.latency_metrics.p95 = samples[int(count * 0.95)]
        self.latency_metrics.p99 = samples[int(count * 0.99)]
        self.latency_metrics.max = samples[-1]

        return self.latency_metrics

    def serialize_message(self, message: ProtocolMessage) -> bytes:
        """
        Serialize message to bytes with optional compression.

        Target: <1KB message size

        Args:
            message: Message to serialize

        Returns:
            bytes: Serialized message
        """
        data = {
            "message_id": message.message_id,
            "message_type": message.message_type,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "payload": message.payload,
            "timestamp": message.timestamp,
            "retry_count": message.retry_count
        }

        json_bytes = json.dumps(data).encode('utf-8')

        if self.config.compression_enabled and len(json_bytes) > 512:
            import zlib
            return zlib.compress(json_bytes)

        return json_bytes

    def deserialize_message(self, data: bytes) -> ProtocolMessage:
        """
        Deserialize message from bytes.

        Args:
            data: Serialized message

        Returns:
            ProtocolMessage
        """
        # Try decompress
        if self.config.compression_enabled:
            try:
                import zlib
                data = zlib.decompress(data)
            except:
                pass  # Not compressed

        msg_dict = json.loads(data.decode('utf-8'))

        return ProtocolMessage(
            message_id=msg_dict["message_id"],
            message_type=MessageType(msg_dict["message_type"]),
            sender_id=msg_dict["sender_id"],
            receiver_id=msg_dict["receiver_id"],
            payload=msg_dict["payload"],
            timestamp=msg_dict["timestamp"],
            retry_count=msg_dict["retry_count"]
        )

    # Protected helper methods

    async def _send_with_retry(self, message: ProtocolMessage) -> Dict[str, Any]:
        """Send message with exponential backoff retry."""
        for attempt in range(self.config.max_retries):
            try:
                message.retry_count = attempt
                result = await asyncio.wait_for(
                    self._send_message(message),
                    timeout=self.config.timeout_ms / 1000
                )
                return result
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    self._record_failure(message.receiver_id)
                    raise

                # Exponential backoff
                delay = self.config.retry_delay_ms * (2 ** attempt) / 1000
                await asyncio.sleep(delay)
            except Exception as e:
                self._record_failure(message.receiver_id)
                raise

        raise RuntimeError("Max retries exceeded")

    async def _send_message(self, message: ProtocolMessage) -> Dict[str, Any]:
        """
        Send message (to be overridden by transport layer).

        Subclasses implement actual transport (WebSocket, HTTP, etc.)
        """
        # Mock implementation for testing
        return {"status": "received"}

    def _check_circuit_breaker(self, agent_id: str) -> bool:
        """Check if circuit breaker allows request."""
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreaker()

        breaker = self.circuit_breakers[agent_id]

        if breaker.state == CircuitBreakerState.OPEN:
            # Check if timeout expired
            if time.time() - breaker.last_failure_time > breaker.timeout_ms / 1000:
                breaker.state = CircuitBreakerState.HALF_OPEN
                return True
            return False

        return True

    def _record_success(self, agent_id: str) -> None:
        """Record successful request."""
        if agent_id not in self.circuit_breakers:
            return

        breaker = self.circuit_breakers[agent_id]

        if breaker.state == CircuitBreakerState.HALF_OPEN:
            breaker.success_count += 1
            if breaker.success_count >= breaker.success_threshold:
                breaker.state = CircuitBreakerState.CLOSED
                breaker.failure_count = 0
                breaker.success_count = 0

    def _record_failure(self, agent_id: str) -> None:
        """Record failed request."""
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreaker()

        breaker = self.circuit_breakers[agent_id]
        breaker.failure_count += 1
        breaker.last_failure_time = time.time()

        if breaker.failure_count >= breaker.failure_threshold:
            breaker.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPEN for {agent_id}")

    def _record_latency(self, latency_ms: float) -> None:
        """Record latency sample."""
        self.latency_metrics.samples.append(latency_ms)

        # Keep only last 1000 samples
        if len(self.latency_metrics.samples) > 1000:
            self.latency_metrics.samples = self.latency_metrics.samples[-1000:]

    def _track_task(self, message: ProtocolMessage) -> None:
        """Track task for debugging."""
        task_id = message.payload.get("id", message.message_id)
        self.task_registry[task_id] = {
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "start_time": time.time(),
            "status": "pending"
        }

    def _untrack_task(self, task_id: str) -> None:
        """Remove task from tracking."""
        if task_id in self.task_registry:
            del self.task_registry[task_id]

    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        import uuid
        return str(uuid.uuid4())

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        # Handlers will be implemented by subclasses
        pass


# Factory function
def create_protocol(config: Optional[ProtocolConfig] = None) -> EnhancedLightweightProtocol:
    """
    Create protocol instance.

    Args:
        config: Optional configuration

    Returns:
        EnhancedLightweightProtocol instance
    """
    return EnhancedLightweightProtocol(config)
