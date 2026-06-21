"""Analysis router contract tests — attribution / retro / daily-pnl / backtest / var / scenario / whatif."""
from __future__ import annotations

import dataclasses
from datetime import date

import pytest


# ── Existing endpoints ────────────────────────────────────────────────────────

class TestAttribution:
    def test_attribution_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/analysis/attribution")
        assert resp.status_code == 200

    def test_attribution_guest_403(self, guest_client, mock_backend):
        resp = guest_client.get("/api/analysis/attribution")
        assert resp.status_code == 403

    def test_attribution_shape(self, member_client, mock_backend):
        body = member_client.get("/api/analysis/attribution").json()
        assert "columns" in body and "rows" in body
        assert "구분" in body["columns"]
        assert "기여(만원)" in body["columns"]

    def test_attribution_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/analysis/attribution")
        assert resp.status_code == 401

    def test_attribution_backend_error_surfaces(self, error_member_client, monkeypatch):
        """Backend exception must propagate as non-200 (fail-loud)."""
        import app.services.backend as bmod

        def _raise():
            raise RuntimeError("analysis failure")

        monkeypatch.setattr(bmod, "attribution_df", _raise)
        resp = error_member_client.get("/api/analysis/attribution")
        assert resp.status_code != 200


class TestRetro:
    def test_retro_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/analysis/retro")
        assert resp.status_code == 200

    def test_retro_shape(self, member_client, mock_backend):
        body = member_client.get("/api/analysis/retro").json()
        assert "승률" in body
        assert "평균R" in body
        assert "MDD" in body
        assert "규율" in body

    def test_retro_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/analysis/retro")
        assert resp.status_code == 401

    def test_retro_backend_error_surfaces(self, error_member_client, monkeypatch):
        """Backend exception must propagate as non-200 (fail-loud)."""
        import app.services.backend as bmod

        def _raise():
            raise RuntimeError("metrics error")

        monkeypatch.setattr(bmod, "retro_metrics", _raise)
        resp = error_member_client.get("/api/analysis/retro")
        assert resp.status_code != 200


class TestDailyPnl:
    def test_daily_pnl_member_200(self, member_client, mock_backend):
        resp = member_client.get("/api/analysis/daily-pnl")
        assert resp.status_code == 200

    def test_daily_pnl_shape(self, member_client, mock_backend):
        body = member_client.get("/api/analysis/daily-pnl").json()
        assert "columns" in body and "rows" in body
        assert "date" in body["columns"]
        assert "pnl" in body["columns"]

    def test_daily_pnl_unauthenticated_401(self, client, mock_backend):
        client.cookies.clear()
        resp = client.get("/api/analysis/daily-pnl")
        assert resp.status_code == 401


# ── Phase 5: Backtest ─────────────────────────────────────────────────────────

from app.quant.backtest import BacktestResult  # noqa: E402

_FAKE_RESULT = BacktestResult(
    symbol="005930",
    strategy="SMA_CROSSOVER",
    start=date(2025, 1, 1),
    end=date(2025, 6, 30),
    total_return_pct=12.5,
    trade_count=4,
    win_rate_pct=75.0,
    max_drawdown_pct=5.2,
    trades=[
        {"date": date(2025, 2, 1), "action": "BUY", "price": 70000, "shares": 10},
        {"date": date(2025, 3, 1), "action": "SELL", "price": 75000, "shares": 10, "pnl": 50000.0},
    ],
    equity_curve=[
        {"date": date(2025, 1, 2), "equity": 1_000_000},
        {"date": date(2025, 6, 30), "equity": 1_125_000},
    ],
)


