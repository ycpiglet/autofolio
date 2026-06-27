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
"""
from __future__ import annotations

import logging
import re

_REDACTED = "***REDACTED***"

# keyword [:=] value   →   keyword=***REDACTED***
# Value is a quoted string or a run of non-delimiter chars.
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

_BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+")


def redact(text: str) -> str:
    """Return *text* with any credential-shaped values replaced."""
    if not text:
        return text
    redacted = _KV_RE.sub(lambda m: m.group(1) + _REDACTED, text)
    redacted = _BEARER_RE.sub("Bearer " + _REDACTED, redacted)
    return redacted


class RedactionFilter(logging.Filter):
    """A logging.Filter that scrubs credential-shaped values from records.

    The filter mutates ``record.msg``/``record.args`` in place only when a
    redaction actually occurs, so non-secret records are untouched (lazy
    formatting is preserved for the common case).
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 — never break logging
            return True
        redacted = redact(message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


def install_redaction_filter() -> RedactionFilter:
    """Attach a RedactionFilter to the root logger and all root handlers.

    Idempotent: re-invoking will not stack duplicate filters. Returns the shared
    filter instance so callers (e.g. ``get_logger``) can attach it to their own
    handlers, which is required because Python's logging applies *handler*
    filters (not ancestor-logger filters) when a child logger emits a record.
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
