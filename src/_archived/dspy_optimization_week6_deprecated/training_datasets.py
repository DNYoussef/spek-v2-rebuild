"""
Training Dataset Generation for DSPy Optimization

Creates realistic training datasets for P0 agents with proper task payloads,
expected outputs, and quality labels for supervised learning.

Week 6 Day 2
Version: 8.0.0
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path

from src.agents.AgentBase import Task


@dataclass
class TrainingExample:
    """Single training example for DSPy."""
    input_task: Task
    expected_output: Dict[str, Any]
    quality_label: float  # 0-100
    rationale: str = ""  # Why this output is good/bad


@dataclass
class TrainingDataset:
    """Complete training dataset for an agent."""
    agent_id: str
    examples: List[TrainingExample]
    train_split: List[TrainingExample] = field(default_factory=list)
    val_split: List[TrainingExample] = field(default_factory=list)

    def split(self, train_ratio: float = 0.8):
        """Split dataset into train/validation sets."""
        split_idx = int(len(self.examples) * train_ratio)
        self.train_split = self.examples[:split_idx]
        self.val_split = self.examples[split_idx:]


class DatasetGenerator:
    """Generates training datasets for P0 agents."""

    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_queen_dataset(self, size: int = 100) -> TrainingDataset:
        """Generate training dataset for Queen agent."""
        examples = []

        # Example 1: Feature implementation workflow (HIGH QUALITY)
        examples.append(TrainingExample(
            input_task=Task(
                id="train-queen-001",
                type="orchestrate",
                description="Implement user authentication feature",
                payload={
                    "workflow": {
                        "objective": "Add login/logout functionality",
                        "steps": []  # Queen should generate this
                    }
                },
                priority=8
            ),
            expected_output={
                "workflow_id": "train-queen-001",
                "steps": [
                    {"agent": "spec-writer", "task_type": "write-spec", "description": "Document auth requirements"},
                    {"agent": "architect", "task_type": "design", "description": "Design auth architecture"},
                    {"agent": "coder", "task_type": "implement", "description": "Implement login/logout"},
                    {"agent": "tester", "task_type": "test", "description": "Create auth tests"},
                    {"agent": "security-manager", "task_type": "security-scan", "description": "Validate auth security"}
                ],
                "estimated_duration_min": 45
            },
            quality_label=95.0,
            rationale="Complete workflow with security validation, proper sequencing"
        ))

        # Example 2: Bug fix workflow (MEDIUM QUALITY)
        examples.append(TrainingExample(
            input_task=Task(
                id="train-queen-002",
                type="coordinate",
                description="Fix critical authentication bug",
                payload={
                    "workflow": {
                        "objective": "Resolve login failure issue",
                        "steps": []
                    }
                },
                priority=9
            ),
            expected_output={
                "workflow_id": "train-queen-002",
                "steps": [
                    {"agent": "debugger", "task_type": "debug", "description": "Identify root cause"},
                    {"agent": "coder", "task_type": "fix", "description": "Implement fix"},
                    {"agent": "tester", "task_type": "test", "description": "Verify fix"}
                ],
                "estimated_duration_min": 20
            },
            quality_label=75.0,
            rationale="Good workflow but missing reviewer step for quality assurance"
        ))

        # Add more examples (simplified for demonstration)
        for i in range(3, min(size, 10)):
            examples.append(self._generate_queen_example(i))

        dataset = TrainingDataset(agent_id="queen", examples=examples)
        dataset.split(train_ratio=0.8)
        return dataset

    def generate_tester_dataset(self, size: int = 100) -> TrainingDataset:
        """Generate training dataset for Tester agent."""
        examples = []

        # Example 1: Unit test generation (HIGH QUALITY)
        examples.append(TrainingExample(
            input_task=Task(
                id="train-tester-001",
                type="test",
                description="Create unit tests for authentication function",
                payload={
                    "source_file": "src/auth/login.py",
                    "function_name": "authenticate_user",
                    "test_type": "unit"
                },
                priority=7
            ),
            expected_output={
                "test_file": "tests/unit/test_auth_login.py",
                "test_count": 8,
                "coverage_pct": 95.0,
                "tests": [
                    {"name": "test_valid_credentials", "type": "happy_path"},
                    {"name": "test_invalid_password", "type": "error_case"},
                    {"name": "test_invalid_email", "type": "error_case"},
                    {"name": "test_missing_credentials", "type": "edge_case"},
                    {"name": "test_sql_injection_attempt", "type": "security"},
                    {"name": "test_concurrent_login", "type": "edge_case"},
                    {"name": "test_account_locked", "type": "error_case"},
                    {"name": "test_expired_session", "type": "edge_case"}
                ]
            },
            quality_label=95.0,
            rationale="Comprehensive coverage: happy path, errors, edge cases, security"
        ))

        # Example 2: Integration test (GOOD QUALITY)
        examples.append(TrainingExample(
            input_task=Task(
                id="train-tester-002",
                type="generate-tests",
                description="Create integration tests for API endpoints",
                payload={
                    "source_file": "src/api/auth_routes.py",
                    "test_type": "integration"
                },
                priority=6
            ),
            expected_output={
                "test_file": "tests/integration/test_auth_api.py",
                "test_count": 5,
                "coverage_pct": 85.0,
                "tests": [
                    {"name": "test_login_endpoint", "type": "happy_path"},
                    {"name": "test_logout_endpoint", "type": "happy_path"},
                    {"name": "test_invalid_token", "type": "error_case"},
                    {"name": "test_rate_limiting", "type": "edge_case"},
                    {"name": "test_cors_headers", "type": "security"}
                ]
            },
            quality_label=85.0,
            rationale="Good coverage but missing some edge cases like token expiry"
        ))

        # Add more examples
        for i in range(3, min(size, 10)):
            examples.append(self._generate_tester_example(i))

        dataset = TrainingDataset(agent_id="tester", examples=examples)
        dataset.split(train_ratio=0.8)
        return dataset

    def generate_reviewer_dataset(self, size: int = 100) -> TrainingDataset:
        """Generate training dataset for Reviewer agent."""
        examples = []

        # Example 1: Code quality review (HIGH QUALITY)
        examples.append(TrainingExample(
            input_task=Task(
                id="train-reviewer-001",
                type="review",
                description="Review authentication implementation",
                payload={
                    "file_path": "src/auth/login.py",
                    "review_type": "quality",
                    "code_snippet": "def authenticate(email, pwd):\n    user = db.query(f'SELECT * FROM users WHERE email={email}')\n    return user.password == pwd"
                },
                priority=7
            ),
            expected_output={
                "review_summary": "Critical security vulnerabilities and poor practices found",
                "issues": [
                    {
                        "severity": "critical",
                        "type": "security",
                        "description": "SQL injection vulnerability in query",
                        "line": 2,
                        "suggestion": "Use parameterized queries: db.query('SELECT * FROM users WHERE email=?', [email])"
                    },
                    {
                        "severity": "critical",
                        "type": "security",
                        "description": "Plain text password comparison",
                        "line": 3,
                        "suggestion": "Use bcrypt.checkpw(pwd.encode(), user.password_hash)"
                    },
                    {
                        "severity": "medium",
                        "type": "style",
                        "description": "Poor parameter naming (pwd instead of password)",
                        "line": 1,
                        "suggestion": "Use descriptive names: authenticate(email: str, password: str)"
                    }
                ],
                "quality_score": 15.0
            },
            quality_label=98.0,
            rationale="Identified all critical security issues with actionable fixes"
        ))

        dataset = TrainingDataset(agent_id="reviewer", examples=examples[:min(size, 10)])
        dataset.split(train_ratio=0.8)
        return dataset

    def generate_coder_dataset(self, size: int = 100) -> TrainingDataset:
        """Generate training dataset for Coder agent."""
        examples = []

        # Example 1: Function implementation (HIGH QUALITY)
        examples.append(TrainingExample(
            input_task=Task(
                id="train-coder-001",
                type="implement",
                description="Implement secure login function",
                payload={
                    "specification": "Create login function with email/password validation, rate limiting, and secure password hashing",
                    "language": "python",
                    "output_file": "src/auth/login.py"
                },
                priority=8
            ),
            expected_output={
                "file_path": "src/auth/login.py",
                "code": """
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.db import get_db
from src.models import User

