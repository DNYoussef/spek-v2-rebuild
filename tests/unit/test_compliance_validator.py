"""
Unit Tests - ComplianceValidator

Tests for compliance_validator.py covering:
- NASA POT10 validation (Rules 3, 4, 5, 6, 7)
- DFARS 252.204-7012 validation
- ISO27001 A.14.2.1 validation
- Generic compliance validation
- Compliance score calculation
- Recommendation generation

Target: 50+ tests
Version: 6.0.0 (Week 2 Day 3-5)
"""

import pytest
from analyzer.engines.compliance_validator import ComplianceValidator, create_compliance_validator


class TestComplianceValidatorInitialization:
    """Test ComplianceValidator initialization and configuration."""

    def test_create_compliance_validator(self):
        """Test factory function creates validator."""
        validator = create_compliance_validator()
        assert validator is not None
        assert isinstance(validator, ComplianceValidator)

    def test_validator_has_standards_config(self):
        """Test validator has standards configuration."""
        validator = ComplianceValidator()
        assert validator.standards_config is not None
        assert "NASA_POT10" in validator.standards_config
        assert "DFARS" in validator.standards_config
        assert "ISO27001" in validator.standards_config

    def test_nasa_pot10_config(self):
        """Test NASA POT10 configuration."""
        validator = ComplianceValidator()
        nasa_config = validator.standards_config["NASA_POT10"]

        assert "rules" in nasa_config
        assert "threshold" in nasa_config
        assert nasa_config["threshold"] == 0.92


