"""Analysis router contract tests — attribution / retro / daily-pnl."""
from __future__ import annotations


class TestAttribution:
    def test_attribution_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/analysis/attribution")
        assert resp.status_code == 200

    def test_attribution_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/analysis/attribution").json()
        assert "columns" in body and "rows" in body
        assert "구분" in body["columns"]
        assert "기여(만원)" in body["columns"]

    def test_attribution_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/analysis/attribution")
        assert resp.status_code == 401

    def test_attribution_backend_error_surfaces(self, error_client, monkeypatch):
        """Backend exception must propagate as non-200 (fail-loud)."""
        import app.ui.backend as bmod

        def _raise():
            raise RuntimeError("analysis failure")

        monkeypatch.setattr(bmod, "attribution_df", _raise)
        resp = error_client.get("/api/analysis/attribution")
        assert resp.status_code != 200


class TestRetro:
    def test_retro_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/analysis/retro")
        assert resp.status_code == 200

    def test_retro_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/analysis/retro").json()
        assert "승률" in body
        assert "평균R" in body
        assert "MDD" in body
        assert "규율" in body

    def test_retro_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/analysis/retro")
        assert resp.status_code == 401

    def test_retro_backend_error_surfaces(self, error_client, monkeypatch):
        """Backend exception must propagate as non-200 (fail-loud)."""
        import app.ui.backend as bmod

        def _raise():
            raise RuntimeError("metrics error")

        monkeypatch.setattr(bmod, "retro_metrics", _raise)
        resp = error_client.get("/api/analysis/retro")
        assert resp.status_code != 200


class TestDailyPnl:
    def test_daily_pnl_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/analysis/daily-pnl")
        assert resp.status_code == 200

    def test_daily_pnl_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/analysis/daily-pnl").json()
        assert "columns" in body and "rows" in body
        assert "date" in body["columns"]
        assert "pnl" in body["columns"]

    def test_daily_pnl_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/analysis/daily-pnl")
        assert resp.status_code == 401
