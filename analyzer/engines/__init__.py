"""
Engines Module - Modular analysis engines

Contains specialized analysis engines:
- SyntaxAnalyzer: AST-based syntax analysis
- PatternDetector: Pattern and anti-pattern detection
- ComplianceValidator: Multi-standard compliance validation

Version: 6.0.0 (Week 2 Day 2)
"""

from .syntax_analyzer import SyntaxAnalyzer, create_syntax_analyzer
from .pattern_detector import PatternDetector, Pattern, create_pattern_detector
from .compliance_validator import ComplianceValidator, create_compliance_validator

__all__ = [
    "SyntaxAnalyzer",
    "create_syntax_analyzer",
    "PatternDetector",
    "Pattern",
    "create_pattern_detector",
    "ComplianceValidator",
    "create_compliance_validator",
]

__version__ = "6.0.0"
__version_info__ = (6, 0, 0)
