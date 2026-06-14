"""TASK-066: Notification channel fallback integration tests.

Tests that when one channel send() raises, the NotificationBus:
1. Catches the exception (does not crash)
2. Continues to the next adapter
3. Logs a warning (does not silently swallow)

Also tests: when ALL channels fail, the bus completes without raising,
and that a warning is logged for each failed channel.

Uses the real NotificationBus from app.notification.base — no product code changes.
"""
from __future__ import annotations

import logging
from typing import Sequence
from unittest.mock import MagicMock, call, patch

import pytest

from app.notification.base import BaseNotifier, NotificationBus


# ---------------------------------------------------------------------------
# Fake adapters for testing
# ---------------------------------------------------------------------------

class FakeNotifier(BaseNotifier):
    """A test adapter that records calls and can be configured to raise."""

    def __init__(self, name: str, *, should_raise: bool = False, enabled: bool = True):
        self._name = name
        self._should_raise = should_raise
        self._enabled = enabled
        self.send_calls: list[str] = []

    @property
    def channel_name(self) -> str:
        return self._name

    @property
    def enabled(self) -> bool:
        return self._enabled

    def send(self, text: str) -> None:
        self.send_calls.append(text)
        if self._should_raise:
            raise RuntimeError(f"[{self._name}] send failed (simulated)")


# ---------------------------------------------------------------------------
# Tests: fallback behavior
# ---------------------------------------------------------------------------

class TestNotificationBusFallback:
    def test_first_channel_failure_second_channel_still_called(self):
        """When the first adapter raises, the second adapter must still receive send()."""
        first = FakeNotifier("telegram", should_raise=True)
        second = FakeNotifier("discord", should_raise=False)
        bus = NotificationBus([first, second])

        bus.send("test message")

        # First channel attempted
        assert first.send_calls == ["test message"]
        # Second channel received the message despite first failure
        assert second.send_calls == ["test message"]

    def test_all_channels_fail_bus_does_not_raise(self):
        """When every adapter raises, NotificationBus.send() completes without raising."""
        adapters = [
            FakeNotifier("telegram", should_raise=True),
            FakeNotifier("discord", should_raise=True),
            FakeNotifier("email", should_raise=True),
        ]
        bus = NotificationBus(adapters)

        # Must NOT raise — the bus swallows per-channel errors
        bus.send("all fail message")

        # All adapters were attempted
        for adapter in adapters:
            assert adapter.send_calls == ["all fail message"], (
                f"Adapter {adapter.channel_name!r} was not called"
            )

    def test_all_channels_fail_warnings_are_logged(self, caplog):
        """When all channels fail, a warning must be logged for each failure (not silent)."""
        adapters = [
            FakeNotifier("telegram", should_raise=True),
            FakeNotifier("discord", should_raise=True),
        ]
        bus = NotificationBus(adapters)

        with caplog.at_level(logging.WARNING, logger="autofolio.notification.bus"):
            bus.send("fail all")

        # Two warnings — one per adapter
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) >= 2, (
            f"Expected at least 2 warnings for 2 failing channels, got {len(warnings)}: "
            f"{[r.message for r in warnings]}"
        )

    def test_disabled_channel_is_skipped(self):
        """Adapters with enabled=False must be skipped entirely (not called at all)."""
        disabled = FakeNotifier("disabled_channel", should_raise=False, enabled=False)
        active = FakeNotifier("active_channel", should_raise=False, enabled=True)
        bus = NotificationBus([disabled, active])

        bus.send("skip disabled")

        assert disabled.send_calls == [], "Disabled adapter must not be called"
        assert active.send_calls == ["skip disabled"]

    def test_partial_success_first_fails_last_succeeds(self):
        """Middle-channel failure does not prevent subsequent adapters from receiving messages."""
        first = FakeNotifier("a", should_raise=True)
        second = FakeNotifier("b", should_raise=True)
        third = FakeNotifier("c", should_raise=False)
        bus = NotificationBus([first, second, third])

        bus.send("partial success")

        assert third.send_calls == ["partial success"], (
            "Last (working) channel must receive message even after earlier failures"
        )

    def test_send_fill_fallback_on_first_channel_failure(self):
        """send_fill() also falls back when first channel raises."""
        first = FakeNotifier("telegram_fill", should_raise=True)
        second = FakeNotifier("discord_fill", should_raise=False)

        # Override send_fill to delegate to send() for consistency
        # The real BaseNotifier.send_fill calls self.send() so our fake will record it
        bus = NotificationBus([first, second])
        bus.send_fill("005930", "BUY", 1, 70_000.0)

        # Fallback channel received the fill notification
        assert len(second.send_calls) == 1
        assert "005930" in second.send_calls[0]
        assert "BUY" in second.send_calls[0]

    def test_bus_enabled_is_true_when_any_adapter_enabled(self):
        """bus.enabled is True when at least one registered adapter is enabled."""
        adapters = [
            FakeNotifier("off1", enabled=False),
            FakeNotifier("on1", enabled=True),
        ]
        bus = NotificationBus(adapters)
        assert bus.enabled is True

    def test_bus_enabled_is_false_when_no_adapters_enabled(self):
        """bus.enabled is False when all registered adapters are disabled."""
        adapters = [
            FakeNotifier("off1", enabled=False),
            FakeNotifier("off2", enabled=False),
        ]
        bus = NotificationBus(adapters)
        assert bus.enabled is False

    def test_bus_enabled_is_false_when_no_adapters(self):
        """bus.enabled is False when no adapters are registered."""
        bus = NotificationBus([])
        assert bus.enabled is False

    def test_channel_failure_logged_with_channel_name(self, caplog):
        """Log warning must include the channel name for diagnostic traceability."""
        failing = FakeNotifier("my_channel", should_raise=True)
        bus = NotificationBus([failing])

        with caplog.at_level(logging.WARNING, logger="autofolio.notification.bus"):
            bus.send("diagnostic test")

        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("my_channel" in msg for msg in warning_messages), (
            f"Expected channel name 'my_channel' in warning. Got: {warning_messages}"
        )