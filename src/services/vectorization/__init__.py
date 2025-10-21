"""
Vectorization Service Module

Provides incremental vector indexing with git diff optimization.

Week 4 Day 2
Version: 8.0.0
"""

from .IncrementalIndexer import (
    IncrementalIndexer,
    create_incremental_indexer,
    VectorizationResult,
    ChangedFiles
)

from .ParallelEmbedder import (
    ParallelEmbedder,
    create_parallel_embedder,
    EmbeddingResult,
    BatchEmbeddingResult,
    ProgressUpdate
)

from .GitFingerprintManager import (
    GitFingerprintManager,
    create_git_fingerprint_manager,
    FingerprintResult
)

__all__ = [
    'IncrementalIndexer',
    'create_incremental_indexer',
    'VectorizationResult',
    'ChangedFiles',
    'ParallelEmbedder',
    'create_parallel_embedder',
    'EmbeddingResult',
    'BatchEmbeddingResult',
    'ProgressUpdate',
    'GitFingerprintManager',
    'create_git_fingerprint_manager',
    'FingerprintResult',
]
