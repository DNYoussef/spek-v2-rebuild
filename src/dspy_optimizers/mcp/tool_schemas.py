"""
MCP Tool Schemas

Schema definitions for common MCP tools to validate tool calls.

Week 21 Day 3
Version: 1.0.0
"""

from typing import Dict, List, Any


# ============================================================================
# MCP Tool Schema Definitions
# ============================================================================

MCP_TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    # GitHub Tools
    "github__create_pr": {
        "description": "Create a new pull request on GitHub",
        "required": ["title", "body", "head", "base"],
        "optional": ["draft", "maintainer_can_modify", "labels", "assignees"],
        "types": {
            "title": str,
            "body": str,
            "head": str,
            "base": str,
            "draft": bool,
            "maintainer_can_modify": bool,
            "labels": list,
            "assignees": list
        }
    },

    "github__create_issue": {
        "description": "Create a new issue on GitHub",
        "required": ["title", "body"],
        "optional": ["labels", "assignees", "milestone"],
        "types": {
            "title": str,
            "body": str,
            "labels": list,
            "assignees": list,
            "milestone": int
        }
    },

    "github__list_prs": {
        "description": "List pull requests in a repository",
        "required": [],
        "optional": ["state", "sort", "direction", "per_page", "page"],
        "types": {
            "state": str,  # open, closed, all
            "sort": str,  # created, updated, popularity
            "direction": str,  # asc, desc
            "per_page": int,
            "page": int
        }
    },

    "github__merge_pr": {
        "description": "Merge a pull request",
        "required": ["pull_number"],
        "optional": ["commit_title", "commit_message", "merge_method"],
        "types": {
            "pull_number": int,
            "commit_title": str,
            "commit_message": str,
            "merge_method": str  # merge, squash, rebase
        }
    },

    # Filesystem Tools
    "filesystem__read": {
        "description": "Read contents of a file",
        "required": ["path"],
        "optional": ["encoding"],
        "types": {
            "path": str,
            "encoding": str  # utf-8, ascii, etc.
        }
    },

    "filesystem__write": {
        "description": "Write contents to a file",
        "required": ["path", "content"],
        "optional": ["encoding", "create_dirs"],
        "types": {
            "path": str,
            "content": str,
            "encoding": str,
            "create_dirs": bool
        }
    },

    "filesystem__search": {
        "description": "Search for files matching pattern",
        "required": ["pattern"],
        "optional": ["path", "recursive", "max_results"],
        "types": {
            "pattern": str,
            "path": str,
            "recursive": bool,
            "max_results": int
        }
    },

    # Code Tools
    "code__analyze": {
        "description": "Analyze code for issues",
        "required": ["file_path"],
        "optional": ["analyzer_type", "rules"],
        "types": {
            "file_path": str,
            "analyzer_type": str,  # syntax, security, quality
            "rules": list
        }
    },

    "code__refactor": {
        "description": "Refactor code according to rules",
        "required": ["file_path", "refactor_type"],
        "optional": ["options"],
        "types": {
            "file_path": str,
            "refactor_type": str,  # extract_method, rename, etc.
            "options": dict
        }
    },

    "code__generate_tests": {
        "description": "Generate test cases for code",
        "required": ["source_file"],
        "optional": ["test_type", "coverage_target"],
        "types": {
            "source_file": str,
            "test_type": str,  # unit, integration
            "coverage_target": float
        }
    },

    # Cloud Tools (Azure)
    "azure__deploy": {
        "description": "Deploy application to Azure",
        "required": ["resource_group", "app_name"],
        "optional": ["region", "plan", "runtime"],
        "types": {
            "resource_group": str,
            "app_name": str,
            "region": str,
            "plan": str,
            "runtime": str
        }
    },

    # Cloud Tools (AWS)
    "aws__s3_upload": {
        "description": "Upload file to AWS S3",
        "required": ["bucket", "key", "file_path"],
        "optional": ["acl", "metadata"],
        "types": {
            "bucket": str,
            "key": str,
            "file_path": str,
            "acl": str,  # private, public-read, etc.
            "metadata": dict
        }
    },

    # Database Tools
    "mongodb__query": {
        "description": "Query MongoDB collection",
        "required": ["collection", "query"],
        "optional": ["projection", "limit", "sort"],
        "types": {
            "collection": str,
            "query": dict,
            "projection": dict,
            "limit": int,
            "sort": dict
        }
    },

    "postgres__execute": {
        "description": "Execute PostgreSQL query",
        "required": ["query"],
        "optional": ["parameters", "fetch"],
        "types": {
            "query": str,
            "parameters": list,
            "fetch": bool
        }
    },

    # Productivity Tools
    "todoist__add_task": {
        "description": "Add task to Todoist",
        "required": ["content"],
        "optional": ["project_id", "due_date", "priority", "labels"],
        "types": {
            "content": str,
            "project_id": str,
            "due_date": str,
            "priority": int,  # 1-4
            "labels": list
        }
    },

    "jira__create_ticket": {
        "description": "Create Jira ticket",
        "required": ["project", "summary", "issue_type"],
        "optional": ["description", "assignee", "priority", "labels"],
        "types": {
            "project": str,
            "summary": str,
            "issue_type": str,  # Bug, Story, Task, etc.
            "description": str,
            "assignee": str,
            "priority": str,
            "labels": list
        }
    }
}


# ============================================================================
# Schema Validation Helper
# ============================================================================

def validate_tool_call(tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate MCP tool call against schema.

    Args:
        tool_name: MCP tool name
        parameters: Tool call parameters

    Returns:
        Tuple of (valid: bool, errors: List[str])
    """
    errors = []

    # Check if tool exists
    if tool_name not in MCP_TOOL_SCHEMAS:
        errors.append(f"Unknown MCP tool: {tool_name}")
        return False, errors

    schema = MCP_TOOL_SCHEMAS[tool_name]

    # Check required fields
    for field in schema["required"]:
        if field not in parameters:
            errors.append(f"Missing required field: {field}")

    # Check parameter types
    for param, value in parameters.items():
        if param in schema["types"]:
            expected_type = schema["types"][param]
            if not isinstance(value, expected_type):
                errors.append(
                    f"Invalid type for {param}: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

    return len(errors) == 0, errors
