"""Engine router contract tests."""
from __future__ import annotations


class TestEngineStatus:
    def test_status_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/engine/status")
        assert resp.status_code == 200

    def test_status_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/engine/status").json()
        assert "env" in body
        assert "auto_trading_enabled" in body
        assert "kill_switch_active" in body
        assert "circuit_breaker" in body
        cb = body["circuit_breaker"]
        assert "triggered" in cb
        assert "threshold_pct" in cb
        assert "consecutive_failures" in cb
        assert "today_pnl" in cb

    def test_status_env_value(self, guest_client, mock_backend):
        body = guest_client.get("/api/engine/status").json()
        assert body["env"] == "mock"

    def test_status_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/engine/status")
        assert resp.status_code == 401