class TestBacktest:
    def test_backtest_member_200(self, member_client, monkeypatch):
        import app.quant.backtest as bt_mod

        monkeypatch.setattr(bt_mod, "run_sma_crossover", lambda *a, **kw: _FAKE_RESULT)
        resp = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-01-01", "end": "2025-06-30"},
        )
        assert resp.status_code == 200

    def test_backtest_shape(self, member_client, monkeypatch):
        import app.quant.backtest as bt_mod

        monkeypatch.setattr(bt_mod, "run_sma_crossover", lambda *a, **kw: _FAKE_RESULT)
        body = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-01-01", "end": "2025-06-30"},
        ).json()
        assert body["symbol"] == "005930"
        assert body["strategy"] == "SMA_CROSSOVER"
        assert "total_return_pct" in body
        assert "trade_count" in body
        assert "win_rate_pct" in body
        assert "max_drawdown_pct" in body
        assert isinstance(body["trades"], list)
        assert isinstance(body["equity_curve"], list)

    def test_backtest_unauthenticated_401(self, client):
        client.cookies.clear()
        resp = client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-01-01", "end": "2025-06-30"},
        )
        assert resp.status_code == 401

    def test_backtest_bad_symbol_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "BAD SYMBOL!", "start": "2025-01-01", "end": "2025-06-30"},
        )
        assert resp.status_code == 422

    def test_backtest_empty_symbol_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "", "start": "2025-01-01", "end": "2025-06-30"},
        )
        assert resp.status_code == 422

    def test_backtest_bad_start_date_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "not-a-date", "end": "2025-06-30"},
        )
        assert resp.status_code == 422

    def test_backtest_bad_end_date_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-01-01", "end": "2025-13-99"},
        )
        assert resp.status_code == 422

    def test_backtest_start_after_end_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-12-01", "end": "2025-01-01"},
        )
        assert resp.status_code == 422

    def test_backtest_fast_gte_slow_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/backtest",
            params={
                "symbol": "005930",
                "start": "2025-01-01",
                "end": "2025-06-30",
                "fast": "20",
                "slow": "5",
            },
        )
        assert resp.status_code == 422

    def test_backtest_backend_error_surfaces(self, error_member_client, monkeypatch):
        """Backend exception must propagate as non-200 (fail-loud)."""
        import app.quant.backtest as bt_mod

        def _raise(*a, **kw):
            raise RuntimeError("backtest failure")

        monkeypatch.setattr(bt_mod, "run_sma_crossover", _raise)
        resp = error_member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-01-01", "end": "2025-06-30"},
        )
        assert resp.status_code != 200

    def test_backtest_dates_serialized_as_strings(self, member_client, monkeypatch):
        """All date fields must be ISO strings, not Python date objects."""
        import app.quant.backtest as bt_mod

        monkeypatch.setattr(bt_mod, "run_sma_crossover", lambda *a, **kw: _FAKE_RESULT)
        body = member_client.get(
            "/api/analysis/backtest",
            params={"symbol": "005930", "start": "2025-01-01", "end": "2025-06-30"},
        ).json()
        assert isinstance(body["start"], str)
        assert isinstance(body["end"], str)
        # trades and equity_curve dates also stringified
        for t in body["trades"]:
            assert isinstance(t["date"], str)
        for p in body["equity_curve"]:
            assert isinstance(p["date"], str)


# ── Phase 5: VaR ─────────────────────────────────────────────────────────────

from app.quant.risk_sim import SimulationResult  # noqa: E402

import pandas as pd  # noqa: E402

_FAKE_SIM = SimulationResult(
    total_value=750_000.0,
    n_simulations=10_000,
    horizon_days=10,
    var_95=15_000.0,
    var_99=25_000.0,
    cvar_95=30_000.0,
    max_drawdown_pct=3.5,
    percentiles={1: 35_000.0, 5: 15_000.0, 10: 10_000.0, 25: 5_000.0, 50: -2_000.0},
    note="10,000회 시뮬레이션, 10일 horizon",
)

_SAMPLE_PNL = pd.DataFrame(
    [
        {"date": "2025-06-10", "pnl": 5_000.0},
        {"date": "2025-06-11", "pnl": -3_000.0},
        {"date": "2025-06-12", "pnl": 2_000.0},
    ]
)

_SAMPLE_SUMMARY = {
    "scts_evlu_amt": 750_000.0,
    "dnca_tot_amt": 0.0,
    "tot_evlu_amt": 750_000.0,
    "nass_amt": 750_000.0,
    "source": "estimated",
}


