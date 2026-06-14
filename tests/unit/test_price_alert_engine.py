"""TDD tests for price alert evaluation loop in LiveTradingEngine (TASK-061).

These tests were written BEFORE evaluate_price_alerts() existed.
Initial run must show FAIL (AttributeError or condition not met).
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from app.database.repositories import Repository
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine

_SENTINEL = object()  # Sentinel for "create a fresh MagicMock notifier"


def _make_engine(tmpdir: Path, price: float, notifier: object = _SENTINEL):
    """Return (engine, repo, notifier) with broker returning a fixed price.

    Pass notifier=None to create an engine with no notifier (tests None-safety).
    Default (omitted) creates a fresh MagicMock so callers can assert on .send().
    """
    db_path = tmpdir / "test.db"
    initialize_database(db_path)
    repo = Repository(db_path)

    mock_broker = MagicMock()
    price_result = MagicMock()
    price_result.price = price
    mock_broker.get_current_price.return_value = price_result

    actual_notifier = MagicMock() if notifier is _SENTINEL else notifier
    engine = LiveTradingEngine(broker=mock_broker, repo=repo, notifier=actual_notifier)
    return engine, repo, actual_notifier


def test_alert_above_fires_when_price_meets_condition():
    """ABOVE alert fires when current_price >= target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "ABOVE")

        engine.evaluate_price_alerts()

        notifier.send.assert_called_once()
        call_text = notifier.send.call_args[0][0]
        assert "005930" in call_text

        alerts = repo.list_active_alerts()
        assert not any(a["id"] == alert_id for a in alerts), "Alert should be inactive"


def test_alert_above_does_not_fire_when_price_below_target():
    """ABOVE alert does NOT fire when current_price < target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=45000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "ABOVE")

        engine.evaluate_price_alerts()

        notifier.send.assert_not_called()

        alerts = repo.list_active_alerts()
        assert any(a["id"] == alert_id for a in alerts), "Alert should still be active"


def test_alert_below_fires_when_price_meets_condition():
    """BELOW alert fires when current_price <= target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=45000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "BELOW")

        engine.evaluate_price_alerts()

        notifier.send.assert_called_once()
        call_text = notifier.send.call_args[0][0]
        assert "005930" in call_text

        alerts = repo.list_active_alerts()
        assert not any(a["id"] == alert_id for a in alerts)


def test_alert_below_does_not_fire_when_price_above_target():
    """BELOW alert does NOT fire when current_price > target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "BELOW")

        engine.evaluate_price_alerts()

        notifier.send.assert_not_called()

        alerts = repo.list_active_alerts()
        assert any(a["id"] == alert_id for a in alerts)


def test_already_fired_alert_not_resent():
    """An alert with active=0 must not be re-evaluated or re-sent."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "ABOVE")
        repo.trigger_alert(alert_id)  # pre-fire

        engine.evaluate_price_alerts()

        notifier.send.assert_not_called()


def test_run_once_includes_alert_evaluation():
    """run_once() must trigger alert evaluation; notifier is called for met alerts."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        repo.add_price_alert("005930", 50000.0, "ABOVE")

        engine.run_once()

        notifier.send.assert_called()


def test_evaluate_alerts_no_notifier_does_not_raise():
    """evaluate_price_alerts() is safe when self.notifier is None."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, _notifier = _make_engine(Path(tmpdir), price=55000.0, notifier=None)
        repo.add_price_alert("005930", 50000.0, "ABOVE")

        # Must not raise even without a notifier
        engine.evaluate_price_alerts()

        # Alert should still be marked inactive (logic runs, notify step skipped)
        alerts = repo.list_active_alerts()
        assert alerts == []
