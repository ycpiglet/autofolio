from __future__ import annotations

from app.brokers.base import BrokerClient
from app.common.enums import ConditionStatus
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

            # Atomic CAS claim: ACTIVE → PROCESSING.
            # If another concurrent run_once() already claimed this condition,
            # skip it entirely to prevent duplicate order execution.
            if not self.repo.atomic_claim_condition(cid):
                log_event(
                    logger, "condition_skipped_already_claimed",
                    run=run_id, symbol=sym, condition_id=cid,
                )
                messages.append(f"condition_id={cid}: skipped (already claimed)")
                continue

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
                else:
                    # If process_condition_once() returned without triggering a terminal
                    # status transition (e.g. "not triggered", "safety blocked"), the
                    # condition is still PROCESSING.  Release the claim so the next
                    # run_once() cycle can re-evaluate it.
                    current = self.repo.get_condition(cid)
                    if current and current.get("status") == ConditionStatus.PROCESSING.value:
                        self.repo.update_condition_status(cid, ConditionStatus.ACTIVE.value)
            except Exception as exc:
                error_count += 1
                logger.exception("Failed to process condition %s", cid)
                # Transition PROCESSING → ERROR so the condition is not silently lost.
                self.repo.update_condition_status(cid, ConditionStatus.ERROR.value)
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
        self.evaluate_price_alerts()
        return messages

    def evaluate_price_alerts(self) -> list[str]:
        """가격 알림 평가 — active 알림 전체를 순회, 조건 충족 시 발송 후 비활성화.

        거래 시간 제한 없이 실행된다 (주문이 아닌 알림이므로).
        """
        alerts = self.repo.list_active_alerts()
        fired: list[str] = []
        for alert in alerts:
            alert_id = alert["id"]
            symbol = alert["symbol"]
            target_price = float(alert["target_price"])
            direction = alert["direction"]
            try:
                current_price = float(self.broker.get_current_price(symbol).price)
            except Exception as exc:  # noqa: BLE001
                log_event(logger, "price_alert_price_fetch_error",
                          alert_id=alert_id, symbol=symbol, error=str(exc))
                continue

            condition_met = (
                (direction == "ABOVE" and current_price >= target_price)
                or (direction == "BELOW" and current_price <= target_price)
            )
            if not condition_met:
                continue

            msg = (
                f"[가격 알림] {symbol} {direction} {target_price:,.0f} — "
                f"현재가 {current_price:,.0f}"
            )
            log_event(logger, "price_alert_fired",
                      alert_id=alert_id, symbol=symbol,
                      direction=direction, target_price=target_price,
                      current_price=current_price)
            if self.notifier:
                self.notifier.send(msg)
            self.repo.trigger_alert(alert_id)
            fired.append(msg)
        return fired
