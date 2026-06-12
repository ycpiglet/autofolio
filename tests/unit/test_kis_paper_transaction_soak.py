from __future__ import annotations

from app.common.enums import OrderType, Side

from scripts import kis_paper_transaction_soak as soak


def test_below_market_limit_price_uses_valid_tick():
    assert soak._below_market_limit_price(134_715) == 121_200
    assert soak._below_market_limit_price(2_274_000) == 2_046_000


def test_guard_rejects_non_paper_endpoint():
    class Settings:
        kis_env = "prod"
        kis_base_url = "https://openapi.koreainvestment.com:9443"
        kis_app_key = "x"
        kis_account_no = "y"

    try:
        soak._guard_paper(Settings())
    except RuntimeError as exc:
        assert "paper-only" in str(exc)
    else:
        raise AssertionError("non-paper settings must be rejected")


def test_recorded_order_shape_is_redacted():
    record = soak.RecordedOrder(
        symbol="069500",
        side=Side.BUY.value,
        order_type=OrderType.MARKET.value,
        expected="FILLED",
        status="FILLED",
        filled_quantity=1,
        order_log_id=7,
        execution_log_id=8,
        broker_order_id_tail="1234",
    )

    assert record.broker_order_id_tail == "1234"
    assert not hasattr(record, "account_no")
