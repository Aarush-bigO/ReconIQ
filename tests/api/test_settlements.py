"""
API tests for settlements endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestListSettlements:
    def test_list_returns_200(self):
        response = client.get("/settlements")
        assert response.status_code == 200

    def test_list_has_total(self):
        response = client.get("/settlements")
        data = response.json()
        assert "total" in data
        assert "settlements" in data

    def test_filter_by_status(self):
        response = client.get("/settlements?status=SETTLED")
        data = response.json()
        for s in data["settlements"]:
            assert s["status"] == "SETTLED"


class TestSettlementStats:
    def test_stats_returns_200(self):
        response = client.get("/settlements/stats")
        assert response.status_code == 200

    def test_stats_has_fields(self):
        response = client.get("/settlements/stats")
        data = response.json()
        assert "total_settlements" in data
        assert "total_gross_minor" in data


class TestSettlementReconciliation:
    def test_recon_returns_200(self):
        response = client.get("/settlements/reconciliation")
        assert response.status_code == 200

    def test_recon_has_summary(self):
        response = client.get("/settlements/reconciliation")
        data = response.json()
        assert "summary" in data
