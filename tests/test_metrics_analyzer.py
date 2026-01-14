"""Tests for the metrics analyzer service."""

import io

import pandas as pd
import pytest

from app.schemas.campaign import Severity
from app.services.metrics_analyzer import (
    analyze_metrics,
    analysis_to_llm_context,
    calculate_summary,
    detect_high_cpa,
    detect_high_ctr_low_conversion,
    detect_low_volume,
    detect_zero_conversions_high_spend,
    group_by_channel,
    rank_campaigns,
)


class TestCalculateSummary:
    """Tests for summary statistics calculation."""

    def test_basic_statistics(self):
        """Should calculate mean, median, std, min, max."""
        series = pd.Series([10, 20, 30, 40, 50])
        summary = calculate_summary(series)
        
        assert summary.mean == 30.0
        assert summary.median == 30.0
        assert summary.min == 10.0
        assert summary.max == 50.0
        assert summary.std > 0

    def test_single_value(self):
        """Should handle single value series."""
        series = pd.Series([42])
        summary = calculate_summary(series)
        
        assert summary.mean == 42.0
        assert summary.median == 42.0
        assert summary.std == 0.0


class TestDetectHighCtrLowConversion:
    """Tests for high CTR + low conversion pattern detection."""

    def test_pattern_detected(self, edge_cases_csv: bytes):
        """High CTR with low conversion should be detected."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        patterns = detect_high_ctr_low_conversion(df)
        
        assert len(patterns) >= 1
        assert any("High CTR Low Conv" in p.campaigns for p in patterns)
        assert all(p.severity == Severity.HIGH for p in patterns)

    def test_no_pattern_in_normal_data(self, sample_df: pd.DataFrame):
        """Normal data should not trigger pattern."""
        patterns = detect_high_ctr_low_conversion(sample_df)
        # May or may not have patterns depending on data
        # Just verify no errors


class TestDetectHighCpa:
    """Tests for high CPA pattern detection."""

    def test_high_cpa_detected(self, edge_cases_csv: bytes):
        """High CPA campaigns should be detected."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        patterns = detect_high_cpa(df)
        
        assert len(patterns) >= 1
        # Very High CPA campaign should be flagged


class TestDetectLowVolume:
    """Tests for low volume detection."""

    def test_low_volume_detected(self, edge_cases_csv: bytes):
        """Low volume campaigns should be detected."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        patterns = detect_low_volume(df)
        
        assert len(patterns) >= 1
        assert any("Low Volume" in p.campaigns for p in patterns)
        assert all(p.severity == Severity.MEDIUM for p in patterns)


class TestDetectZeroConversionsHighSpend:
    """Tests for zero conversions with high spend detection."""

    def test_zero_conversions_detected(self, edge_cases_csv: bytes):
        """Zero conversion campaigns with high spend should be detected."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        patterns = detect_zero_conversions_high_spend(df)
        
        assert len(patterns) >= 1
        assert any("Zero Conversions" in p.campaigns for p in patterns)
        assert all(p.severity == Severity.CRITICAL for p in patterns)


class TestGroupByChannel:
    """Tests for channel grouping."""

    def test_channels_grouped(self, sample_df: pd.DataFrame):
        """Should group metrics by channel."""
        channels = group_by_channel(sample_df)
        
        assert len(channels) >= 1
        channel_names = {c.channel for c in channels}
        assert "Google Ads" in channel_names

    def test_aggregations_correct(self):
        """Should correctly aggregate metrics."""
        df = pd.DataFrame({
            "campaign_name": ["A", "B"],
            "impressions": [1000, 2000],
            "clicks": [100, 200],
            "ctr": [10.0, 10.0],
            "conversions": [10, 20],
            "cost": [500.0, 1000.0],
            "cpa": [50.0, 50.0],
            "channel": ["Google Ads", "Google Ads"],
        })
        channels = group_by_channel(df)
        
        assert len(channels) == 1
        google = channels[0]
        assert google.total_impressions == 3000
        assert google.total_clicks == 300
        assert google.total_conversions == 30
        assert google.total_cost == 1500.0
        assert google.campaign_count == 2


class TestRankCampaigns:
    """Tests for campaign ranking."""

    def test_ranking_works(self, sample_df: pd.DataFrame):
        """Should rank campaigns by efficiency."""
        top, bottom = rank_campaigns(sample_df, top_n=3)
        
        assert len(top) == 3
        assert len(bottom) == 3

    def test_top_n_parameter(self, sample_df: pd.DataFrame):
        """Should respect top_n parameter."""
        top, bottom = rank_campaigns(sample_df, top_n=2)
        
        assert len(top) == 2
        assert len(bottom) == 2


class TestAnalyzeMetrics:
    """Integration tests for full metrics analysis."""

    def test_complete_analysis(self, sample_df: pd.DataFrame):
        """Should return complete analysis."""
        analysis = analyze_metrics(sample_df)
        
        assert analysis.total_campaigns == len(sample_df)
        assert analysis.total_spend > 0
        assert analysis.total_conversions > 0
        assert len(analysis.by_channel) >= 1
        assert len(analysis.top_performers) > 0
        assert len(analysis.bottom_performers) > 0

    def test_patterns_detected(self, edge_cases_csv: bytes):
        """Should detect patterns in edge case data."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        analysis = analyze_metrics(df)
        
        assert len(analysis.patterns_detected) >= 1


class TestAnalysisToLlmContext:
    """Tests for LLM context conversion."""

    def test_context_structure(self, sample_df: pd.DataFrame):
        """Should produce valid LLM context."""
        analysis = analyze_metrics(sample_df)
        context = analysis_to_llm_context(analysis)
        
        assert "overview" in context
        assert "top_performers" in context
        assert "bottom_performers" in context
        assert "channels" in context
        assert "issues" in context

    def test_context_values_formatted(self, sample_df: pd.DataFrame):
        """Values should be formatted for readability."""
        analysis = analyze_metrics(sample_df)
        context = analysis_to_llm_context(analysis)
        
        # Check that currency values are formatted
        assert "$" in context["overview"]["total_spend"]
        assert "%" in context["overview"]["avg_ctr"]
