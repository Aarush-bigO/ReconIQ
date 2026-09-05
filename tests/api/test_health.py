"""
API tests for health and system status endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_required_fields(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data

    def test_health_version_is_1_0_0(self):
        response = client.get("/health")
        assert response.json()["version"] == "1.0.0"


class TestSystemStatus:
    def test_system_status_returns_200(self):
        response = client.get("/system/status")
        assert response.status_code == 200

    def test_system_status_has_sections(self):
        response = client.get("/system/status")
        data = response.json()
        assert "api" in data
        assert "database" in data
        assert "razorpay" in data
        assert "llm" in data
        assert "thresholds" in data

    def test_database_has_record_counts(self):
        response = client.get("/system/status")
        data = response.json()
        db_section = data["database"]
        assert "record_counts" in db_section
        counts = db_section["record_counts"]
        if "error" not in counts:
            assert "transactions" in counts
            assert "settlements" in counts