class LoginManager:
    def __init__(self):
        self.rate_limit_cache: Dict[str, list] = {}
        self.max_attempts = 5
        self.lockout_duration_min = 15

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        \"\"\"Authenticate user with email and password.\"\"\"
        # Rate limiting check
        if self._is_rate_limited(email):
            raise ValueError(f"Too many login attempts. Try again in {self.lockout_duration_min} min.")

        # Validate input
        if not email or not password:
            self._record_attempt(email)
            raise ValueError("Email and password required")

        # Query user
        db = get_db()
        user = await db.query_one("SELECT * FROM users WHERE email = ?", [email])

        if not user:
            self._record_attempt(email)
            raise ValueError("Invalid credentials")

        # Verify password
        if not bcrypt.checkpw(password.encode(), user.password_hash):
            self._record_attempt(email)
            raise ValueError("Invalid credentials")

        # Clear rate limit on success
        self._clear_attempts(email)
        return user
""",
                "nasa_compliant": True,
                "type_hints": True,
                "error_handling": True
            },
            quality_label=95.0,
            rationale="Secure implementation with rate limiting, parameterized queries, bcrypt, type hints"
        ))

        dataset = TrainingDataset(agent_id="coder", examples=examples[:min(size, 10)])
        dataset.split(train_ratio=0.8)
        return dataset

    def _generate_queen_example(self, index: int) -> TrainingExample:
        """Generate synthetic Queen example."""
        return TrainingExample(
            input_task=Task(
                id=f"train-queen-{index:03d}",
                type="orchestrate",
                description=f"Generic workflow {index}",
                payload={"workflow": {"objective": f"Task {index}", "steps": []}},
                priority=5
            ),
            expected_output={"workflow_id": f"train-queen-{index:03d}", "steps": []},
            quality_label=70.0,
            rationale="Synthetic example"
        )

    def _generate_tester_example(self, index: int) -> TrainingExample:
        """Generate synthetic Tester example."""
        return TrainingExample(
            input_task=Task(
                id=f"train-tester-{index:03d}",
                type="test",
                description=f"Test generation {index}",
                payload={"source_file": f"src/module_{index}.py", "test_type": "unit"},
                priority=5
            ),
            expected_output={"test_file": f"tests/test_module_{index}.py", "test_count": 5},
            quality_label=70.0,
            rationale="Synthetic example"
        )

    def save_dataset(self, dataset: TrainingDataset, filename: str = None):
        """Save dataset to JSON file."""
        if filename is None:
            filename = f"{dataset.agent_id}_training_dataset.json"

        output_path = self.output_dir / filename

        data = {
            "agent_id": dataset.agent_id,
            "total_examples": len(dataset.examples),
            "train_examples": len(dataset.train_split),
            "val_examples": len(dataset.val_split),
            "examples": [
                {
                    "input_task": {
                        "id": ex.input_task.id,
                        "type": ex.input_task.type,
                        "description": ex.input_task.description,
                        "payload": ex.input_task.payload,
                        "priority": ex.input_task.priority
                    },
                    "expected_output": ex.expected_output,
                    "quality_label": ex.quality_label,
                    "rationale": ex.rationale
                }
                for ex in dataset.examples
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Dataset saved to: {output_path}")
        print(f"  Total: {len(dataset.examples)} examples")
        print(f"  Train: {len(dataset.train_split)} examples")
        print(f"  Val: {len(dataset.val_split)} examples")


def create_dataset_generator(output_dir: str = "datasets") -> DatasetGenerator:
    """Factory function to create dataset generator."""
    return DatasetGenerator(output_dir=output_dir)
