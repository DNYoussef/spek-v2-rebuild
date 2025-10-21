"""
MCP Tool Call Signature

Used by any agent when calling MCP (Model Context Protocol) tools
to ensure correct parameter formatting and tool selection.

Week 21 Day 3
Version: 1.0.0
"""

import dspy


class MCPToolCallSignature(dspy.Signature):
    """
    Generate valid MCP tool call with correct parameters.

    You are an expert at using MCP (Model Context Protocol) tools correctly.
    Your role is to translate agent intent into properly-formatted MCP tool
    calls with all required parameters and correct types.

    Common MCP tools:
    - GitHub: github__create_pr, github__create_issue, github__list_prs
    - Filesystem: filesystem__read, filesystem__write, filesystem__search
    - Code: code__analyze, code__refactor, code__generate_tests
    - Cloud: azure__deploy, aws__s3_upload, kubernetes__apply
    - Database: mongodb__query, postgres__execute
    - Productivity: todoist__add_task, jira__create_ticket

    Each tool call must have:
    - Correct tool name (exact match to MCP schema)
    - All required parameters (validated against schema)
    - Correct parameter types (string, int, object, array)
    - Valid parameter values (no placeholders or mock data)

    Follow the 26 prompt engineering principles:
    - Accuracy: Match MCP schema exactly
    - Completeness: Include all required fields
    - Type Safety: Correct parameter types
    - Validation: No placeholder/TODO values
    """

    tool_name = dspy.InputField(
        desc="MCP tool to call (e.g., github__create_pr, filesystem__write)"
    )
    intent = dspy.InputField(
        desc="What the agent wants to accomplish with this tool call"
    )
    context = dspy.InputField(
        desc="Available context (files, data, branches, etc.) that can be used as parameters"
    )

    reasoning = dspy.OutputField(
        desc="Tool selection reasoning and parameter extraction logic",
        prefix="Reasoning: Let's think step by step in order to"
    )

    tool_call = dspy.OutputField(
        desc=(
            "MCP tool call as JSON object. "
            "Must have: "
            "{'tool': str, 'parameters': dict} "
            "where parameters match the MCP schema for this tool"
        )
    )
