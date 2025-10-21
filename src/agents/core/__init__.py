"""
Core Agents (5 total)

- queen: Top-level coordinator
- coder: Code implementation
- researcher: Research and analysis
- tester: Test creation and validation
- reviewer: Code review and quality

Week 5
Version: 8.0.0
"""

from .QueenAgent import QueenAgent, create_queen_agent
from .TesterAgent import TesterAgent, create_tester_agent
from .ReviewerAgent import ReviewerAgent, create_reviewer_agent
from .CoderAgent import CoderAgent, create_coder_agent
from .ResearcherAgent import ResearcherAgent, create_researcher_agent

__all__ = [
    "QueenAgent",
    "create_queen_agent",
    "TesterAgent",
    "create_tester_agent",
    "ReviewerAgent",
    "create_reviewer_agent",
    "CoderAgent",
    "create_coder_agent",
    "ResearcherAgent",
    "create_researcher_agent"
]
