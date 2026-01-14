"""Integration tests for API routes."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint should return 200."""
        response = client.get("/health")
        
        assert response.status_code == 200

    def test_health_returns_status(self, client: TestClient):
        """Health endpoint should return status info."""
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "llm_provider" in data


class TestAnalyzeEndpoint:
    """Tests for POST /analyze-campaign endpoint."""

    def test_valid_csv_returns_insights(
        self, 
        client: TestClient, 
        sample_csv_content: bytes,
    ):
        """Valid CSV should return insights."""
        response = client.post(
            "/analyze-campaign",
            files={"file": ("campaigns.csv", sample_csv_content, "text/csv")},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "executive_summary" in data
        assert "key_issues" in data
        assert "recommendations" in data
        assert "risk_alerts" in data
        assert "metrics_summary" in data

    def test_invalid_csv_returns_400(
        self, 
        client: TestClient, 
        invalid_csv_missing_columns: bytes,
    ):
        """Invalid CSV should return 400."""
        response = client.post(
            "/analyze-campaign",
            files={"file": ("campaigns.csv", invalid_csv_missing_columns, "text/csv")},
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_empty_file_returns_422(self, client: TestClient):
        """Empty file should return 422."""
        response = client.post(
            "/analyze-campaign",
            files={"file": ("campaigns.csv", b"", "text/csv")},
        )
        
        assert response.status_code == 422

    def test_non_csv_file_rejected(self, client: TestClient):
        """Non-CSV file should be rejected."""
        response = client.post(
            "/analyze-campaign",
            files={"file": ("data.json", b'{"test": true}', "application/json")},
        )
        
        assert response.status_code == 422

    def test_response_has_request_id(
        self, 
        client: TestClient, 
        sample_csv_content: bytes,
    ):
        """Response should include X-Request-ID header."""
        response = client.post(
            "/analyze-campaign",
            files={"file": ("campaigns.csv", sample_csv_content, "text/csv")},
        )
        
        assert "X-Request-ID" in response.headers

    def test_sample_file_works(
        self, 
        client: TestClient,
        sample_csv_file_path: Path,
    ):
        """Sample CSV file from data/ should work."""
        if not sample_csv_file_path.exists():
            pytest.skip("Sample file not found")
        
        with open(sample_csv_file_path, "rb") as f:
            content = f.read()
        
        response = client.post(
            "/analyze-campaign",
            files={"file": ("sample_campaign.csv", content, "text/csv")},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metrics_summary"]["total_campaigns"] == 25

    def test_edge_cases_detected(
        self, 
        client: TestClient, 
        edge_cases_csv: bytes,
    ):
        """Edge cases should be properly detected."""
        response = client.post(
            "/analyze-campaign",
            files={"file": ("edge_cases.csv", edge_cases_csv, "text/csv")},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have detected issues
        assert len(data["key_issues"]) >= 1
        
        # Should have recommendations
        assert len(data["recommendations"]) >= 1
