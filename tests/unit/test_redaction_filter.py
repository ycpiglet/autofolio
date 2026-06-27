"""Tests for app/observability/redaction.py — logging secret redaction (P0.2)."""
import io
import logging

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


def test_redact_bearer_token():
    out = redact("Authorization header: Bearer eyJabc.def-123")
    assert "eyJabc.def-123" not in out
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
