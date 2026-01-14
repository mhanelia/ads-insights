"""Pydantic schemas for request/response models."""

from .campaign import (
    CampaignDataRow,
    ValidationError,
    ValidationResult,
    MetricsSummary,
    ChannelMetrics,
    PatternDetection,
    MetricsAnalysis,
    KeyIssue,
    Recommendation,
    RiskAlert,
    InsightResponse,
)

__all__ = [
    "CampaignDataRow",
    "ValidationError",
    "ValidationResult",
    "MetricsSummary",
    "ChannelMetrics",
    "PatternDetection",
    "MetricsAnalysis",
    "KeyIssue",
    "Recommendation",
    "RiskAlert",
    "InsightResponse",
]
