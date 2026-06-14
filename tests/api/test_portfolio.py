"""Portfolio router contract tests.

All endpoints require_session. Tests run with both guest and owner sessions.
Backend functions are monkeypatched — no network/DB.
"""
from __future__ import annotations


class TestHoldings:
    def test_holdings_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/holdings")
        assert resp.status_code == 200

    def test_holdings_shape(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/holdings")
        body = resp.json()
        assert "columns" in body and "rows" in body
        assert "종목" in body["columns"]
        assert "티커" in body["columns"]
        assert len(body["rows"]) == 1

    def test_holdings_korean_column_keys_preserved(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/holdings")
        columns = resp.json()["columns"]
        expected_kr = {"종목", "티커", "자산군", "지역", "수량", "평단", "현재가",
                       "평가금액", "평가손익", "손익률", "예상연배당", "배당수익률", "비중"}
        assert expected_kr == set(columns)

    def test_holdings_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/holdings")
        assert resp.status_code == 401


class TestKpis:
    def test_kpis_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/kpis")
        assert resp.status_code == 200

    def test_kpis_returns_expected_keys(self, guest_client, mock_backend):
        body = resp = guest_client.get("/api/portfolio/kpis")
        body = resp.json()
        assert set(body.keys()) == {"총자산", "일손익률", "누적손익률", "현금비중", "평가손익"}

    def test_kpis_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/kpis")
        assert resp.status_code == 401


class TestAssetCurve:
    def test_asset_curve_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/asset-curve")
        assert resp.status_code == 200

    def test_asset_curve_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/portfolio/asset-curve").json()
        assert "columns" in body and "rows" in body
        assert "자산" in body["columns"]

    def test_asset_curve_days_param(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/asset-curve?days=30")
        assert resp.status_code == 200

    def test_asset_curve_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/asset-curve")
        assert resp.status_code == 401


class TestAllocationGap:
    def test_allocation_gap_guest_200(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/allocation-gap")
        assert resp.status_code == 200

    def test_allocation_gap_shape(self, guest_client, mock_backend):
        body = guest_client.get("/api/portfolio/allocation-gap").json()
        assert "자산군" in body["columns"]

    def test_allocation_gap_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/allocation-gap")
        assert resp.status_code == 401
