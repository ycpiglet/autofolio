"""Market router Phase 2 contract tests — price / fundamental / order-book /
intraday / sectors / disclosures."""
from __future__ import annotations

import pytest


class TestPrice:
    def test_price_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/price?symbol=005930")
        assert resp.status_code == 200

    def test_price_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/price?symbol=005930").json()
        assert body["symbol"] == "005930"
        assert body["price"] == 75_000.0

    def test_price_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/price?symbol=005930")
        assert resp.status_code == 401

    def test_price_invalid_symbol_422(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/price?symbol=" + "A" * 30)
        assert resp.status_code == 422

    def test_price_backend_error_surfaces(self, error_client, monkeypatch):
        """Backend exception must not produce a silent empty 200."""
        import app.services.backend as bmod

        def _raise(sym):
            raise RuntimeError("KIS down")

        monkeypatch.setattr(bmod, "price", _raise)
        resp = error_client.get("/api/market/price?symbol=005930")
        assert resp.status_code != 200


class TestFundamental:
    def test_fundamental_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/fundamental?symbol=005930")
        assert resp.status_code == 200

    def test_fundamental_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/fundamental?symbol=005930").json()
        assert "per" in body

    def test_fundamental_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/fundamental?symbol=005930")
        assert resp.status_code == 401


class TestOrderBook:
    def test_order_book_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/order-book?symbol=005930")
        assert resp.status_code == 200

    def test_order_book_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/order-book?symbol=005930").json()
        assert "columns" in body and "rows" in body
        assert "level" in body["columns"]

    def test_order_book_market_param(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/order-book?symbol=005930&market=J")
        assert resp.status_code == 200

    def test_order_book_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/order-book?symbol=005930")
        assert resp.status_code == 401


class TestIntraday:
    def test_intraday_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/intraday?symbol=005930")
        assert resp.status_code == 200

    def test_intraday_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/intraday?symbol=005930").json()
        assert "columns" in body and "rows" in body

    def test_intraday_params(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/intraday?symbol=005930&time_unit=5&count=30")
        assert resp.status_code == 200

    def test_intraday_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/intraday?symbol=005930")
        assert resp.status_code == 401


class TestSectors:
    def test_sectors_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/sectors")
        assert resp.status_code == 200

    def test_sectors_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/sectors").json()
        assert "columns" in body and "rows" in body
        assert "name" in body["columns"]

    def test_sectors_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/sectors")
        assert resp.status_code == 401


class TestDisclosures:
    def test_disclosures_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/disclosures?symbol=005930")
        assert resp.status_code == 200

    def test_disclosures_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/market/disclosures?symbol=005930").json()
        assert "columns" in body and "rows" in body
        assert "title" in body["columns"]

    def test_disclosures_days_param(self, guest_client, mock_backend):
        resp = guest_client.get("/api/market/disclosures?symbol=005930&days=5")
        assert resp.status_code == 200

    def test_disclosures_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/market/disclosures?symbol=005930")
        assert resp.status_code == 401
