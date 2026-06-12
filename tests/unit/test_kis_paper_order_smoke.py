from scripts.kis_paper_order_smoke import _below_market_limit_price


def test_below_market_limit_price_uses_valid_tick_above_lower_band():
    assert _below_market_limit_price(333_000) == 299_500


def test_below_market_limit_price_stays_below_current_price():
    target = _below_market_limit_price(134_365)

    assert target < 134_365
    assert target % 100 == 0