class TestVar:
    def _patch(self, monkeypatch, sim_result=None):
        import app.services.backend as bmod
        import app.quant.risk_sim as rs_mod

        monkeypatch.setattr(bmod, "daily_pnl_series", lambda: _SAMPLE_PNL)
        monkeypatch.setattr(bmod, "account_summary", lambda: _SAMPLE_SUMMARY)
        monkeypatch.setattr(
            rs_mod,
            "compute_var",
            lambda *a, **kw: sim_result or _FAKE_SIM,
        )

    def test_var_member_200(self, member_client, monkeypatch):
        self._patch(monkeypatch)
        resp = member_client.get("/api/analysis/var")
        assert resp.status_code == 200

    def test_var_shape(self, member_client, monkeypatch):
        self._patch(monkeypatch)
        body = member_client.get("/api/analysis/var").json()
        assert "var_95" in body
        assert "var_99" in body
        assert "cvar_95" in body
        assert "horizon_days" in body
        assert "n_simulations" in body
        assert "max_drawdown_pct" in body
        assert "percentiles" in body
        assert "note" in body

    def test_var_unauthenticated_401(self, client):
        client.cookies.clear()
        resp = client.get("/api/analysis/var")
        assert resp.status_code == 401

    def test_var_n_simulations_clamped(self, member_client, monkeypatch):
        """n_simulations above cap must be clamped to 50_000, not rejected."""
        captured = {}

        import app.services.backend as bmod
        import app.quant.risk_sim as rs_mod

        monkeypatch.setattr(bmod, "daily_pnl_series", lambda: _SAMPLE_PNL)
        monkeypatch.setattr(bmod, "account_summary", lambda: _SAMPLE_SUMMARY)

        def _capture(*args, **kwargs):
            captured["n_sim"] = kwargs.get("n_simulations", args[2] if len(args) > 2 else None)
            return _FAKE_SIM

        monkeypatch.setattr(rs_mod, "compute_var", _capture)
        resp = member_client.get("/api/analysis/var", params={"n_simulations": "999999"})
        assert resp.status_code == 200
        assert captured.get("n_sim", 999999) <= 50_000

    def test_var_empty_portfolio_returns_200_with_note(self, member_client, monkeypatch):
        """Empty pnl / zero portfolio value → 200 with explicit note, not fabricated."""
        import app.services.backend as bmod

        monkeypatch.setattr(bmod, "daily_pnl_series", lambda: pd.DataFrame(columns=["date", "pnl"]))
        monkeypatch.setattr(bmod, "account_summary", lambda: {"tot_evlu_amt": 0.0})
        resp = member_client.get("/api/analysis/var")
        assert resp.status_code == 200
        body = resp.json()
        assert "note" in body
        assert body["note"]  # non-empty note signals the empty-data path

    def test_var_backend_error_surfaces(self, error_member_client, monkeypatch):
        """Backend exception must propagate as non-200 (fail-loud)."""
        import app.services.backend as bmod

        def _raise():
            raise RuntimeError("pnl failure")

        monkeypatch.setattr(bmod, "daily_pnl_series", _raise)
        monkeypatch.setattr(bmod, "account_summary", lambda: _SAMPLE_SUMMARY)
        resp = error_member_client.get("/api/analysis/var")
        assert resp.status_code != 200

    def test_var_horizon_days_below_min_422(self, member_client):
        resp = member_client.get("/api/analysis/var", params={"horizon_days": "0"})
        assert resp.status_code == 422

    def test_var_n_simulations_below_min_422(self, member_client):
        resp = member_client.get("/api/analysis/var", params={"n_simulations": "5"})
        assert resp.status_code == 422


# ── Phase 5: Scenario ─────────────────────────────────────────────────────────

_SAMPLE_SCENARIO = pd.DataFrame(
    [
        {
            "시나리오": "Bull",
            "자산군": "주식",
            "현재금액(원)": 750_000,
            "변동률(%)": 15.0,
            "변동액(원)": 112_500,
            "시나리오후금액(원)": 862_500,
        },
        {
            "시나리오": "Bull",
            "자산군": "합계",
            "현재금액(원)": 750_000,
            "변동률(%)": 15.0,
            "변동액(원)": 112_500,
            "시나리오후금액(원)": 862_500,
        },
    ]
)


