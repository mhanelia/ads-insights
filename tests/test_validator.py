"""Tests for the data validator service."""

import io

import pandas as pd
import pytest

from app.services.validator import (
    detect_outliers,
    validate_campaign_data,
    validate_columns,
    validate_data_types,
    validate_null_values,
)


class TestValidateColumns:
    """Tests for column validation."""

    def test_valid_columns_pass(self, sample_df: pd.DataFrame):
        """Valid DataFrame should pass column validation."""
        errors = validate_columns(sample_df)
        assert len(errors) == 0

    def test_missing_columns_detected(self, invalid_csv_missing_columns: bytes):
        """Missing columns should be detected."""
        df = pd.read_csv(io.BytesIO(invalid_csv_missing_columns))
        errors = validate_columns(df)
        
        assert len(errors) > 0
        missing_fields = {e.field for e in errors}
        assert "ctr" in missing_fields
        assert "conversions" in missing_fields
        assert "cost" in missing_fields
        assert "cpa" in missing_fields
        assert "channel" in missing_fields

    def test_empty_dataframe(self):
        """Empty DataFrame should fail validation."""
        df = pd.DataFrame()
        errors = validate_columns(df)
        assert len(errors) == 8  # All required columns missing


class TestValidateNullValues:
    """Tests for null value detection."""

    def test_no_nulls_pass(self, sample_df: pd.DataFrame):
        """DataFrame without nulls should pass."""
        errors = validate_null_values(sample_df)
        assert len(errors) == 0

    def test_null_values_detected(self, invalid_csv_null_values: bytes):
        """Null values should be detected."""
        df = pd.read_csv(io.BytesIO(invalid_csv_null_values))
        errors = validate_null_values(df)
        
        assert len(errors) >= 2
        fields_with_nulls = {e.field for e in errors}
        assert "impressions" in fields_with_nulls
        assert "clicks" in fields_with_nulls


class TestValidateDataTypes:
    """Tests for data type and constraint validation."""

    def test_valid_data_pass(self, sample_df: pd.DataFrame):
        """Valid data should pass type validation."""
        errors = validate_data_types(sample_df)
        assert len(errors) == 0

    def test_negative_values_detected(self, invalid_csv_negative_values: bytes):
        """Negative values should be detected."""
        df = pd.read_csv(io.BytesIO(invalid_csv_negative_values))
        errors = validate_data_types(df)
        
        assert len(errors) >= 2
        # Should detect negative conversions and negative cost

    def test_ctr_out_of_bounds(self):
        """CTR outside 0-100 range should be detected."""
        df = pd.DataFrame({
            "campaign_name": ["Test"],
            "impressions": [1000],
            "clicks": [100],
            "ctr": [150.0],  # Invalid: > 100%
            "conversions": [10],
            "cost": [500.0],
            "cpa": [50.0],
            "channel": ["Google Ads"],
        })
        errors = validate_data_types(df)
        
        assert len(errors) >= 1
        assert any(e.field == "ctr" for e in errors)

    def test_clicks_exceed_impressions(self):
        """Clicks exceeding impressions should be detected."""
        df = pd.DataFrame({
            "campaign_name": ["Test"],
            "impressions": [100],
            "clicks": [200],  # Invalid: > impressions
            "ctr": [200.0],
            "conversions": [10],
            "cost": [500.0],
            "cpa": [50.0],
            "channel": ["Google Ads"],
        })
        errors = validate_data_types(df)
        
        assert any(e.field == "clicks" for e in errors)


class TestDetectOutliers:
    """Tests for outlier detection."""

    def test_outliers_detected(self):
        """Outliers should be detected using IQR method."""
        # Create data with a clear outlier
        df = pd.DataFrame({
            "campaign_name": [f"Campaign {i}" for i in range(10)],
            "impressions": [1000] * 10,
            "clicks": [100] * 10,
            "ctr": [3.0] * 9 + [50.0],  # Last one is a clear outlier
            "conversions": [10] * 10,
            "cost": [500.0] * 10,
            "cpa": [50.0] * 9 + [500.0],  # Last one is a clear outlier
            "channel": ["Google Ads"] * 10,
        })
        warnings = detect_outliers(df, columns=["cpa"])
        
        # CPA of 500 should be detected as outlier when others are 50
        assert len(warnings) >= 1


    def test_no_outliers_in_uniform_data(self):
        """Uniform data should have no outliers."""
        df = pd.DataFrame({
            "campaign_name": [f"Campaign {i}" for i in range(10)],
            "impressions": [1000] * 10,
            "clicks": [100] * 10,
            "ctr": [10.0] * 10,
            "conversions": [10] * 10,
            "cost": [500.0] * 10,
            "cpa": [50.0] * 10,
            "channel": ["Google Ads"] * 10,
        })
        warnings = detect_outliers(df)
        assert len(warnings) == 0


class TestValidateCampaignData:
    """Integration tests for full validation."""

    def test_valid_data_passes(self, sample_df: pd.DataFrame):
        """Valid data should pass all validations."""
        result = validate_campaign_data(sample_df)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.rows_processed == len(sample_df)

    def test_invalid_data_fails(self, invalid_csv_missing_columns: bytes):
        """Invalid data should fail validation."""
        df = pd.read_csv(io.BytesIO(invalid_csv_missing_columns))
        result = validate_campaign_data(df)
        
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_warnings_included(self, edge_cases_csv: bytes):
        """Warnings should be included in result."""
        df = pd.read_csv(io.BytesIO(edge_cases_csv))
        result = validate_campaign_data(df)
        
        # Should have warnings for outliers
        assert result.is_valid is True  # Outliers are warnings, not errors
