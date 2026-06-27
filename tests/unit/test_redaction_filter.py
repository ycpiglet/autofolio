"""Tests for app/observability/redaction.py — logging secret redaction (P0.2).

Adversarial additions (2026-06-27):
- Real ``Authorization: Bearer <jwt>`` header form (no injected "header" word).
- Exception traceback (exc_info/exc_text) coverage.
- Structured ``extra=`` values via JSONL formatter.
- Child-logger record through a root handler.
"""
import io
import json
import logging
import traceback

from app.observability.redaction import (
    RedactionFilter,
    install_redaction_filter,
    redact,
)


def test_redact_appsecret_value():
    out = redact("KIS payload appsecret=ABC123XYZ next")
    assert "ABC123XYZ" not in out
    assert "***REDACTED***" in out
    # keyword preserved for diagnosability
    assert "appsecret=" in out


def test_redact_handles_multiple_keywords_and_separators():
    src = 'appkey: KKK111 token=TTT222 "appsecret":"SSS333" password = PPP444'
    out = redact(src)
    for secret in ("KKK111", "TTT222", "SSS333", "PPP444"):
        assert secret not in out
    assert out.count("***REDACTED***") == 4


def test_redact_bearer_token_with_injected_word():
    # Original form (keyword "header" injected) — must still redact.
    out = redact("Authorization header: Bearer eyJabc.def-123")
    assert "eyJabc.def-123" not in out
    assert "***REDACTED***" in out


# ---------------------------------------------------------------------------
# Critical — real Authorization: Bearer <jwt> (no injected "header" word)
# Before fix: _KV_RE ran first, matched "authorization: " + bare "Bearer"
# (stopped at the space), leaving the actual JWT visible.
# After fix:  _BEARER_RE runs first → "Bearer eyJ..." redacted → JWT gone.
# ---------------------------------------------------------------------------

JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.REAL-SIG"


def test_redact_authorization_bearer_real_header_form():
    """The actual HTTP-header form must not leak the JWT."""
    text = f"Authorization: Bearer {JWT}"
    out = redact(text)
    assert JWT not in out, f"JWT leaked in: {out!r}"
    assert "***REDACTED***" in out


def test_redact_authorization_bearer_quoted_dict():
    """Python-repr / JSON dict form: 'Authorization': 'Bearer <jwt>'."""
    text = f"'Authorization': 'Bearer {JWT}'"
    out = redact(text)
    assert JWT not in out, f"JWT leaked in: {out!r}"
    assert "***REDACTED***" in out


def test_redact_bare_bearer():
    """Bare ``Bearer <token>`` without a leading key."""
    out = redact(f"Bearer {JWT}")
    assert JWT not in out, f"JWT leaked in: {out!r}"
    assert "***REDACTED***" in out


def test_redact_leaves_plain_prose_untouched():
    # No assignment after the keyword → not a credential, must stay intact.
    prose = "KIS token request failed: HTTP 401 EGW00133 bad creds"
    assert redact(prose) == prose


def test_redaction_filter_mutates_record():
    flt = RedactionFilter()
    record = logging.LogRecord(
        name="x", level=logging.INFO, pathname=__file__, lineno=1,
        msg="appsecret=%s", args=("ABC123XYZ",), exc_info=None,
    )
    assert flt.filter(record) is True
    assert "ABC123XYZ" not in record.getMessage()
    assert "***REDACTED***" in record.getMessage()


def test_filter_redacts_when_attached_to_handler():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(RedactionFilter())

    logger = logging.getLogger("test.redaction.handler")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("issuing token with appsecret=TOPSECRET999")
    handler.flush()
    out = stream.getvalue()
    assert "TOPSECRET999" not in out
    assert "***REDACTED***" in out


def test_install_redaction_filter_is_idempotent():
    root = logging.getLogger()
    before = [f for f in root.filters if isinstance(f, RedactionFilter)]
    f1 = install_redaction_filter()
    f2 = install_redaction_filter()
    after = [f for f in root.filters if isinstance(f, RedactionFilter)]
    assert f1 is f2
    # No duplicate RedactionFilter stacked on the root logger.
    assert len(after) == 1
    # Clean up only if we added it (leave pre-existing state alone).
    if not before:
        root.removeFilter(f1)


# ---------------------------------------------------------------------------
# Important #3a — exception traceback (exc_info / exc_text) coverage
# ---------------------------------------------------------------------------

def test_filter_redacts_exception_traceback():
    """A secret embedded in an exception message must not survive in exc_text."""
    secret = "SUPERSECRET_IN_EXC"
    try:
        raise RuntimeError(f"appkey={secret} caused failure")
    except RuntimeError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test.exc", level=logging.ERROR, pathname=__file__, lineno=1,
        msg="error occurred", args=(), exc_info=exc_info,
    )
    flt = RedactionFilter()
    flt.filter(record)

    # exc_text must have been computed and redacted
    assert record.exc_text is not None
    assert secret not in record.exc_text, (
        f"Secret survived in exc_text: {record.exc_text!r}"
    )
    assert "***REDACTED***" in record.exc_text


# ---------------------------------------------------------------------------
# Important #3b — structured extra={} coverage via JSONL formatter
# ---------------------------------------------------------------------------

def test_jsonl_formatter_redacts_extra_string_values():
    """Secrets passed as extra={...} must not appear raw in JSONL output."""
    from app.common.logger import _JsonLinesFormatter

    secret = "eyJSECRET.extra.value"
    record = logging.LogRecord(
        name="test.extra", level=logging.INFO, pathname=__file__, lineno=1,
        msg="structured event", args=(), exc_info=None,
    )
    # Simulate extra= by injecting into record.__dict__
    record.__dict__["token"] = f"Bearer {secret}"

    formatter = _JsonLinesFormatter()
    line = formatter.format(record)
    payload = json.loads(line)

    assert secret not in line, f"Secret leaked in JSONL line: {line!r}"
    token_val = payload.get("extra", {}).get("token", "")
    assert secret not in token_val, f"Secret in extra.token: {token_val!r}"
    assert "***REDACTED***" in token_val


# ---------------------------------------------------------------------------
# Important #4 — child logger propagated through root handler is redacted
# ---------------------------------------------------------------------------

def test_child_logger_through_root_handler_is_redacted():
    """A plain logging.getLogger child that propagates to root must be redacted.

    Python only applies *handler* filters (not ancestor-logger filters) when a
    child record propagates.  install_redaction_filter attaches to root handlers,
    so the filter fires for propagated child records too.
    """
    secret = "CHILD_SECRET_VALUE"

    stream = io.StringIO()
    root_handler = logging.StreamHandler(stream)
    root_handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    root_saved_handlers = list(root.handlers)
    root_saved_level = root.level

    try:
        root.handlers = [root_handler]
        root.setLevel(logging.DEBUG)

        # install_redaction_filter attaches to root + root handlers
        flt = install_redaction_filter()

        child = logging.getLogger("test.child.redaction_propagation")
        child.handlers = []
        child.propagate = True
        child.setLevel(logging.DEBUG)

        child.info("appsecret=%s", secret)
        root_handler.flush()

        out = stream.getvalue()
        assert secret not in out, f"Secret leaked via child→root propagation: {out!r}"
        assert "***REDACTED***" in out

    finally:
        root.handlers = root_saved_handlers
        root.setLevel(root_saved_level)
        # Remove filter added by install_redaction_filter if it wasn't there before
        for f in list(root.filters):
            if isinstance(f, RedactionFilter):
                root.removeFilter(f)
