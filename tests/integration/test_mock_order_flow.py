from pathlib import Path
from tempfile import TemporaryDirectory

from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import OrderStatus
from app.database.sqlite_db import initialize_database
from app.database.repositories import Repository, WhitelistSymbol
from app.engine.order_flow import OrderFlow
from app.risk.safety_checker import SafetyChecker


def test_mock_order_flow_limit_fill(monkeypatch):
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        initialize_database(db_path)

        repo = Repository(db_path)
        repo.set_system_state("auto_trading_enabled", "true")
        repo.set_system_state("kill_switch_active", "false")
        repo.add_whitelist_symbol(
            WhitelistSymbol(
                symbol="005930",
                name="삼성전자",
                market="KRX",
                role="LARGE_CAP_TEST",
            )
        )
        condition_id = repo.add_trade_condition(
            symbol="005930",
            side="BUY",
            target_price=70000,
            quantity=1,
            order_type="LIMIT",
            allow_market_fallback=False,
            auto_enabled=True,
        )

        broker = MockBrokerClient(prices={"005930": 69900.0})
        flow = OrderFlow(
            broker=broker,
            repo=repo,
            safety_checker=SafetyChecker(repo),
            order_timeout_sec=0,
        )
        condition = repo.get_condition(condition_id)

        # 테스트 시간은 장중으로 고정한다.
        import app.risk.safety_checker as safety_checker_module
        monkeypatch.setattr(safety_checker_module, "is_within_trading_window", lambda *args, **kwargs: True)

        result = flow.process_condition_once(condition)

        assert result.executed
        logs = repo.list_order_logs()
        assert logs[0]["order_status"] == OrderStatus.FILLED.value


def test_mock_order_flow_pending_cancel_then_market_fallback(monkeypatch):
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        initialize_database(db_path)

        repo = Repository(db_path)
        repo.set_system_state("auto_trading_enabled", "true")
        repo.set_system_state("kill_switch_active", "false")
        repo.add_whitelist_symbol(
            WhitelistSymbol(
                symbol="005930",
                name="삼성전자",
                market="KRX",
                role="LARGE_CAP_TEST",
            )
        )
        condition_id = repo.add_trade_condition(
            symbol="005930",
            side="BUY",
            target_price=70000,
            quantity=1,
            order_type="LIMIT",
            allow_market_fallback=True,
            auto_enabled=True,
        )

        broker = MockBrokerClient(prices={"005930": 69900.0}, fill_limit_orders=False)
        flow = OrderFlow(
            broker=broker,
            repo=repo,
            safety_checker=SafetyChecker(repo),
            order_timeout_sec=0,
        )
        condition = repo.get_condition(condition_id)

        import app.risk.safety_checker as safety_checker_module
        monkeypatch.setattr(safety_checker_module, "is_within_trading_window", lambda *args, **kwargs: True)

        result = flow.process_condition_once(condition)

        assert result.executed
        logs = repo.list_order_logs()
        assert len(logs) == 2
        assert logs[0]["fallback_to_market"] == 1
        assert logs[0]["order_status"] == OrderStatus.FILLED.value
