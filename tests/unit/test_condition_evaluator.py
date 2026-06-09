from app.engine.condition_evaluator import is_condition_triggered


def test_buy_triggered_when_current_price_below_target():
    assert is_condition_triggered(side="BUY", current_price=69900, target_price=70000)


def test_buy_not_triggered_when_current_price_above_target():
    assert not is_condition_triggered(side="BUY", current_price=70100, target_price=70000)


def test_sell_triggered_when_current_price_above_target():
    assert is_condition_triggered(side="SELL", current_price=76100, target_price=76000)


def test_sell_not_triggered_when_current_price_below_target():
    assert not is_condition_triggered(side="SELL", current_price=75900, target_price=76000)
