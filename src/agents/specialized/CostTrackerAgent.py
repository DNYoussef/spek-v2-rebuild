"""
CostTrackerAgent - Budget Monitoring Specialist

Tracks and optimizes resource costs:
- Monitor API usage and costs
- Track infrastructure expenses
- Predict future costs
- Generate cost optimization recommendations

Part of specialized agent roster (Week 5 Day 5).

Week 5 Day 5
Version: 8.0.0
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

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
from src.agents.instructions import COST_TRACKER_INSTRUCTIONS


# ============================================================================
# Cost-Tracker Specific Types
# ============================================================================

@dataclass
class CostEntry:
    """Single cost entry."""
    entry_id: str
    service: str  # claude, gemini, pinecone, docker, etc.
    cost_usd: float
    usage_units: float  # tokens, requests, hours, etc.
    timestamp: str


@dataclass
class CostReport:
    """Cost tracking report."""
    report_id: str
    period_start: str
    period_end: str
    total_cost_usd: float
    cost_by_service: Dict[str, float]
    budget_used_pct: float
    recommendations: List[str]


# ============================================================================
# CostTrackerAgent Class
# ============================================================================

class CostTrackerAgent(AgentBase):
    """
    Cost-Tracker Agent - Budget monitoring specialist.

    Responsibilities:
    - Track API and infrastructure costs
    - Monitor budget usage
    - Predict future costs
    - Generate cost optimization recommendations
    """

    def __init__(self):
        """Initialize Cost-Tracker Agent."""
        metadata = create_agent_metadata(
            agent_id="cost-tracker",
            name="Budget Monitoring Specialist",
            agent_type=AgentType.SPECIALIZED,
            supported_task_types=[
                "track-cost",
                "generate-cost-report",
                "predict-cost",
                "optimize-cost"
            ],
            capabilities=[
                AgentCapability(
                    name="Cost Tracking",
                    description="Track API and infrastructure costs",
                    level=10
                ),
                AgentCapability(
                    name="Budget Monitoring",
                    description="Monitor budget usage and alerts",
                    level=9
                ),
                AgentCapability(
                    name="Cost Prediction",
                    description="Predict future costs based on trends",
                    level=9
                ),
                AgentCapability(
                    name="Cost Optimization",
                    description="Generate cost optimization recommendations",
                    level=8
                ),
                AgentCapability(
                    name="Cost Reporting",
                    description="Generate comprehensive cost reports",
                    level=8
                )
            ]
        ,
            # Week 21: System instructions with all 26 prompt engineering principles
            system_instructions=COST_TRACKER_INSTRUCTIONS.to_prompt()
        )

        super().__init__(metadata=metadata)

        # Service pricing (USD per unit)
        self.pricing = {
            "claude": 0.00025,  # per 1K tokens
            "gemini": 0.0,      # free tier
            "pinecone": 0.096,  # per hour (pod-based)
            "docker": 0.01,     # per container-hour
            "github": 0.0       # free for public repos
        }

        # Monthly budget (USD)
        self.monthly_budget = 220.0  # From SPEC-v6-FINAL

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

        # Cost-Tracker specific validation
        if task.type == "track-cost":
            errors.extend(self._validate_track_payload(task))

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
            if task.type == "track-cost":
                result_data = await self._execute_track(task)
            elif task.type == "generate-cost-report":
                result_data = await self._execute_generate_report(task)
            elif task.type == "predict-cost":
                result_data = await self._execute_predict(task)
            elif task.type == "optimize-cost":
                result_data = await self._execute_optimize(task)
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

    async def _execute_track(self, task: Task) -> Dict[str, Any]:
        """
        Track cost entry.

        Args:
            task: Track-cost task

        Returns:
            Cost tracking result
        """
        service = task.payload.get("service", "claude")
        usage_units = task.payload.get("usage_units", 0.0)

        self.log_info(f"Tracking cost for {service}: {usage_units} units")

        # Calculate cost
        unit_price = self.pricing.get(service, 0.0)
        cost_usd = usage_units * unit_price

        # Create cost entry
        entry = CostEntry(
            entry_id=f"cost-{int(time.time())}",
            service=service,
            cost_usd=cost_usd,
            usage_units=usage_units,
            timestamp=datetime.now().isoformat()
        )

        return {
            "entry_id": entry.entry_id,
            "service": service,
            "cost_usd": cost_usd,
            "usage_units": usage_units,
            "unit_price": unit_price,
            "entry": entry.__dict__
        }

    async def _execute_generate_report(
        self,
        task: Task
    ) -> Dict[str, Any]:
        """Generate cost report."""
        period_days = task.payload.get("period_days", 30)

        self.log_info(f"Generating cost report for {period_days} days")

        # Calculate period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        # Simulate cost data
        cost_by_service = {
            "claude": 43.0,   # Primary LLM
            "gemini": 0.0,    # Free tier
            "pinecone": 0.0,  # Not yet deployed
            "docker": 0.0,    # Local development
            "github": 0.0     # Free tier
        }

        total_cost = sum(cost_by_service.values())
        budget_used_pct = (total_cost / self.monthly_budget) * 100

        # Generate recommendations
        recommendations = self._generate_recommendations(
            cost_by_service,
            budget_used_pct
        )

        # Create report
        report = CostReport(
            report_id=f"report-{int(time.time())}",
            period_start=start_date.isoformat(),
            period_end=end_date.isoformat(),
            total_cost_usd=total_cost,
            cost_by_service=cost_by_service,
            budget_used_pct=budget_used_pct,
            recommendations=recommendations
        )

        return {
            "report_id": report.report_id,
            "period_days": period_days,
            "total_cost_usd": total_cost,
            "budget_used_pct": budget_used_pct,
            "recommendation_count": len(recommendations),
            "report": report.__dict__
        }

    async def _execute_predict(self, task: Task) -> Dict[str, Any]:
        """Predict future costs."""
        forecast_days = task.payload.get("forecast_days", 30)

        self.log_info(f"Predicting costs for {forecast_days} days")

        # Simple linear projection
        current_monthly_cost = 43.0  # From v6-FINAL spec
        daily_cost = current_monthly_cost / 30

        predicted_cost = daily_cost * forecast_days

        return {
            "forecast_days": forecast_days,
            "predicted_cost_usd": predicted_cost,
            "daily_cost_usd": daily_cost,
            "budget_impact_pct": (predicted_cost / self.monthly_budget) * 100
        }

    async def _execute_optimize(self, task: Task) -> Dict[str, Any]:
        """Generate cost optimization recommendations."""
        self.log_info("Generating cost optimization recommendations")

        # Current costs
        current_costs = {
            "claude": 43.0,
            "gemini": 0.0,
            "total": 43.0
        }

        # Optimization strategies
        optimizations = [
            {
                "strategy": "Use Gemini for simple tasks",
                "potential_savings_usd": 15.0,
                "effort": "low"
            },
            {
                "strategy": "Implement caching for repeated queries",
                "potential_savings_usd": 10.0,
                "effort": "medium"
            },
            {
                "strategy": "Batch API requests",
                "potential_savings_usd": 5.0,
                "effort": "low"
            }
        ]

        total_savings = sum(opt["potential_savings_usd"] for opt in optimizations)

        return {
            "current_cost_usd": current_costs["total"],
            "potential_savings_usd": total_savings,
            "optimized_cost_usd": current_costs["total"] - total_savings,
            "optimization_count": len(optimizations),
            "optimizations": optimizations
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _generate_recommendations(
        self,
        cost_by_service: Dict[str, float],
        budget_used_pct: float
    ) -> List[str]:
        """Generate cost recommendations."""
        recommendations = []

        # Budget alerts
        if budget_used_pct > 80:
            recommendations.append(
                "ALERT: Budget usage exceeds 80%"
            )
        elif budget_used_pct > 50:
            recommendations.append(
                "WARNING: Budget usage exceeds 50%"
            )

        # Service-specific recommendations
        if cost_by_service.get("claude", 0) > 30:
            recommendations.append(
                "Consider using Gemini for simple tasks to reduce costs"
            )

        if cost_by_service.get("pinecone", 0) > 20:
            recommendations.append(
                "Review Pinecone pod configuration for optimization"
            )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "Cost usage is within acceptable limits"
            )

        return recommendations

    # ========================================================================
    # Validation Methods
    # ========================================================================

    def _validate_track_payload(self, task: Task) -> List[ValidationError]:
        """Validate track-cost task payload."""
        errors = []

        if "service" not in task.payload:
            errors.append(ValidationError(
                field="payload.service",
                message="Track task requires 'service' in payload",
                severity=10
            ))

        if "usage_units" not in task.payload:
            errors.append(ValidationError(
                field="payload.usage_units",
                message="Track task requires 'usage_units' in payload",
                severity=10
            ))

        return errors


# ============================================================================
# Factory Function
# ============================================================================

def create_cost_tracker_agent() -> CostTrackerAgent:
    """
    Create Cost-Tracker Agent instance.

    Returns:
        CostTrackerAgent
    """
    return CostTrackerAgent()
