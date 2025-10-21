"""
SPEK Platform Protocols Module

Provides communication protocols for agent coordination:
- EnhancedLightweightProtocol: Fast, direct agent-to-agent coordination

Version: 8.0.0 (Week 3 Day 2)
"""

from .EnhancedLightweightProtocol import (
    EnhancedLightweightProtocol,
    ProtocolConfig,
    ProtocolMessage,
    MessageType,
    LatencyMetrics,
    CircuitBreaker,
    CircuitBreakerState,
    create_protocol,
)

__version__ = "8.0.0"
__all__ = [
    "EnhancedLightweightProtocol",
    "ProtocolConfig",
    "ProtocolMessage",
    "MessageType",
    "LatencyMetrics",
    "CircuitBreaker",
    "CircuitBreakerState",
    "create_protocol",
]
