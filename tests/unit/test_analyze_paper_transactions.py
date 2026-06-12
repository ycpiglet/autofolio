from __future__ import annotations

import pytest

from scripts import analyze_paper_transactions as report


def test_count_groups_missing_values():
    rows = [{"status": "FILLED"}, {"status": "FILLED"}, {"status": ""}, {}]

    assert report._count(rows, "status") == {"FILLED": 2, "unknown": 2}


def test_summarize_kis_redacted_with_fake_client():
    class Client:
        def get_today_orders(self, **kwargs):
            return [
                {
                    "pdno": "005930",
                    "sll_buy_dvsn_cd": "02",
                    "tot_ccld_qty": "1",
                    "cncl_yn": "N",
                    "status": "FILLED",
                    "odno": "secret-order-number",
                },
                {
                    "pdno": "069500",
                    "sll_buy_dvsn_cd": "02",
                    "tot_ccld_qty": "0",
                    "cncl_yn": "Y",
                    "status": "CANCELED",
                    "odno": "another-secret-order-number",
                },
            ]

    summary = report.summarize_kis(Client())

    assert summary["available"] is True
    assert summary["today_order_rows"] == 2
    assert summary["filled_row_count"] == 1
    assert summary["canceled_rows"] == 1
    assert summary["rows_by_symbol"] == {"005930": 1, "069500": 1}
    assert summary["warnings"] == []
    assert "odno" not in summary


def test_summarize_kis_retries_then_succeeds():
    class Client:
        def __init__(self):
            self.calls = 0

        def get_today_orders(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("temporary timeout")
            return [{"pdno": "069500", "tot_ccld_qty": "1", "status": "FILLED"}]

    client = Client()
    summary = report.summarize_kis(client, retries=1, retry_sleep=0)

    assert client.calls == 2
    assert summary["available"] is True
    assert summary["today_order_rows"] == 1
    assert summary["warnings"] == ["attempt 1/2: TimeoutError: temporary timeout"]


def test_summarize_kis_reports_unavailable_after_retries():
    class Client:
        def get_today_orders(self, **kwargs):
            raise TimeoutError("temporary timeout")

    summary = report.summarize_kis(Client(), retries=1, retry_sleep=0)

    assert summary["available"] is False
    assert summary["today_order_rows"] == 0
    assert summary["warnings"] == [
        "attempt 1/2: TimeoutError: temporary timeout",
        "attempt 2/2: TimeoutError: temporary timeout",
    ]


def test_main_fails_when_kis_unavailable(monkeypatch, capsys):
    monkeypatch.setattr(report, "summarize_db", lambda repo, limit: {"order_rows": 0, "execution_rows": 0})
    monkeypatch.setattr(
        report,
        "summarize_ui",
        lambda: {"order_log_rows": 0, "recent_fills_rows": 0, "holdings_rows": 0, "kis_today_orders_rows": 0},
    )
    monkeypatch.setattr(
        report,
        "summarize_kis",
        lambda client, retries, retry_sleep: {
            "available": False,
            "today_order_rows": 0,
            "open_like_count": 0,
            "warnings": ["attempt 1/1: TimeoutError: temporary timeout"],
        },
    )

    with pytest.raises(SystemExit) as exc:
        raise SystemExit(report.main(["--kis-retries", "0"]))

    assert exc.value.code == 1
    assert '"kis_available": false' in capsys.readouterr().out
