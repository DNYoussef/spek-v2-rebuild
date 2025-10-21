"""
Context DNA Bridge (Python → TypeScript)

Provides Python interface to TypeScript Context DNA storage system.
Uses subprocess to call Node.js scripts for Context DNA operations.

Week 20 Day 1
Version: 8.0.0
"""

import json
import subprocess
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


# ============================================================================
# Types (Python equivalents of TypeScript types)
# ============================================================================

@dataclass
class AgentExecutionContext:
    """Agent execution context."""
    agent_id: str
    project_id: str
    session_id: str
    start_time: datetime
    task_id: Optional[str] = None
    parent_agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ContextPersistenceResult:
    """Context persistence result."""
    success: bool
    performance_ms: float
    context_id: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Context DNA Bridge
# ============================================================================

class ContextDNABridge:
    """
    Bridge between Python AgentBase and TypeScript Context DNA.

    Provides Python-friendly interface for context persistence.
    """

    def __init__(self, node_script_path: Optional[str] = None):
        """
        Initialize Context DNA bridge.

        Args:
            node_script_path: Path to Node.js script (optional)
        """
        # Default to atlantis-ui directory
        self.node_script_path = node_script_path or (
            "C:/Users/17175/Desktop/spek-v2-rebuild/atlantis-ui/"
        )

    async def initialize_context(
        self,
        context: AgentExecutionContext
    ) -> None:
        """
        Initialize agent execution context.

        Args:
            context: Agent execution context
        """
        payload = {
            "operation": "initialize_context",
            "context": self._serialize_context(context),
        }

        result = await self._call_node_script(payload)

        if not result.get("success"):
            logger.error(
                f"Failed to initialize context: {result.get('error')}"
            )

    async def store_agent_thought(
        self,
        context: AgentExecutionContext,
        thought: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store agent thought during execution.

        Args:
            context: Agent execution context
            thought: Agent thought content
            metadata: Optional metadata
        """
        payload = {
            "operation": "store_agent_thought",
            "context": self._serialize_context(context),
            "thought": thought,
            "metadata": metadata or {},
        }

        result = await self._call_node_script(payload)

        if not result.get("success"):
            logger.warning(
                f"Failed to store agent thought: {result.get('error')}"
            )

    async def store_agent_result(
        self,
        context: AgentExecutionContext,
        result_data: Dict[str, Any]
    ) -> ContextPersistenceResult:
        """
        Store agent result after execution.

        Args:
            context: Agent execution context
            result_data: Result data (success, output, error, etc.)

        Returns:
            ContextPersistenceResult
        """
        payload = {
            "operation": "store_agent_result",
            "context": self._serialize_context(context),
            "result": result_data,
        }

        result = await self._call_node_script(payload)

        return ContextPersistenceResult(
            success=result.get("success", False),
            context_id=result.get("contextId"),
            error=result.get("error"),
            performance_ms=result.get("performanceMs", 0.0),
        )

    async def retrieve_context(
        self,
        project_id: str,
        agent_id: str,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for agent execution.

        Args:
            project_id: Project ID
            agent_id: Agent ID
            query: Search query
            limit: Maximum number of results

        Returns:
            Dict with conversations, memories, tasks
        """
        payload = {
            "operation": "retrieve_context",
            "query": {
                "projectId": project_id,
                "agentId": agent_id,
                "query": query,
                "limit": limit,
            },
        }

        result = await self._call_node_script(payload)

        return {
            "conversations": result.get("conversations", []),
            "memories": result.get("memories", []),
            "tasks": result.get("tasks", []),
            "performance_ms": result.get("performanceMs", 0.0),
        }

    async def finalize_context(
        self,
        context: AgentExecutionContext
    ) -> None:
        """
        Finalize agent execution context.

        Args:
            context: Agent execution context
        """
        payload = {
            "operation": "finalize_context",
            "context": self._serialize_context(context),
        }

        result = await self._call_node_script(payload)

        if not result.get("success"):
            logger.warning(
                f"Failed to finalize context: {result.get('error')}"
            )

    # Private helper methods
    def _serialize_context(
        self,
        context: AgentExecutionContext
    ) -> Dict[str, Any]:
        """Serialize context to JSON-compatible dict."""
        return {
            "agentId": context.agent_id,
            "projectId": context.project_id,
            "taskId": context.task_id,
            "parentAgentId": context.parent_agent_id,
            "sessionId": context.session_id,
            "startTime": context.start_time.isoformat(),
            "metadata": context.metadata or {},
        }

    async def _call_node_script(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Node.js script with payload.

        Args:
            payload: JSON payload

        Returns:
            Result dict
        """
        try:
            # Write payload to temp file
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False
            ) as f:
                json.dump(payload, f)
                temp_file = f.name

            try:
                # Call Node.js script
                result = subprocess.run(
                    [
                        "node",
                        f"{self.node_script_path}/scripts/context-dna-bridge.js",
                        temp_file,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,  # 5 second timeout
                )

                if result.returncode == 0:
                    return json.loads(result.stdout)
                else:
                    logger.error(f"Node.js script error: {result.stderr}")
                    return {
                        "success": False,
                        "error": result.stderr,
                    }

            finally:
                # Clean up temp file
                os.unlink(temp_file)

        except Exception as e:
            logger.error(f"Failed to call Node.js script: {e}")
            return {
                "success": False,
                "error": str(e),
            }


# ============================================================================
# Singleton Instance
# ============================================================================

_context_dna_bridge: Optional[ContextDNABridge] = None


def get_context_dna_bridge() -> ContextDNABridge:
    """Get or create Context DNA bridge singleton."""
    global _context_dna_bridge
    if _context_dna_bridge is None:
        _context_dna_bridge = ContextDNABridge()
    return _context_dna_bridge
