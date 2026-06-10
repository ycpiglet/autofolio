"""포트폴리오 최적화 단위 테스트."""
from app.quant.optimizer import equal_weight, inverse_volatility, momentum_weight, suggest_rebalancing


def test_equal_weight_sum_to_one():
    r = equal_weight(["A", "B", "C", "D"])
    assert abs(sum(r.weights.values()) - 1.0) < 0.01


def test_equal_weight_empty():
    r = equal_weight([])
    assert r.weights == {}


def test_inverse_volatility_higher_vol_lower_weight():
    prices = {
        "HIGH_VOL": [100 * (1 + (i % 2) * 0.1) for i in range(30)],
        "LOW_VOL": [100 + i * 0.01 for i in range(30)],
    }
    r = inverse_volatility(prices)
    assert r.weights["LOW_VOL"] > r.weights["HIGH_VOL"]


def test_momentum_weight_excludes_negative():
    prices = {
        "UP": [100 + i for i in range(70)],
        "DOWN": [200 - i for i in range(70)],
    }
    r = momentum_weight(prices, lookback=60)
    assert "DOWN" not in r.weights or r.weights.get("DOWN", 0) == 0
    assert r.weights.get("UP", 0) > 0


def test_suggest_rebalancing_identifies_gaps():
    current = {"A": 0.4, "B": 0.6}
    target = {"A": 0.5, "B": 0.5}
    sug = suggest_rebalancing(current, target, total_value=1_000_000, threshold_pct=2.0)
    assert len(sug) == 2
    assert all(s["action"] in ("매수", "매도") for s in sug)
