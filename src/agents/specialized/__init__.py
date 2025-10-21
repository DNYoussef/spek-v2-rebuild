"""
Specialized Agents (14 total - COMPLETE)

SPARC workflow agents (Day 4):
- architect: System architecture design
- pseudocode-writer: Algorithm design
- spec-writer: Requirements documentation
- integration-engineer: System integration

Development support agents (Day 5):
- debugger: Bug fixing and debugging
- docs-writer: Documentation generation
- devops: Deployment automation
- security-manager: Security validation
- cost-tracker: Budget monitoring

Quality and orchestration agents (Day 6):
- theater-detector: Mock code detection
- nasa-enforcer: NASA Rule 10 compliance
- fsm-analyzer: FSM validation
- orchestrator: Workflow orchestration
- planner: Task planning

Week 5 Days 4-6
Version: 8.0.0
"""

# Day 4 agents
from .ArchitectAgent import ArchitectAgent, create_architect_agent
from .PseudocodeWriterAgent import (PseudocodeWriterAgent, create_pseudocode_writer_agent)
from .SpecWriterAgent import SpecWriterAgent, create_spec_writer_agent
from .IntegrationEngineerAgent import (IntegrationEngineerAgent, create_integration_engineer_agent)

# Day 5 agents
from .DebuggerAgent import DebuggerAgent, create_debugger_agent
from .DocsWriterAgent import DocsWriterAgent, create_docs_writer_agent
from .DevOpsAgent import DevOpsAgent, create_devops_agent
from .SecurityManagerAgent import (SecurityManagerAgent, create_security_manager_agent)
from .CostTrackerAgent import CostTrackerAgent, create_cost_tracker_agent

# Day 6 agents
from .TheaterDetectorAgent import TheaterDetectorAgent, create_theater_detector_agent
from .NASAEnforcerAgent import NASAEnforcerAgent, create_nasa_enforcer_agent
from .FSMAnalyzerAgent import FSMAnalyzerAgent, create_fsm_analyzer_agent
from .OrchestratorAgent import OrchestratorAgent, create_orchestrator_agent
from .PlannerAgent import PlannerAgent, create_planner_agent

__all__ = [
    # Day 4
    "ArchitectAgent", "create_architect_agent",
    "PseudocodeWriterAgent", "create_pseudocode_writer_agent",
    "SpecWriterAgent", "create_spec_writer_agent",
    "IntegrationEngineerAgent", "create_integration_engineer_agent",
    # Day 5
    "DebuggerAgent", "create_debugger_agent",
    "DocsWriterAgent", "create_docs_writer_agent",
    "DevOpsAgent", "create_devops_agent",
    "SecurityManagerAgent", "create_security_manager_agent",
    "CostTrackerAgent", "create_cost_tracker_agent",
    # Day 6
    "TheaterDetectorAgent", "create_theater_detector_agent",
    "NASAEnforcerAgent", "create_nasa_enforcer_agent",
    "FSMAnalyzerAgent", "create_fsm_analyzer_agent",
    "OrchestratorAgent", "create_orchestrator_agent",
    "PlannerAgent", "create_planner_agent"
]
