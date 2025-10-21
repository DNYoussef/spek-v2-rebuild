"""Research Coordinator - Spawns researcher agents for Loop 1.

This module provides utilities for spawning researcher agents and collecting
research findings for pre-mortem planning and risk analysis.

NASA Rule 10 Compliant: All functions ≤60 LOC
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def validate_research_topic(topic: str) -> Dict[str, Any]:
    """Validate research topic input.

    Args:
        topic: Research topic string to validate

    Returns:
        Dict with validation result and error message if invalid

    Raises:
        ValueError: If topic is invalid
    """
    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty")

    if len(topic) > 500:
        raise ValueError("Research topic too long (max 500 chars)")

    return {
        "valid": True,
        "topic": topic.strip(),
        "length": len(topic.strip())
    }


def build_researcher_prompt(
    topic: str,
    focus_areas: Optional[List[str]] = None,
    depth: str = "comprehensive"
) -> str:
    """Build structured prompt for researcher agent.

    Args:
        topic: Main research topic
        focus_areas: Optional list of specific areas to investigate
        depth: Research depth (quick, moderate, comprehensive)

    Returns:
        Formatted prompt string for researcher agent
    """
    prompt_parts = [
        f"Research Topic: {topic}",
        "",
        f"Research Depth: {depth}",
        ""
    ]

    if focus_areas:
        prompt_parts.extend([
            "Focus Areas:",
            *[f"- {area}" for area in focus_areas],
            ""
        ])

    prompt_parts.extend([
        "Requirements:",
        "- Provide evidence-based findings",
        "- Include quantitative data where possible",
        "- Cite sources and references",
        "- Identify risks and opportunities",
        "- Suggest mitigation strategies",
        "",
        "Output Format: Structured markdown with sections"
    ])

    return "\n".join(prompt_parts)


def _execute_spawn_command(
    cmd: List[str],
    timestamp: str,
    topic: str,
    output_file: Path,
    focus_areas: List[str],
    depth: str
) -> Dict[str, Any]:
    """Execute spawn command and handle results.

    Args:
        cmd: Command list for subprocess
        timestamp: Timestamp for agent ID
        topic: Research topic
        output_file: Output file path
        focus_areas: Focus areas list
        depth: Research depth

    Returns:
        Dict with execution results
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        return {
            "success": result.returncode == 0,
            "agent_id": f"researcher_{timestamp}",
            "output_path": str(output_file),
            "topic": topic,
            "focus_areas": focus_areas,
            "depth": depth,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": timestamp
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Agent spawn timeout (300s)",
            "topic": topic
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to spawn agent: {str(e)}",
            "topic": topic
        }


def spawn_researcher_agent(
    topic: str,
    output_dir: Path,
    focus_areas: Optional[List[str]] = None,
    depth: str = "comprehensive"
) -> Dict[str, Any]:
    """Spawn researcher agent via Claude Flow.

    Args:
        topic: Research topic to investigate
        output_dir: Directory for research output
        focus_areas: Optional specific areas to focus on
        depth: Research depth level

    Returns:
        Dict with agent_id, status, output_path, and metadata
    """
    validation = validate_research_topic(topic)
    prompt = build_researcher_prompt(topic, focus_areas, depth)

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"research_{timestamp}.md"

    cmd = [
        "npx", "claude-flow@alpha",
        "agent", "spawn",
        "--type", "researcher",
        "--task", prompt,
        "--output", str(output_file)
    ]

    return _execute_spawn_command(
        cmd, timestamp, validation["topic"],
        output_file, focus_areas or [], depth
    )


def collect_research_findings(research_dir: Path) -> Dict[str, Any]:
    """Collect and aggregate research findings from directory.

    Args:
        research_dir: Directory containing research markdown files

    Returns:
        Dict with aggregated findings, file count, and metadata
    """
    if not research_dir.exists():
        return {
            "success": False,
            "error": f"Research directory not found: {research_dir}"
        }

    findings = []
    research_files = list(research_dir.glob("research_*.md"))

    for file_path in research_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            findings.append({
                "file": file_path.name,
                "content": content,
                "size": len(content),
                "modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat()
            })
        except Exception as e:
            findings.append({
                "file": file_path.name,
                "error": f"Failed to read: {str(e)}"
            })

    return {
        "success": True,
        "findings": findings,
        "file_count": len(findings),
        "total_size": sum(f.get("size", 0) for f in findings),
        "research_dir": str(research_dir)
    }


def export_research_summary(
    findings: Dict[str, Any],
    output_path: Path
) -> Dict[str, Any]:
    """Export research findings summary to JSON.

    Args:
        findings: Research findings dict from collect_research_findings
        output_path: Path for JSON export

    Returns:
        Dict with export status and file path
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(findings, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "export_path": str(output_path),
            "file_count": findings.get("file_count", 0)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Export failed: {str(e)}"
        }


if __name__ == "__main__":
    # Example usage
    print("Research Coordinator - Example Usage\n")

    # Example 1: Spawn researcher for AI agent coordination
    topic = "Best practices for AI agent coordination systems"
    focus = ["performance optimization", "error handling", "testing"]

    result = spawn_researcher_agent(
        topic=topic,
        output_dir=Path("research"),
        focus_areas=focus,
        depth="comprehensive"
    )

    print(f"Agent Spawn Result: {result['success']}")
    if result['success']:
        print(f"Output: {result['output_path']}")

    # Example 2: Collect findings
    findings = collect_research_findings(Path("research"))
    print(f"\nFindings Collected: {findings['file_count']} files")

    # Example 3: Export summary
    export_result = export_research_summary(
        findings,
        Path("research/summary.json")
    )
    print(f"Export Success: {export_result['success']}")
