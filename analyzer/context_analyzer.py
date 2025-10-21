from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple, Callable, Set

from analyzer.constants.thresholds import MAXIMUM_FILE_LENGTH_LINES, MAXIMUM_GOD_OBJECTS_ALLOWED, MAXIMUM_NESTED_DEPTH, MAXIMUM_RETRY_ATTEMPTS

"""Provides context classification and domain-specific analysis for accurate
god object detection and connascence analysis. Reduces false positives by
understanding the purpose and domain of code structures.
"""

import ast
from dataclasses import dataclass
from enum import Enum
import re
from typing import Dict, List, Optional, Set

class ClassContext(Enum):
    """Classification of class contexts for domain-specific analysis."""

    CONFIG = "config"  # Configuration classes
    DATA_MODEL = "data_model"  # Data transfer objects, models
    API_CONTROLLER = "api_controller"  # REST controllers, handlers
    UTILITY = "utility"  # Helper/utility classes
    BUSINESS_LOGIC = "business_logic"  # Core business logic
    FRAMEWORK = "framework"  # Framework/library code
    TEST = "test"  # Test classes
    INFRASTRUCTURE = "infrastructure"  # Database, messaging, etc.
    UNKNOWN = "unknown"  # Unable to classify

class ResponsibilityType(Enum):
    """Types of responsibilities for cohesion analysis."""

    DATA_MANAGEMENT = "data_management"
    BUSINESS_RULE = "business_rule"
    COORDINATION = "coordination"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    PERSISTENCE = "persistence"
    COMMUNICATION = "communication"
    CONFIGURATION = "configuration"

@dataclass
class ClassAnalysis:
    """Complete analysis of a class including context and responsibilities."""

    name: str
    context: ClassContext
    method_count: int
    lines_of_code: int
    responsibilities: Set[ResponsibilityType]
    cohesion_score: float
    god_object_threshold: int
    god_object_reason: Optional[str] = None
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

@dataclass
class MethodAnalysis:
    """Analysis of individual methods for responsibility tracking."""

    name: str
    lines_of_code: int
    complexity_score: float
    responsibilities: Set[ResponsibilityType]
    parameter_count: int
    return_complexity: int

