"""Tests for app/risk/duplicate_guard.py."""
import pytest
from datetime import datetime, timedelta


def test_active_no_cooldown_is_executable():
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 10, 10, 0, 0)
    assert is_condition_executable("ACTIVE", None, now) is True


def test_inactive_status_not_executable():
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 10, 10, 0, 0)
    assert is_condition_executable("DISABLED", None, now) is False
    assert is_condition_executable("TRIGGERED", None, now) is False
    assert is_condition_executable("ERROR", None, now) is False


def test_active_with_future_cooldown_not_executable():
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 10, 10, 0, 0)
    future = (now + timedelta(hours=1)).isoformat()
    assert is_condition_executable("ACTIVE", future, now) is False


def test_active_with_past_cooldown_is_executable():
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 10, 10, 0, 0)
    past = (now - timedelta(hours=1)).isoformat()
    assert is_condition_executable("ACTIVE", past, now) is True


def test_active_with_invalid_cooldown_not_executable():
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 10, 10, 0, 0)
    assert is_condition_executable("ACTIVE", "not-a-date", now) is False
