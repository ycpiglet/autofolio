from __future__ import annotations

from datetime import date, datetime, timedelta
from math import nan

import pytest

from app.brokers.base import PriceQuote
from app.data.quality import (
    CorporateAction,
    apply_split_adjustment,
    validate_corporate_actions,
    validate_ohlcv_bars,
    validate_price_quote,
)


@pytest.mark.parametrize("price", [0.0, -1.0, nan])
def test_quote_validator_rejects_invalid_price(price):
    result = validate_price_quote(PriceQuote(symbol="005930", price=price))

    assert not result.ok
    assert result.issues[0].code == "invalid_price"


def test_quote_validator_rejects_stale_quote():
    result = validate_price_quote(
        PriceQuote(
            symbol="005930",
            price=70_000.0,
            as_of=datetime(2026, 6, 12, 9, 0),
            source="fixture",
        ),
        now=datetime(2026, 6, 12, 10, 0),
    )

    assert not result.ok
    assert result.issues[0].code == "stale_price"


def test_price_quote_validator_accepts_current_positive_quote():
    result = validate_price_quote(
        PriceQuote(
            symbol="005930",
            price=70_000.0,
            as_of=datetime(2026, 6, 12, 9, 5),
        ),
        now=datetime(2026, 6, 12, 9, 10),
    )

    assert result.ok


def test_holiday_session_is_not_reported_as_missing_bar():
    rows = [
        {"date": "2026-06-12", "open": 100.0, "high": 110.0, "low": 99.0, "close": 105.0, "volume": 1000},
        {"date": "2026-06-16", "open": 106.0, "high": 112.0, "low": 101.0, "close": 108.0, "volume": 1200},
    ]

    result = validate_ohlcv_bars(
        symbol="005930",
        rows=rows,
        start=date(2026, 6, 12),
        end=date(2026, 6, 16),
        holidays=[date(2026, 6, 15)],
    )

    assert result.ok


def test_missing_business_bar_is_reported():
    rows = [
        {"date": "2026-06-12", "open": 100.0, "high": 110.0, "low": 99.0, "close": 105.0, "volume": 1000},
    ]

    result = validate_ohlcv_bars(
        symbol="005930",
        rows=rows,
        start=date(2026, 6, 12),
        end=date(2026, 6, 16),
    )

    assert not result.ok
    assert "missing bar" in result.reason


def test_invalid_ohlcv_bar_is_reported():
    rows = [
        {"date": "2026-06-12", "open": 100.0, "high": 90.0, "low": 99.0, "close": 0.0, "volume": 1000},
    ]

    result = validate_ohlcv_bars(
        symbol="005930",
        rows=rows,
        start=date(2026, 6, 12),
        end=date(2026, 6, 12),
    )

    assert not result.ok
    assert {issue.code for issue in result.issues} >= {"invalid_price", "invalid_bar_range"}


def test_split_adjustment_fixture_standardizes_pre_ex_date_rows():
    rows = [
        {"date": "2026-06-12", "open": 100.0, "high": 120.0, "low": 90.0, "close": 110.0, "volume": 1000},
        {"date": "2026-06-15", "open": 55.0, "high": 60.0, "low": 50.0, "close": 58.0, "volume": 2500},
    ]
    action = CorporateAction("005930", "split", date(2026, 6, 15), ratio=2.0)

    adjusted = apply_split_adjustment(rows, action)

    assert adjusted[0]["open"] == 50.0
    assert adjusted[0]["close"] == 55.0
    assert adjusted[0]["volume"] == 2000
    assert adjusted[0]["adjusted_for"] == "split:2@2026-06-15"
    assert adjusted[1]["close"] == 58.0


def test_corporate_action_fixture_validation_covers_split_and_dividend():
    result = validate_corporate_actions(
        [
            CorporateAction("005930", "split", date(2026, 6, 15), ratio=2.0),
            CorporateAction("005930", "cash_dividend", date(2026, 6, 16), cash_amount=500.0),
        ]
    )
    invalid = validate_corporate_actions(
        [CorporateAction("005930", "cash_dividend", date(2026, 6, 16), cash_amount=0.0)]
    )

    assert result.ok
    assert not invalid.ok
    assert invalid.issues[0].code == "invalid_dividend"
