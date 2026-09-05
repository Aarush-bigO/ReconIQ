"""
API tests for transactions endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app, raise_server_exceptions=False)


class TestListTransactions:
    def test_list_returns_200(self):
        response = client.get("/transactions")
        assert response.status_code == 200

    def test_list_has_pagination(self):
        response = client.get("/transactions")
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "records" in data

    def test_list_with_page_size(self):
        response = client.get("/transactions?page_size=10")
        data = response.json()
        assert len(data["records"]) <= 10

    def test_filter_by_source(self):
        response = client.get("/transactions?source=Razorpay")
        data = response.json()
        for record in data["records"]:
            assert record["source"] == "Razorpay"


class TestTransactionDetail:
    def test_invalid_id_returns_404(self):
        response = client.get("/transactions/nonexistent_id_12345")
        assert response.status_code == 404


class TestTransactionStats:
    def test_stats_returns_200(self):
        response = client.get("/transactions/stats")
        assert response.status_code == 200

    def test_stats_has_fields(self):
        response = client.get("/transactions/stats")
        data = response.json()
        assert "total_transactions" in data
        assert "by_source" in data
        assert "by_status" in data
