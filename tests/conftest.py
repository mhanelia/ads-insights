"""Pytest configuration and shared fixtures."""

import io
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_csv_content() -> bytes:
    """Valid sample CSV content."""
    return b"""campaign_name,impressions,clicks,ctr,conversions,cost,cpa,channel
Brand Awareness,150000,4500,3.0,120,8500.00,70.83,Google Ads
Product Launch,85000,3400,4.0,95,6200.00,65.26,Google Ads
Retargeting,200000,12000,6.0,450,15000.00,33.33,Meta Ads
Summer Sale,120000,2400,2.0,80,5500.00,68.75,Meta Ads
Lead Gen B2B,45000,1350,3.0,42,4800.00,114.29,LinkedIn Ads
"""


@pytest.fixture
def sample_df(sample_csv_content: bytes) -> pd.DataFrame:
    """Valid sample DataFrame."""
    df = pd.read_csv(io.BytesIO(sample_csv_content))
    return df


@pytest.fixture
def invalid_csv_missing_columns() -> bytes:
    """CSV with missing required columns."""
    return b"""campaign_name,impressions,clicks
Brand Awareness,150000,4500
Product Launch,85000,3400
"""


@pytest.fixture
def invalid_csv_null_values() -> bytes:
    """CSV with null values."""
    return b"""campaign_name,impressions,clicks,ctr,conversions,cost,cpa,channel
Brand Awareness,150000,4500,3.0,120,8500.00,70.83,Google Ads
Product Launch,,3400,4.0,95,6200.00,65.26,Google Ads
Retargeting,200000,,6.0,450,15000.00,33.33,Meta Ads
"""


@pytest.fixture
def invalid_csv_negative_values() -> bytes:
    """CSV with negative values."""
    return b"""campaign_name,impressions,clicks,ctr,conversions,cost,cpa,channel
Brand Awareness,150000,4500,3.0,-120,8500.00,70.83,Google Ads
Product Launch,85000,3400,4.0,95,-6200.00,65.26,Google Ads
"""


@pytest.fixture
def edge_cases_csv() -> bytes:
    """CSV with edge cases and outliers."""
    return b"""campaign_name,impressions,clicks,ctr,conversions,cost,cpa,channel
Normal Campaign,100000,3000,3.0,100,5000.00,50.00,Google Ads
High CTR Low Conv,80000,6400,8.0,5,4000.00,800.00,Meta Ads
Zero Conversions,50000,2500,5.0,0,7500.00,0.00,Google Ads
Very High CPA,60000,1800,3.0,10,15000.00,1500.00,LinkedIn Ads
Low Volume,500,25,5.0,2,100.00,50.00,TikTok Ads
"""


@pytest.fixture
def sample_csv_file_path() -> Path:
    """Path to the sample CSV file."""
    return Path(__file__).parent.parent / "data" / "sample_campaign.csv"
