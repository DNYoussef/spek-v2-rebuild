"""
Cache Service - Redis-backed caching with smart invalidation

Exports:
- RedisCacheLayer: High-performance Redis caching
- CacheInvalidator: Smart invalidation strategies
- CacheMetrics: Performance tracking
- InvalidationStrategy: Invalidation types

Week 4 Day 4
Version: 8.0.0
"""

from .RedisCacheLayer import (
    RedisCacheLayer,
    CacheEntry,
    CacheMetrics,
    create_cache_layer
)

from .CacheInvalidator import (
    CacheInvalidator,
    InvalidationStrategy,
    InvalidationEvent,
    InvalidationResult,
    create_invalidator
)

__all__ = [
    # Main classes
    'RedisCacheLayer',
    'CacheInvalidator',

    # Types
    'CacheEntry',
    'CacheMetrics',
    'InvalidationStrategy',
    'InvalidationEvent',
    'InvalidationResult',

    # Factory functions
    'create_cache_layer',
    'create_invalidator'
]
