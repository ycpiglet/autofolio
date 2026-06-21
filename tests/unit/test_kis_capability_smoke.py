from scripts.kis_capability_smoke import (
    _env_status,
    _redact_text,
    _summarize_account_summary,
    _summarize_today_orders,
)


def test_redact_text_masks_long_digit_and_token_like_values():
    text = _redact_text("account=5019231301 token=abcdefghijklmnopqrstuvwxyz1234567890")

    assert "5019231301" not in text
    assert "abcdefghijklmnopqrstuvwxyz1234567890" not in text
    assert "[digits]" in text
    assert "[redacted]" in text


def test_summarize_today_orders_counts_without_amounts_or_raw_rows():
    summary = _summarize_today_orders(
        [
            {"odno": "1", "cncl_yn": "N", "rmn_qty": "1", "ord_unpr": "999999"},
            {"odno": "2", "cncl_yn": "Y", "rmn_qty": "1", "ord_unpr": "888888"},
        ]
    )

    assert summary == {"count": 2, "open_like_count": 1, "canceled_count": 1}


def test_summarize_account_summary_reports_shape_not_values():
    summary = _summarize_account_summary(
        {
            "source": "kis",
            "dnca_tot_amt": 123456,
            "tot_evlu_amt": 234567,
            "nass_amt": 345678,
        }
    )

    assert summary == {"source": "kis", "numeric_field_count": 3}


def test_env_status_prioritizes_fail_then_watch_then_pass():
    assert _env_status([{"status": "pass"}, {"status": "pass"}]) == "pass"
    assert _env_status([{"status": "pass"}, {"status": "skip"}]) == "watch"
    assert _env_status([{"status": "pass"}, {"status": "fail"}]) == "fail"
    assert _env_status([{"status": "skip"}]) == "skip"
