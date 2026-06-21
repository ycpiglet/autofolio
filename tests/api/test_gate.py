"""Auth gate tests — 401 without session, 403 for guest on guarded routes.

These tests verify the safety seams:
- require_owner gates Owner/admin-only surfaces.
- require_app_user gates approved self-service surfaces.

The tests use dedicated test routes so we don't need real endpoints to test the
dependencies.
"""
from __future__ import annotations

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from app.api.deps import require_app_user, require_owner, require_session
from app.api.main import create_app


@pytest.fixture(scope="module")
def app_with_owner_route():
    """App with a synthetic /api/_test/owner-only route for testing require_owner."""
    app = create_app()

    @app.get("/api/_test/owner-only")
    def _owner_only(session=Depends(require_owner)):
        return {"ok": True, "role": session["role"]}

    @app.get("/api/_test/app-user")
    def _app_user(session=Depends(require_app_user)):
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

    def test_member_gets_403_on_owner_only_route(self, gated_client):
        from app.api.security import encode_session

        gated_client.cookies.set(
            "af_session",
            encode_session({"role": "member", "username": "alice", "data_source": "backend"}),
        )
        resp = gated_client.get("/api/_test/owner-only")
        assert resp.status_code == 403

    def test_member_gets_200_on_app_user_route(self, gated_client):
        from app.api.security import encode_session

        gated_client.cookies.set(
            "af_session",
            encode_session({"role": "member", "username": "alice", "data_source": "backend"}),
        )
        resp = gated_client.get("/api/_test/app-user")
        assert resp.status_code == 200
        assert resp.json()["role"] == "member"

    def test_guest_gets_403_on_app_user_route(self, gated_client):
        from app.api.security import encode_session

        gated_client.cookies.set(
            "af_session", encode_session({"role": "guest", "data_source": "demo"})
        )
        resp = gated_client.get("/api/_test/app-user")
        assert resp.status_code == 403

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

    def test_member_cannot_mutate_global_engine_state(self, client):
        from app.api.security import encode_session

        csrf = "csrf-member"
        client.cookies.set(
            "af_session",
            encode_session(
                {
                    "role": "member",
                    "username": "alice",
                    "data_source": "backend",
                    "csrf_token": csrf,
                }
            ),
        )
        resp = client.post(
            "/api/engine/kill-switch",
            json={"active": True},
            headers={"X-CSRF-Token": csrf},
        )
        assert resp.status_code == 403
