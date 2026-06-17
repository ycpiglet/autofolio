"""Market router contract tests."""
from __future__ import annotations


class TestIndices:
    def test_indices_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/indices")
        assert resp.status_code == 200

    def test_indices_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/indices").json()
        assert "columns" in body and "rows" in body

    def test_indices_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/indices")
        assert resp.status_code == 401


class TestWatchlist:
    def test_watchlist_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/watchlist")
        assert resp.status_code == 200

    def test_watchlist_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/watchlist").json()
        assert "columns" in body and "rows" in body
        assert "symbol" in body["columns"]
        assert "price" in body["columns"]

    def test_watchlist_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/watchlist")
        assert resp.status_code == 401


class TestSymbols:
    def test_symbols_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/symbols")
        assert resp.status_code == 200

    def test_symbols_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/symbols").json()
        # Should be a dict mapping code -> name
        assert isinstance(body, dict)
        assert "005930" in body
        assert body["005930"] == "삼성전자"

    def test_symbols_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/symbols")
        assert resp.status_code == 401

    def test_symbols_empty_when_whitelist_empty(self, guest_client, monkeypatch):
        import pandas as pd
        import app.services.backend as backend_mod
        monkeypatch.setattr(backend_mod, "list_whitelist", lambda: pd.DataFrame())
        resp = guest_client.get("/api/market/symbols")
        assert resp.status_code == 200
        assert resp.json() == {}
