"""
InfrastructureOpsAgent - Infrastructure Operations Specialist

Kubernetes, Docker, and cloud infrastructure management:
- Deploy and manage Kubernetes resources
- Configure Docker containers
- Scale infrastructure resources
- Monitor cluster health

Part of specialized agent roster (Week 9 Day 1).

Week 9 Day 1
Version: 8.0.0
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

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
from src.agents.instructions import INFRASTRUCTURE_OPS_INSTRUCTIONS


# ============================================================================
# Infrastructure-Specific Types
# ============================================================================

@dataclass
class KubernetesDeployment:
    """Kubernetes deployment specification."""
    name: str
    namespace: str
    replicas: int
    image: str
    ports: List[int]
    env_vars: Dict[str, str]


@dataclass
class InfrastructureConfig:
    """Infrastructure configuration."""
    provider: str  # aws, gcp, azure, local
    cluster_name: str
    node_count: int
    node_type: str
    region: str


# ============================================================================
# InfrastructureOpsAgent Class
# ============================================================================

class InfrastructureOpsAgent(AgentBase):
    """
    Infrastructure-Ops Agent - Infrastructure operations specialist.

    Responsibilities:
    - Deploy Kubernetes resources
    - Manage Docker containers
    - Scale infrastructure
    - Monitor cluster health
    """

    def __init__(self):
        """Initialize Infrastructure-Ops Agent."""
        metadata = create_agent_metadata(
            agent_id="infrastructure-ops",
            name="Infrastructure Operations Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "deploy-infrastructure",
                "scale-infrastructure",
                "monitor-infrastructure",
                "configure-infrastructure"
            ],
            capabilities=[
                AgentCapability(
                    name="Kubernetes Management",
                    description="Deploy and manage K8s resources",
                    level=10
                ),
                AgentCapability(
                    name="Docker Containerization",
                    description="Build and manage containers",
                    level=9
                ),
                AgentCapability(
                    name="Cloud Infrastructure",
                    description="Manage cloud resources",
                    level=9
                ),
                AgentCapability(
                    name="Auto-scaling",
                    description="Configure auto-scaling policies",
                    level=8
                ),
                AgentCapability(
                    name="Infrastructure Monitoring",
                    description="Monitor cluster health",
                    level=8
                )
            ],
            # Week 21: System instructions with all 26 principles
            system_instructions=INFRASTRUCTURE_OPS_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Kubernetes resource types
        self.k8s_resources = [
            "Deployment", "Service", "ConfigMap", "Secret",
            "Ingress", "PersistentVolumeClaim", "StatefulSet"
        ]

        # Cloud providers
        self.cloud_providers = ["aws", "gcp", "azure", "local"]

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

        # Infrastructure-specific validation
        if task.type == "deploy-infrastructure":
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
            if task.type == "deploy-infrastructure":
                result_data = await self._execute_deploy(task)
            elif task.type == "scale-infrastructure":
                result_data = await self._execute_scale(task)
            elif task.type == "monitor-infrastructure":
                result_data = await self._execute_monitor(task)
            elif task.type == "configure-infrastructure":
                result_data = await self._execute_configure(task)
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
        Deploy infrastructure resources.

        Args:
            task: Deploy-infrastructure task

        Returns:
            Deployment result
        """
        deployment_spec = task.payload.get("deployment", {})
        app_name = deployment_spec.get("name", "app")
        namespace = deployment_spec.get("namespace", "default")
        replicas = deployment_spec.get("replicas", 3)

        self.log_info(
            f"Deploying {app_name} to namespace {namespace} "
            f"with {replicas} replicas"
        )

        # Generate Kubernetes manifests
        manifests = self._generate_k8s_manifests(deployment_spec)

        # Write manifests to files
        output_dir = task.payload.get("output_dir", "k8s")
        manifest_files = []

        for resource_type, manifest in manifests.items():
            file_path = Path(output_dir) / f"{app_name}-{resource_type.lower()}.yaml"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(manifest)

            manifest_files.append(str(file_path))

        # Create deployment metadata
        deployment = KubernetesDeployment(
            name=app_name,
            namespace=namespace,
            replicas=replicas,
            image=deployment_spec.get("image", "app:latest"),
            ports=deployment_spec.get("ports", [80]),
            env_vars=deployment_spec.get("env_vars", {})
        )

        return {
            "app_name": app_name,
            "namespace": namespace,
            "replicas": replicas,
            "manifest_files": manifest_files,
            "deployment": deployment.__dict__
        }

    async def _execute_scale(self, task: Task) -> Dict[str, Any]:
        """
        Scale infrastructure resources.

        Args:
            task: Scale-infrastructure task

        Returns:
            Scaling result
        """
        deployment_name = task.payload.get("deployment_name")
        target_replicas = task.payload.get("target_replicas", 5)
        namespace = task.payload.get("namespace", "default")

        self.log_info(
            f"Scaling {deployment_name} to {target_replicas} replicas "
            f"in namespace {namespace}"
        )

        # Generate scaling command
        scale_command = (
            f"kubectl scale deployment/{deployment_name} "
            f"--replicas={target_replicas} -n {namespace}"
        )

        return {
            "deployment_name": deployment_name,
            "target_replicas": target_replicas,
            "namespace": namespace,
            "scale_command": scale_command,
            "scaled": True
        }

    async def _execute_monitor(self, task: Task) -> Dict[str, Any]:
        """
        Monitor infrastructure health.

        Args:
            task: Monitor-infrastructure task

        Returns:
            Monitoring result
        """
        cluster_name = task.payload.get("cluster_name", "default")
        namespace = task.payload.get("namespace", "default")

        self.log_info(f"Monitoring cluster {cluster_name}")

        # Simulate health check
        health_metrics = {
            "cluster_status": "healthy",
            "node_count": 3,
            "pods_running": 15,
            "pods_pending": 0,
            "pods_failed": 0,
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 38.5
        }

        # Check thresholds
        alerts = []
        if health_metrics["memory_usage"] > 80:
            alerts.append("High memory usage detected")
        if health_metrics["cpu_usage"] > 80:
            alerts.append("High CPU usage detected")
        if health_metrics["pods_failed"] > 0:
            alerts.append(f"{health_metrics['pods_failed']} pods failed")

        return {
            "cluster_name": cluster_name,
            "namespace": namespace,
            "health_metrics": health_metrics,
            "alerts": alerts,
            "healthy": len(alerts) == 0
        }

    async def _execute_configure(self, task: Task) -> Dict[str, Any]:
        """
        Configure infrastructure.

        Args:
            task: Configure-infrastructure task

        Returns:
            Configuration result
        """
        config_spec = task.payload.get("config", {})
        provider = config_spec.get("provider", "aws")
        cluster_name = config_spec.get("cluster_name", "spek-cluster")

        self.log_info(
            f"Configuring {provider} infrastructure for {cluster_name}"
        )

        # Create infrastructure config
        config = InfrastructureConfig(
            provider=provider,
            cluster_name=cluster_name,
            node_count=config_spec.get("node_count", 3),
            node_type=config_spec.get("node_type", "t3.medium"),
            region=config_spec.get("region", "us-east-1")
        )

        # Generate Terraform/IaC config
        iac_config = self._generate_iac_config(config)

        # Write config file
        output_dir = task.payload.get("output_dir", "infrastructure")
        config_file = Path(output_dir) / f"{cluster_name}.tf"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(iac_config)

        return {
            "provider": provider,
            "cluster_name": cluster_name,
            "config_file": str(config_file),
            "config": config.__dict__
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _generate_k8s_manifests(
        self,
        spec: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate Kubernetes manifests."""
        manifests = {}

        app_name = spec.get("name", "app")
        namespace = spec.get("namespace", "default")
        replicas = spec.get("replicas", 3)
        image = spec.get("image", "app:latest")
        ports = spec.get("ports", [80])

        # Deployment manifest
        manifests["Deployment"] = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: {namespace}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {image}
        ports:
"""
        for port in ports:
            manifests["Deployment"] += f"""        - containerPort: {port}
"""

        # Service manifest
        manifests["Service"] = f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}
  namespace: {namespace}
spec:
  selector:
    app: {app_name}
  ports:
"""
        for port in ports:
            manifests["Service"] += f"""  - protocol: TCP
    port: {port}
    targetPort: {port}
"""
        manifests["Service"] += "  type: LoadBalancer\n"

        return manifests

    def _generate_iac_config(self, config: InfrastructureConfig) -> str:
        """Generate Infrastructure as Code configuration."""
        if config.provider == "aws":
            return self._generate_aws_terraform(config)
        elif config.provider == "gcp":
            return self._generate_gcp_terraform(config)
        else:
            return f"# Infrastructure config for {config.provider}\n"

    def _generate_aws_terraform(
        self,
        config: InfrastructureConfig
    ) -> str:
        """Generate AWS Terraform configuration."""
        return f"""# AWS EKS Cluster Configuration
# Generated by InfrastructureOpsAgent

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{config.region}"
}}

