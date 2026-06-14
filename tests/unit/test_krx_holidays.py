"""KRX 휴장일 캘린더 단위 테스트."""
from __future__ import annotations

from datetime import date

import pytest

from app.data.krx_holidays import KRX_HOLIDAYS, is_krx_holiday


# ---- data sanity ----

def test_krx_holidays_is_a_set_of_iso_strings():
    """KRX_HOLIDAYS is a set of YYYY-MM-DD strings."""
    assert isinstance(KRX_HOLIDAYS, (set, frozenset))
    for item in KRX_HOLIDAYS:
        assert isinstance(item, str)
        date.fromisoformat(item)


def test_krx_holidays_contains_2026_new_year():
    """2026-01-01 (신정) is in the holiday list."""
    assert "2026-01-01" in KRX_HOLIDAYS


def test_krx_holidays_contains_2025_new_year():
    """2025-01-01 (신정) is in the holiday list."""
    assert "2025-01-01" in KRX_HOLIDAYS


def test_krx_holidays_contains_seollal_2026():
    """2026 설날 (2026-01-28/29/30) included."""
    assert "2026-01-28" in KRX_HOLIDAYS
    assert "2026-01-29" in KRX_HOLIDAYS
    assert "2026-01-30" in KRX_HOLIDAYS


def test_krx_holidays_contains_christmas_2026():
    """2026-12-25 (성탄절) in holiday list."""
    assert "2026-12-25" in KRX_HOLIDAYS


# ---- is_krx_holiday helper ----

def test_is_krx_holiday_new_year_2026():
    """2026-01-01 is a KRX holiday."""
    assert is_krx_holiday(date(2026, 1, 1)) is True


def test_is_krx_holiday_known_trading_day():
    """2026-06-10 (Wednesday, not a holiday) is NOT a KRX holiday."""
    assert is_krx_holiday(date(2026, 6, 10)) is False


def test_is_krx_holiday_accepts_string():
    """is_krx_holiday also works with a date-string argument."""
    assert is_krx_holiday("2026-01-01") is True
    assert is_krx_holiday("2026-06-10") is False
