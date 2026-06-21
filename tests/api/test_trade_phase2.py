"""Trade router Phase 2 contract tests — conditions / orders."""
from __future__ import annotations


class TestConditions:
    def test_conditions_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/trade/conditions")
        assert resp.status_code == 200

    def test_conditions_guest_403(self, guest_client, mock_backend):
        resp = guest_client.get("/api/trade/conditions")
        assert resp.status_code == 403

    def test_conditions_shape(self, member_client, mock_backend):
        body = member_client.get("/api/trade/conditions").json()
        assert "columns" in body and "rows" in body
        assert "symbol" in body["columns"]

    def test_conditions_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/trade/conditions")
        assert resp.status_code == 401

    def test_conditions_backend_error_surfaces(self, error_member_client, monkeypatch):
        """Backend exception must not produce a silent empty 200."""
        import app.services.backend as bmod

        def _raise():
            raise RuntimeError("DB error")

        monkeypatch.setattr(bmod, "list_conditions", _raise)
        resp = error_member_client.get("/api/trade/conditions")
        assert resp.status_code != 200


class TestOrders:
    def test_orders_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/trade/orders")
        assert resp.status_code == 200

    def test_orders_shape(self, member_client, mock_backend):
        body = member_client.get("/api/trade/orders").json()
        assert "columns" in body and "rows" in body
        assert "symbol" in body["columns"]

    def test_orders_limit_param(self, member_client, mock_backend):
        resp = member_client.get("/api/trade/orders?limit=50")
        assert resp.status_code == 200

    def test_orders_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/trade/orders")
        assert resp.status_code == 401
