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
