"""
DSPy Core Optimizers

Core optimizer modules for agent-to-agent communication optimization.
Each optimizer is trained on specific communication paths.

Week 21 Day 3
Version: 1.0.0
"""

from .queen_to_princess import (
    QueenToPrincessDevOptimizer,
    QueenToPrincessQualityOptimizer,
    QueenToPrincessCoordinationOptimizer
)

__all__ = [
    "QueenToPrincessDevOptimizer",
    "QueenToPrincessQualityOptimizer",
    "QueenToPrincessCoordinationOptimizer"
]
