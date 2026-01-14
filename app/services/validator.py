"""Data validation service for campaign CSV files."""

from typing import Optional

import numpy as np
import pandas as pd

from app.config import get_settings
from app.logging_config import get_logger
from app.schemas.campaign import ValidationError, ValidationResult
from app.services.csv_loader import REQUIRED_COLUMNS

logger = get_logger(__name__)


def validate_columns(df: pd.DataFrame) -> list[ValidationError]:
    """
    Validate that all required columns are present.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        List of validation errors for missing columns
    """
    errors = []
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    
    for col in missing_columns:
        errors.append(
            ValidationError(
                field=col,
                message=f"Required column '{col}' is missing",
            )
        )
    
    if errors:
        logger.warning("missing_columns", missing=list(missing_columns))
    
    return errors


def validate_null_values(df: pd.DataFrame) -> list[ValidationError]:
    """
    Detect null/NaN values in required columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        List of validation errors for null values
    """
    errors = []
    
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            continue
            
        null_mask = df[col].isna()
        null_rows = df.index[null_mask].tolist()
        
        if null_rows:
            for row in null_rows[:5]:  # Report first 5 only
                errors.append(
                    ValidationError(
                        field=col,
                        message=f"Null value found in column '{col}'",
                        row=int(row) + 2,  # +2 for header and 0-index
                    )
                )
            
            if len(null_rows) > 5:
                errors.append(
                    ValidationError(
                        field=col,
                        message=f"... and {len(null_rows) - 5} more null values in '{col}'",
                    )
                )
    
    if errors:
        logger.warning("null_values_detected", error_count=len(errors))
    
    return errors


def validate_data_types(df: pd.DataFrame) -> list[ValidationError]:
    """
    Validate data types and value constraints.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        List of validation errors for invalid values
    """
    errors = []
    
    # Check for negative values in numeric columns
    numeric_cols = ["impressions", "clicks", "conversions", "cost", "cpa"]
    for col in numeric_cols:
        if col not in df.columns:
            continue
            
        negative_mask = df[col] < 0
        negative_rows = df.index[negative_mask].tolist()
        
        for row in negative_rows[:3]:
            errors.append(
                ValidationError(
                    field=col,
                    message=f"Negative value not allowed in '{col}'",
                    row=int(row) + 2,
                    value=str(df.loc[row, col]),
                )
            )
    
    # Check CTR bounds (0-100%)
    if "ctr" in df.columns:
        invalid_ctr = (df["ctr"] < 0) | (df["ctr"] > 100)
        invalid_rows = df.index[invalid_ctr].tolist()
        
        for row in invalid_rows[:3]:
            errors.append(
                ValidationError(
                    field="ctr",
                    message="CTR must be between 0 and 100%",
                    row=int(row) + 2,
                    value=str(df.loc[row, "ctr"]),
                )
            )
    
    # Check clicks <= impressions
    if "clicks" in df.columns and "impressions" in df.columns:
        invalid_clicks = df["clicks"] > df["impressions"]
        invalid_rows = df.index[invalid_clicks].tolist()
        
        for row in invalid_rows[:3]:
            errors.append(
                ValidationError(
                    field="clicks",
                    message="Clicks cannot exceed impressions",
                    row=int(row) + 2,
                    value=f"clicks={df.loc[row, 'clicks']}, impressions={df.loc[row, 'impressions']}",
                )
            )
    
    if errors:
        logger.warning("invalid_values_detected", error_count=len(errors))
    
    return errors


def detect_outliers(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
) -> list[ValidationError]:
    """
    Detect statistical outliers using IQR method.
    
    Args:
        df: DataFrame to check
        columns: Columns to check (defaults to numeric metrics)
        
    Returns:
        List of warnings for detected outliers
    """
    settings = get_settings()
    warnings = []
    
    if columns is None:
        columns = ["ctr", "cpa", "cost"]
    
    for col in columns:
        if col not in df.columns:
            continue
            
        values = df[col].dropna()
        if len(values) < 4:  # Need at least 4 values for IQR
            continue
            
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - settings.outlier_threshold * iqr
        upper_bound = q3 + settings.outlier_threshold * iqr
        
        outlier_mask = (values < lower_bound) | (values > upper_bound)
        outlier_indices = values[outlier_mask].index.tolist()
        
        for idx in outlier_indices[:3]:
            campaign_name = df.loc[idx, "campaign_name"] if "campaign_name" in df.columns else f"Row {idx}"
            warnings.append(
                ValidationError(
                    field=col,
                    message=f"Outlier detected in '{col}' for campaign '{campaign_name}'",
                    row=int(idx) + 2,
                    value=str(df.loc[idx, col]),
                )
            )
    
    if warnings:
        logger.info("outliers_detected", count=len(warnings))
    
    return warnings


def validate_campaign_data(df: pd.DataFrame) -> ValidationResult:
    """
    Run all validations on campaign data.
    
    Args:
        df: DataFrame with campaign data
        
    Returns:
        ValidationResult with all errors and warnings
    """
    logger.info("starting_validation", rows=len(df))
    
    all_errors = []
    all_warnings = []
    
    # Critical validations (will fail the request)
    all_errors.extend(validate_columns(df))
    
    # Only continue if required columns exist
    if not all_errors:
        all_errors.extend(validate_null_values(df))
        all_errors.extend(validate_data_types(df))
        
        # Non-critical (warnings only)
        all_warnings.extend(detect_outliers(df))
    
    is_valid = len(all_errors) == 0
    
    result = ValidationResult(
        is_valid=is_valid,
        errors=all_errors,
        warnings=all_warnings,
        rows_processed=len(df),
    )
    
    logger.info(
        "validation_complete",
        is_valid=is_valid,
        error_count=len(all_errors),
        warning_count=len(all_warnings),
    )
    
    return result
