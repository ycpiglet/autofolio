"""SafetyChecker 단위 테스트 — 각 안전 게이트를 독립적으로 검증."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.brokers.mock.mock_client import MockBrokerClient
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.risk.safety_checker import SafetyChecker


@pytest.fixture
def env():
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "test.db"
        initialize_database(db)
        repo = Repository(db)
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
        )
        repo.set_system_state("auto_trading_enabled", "true")
        repo.set_system_state("kill_switch_active", "false")
        checker = SafetyChecker(repo)
        yield repo, checker


def _cond(symbol="005930", qty=1):
    return {
        "id": 1, "symbol": symbol, "side": "BUY", "quantity": qty,
        "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
    }


# ---- 기본 통과 ----
def test_allowed_when_all_gates_pass(env, monkeypatch):
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert r.allowed, r.reason


# ---- 킬스위치 ----
def test_kill_switch_blocks(env, monkeypatch):
    repo, checker = env
    repo.set_system_state("kill_switch_active", "true")
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert not r.allowed
    assert "kill" in r.reason.lower()


# ---- 자동매매 OFF ----
def test_auto_trading_disabled_blocks(env, monkeypatch):
    repo, checker = env
    repo.set_system_state("auto_trading_enabled", "false")
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert not r.allowed
    assert "auto" in r.reason.lower() or "disabled" in r.reason.lower()


# ---- 화이트리스트 외 종목 ----
def test_non_whitelist_symbol_blocked(env, monkeypatch):
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    r = checker.check(condition=_cond(symbol="999999"), current_price=10000, now=datetime.now())
    assert not r.allowed
    assert "whitelist" in r.reason.lower()


# ---- 거래시간 외 ----
def test_outside_trading_window_blocked(env, monkeypatch):
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: False)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert not r.allowed
    assert "window" in r.reason.lower() or "trading" in r.reason.lower()


# ---- 주문금액 한도 초과 ----
def test_order_amount_exceeded_blocks(env, monkeypatch):
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    # 현재가 200,000 × 2주 = 400,000 > default 100,000 한도
    r = checker.check(condition=_cond(qty=2), current_price=200_000, now=datetime.now())
    assert not r.allowed
    assert "amount" in r.reason.lower() or "한도" in r.reason


# ---- 1주 예외 허용 ----
def test_one_share_exception_allowed(env, monkeypatch):
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    # 200,000 × 1주 = 200,000 > 100,000 한도 → 1주 예외 적용됨
    r = checker.check(condition=_cond(qty=1), current_price=200_000, now=datetime.now())
    assert r.allowed, r.reason


# ---- KRX 휴장일 차단 ----

def test_krx_holiday_blocks_order(env, monkeypatch):
    """KRX 휴장일에는 SafetyChecker가 주문을 차단한다."""
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: True)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert not r.allowed
    assert "휴장" in r.reason or "holiday" in r.reason.lower() or "krx" in r.reason.lower()


def test_non_holiday_does_not_block(env, monkeypatch):
    """KRX 휴장일이 아닌 날에는 holiday 사유로 차단하지 않는다."""
    repo, checker = env
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert r.allowed, r.reason


# ---- TASK-087 A2: deployment env flag gate ----
def test_auto_exec_flag_blocks(env, monkeypatch):
    """Env flag OFF → SafetyChecker blocks even when auto_trading_enabled=true in DB."""
    repo, checker = env
    monkeypatch.delenv("AUTOFOLIO_AUTO_EXEC_ENABLED", raising=False)
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
    assert not r.allowed
    assert (
        "locked" in r.reason.lower()
        or "AUTOFOLIO_AUTO_EXEC_ENABLED" in r.reason
    )
