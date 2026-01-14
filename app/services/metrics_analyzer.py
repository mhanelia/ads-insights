"""Deterministic metrics analysis service using Pandas."""

from typing import Any

import numpy as np
import pandas as pd

from app.config import get_settings
from app.logging_config import get_logger
from app.schemas.campaign import (
    ChannelMetrics,
    MetricsAnalysis,
    MetricsSummary,
    PatternDetection,
    Severity,
)

logger = get_logger(__name__)


def calculate_summary(series: pd.Series) -> MetricsSummary:
    """Calculate summary statistics for a numeric series."""
    return MetricsSummary(
        mean=float(series.mean()),
        median=float(series.median()),
        std=float(series.std()) if len(series) > 1 else 0.0,
        min=float(series.min()),
        max=float(series.max()),
    )


def detect_high_ctr_low_conversion(df: pd.DataFrame) -> list[PatternDetection]:
    """
    Detect campaigns with high CTR but low conversion rate.
    
    This pattern often indicates:
    - Misleading ad copy
    - Landing page issues
    - Wrong audience targeting
    """
    settings = get_settings()
    patterns = []
    
    # Calculate conversion rate
    df = df.copy()
    df["conversion_rate"] = (df["conversions"] / df["clicks"] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    
    high_ctr_low_conv = df[
        (df["ctr"] > settings.high_ctr_threshold) & 
        (df["conversion_rate"] < settings.low_conversion_rate_threshold)
    ]
    
    if len(high_ctr_low_conv) > 0:
        patterns.append(
            PatternDetection(
                pattern_type="high_ctr_low_conversion",
                campaigns=high_ctr_low_conv["campaign_name"].tolist(),
                description=(
                    f"Found {len(high_ctr_low_conv)} campaign(s) with CTR above "
                    f"{settings.high_ctr_threshold}% but conversion rate below "
                    f"{settings.low_conversion_rate_threshold}%. "
                    "This may indicate landing page issues or misleading ad copy."
                ),
                severity=Severity.HIGH,
            )
        )
        logger.info(
            "pattern_detected",
            pattern="high_ctr_low_conversion",
            count=len(high_ctr_low_conv),
        )
    
    return patterns


def detect_high_cpa(df: pd.DataFrame) -> list[PatternDetection]:
    """Detect campaigns with CPA significantly above average."""
    settings = get_settings()
    patterns = []
    
    avg_cpa = df["cpa"].mean()
    threshold = avg_cpa * settings.high_cpa_multiplier
    
    high_cpa = df[df["cpa"] > threshold]
    
    if len(high_cpa) > 0:
        patterns.append(
            PatternDetection(
                pattern_type="high_cpa",
                campaigns=high_cpa["campaign_name"].tolist(),
                description=(
                    f"Found {len(high_cpa)} campaign(s) with CPA above "
                    f"{settings.high_cpa_multiplier}x the average (${avg_cpa:.2f}). "
                    f"These campaigns are spending ${high_cpa['cpa'].mean():.2f} per acquisition."
                ),
                severity=Severity.HIGH,
            )
        )
        logger.info(
            "pattern_detected",
            pattern="high_cpa",
            count=len(high_cpa),
            avg_cpa=avg_cpa,
        )
    
    return patterns


def detect_low_volume(df: pd.DataFrame) -> list[PatternDetection]:
    """Detect campaigns with insufficient volume for statistical significance."""
    settings = get_settings()
    patterns = []
    
    low_volume = df[df["impressions"] < settings.min_impressions_threshold]
    
    if len(low_volume) > 0:
        patterns.append(
            PatternDetection(
                pattern_type="low_volume",
                campaigns=low_volume["campaign_name"].tolist(),
                description=(
                    f"Found {len(low_volume)} campaign(s) with less than "
                    f"{settings.min_impressions_threshold:,} impressions. "
                    "Results may not be statistically significant."
                ),
                severity=Severity.MEDIUM,
            )
        )
        logger.info(
            "pattern_detected",
            pattern="low_volume",
            count=len(low_volume),
        )
    
    return patterns


def detect_zero_conversions_high_spend(df: pd.DataFrame) -> list[PatternDetection]:
    """Detect campaigns with zero conversions but significant spend."""
    patterns = []
    
    avg_cost = df["cost"].mean()
    zero_conv_high_spend = df[(df["conversions"] == 0) & (df["cost"] > avg_cost)]
    
    if len(zero_conv_high_spend) > 0:
        total_wasted = zero_conv_high_spend["cost"].sum()
        patterns.append(
            PatternDetection(
                pattern_type="zero_conversions_high_spend",
                campaigns=zero_conv_high_spend["campaign_name"].tolist(),
                description=(
                    f"Found {len(zero_conv_high_spend)} campaign(s) with zero conversions "
                    f"but above-average spend. Total at-risk budget: ${total_wasted:,.2f}"
                ),
                severity=Severity.CRITICAL,
            )
        )
        logger.info(
            "pattern_detected",
            pattern="zero_conversions_high_spend",
            count=len(zero_conv_high_spend),
            total_wasted=total_wasted,
        )
    
    return patterns


def group_by_channel(df: pd.DataFrame) -> list[ChannelMetrics]:
    """Aggregate metrics by marketing channel."""
    channel_groups = df.groupby("channel").agg({
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "cost": "sum",
        "ctr": "mean",
        "cpa": "mean",
        "campaign_name": "count",
    }).reset_index()
    
    channels = []
    for _, row in channel_groups.iterrows():
        channels.append(
            ChannelMetrics(
                channel=row["channel"],
                total_impressions=int(row["impressions"]),
                total_clicks=int(row["clicks"]),
                total_conversions=int(row["conversions"]),
                total_cost=float(row["cost"]),
                avg_ctr=float(row["ctr"]),
                avg_cpa=float(row["cpa"]) if not pd.isna(row["cpa"]) else 0.0,
                campaign_count=int(row["campaign_name"]),
            )
        )
    
    return channels


def rank_campaigns(df: pd.DataFrame, top_n: int = 3) -> tuple[list[str], list[str]]:
    """
    Rank campaigns by conversion performance.
    
    Returns:
        Tuple of (top_performers, bottom_performers) campaign names
    """
    # Calculate efficiency score: conversions per dollar spent
    df = df.copy()
    df["efficiency"] = (df["conversions"] / df["cost"]).replace([np.inf, -np.inf], 0).fillna(0)
    
    sorted_df = df.sort_values("efficiency", ascending=False)
    
    top_performers = sorted_df.head(top_n)["campaign_name"].tolist()
    bottom_performers = sorted_df.tail(top_n)["campaign_name"].tolist()
    
    return top_performers, bottom_performers


def analyze_metrics(df: pd.DataFrame) -> MetricsAnalysis:
    """
    Perform complete deterministic analysis on campaign data.
    
    Args:
        df: Validated DataFrame with campaign data
        
    Returns:
        MetricsAnalysis with all computed metrics and patterns
    """
    logger.info("starting_metrics_analysis", campaigns=len(df))
    
    # Calculate summaries
    impressions_summary = calculate_summary(df["impressions"])
    ctr_summary = calculate_summary(df["ctr"])
    cpa_summary = calculate_summary(df["cpa"])
    conversions_summary = calculate_summary(df["conversions"])
    
    # Detect patterns
    patterns = []
    patterns.extend(detect_high_ctr_low_conversion(df))
    patterns.extend(detect_high_cpa(df))
    patterns.extend(detect_low_volume(df))
    patterns.extend(detect_zero_conversions_high_spend(df))
    
    # Group by channel
    by_channel = group_by_channel(df)
    
    # Rank campaigns
    top_performers, bottom_performers = rank_campaigns(df)
    
    analysis = MetricsAnalysis(
        total_campaigns=len(df),
        total_spend=float(df["cost"].sum()),
        total_conversions=int(df["conversions"].sum()),
        impressions_summary=impressions_summary,
        ctr_summary=ctr_summary,
        cpa_summary=cpa_summary,
        conversions_summary=conversions_summary,
        by_channel=by_channel,
        patterns_detected=patterns,
        top_performers=top_performers,
        bottom_performers=bottom_performers,
    )
    
    logger.info(
        "metrics_analysis_complete",
        total_spend=analysis.total_spend,
        total_conversions=analysis.total_conversions,
        patterns_found=len(patterns),
    )
    
    return analysis


def analysis_to_llm_context(analysis: MetricsAnalysis) -> dict[str, Any]:
    """
    Convert MetricsAnalysis to a simplified dict for LLM context.
    
    This provides a cleaner, more focused input for the LLM
    to reduce token usage and improve insight quality.
    """
    return {
        "overview": {
            "total_campaigns": analysis.total_campaigns,
            "total_spend": f"${analysis.total_spend:,.2f}",
            "total_conversions": analysis.total_conversions,
            "avg_cpa": f"${analysis.cpa_summary.mean:.2f}",
            "avg_ctr": f"{analysis.ctr_summary.mean:.2f}%",
        },
        "top_performers": analysis.top_performers,
        "bottom_performers": analysis.bottom_performers,
        "channels": [
            {
                "name": ch.channel,
                "campaigns": ch.campaign_count,
                "spend": f"${ch.total_cost:,.2f}",
                "conversions": ch.total_conversions,
                "avg_cpa": f"${ch.avg_cpa:.2f}",
            }
            for ch in analysis.by_channel
        ],
        "issues": [
            {
                "type": p.pattern_type,
                "severity": p.severity.value,
                "campaigns": p.campaigns,
                "description": p.description,
            }
            for p in analysis.patterns_detected
        ],
    }
