"""Tests for the insight chain service including prompt regression tests."""

import io

import pandas as pd
import pytest

from app.schemas.campaign import InsightResponse, Priority, Severity
from app.services.insight_chain import (
    generate_fallback_insights,
    load_prompt_template,
)
from app.services.metrics_analyzer import analyze_metrics


class TestLoadPromptTemplate:
    """Tests for prompt template loading."""

    def test_template_loads(self):
        """Should load prompt template from file."""
        template = load_prompt_template()
        
        assert len(template) > 0
        assert "{analysis_data}" in template
        assert "{format_instructions}" in template

    def test_template_contains_required_sections(self):
        """Template should contain required sections."""
        template = load_prompt_template()
        
        assert "REGRAS" in template
        assert "DADOS DA ANÁLISE" in template
        assert "FORMATO DE RESPOSTA" in template


class TestGenerateFallbackInsights:
    """Tests for deterministic fallback insights."""

    def test_fallback_returns_valid_response(self, sample_df: pd.DataFrame):
        """Fallback should return valid InsightResponse."""
        analysis = analyze_metrics(sample_df)
        insights = generate_fallback_insights(analysis)
        
        assert isinstance(insights, InsightResponse)
        assert len(insights.executive_summary) > 0
        assert insights.metrics_summary is not None

    def test_fallback_includes_recommendations(self, edge_cases_csv: bytes):
        """Fallback should generate recommendations for issues."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        assert len(insights.recommendations) >= 1
        assert all(r.title for r in insights.recommendations)
        assert all(r.description for r in insights.recommendations)

    def test_fallback_includes_risk_alerts(self, edge_cases_csv: bytes):
        """Fallback should generate risk alerts for critical issues."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        # Should have risk alerts for critical patterns
        assert len(insights.risk_alerts) >= 1

    def test_fallback_maps_patterns_to_issues(self, edge_cases_csv: bytes):
        """Patterns should be mapped to key issues."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        # Number of issues should match patterns
        assert len(insights.key_issues) == len(analysis.patterns_detected)


class TestPromptRegression:
    """
    Prompt regression tests.
    
    These tests ensure that changes to the prompt don't break
    the expected output structure.
    """

    def test_response_has_executive_summary(self, sample_df: pd.DataFrame):
        """Response must have executive summary."""
        analysis = analyze_metrics(sample_df)
        insights = generate_fallback_insights(analysis)
        
        assert insights.executive_summary is not None
        assert len(insights.executive_summary) > 10
        assert len(insights.executive_summary) < 1000  # Not too long

    def test_response_has_recommendations(self, edge_cases_csv: bytes):
        """Response must have at least one recommendation for problematic data."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        assert len(insights.recommendations) >= 1

    def test_recommendations_have_required_fields(self, edge_cases_csv: bytes):
        """Each recommendation must have all required fields."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        for rec in insights.recommendations:
            assert rec.title, "Recommendation must have title"
            assert rec.description, "Recommendation must have description"
            assert rec.rationale, "Recommendation must have rationale"
            assert rec.priority in Priority, "Recommendation must have valid priority"
            assert rec.expected_outcome, "Recommendation must have expected outcome"

    def test_response_no_empty_executive_summary(self, sample_df: pd.DataFrame):
        """Executive summary must not be empty or placeholder."""
        analysis = analyze_metrics(sample_df)
        insights = generate_fallback_insights(analysis)
        
        assert insights.executive_summary.strip() != ""
        assert "TODO" not in insights.executive_summary
        assert "placeholder" not in insights.executive_summary.lower()

    def test_key_issues_have_severity(self, edge_cases_csv: bytes):
        """Each key issue must have valid severity."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        for issue in insights.key_issues:
            assert issue.severity in Severity

    def test_risk_alerts_have_mitigation(self, edge_cases_csv: bytes):
        """Each risk alert must have mitigation suggestion."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        insights = generate_fallback_insights(analysis)
        
        for alert in insights.risk_alerts:
            assert alert.mitigation, "Risk alert must have mitigation"
            assert len(alert.mitigation) > 5

    def test_metrics_summary_preserved(self, sample_df: pd.DataFrame):
        """Metrics summary must be preserved in response."""
        analysis = analyze_metrics(sample_df)
        insights = generate_fallback_insights(analysis)
        
        assert insights.metrics_summary is not None
        assert insights.metrics_summary.total_campaigns == analysis.total_campaigns
        assert insights.metrics_summary.total_spend == analysis.total_spend

    def test_generated_at_timestamp(self, sample_df: pd.DataFrame):
        """Response must have generated_at timestamp."""
        analysis = analyze_metrics(sample_df)
        insights = generate_fallback_insights(analysis)
        
        assert insights.generated_at is not None
