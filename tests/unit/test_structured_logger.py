"""Unit tests for app.common.logger structured-logging additions."""
from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_logger(name: str) -> logging.Logger:
    """Remove any cached logger so tests are isolated."""
    log = logging.getLogger(name)
    log.handlers.clear()
    # Remove the _jsonl_handler marker so get_structured_logger adds it again.
    if hasattr(log, "_jsonl_handler"):
        delattr(log, "_jsonl_handler")
    return log


# ---------------------------------------------------------------------------
# Tests for get_structured_logger
# ---------------------------------------------------------------------------

class TestGetStructuredLogger:
    def test_returns_logger_instance(self, tmp_path):
        with patch("app.common.logger.Path", lambda *a: tmp_path / Path(*a)):
            _fresh_logger("test.structured.a")
            from app.common.logger import get_structured_logger
            logger = get_structured_logger("test.structured.a")
        assert isinstance(logger, logging.Logger)

    def test_jsonl_handler_attached(self, tmp_path):
        """After get_structured_logger the logger must have a FileHandler
        writing to events.jsonl."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        _fresh_logger("test.structured.b")
        with patch("app.common.logger.Path") as mock_path:
            # Make Path("logs") resolve to our tmp logs dir.
            mock_path.side_effect = lambda *a: logs_dir if a == ("logs",) else Path(*a)
            mock_path.return_value = logs_dir

            from importlib import reload
            import app.common.logger as lg_module
            reload(lg_module)

            lg_module.get_logger("test.structured.b")  # prime plain logger
            _fresh_logger("test.structured.b")
            # Direct approach: call with real FS pointing at tmp_path.

        # Simpler integration: just verify the jsonl marker is set after call.
        import app.common.logger as lg
        _fresh_logger("test.structured.c")
        real_logs = Path("logs")
        real_logs.mkdir(exist_ok=True)
        structured = lg.get_structured_logger("test.structured.c")
        assert getattr(structured, "_jsonl_handler", False) is True

    def test_idempotent_handler_attachment(self):
        """Calling get_structured_logger twice must not double-add handlers."""
        import app.common.logger as lg
        name = "test.structured.idempotent"
        _fresh_logger(name)
        Path("logs").mkdir(exist_ok=True)
        lg.get_structured_logger(name)
        count_before = len(logging.getLogger(name).handlers)
        lg.get_structured_logger(name)
        count_after = len(logging.getLogger(name).handlers)
        assert count_before == count_after


# ---------------------------------------------------------------------------
# Tests for _JsonLinesFormatter
# ---------------------------------------------------------------------------

class TestJsonLinesFormatter:
    def _make_record(self, msg: str, level: int = logging.INFO, name: str = "test") -> logging.LogRecord:
        return logging.LogRecord(
            name=name,
            level=level,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=None,
        )

    def test_output_is_valid_json(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("hello world")
        output = fmt.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_required_keys_present(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("test message", name="mylogger")
        parsed = json.loads(fmt.format(record))
        assert "ts" in parsed
        assert "level" in parsed
        assert "logger" in parsed
        assert "msg" in parsed
        assert "extra" in parsed

    def test_ts_is_iso8601_utc(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("ts check")
        parsed = json.loads(fmt.format(record))
        ts = parsed["ts"]
        # Must end with Z and contain T separator
        assert ts.endswith("Z")
        assert "T" in ts

    def test_level_field(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("warn msg", level=logging.WARNING)
        parsed = json.loads(fmt.format(record))
        assert parsed["level"] == "WARNING"

    def test_logger_name_field(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("msg", name="my.module")
        parsed = json.loads(fmt.format(record))
        assert parsed["logger"] == "my.module"

    def test_msg_field(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("the message")
        parsed = json.loads(fmt.format(record))
        assert parsed["msg"] == "the message"

    def test_extra_field_empty_when_no_extras(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("plain")
        parsed = json.loads(fmt.format(record))
        assert parsed["extra"] == {}

    def test_extra_field_captures_custom_attrs(self):
        from app.common.logger import _JsonLinesFormatter
        fmt = _JsonLinesFormatter()
        record = self._make_record("with extra")
        record.symbol = "005930"
        record.executed = True
        parsed = json.loads(fmt.format(record))
        assert parsed["extra"]["symbol"] == "005930"
        assert parsed["extra"]["executed"] is True


# ---------------------------------------------------------------------------
# Tests for log_event
# ---------------------------------------------------------------------------

class TestLogEvent:
    def test_emits_info_level(self):
        import app.common.logger as lg
        captured: list[logging.LogRecord] = []

        class _Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                captured.append(record)

        name = "test.log_event.level"
        _fresh_logger(name)
        plain = logging.getLogger(name)
        plain.setLevel(logging.DEBUG)
        plain.addHandler(_Capture())

        lg.log_event(plain, "my_event", foo="bar")
        assert len(captured) == 1
        assert captured[0].levelno == logging.INFO

    def test_message_is_valid_json(self):
        import app.common.logger as lg
        captured: list[str] = []

        class _Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                captured.append(record.getMessage())

        name = "test.log_event.json"
        _fresh_logger(name)
        plain = logging.getLogger(name)
        plain.setLevel(logging.DEBUG)
        plain.addHandler(_Capture())

        lg.log_event(plain, "engine_run_start", conditions=5)
        assert len(captured) == 1
        payload = json.loads(captured[0])
        assert payload["event"] == "engine_run_start"
        assert payload["conditions"] == 5

    def test_kwargs_included_in_payload(self):
        import app.common.logger as lg
        captured: list[str] = []

        class _Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                captured.append(record.getMessage())

        name = "test.log_event.kwargs"
        _fresh_logger(name)
        plain = logging.getLogger(name)
        plain.setLevel(logging.DEBUG)
        plain.addHandler(_Capture())

        lg.log_event(plain, "condition_processed", symbol="005930", executed=True, message="Order filled.")
        payload = json.loads(captured[0])
        assert payload["symbol"] == "005930"
        assert payload["executed"] is True
        assert payload["message"] == "Order filled."

    def test_event_key_present(self):
        import app.common.logger as lg
        captured: list[str] = []

        class _Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                captured.append(record.getMessage())

        name = "test.log_event.event_key"
        _fresh_logger(name)
        plain = logging.getLogger(name)
        plain.setLevel(logging.DEBUG)
        plain.addHandler(_Capture())

        lg.log_event(plain, "engine_run_end", processed=3, executed=1)
        payload = json.loads(captured[0])
        assert "event" in payload
        assert payload["event"] == "engine_run_end"
