"""Logging redaction filter — defence-in-depth against secret leakage in logs.

Even though broker code is hardened to not place raw secrets into exception
messages (P0.1) and the token cache is encrypted (P0.3), a logging.Filter on the
root logger + handlers acts as a final safety net: any record whose rendered
message contains a credential-shaped ``key=value`` pair (case-insensitive) is
redacted before it reaches any handler/file.

Keywords redacted: authorization, appkey, appsecret, secretkey, app-key,
app-secret, token, secret, password (and underscore/space variants). The value
following a ``:`` or ``=`` separator is replaced with ``***REDACTED***``; the
keyword itself is preserved so log lines stay diagnosable. ``Bearer <token>``
sequences are also redacted.

Plain prose that merely mentions a keyword without an assignment (e.g. "KIS
token request failed") is left intact, so normal diagnostics are unaffected.

Ordering note: ``_BEARER_RE`` runs BEFORE ``_KV_RE`` so that
``Authorization: Bearer eyJ.REAL.sig`` is fully masked.  If ``_KV_RE`` ran
first it would redact only the first bare token (``Bearer``) and leave the
actual JWT visible.

Handler attachment: ``install_redaction_filter`` attaches the filter to both the
root *logger* (belt-and-suspenders) and to every root *handler* so records
propagated from plain ``logging.getLogger(__name__)`` child loggers — which only
traverse handler filters, not ancestor-logger filters — are also covered.
"""
from __future__ import annotations

import logging
import re

_REDACTED = "***REDACTED***"

# Bearer <token>  →  Bearer ***REDACTED***
# Must run BEFORE _KV_RE: "Authorization: Bearer eyJ.sig" would otherwise have
# "authorization:" matched by _KV_RE but the KV bare-value stops at the space
# inside "Bearer <jwt>", leaving the actual JWT visible.
_BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+")

# keyword [:=] value   →   keyword=***REDACTED***
# Value is a quoted string or a run of non-whitespace/delimiter chars.
# For space-containing unquoted values (e.g. "password = my secret phrase"),
# only the first token is redacted; wrap values in quotes to guarantee full
# coverage, or prefer using _BEARER_RE for token-shaped secrets.
_KV_RE = re.compile(
    r"""(?ix)
    (                                   # group 1: keyword + optional quote + separator
        ["']?
        \b(?:authorization
            |app[\s_-]?key
            |app[\s_-]?secret
            |secret[\s_-]?key
            |access[\s_-]?token
            |token
            |secret
            |password)\b
        ["']?
        \s*[:=]\s*
    )
    (?:
        "[^"]*"                         # double-quoted value
        |'[^']*'                        # single-quoted value
        |[^\s,;}\)\]]+                  # bare value up to a delimiter
    )
    """,
)


def redact(text: str) -> str:
    """Return *text* with any credential-shaped values replaced.

    ``_BEARER_RE`` runs first so ``Authorization: Bearer <jwt>`` is fully
    masked before ``_KV_RE`` processes the ``authorization:`` key.
    """
    if not text:
        return text
    # Step 1: scrub Bearer tokens (must precede KV so the JWT is not left behind)
    redacted = _BEARER_RE.sub("Bearer " + _REDACTED, text)
    # Step 2: scrub key=value / key:value credential pairs
    redacted = _KV_RE.sub(lambda m: m.group(1) + _REDACTED, redacted)
    return redacted


class RedactionFilter(logging.Filter):
    """A logging.Filter that scrubs credential-shaped values from records.

    Covers three surfaces:

    1. **Rendered message** (``record.msg`` + ``record.args``) — the common
       case; mutated in place only when redaction fires.
    2. **Exception traceback** (``record.exc_text`` / ``record.exc_info``) —
       formatted eagerly so the formatter cannot emit the raw traceback later.
    3. **Extra attributes** — non-standard ``record.__dict__`` keys written by
       ``logging.getLogger(...).info(msg, extra={...})`` calls.  String values
       are redacted in place so the JSONL formatter cannot emit them raw.
    """

    # Standard LogRecord attribute names — anything else is "extra".
    _STANDARD_ATTRS: frozenset[str] = frozenset({
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "message", "module",
        "msecs", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName", "taskName",
    })

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        # --- 1. Rendered message -------------------------------------------
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 — never break logging
            return True
        redacted_msg = redact(message)
        if redacted_msg != message:
            record.msg = redacted_msg
            record.args = ()

        # --- 2. Exception traceback ----------------------------------------
        # exc_text is set lazily by the formatter; force it now so we can
        # redact before any handler sees the raw traceback.
        if record.exc_info and record.exc_info[0] is not None:
            if not record.exc_text:
                record.exc_text = logging.Formatter().formatException(
                    record.exc_info
                )
            redacted_exc = redact(record.exc_text)
            if redacted_exc != record.exc_text:
                record.exc_text = redacted_exc
                record.exc_info = None  # prevent re-formatting from overwriting

        # --- 3. Extra attributes -------------------------------------------
        for key, val in list(record.__dict__.items()):
            if key in self._STANDARD_ATTRS or key.startswith("_"):
                continue
            if isinstance(val, str):
                scrubbed = redact(val)
                if scrubbed != val:
                    setattr(record, key, scrubbed)

        return True


def install_redaction_filter() -> RedactionFilter:
    """Attach a RedactionFilter to the root logger and all root handlers.

    Idempotent: re-invoking will not stack duplicate filters. Returns the shared
    filter instance so callers (e.g. ``get_logger``) can attach it to their own
    handlers, which is required because Python's logging applies *handler*
    filters (not ancestor-logger filters) when a child logger emits a record.

    Belt-and-suspenders: the filter is kept on the root *logger* (covers direct
    root-logger calls) **and** on every root *handler* (covers propagated child
    records).  New handlers added after startup (e.g. uvicorn) should call this
    function again, or add the returned filter to their new handler directly.
    """
    root = logging.getLogger()
    existing = next(
        (f for f in root.filters if isinstance(f, RedactionFilter)), None
    )
    flt = existing or RedactionFilter()
    if existing is None:
        root.addFilter(flt)
    for handler in root.handlers:
        if not any(isinstance(f, RedactionFilter) for f in handler.filters):
            handler.addFilter(flt)
    return flt
