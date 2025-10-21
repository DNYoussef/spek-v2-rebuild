"""
MCP Tool Validator

DSPy module for validating and optimizing MCP tool calls.
Ensures correct tool selection and parameter formatting.

Week 21 Day 3
Version: 1.0.0
"""

import dspy
import json
from typing import Any, Dict
from pathlib import Path

from src.dspy_optimizers.signatures import MCPToolCallSignature
from .tool_schemas import MCP_TOOL_SCHEMAS, validate_tool_call


class MCPToolValidator(dspy.Module):
    """
    Validate and optimize MCP tool calls.

    Learns to:
    - Select correct MCP tool for agent intent
    - Extract parameters from context
    - Format parameters with correct types
    - Include all required fields
    - Avoid placeholder/TODO values

    Training focuses on:
    - GitHub tools (PR creation, issue management)
    - Filesystem operations (read, write, search)
    - Code tools (analyze, refactor, test generation)
    - Cloud deployments (Azure, AWS)
    """

    def __init__(self):
        super().__init__()
        # Chain-of-Thought for parameter extraction reasoning
        self.validate_call = dspy.ChainOfThought(MCPToolCallSignature)

    def forward(
        self,
        tool_name: str,
        intent: str,
        context: Dict[str, Any]
    ) -> dspy.Prediction:
        """
        Generate validated MCP tool call.

        Args:
            tool_name: MCP tool to call (e.g., github__create_pr)
            intent: What agent wants to accomplish
            context: Available context (files, data, etc.)

        Returns:
            Prediction with reasoning, tool_call (JSON), and valid flag

        Latency: ~150ms average (100-250ms range)
        """
        # Convert context dict to string for DSPy
        context_str = json.dumps(context, indent=2)

        # Generate tool call
        result = self.validate_call(
            tool_name=tool_name,
            intent=intent,
            context=context_str
        )

        # Parse and validate tool call
        try:
            tool_call = json.loads(result.tool_call)

            # Schema validation
            valid, errors = validate_tool_call(
                tool_name=tool_call.get("tool", ""),
                parameters=tool_call.get("parameters", {})
            )

            if not valid:
                return dspy.Prediction(
                    reasoning=result.reasoning,
                    tool_call=tool_call,
                    valid=False,
                    errors=errors
                )

            return dspy.Prediction(
                reasoning=result.reasoning,
                tool_call=tool_call,
                valid=True,
                errors=[]
            )

        except json.JSONDecodeError as e:
            return dspy.Prediction(
                reasoning=result.reasoning,
                tool_call={},
                valid=False,
                errors=[f"Invalid JSON: {str(e)}"]
            )
        except Exception as e:
            return dspy.Prediction(
                reasoning=result.reasoning,
                tool_call={},
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )

    def load(self, path: str) -> None:
        """
        Load compiled model from JSON.

        Args:
            path: Path to compiled model JSON (instruction + demos)
        """
        model_path = Path(path)
        if not model_path.exists():
            raise FileNotFoundError(f"Compiled model not found: {path}")

        # DSPy loads frozen instruction + demonstrations
        super().load(path)

    def get_available_tools(self) -> Dict[str, str]:
        """
        Get list of available MCP tools with descriptions.

        Returns:
            Dict mapping tool name to description
        """
        return {
            tool: schema["description"]
            for tool, schema in MCP_TOOL_SCHEMAS.items()
        }


# ============================================================================
# Helper Functions
# ============================================================================

def create_mcp_validator() -> MCPToolValidator:
    """
    Create MCP tool validator instance.

    Returns:
        Configured MCPToolValidator
    """
    return MCPToolValidator()
