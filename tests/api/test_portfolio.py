"""Portfolio router contract tests.

Read endpoints require an approved app user. Tests use member sessions for
normal reads and verify guest sessions are rejected.
Backend functions are monkeypatched — no network/DB.
"""
from __future__ import annotations

from app.api.security import encode_session

CSRF = "portfolio-csrf"


def owner_headers() -> dict[str, str]:
    return {"X-CSRF-Token": CSRF}


def set_owner_session(client) -> None:
    client.cookies.set(
        "af_session",
        encode_session({"role": "owner", "username": "testuser", "data_source": "backend", "csrf_token": CSRF}),
    )


class TestHoldings:
    def test_holdings_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/holdings")
        assert resp.status_code == 200

    def test_holdings_guest_403(self, guest_client, mock_backend):
        resp = guest_client.get("/api/portfolio/holdings")
        assert resp.status_code == 403

    def test_holdings_shape(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/holdings")
        body = resp.json()
        assert "columns" in body and "rows" in body
        assert "종목" in body["columns"]
        assert "티커" in body["columns"]
        assert len(body["rows"]) == 1

    def test_holdings_korean_column_keys_preserved(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/holdings")
        columns = resp.json()["columns"]
        expected_kr = {"종목", "티커", "자산군", "지역", "섹터", "전략", "위험버킷", "수량", "평단", "현재가",
                       "평가금액", "평가손익", "손익률", "예상연배당", "배당수익률", "비중"}
        assert expected_kr.issubset(set(columns))

    def test_holdings_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/holdings")
        assert resp.status_code == 401


class TestKpis:
    def test_kpis_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/kpis")
        assert resp.status_code == 200

    def test_kpis_returns_expected_keys(self, member_client, mock_backend):
        body = resp = member_client.get("/api/portfolio/kpis")
        body = resp.json()
        assert set(body.keys()) == {"총자산", "일손익률", "누적손익률", "현금비중", "평가손익"}

    def test_kpis_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/kpis")
        assert resp.status_code == 401


class TestAssetCurve:
    def test_asset_curve_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/asset-curve")
        assert resp.status_code == 200

    def test_asset_curve_shape(self, member_client, mock_backend):
        body = member_client.get("/api/portfolio/asset-curve").json()
        assert "columns" in body and "rows" in body
        assert "자산" in body["columns"]
        assert "date" in body["columns"]  # named index must be preserved

    def test_asset_curve_date_in_rows(self, member_client, mock_backend):
        body = member_client.get("/api/portfolio/asset-curve").json()
        assert len(body["rows"]) == 3
        assert "date" in body["rows"][0]

    def test_asset_curve_days_param(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/asset-curve?days=30")
        assert resp.status_code == 200

    def test_asset_curve_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/asset-curve")
        assert resp.status_code == 401


class TestAllocationGap:
    def test_allocation_gap_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/allocation-gap")
        assert resp.status_code == 200

    def test_allocation_gap_shape(self, member_client, mock_backend):
        body = member_client.get("/api/portfolio/allocation-gap").json()
        assert "자산군" in body["columns"]

    def test_allocation_gap_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/allocation-gap")
        assert resp.status_code == 401


class TestOverview:
    def test_overview_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/portfolio/overview")
        assert resp.status_code == 200

    def test_overview_shape(self, member_client, mock_backend):
        body = member_client.get("/api/portfolio/overview").json()

        assert "kpis" in body
        assert "holdings" in body
        assert "groups" in body
        assert "diagnostics" in body
        assert "top_movers" in body
        assert "concentration" in body
        assert "allocation_gap" in body
        assert "data_quality" in body

        assert body["kpis"]["total_assets"] == 750_000.0
        assert body["kpis"]["total_market_value"] == 750_000.0
        assert body["kpis"]["unrealized_pnl"] == 50_000.0
        assert body["kpis"]["holdings_count"] == 1
        assert body["groups"]["automatic"][0]["id"] == "asset-class"
        assert body["top_movers"]["contributors"][0]["종목"] == "삼성전자"

    def test_overview_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/portfolio/overview")
        assert resp.status_code == 401


class TestGroups:
    def test_create_group_owner_200(self, client, mock_backend, monkeypatch):
        def fake_create_portfolio_group(**payload):
            return {"group_id": "pg_test", **payload}

        monkeypatch.setattr(mock_backend, "create_portfolio_group", fake_create_portfolio_group)
        set_owner_session(client)

        resp = client.post(
            "/api/portfolio/groups",
            json={"name": "코어", "symbols": ["005930", "069500"]},
            headers=owner_headers(),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["group_id"] == "pg_test"
        assert body["name"] == "코어"

    def test_create_group_missing_csrf_403(self, client, mock_backend):
        set_owner_session(client)
        resp = client.post("/api/portfolio/groups", json={"name": "코어", "symbols": ["005930"]})
        assert resp.status_code == 403
