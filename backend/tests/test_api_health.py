"""API tests for health and readiness endpoints."""

import pytest

pytestmark = pytest.mark.unit


def test_health_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data


def test_health_includes_environment(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["environment"] == "development"


def test_root_returns_service_info(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "service" in body
    assert "version" in body


def test_secure_headers_present(client):
    response = client.get("/api/v1/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"


def test_readiness_check_requires_db(client):
    """Readiness endpoint exists (may return 503 with mock DB)."""
    response = client.get("/api/v1/ready")
    assert response.status_code in (200, 503)
