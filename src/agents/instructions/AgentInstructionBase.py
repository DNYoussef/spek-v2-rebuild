"""
Agent Instruction Framework - Base System Instructions

Embeds all 26 prompt engineering principles into agent communication.
Enforces quality in Queen→Princess→Drone hierarchy.

Week 21 (Post-DSPy Decision)
Version: 8.0.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AgentInstruction:
    """
    Complete system instruction for an agent.

    Embeds all 26 prompt engineering principles:
    1. Clarity & Specificity
    2. Role Assignment (Persona)
    3. Step-by-Step Reasoning (Chain of Thought)
    4. Examples (Few-Shot Learning) - via training data
    5. Output Format Specification
    6. Constraints & Boundaries
    7. Context Provision
    8. Error Prevention
    9. Incremental Prompting
    10. Avoid Leading Questions
    11. Specificity in Restrictions
    12. Task Complexity Acknowledgment
    13. Address Edge Cases
    14. Consistency in Terminology
    15. Explicit Assumptions
    16. Clarify Ambiguities
    17. Quality Over Speed
    18. Provide Feedback Loops
    19. Use Analogies When Helpful
    20. Test Understanding
    21. Iterative Refinement
    22. Avoid Overloading
    23. Regulatory Compliance (NASA Rule 10)
    24. Testing Requirements
    25. Security Considerations
    26. Performance Considerations
    """

    agent_id: str
    role_persona: str  # Principle 2: Role assignment
    expertise_areas: List[str]  # Principle 2: Specific expertise

    reasoning_process: List[str]  # Principle 3: Step-by-step thinking

    constraints: Dict[str, str]  # Principle 6: Boundaries
    output_format: str  # Principle 5: Structured output

    common_mistakes: List[str]  # Principle 8: Error prevention
    quality_checklist: List[str]  # Principle 17: Quality requirements

    edge_cases: List[str]  # Principle 13: Edge case handling
    security_requirements: List[str]  # Principle 25: Security
    performance_requirements: List[str]  # Principle 26: Performance

    nasa_compliance_notes: Optional[str] = None  # Principle 23: Regulatory
    examples: Optional[List[Dict]] = None  # Principle 4: Few-shot

    def to_prompt(self) -> str:
        """
        Convert instruction to full system prompt.

        Returns:
            Formatted system prompt with all principles embedded
        """
        sections = []

        # Principle 2: Role & Expertise
        sections.append(f"ROLE & PERSONA:\n{self.role_persona}\n")
        sections.append(f"EXPERTISE: {', '.join(self.expertise_areas)}\n")

        # Principle 3: Reasoning Process (Chain of Thought)
        sections.append("REASONING PROCESS (think step-by-step):")
        for i, step in enumerate(self.reasoning_process, 1):
            sections.append(f"  {i}. {step}")
        sections.append("")

        # Principle 6: Constraints & Boundaries
        sections.append("CONSTRAINTS:")
        for key, value in self.constraints.items():
            sections.append(f"  - {key}: {value}")
        sections.append("")

        # Principle 5: Output Format
        sections.append("OUTPUT FORMAT:")
        sections.append(self.output_format)
        sections.append("")

        # Principle 8: Error Prevention (Common Mistakes)
        sections.append("COMMON MISTAKES TO AVOID:")
        for mistake in self.common_mistakes:
            sections.append(f"  ✗ {mistake}")
        sections.append("")

        # Principle 17: Quality Checklist
        sections.append("QUALITY CHECKLIST (verify before responding):")
        for check in self.quality_checklist:
            sections.append(f"  ✓ {check}")
        sections.append("")

        # Principle 13: Edge Cases
        if self.edge_cases:
            sections.append("EDGE CASES TO CONSIDER:")
            for edge_case in self.edge_cases:
                sections.append(f"  ⚠ {edge_case}")
            sections.append("")

        # Principle 25: Security
        if self.security_requirements:
            sections.append("SECURITY REQUIREMENTS:")
            for req in self.security_requirements:
                sections.append(f"  \ud83d\udee1 {req}")
            sections.append("")

        # Principle 26: Performance
        if self.performance_requirements:
            sections.append("PERFORMANCE REQUIREMENTS:")
            for req in self.performance_requirements:
                sections.append(f"  \u26a1 {req}")
            sections.append("")

        # Principle 23: NASA Rule 10 Compliance
        if self.nasa_compliance_notes:
            sections.append("NASA RULE 10 COMPLIANCE:")
            sections.append(f"  {self.nasa_compliance_notes}")
            sections.append("")

        # Principle 4: Examples (if provided)
        if self.examples:
            sections.append("EXAMPLES:")
            for i, example in enumerate(self.examples, 1):
                sections.append(f"\n  Example {i}:")
                sections.append(f"    Input: {example.get('input', 'N/A')}")
                sections.append(f"    Output: {example.get('output', 'N/A')}")
                if 'rationale' in example:
                    sections.append(f"    Rationale: {example['rationale']}")
            sections.append("")

        return "\n".join(sections)

    def validate_response(self, response: Dict) -> tuple[bool, List[str]]:
        """
        Validate agent response against instruction quality criteria.

        Args:
            response: Agent response to validate

        Returns:
            (is_valid, list of validation errors)
        """
        errors = []

        # Basic structure validation
        if not isinstance(response, dict):
            errors.append("Response must be a dictionary")
            return (False, errors)

        # Add agent-specific validation in subclasses
        return (len(errors) == 0, errors)


def create_instruction(
    agent_id: str,
    role_persona: str,
    expertise_areas: List[str],
    reasoning_process: List[str],
    constraints: Dict[str, str],
    output_format: str,
    common_mistakes: List[str],
    quality_checklist: List[str],
    edge_cases: Optional[List[str]] = None,
    security_requirements: Optional[List[str]] = None,
    performance_requirements: Optional[List[str]] = None,
    nasa_compliance_notes: Optional[str] = None,
    examples: Optional[List[Dict]] = None
) -> AgentInstruction:
    """
    Factory function to create agent instruction.

    Ensures all 26 principles are considered.
    """
    return AgentInstruction(
        agent_id=agent_id,
        role_persona=role_persona,
        expertise_areas=expertise_areas,
        reasoning_process=reasoning_process,
        constraints=constraints,
        output_format=output_format,
        common_mistakes=common_mistakes,
        quality_checklist=quality_checklist,
        edge_cases=edge_cases or [],
        security_requirements=security_requirements or [],
        performance_requirements=performance_requirements or [],
        nasa_compliance_notes=nasa_compliance_notes,
        examples=examples
    )


# Export
__all__ = ['AgentInstruction', 'create_instruction']
