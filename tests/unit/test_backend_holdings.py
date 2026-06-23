"""backend.holdings_df 의 순수 구성 헬퍼 테스트 (네트워크/DB 없음, pandas 만 사용)."""
from __future__ import annotations

from app.brokers.base import Position
from app.services import backend
from app.services.backend import HOLDINGS_COLUMNS, _build_holdings_df


def test_build_holdings_empty_returns_schema():
    df = _build_holdings_df([], lambda s: 0.0, lambda s: {})
    assert list(df.columns) == HOLDINGS_COLUMNS
    assert df.empty


def test_build_holdings_computes_pnl_class_and_weight():
    positions = [Position("005930", 10, 70000.0), Position("069500", 40, 36500.0)]
    prices = {"005930": 77000.0, "069500": 37800.0}
    meta = {
        "005930": {"name": "삼성전자", "role": "LARGE_CAP_TEST"},
        "069500": {"name": "KODEX 200", "role": "ETF_TEST"},
    }
    df = _build_holdings_df(positions, lambda s: prices[s], lambda s: meta.get(s, {}))

    assert list(df.columns) == HOLDINGS_COLUMNS
    r0 = df[df["티커"] == "005930"].iloc[0]
    assert r0["종목"] == "삼성전자"
    assert r0["자산군"] == "주식"
    assert r0["평가금액"] == 770000
    assert r0["평가손익"] == 70000          # (77000-70000)*10
    assert r0["손익률"] == 10.0
    assert df[df["티커"] == "069500"].iloc[0]["자산군"] == "ETF"
    # 비중 합은 ~100%
    assert abs(df["비중"].sum() - 100.0) < 0.5


def test_build_holdings_converts_overseas_position_to_krw():
    position = Position(
        symbol="AAPL",
        quantity=2,
        avg_price=190.0,
        market="NASD",
        currency="USD",
        fx_rate=1300.0,
    )

    df = _build_holdings_df(
        [position],
        lambda s: 200.0,
        lambda s: {"name": "Apple", "role": "US_STOCK", "market": "NASD"},
    )

    row = df.iloc[0]
    assert row["지역"] == "US"
    assert row["평단"] == 247000
    assert row["현재가"] == 260000
    assert row["평가금액"] == 520000
    assert row["평가손익"] == 26000


def test_build_holdings_handles_missing_avg_and_name_fallback():
    df = _build_holdings_df([Position("005930", 5, None)], lambda s: 100.0, lambda s: {})
    row = df.iloc[0]
    assert row["평단"] == 0
    assert row["손익률"] == 0.0
    assert row["예상연배당"] == 0
    assert row["배당수익률"] == 0.0
    assert row["종목"] == "삼성전자"  # 기본 별칭이 있으면 종목명으로 보강


def test_build_holdings_adds_dividend_income_and_yield():
    positions = [Position("005930", 10, 70000.0)]
    df = _build_holdings_df(
        positions,
        lambda s: 80000.0,
        lambda s: {"name": "삼성전자", "role": "LARGE_CAP_TEST"},
        lambda s: {"annual_cash_dividend": 400.0, "latest_dividend_rate": 0.5},
    )

    row = df.iloc[0]
    assert row["예상연배당"] == 4000
    assert row["배당수익률"] == 0.5


def test_holdings_df_can_skip_dividend_calls(monkeypatch):
    monkeypatch.setattr(backend, "_LAST_HOLDINGS_DF", None)

    class Repo:
        def list_whitelist_symbols(self):
            return [{"symbol": "005930", "name": "삼성전자", "role": "LARGE_CAP_TEST"}]

    class Broker:
        def get_positions(self):
            return [Position("005930", 1, 70000.0)]

        def get_prices_batch(self, symbols):
            return {"005930": 71000.0}

        def get_current_price(self, symbol):
            raise AssertionError("batch price should be used")

        def get_dividend_info(self, symbol):
            raise AssertionError("dividend lookup should be skipped")

    monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), Broker(), None, None))

    df = backend.holdings_df(include_dividends=False)

    row = df.iloc[0]
    assert row["종목"] == "삼성전자"
    assert row["평가금액"] == 71000
    assert row["예상연배당"] == 0


def test_holdings_df_returns_empty_schema_when_live_positions_fail_without_cache(monkeypatch):
    monkeypatch.setattr(backend, "_LAST_HOLDINGS_DF", None)

    class Repo:
        def list_whitelist_symbols(self):
            return [{"symbol": "005930", "name": "삼성전자", "role": "LARGE_CAP_TEST"}]

    class FailingBroker:
        def get_positions(self):
            raise RuntimeError("KIS positions unavailable")

    monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), FailingBroker(), None, None))

    df = backend.holdings_df(include_dividends=False)

    assert list(df.columns) == HOLDINGS_COLUMNS
    assert df.empty


def test_holdings_df_uses_cached_snapshot_when_live_positions_fail(monkeypatch):
    monkeypatch.setattr(backend, "_LAST_HOLDINGS_DF", None)

    class Repo:
        def list_whitelist_symbols(self):
            return [{"symbol": "005930", "name": "삼성전자", "role": "LARGE_CAP_TEST"}]

    class WorkingBroker:
        def get_positions(self):
            return [Position("005930", 2, 70000.0)]

        def get_prices_batch(self, symbols):
            return {"005930": 72000.0}

    class FailingBroker:
        def get_positions(self):
            raise RuntimeError("KIS positions unavailable")

    monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), WorkingBroker(), None, None))
    first = backend.holdings_df(include_dividends=False)
    assert first.iloc[0]["평가금액"] == 144000

    monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), FailingBroker(), None, None))
    cached = backend.holdings_df(include_dividends=False)

    assert cached.iloc[0]["종목"] == "삼성전자"
    assert cached.iloc[0]["평가금액"] == 144000
