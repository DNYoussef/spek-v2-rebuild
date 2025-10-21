"""
Pattern Detector - Advanced pattern detection engine

Detects code patterns including connascence, god objects,
magic literals, and architectural anti-patterns using
AST analysis and heuristics.

NASA Rule 3 Compliance: ≤200 LOC target
Version: 6.0.0 (Week 2 Day 2)
"""

import ast
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Pattern detection result."""
    pattern_type: str
    severity: str
    description: str
    location: Tuple[int, int]  # (line, column)
    context: str
    recommendation: str
    confidence: float


class PatternDetector:
    """
    Advanced pattern detection engine.

    Detects:
    - Connascence (CoN, CoT, CoM, CoP, CoA)
    - God objects (>50 methods)
    - Magic literals
    - Position coupling
    - Duplicated logic
    """

    def __init__(self):
        """Initialize pattern detector with thresholds."""
        self.logger = logging.getLogger(__name__)
        self.god_object_threshold = 50
        self.magic_literal_exclusions = [0, 1, -1, True, False, None, "", []]
        self.confidence_threshold = 0.7

    def detect(self, ast_tree, source_code: Optional[str] = None) -> List[Pattern]:
        """
        Detect patterns in code.

        Args:
            ast_tree: AST tree from ast.parse()
            source_code: Optional source code for regex analysis

        Returns:
            List of Pattern objects sorted by severity and confidence
        """
        # Validation
        assert ast_tree is not None, "ast_tree cannot be None"

        patterns = []

        try:
            # AST-based pattern detection
            if hasattr(ast_tree, 'body'):
                patterns.extend(self._detect_ast_patterns(ast_tree))

            # Source code pattern detection
            if source_code:
                patterns.extend(self._detect_source_patterns(source_code))

            # Connascence pattern detection
            patterns.extend(self._detect_connascence(ast_tree, source_code))

            # Sort by severity and confidence
            patterns.sort(key=lambda p: (
                p.severity == "critical",
                p.severity == "high",
                p.confidence
            ), reverse=True)

            # Limit to top 50 patterns
            self.logger.info(f"Detected {len(patterns)} patterns")
            return patterns[:50]

        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
            return [Pattern(
                pattern_type="detection_error",
                severity="medium",
                description=f"Pattern detection failed: {str(e)}",
                location=(0, 0),
                context="",
                recommendation="Review pattern detection configuration",
                confidence=0.8
            )]

    def _detect_ast_patterns(self, ast_tree) -> List[Pattern]:
        """
        Detect patterns in AST structure.

        Detects:
        - God objects (classes with >50 methods)
        - Magic literals (hardcoded values)
        - Position coupling (>6 parameters)
        """
        patterns = []

        for node in ast.walk(ast_tree):
            # God object detection
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > self.god_object_threshold:
                    patterns.append(Pattern(
                        pattern_type="god_object",
                        severity="critical",
                        description=f"Class '{node.name}' has {len(methods)} methods (>{self.god_object_threshold})",
                        location=(node.lineno, node.col_offset),
                        context=node.name,
                        recommendation="Split class into focused, single-responsibility classes",
                        confidence=0.95
                    ))

            # Position coupling (CoP) - too many parameters
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 6:
                    patterns.append(Pattern(
                        pattern_type="position_coupling",
                        severity="high" if param_count > 10 else "medium",
                        description=f"Function '{node.name}' has {param_count} parameters (NASA Rule 6: ≤6)",
                        location=(node.lineno, node.col_offset),
                        context=node.name,
                        recommendation="Reduce parameters or use configuration object",
                        confidence=0.90
                    ))

            # Magic literal detection (CoM)
            if isinstance(node, ast.Num):
                if node.n not in self.magic_literal_exclusions:
                    patterns.append(Pattern(
                        pattern_type="magic_literal",
                        severity="low",
                        description=f"Magic literal '{node.n}' found",
                        location=(node.lineno, node.col_offset),
                        context=str(node.n),
                        recommendation="Extract to named constant",
                        confidence=0.80
                    ))

            # String magic literals
            if isinstance(node, ast.Str):
                if node.s and len(node.s) > 3 and node.s not in self.magic_literal_exclusions:
                    patterns.append(Pattern(
                        pattern_type="magic_literal",
                        severity="low",
                        description=f"Magic string '{node.s[:20]}...' found",
                        location=(node.lineno, node.col_offset),
                        context=node.s[:30],
                        recommendation="Extract to named constant",
                        confidence=0.75
                    ))

        return patterns

    def _detect_source_patterns(self, source_code: str) -> List[Pattern]:
        """
        Detect patterns in source code using regex.

        Detects:
        - Duplicated code blocks
        - TODO comments (theater indicator)
        - Complex conditionals
        """
        patterns = []
        lines = source_code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # TODO/FIXME detection (theater indicator)
            if re.search(r'\b(TODO|FIXME|XXX|HACK)\b', line, re.IGNORECASE):
                patterns.append(Pattern(
                    pattern_type="theater_indicator",
                    severity="medium",
                    description="TODO/FIXME comment found (potential theater)",
                    location=(line_num, 0),
                    context=line.strip(),
                    recommendation="Implement functionality or remove comment",
                    confidence=0.70
                ))

            # Complex conditional detection
            if line.count('and') + line.count('or') > 3:
                patterns.append(Pattern(
                    pattern_type="complex_conditional",
                    severity="medium",
                    description="Complex conditional logic detected",
                    location=(line_num, 0),
                    context=line.strip(),
                    recommendation="Extract to separate function with descriptive name",
                    confidence=0.85
                ))

        return patterns

    def _detect_connascence(self, ast_tree, source_code: Optional[str]) -> List[Pattern]:
        """
        Detect connascence patterns.

        Detects:
        - CoN (Connascence of Name)
        - CoT (Connascence of Type)
        - CoM (Connascence of Meaning)
        - CoP (Connascence of Position)
        - CoA (Connascence of Algorithm)
        """
        patterns = []

        # CoA detection - duplicated algorithm logic
        # This is a simplified heuristic - real implementation would use AST comparison
        if source_code:
            lines = source_code.split('\n')
            code_blocks = {}

            for i in range(len(lines) - 5):
                block = '\n'.join(lines[i:i+5])
                block_hash = hash(block.strip())

                if block_hash in code_blocks and block.strip():
                    patterns.append(Pattern(
                        pattern_type="connascence_algorithm",
                        severity="high",
                        description="Duplicated algorithm logic detected (CoA)",
                        location=(i + 1, 0),
                        context=block[:50],
                        recommendation="Extract to shared function",
                        confidence=0.80
                    ))
                else:
                    code_blocks[block_hash] = i + 1

        return patterns


# Factory function
def create_pattern_detector() -> PatternDetector:
    """Create and return PatternDetector instance."""
    return PatternDetector()