class TestNASAPOT10Validation:
    """Test NASA Power of Ten compliance validation."""

    def test_validate_nasa_pot10_clean_code(self, sample_python_clean_code, analysis_result_builder):
        """Test NASA validation with clean code."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["NASA_POT10"])

        assert compliance["success"] is True
        nasa_result = compliance["individual_scores"]["NASA_POT10"]
        assert nasa_result["score"] >= 0.92
        assert nasa_result["passed"] is True

    def test_detect_nasa_rule_3_violations(self, analysis_result_builder):
        """Test detection of NASA Rule 3 violations (function >60 lines)."""
        validator = ComplianceValidator()
        results = (analysis_result_builder()
                  .with_nasa_violation(3)
                  .build())

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        assert nasa_result["critical_violations"] >= 1
        assert nasa_result["passed"] is False

    def test_nasa_compliance_score_calculation(self, analysis_result_builder):
        """Test NASA compliance score calculation."""
        validator = ComplianceValidator()

        # Create results with 1 critical violation out of 10 total issues
        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "nasa_rule_3_violation", "severity": "critical"},
            {"type": "other_issue", "severity": "low"},
            {"type": "other_issue", "severity": "low"},
        ]

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        # Score should be 1.0 - (1 critical / 3 total) = 0.67
        expected_score = 1.0 - (1 / 3)
        assert abs(nasa_result["score"] - expected_score) < 0.01

    def test_nasa_92_percent_threshold(self, analysis_result_builder):
        """Test NASA 92% compliance threshold."""
        validator = ComplianceValidator()

        # Create scenario with exactly 92% compliance
        # 8 critical violations out of 100 total = 92% compliant
        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "nasa_rule_3_violation", "severity": "critical"}
            for _ in range(8)
        ] + [
            {"type": "other_issue", "severity": "low"}
            for _ in range(92)
        ]

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        # Should pass at exactly 92%
        assert nasa_result["score"] >= 0.92
        assert nasa_result["passed"] is True

    def test_nasa_rules_checked(self):
        """Test that all NASA rules are checked."""
        validator = ComplianceValidator()
        results = {"syntax_issues": []}

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        expected_rules = ["RULE_3", "RULE_4", "RULE_5", "RULE_6", "RULE_7"]
        assert nasa_result["rules_checked"] == expected_rules

    def test_nasa_multiple_violations(self, analysis_result_builder):
        """Test NASA validation with multiple rule violations."""
        validator = ComplianceValidator()

        results = (analysis_result_builder()
                  .with_nasa_violation(3)
                  .with_nasa_violation(4)
                  .with_nasa_violation(6)
                  .build())

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        assert nasa_result["total_violations"] == 3
        assert nasa_result["critical_violations"] == 3

    def test_nasa_recommendations_on_failure(self, analysis_result_builder):
        """Test that NASA failures include recommendations."""
        validator = ComplianceValidator()
        results = (analysis_result_builder()
                  .with_nasa_violation(3)
                  .build())

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        assert len(nasa_result["recommendations"]) > 0
        assert any("NASA" in r for r in nasa_result["recommendations"])


class TestDFARSValidation:
    """Test DFARS 252.204-7012 compliance validation."""

    def test_validate_dfars_clean_code(self, analysis_result_builder):
        """Test DFARS validation with clean code."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["DFARS"])

        assert compliance["success"] is True
        dfars_result = compliance["individual_scores"]["DFARS"]
        assert dfars_result["score"] >= 0.95
        assert dfars_result["passed"] is True

    def test_detect_security_violations(self, analysis_result_builder):
        """Test detection of security violations for DFARS."""
        validator = ComplianceValidator()

        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "security_risk", "severity": "critical"},
            {"type": "vulnerability", "severity": "critical"}
        ]

        compliance = validator.validate(results, ["DFARS"])
        dfars_result = compliance["individual_scores"]["DFARS"]

        assert dfars_result["critical_security_violations"] >= 2
        assert dfars_result["passed"] is False

    def test_dfars_95_percent_threshold(self, analysis_result_builder):
        """Test DFARS 95% compliance threshold."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        # No critical security issues
        compliance = validator.validate(results, ["DFARS"])
        dfars_result = compliance["individual_scores"]["DFARS"]

        assert dfars_result["score"] >= 0.95
        assert dfars_result["passed"] is True

    def test_dfars_sections_checked(self):
        """Test that DFARS sections are documented."""
        validator = ComplianceValidator()
        results = {"syntax_issues": []}

        compliance = validator.validate(results, ["DFARS"])
        dfars_result = compliance["individual_scores"]["DFARS"]

        assert "sections_checked" in dfars_result
        assert "252.204-7012" in dfars_result["sections_checked"]

    def test_dfars_security_impact_calculation(self, analysis_result_builder):
        """Test DFARS security impact on compliance score."""
        validator = ComplianceValidator()

        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "security_risk", "severity": "critical"}
        ]

        compliance = validator.validate(results, ["DFARS"])
        dfars_result = compliance["individual_scores"]["DFARS"]

        # Each critical security issue = -10%
        assert dfars_result["score"] <= 0.90

    def test_dfars_recommendations_on_failure(self, analysis_result_builder):
        """Test that DFARS failures include recommendations."""
        validator = ComplianceValidator()

        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "security_risk", "severity": "critical"}
        ]

        compliance = validator.validate(results, ["DFARS"])
        dfars_result = compliance["individual_scores"]["DFARS"]

        assert len(dfars_result["recommendations"]) > 0
        assert any("security" in r.lower() for r in dfars_result["recommendations"])


class TestISO27001Validation:
    """Test ISO27001 A.14.2.1 compliance validation."""

    def test_validate_iso27001_clean_code(self, analysis_result_builder):
        """Test ISO27001 validation with clean code."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["ISO27001"])

        assert compliance["success"] is True
        iso_result = compliance["individual_scores"]["ISO27001"]
        assert iso_result["score"] >= 0.85
        assert iso_result["passed"] is True

    def test_detect_quality_violations(self, analysis_result_builder):
        """Test detection of quality violations for ISO27001."""
        validator = ComplianceValidator()

        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "quality_issue", "severity": "high"},
            {"type": "code_smell", "severity": "critical"}
        ]

        compliance = validator.validate(results, ["ISO27001"])
        iso_result = compliance["individual_scores"]["ISO27001"]

        assert iso_result["quality_violations"] >= 2

    def test_iso27001_85_percent_threshold(self, analysis_result_builder):
        """Test ISO27001 85% compliance threshold."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["ISO27001"])
        iso_result = compliance["individual_scores"]["ISO27001"]

        assert iso_result["passed"] is True
        assert iso_result["score"] >= 0.85

    def test_iso27001_controls_checked(self):
        """Test that ISO27001 controls are documented."""
        validator = ComplianceValidator()
        results = {"syntax_issues": []}

        compliance = validator.validate(results, ["ISO27001"])
        iso_result = compliance["individual_scores"]["ISO27001"]

        assert "controls_checked" in iso_result
        assert "A.14.2.1" in iso_result["controls_checked"]

    def test_iso27001_quality_impact_calculation(self, analysis_result_builder):
        """Test ISO27001 quality impact on compliance score."""
        validator = ComplianceValidator()

        results = analysis_result_builder().build()
        results["syntax_issues"] = [
            {"type": "quality_issue", "severity": "high"}
        ]

        compliance = validator.validate(results, ["ISO27001"])
        iso_result = compliance["individual_scores"]["ISO27001"]

        # Each high/critical issue = -5%
        assert iso_result["score"] <= 0.95


class TestGenericCompliance:
    """Test generic compliance validation."""

    def test_validate_custom_standard(self, analysis_result_builder):
        """Test validation of custom standard."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["CUSTOM_STANDARD"])

        assert compliance["success"] is True
        custom_result = compliance["individual_scores"]["CUSTOM_STANDARD"]
        assert "score" in custom_result
        assert "passed" in custom_result

    def test_generic_compliance_80_percent_threshold(self, analysis_result_builder):
        """Test generic compliance 80% threshold."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["GENERIC"])
        generic_result = compliance["individual_scores"]["GENERIC"]

        # Clean code should pass 80% threshold
        assert generic_result["score"] >= 0.80
        assert generic_result["passed"] is True

    def test_generic_compliance_with_issues(self, analysis_result_builder):
        """Test generic compliance with multiple issues."""
        validator = ComplianceValidator()

        results = analysis_result_builder().build()
        results["syntax_issues"] = [{"type": "issue", "severity": "medium"} for _ in range(50)]

        compliance = validator.validate(results, ["GENERIC"])
        generic_result = compliance["individual_scores"]["GENERIC"]

        # 50 issues * 0.02 = 1.0, so score = 0.0
        assert generic_result["score"] == 0.0
        assert generic_result["passed"] is False


class TestMultiStandardValidation:
    """Test validation against multiple standards."""

    def test_validate_all_standards_default(self, analysis_result_builder):
        """Test validation with default standards list."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results)

        assert compliance["success"] is True
        assert "NASA_POT10" in compliance["individual_scores"]
        assert "DFARS" in compliance["individual_scores"]
        assert "ISO27001" in compliance["individual_scores"]

    def test_validate_multiple_standards(self, analysis_result_builder):
        """Test validation against multiple standards."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        standards = ["NASA_POT10", "DFARS"]
        compliance = validator.validate(results, standards)

        assert len(compliance["individual_scores"]) == 2
        assert compliance["standards"] == standards

    def test_overall_score_calculation(self, analysis_result_builder):
        """Test overall compliance score calculation."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["NASA_POT10", "DFARS", "ISO27001"])

        # Overall score = average of individual scores
        individual_scores = [
            r["score"] for r in compliance["individual_scores"].values()
        ]
        expected_overall = sum(individual_scores) / len(individual_scores)

        assert abs(compliance["overall_score"] - expected_overall) < 0.01

    def test_standards_list_in_result(self, analysis_result_builder):
        """Test that validated standards list is included in result."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        standards = ["NASA_POT10", "ISO27001"]
        compliance = validator.validate(results, standards)

        assert compliance["standards"] == standards


class TestRecommendationGeneration:
    """Test compliance recommendation generation."""

    def test_generate_recommendations_passed(self, analysis_result_builder):
        """Test recommendations for passed compliance."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results)

        # Passed standards should have positive checkmark recommendations
        recommendations = compliance["recommendations"]
        passed_recs = [r for r in recommendations if "✅" in r]
        assert len(passed_recs) >= 3  # All 3 standards should pass

    def test_generate_recommendations_failed(self, analysis_result_builder):
        """Test recommendations for failed compliance."""
        validator = ComplianceValidator()

        results = (analysis_result_builder()
                  .with_nasa_violation(3)
                  .build())

        compliance = validator.validate(results, ["NASA_POT10"])

        recommendations = compliance["recommendations"]
        failed_recs = [r for r in recommendations if "❌" in r]
        assert len(failed_recs) >= 1

    def test_overall_recommendation_on_failure(self, analysis_result_builder):
        """Test overall recommendation when any standard fails."""
        validator = ComplianceValidator()

        results = (analysis_result_builder()
                  .with_nasa_violation(3)
                  .build())

        compliance = validator.validate(results)

        recommendations = compliance["recommendations"]
        # Should have overall warning
        assert any("⚠" in r or "compliance violations" in r.lower() for r in recommendations)

    def test_actionable_recommendations(self, analysis_result_builder):
        """Test that recommendations are actionable."""
        validator = ComplianceValidator()

        results = (analysis_result_builder()
                  .with_nasa_violation(3)
                  .build())

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        for rec in nasa_result["recommendations"]:
            assert len(rec) > 0
            assert isinstance(rec, str)


