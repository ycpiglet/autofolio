"""Phase 3 state-changing endpoints — safety gate tests.

Coverage:
- CSRF: all state-changing endpoints reject missing/wrong token; accept correct token
- no session 401: all state-changing endpoints reject anonymous callers
- guest 403: all state-changing endpoints reject guest
- kill-switch: owner can toggle; DB updated
- auto-trading: owner can toggle; DB updated
- run-once single-flight: 409 when locked, 200 when unlocked
- trade/conditions gate mapping: all GateResult variants → correct HTTP status
- ack_token 2-step: valid ack→201, tampered→409, expired→409, payload mismatch→409
- ConditionRequest schema: invalid side / zero quantity / non-positive price → 422
- secure cookie guard: AUTOFOLIO_ENV=production → secure=True
- NO POST /api/trade/orders: assert 404
- /me returns csrf_token for authed session
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_ack_token, encode_session


# ── Fixtures ──────────────────────────────────────────────────────────────────

CSRF = "deadbeefcafe" * 5  # 60-char hex — deterministic for tests


def _owner_session(csrf: str = CSRF) -> str:
    return encode_session({
        "role": "owner",
        "username": "testuser",
        "data_source": "backend",
        "csrf_token": csrf,
    })


def _guest_session() -> str:
    return encode_session({
        "role": "guest",
        "data_source": "demo",
        "csrf_token": CSRF,
    })


@pytest.fixture(scope="module")
def app():
    return create_app()


@pytest.fixture()
def owner_client(app):
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("af_session", _owner_session())
    return c


@pytest.fixture()
def guest_client(app):
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("af_session", _guest_session())
    return c


@pytest.fixture()
def anon_client(app):
    return TestClient(app, raise_server_exceptions=True)


def owner_headers(csrf: str = CSRF) -> dict:
    return {"X-CSRF-Token": csrf}


# ── /me csrf_token ────────────────────────────────────────────────────────────

class TestMeCsrfToken:
    def test_me_returns_csrf_token_for_owner(self, owner_client):
        resp = owner_client.get("/api/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["csrf_token"] == CSRF

    def test_me_returns_csrf_token_for_guest(self, guest_client):
        resp = guest_client.get("/api/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["csrf_token"] == CSRF

    def test_me_401_without_session(self, anon_client):
        resp = anon_client.get("/api/auth/me")
        assert resp.status_code == 401


# ── CSRF + guest 403 sweep ────────────────────────────────────────────────────

STATE_CHANGING_ENDPOINTS = [
    ("POST", "/api/engine/kill-switch", {"active": False}),
    ("POST", "/api/engine/auto-trading", {"enabled": False}),
    ("POST", "/api/engine/run-once", None),
    ("POST", "/api/trade/conditions", {"symbol": "005930", "side": "BUY", "target_price": 70000.0, "quantity": 1}),
    ("PUT", "/api/settings/risk-limits", {"max_order_amount": 100000.0}),
]


class TestNoSessionBlocked:
    """Anonymous callers (no session cookie at all) must get 401 on every state-changing endpoint."""

    @pytest.mark.parametrize("method,path,body", STATE_CHANGING_ENDPOINTS)
    def test_anon_gets_401(self, anon_client, method, path, body):
        fn = getattr(anon_client, method.lower())
        resp = fn(path, json=body, headers=owner_headers())
        assert resp.status_code == 401, (
            f"{method} {path}: expected 401 for anonymous caller, got {resp.status_code}"
        )


class TestGuestBlocked:
    @pytest.mark.parametrize("method,path,body", STATE_CHANGING_ENDPOINTS)
    def test_guest_gets_403(self, guest_client, method, path, body):
        fn = getattr(guest_client, method.lower())
        resp = fn(path, json=body, headers=owner_headers())
        assert resp.status_code == 403, f"{method} {path}: expected 403 for guest, got {resp.status_code}"


class TestCsrfRequired:
    @pytest.mark.parametrize("method,path,body", STATE_CHANGING_ENDPOINTS)
    def test_missing_csrf_gets_403(self, owner_client, method, path, body):
        fn = getattr(owner_client, method.lower())
        resp = fn(path, json=body)   # no X-CSRF-Token header
        assert resp.status_code == 403, f"{method} {path}: expected 403 for missing CSRF"

    @pytest.mark.parametrize("method,path,body", STATE_CHANGING_ENDPOINTS)
    def test_wrong_csrf_gets_403(self, owner_client, method, path, body):
        fn = getattr(owner_client, method.lower())
        resp = fn(path, json=body, headers={"X-CSRF-Token": "wrongtoken"})
        assert resp.status_code == 403, f"{method} {path}: expected 403 for wrong CSRF"


# ── Kill switch ───────────────────────────────────────────────────────────────

class TestKillSwitch:
    def test_kill_switch_activate(self, owner_client):
        with patch("app.ui.backend.set_flag") as mock_set, \
             patch("app.ui.backend.get_flag", return_value=True):
            resp = owner_client.post(
                "/api/engine/kill-switch",
                json={"active": True},
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["kill_switch_active"] is True
        mock_set.assert_called_once_with("kill_switch_active", True)

    def test_kill_switch_deactivate(self, owner_client):
        with patch("app.ui.backend.set_flag") as mock_set, \
             patch("app.ui.backend.get_flag", return_value=False):
            resp = owner_client.post(
                "/api/engine/kill-switch",
                json={"active": False},
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        assert resp.json()["kill_switch_active"] is False
        mock_set.assert_called_once_with("kill_switch_active", False)

    def test_kill_switch_guest_403(self, guest_client):
        resp = guest_client.post(
            "/api/engine/kill-switch",
            json={"active": True},
            headers=owner_headers(),
        )
        assert resp.status_code == 403


# ── Auto-trading ──────────────────────────────────────────────────────────────

class TestAutoTrading:
    def test_auto_trading_enable(self, owner_client):
        with patch("app.ui.backend.set_flag") as mock_set, \
             patch("app.ui.backend.get_flag", return_value=True):
            resp = owner_client.post(
                "/api/engine/auto-trading",
                json={"enabled": True},
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        assert resp.json()["auto_trading_enabled"] is True
        mock_set.assert_called_once_with("auto_trading_enabled", True)

    def test_auto_trading_disable(self, owner_client):
        with patch("app.ui.backend.set_flag") as mock_set, \
             patch("app.ui.backend.get_flag", return_value=False):
            resp = owner_client.post(
                "/api/engine/auto-trading",
                json={"enabled": False},
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        assert resp.json()["auto_trading_enabled"] is False


# ── Run-once single-flight ────────────────────────────────────────────────────

class TestRunOnce:
    def test_run_once_200(self, owner_client):
        with patch("app.ui.backend.run_engine_once", return_value=["BUY 005930 done"]):
            resp = owner_client.post(
                "/api/engine/run-once",
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["results"] == ["BUY 005930 done"]

    def test_run_once_409_when_locked(self, app, owner_client):
        """Simulate the single-flight lock already held → 409."""
        import app.api.routers.engine as engine_mod

        # Acquire the lock externally to simulate a concurrent run
        acquired = engine_mod._run_once_lock.acquire(blocking=False)
        assert acquired, "Lock should be free at test start"
        try:
            resp = owner_client.post(
                "/api/engine/run-once",
                headers=owner_headers(),
            )
            assert resp.status_code == 409
            assert "이미 실행 중" in resp.json()["detail"]
        finally:
            engine_mod._run_once_lock.release()

    def test_run_once_lock_released_after_success(self, app, owner_client):
        """Lock must be released after run completes so a second call can proceed."""
        with patch("app.ui.backend.run_engine_once", return_value=[]):
            resp1 = owner_client.post("/api/engine/run-once", headers=owner_headers())
            resp2 = owner_client.post("/api/engine/run-once", headers=owner_headers())
        assert resp1.status_code == 200
        assert resp2.status_code == 200

    def test_run_once_lock_released_after_exception(self, app, owner_client):
        """Lock must be released even when run_engine_once raises."""
        err_client = TestClient(create_app(), raise_server_exceptions=False)
        err_client.cookies.set("af_session", _owner_session())

        with patch("app.ui.backend.run_engine_once", side_effect=RuntimeError("boom")):
            resp = err_client.post("/api/engine/run-once", headers=owner_headers())
        # Server returns 500 (fail-closed)
        assert resp.status_code == 500

        # Lock should be free now — a fresh call should work
        with patch("app.ui.backend.run_engine_once", return_value=[]):
            resp2 = err_client.post("/api/engine/run-once", headers=owner_headers())
        assert resp2.status_code == 200


# ── POST /api/trade/conditions gate mapping ───────────────────────────────────

from app.services.trading import GateResult


class TestConditionsPost:
    _BODY = {
        "symbol": "005930",
        "side": "BUY",
        "target_price": 70000.0,
        "quantity": 1,
        "auto": False,
    }

    def _post(self, client, body=None, headers=None):
        return client.post(
            "/api/trade/conditions",
            json=body if body is not None else self._BODY,
            headers=headers if headers is not None else owner_headers(),
        )

    def test_saved_returns_201(self, owner_client):
        gate = GateResult(status="saved", message="저장됨", condition_id=42)
        with patch("app.services.trading.save_condition_with_gates", return_value=gate):
            resp = self._post(owner_client)
        assert resp.status_code == 201
        assert resp.json()["status"] == "saved"
        assert resp.json()["condition_id"] == 42

    def test_blocked_disclosure_returns_422(self, owner_client):
        gate = GateResult(status="blocked_disclosure", message="공시 차단")
        with patch("app.services.trading.save_condition_with_gates", return_value=gate):
            resp = self._post(owner_client)
        assert resp.status_code == 422
        assert resp.json()["detail"]["status"] == "blocked_disclosure"

    def test_rejected_returns_422(self, owner_client):
        gate = GateResult(status="rejected", message="법규 위반")
        with patch("app.services.trading.save_condition_with_gates", return_value=gate):
            resp = self._post(owner_client)
        assert resp.status_code == 422
        assert resp.json()["detail"]["status"] == "rejected"

    def test_needs_acknowledgement_returns_409_with_ack_token(self, owner_client):
        gate = GateResult(status="needs_acknowledgement", message="CAUTION: 리스크 주의")
        with patch("app.services.trading.save_condition_with_gates", return_value=gate):
            resp = self._post(owner_client)
        assert resp.status_code == 409
        detail = resp.json()["detail"]
        assert detail["status"] == "needs_acknowledgement"
        assert "ack_token" in detail
        assert len(detail["ack_token"]) > 10  # non-empty signed token

    def test_error_returns_500(self, app):
        gate = GateResult(status="error", message="에이전트 오류")
        err_client = TestClient(create_app(), raise_server_exceptions=False)
        err_client.cookies.set("af_session", _owner_session())
        with patch("app.services.trading.save_condition_with_gates", return_value=gate):
            resp = err_client.post(
                "/api/trade/conditions",
                json=self._BODY,
                headers=owner_headers(),
            )
        assert resp.status_code == 500

    def test_guest_gets_403(self, guest_client):
        resp = self._post(guest_client)
        assert resp.status_code == 403

    def test_missing_csrf_gets_403(self, owner_client):
        resp = owner_client.post("/api/trade/conditions", json=self._BODY)
        assert resp.status_code == 403

    # ── ack_token 2-step ──────────────────────────────────────────────────────

    def test_valid_ack_token_saves(self, owner_client):
        """Valid ack_token with matching payload → 201."""
        # Step 1: get the ack_token
        gate_ack = GateResult(status="needs_acknowledgement", message="CAUTION: 주의")
        with patch("app.services.trading.save_condition_with_gates", return_value=gate_ack):
            resp1 = self._post(owner_client)
        assert resp1.status_code == 409
        ack_token = resp1.json()["detail"]["ack_token"]

        # Step 2: re-submit with ack_token → should save
        gate_saved = GateResult(status="saved", message="저장됨", condition_id=1)
        with patch("app.services.trading.save_condition_with_gates", return_value=gate_saved) as mock_gate:
            body_with_ack = {**self._BODY, "ack_token": ack_token}
            resp2 = owner_client.post(
                "/api/trade/conditions",
                json=body_with_ack,
                headers=owner_headers(),
            )
        assert resp2.status_code == 201
        # Confirm caution_acknowledged=True was passed
        call_kwargs = mock_gate.call_args
        assert call_kwargs.kwargs.get("caution_acknowledged") is True

    def test_tampered_ack_token_treated_as_no_ack(self, owner_client):
        """Tampered ack_token → fail-closed: re-run gate without caution_acknowledged."""
        gate_ack = GateResult(status="needs_acknowledgement", message="CAUTION: 주의")
        with patch("app.services.trading.save_condition_with_gates", return_value=gate_ack) as mock_gate:
            resp = owner_client.post(
                "/api/trade/conditions",
                json={**self._BODY, "ack_token": "tampered.garbage.token"},
                headers=owner_headers(),
            )
        assert resp.status_code == 409
        # Must have been called with caution_acknowledged=False (not acknowledged)
        call_kwargs = mock_gate.call_args
        assert call_kwargs.kwargs.get("caution_acknowledged") is False

    def test_mismatched_payload_ack_token_treated_as_no_ack(self, owner_client):
        """ack_token signed for a different body → fail-closed."""
        # Sign a token for a DIFFERENT symbol
        wrong_token = encode_ack_token({
            "symbol": "WRONG",
            "side": "BUY",
            "target_price": 70000.0,
            "quantity": 1,
        })
        gate_ack = GateResult(status="needs_acknowledgement", message="CAUTION: 주의")
        with patch("app.services.trading.save_condition_with_gates", return_value=gate_ack) as mock_gate:
            resp = owner_client.post(
                "/api/trade/conditions",
                json={**self._BODY, "ack_token": wrong_token},
                headers=owner_headers(),
            )
        assert resp.status_code == 409
        call_kwargs = mock_gate.call_args
        assert call_kwargs.kwargs.get("caution_acknowledged") is False

    def test_expired_ack_token_treated_as_no_ack(self, owner_client):
        """An EXPIRED ack_token must fail closed → re-gated to 409, condition NOT saved.

        Simulates expiry by patching decode_ack_token (as used in the router) to return
        None — exactly what itsdangerous.SignatureExpired produces on a real expired token.
        """
        # A syntactically valid (but expired) token — content doesn't matter because
        # decode_ack_token is patched to return None (= expired/invalid).
        some_valid_looking_token = encode_ack_token({
            "symbol": self._BODY["symbol"],
            "side": self._BODY["side"],
            "target_price": self._BODY["target_price"],
            "quantity": self._BODY["quantity"],
        })

        gate_ack = GateResult(status="needs_acknowledgement", message="CAUTION: 주의")
        # Patch decode_ack_token in the router's module namespace to simulate expiry
        with patch("app.api.routers.trade.decode_ack_token", return_value=None), \
             patch("app.services.trading.save_condition_with_gates", return_value=gate_ack) as mock_gate:
            resp = owner_client.post(
                "/api/trade/conditions",
                json={**self._BODY, "ack_token": some_valid_looking_token},
                headers=owner_headers(),
            )

        # Expired token must be treated as no acknowledgement → re-gated → 409
        assert resp.status_code == 409
        # Confirm condition was NOT saved (caution_acknowledged=False)
        call_kwargs = mock_gate.call_args
        assert call_kwargs.kwargs.get("caution_acknowledged") is False


# ── ConditionRequest schema validation ───────────────────────────────────────

class TestConditionRequestSchema:
    """FastAPI/Pydantic should reject invalid payloads before reaching the service."""

    def _post(self, client, body):
        return client.post(
            "/api/trade/conditions",
            json=body,
            headers=owner_headers(),
        )

    def test_invalid_side_returns_422(self, owner_client):
        """side must be BUY or SELL — anything else is 422."""
        body = {"symbol": "005930", "side": "HOLD", "target_price": 70000.0, "quantity": 1}
        resp = self._post(owner_client, body)
        assert resp.status_code == 422, f"Expected 422 for invalid side, got {resp.status_code}"

    def test_zero_quantity_returns_422(self, owner_client):
        """quantity must be >= 1."""
        body = {"symbol": "005930", "side": "BUY", "target_price": 70000.0, "quantity": 0}
        resp = self._post(owner_client, body)
        assert resp.status_code == 422, f"Expected 422 for zero quantity, got {resp.status_code}"

    def test_negative_quantity_returns_422(self, owner_client):
        """quantity < 1 must be rejected."""
        body = {"symbol": "005930", "side": "BUY", "target_price": 70000.0, "quantity": -5}
        resp = self._post(owner_client, body)
        assert resp.status_code == 422, f"Expected 422 for negative quantity, got {resp.status_code}"

    def test_zero_target_price_returns_422(self, owner_client):
        """target_price must be > 0."""
        body = {"symbol": "005930", "side": "BUY", "target_price": 0.0, "quantity": 1}
        resp = self._post(owner_client, body)
        assert resp.status_code == 422, f"Expected 422 for zero target_price, got {resp.status_code}"

    def test_negative_target_price_returns_422(self, owner_client):
        """Negative target_price must be rejected."""
        body = {"symbol": "005930", "side": "SELL", "target_price": -100.0, "quantity": 1}
        resp = self._post(owner_client, body)
        assert resp.status_code == 422, f"Expected 422 for negative target_price, got {resp.status_code}"


# ── Secure cookie production guard ────────────────────────────────────────────

class TestSecureCookieGuard:
    def test_secure_false_by_default(self):
        """Without AUTOFOLIO_ENV=production, COOKIE_KWARGS.secure must be False."""
        import os
        os.environ.pop("AUTOFOLIO_ENV", None)
        import importlib
        import app.api.security as sec_mod
        importlib.reload(sec_mod)
        assert sec_mod.COOKIE_KWARGS["secure"] is False

    def test_secure_true_in_production(self, monkeypatch):
        """With AUTOFOLIO_ENV=production, COOKIE_KWARGS.secure must be True."""
        monkeypatch.setenv("AUTOFOLIO_ENV", "production")
        import importlib
        import app.api.security as sec_mod
        importlib.reload(sec_mod)
        assert sec_mod.COOKIE_KWARGS["secure"] is True
        # Restore: reload without the env var so other tests aren't affected
        monkeypatch.delenv("AUTOFOLIO_ENV", raising=False)
        importlib.reload(sec_mod)


# ── No direct order endpoint ──────────────────────────────────────────────────

class TestNoOrderEndpoint:
    def test_post_trade_orders_is_404(self, anon_client):
        resp = anon_client.post("/api/trade/orders", json={})
        assert resp.status_code in (404, 405)


# ── PUT /api/settings/risk-limits ────────────────────────────────────────────

class TestRiskLimits:
    def test_risk_limits_saves(self, owner_client):
        with patch("app.ui.backend.set_risk_limits") as mock_set:
            resp = owner_client.put(
                "/api/settings/risk-limits",
                json={"max_order_amount": 100000.0, "max_daily_amount": 300000.0},
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "saved"
        mock_set.assert_called_once_with(
            max_order_amount=100000.0,
            max_daily_amount=300000.0,
        )

    def test_risk_limits_partial_update(self, owner_client):
        """Only max_order_amount provided — max_daily_amount should be None."""
        with patch("app.ui.backend.set_risk_limits") as mock_set:
            resp = owner_client.put(
                "/api/settings/risk-limits",
                json={"max_order_amount": 50000.0},
                headers=owner_headers(),
            )
        assert resp.status_code == 200
        mock_set.assert_called_once_with(
            max_order_amount=50000.0,
            max_daily_amount=None,
        )

    def test_risk_limits_guest_403(self, guest_client):
        resp = guest_client.put(
            "/api/settings/risk-limits",
            json={"max_order_amount": 100000.0},
            headers=owner_headers(),
        )
        assert resp.status_code == 403

    def test_risk_limits_missing_csrf_403(self, owner_client):
        resp = owner_client.put(
            "/api/settings/risk-limits",
            json={"max_order_amount": 100000.0},
        )
        assert resp.status_code == 403
