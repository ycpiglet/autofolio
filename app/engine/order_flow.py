from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import time

from app.brokers.base import BrokerClient, OrderRequest
from app.common.enums import ConditionStatus, OrderStatus, OrderType, Side
from app.config.settings import settings
from app.database.repositories import Repository
from app.risk.safety_checker import SafetyChecker
from app.engine.condition_evaluator import is_condition_triggered


@dataclass(frozen=True)
class OrderFlowResult:
    executed: bool
    message: str
    order_log_id: int | None = None


class OrderFlow:
    def __init__(
        self,
        *,
        broker: BrokerClient,
        repo: Repository,
        safety_checker: SafetyChecker,
        order_timeout_sec: int | None = None,
    ):
        self.broker = broker
        self.repo = repo
        self.safety_checker = safety_checker
        self.order_timeout_sec = (
            settings.default_order_timeout_sec
            if order_timeout_sec is None
            else order_timeout_sec
        )

    def process_condition_once(self, condition: dict) -> OrderFlowResult:
        quote = self.broker.get_current_price(condition["symbol"])
        current_price = quote.price

        triggered = is_condition_triggered(
            side=condition["side"],
            current_price=current_price,
            target_price=float(condition["target_price"]),
        )
        if not triggered:
            return OrderFlowResult(False, "Condition is not triggered.")

        safety = self.safety_checker.check(condition=condition, current_price=current_price)
        if not safety.allowed:
            return OrderFlowResult(False, f"Safety check rejected: {safety.reason}")

        order_type = OrderType(condition["order_type"])
        side = Side(condition["side"])
        quantity = int(condition["quantity"])

        order_price = None
        if order_type == OrderType.LIMIT:
            order_price = float(condition["target_price"])

        request = OrderRequest(
            symbol=condition["symbol"],
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=order_price,
        )

        result = self.broker.place_order(request)
        order_log_id = self.repo.create_order_log(
            condition_id=condition["id"],
            symbol=condition["symbol"],
            side=side.value,
            order_type=order_type.value,
            order_price=order_price,
            current_price=current_price,
            quantity=quantity,
            kis_order_id=result.broker_order_id,
            order_status=result.status.value,
            fallback_to_market=False,
            error_message=result.message if result.status == OrderStatus.FAILED else None,
        )

        if result.status == OrderStatus.FILLED:
            self.repo.create_execution_log(
                order_log_id=order_log_id,
                symbol=condition["symbol"],
                filled_price=result.filled_price,
                filled_quantity=result.filled_quantity,
                raw_status=result.message,
            )
            self._mark_condition_triggered(condition["id"])
            return OrderFlowResult(True, "Order filled.", order_log_id)

        if result.status == OrderStatus.PENDING:
            return self._handle_pending_limit_order(condition, result.broker_order_id, order_log_id, current_price)

        if result.status == OrderStatus.FAILED:
            self.repo.update_condition_status(condition["id"], ConditionStatus.ERROR.value)
            return OrderFlowResult(False, f"Order failed: {result.message}", order_log_id)

        return OrderFlowResult(False, f"Unhandled order status: {result.status}", order_log_id)

    def _handle_pending_limit_order(
        self,
        condition: dict,
        broker_order_id: str,
        order_log_id: int,
        current_price: float,
    ) -> OrderFlowResult:
        if self.order_timeout_sec > 0:
            time.sleep(self.order_timeout_sec)

        status = self.broker.get_order_status(broker_order_id)
        if status.status == OrderStatus.FILLED:
            self.repo.update_order_status(order_log_id, OrderStatus.FILLED.value)
            self.repo.create_execution_log(
                order_log_id=order_log_id,
                symbol=condition["symbol"],
                filled_price=status.filled_price,
                filled_quantity=status.filled_quantity,
                raw_status=status.message,
            )
            self._mark_condition_triggered(condition["id"])
            return OrderFlowResult(True, "Pending order filled.", order_log_id)

        cancel_result = self.broker.cancel_order(broker_order_id)
        if cancel_result.status != OrderStatus.CANCELED:
            self.repo.update_order_status(
                order_log_id,
                OrderStatus.FAILED.value,
                "Failed to cancel pending order.",
            )
            self.repo.set_system_state("auto_trading_enabled", "false")
            return OrderFlowResult(False, "Failed to cancel pending order. Auto trading disabled.", order_log_id)

        self.repo.update_order_status(order_log_id, OrderStatus.CANCELED.value)

        if not bool(condition.get("allow_market_fallback")):
            self._mark_condition_triggered(condition["id"])
            return OrderFlowResult(False, "Limit order canceled. Market fallback disabled.", order_log_id)

        return self._fallback_to_market(condition, current_price)

    def _fallback_to_market(self, condition: dict, current_price: float) -> OrderFlowResult:
        request = OrderRequest(
            symbol=condition["symbol"],
            side=Side(condition["side"]),
            order_type=OrderType.MARKET,
            quantity=int(condition["quantity"]),
            price=None,
        )
        result = self.broker.place_order(request)
        order_log_id = self.repo.create_order_log(
            condition_id=condition["id"],
            symbol=condition["symbol"],
            side=condition["side"],
            order_type=OrderType.MARKET.value,
            order_price=None,
            current_price=current_price,
            quantity=int(condition["quantity"]),
            kis_order_id=result.broker_order_id,
            order_status=result.status.value,
            fallback_to_market=True,
            error_message=result.message if result.status == OrderStatus.FAILED else None,
        )

        if result.status == OrderStatus.FILLED:
            self.repo.create_execution_log(
                order_log_id=order_log_id,
                symbol=condition["symbol"],
                filled_price=result.filled_price,
                filled_quantity=result.filled_quantity,
                raw_status=result.message,
            )
            self._mark_condition_triggered(condition["id"])
            return OrderFlowResult(True, "Market fallback filled.", order_log_id)

        self.repo.update_condition_status(condition["id"], ConditionStatus.ERROR.value)
        return OrderFlowResult(False, "Market fallback failed.", order_log_id)

    def _mark_condition_triggered(self, condition_id: int) -> None:
        self.repo.update_condition_status(condition_id, ConditionStatus.TRIGGERED.value)
        self.repo.set_condition_cooldown(
            condition_id,
            datetime.now() + timedelta(minutes=settings.default_cooldown_min),
        )
