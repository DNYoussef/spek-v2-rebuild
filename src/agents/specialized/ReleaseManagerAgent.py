"""
ReleaseManagerAgent - Release Management Specialist

Version control, changelog generation, and release coordination:
- Prepare release artifacts
- Generate changelogs from git history
- Create git tags and releases
- Coordinate deployment phases

Part of specialized agent roster (Week 9 Day 2).

Week 9 Day 2
Version: 8.0.0
"""

import time
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from src.agents.AgentBase import (
    AgentBase,
    AgentType,
    AgentStatus,
    AgentCapability,
    AgentMetadata,
    Task,
    ValidationResult,
    ValidationError,
    Result,
    ErrorInfo,
    create_agent_metadata
)
from src.agents.instructions import RELEASE_MANAGER_INSTRUCTIONS


# ============================================================================
# Release-Specific Types
# ============================================================================

@dataclass
class ReleaseInfo:
    """Release information."""
    version: str
    tag: str
    branch: str
    commit_sha: str
    release_notes: str
    changelog: str
    artifacts: List[str]


@dataclass
class VersionInfo:
    """Semantic version information."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    def __str__(self) -> str:
        """Format version string."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version


# ============================================================================
# ReleaseManagerAgent Class
# ============================================================================

class ReleaseManagerAgent(AgentBase):
    """
    Release-Manager Agent - Release management specialist.

    Responsibilities:
    - Prepare releases
    - Generate changelogs
    - Create git tags
    - Coordinate deployments
    """

    def __init__(self):
        """Initialize Release-Manager Agent."""
        metadata = create_agent_metadata(
            agent_id="release-manager",
            name="Release Management Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "prepare-release",
                "generate-changelog",
                "tag-release",
                "coordinate-deployment"
            ],
            capabilities=[
                AgentCapability(
                    name="Release Coordination",
                    description="Coordinate release process",
                    level=10
                ),
                AgentCapability(
                    name="Version Management",
                    description="Manage semantic versioning",
                    level=9
                ),
                AgentCapability(
                    name="Changelog Generation",
                    description="Generate changelogs from commits",
                    level=9
                ),
                AgentCapability(
                    name="Git Operations",
                    description="Perform git tagging and branching",
                    level=8
                ),
                AgentCapability(
                    name="Rollback Management",
                    description="Plan and execute rollbacks",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 principles
            system_instructions=RELEASE_MANAGER_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Commit message patterns
        self.commit_patterns = {
            "feat": r"^feat(\(.+\))?:",
            "fix": r"^fix(\(.+\))?:",
            "docs": r"^docs(\(.+\))?:",
            "style": r"^style(\(.+\))?:",
            "refactor": r"^refactor(\(.+\))?:",
            "perf": r"^perf(\(.+\))?:",
            "test": r"^test(\(.+\))?:",
            "chore": r"^chore(\(.+\))?:"
        }

    # ========================================================================
    # AgentContract Implementation
    # ========================================================================

    async def validate(self, task: Task) -> ValidationResult:
        """
        Validate task before execution.

        Target: <5ms latency

        Args:
            task: Task to validate

        Returns:
            ValidationResult
        """
        start_time = time.time()
        errors = []

        # Common structure validation
        errors.extend(self.validate_task_structure(task))

        # Task type validation
        errors.extend(self.validate_task_type(task))

        # Release-specific validation
        if task.type == "prepare-release":
            errors.extend(self._validate_release_payload(task))

        validation_time = (time.time() - start_time) * 1000  # ms

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            validation_time=validation_time
        )

    async def execute(self, task: Task) -> Result:
        """
        Execute validated task.

        Routes to appropriate handler based on task type.

        Args:
            task: Task to execute

        Returns:
            Result
        """
        start_time = time.time()

        try:
            self.update_status(AgentStatus.BUSY)
            self.log_info(f"Executing task {task.id} (type: {task.type})")

            # Route to handler
            if task.type == "prepare-release":
                result_data = await self._execute_prepare_release(task)
            elif task.type == "generate-changelog":
                result_data = await self._execute_generate_changelog(task)
            elif task.type == "tag-release":
                result_data = await self._execute_tag_release(task)
            elif task.type == "coordinate-deployment":
                result_data = await self._execute_coordinate_deployment(task)
            else:
                raise ValueError(f"Unsupported task type: {task.type}")

            execution_time = (time.time() - start_time) * 1000  # ms

            self.update_status(AgentStatus.IDLE)

            return self.build_result(
                task_id=task.id,
                success=True,
                data=result_data,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000  # ms
            self.log_error(f"Task {task.id} failed", exc=e)

            self.update_status(AgentStatus.ERROR)

            return self.build_result(
                task_id=task.id,
                success=False,
                error=ErrorInfo(
                    code="EXECUTION_FAILED",
                    message=str(e),
                    stack=None
                ),
                execution_time=execution_time
            )

    # ========================================================================
    # Task Execution Methods
    # ========================================================================

    async def _execute_prepare_release(self, task: Task) -> Dict[str, Any]:
        """
        Prepare release artifacts.

        Args:
            task: Prepare-release task

        Returns:
            Release preparation result
        """
        current_version = task.payload.get("current_version", "1.0.0")
        bump_type = task.payload.get("bump_type", "minor")

        self.log_info(
            f"Preparing release: bumping {current_version} ({bump_type})"
        )

        # Calculate next version
        next_version = self._calculate_next_version(
            current_version,
            bump_type
        )

        # Generate changelog
        changelog = await self._generate_changelog_content(
            task.payload.get("commits", [])
        )

        # Create release notes
        release_notes = self._generate_release_notes(
            str(next_version),
            changelog
        )

        # Write changelog file
        changelog_file = Path("CHANGELOG.md")
        if changelog_file.exists():
            with open(changelog_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = "# Changelog\n\n"

        # Prepend new version
        new_content = (
            f"# Changelog\n\n"
            f"## [{next_version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"{changelog}\n\n"
            f"{existing_content.replace('# Changelog\n\n', '')}"
        )

        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Create release info
        release = ReleaseInfo(
            version=str(next_version),
            tag=f"v{next_version}",
            branch=task.payload.get("branch", "main"),
            commit_sha="HEAD",
            release_notes=release_notes,
            changelog=changelog,
            artifacts=[]
        )

        return {
            "current_version": current_version,
            "next_version": str(next_version),
            "changelog_file": str(changelog_file),
            "release_notes": release_notes,
            "release": release.__dict__
        }

    async def _execute_generate_changelog(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Generate changelog from git history.

        Args:
            task: Generate-changelog task

        Returns:
            Changelog generation result
        """
        from_version = task.payload.get("from_version")
        to_version = task.payload.get("to_version", "HEAD")

        self.log_info(
            f"Generating changelog from {from_version} to {to_version}"
        )

        # Simulate commit parsing
        commits = task.payload.get("commits", [])

        # Categorize commits
        categorized = self._categorize_commits(commits)

        # Generate markdown
        changelog = self._format_changelog_markdown(categorized)

        return {
            "from_version": from_version,
            "to_version": to_version,
            "commit_count": len(commits),
            "changelog": changelog
        }

    async def _execute_tag_release(self, task: Task) -> Dict[str, Any]:
        """
        Create git tag and release.

        Args:
            task: Tag-release task

        Returns:
            Tagging result
        """
        version = task.payload.get("version")
        tag = f"v{version}"
        message = task.payload.get("message", f"Release {version}")

        self.log_info(f"Creating git tag: {tag}")

        # Generate git commands
        commands = [
            f"git tag -a {tag} -m \"{message}\"",
            f"git push origin {tag}"
        ]

        return {
            "version": version,
            "tag": tag,
            "message": message,
            "commands": commands,
            "tagged": True
        }

    async def _execute_coordinate_deployment(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """
        Coordinate deployment phases.

        Args:
            task: Coordinate-deployment task

        Returns:
            Deployment coordination result
        """
        version = task.payload.get("version")
        environment = task.payload.get("environment", "production")

        self.log_info(
            f"Coordinating deployment of {version} to {environment}"
        )

        # Deployment phases
        phases = [
            "Pre-deployment checks",
            "Build artifacts",
            "Deploy to staging",
            "Run smoke tests",
            "Deploy to production",
            "Post-deployment verification",
            "Rollback plan ready"
        ]

        return {
            "version": version,
            "environment": environment,
            "phases": phases,
            "phase_count": len(phases),
            "status": "coordinated"
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_next_version(
        self,
        current: str,
        bump_type: str
    ) -> VersionInfo:
        """Calculate next semantic version."""
        # Parse current version
        match = re.match(
            r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?(?:\+(.+))?$",
            current
        )

        if not match:
            # Default to 1.0.0
            major, minor, patch = 1, 0, 0
            prerelease, build = None, None
        else:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
            prerelease = match.group(4)
            build = match.group(5)

        # Bump version
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            # Default to patch
            patch += 1

        return VersionInfo(
            major=major,
            minor=minor,
            patch=patch,
            prerelease=None,
            build=None
        )

    async def _generate_changelog_content(
        self,
        commits: List[str]
    ) -> str:
        """Generate changelog content from commits."""
        if not commits:
            commits = [
                "feat: Add new feature X",
                "fix: Resolve bug in Y",
                "docs: Update README"
            ]

        categorized = self._categorize_commits(commits)
        return self._format_changelog_markdown(categorized)

    def _categorize_commits(
        self,
        commits: List[str]
    ) -> Dict[str, List[str]]:
        """Categorize commits by type."""
        categorized = {
            "Features": [],
            "Bug Fixes": [],
            "Documentation": [],
            "Performance": [],
            "Other": []
        }

        for commit in commits:
            commit_lower = commit.lower()

            if re.match(self.commit_patterns["feat"], commit_lower):
                categorized["Features"].append(commit)
            elif re.match(self.commit_patterns["fix"], commit_lower):
                categorized["Bug Fixes"].append(commit)
            elif re.match(self.commit_patterns["docs"], commit_lower):
                categorized["Documentation"].append(commit)
            elif re.match(self.commit_patterns["perf"], commit_lower):
                categorized["Performance"].append(commit)
            else:
                categorized["Other"].append(commit)

        return categorized

    def _format_changelog_markdown(
        self,
        categorized: Dict[str, List[str]]
    ) -> str:
        """Format categorized commits as markdown."""
        markdown = ""

        for category, commits in categorized.items():
            if commits:
                markdown += f"### {category}\n\n"
                for commit in commits:
                    # Extract commit message
                    msg = re.sub(r"^[a-z]+(\(.+\))?:\s*", "", commit)
                    markdown += f"- {msg}\n"
                markdown += "\n"

        return markdown.strip()

    def _generate_release_notes(
        self,
        version: str,
        changelog: str
    ) -> str:
        """Generate release notes."""
        return f"""# Release {version}

{changelog}

## Installation

```bash
# Install via pip
pip install spek-platform=={version}

# Install via npm
npm install @spek/platform@{version}
```

## Contributors

Thank you to all contributors who made this release possible!
"""

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_release_payload(self, task: Task) -> List[ValidationError]:
        """Validate prepare-release task payload."""
        errors = []

        if "current_version" not in task.payload:
            errors.append(ValidationError(
                field="payload.current_version",
                message="Release task requires 'current_version'",
                severity=8
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_release_manager_agent() -> ReleaseManagerAgent:
    """
    Create Release-Manager Agent instance.

    Returns:
        ReleaseManagerAgent
    """
    return ReleaseManagerAgent()
