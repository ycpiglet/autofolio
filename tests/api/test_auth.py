"""Auth router contract and gate tests.

Covers:
- POST /api/auth/login  guest → 403 by default; 200 only with dev opt-in
- POST /api/auth/login  local (mocked) → 200 + cookie
- POST /api/auth/login  local fail → 401
- POST /api/auth/logout → 200, cookie cleared
- GET  /api/auth/me     with valid session → 200
- GET  /api/auth/me     without session → 401
"""
from __future__ import annotations

from unittest.mock import patch


# ── Guest login ────────────────────────────────────────────────────────────────

class TestGuestLogin:
    def test_guest_login_disabled_by_default(self, client, monkeypatch):
        monkeypatch.delenv("AUTOFOLIO_GUEST_DEMO_ENABLED", raising=False)
        resp = client.post("/api/auth/login", json={"guest": True})
        assert resp.status_code == 403
        assert "비활성화" in resp.json()["detail"]

    def test_guest_login_requires_explicit_dev_opt_in(self, client, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_GUEST_DEMO_ENABLED", "1")
        resp = client.post("/api/auth/login", json={"guest": True})
        assert resp.status_code == 200
        assert "af_session" in resp.cookies
        body = resp.json()
        assert body["role"] == "guest"
        assert body["data_source"] == "demo"
        assert body["username"] is None


# ── Local login ────────────────────────────────────────────────────────────────

class TestLocalLogin:
    def test_local_login_ok_sets_owner_session(self, client):
        with patch("app.services.auth_service.login_or_register", return_value=(True, "로그인")):
            resp = client.post(
                "/api/auth/login",
                json={"username": "alice", "password": "secret"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["role"] == "owner"
        assert body["username"] == "alice"
        assert body["data_source"] == "backend"
        assert "af_session" in resp.cookies

    def test_local_login_wrong_password_returns_401(self, client):
        with patch(
            "app.services.auth_service.login_or_register",
            return_value=(False, "비밀번호 불일치"),
        ):
            resp = client.post(
                "/api/auth/login",
                json={"username": "alice", "password": "wrong"},
            )
        assert resp.status_code == 401

    def test_local_login_missing_fields_returns_422(self, client):
        resp = client.post("/api/auth/login", json={"username": "", "password": ""})
        assert resp.status_code == 422

    def test_unknown_local_account_requires_approval(self, client, tmp_path, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
        monkeypatch.delenv("AUTOFOLIO_LOCAL_AUTO_REGISTER", raising=False)

        import importlib

        from app.services import auth_service as auth_mod
        from app.ui import vault as vault_mod

        importlib.reload(vault_mod)
        importlib.reload(auth_mod)

        resp = client.post(
            "/api/auth/login",
            json={"username": "new-user", "password": "secret123"},
        )
        assert resp.status_code == 401
        assert "승인된 계정" in resp.json()["detail"]
        assert vault_mod.load().get("users", {}) == {}


# ── Logout ────────────────────────────────────────────────────────────────────

class TestLogout:
    def test_logout_returns_200(self, guest_client):
        resp = guest_client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["status"] == "logged_out"


# ── /me ───────────────────────────────────────────────────────────────────────

class TestMe:
    def test_me_with_guest_session(self, guest_client):
        resp = guest_client.get("/api/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["role"] == "guest"
        assert body["data_source"] == "demo"

    def test_me_with_owner_session(self, owner_client):
        resp = owner_client.get("/api/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["role"] == "owner"
        assert body["username"] == "testuser"

    def test_me_without_session_returns_401(self, client):
        client.cookies.clear()
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


class TestTamperedCookie:
    def test_tampered_cookie_returns_401(self, client):
        """A garbage/tampered af_session cookie must fail closed (401)."""
        client.cookies.set("af_session", "this.is.garbage.not.a.real.signed.cookie")
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401
