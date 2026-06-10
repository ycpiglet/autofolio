"""VaR/MDD 몬테카를로 시뮬레이션 단위 테스트."""
from app.quant.risk_sim import compute_var, SimulationResult


def test_compute_var_basic():
    # 일별 수익률 ±1% 무작위
    returns = [0.01, -0.01] * 50
    result = compute_var(1_000_000.0, returns, horizon_days=10, n_simulations=1000)
    assert isinstance(result, SimulationResult)
    assert result.var_95 >= 0
    assert result.var_99 >= result.var_95
    assert result.cvar_95 >= result.var_95
    assert 0.0 <= result.max_drawdown_pct <= 100.0


def test_compute_var_empty_returns():
    result = compute_var(1_000_000.0, [])
    assert result.var_95 == 0.0
    assert result.n_simulations == 0


def test_compute_var_zero_portfolio():
    result = compute_var(0.0, [0.01, -0.01] * 10)
    assert result.var_95 == 0.0


def test_compute_var_percentiles_ordered():
    returns = [0.02, -0.02, 0.01, -0.015, 0.005] * 20
    result = compute_var(500_000.0, returns, n_simulations=500)
    p = result.percentiles
    assert p[1] >= p[5] >= p[10] >= p[25]  # 하위 %일수록 손실 큼


def test_compute_var_high_volatility_bigger_var():
    # 고변동성일수록 MDD가 더 커야 한다 (VaR가 0일 수 있어 MDD로 비교)
    low_vol = [0.001, -0.001] * 50
    high_vol = [0.05, -0.05] * 50
    r_low = compute_var(1_000_000.0, low_vol, n_simulations=1000, horizon_days=20)
    r_high = compute_var(1_000_000.0, high_vol, n_simulations=1000, horizon_days=20)
    assert r_high.max_drawdown_pct > r_low.max_drawdown_pct