class TestExecutionMetrics:
    """Test execution time and performance metrics."""

    def test_execution_time_recorded(self, analysis_result_builder):
        """Test that execution time is recorded."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results)

        assert "execution_time" in compliance
        assert compliance["execution_time"] > 0
        assert compliance["execution_time"] < 1.0  # Should be fast

    def test_execution_time_reasonable(self, analysis_result_builder):
        """Test that execution time is reasonable for multiple standards."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["NASA_POT10", "DFARS", "ISO27001"])

        # Should complete quickly even with 3 standards
        assert compliance["execution_time"] < 0.5


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_analysis_results_raises_assertion(self):
        """Test that empty analysis results raise assertion error."""
        validator = ComplianceValidator()

        with pytest.raises(AssertionError, match="analysis_results cannot be empty"):
            validator.validate({}, ["NASA_POT10"])

    def test_none_analysis_results_raises_assertion(self):
        """Test that None analysis results raise assertion error."""
        validator = ComplianceValidator()

        with pytest.raises(AssertionError):
            validator.validate(None, ["NASA_POT10"])

    def test_validation_failure_returns_error_result(self):
        """Test that validation failures return error result."""
        validator = ComplianceValidator()

        # Trigger validation error by passing invalid data structure
        invalid_results = {"invalid": "data"}

        compliance = validator.validate(invalid_results, ["NASA_POT10"])

        if not compliance["success"]:
            assert "error" in compliance
            assert compliance["overall_score"] == 0.0

    def test_unknown_standard_uses_generic_validation(self, analysis_result_builder):
        """Test that unknown standards use generic validation."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["UNKNOWN_STANDARD"])

        assert compliance["success"] is True
        assert "UNKNOWN_STANDARD" in compliance["individual_scores"]

    def test_empty_standards_list_uses_defaults(self, analysis_result_builder):
        """Test that empty standards list uses defaults."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, [])

        # Should use default standards (NASA, DFARS, ISO)
        assert len(compliance["individual_scores"]) == 3


class TestResultStructure:
    """Test compliance result structure."""

    def test_result_has_required_fields(self, analysis_result_builder):
        """Test that result contains all required fields."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results)

        required_fields = [
            "success", "overall_score", "standards",
            "individual_scores", "execution_time", "recommendations"
        ]

        for field in required_fields:
            assert field in compliance

    def test_individual_score_structure(self, analysis_result_builder):
        """Test individual score structure."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results, ["NASA_POT10"])
        nasa_result = compliance["individual_scores"]["NASA_POT10"]

        assert "score" in nasa_result
        assert "passed" in nasa_result
        assert "recommendations" in nasa_result
        assert isinstance(nasa_result["score"], float)
        assert isinstance(nasa_result["passed"], bool)

    def test_overall_score_range(self, analysis_result_builder):
        """Test that overall score is in valid range [0.0, 1.0]."""
        validator = ComplianceValidator()
        results = analysis_result_builder().build()

        compliance = validator.validate(results)

        assert 0.0 <= compliance["overall_score"] <= 1.0
