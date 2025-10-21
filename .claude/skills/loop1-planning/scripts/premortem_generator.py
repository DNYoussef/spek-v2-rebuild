#!/usr/bin/env python3
"""
Premortem Generator - Calculates risk scores and implements GO/NO-GO logic

Atomic skill helper for Loop 1 Planning phase.
Implements risk assessment and decision logic from SPEK methodology.

VERSION: 1.0.0
USAGE: python premortem_generator.py --risks risks.json
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """Risk severity levels."""
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low


class Decision(Enum):
    """Launch decision states."""
    GO = "GO"
    CAUTION = "CAUTION"
    NO_GO = "NO_GO"


class PremorteMGenerator:
    """Generates premortem analysis with risk scoring."""

    # Risk weights from SPEK methodology
    RISK_WEIGHTS = {
        RiskLevel.P0: 500,
        RiskLevel.P1: 200,
        RiskLevel.P2: 50,
        RiskLevel.P3: 10
    }

    # Decision thresholds
    THRESHOLDS = {
        Decision.GO: 2000,
        Decision.CAUTION: 3500,
        Decision.NO_GO: 3501
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize premortem generator.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir or Path.cwd() / "premortem"
        self.output_dir.mkdir(exist_ok=True)

    def calculate_risk_score(self, risks: List[Dict[str, Any]]) -> int:
        """
        Calculate total risk score.

        Args:
            risks: List of risk dictionaries

        Returns:
            Total risk score
        """
        total = 0
        for risk in risks:
            try:
                level = RiskLevel(risk.get("level", "P3"))
                count = int(risk.get("count", 1))
                total += self.RISK_WEIGHTS[level] * count
            except (ValueError, KeyError) as e:
                print(f"Warning: Invalid risk entry: {risk} ({e})")
        return total

    def determine_decision(self, score: int) -> Decision:
        """
        Determine GO/CAUTION/NO-GO decision.

        Args:
            score: Total risk score

        Returns:
            Decision enum
        """
        if score <= self.THRESHOLDS[Decision.GO]:
            return Decision.GO
        elif score <= self.THRESHOLDS[Decision.CAUTION]:
            return Decision.CAUTION
        else:
            return Decision.NO_GO

    def calculate_confidence(self, score: int) -> float:
        """
        Calculate confidence percentage.

        Args:
            score: Risk score

        Returns:
            Confidence as percentage (0-100)
        """
        max_score = 10000  # Theoretical maximum
        confidence = max(0, min(100, 100 - (score / max_score * 100)))
        return round(confidence, 1)

    def analyze_risks(
        self, risks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform complete risk analysis.

        Args:
            risks: List of risk dictionaries

        Returns:
            Dict with analysis results
        """
        try:
            score = self.calculate_risk_score(risks)
            decision = self.determine_decision(score)
            confidence = self.calculate_confidence(score)

            # Count by severity
            counts = {level.value: 0 for level in RiskLevel}
            for risk in risks:
                level = risk.get("level", "P3")
                counts[level] = counts.get(level, 0) + risk.get("count", 1)

            return {
                "success": True,
                "score": score,
                "decision": decision.value,
                "confidence": confidence,
                "risk_counts": counts,
                "timestamp": datetime.now().isoformat(),
                "total_risks": len(risks)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_report(
        self, risks: List[Dict[str, Any]], version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Generate premortem report.

        Args:
            risks: List of risks
            version: Version number

        Returns:
            Dict with report result
        """
        analysis = self.analyze_risks(risks)
        if not analysis["success"]:
            return analysis

        report = self._format_report(analysis, risks, version)
        output_file = self.output_dir / f"PREMORTEM-v{version}.md"

        try:
            output_file.write_text(report, encoding="utf-8")
            return {
                "success": True,
                "report_file": str(output_file),
                "analysis": analysis
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _format_report(
        self, analysis: Dict[str, Any], risks: List[Dict[str, Any]], version: str
    ) -> str:
        """Format premortem report."""
        return f"""# Pre-Mortem Analysis v{version}

## Risk Summary

**Total Risk Score**: {analysis['score']}
**Decision**: {analysis['decision']}
**Confidence**: {analysis['confidence']}%
**Generated**: {analysis['timestamp']}

## Risk Breakdown

{self._format_risk_breakdown(analysis['risk_counts'])}

## Decision Rationale

{self._get_decision_rationale(analysis['decision'], analysis['score'])}

## Risk Details

{self._format_risk_details(risks)}
"""

    def _format_risk_breakdown(self, counts: Dict[str, int]) -> str:
        """Format risk breakdown section."""
        lines = []
        for level in ["P0", "P1", "P2", "P3"]:
            count = counts.get(level, 0)
            weight = self.RISK_WEIGHTS[RiskLevel(level)]
            total = count * weight
            lines.append(f"- **{level}**: {count} risks × {weight} = {total}")
        return "\n".join(lines)

    def _get_decision_rationale(self, decision: str, score: int) -> str:
        """Get decision rationale text."""
        if decision == "GO":
            return f"Risk score {score} is within acceptable range (≤2000). Project approved."
        elif decision == "CAUTION":
            return f"Risk score {score} requires mitigation (2001-3500). Proceed with caution."
        else:
            return f"Risk score {score} exceeds threshold (>3500). Project requires revision."

    def _format_risk_details(self, risks: List[Dict[str, Any]]) -> str:
        """Format risk details section."""
        lines = []
        for i, risk in enumerate(risks, 1):
            lines.append(f"### Risk {i}: {risk.get('title', 'Untitled')}")
            lines.append(f"**Level**: {risk.get('level', 'P3')}")
            lines.append(f"**Description**: {risk.get('description', 'N/A')}")
            lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    generator = PremorteMGenerator()

    example_risks = [
        {"level": "P1", "count": 2, "title": "Database migration", "description": "Schema changes"},
        {"level": "P2", "count": 5, "title": "API changes", "description": "Breaking changes"},
        {"level": "P3", "count": 8, "title": "Documentation", "description": "Outdated docs"}
    ]

    result = generator.generate_report(example_risks, version="1.0")
    print(json.dumps(result, indent=2))
