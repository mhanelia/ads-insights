"""CSV file loader service."""

import io
from typing import BinaryIO, Optional

import pandas as pd
from fastapi import UploadFile

from app.logging_config import get_logger
from app.services.csv_transformer import CSVFormat, detect_and_transform

logger = get_logger(__name__)

# Required columns for campaign data
REQUIRED_COLUMNS = [
    "campaign_name",
    "impressions",
    "clicks",
    "ctr",
    "conversions",
    "cost",
    "cpa",
    "channel",
]


async def load_csv_file(file: UploadFile) -> tuple[pd.DataFrame, CSVFormat]:
    """
    Load and parse a CSV file into a DataFrame.
    
    Automatically detects CSV format (original or Meta Ads) and transforms
    to internal format if needed.
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        Tuple of (DataFrame with campaign data, detected format)
        
    Raises:
        ValueError: If file cannot be parsed as CSV
    """
    logger.info("loading_csv", filename=file.filename)
    
    content = await file.read()
    
    # Try different encodings
    encodings = ["utf-8", "latin-1", "cp1252"]
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(
                io.BytesIO(content),
                encoding=encoding,
            )
            logger.info(
                "csv_loaded",
                encoding=encoding,
                rows=len(df),
                columns=list(df.columns),
            )
            break
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Invalid CSV format: {e}")
    
    if df is None:
        raise ValueError("Could not decode CSV file with any supported encoding")
    
    # Normalize column names (lowercase, underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Detect format and transform if needed
    df, csv_format = detect_and_transform(df)
    
    logger.info("csv_format_processed", format=csv_format.value, rows=len(df))
    
    # Convert numeric columns (for original format, Meta format already handles this)
    numeric_columns = ["impressions", "clicks", "ctr", "conversions", "cost", "cpa"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df, csv_format


def load_csv_from_bytes(content: bytes) -> tuple[pd.DataFrame, CSVFormat]:
    """
    Load CSV from bytes content (for testing).
    
    Args:
        content: Raw bytes of CSV file
        
    Returns:
        Tuple of (DataFrame with campaign data, detected format)
    """
    df = pd.read_csv(io.BytesIO(content))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Detect format and transform if needed
    df, csv_format = detect_and_transform(df)
    
    numeric_columns = ["impressions", "clicks", "ctr", "conversions", "cost", "cpa"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df, csv_format
