import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Project-root absolute log directory
# ---------------------------------------------------------------------------
# logger.py lives at app/common/logger.py  →  .parents[0] = app/common
#                                             .parents[1] = app
#                                             .parents[2] = <repo root>
BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 5


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # SECURITY: scrub credential-shaped values from every record this logger
    # emits (defence-in-depth — see app/observability/redaction.py). Handler
    # filters are required because Python applies handler (not ancestor-logger)
    # filters when a child logger emits a record.
    from app.observability.redaction import install_redaction_filter

    redaction_filter = install_redaction_filter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(redaction_filter)
    logger.addHandler(stream_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "trading_app.log",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(redaction_filter)
    logger.addHandler(file_handler)

    return logger


class _JsonLinesFormatter(logging.Formatter):
    """Formats each log record as a single JSON object on one line."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        # Resolve the rendered message first so exc_info / stack_info are included.
        message = record.getMessage()

        # Collect extra fields: anything that is not a standard LogRecord attribute.
        _STANDARD_ATTRS = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "message", "module",
            "msecs", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName",
        }
        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _STANDARD_ATTRS and not k.startswith("_")
        }

        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": message,
        }
        if extra:
            payload["extra"] = extra
        else:
            payload["extra"] = {}

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_structured_logger(name: str) -> logging.Logger:
    """Return a logger that additionally writes JSON Lines to logs/events.jsonl.

    The logger also inherits standard StreamHandler + RotatingFileHandler
    behaviour from get_logger so that human-readable output is preserved.
    """
    # Re-use (or create) the plain-text logger first so we get its handlers.
    logger = get_logger(name)

    # Check whether we already attached a JSON Lines handler to avoid duplicates.
    _JSONL_MARKER = "_jsonl_handler"
    if getattr(logger, _JSONL_MARKER, False):
        return logger

    jsonl_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "events.jsonl",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    jsonl_handler.setFormatter(_JsonLinesFormatter())
    jsonl_handler.setLevel(logging.INFO)
    from app.observability.redaction import install_redaction_filter

    jsonl_handler.addFilter(install_redaction_filter())
    logger.addHandler(jsonl_handler)

    # Mark so we don't double-add on repeated calls.
    setattr(logger, _JSONL_MARKER, True)
    return logger


def log_event(logger: logging.Logger, event_type: str, **kwargs: Any) -> None:
    """Emit a structured event as a JSON string through *logger* at INFO level.

    The message written to every handler is:
        {"event": event_type, <kwargs>}

    When the logger has a _JsonLinesFormatter handler attached (i.e. it was
    created with get_structured_logger), the JSON Lines file receives a fully
    structured record with ts / level / logger fields wrapping this payload.
    """
    payload = {"event": event_type, **kwargs}
    logger.info(json.dumps(payload, ensure_ascii=False, default=str))
