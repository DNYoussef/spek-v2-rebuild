"""
ParallelEmbedder - Parallel batch embedding with OpenAI

Optimizes embedding generation through:
- Batch size 64 (OpenAI-optimized)
- 10 parallel tasks
- Progress streaming with ETA

Performance Target: 10K files in <60s (10x speedup from baseline)

Week 4 Day 2
Version: 8.0.0
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import time
from pathlib import Path
from openai import AsyncOpenAI
import tiktoken


# ============================================================================
# Types
# ============================================================================

@dataclass
class EmbeddingResult:
    """Single file embedding result."""
    file_path: str
    embedding: List[float]
    token_count: int
    embedding_time: float  # seconds


@dataclass
class BatchEmbeddingResult:
    """Batch embedding result."""
    results: List[EmbeddingResult]
    total_files: int
    total_tokens: int
    total_time: float  # seconds
    files_per_second: float


@dataclass
class ProgressUpdate:
    """Progress update for streaming."""
    processed: int
    total: int
    percentage: float
    eta_seconds: float
    current_file: Optional[str] = None


# ============================================================================
# ParallelEmbedder Class
# ============================================================================

class ParallelEmbedder:
    """
    Parallel batch embedder for high-performance vectorization.

    Optimizations:
    - Batch size 64 (OpenAI rate limit optimized)
    - 10 parallel tasks (network I/O concurrent)
    - Token estimation for accurate cost tracking
    - Progress streaming for UI updates
    """

    def __init__(
        self,
        api_key: str,
        batch_size: int = 64,
        parallel_tasks: int = 10,
        model: str = "text-embedding-3-small"
    ):
        """
        Initialize parallel embedder.

        Args:
            api_key: OpenAI API key
            batch_size: Files per batch (default 64, OpenAI optimized)
            parallel_tasks: Concurrent batches (default 10)
            model: OpenAI embedding model
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.batch_size = batch_size
        self.parallel_tasks = parallel_tasks
        self.model = model

        # Token counting
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoding = None

        # Progress callback
        self.progress_callback: Optional[Callable[[ProgressUpdate], None]] = None

    async def embed_files(
        self,
        file_contents: Dict[str, str]
    ) -> BatchEmbeddingResult:
        """
        Embed multiple files in parallel batches.

        Args:
            file_contents: Dict mapping file_path -> file_content

        Returns:
            BatchEmbeddingResult with all embeddings
        """
        start_time = time.time()
        files = list(file_contents.items())
        total_files = len(files)
        batches = self._create_batches(files)

        # Process batches in parallel with progress tracking
        all_results = await self._process_batches_parallel(
            batches,
            total_files,
            start_time
        )

        # Calculate final metrics
        total_time = time.time() - start_time
        total_tokens = sum(r.token_count for r in all_results)
        files_per_second = total_files / total_time if total_time > 0 else 0

        return BatchEmbeddingResult(
            results=all_results,
            total_files=total_files,
            total_tokens=total_tokens,
            total_time=total_time,
            files_per_second=files_per_second
        )

    async def _process_batches_parallel(
        self,
        batches: List[List[tuple[str, str]]],
        total_files: int,
        start_time: float
    ) -> List[EmbeddingResult]:
        """
        Process batches in parallel with progress tracking.

        Args:
            batches: List of file batches
            total_files: Total number of files
            start_time: Operation start time

        Returns:
            List of all embedding results
        """
        all_results: List[EmbeddingResult] = []
        processed = 0
        semaphore = asyncio.Semaphore(self.parallel_tasks)

        async def process_batch_with_limit(batch):
            async with semaphore:
                return await self._process_batch(batch)

        tasks = [process_batch_with_limit(batch) for batch in batches]

        for task in asyncio.as_completed(tasks):
            batch_results = await task
            all_results.extend(batch_results)
            processed += len(batch_results)

            # Report progress
            self._report_progress(
                processed,
                total_files,
                start_time,
                batch_results
            )

        return all_results

    def _report_progress(
        self,
        processed: int,
        total: int,
        start_time: float,
        batch_results: List[EmbeddingResult]
    ) -> None:
        """Report progress to callback if configured."""
        if not self.progress_callback:
            return

        elapsed = time.time() - start_time
        files_per_sec = processed / elapsed if elapsed > 0 else 0
        eta = (total - processed) / files_per_sec if files_per_sec > 0 else 0

        update = ProgressUpdate(
            processed=processed,
            total=total,
            percentage=(processed / total) * 100,
            eta_seconds=eta,
            current_file=batch_results[-1].file_path if batch_results else None
        )
        self.progress_callback(update)

    def _create_batches(
        self,
        files: List[tuple[str, str]]
    ) -> List[List[tuple[str, str]]]:
        """
        Split files into batches of configured size.

        Args:
            files: List of (file_path, content) tuples

        Returns:
            List of batches
        """
        batches = []
        for i in range(0, len(files), self.batch_size):
            batch = files[i:i + self.batch_size]
            batches.append(batch)
        return batches

    async def _process_batch(
        self,
        batch: List[tuple[str, str]]
    ) -> List[EmbeddingResult]:
        """
        Process single batch with OpenAI API.

        Args:
            batch: List of (file_path, content) tuples

        Returns:
            List of EmbeddingResult
        """
        batch_start = time.time()

        # Prepare texts for embedding
        texts = [content for _, content in batch]
        file_paths = [path for path, _ in batch]

        try:
            # Call OpenAI embedding API (batch)
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            # Extract embeddings
            results = []
            for i, embedding_data in enumerate(response.data):
                # Count tokens
                token_count = self._count_tokens(texts[i])

                results.append(EmbeddingResult(
                    file_path=file_paths[i],
                    embedding=embedding_data.embedding,
                    token_count=token_count,
                    embedding_time=time.time() - batch_start
                ))

            return results

        except Exception as e:
            print(f"❌ Batch embedding failed: {e}")
            # Return empty embeddings on failure
            return [
                EmbeddingResult(
                    file_path=path,
                    embedding=[],
                    token_count=0,
                    embedding_time=0
                )
                for path in file_paths
            ]

    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text content

        Returns:
            Estimated token count
        """
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except:
                pass

        # Fallback: rough estimate (4 chars per token)
        return len(text) // 4

    def set_progress_callback(
        self,
        callback: Callable[[ProgressUpdate], None]
    ) -> None:
        """
        Set callback for progress updates.

        Args:
            callback: Function to call with ProgressUpdate
        """
        self.progress_callback = callback

    async def estimate_cost(
        self,
        file_contents: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Estimate API cost before embedding.

        Args:
            file_contents: Dict mapping file_path -> file_content

        Returns:
            Dict with cost estimate details
        """
        # Count total tokens
        total_tokens = sum(
            self._count_tokens(content)
            for content in file_contents.values()
        )

        # OpenAI pricing (text-embedding-3-small)
        cost_per_1m_tokens = 0.02  # $0.02 per 1M tokens

        estimated_cost = (total_tokens / 1_000_000) * cost_per_1m_tokens

        return {
            'total_files': len(file_contents),
            'total_tokens': total_tokens,
            'estimated_cost_usd': round(estimated_cost, 4),
            'model': self.model,
            'batch_size': self.batch_size,
            'parallel_tasks': self.parallel_tasks
        }


def create_parallel_embedder(
    api_key: str,
    batch_size: int = 64,
    parallel_tasks: int = 10
) -> ParallelEmbedder:
    """
    Factory function to create ParallelEmbedder.

    Args:
        api_key: OpenAI API key
        batch_size: Files per batch (default 64)
        parallel_tasks: Concurrent batches (default 10)

    Returns:
        ParallelEmbedder instance
    """
    return ParallelEmbedder(
        api_key=api_key,
        batch_size=batch_size,
        parallel_tasks=parallel_tasks
    )
