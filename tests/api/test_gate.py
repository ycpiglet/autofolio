"""Auth gate tests — 401 without session, 403 for guest on owner-only routes.

These tests verify the safety seam (require_owner) that will gate all
Phase 3 state-changing endpoints.

The tests use a dedicated owner-only test route registered on the app so
we don't need a real Phase 3 endpoint to test the dependency.
"""
from __future__ import annotations

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.api.deps import require_owner, require_session
from app.api.main import create_app


@pytest.fixture(scope="module")
def app_with_owner_route():
    """App with a synthetic /api/_test/owner-only route for testing require_owner."""
    app = create_app()

    @app.get("/api/_test/owner-only")
    def _owner_only(session=Depends(require_owner)):
        return {"ok": True, "role": session["role"]}

    @app.get("/api/_test/session-only")
    def _session_only(session=Depends(require_session)):
        return {"ok": True, "role": session["role"]}

    return app


@pytest.fixture()
def gated_client(app_with_owner_route):
    return TestClient(app_with_owner_route, raise_server_exceptions=True)


# ── require_session → 401 ─────────────────────────────────────────────────────

class TestRequireSession:
    GUARDED_ROUTES = [
        "/api/engine/status",
        "/api/portfolio/holdings",
        "/api/portfolio/kpis",
        "/api/portfolio/asset-curve",
        "/api/portfolio/allocation-gap",
        "/api/market/indices",
        "/api/market/watchlist",
        "/api/trade/fills/recent",
    ]

    @pytest.mark.parametrize("path", GUARDED_ROUTES)
    def test_route_returns_401_without_session(self, client, path):
        """Every require_session endpoint must return 401 with no cookie."""
        client.cookies.clear()
        resp = client.get(path)
        assert resp.status_code == 401, f"{path} expected 401, got {resp.status_code}"


# ── require_owner → 403 for guest ─────────────────────────────────────────────

class TestRequireOwner:
    def test_guest_gets_403_on_owner_only_route(self, gated_client):
        from app.api.security import encode_session

        gated_client.cookies.set(
            "af_session", encode_session({"role": "guest", "data_source": "demo"})
        )
        resp = gated_client.get("/api/_test/owner-only")
        assert resp.status_code == 403

    def test_owner_gets_200_on_owner_only_route(self, gated_client):
        from app.api.security import encode_session

        gated_client.cookies.set(
            "af_session",
            encode_session({"role": "owner", "username": "alice", "data_source": "backend"}),
        )
        resp = gated_client.get("/api/_test/owner-only")
        assert resp.status_code == 200
        assert resp.json()["role"] == "owner"

    def test_no_session_gets_401_on_owner_only_route(self, gated_client):
        gated_client.cookies.clear()
        resp = gated_client.get("/api/_test/owner-only")
        assert resp.status_code == 401

    def test_guest_gets_200_on_session_only_route(self, gated_client):
        """Guest IS allowed on require_session (not require_owner) routes."""
        from app.api.security import encode_session

        gated_client.cookies.set(
            "af_session", encode_session({"role": "guest", "data_source": "demo"})
        )
        resp = gated_client.get("/api/_test/session-only")
        assert resp.status_code == 200

    def test_no_order_endpoint_exists(self, client):
        """Safety invariant: POST /api/trade/orders must not exist (405 or 404)."""
        resp = client.post("/api/trade/orders", json={})
        assert resp.status_code in (404, 405), (
            f"POST /api/trade/orders must not exist — got {resp.status_code}"
        )
