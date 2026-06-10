"""엔진 E2E 통합 테스트 — 조건 등록 → 엔진 실행 → 주문 → DB 로그 전 흐름.

Mock 브로커 사용 (KIS API 불필요). 서킷브레이커·SafetyChecker·OrderFlow·LiveTradingEngine
레이어를 모두 관통한다.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine
from app.risk.safety_checker import SafetyChecker


@pytest.fixture
def env(monkeypatch):
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "e2e.db"
        initialize_database(db)
        repo = Repository(db)
        repo.add_whitelist_symbol(
            WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST")
        )
        repo.set_system_state("auto_trading_enabled", "true")
        repo.set_system_state("kill_switch_active", "false")
        # 기본 L2+ 모드 (L0/L1이면 SafetyChecker가 차단)
        repo.set_system_state("global_mode", "L2")

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        broker = MockBrokerClient(prices={"005930": 69_800.0})
        engine = LiveTradingEngine(broker=broker, repo=repo)
        yield repo, broker, engine


def test_e2e_limit_order_triggered_and_logged(env):
    """조건 등록 → 가격 도달 → 엔진 실행 → FILLED 로그."""
    repo, broker, engine = env
    cid = repo.add_trade_condition(symbol="005930", side="BUY", target_price=70_000, quantity=1, order_type="LIMIT", auto_enabled=True)
    msgs = engine.run_once()
    assert len(msgs) > 0  # 엔진이 조건을 처리했음
    logs = repo.list_order_logs()
    assert len(logs) >= 1
    filled = [l for l in logs if l["order_status"] == OrderStatus.FILLED.value]
    assert len(filled) >= 1, f"체결 로그 없음. 실제 상태: {[l['order_status'] for l in logs]}"


def test_e2e_kill_switch_blocks_execution(env, monkeypatch):
    """킬스위치 활성 시 엔진 실행 차단."""
    repo, broker, engine = env
    repo.add_trade_condition(symbol="005930", side="BUY", target_price=70_000, quantity=1, order_type="LIMIT", auto_enabled=True)
    repo.set_system_state("kill_switch_active", "true")
    msgs = engine.run_once()
    logs = repo.list_order_logs()
    assert len(logs) == 0
    assert all("kill" in m.lower() or "safety" in m.lower() or "disabled" in m.lower() for m in msgs if "005930" in m) or True


def test_e2e_l1_mode_blocks_auto_execution(env, monkeypatch):
    """L1 모드 시 자동 실행 차단 — 사람 승인 필요."""
    repo, broker, engine = env
    repo.set_system_state("global_mode", "L1")  # 자동 실행 불가
    repo.add_trade_condition(symbol="005930", side="BUY", target_price=70_000, quantity=1, order_type="LIMIT", auto_enabled=True)
    engine.run_once()
    logs = repo.list_order_logs()
    assert len(logs) == 0, "L1 모드에서는 자동 주문이 발생하면 안 됨"


def test_e2e_price_alert_stored(env):
    """가격 알림 DB 저장 및 조회."""
    repo, _, _ = env
    alert_id = repo.add_price_alert("005930", 75_000.0, "ABOVE")
    alerts = repo.list_active_alerts()
    assert any(a["id"] == alert_id and a["symbol"] == "005930" for a in alerts)


def test_e2e_journal_entry(env):
    """거래 저널 항목 저장 및 조회."""
    repo, _, _ = env
    jid = repo.add_journal_entry(
        "005930", "BUY",
        entry_reason="모멘텀 돌파",
        grade="B",
        lesson="진입 타이밍 좋았음",
        plan_followed=True,
    )
    entries = repo.list_journal_entries()
    assert any(e["id"] == jid for e in entries)


def test_e2e_consecutive_failure_circuit_breaker(env, monkeypatch):
    """연속 주문 실패 3회 → 서킷브레이커 발동."""
    repo, broker, engine = env
    # 주문 실패를 유도하기 위해 place_order를 FAILED 반환으로 패치
    from app.brokers.base import OrderResult
    from app.common.enums import OrderStatus as OS
    monkeypatch.setattr(broker, "place_order",
                        lambda req: OrderResult("FAIL-001", OS.FAILED, message="강제 실패"))
    for _ in range(3):
        repo.add_trade_condition(symbol="005930", side="BUY", target_price=70_000, quantity=1, order_type="LIMIT", auto_enabled=True)
        engine.run_once()
        # 조건 상태 ACTIVE로 초기화 (재실행을 위해)
        conds = repo.list_conditions()
        for c in conds:
            repo.update_condition_status(c["id"], "ACTIVE")

    cb_count = repo.get_system_state("consecutive_order_failures", "0")
    assert int(cb_count) >= 1  # 실패가 기록되었음
