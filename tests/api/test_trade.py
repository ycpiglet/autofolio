"""Trade router contract tests."""
from __future__ import annotations


class TestRecentFills:
    def test_fills_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/trade/fills/recent")
        assert resp.status_code == 200

    def test_fills_guest_403(self, guest_client, mock_backend):
        resp = guest_client.get("/api/trade/fills/recent")
        assert resp.status_code == 403

    def test_fills_shape(self, member_client, mock_backend):
        body = member_client.get("/api/trade/fills/recent").json()
        assert "columns" in body and "rows" in body
        assert "시각" in body["columns"]
        assert "종목" in body["columns"]

    def test_fills_limit_param(self, member_client, mock_backend):
        resp = member_client.get("/api/trade/fills/recent?limit=5")
        assert resp.status_code == 200

    def test_fills_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/trade/fills/recent")
        assert resp.status_code == 401