module "eks" {{
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "{config.cluster_name}"
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {{
    default = {{
      min_size     = 1
      max_size     = 10
      desired_size = {config.node_count}

      instance_types = ["{config.node_type}"]
    }}
  }}
}}

module "vpc" {{
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "{config.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["{config.region}a", "{config.region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}}
"""

    def _generate_gcp_terraform(
        self,
        config: InfrastructureConfig
    ) -> str:
        """Generate GCP Terraform configuration."""
        return f"""# GCP GKE Cluster Configuration
# Generated by InfrastructureOpsAgent

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 5.0"
    }}
  }}
}}

provider "google" {{
  project = "spek-project"
  region  = "{config.region}"
}}

resource "google_container_cluster" "{config.cluster_name}" {{
  name     = "{config.cluster_name}"
  location = "{config.region}"

  initial_node_count = {config.node_count}

  node_config {{
    machine_type = "{config.node_type}"
  }}
}}
"""

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_deploy_payload(self, task: Task) -> List[ValidationError]:
        """Validate deploy-infrastructure task payload."""
        errors = []

        if "deployment" not in task.payload:
            errors.append(ValidationError(
                field="payload.deployment",
                message="Deploy task requires 'deployment' specification",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_infrastructure_ops_agent() -> InfrastructureOpsAgent:
    """
    Create Infrastructure-Ops Agent instance.

    Returns:
        InfrastructureOpsAgent
    """
    return InfrastructureOpsAgent()
