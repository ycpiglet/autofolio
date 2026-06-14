"""Health endpoint tests — /api/health (no auth required)."""
from __future__ import annotations


def test_health_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_ok_without_cookie(client):
    """Health must not require any session cookie."""
    client.cookies.clear()
    resp = client.get("/api/health")
    assert resp.status_code == 200
