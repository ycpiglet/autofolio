from datetime import datetime

from app.risk.trading_window import is_within_trading_window


def test_inside_trading_window():
    now = datetime(2026, 1, 1, 10, 0)
    assert is_within_trading_window(now, "09:10", "15:20")


def test_before_trading_window():
    now = datetime(2026, 1, 1, 9, 0)
    assert not is_within_trading_window(now, "09:10", "15:20")


def test_after_trading_window():
    now = datetime(2026, 1, 1, 15, 25)
    assert not is_within_trading_window(now, "09:10", "15:20")
