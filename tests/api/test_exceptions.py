"""
API tests for exceptions endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestListExceptions:
    def test_list_returns_200(self):
        response = client.get("/exceptions")
        assert response.status_code == 200

    def test_list_has_structure(self):
        response = client.get("/exceptions")
        data = response.json()
        assert "total" in data
        assert "exceptions" in data

    def test_list_with_severity_filter(self):
        response = client.get("/exceptions?severity=HIGH")
        assert response.status_code == 200

    def test_list_with_status_filter(self):
        response = client.get("/exceptions?status=OPEN")
        assert response.status_code == 200


class TestExceptionSummary:
    def test_summary_returns_200(self):
        response = client.get("/exceptions/summary")
        assert response.status_code == 200


class TestExceptionStats:
    def test_stats_returns_200(self):
        response = client.get("/exceptions/stats")
        assert response.status_code == 200

    def test_stats_has_breakdowns(self):
        response = client.get("/exceptions/stats")
        data = response.json()
        assert "total_exceptions" in data
        assert "by_severity" in data
        assert "by_status" in data
        assert "by_reason_code" in data


class TestExceptionDetail:
    def test_invalid_id_returns_404(self):
        response = client.get("/exceptions/nonexistent_exception_id")
        assert response.status_code == 404


class TestExceptionWorkflow:
    def test_assign_invalid_id_returns_404(self):
        response = client.post("/exceptions/nonexistent/assign", json={"assignee": "test_user"})
        assert response.status_code == 404

    def test_review_invalid_id_returns_404(self):
        response = client.post("/exceptions/nonexistent/review", json={"action": "resolve", "resolution_type": "FALSE_POSITIVE"})
        assert response.status_code == 404
