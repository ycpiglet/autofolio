# tests/unit/test_log_rotation.py
"""TDD tests for TASK-065: RotatingFileHandler + absolute log path."""
from __future__ import annotations

import logging
import logging.handlers
import importlib
from pathlib import Path


def _reset_logger(name: str) -> None:
    """Clear all handlers and markers from a named logger."""
    log = logging.getLogger(name)
    log.handlers.clear()
    if hasattr(log, "_jsonl_handler"):
        delattr(log, "_jsonl_handler")


class TestGetLoggerUsesRotatingFileHandler:
    def test_file_handler_is_rotating(self):
        """get_logger must attach a RotatingFileHandler, not a plain FileHandler."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.plain")
        logger = lg.get_logger("test.rotation.plain")
        file_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.FileHandler)
        ]
        assert file_handlers, "No FileHandler-family handler found"
        for h in file_handlers:
            assert isinstance(h, logging.handlers.RotatingFileHandler), (
                f"Expected RotatingFileHandler, got {type(h).__name__}"
            )

    def test_rotating_handler_max_bytes(self):
        """RotatingFileHandler must be configured for 10 MB max."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.maxbytes")
        logger = lg.get_logger("test.rotation.maxbytes")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        assert rotating[0].maxBytes == 10 * 1024 * 1024, (
            f"Expected 10485760 bytes, got {rotating[0].maxBytes}"
        )

    def test_rotating_handler_backup_count(self):
        """RotatingFileHandler must keep 5 backup files."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.backup")
        logger = lg.get_logger("test.rotation.backup")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        assert rotating[0].backupCount == 5, (
            f"Expected backupCount=5, got {rotating[0].backupCount}"
        )

    def test_log_path_is_absolute(self):
        """The log file path must be absolute (not CWD-relative)."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.abspath")
        logger = lg.get_logger("test.rotation.abspath")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        log_path = Path(rotating[0].baseFilename)
        assert log_path.is_absolute(), (
            f"Expected absolute path, got: {log_path}"
        )

    def test_log_path_ends_in_logs_dir(self):
        """Log path must end in <repo_root>/logs/trading_app.log."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.logdir")
        logger = lg.get_logger("test.rotation.logdir")
        rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert rotating, "No RotatingFileHandler attached"
        log_path = Path(rotating[0].baseFilename)
        assert log_path.parts[-1] == "trading_app.log", (
            f"Expected filename trading_app.log, got {log_path.parts[-1]}"
        )
        assert log_path.parts[-2] == "logs", (
            f"Expected parent dir 'logs', got {log_path.parts[-2]}"
        )


class TestGetStructuredLoggerUsesRotatingFileHandler:
    def test_jsonl_handler_is_rotating(self):
        """get_structured_logger must attach a RotatingFileHandler for events.jsonl."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured")
        logger = lg.get_structured_logger("test.rotation.structured")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating, (
            "No RotatingFileHandler for events.jsonl found. "
            f"Handlers: {[(type(h).__name__, getattr(h, 'baseFilename', '')) for h in logger.handlers]}"
        )

    def test_jsonl_rotating_max_bytes(self):
        """events.jsonl RotatingFileHandler must use 10 MB."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured.mb")
        logger = lg.get_structured_logger("test.rotation.structured.mb")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating
        assert jsonl_rotating[0].maxBytes == 10 * 1024 * 1024

    def test_jsonl_rotating_backup_count(self):
        """events.jsonl RotatingFileHandler must keep 5 backups."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured.bc")
        logger = lg.get_structured_logger("test.rotation.structured.bc")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating
        assert jsonl_rotating[0].backupCount == 5

    def test_jsonl_path_is_absolute(self):
        """events.jsonl path must be absolute."""
        import app.common.logger as lg
        importlib.reload(lg)
        _reset_logger("test.rotation.structured.abs")
        logger = lg.get_structured_logger("test.rotation.structured.abs")
        jsonl_rotating = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and "events.jsonl" in getattr(h, "baseFilename", "")
        ]
        assert jsonl_rotating
        assert Path(jsonl_rotating[0].baseFilename).is_absolute()
