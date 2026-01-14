"""CSV format detection and transformation service.

Supports automatic detection and transformation of different CSV formats:
- Original format (English columns)
- Meta Ads format (Portuguese columns exported from Meta Business Suite)
"""

from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd

from app.logging_config import get_logger

logger = get_logger(__name__)


class CSVFormat(str, Enum):
    """Supported CSV formats."""
    
    ORIGINAL = "original"
    META_ADS = "meta_ads"
    UNKNOWN = "unknown"


# Column mappings for Meta Ads format (Portuguese → Internal)
META_ADS_COLUMN_MAP = {
    "nome_da_campanha": "campaign_name",
    "impressões": "impressions",
    "resultados": "conversions",
    "valor_usado_(eur)": "cost",
    "custo_por_resultado": "cpa",
    "cpc_(custo_por_clique_no_link)": "cpc",
    "alcance": "reach",
    "status_de_veiculação": "status",
    "tipo_de_resultado": "result_type",
}

# Required columns for original format
ORIGINAL_REQUIRED_COLUMNS = {
    "campaign_name",
    "impressions", 
    "clicks",
    "ctr",
    "conversions",
    "cost",
    "cpa",
    "channel",
}

# Required columns for Meta Ads format (after normalization)
META_ADS_REQUIRED_COLUMNS = {
    "nome_da_campanha",
    "impressões",
    "valor_usado_(eur)",
}


def detect_format(df: pd.DataFrame) -> CSVFormat:
    """
    Detect the CSV format based on column names.
    
    Args:
        df: DataFrame with raw CSV data
        
    Returns:
        Detected CSV format
    """
    columns = set(df.columns)
    
    # Check for original format
    if ORIGINAL_REQUIRED_COLUMNS.issubset(columns):
        logger.info("format_detected", format="original")
        return CSVFormat.ORIGINAL
    
    # Check for Meta Ads format
    if META_ADS_REQUIRED_COLUMNS.issubset(columns):
        logger.info("format_detected", format="meta_ads")
        return CSVFormat.META_ADS
    
    logger.warning(
        "unknown_format",
        columns=list(columns),
        expected_original=list(ORIGINAL_REQUIRED_COLUMNS),
        expected_meta=list(META_ADS_REQUIRED_COLUMNS),
    )
    return CSVFormat.UNKNOWN


def transform_meta_ads(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform Meta Ads format to internal format.
    
    Args:
        df: DataFrame in Meta Ads format
        
    Returns:
        DataFrame in internal format
    """
    logger.info("transforming_meta_ads", rows=len(df))
    
    result = pd.DataFrame()
    
    # Direct mappings
    result["campaign_name"] = df["nome_da_campanha"]
    result["impressions"] = pd.to_numeric(df["impressões"], errors="coerce").fillna(0).astype(int)
    result["cost"] = pd.to_numeric(df["valor_usado_(eur)"], errors="coerce").fillna(0)
    
    # Conversions from "Resultados" (may be empty)
    if "resultados" in df.columns:
        result["conversions"] = pd.to_numeric(df["resultados"], errors="coerce").fillna(0).astype(int)
    else:
        result["conversions"] = 0
    
    # CPA from "Custo por resultado" (may be empty)
    if "custo_por_resultado" in df.columns:
        result["cpa"] = pd.to_numeric(df["custo_por_resultado"], errors="coerce").fillna(0)
    else:
        # Calculate CPA if not present
        result["cpa"] = np.where(
            result["conversions"] > 0,
            result["cost"] / result["conversions"],
            0
        )
    
    # Calculate clicks from CPC if available
    if "cpc_(custo_por_clique_no_link)" in df.columns:
        cpc = pd.to_numeric(df["cpc_(custo_por_clique_no_link)"], errors="coerce").fillna(0)
        # clicks = cost / cpc (when cpc > 0)
        result["clicks"] = np.where(
            cpc > 0,
            (result["cost"] / cpc).round().astype(int),
            0
        )
    else:
        result["clicks"] = 0
    
    # Calculate CTR
    result["ctr"] = np.where(
        result["impressions"] > 0,
        (result["clicks"] / result["impressions"]) * 100,
        0
    )
    
    # All campaigns are from Meta Ads
    result["channel"] = "Meta Ads"
    
    # Keep some extra metadata that might be useful
    if "status_de_veiculação" in df.columns:
        result["status"] = df["status_de_veiculação"]
    
    if "tipo_de_resultado" in df.columns:
        result["result_type"] = df["tipo_de_resultado"]
    
    if "alcance" in df.columns:
        result["reach"] = pd.to_numeric(df["alcance"], errors="coerce").fillna(0).astype(int)
    
    logger.info(
        "meta_ads_transformed",
        rows=len(result),
        total_cost=result["cost"].sum(),
        total_conversions=result["conversions"].sum(),
    )
    
    return result


def detect_and_transform(df: pd.DataFrame) -> tuple[pd.DataFrame, CSVFormat]:
    """
    Detect CSV format and transform to internal format if needed.
    
    Args:
        df: DataFrame with raw CSV data (columns already normalized to lowercase)
        
    Returns:
        Tuple of (transformed DataFrame, detected format)
    """
    csv_format = detect_format(df)
    
    if csv_format == CSVFormat.ORIGINAL:
        # Already in correct format, just ensure types
        return df, csv_format
    
    if csv_format == CSVFormat.META_ADS:
        transformed = transform_meta_ads(df)
        return transformed, csv_format
    
    # Unknown format - return as-is and let validation handle errors
    logger.warning("returning_unknown_format", columns=list(df.columns))
    return df, csv_format
