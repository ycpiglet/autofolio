"""Account router contract + safety tests — /api/account/*

Covers:
- GET  /api/account              shape (no secrets), owner/guest, 401 no-session
- POST /api/account/password     happy path (owner + CSRF)
- POST /api/account/password     wrong-old → 401
- POST /api/account/password     weak-new → 400
- POST /api/account/password     guest → 403 (require_owner)
- POST /api/account/password     no-session → 401
- POST /api/account/password     missing CSRF → 403
- POST /api/account/password     username comes from SESSION, not body
"""
from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session

CSRF = "csrf-token-account-test"


def _owner_session(username: str = "alice") -> str:
    return encode_session(
        {
            "role": "owner",
            "username": username,
            "data_source": "backend",
            "csrf_token": CSRF,
        }
    )


def _guest_session() -> str:
    return encode_session(
        {"role": "guest", "data_source": "demo", "csrf_token": CSRF}
    )


def _client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


# ── GET /api/account ───────────────────────────────────────────────────────────

class TestGetAccount:
    def test_owner_shape(self):
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = c.get("/api/account")
        assert resp.status_code == 200
        body = resp.json()
        assert body == {
            "username": "alice",
            "role": "owner",
            "data_source": "backend",
            "is_owner": True,
        }

    def test_guest_shape_is_owner_false(self):
        c = _client()
        c.cookies.set("af_session", _guest_session())
        resp = c.get("/api/account")
        assert resp.status_code == 200
        body = resp.json()
        assert body["role"] == "guest"
        assert body["is_owner"] is False
        assert body["username"] is None

    def test_no_session_returns_401(self):
        c = _client()
        resp = c.get("/api/account")
        assert resp.status_code == 401

    def test_no_secret_in_response(self):
        """Response must never leak password/hash/salt/secret/csrf."""
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = c.get("/api/account")
        assert resp.status_code == 200
        raw = resp.text.lower()
        for forbidden in ("password", "hash", "salt", "secret", "csrf"):
            assert forbidden not in raw, f"leaked {forbidden!r}"
        # Explicit key check too.
        body = resp.json()
        for forbidden_key in ("password", "hash", "salt", "secret", "csrf_token"):
            assert forbidden_key not in body


# ── POST /api/account/password ──────────────────────────────────────────────────

class TestChangePassword:
    def _post(self, c: TestClient, body: dict[str, Any], csrf: str | None = CSRF):
        headers = {"X-CSRF-Token": csrf} if csrf is not None else {}
        return c.post("/api/account/password", json=body, headers=headers)

    def test_happy_path_owner(self, monkeypatch):
        captured: dict[str, Any] = {}

        def fake_change(username, old, new):
            captured["username"] = username
            captured["old"] = old
            captured["new"] = new
            return True, "비밀번호가 변경되었습니다."

        monkeypatch.setattr(
            "app.services.auth_service.change_password", fake_change
        )
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = self._post(
            c, {"old_password": "oldpass12", "new_password": "newpass34"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "changed"
        # username MUST come from session, not the body.
        assert captured["username"] == "alice"

    def test_username_from_session_not_body(self, monkeypatch):
        """Even if the body carries a username, the session's is used."""
        captured: dict[str, Any] = {}

        def fake_change(username, old, new):
            captured["username"] = username
            return True, "ok"

        monkeypatch.setattr(
            "app.services.auth_service.change_password", fake_change
        )
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        # Attacker tries to target "victim" via the body — must be ignored.
        resp = self._post(
            c,
            {
                "old_password": "oldpass12",
                "new_password": "newpass34",
                "username": "victim",
            },
        )
        assert resp.status_code == 200
        assert captured["username"] == "alice"

    def test_wrong_old_returns_401(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.auth_service.change_password",
            lambda u, o, n: (False, "현재 비밀번호가 일치하지 않습니다."),
        )
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = self._post(
            c, {"old_password": "wrongpass", "new_password": "newpass34"}
        )
        assert resp.status_code == 401

    def test_weak_new_returns_400(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.auth_service.change_password",
            lambda u, o, n: (False, "새 비밀번호는 최소 8자 이상이어야 합니다."),
        )
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = self._post(c, {"old_password": "oldpass12", "new_password": "x"})
        assert resp.status_code == 400

    def test_guest_returns_403(self):
        c = _client()
        c.cookies.set("af_session", _guest_session())
        resp = self._post(
            c, {"old_password": "oldpass12", "new_password": "newpass34"}
        )
        assert resp.status_code == 403

    def test_no_session_returns_401(self):
        c = _client()
        resp = self._post(
            c, {"old_password": "oldpass12", "new_password": "newpass34"}
        )
        assert resp.status_code == 401

    def test_missing_csrf_returns_403(self):
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = self._post(
            c,
            {"old_password": "oldpass12", "new_password": "newpass34"},
            csrf=None,
        )
        assert resp.status_code == 403

    def test_change_password_does_not_echo_password(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.auth_service.change_password",
            lambda u, o, n: (True, "비밀번호가 변경되었습니다."),
        )
        c = _client()
        c.cookies.set("af_session", _owner_session("alice"))
        resp = self._post(
            c, {"old_password": "topsecret1", "new_password": "newsecret2"}
        )
        assert resp.status_code == 200
        assert "topsecret1" not in resp.text
        assert "newsecret2" not in resp.text


# ── auth_service.change_password unit-level behavior ─────────────────────────────

class TestChangePasswordService:
    def _isolate_vault(self, tmp_path, monkeypatch):
        """Point the vault at a throwaway dir so we never touch real data."""
        monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
        # Reset cached fernet/paths by reloading vault module-level dirs.
        import importlib

        from app.ui import vault as vault_mod

        importlib.reload(vault_mod)
        return vault_mod

    def test_full_roundtrip(self, tmp_path, monkeypatch):
        self._isolate_vault(tmp_path, monkeypatch)
        import importlib

        from app.services import auth_service as svc
        importlib.reload(svc)

        ok, _ = svc.login_or_register("bob", "origpass1")
        assert ok

        # Wrong old → fail.
        ok, msg = svc.change_password("bob", "nope", "brandnew9")
        assert ok is False
        assert "현재 비밀번호" in msg

        # Too short → fail.
        ok, _ = svc.change_password("bob", "origpass1", "short")
        assert ok is False

        # Same as old → fail.
        ok, _ = svc.change_password("bob", "origpass1", "origpass1")
        assert ok is False

        # Happy path.
        ok, _ = svc.change_password("bob", "origpass1", "brandnew9")
        assert ok is True

        # Old password no longer works; new one does.
        assert svc.login_or_register("bob", "origpass1")[0] is False
        assert svc.login_or_register("bob", "brandnew9")[0] is True
