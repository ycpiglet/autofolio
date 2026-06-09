from __future__ import annotations

from app.brokers.base import BrokerClient
from app.common.logger import get_structured_logger, log_event
from app.database.repositories import Repository
from app.engine.order_flow import OrderFlow
from app.notification.notifier import Notifier
from app.risk.safety_checker import SafetyChecker


logger = get_structured_logger(__name__)
_run_counter = 0


class LiveTradingEngine:
    def __init__(
        self,
        *,
        broker: BrokerClient,
        repo: Repository,
        notifier: Notifier | None = None,
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
        global _run_counter
        _run_counter += 1
        run_id = _run_counter

        conditions = list(self.repo.list_active_conditions())
        log_event(logger, "engine_run_start", run=run_id, conditions=len(conditions))

        messages: list[str] = []
        executed_count = 0
        error_count = 0

        for condition in conditions:
            cid = condition.get("id")
            sym = condition.get("symbol", "?")
            try:
                result = self.order_flow.process_condition_once(condition)
                messages.append(f"condition_id={cid}: {result.message}")
                log_event(
                    logger, "condition_processed",
                    run=run_id, symbol=sym, condition_id=cid,
                    executed=result.executed, message=result.message,
                )
                if result.executed:
                    executed_count += 1
                    if self.notifier:
                        self.notifier.send(
                            f"✅ 체결 [run#{run_id}]: {sym} {condition.get('side')} "
                            f"{condition.get('quantity')}주 — {result.message}"
                        )
            except Exception as exc:
                error_count += 1
                logger.exception("Failed to process condition %s", cid)
                self.repo.update_condition_status(cid, "ERROR")
                messages.append(f"condition_id={cid}: ERROR {exc}")
                log_event(logger, "condition_error", run=run_id, condition_id=cid, error=str(exc))
                if self.notifier:
                    self.notifier.send_error(f"condition {cid}", str(exc))

        log_event(
            logger, "engine_run_end",
            run=run_id, processed=len(conditions),
            executed=executed_count, errors=error_count,
        )
        if self.notifier and (executed_count > 0 or error_count > 0):
            self.notifier.send_engine_summary(run_id, executed_count, error_count)
        return messages
