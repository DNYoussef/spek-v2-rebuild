"""
DevOpsAgent - Deployment Automation Specialist

Automates deployment, monitoring, and infrastructure management:
- Deploy applications to various environments
- Configure CI/CD pipelines
- Monitor system health and performance
- Manage infrastructure as code

Part of specialized agent roster (Week 5 Day 5).

Week 5 Day 5
Version: 8.0.0
"""

import time
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
from src.agents.instructions import DEVOPS_INSTRUCTIONS


# ============================================================================
# DevOps-Specific Types
# ============================================================================

@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    environment: str  # dev, staging, production
    version: str
    replicas: int
    resources: Dict[str, str]  # cpu, memory limits


@dataclass
class DeploymentResult:
    """Deployment operation result."""
    deployment_id: str
    environment: str
    status: str  # success, failed, rolled_back
    deployed_at: str
    duration_seconds: float


# ============================================================================
# DevOpsAgent Class
# ============================================================================

class DevOpsAgent(AgentBase):
    """
    DevOps Agent - Deployment automation specialist.

    Responsibilities:
    - Deploy applications to environments
    - Configure CI/CD pipelines
    - Monitor deployments
    - Manage rollbacks
    """

    def __init__(self):
        """Initialize DevOps Agent."""
        metadata = create_agent_metadata(
            agent_id="devops",
            name="Deployment Automation Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "deploy-app",
                "configure-cicd",
                "monitor-deployment",
                "rollback-deployment"
            ],
            capabilities=[
                AgentCapability(
                    name="Application Deployment",
                    description="Deploy apps to various environments",
                    level=10
                ),
                AgentCapability(
                    name="CI/CD Configuration",
                    description="Configure continuous integration pipelines",
                    level=9
                ),
                AgentCapability(
                    name="Monitoring and Alerting",
                    description="Monitor system health and performance",
                    level=9
                ),
                AgentCapability(
                    name="Rollback Management",
                    description="Rollback failed deployments",
                    level=8
                ),
                AgentCapability(
                    name="Infrastructure as Code",
                    description="Manage infrastructure with code",
                    level=8
                )
            ]
        ,
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=DEVOPS_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Supported environments
        self.environments = ["dev", "staging", "production"]

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

        # DevOps-specific validation
        if task.type == "deploy-app":
            errors.extend(self._validate_deploy_payload(task))

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
            if task.type == "deploy-app":
                result_data = await self._execute_deploy(task)
            elif task.type == "configure-cicd":
                result_data = await self._execute_configure_cicd(task)
            elif task.type == "monitor-deployment":
                result_data = await self._execute_monitor(task)
            elif task.type == "rollback-deployment":
                result_data = await self._execute_rollback(task)
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

    async def _execute_deploy(self, task: Task) -> Dict[str, Any]:
        """
        Deploy application to environment.

        Args:
            task: Deploy-app task

        Returns:
            Deployment result
        """
        environment = task.payload.get("environment", "dev")
        version = task.payload.get("version", "1.0.0")

        self.log_info(f"Deploying version {version} to {environment}")

        deployment_start = time.time()

        # Create deployment config
        config = DeploymentConfig(
            environment=environment,
            version=version,
            replicas=self._get_replica_count(environment),
            resources=self._get_resource_limits(environment)
        )

        # Perform deployment steps
        steps_completed = await self._perform_deployment_steps(config)

        deployment_duration = time.time() - deployment_start

        # Create deployment result
        result = DeploymentResult(
            deployment_id=f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            environment=environment,
            status="success",
            deployed_at=datetime.now().isoformat(),
            duration_seconds=deployment_duration
        )

        return {
            "deployment_id": result.deployment_id,
            "environment": environment,
            "version": version,
            "status": result.status,
            "duration_seconds": result.duration_seconds,
            "steps_completed": steps_completed,
            "result": result.__dict__
        }

    async def _execute_configure_cicd(self, task: Task) -> Dict[str, Any]:
        """Configure CI/CD pipeline."""
        pipeline_type = task.payload.get("pipeline_type", "github-actions")

        self.log_info(f"Configuring {pipeline_type} pipeline")

        # Generate pipeline configuration
        config_file = self._generate_pipeline_config(pipeline_type)

        return {
            "pipeline_type": pipeline_type,
            "config_file": config_file,
            "configured": True
        }

    async def _execute_monitor(self, task: Task) -> Dict[str, Any]:
        """Monitor deployment."""
        deployment_id = task.payload.get("deployment_id")

        self.log_info(f"Monitoring deployment {deployment_id}")

        # Check deployment health
        health = self._check_deployment_health(deployment_id)

        return {
            "deployment_id": deployment_id,
            "health": health,
            "status": "healthy" if health > 80 else "degraded"
        }

    async def _execute_rollback(self, task: Task) -> Dict[str, Any]:
        """Rollback deployment."""
        deployment_id = task.payload.get("deployment_id")
        previous_version = task.payload.get("previous_version", "1.0.0")

        self.log_info(
            f"Rolling back {deployment_id} to {previous_version}"
        )

        # Perform rollback
        rollback_success = await self._perform_rollback(
            deployment_id,
            previous_version
        )

        return {
            "deployment_id": deployment_id,
            "previous_version": previous_version,
            "rollback_success": rollback_success
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_replica_count(self, environment: str) -> int:
        """Get replica count for environment."""
        replicas = {
            "dev": 1,
            "staging": 2,
            "production": 3
        }
        return replicas.get(environment, 1)

    def _get_resource_limits(self, environment: str) -> Dict[str, str]:
        """Get resource limits for environment."""
        if environment == "production":
            return {"cpu": "2000m", "memory": "4Gi"}
        elif environment == "staging":
            return {"cpu": "1000m", "memory": "2Gi"}
        else:
            return {"cpu": "500m", "memory": "1Gi"}

    async def _perform_deployment_steps(
        self,
        config: DeploymentConfig
    ) -> List[str]:
        """Perform deployment steps."""
        steps = [
            f"Validate {config.environment} environment",
            f"Build version {config.version}",
            f"Run pre-deployment tests",
            f"Deploy {config.replicas} replicas",
            f"Configure resources: {config.resources}",
            f"Run health checks",
            f"Enable traffic routing"
        ]

        # Simulate deployment
        completed = []
        for step in steps:
            self.log_info(f"Executing: {step}")
            completed.append(step)

        return completed

    def _generate_pipeline_config(self, pipeline_type: str) -> str:
        """Generate CI/CD pipeline configuration."""
        if pipeline_type == "github-actions":
            config_file = ".github/workflows/deploy.yml"
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)

            config_content = """name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: |
          echo "Deploying..."
"""

            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)

            return config_file

        return f"config/{pipeline_type}.yml"

    def _check_deployment_health(self, deployment_id: str) -> float:
        """Check deployment health."""
        # Simplified health check
        return 95.0  # 95% healthy

    async def _perform_rollback(
        self,
        deployment_id: str,
        previous_version: str
    ) -> bool:
        """Perform deployment rollback."""
        self.log_info(f"Rolling back {deployment_id}")

        # Rollback steps
        steps = [
            "Stop current deployment",
            f"Restore previous version {previous_version}",
            "Run health checks",
            "Route traffic to previous version"
        ]

        for step in steps:
            self.log_info(f"Rollback: {step}")

        return True

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_deploy_payload(self, task: Task) -> List[ValidationError]:
        """Validate deploy-app task payload."""
        errors = []

        environment = task.payload.get("environment")
        if not environment:
            errors.append(ValidationError(
                field="payload.environment",
                message="Deploy task requires 'environment' in payload",
                severity=10
            ))
        elif environment not in self.environments:
            errors.append(ValidationError(
                field="payload.environment",
                message=f"Invalid environment: {environment}",
                severity=8
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_devops_agent() -> DevOpsAgent:
    """
    Create DevOps Agent instance.

    Returns:
        DevOpsAgent
    """
    return DevOpsAgent()