class ContextAnalyzer:
    """Analyzes code context to provide domain-specific thresholds and rules."""

    def __init__(self):
        # Context classification patterns
        self.config_indicators = {
            "name_patterns": [r".*[Cc]onfig.*", r".*[Ss]ettings?.*", r".*[Pp]roperties.*", r".*[Cc]onstants.*"],
            "method_patterns": [r"get_.*", r"set_.*", r"load_.*", r"save_.*", r"configure_.*"],
            "base_classes": ["Config", "Settings", "BaseConfig", "ConfigParser"],
            "imports": ["configparser", "settings", "config", "dynaconf"],
        }

        self.data_model_indicators = {
            "name_patterns": [r".*[Mm]odel.*", r".*[Dd][Tt][Oo].*", r".*[Ee]ntity.*", r".*[Dd]ata.*"],
            "method_patterns": [r"to_dict", r"from_dict", r"to_json", r"from_json", r"serialize", r"deserialize"],
            "base_classes": ["BaseModel", "Model", "Entity", "DTO", "DataClass"],
            "imports": ["pydantic", "dataclasses", "marshmallow", "sqlalchemy"],
        }

        self.api_controller_indicators = {
            "name_patterns": [r".*[Cc]ontroller.*", r".*[Hh]andler.*", r".*[Vv]iew.*", r".*[Aa][Pp][Ii].*"],
            "method_patterns": [r"get", r"post", r"put", r"delete", r"patch", r"handle_.*"],
            "base_classes": ["APIView", "Controller", "Handler", "Resource"],
            "imports": ["flask", "django", "fastapi", "tornado", "aiohttp"],
        }

        self.utility_indicators = {
            "name_patterns": [r".*[Uu]til.*", r".*[Hh]elper.*", r".*[Tt]ool.*", r".*[Uu]tility.*"],
            "method_patterns": [r"format_.*", r"parse_.*", r"convert_.*", r"transform_.*"],
            "base_classes": ["Utility", "Helper", "Tool"],
            "static_methods_ratio": 0.5,  # More than 50% static methods
        }

        # Dynamic threshold configuration
        self.context_thresholds = {
            ClassContext.CONFIG: {
                "method_threshold": 30,  # Config classes can have many getters/setters
                "loc_threshold": 800,  # Higher LOC acceptable for config
                "parameter_threshold": 8,  # Config methods may have many parameters
            },
            ClassContext.DATA_MODEL: {
                "method_threshold": 25,  # Models can have many properties
                "loc_threshold": 400,  # Focus on data cohesion, not LOC
                "parameter_threshold": 12,  # Constructor parameters
            },
            ClassContext.API_CONTROLLER: {
                "method_threshold": 20,  # One method per endpoint is reasonable
                "loc_threshold": 600,  # Controllers coordinate, may be longer
                "parameter_threshold": 6,  # HTTP methods should be simple
            },
            ClassContext.UTILITY: {
                "method_threshold": 40,  # Utility classes can have many helpers
                "loc_threshold": 1000,  # Utilities are collections of functions
                "parameter_threshold": 8,  # Utility functions may need more params
            },
            ClassContext.BUSINESS_LOGIC: {
                "method_threshold": 15,  # Strict for business logic
                "loc_threshold": 300,  # Keep business logic focused
                "parameter_threshold": MAXIMUM_NESTED_DEPTH,  # Business methods should be simple
            },
            ClassContext.FRAMEWORK: {
                "method_threshold": 50,  # Framework classes can be large
                "loc_threshold": 1200,  # Framework complexity acceptable
                "parameter_threshold": 10,  # Framework flexibility needs parameters
            },
            ClassContext.INFRASTRUCTURE: {
                "method_threshold": MAXIMUM_GOD_OBJECTS_ALLOWED,  # Database/messaging classes
                "loc_threshold": 600,  # Infrastructure coordination
                "parameter_threshold": 8,  # Connection parameters, etc.
            },
            ClassContext.TEST: {
                "method_threshold": 40,  # Test classes can have many test methods
                "loc_threshold": 800,  # Test files can be long
                "parameter_threshold": 10,  # Test methods may need many parameters
            },
            ClassContext.UNKNOWN: {
                "method_threshold": 18,  # Conservative default
                "loc_threshold": MAXIMUM_FILE_LENGTH_LINES,  # Original threshold
                "parameter_threshold": 6,  # NASA compliance
            },
        }

    def analyze_class_context(self, class_node: ast.ClassDef, source_lines: List[str], file_path: str) -> ClassAnalysis:
        """Perform comprehensive context analysis of a class."""

        # Basic metrics
        method_count = self._count_methods(class_node)
        loc = self._calculate_lines_of_code(class_node, source_lines)

        # Classify context
        context = self._classify_class_context(class_node, source_lines, file_path)

        # Analyze responsibilities and cohesion
        methods = self._analyze_methods(class_node, source_lines)
        responsibilities = self._identify_responsibilities(class_node, methods)
        cohesion_score = self._calculate_cohesion(methods, responsibilities)

        # Get context-specific threshold
        thresholds = self.context_thresholds[context]
        god_object_threshold = thresholds["method_threshold"]

        # Determine if this is a god object with context-aware reasoning
        god_object_reason = self._assess_god_object_with_context(
            class_node.name, context, method_count, loc, cohesion_score, thresholds
        )

        # Generate context-specific recommendations
        recommendations = self._generate_recommendations(context, method_count, loc, cohesion_score, responsibilities)

        return ClassAnalysis(
            name=class_node.name,
            context=context,
            method_count=method_count,
            lines_of_code=loc,
            responsibilities=responsibilities,
            cohesion_score=cohesion_score,
            god_object_threshold=god_object_threshold,
            god_object_reason=god_object_reason,
            recommendations=recommendations,
        )

    def _classify_class_context(
        self, class_node: ast.ClassDef, source_lines: List[str], file_path: str
    ) -> ClassContext:
        """Classify the context/domain of a class using multiple indicators."""

        scores = {context: 0 for context in ClassContext}

        # File path indicators
        path_lower = file_path.lower()
        if any(term in path_lower for term in ["test", "spec"]):
            scores[ClassContext.TEST] += 3
        elif any(term in path_lower for term in ["config", "settings"]):
            scores[ClassContext.CONFIG] += 2
        elif any(term in path_lower for term in ["model", "entity", "dto"]):
            scores[ClassContext.DATA_MODEL] += 2
        elif any(term in path_lower for term in ["api", "controller", "handler", "view"]):
            scores[ClassContext.API_CONTROLLER] += 2
        elif any(term in path_lower for term in ["util", "helper", "tool"]):
            scores[ClassContext.UTILITY] += 2
        elif any(term in path_lower for term in ["db", "database", "persistence", "repository"]):
            scores[ClassContext.INFRASTRUCTURE] += 2

        # Class name analysis
        class_name = class_node.name.lower()
        self._score_class_name_patterns(class_name, scores)

        # Base class analysis
        for base in class_node.bases:
            base_name = ast.unparse(base) if hasattr(ast, "unparse") else str(base)
            self._score_base_class(base_name, scores)

        # Method pattern analysis
        methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef)]
        for method in methods:
            method_name = method.name.lower()
            self._score_method_patterns(method_name, scores)

        # Static method ratio for utilities
        if methods:
            static_methods = len(
                [
                    m
                    for m in methods
                    if any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in m.decorator_list)
                ]
            )
            static_ratio = static_methods / len(methods)
            if static_ratio >= self.utility_indicators["static_methods_ratio"]:
                scores[ClassContext.UTILITY] += 2

        # Business logic is default for substantial classes with mixed responsibilities
        if max(scores.values()) == 0 and len(methods) > 5:
            scores[ClassContext.BUSINESS_LOGIC] += 1

        # Return the highest scoring context
        best_context = max(scores.items(), key=lambda x: x[1])
        return best_context[0] if best_context[1] > 0 else ClassContext.UNKNOWN

    def _score_class_name_patterns(self, class_name, scores):
        for context, indicators in [
            (ClassContext.CONFIG, self.config_indicators),
            (ClassContext.DATA_MODEL, self.data_model_indicators),
            (ClassContext.API_CONTROLLER, self.api_controller_indicators),
            (ClassContext.UTILITY, self.utility_indicators),
        ]:
            for pattern in indicators["name_patterns"]:
                if re.match(pattern, class_name):
                    scores[context] += 2
                    break

    def _score_base_class(self, base_name, scores):
        for context, indicators in [
            (ClassContext.CONFIG, self.config_indicators),
            (ClassContext.DATA_MODEL, self.data_model_indicators),
            (ClassContext.API_CONTROLLER, self.api_controller_indicators),
            (ClassContext.UTILITY, self.utility_indicators),
        ]:
            if base_name in indicators["base_classes"]:
                scores[context] += 3

    def _score_method_patterns(self, method_name, scores):
        for context, indicators in [
            (ClassContext.CONFIG, self.config_indicators),
            (ClassContext.DATA_MODEL, self.data_model_indicators),
            (ClassContext.API_CONTROLLER, self.api_controller_indicators),
            (ClassContext.UTILITY, self.utility_indicators),
        ]:
            for pattern in indicators["method_patterns"]:
                if re.match(pattern, method_name):
                    scores[context] += 1
                    break

    def _assess_context_specific_issues(self, context, method_count, loc, cohesion_score):
        if context == ClassContext.CONFIG:
            if cohesion_score < 0.2 and method_count > 40:
                return "Configuration class lacks cohesion with excessive methods"
            if method_count > 50:
                return "Configuration class has too many methods even for config context"
        elif context == ClassContext.DATA_MODEL:
            if method_count > 30 and cohesion_score < 0.5:
                return "Data model has too many disparate operations"
        elif context == ClassContext.API_CONTROLLER:
            if method_count > 25:
                return "API controller handling too many endpoints"
        elif context == ClassContext.UTILITY:
            if method_count > 50 and cohesion_score < 0.2:
                return "Utility class is too broad and unfocused"
        elif context == ClassContext.BUSINESS_LOGIC:
            if method_count > 15 or loc > 300:
                return "Business logic class violates Single Responsibility Principle"
        return None

    def _count_methods(self, class_node: ast.ClassDef) -> int:
        """Count methods in a class, excluding special methods."""
        methods = [node for node in class_node.body if isinstance(node, ast.FunctionDef)]
        # Exclude special methods like __init__, __str__, etc.
        regular_methods = [m for m in methods if not (m.name.startswith("__") and m.name.endswith("__"))]
        return len(regular_methods)

    def _calculate_lines_of_code(self, class_node: ast.ClassDef, source_lines: List[str]) -> int:
        """Calculate lines of code for a class, excluding comments and blank lines."""
        if hasattr(class_node, "end_lineno") and class_node.end_lineno:
            start_line = class_node.lineno - 1  # Convert to 0-based indexing
            end_line = class_node.end_lineno

            loc = 0
            for i in range(start_line, min(end_line, len(source_lines))):
                line = source_lines[i].strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    loc += 1
            return loc
        else:
            # Fallback estimation
            return (
                len([node for node in class_node.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]) * 8
            )

    def _analyze_methods(self, class_node: ast.ClassDef, source_lines: List[str]) -> List[MethodAnalysis]:
        """Analyze individual methods for responsibility and complexity."""
        methods = []

        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate method LOC
                if hasattr(node, "end_lineno") and node.end_lineno:
                    method_loc = node.end_lineno - node.lineno
                else:
                    method_loc = len(node.body)

                # Calculate complexity (simplified)
                complexity = self._calculate_method_complexity(node)

                # Identify responsibilities
                responsibilities = self._identify_method_responsibilities(node)

                # Count parameters
                param_count = len(node.args.args)

                # Calculate return complexity
                return_complexity = self._analyze_return_complexity(node)

                methods.append(
                    MethodAnalysis(
                        name=node.name,
                        lines_of_code=method_loc,
                        complexity_score=complexity,
                        responsibilities=responsibilities,
                        parameter_count=param_count,
                        return_complexity=return_complexity,
                    )
                )

        return methods

    def _calculate_method_complexity(self, method_node: ast.FunctionDef) -> float:
        """Calculate cyclomatic complexity of a method."""
        complexity = 1  # Base complexity

        for node in ast.walk(method_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.BoolOp, ast.Compare)):
                complexity += 1

        return float(complexity)

    def _identify_method_responsibilities(self, method_node: ast.FunctionDef) -> Set[ResponsibilityType]:
        """Identify the responsibilities of a method based on its operations."""
        responsibilities = set()

        method_name = method_node.name.lower()

        # Name-based responsibility identification
        if any(prefix in method_name for prefix in ["get_", "fetch_", "load_", "read_"]):
            responsibilities.add(ResponsibilityType.DATA_MANAGEMENT)
        elif any(prefix in method_name for prefix in ["set_", "save_", "store_", "write_", "update_"]):
            responsibilities.add(ResponsibilityType.PERSISTENCE)
        elif any(prefix in method_name for prefix in ["validate_", "check_", "verify_"]):
            responsibilities.add(ResponsibilityType.VALIDATION)
        elif any(prefix in method_name for prefix in ["transform_", "convert_", "format_", "parse_"]):
            responsibilities.add(ResponsibilityType.TRANSFORMATION)
        elif any(prefix in method_name for prefix in ["send_", "receive_", "notify_", "publish_"]):
            responsibilities.add(ResponsibilityType.COMMUNICATION)
        elif any(prefix in method_name for prefix in ["configure_", "setup_", "initialize_"]):
            responsibilities.add(ResponsibilityType.CONFIGURATION)
        elif any(prefix in method_name for prefix in ["process_", "handle_", "execute_"]):
            responsibilities.add(ResponsibilityType.COORDINATION)

        # AST-based responsibility identification
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name.lower() in ["open", "read", "write", "save", "load"]:
                    responsibilities.add(ResponsibilityType.PERSISTENCE)
                elif func_name.lower() in ["validate", "check", "assert"]:
                    responsibilities.add(ResponsibilityType.VALIDATION)
                elif func_name.lower() in ["send", "post", "get", "request"]:
                    responsibilities.add(ResponsibilityType.COMMUNICATION)

        # If no specific responsibility identified, assume business logic
        if not responsibilities:
            responsibilities.add(ResponsibilityType.BUSINESS_RULE)

        return responsibilities

    def _analyze_return_complexity(self, method_node: ast.FunctionDef) -> int:
        """Analyze the complexity of return statements."""
        return_complexity = 0

        for node in ast.walk(method_node):
            if isinstance(node, ast.Return) and node.value:
                if isinstance(node.value, (ast.Dict, ast.List, ast.Tuple)):
                    return_complexity += 2
                elif isinstance(node.value, ast.Call):
                    return_complexity += 1
                else:
                    return_complexity += 0.5

        return int(return_complexity)

    def _identify_responsibilities(
        self, class_node: ast.ClassDef, methods: List[MethodAnalysis]
    ) -> Set[ResponsibilityType]:
        """Identify all responsibilities handled by a class."""
        all_responsibilities = set()

        for method in methods:
            all_responsibilities.update(method.responsibilities)

        return all_responsibilities

    def _calculate_cohesion(self, methods: List[MethodAnalysis], responsibilities: Set[ResponsibilityType]) -> float:
        """Calculate cohesion score based on responsibility distribution."""
        if not methods:
            return 1.0  # Empty class has perfect cohesion

        if not responsibilities:
            return 0.5  # Default moderate score if no responsibilities detected

        # Measure how focused the class is on its responsibilities
        total_methods = len(methods)
        responsibility_count = len(responsibilities)

        # Context-aware responsibility scoring
        max_acceptable_responsibilities = 5.0  # Allow up to 5 different types of responsibilities
        responsibility_penalty = min(responsibility_count / max_acceptable_responsibilities, 1.0)

        # Measure consistency of method sizes
        if total_methods > 1:
            method_sizes = [max(1, method.lines_of_code) for method in methods]  # Avoid zero
            avg_size = sum(method_sizes) / len(method_sizes)
            if avg_size > 0:
                size_variance = sum((size - avg_size) ** 2 for size in method_sizes) / len(method_sizes)
                consistency_score = 1.0 / (1.0 + size_variance / 100.0)  # Normalize variance
            else:
                consistency_score = 0.5
        else:
            consistency_score = 1.0

        # Base cohesion calculation
        base_cohesion = (1.0 - responsibility_penalty * 0.6) * consistency_score

        # Boost cohesion for patterns that indicate good organization
        if responsibility_count <= 3:  # Very focused classes get bonus
            base_cohesion *= 1.2
        elif responsibility_count <= 5:  # Moderately focused classes get small bonus
            base_cohesion *= 1.1

        # Method naming consistency bonus
        if self._has_consistent_naming_pattern(methods):
            base_cohesion *= 1.1

        return max(0.1, min(1.0, base_cohesion))  # Ensure reasonable bounds

    def _has_consistent_naming_pattern(self, methods: List[MethodAnalysis]) -> bool:
        """Check if methods follow consistent naming patterns."""
        if len(methods) < 3:
            return True  # Small classes are considered consistent

        # Check for getter/setter patterns
        getters = sum(1 for m in methods if m.name.startswith("get_"))
        setters = sum(1 for m in methods if m.name.startswith("set_"))
        total = len(methods)

        # If majority are getters/setters, consider it consistent
        if (getters + setters) / total > 0.6:
            return True

        # Check for other consistent prefixes
        prefixes = {}
        for method in methods:
            parts = method.name.split("_")
            if len(parts) > 1:
                prefix = parts[0]
                prefixes[prefix] = prefixes.get(prefix, 0) + 1

        # If any prefix accounts for >40% of methods, consider it consistent
        return any(count / total > 0.4 for count in prefixes.values())

    def _assess_god_object_with_context(
        self,
        class_name: str,
        context: ClassContext,
        method_count: int,
        loc: int,
        cohesion_score: float,
        thresholds: Dict[str, int],
    ) -> Optional[str]:
        """Assess if a class is a god object considering its context."""

        issues = []

        # Check method count against context-specific threshold
        if method_count > thresholds["method_threshold"]:
            issues.append(
                f"Method count ({method_count}) exceeds {context.value} threshold ({thresholds['method_threshold']})"
            )

        # Check lines of code against context-specific threshold
        if loc > thresholds["loc_threshold"]:
            issues.append(f"Lines of code ({loc}) exceeds {context.value} threshold ({thresholds['loc_threshold']})")

        # Check cohesion for business logic classes (stricter)
        if context == ClassContext.BUSINESS_LOGIC and cohesion_score < 0.6:
            issues.append(f"Low cohesion ({cohesion_score:.2f}) in business logic class")
        elif context not in [ClassContext.FRAMEWORK, ClassContext.UTILITY] and cohesion_score < 0.4:
            issues.append(f"Very low cohesion ({cohesion_score:.2f})")

        # Context-specific god object assessment
        context_issue = self._assess_context_specific_issues(context, method_count, loc, cohesion_score)
        if context_issue:
            issues.append(context_issue)

        return "; ".join(issues) if issues else None

    def _generate_recommendations(
        self,
        context: ClassContext,
        method_count: int,
        loc: int,
        cohesion_score: float,
        responsibilities: Set[ResponsibilityType],
    ) -> List[str]:
        """Generate context-specific recommendations for improvement."""
        recommendations = []

        if context == ClassContext.CONFIG:
            if method_count > 30:
                recommendations.append("Consider splitting configuration into domain-specific config classes")
            if cohesion_score < 0.4:
                recommendations.append("Group related configuration properties into nested configuration objects")
        elif context == ClassContext.DATA_MODEL:
            if method_count > 25:
                recommendations.append("Extract business logic methods to separate service classes")
            recommendations.append("Focus on data representation and basic operations only")
        elif context == ClassContext.API_CONTROLLER:
            if method_count > 20:
                recommendations.append("Split into multiple controllers based on resource domains")
            recommendations.append("Extract business logic to service layer")
        elif context == ClassContext.UTILITY:
            if method_count > 40:
                recommendations.append("Split utility class by functional domains")
            recommendations.append("Consider converting static methods to module-level functions")
        elif context == ClassContext.BUSINESS_LOGIC:
            if method_count > 15:
                recommendations.append("Apply Single Responsibility Principle - split by business domain")
            if len(responsibilities) > 2:
                recommendations.append("Extract different responsibilities into separate classes")
        elif context == ClassContext.INFRASTRUCTURE:
            recommendations.append("Consider using composition over inheritance")
            recommendations.append("Extract different infrastructure concerns into separate classes")

        # General recommendations based on metrics
        if cohesion_score < 0.2:
            recommendations.append("Improve cohesion by grouping related methods and extracting unrelated ones")
        if loc > 1000:
            recommendations.append("Consider breaking into smaller, more focused classes")

        return recommendations

    def get_context_specific_thresholds(self, context: ClassContext) -> Dict[str, int]:
        """Get the thresholds for a specific context."""
        return self.context_thresholds.get(context, self.context_thresholds[ClassContext.UNKNOWN])

    def is_god_object_with_context(self, class_analysis: ClassAnalysis) -> bool:
        """Determine if a class is a god object based on context-aware analysis."""
        return class_analysis.god_object_reason is not None
