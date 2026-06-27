"""SafetyChecker Phase 2 multitenant 단위 테스트.

Flag-OFF: user_id param ignored → global behavior (byte-identical invariant).
Flag-ON + user_id: per-user PnL/limits used → isolation between users.
"""
from __future__ import annotations

from datetime import datetime

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.risk.safety_checker import SafetyChecker


def _cond(symbol="005930", qty=1):
    return {
        "id": 1, "symbol": symbol, "side": "BUY", "quantity": qty,
        "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
    }


def _make_env(tmp_path):
    db = tmp_path / "test.db"
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    checker = SafetyChecker(repo)
    return repo, checker


def _insert_loss_cycle(repo, user_id, symbol="005930", buy_price=75_000.0, sell_price=60_000.0, qty=1):
    """Insert a BUY+SELL cycle where sell_price < buy_price → realized loss."""
    buy_cid = repo.add_trade_condition(
        symbol=symbol, side="BUY", target_price=buy_price,
        quantity=qty, user_id=user_id,
    )
    buy_order_id = repo.create_order_log(
        condition_id=buy_cid, symbol=symbol, side="BUY",
        order_type="LIMIT", order_price=buy_price, current_price=buy_price,
        quantity=qty, kis_order_id=None, order_status="FILLED",
        user_id=user_id,
    )
    repo.create_execution_log(
        order_log_id=buy_order_id, symbol=symbol,
        filled_price=buy_price, filled_quantity=qty,
        user_id=user_id,
    )
    sell_cid = repo.add_trade_condition(
        symbol=symbol, side="SELL", target_price=sell_price,
        quantity=qty, user_id=user_id,
    )
    sell_order_id = repo.create_order_log(
        condition_id=sell_cid, symbol=symbol, side="SELL",
        order_type="LIMIT", order_price=sell_price, current_price=sell_price,
        quantity=qty, kis_order_id=None, order_status="FILLED",
        user_id=user_id,
    )
    repo.create_execution_log(
        order_log_id=sell_order_id, symbol=symbol,
        filled_price=sell_price, filled_quantity=qty,
        user_id=user_id,
    )


# ---------- Flag-OFF characterization ----------

def test_flag_off_is_default(monkeypatch):
    """AUTOFOLIO_MULTI_TENANT_ENABLED absent → multi_tenant_enabled() = False."""
    from app.services.flags import multi_tenant_enabled
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    assert multi_tenant_enabled() is False


def test_flag_off_user_id_param_is_ignored(tmp_path, monkeypatch):
    """Flag OFF: user_id passed to check() has no effect — uses global path."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    repo, checker = _make_env(tmp_path)
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)
    # With flag OFF, user_id is ignored → same global behavior as no user_id
    r_with_uid = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="any_user")
    r_without_uid = checker.check(condition=_cond(), current_price=70_000, now=datetime.now())
    assert r_with_uid.allowed == r_without_uid.allowed


# ---------- Flag-ON isolation ----------

def test_per_user_circuit_breaker_isolation(tmp_path, monkeypatch):
    """Flag ON: user_a's large loss trips circuit-breaker for user_a only.
    user_b has no loss → passes.  Both use the SAME shared DB.

    Default: max_daily_amount=300_000, threshold=3.0%  →  trip if |pnl| >= 9_000.
    user_a loss: (60_000 - 75_000) * 1 = -15_000 → loss_pct = 5.0% → TRIPS.
    user_b: no fills → pnl = 0 → does NOT trip.
    """
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    repo, checker = _make_env(tmp_path)
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

    # Seed user_a's loss BEFORE any checks (both users' data coexist in the DB)
    _insert_loss_cycle(repo, "user_a", buy_price=75_000.0, sell_price=60_000.0, qty=1)

    # user_b has no activity — check user_b first to confirm isolation
    r_b = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_b")
    assert r_b.allowed, (
        f"user_b should pass (no loss) but got: {r_b.reason}"
    )

    # user_a has a big loss → circuit breaker triggers
    r_a = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_a")
    assert not r_a.allowed
    assert "circuit breaker" in r_a.reason.lower() or "loss" in r_a.reason.lower(), (
        f"Expected circuit-breaker reason for user_a, got: {r_a.reason}"
    )


def test_flag_on_no_user_id_uses_global_path(tmp_path, monkeypatch):
    """Flag ON + user_id=None → _effective_uid=None → global path (unchanged)."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    repo, checker = _make_env(tmp_path)
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)
    # No user_id → same as calling with no user_id
    r = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id=None)
    assert r.allowed, r.reason


# ---------- Repository: get_user_risk_limit ----------

def test_get_user_risk_limit_falls_back_to_global(tmp_path):
    """No per-user limit row → get_user_risk_limit falls back to GLOBAL."""
    db = tmp_path / "test.db"
    initialize_database(db)
    repo = Repository(db)
    limit = repo.get_user_risk_limit("some_user")
    global_limit = repo.get_global_risk_limit()
    assert limit["max_daily_amount"] == global_limit["max_daily_amount"]
    assert limit["max_order_amount"] == global_limit["max_order_amount"]
