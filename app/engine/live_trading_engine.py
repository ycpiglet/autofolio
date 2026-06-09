from __future__ import annotations

from app.brokers.base import BrokerClient
from app.common.logger import get_logger
from app.database.repositories import Repository
from app.engine.order_flow import OrderFlow
from app.notification.telegram_notifier import TelegramNotifier
from app.risk.safety_checker import SafetyChecker


logger = get_logger(__name__)


class LiveTradingEngine:
    def __init__(
        self,
        *,
        broker: BrokerClient,
        repo: Repository,
        notifier: TelegramNotifier | None = None,
    ):
        self.broker = broker
        self.repo = repo
        self.safety_checker = SafetyChecker(repo)
        self.order_flow = OrderFlow(
            broker=broker,
            repo=repo,
            safety_checker=self.safety_checker,
        )
        self.notifier = notifier

    def run_once(self) -> list[str]:
        messages: list[str] = []
        for condition in self.repo.list_active_conditions():
            try:
                result = self.order_flow.process_condition_once(condition)
                messages.append(f"condition_id={condition['id']}: {result.message}")
                if result.executed and self.notifier:
                    self.notifier.send_message(
                        f"[ORDER] {condition['symbol']} {condition['side']} executed. {result.message}"
                    )
            except Exception as exc:
                logger.exception("Failed to process condition %s", condition.get("id"))
                self.repo.update_condition_status(condition["id"], "ERROR")
                messages.append(f"condition_id={condition['id']}: ERROR {exc}")
                if self.notifier:
                    self.notifier.send_message(f"[ERROR] condition {condition['id']}: {exc}")
        return messages
