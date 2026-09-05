"""
API tests for audit trail endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestAuditTrail:
    def test_audit_returns_200(self):
        response = client.get("/audit")
        assert response.status_code == 200

    def test_audit_has_chain_status(self):
        response = client.get("/audit")
        data = response.json()
        assert "chain_valid" in data
        assert "total" in data


class TestAuditVerification:
    def test_verify_returns_200(self):
        response = client.get("/audit/verify")
        assert response.status_code == 200

    def test_verify_has_status(self):
        response = client.get("/audit/verify")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["VERIFIED", "TAMPERED"]
        assert "event_count" in data


class TestAuditExport:
    def test_export_returns_200(self):
        response = client.get("/audit/export")
        assert response.status_code == 200


class TestAuditStatistics:
    def test_statistics_returns_200(self):
        response = client.get("/audit/statistics")
        assert response.status_code == 200