class TestScenario:
    def test_scenario_member_200(self, member_client, monkeypatch):
        import app.services.backend as bmod

        monkeypatch.setattr(bmod, "scenario_analysis", lambda scenarios=None: _SAMPLE_SCENARIO)
        resp = member_client.get("/api/analysis/scenario")
        assert resp.status_code == 200

    def test_scenario_shape(self, member_client, monkeypatch):
        import app.services.backend as bmod

        monkeypatch.setattr(bmod, "scenario_analysis", lambda scenarios=None: _SAMPLE_SCENARIO)
        body = member_client.get("/api/analysis/scenario").json()
        assert "columns" in body and "rows" in body
        assert "시나리오" in body["columns"]
        assert "자산군" in body["columns"]
        assert "변동률(%)" in body["columns"]

    def test_scenario_unauthenticated_401(self, client):
        client.cookies.clear()
        resp = client.get("/api/analysis/scenario")
        assert resp.status_code == 401

    def test_scenario_backend_error_surfaces(self, error_member_client, monkeypatch):
        import app.services.backend as bmod

        def _raise(scenarios=None):
            raise RuntimeError("scenario failure")

        monkeypatch.setattr(bmod, "scenario_analysis", _raise)
        resp = error_member_client.get("/api/analysis/scenario")
        assert resp.status_code != 200


# ── Phase 5: Whatif ───────────────────────────────────────────────────────────

_SAMPLE_WHATIF = {
    "symbol": "005930",
    "current_weight": 100.0,
    "new_weight": 50.0,
    "delta_shares": -5,
    "delta_cost": -375_000,
    "new_total_assets_estimated": 750_000.0,
    "risk_note": "",
}


class TestWhatif:
    def test_whatif_member_200(self, member_client, monkeypatch):
        import app.services.backend as bmod

        monkeypatch.setattr(bmod, "whatif_weight_change", lambda sym, w: _SAMPLE_WHATIF)
        resp = member_client.get(
            "/api/analysis/whatif",
            params={"symbol": "005930", "weight": "50.0"},
        )
        assert resp.status_code == 200

    def test_whatif_shape(self, member_client, monkeypatch):
        import app.services.backend as bmod

        monkeypatch.setattr(bmod, "whatif_weight_change", lambda sym, w: _SAMPLE_WHATIF)
        body = member_client.get(
            "/api/analysis/whatif",
            params={"symbol": "005930", "weight": "50.0"},
        ).json()
        assert "symbol" in body
        assert "current_weight" in body
        assert "new_weight" in body
        assert "delta_shares" in body
        assert "delta_cost" in body

    def test_whatif_unauthenticated_401(self, client):
        client.cookies.clear()
        resp = client.get(
            "/api/analysis/whatif",
            params={"symbol": "005930", "weight": "50.0"},
        )
        assert resp.status_code == 401

    def test_whatif_bad_symbol_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/whatif",
            params={"symbol": "bad symbol!", "weight": "50.0"},
        )
        assert resp.status_code == 422

    def test_whatif_empty_symbol_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/whatif",
            params={"symbol": "", "weight": "50.0"},
        )
        assert resp.status_code == 422

    def test_whatif_weight_over_100_422(self, member_client):
        resp = member_client.get(
            "/api/analysis/whatif",
            params={"symbol": "005930", "weight": "150.0"},
        )
        assert resp.status_code == 422

    def test_whatif_backend_error_surfaces(self, error_member_client, monkeypatch):
        import app.services.backend as bmod

        def _raise(sym, w):
            raise RuntimeError("whatif failure")

        monkeypatch.setattr(bmod, "whatif_weight_change", _raise)
        resp = error_member_client.get(
            "/api/analysis/whatif",
            params={"symbol": "005930", "weight": "50.0"},
        )
        assert resp.status_code != 200
