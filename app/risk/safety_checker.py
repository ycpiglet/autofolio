from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.config.settings import settings
from app.database.repositories import Repository
from app.risk.duplicate_guard import is_condition_executable
from app.risk.trading_window import is_within_trading_window


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    reason: str = ""


class SafetyChecker:
    def __init__(self, repo: Repository):
        self.repo = repo

    def check(
        self,
        *,
        condition: dict,
        current_price: float,
        now: datetime | None = None,
    ) -> SafetyResult:
        now = now or datetime.now()

        if self.repo.get_system_state("kill_switch_active", "false") == "true":
            return SafetyResult(False, "Kill switch is active.")

        if self.repo.get_system_state("auto_trading_enabled", "false") != "true":
            return SafetyResult(False, "Auto trading is disabled.")

        symbol_info = self.repo.get_whitelist_symbol(condition["symbol"])
        if not symbol_info:
            return SafetyResult(False, "Symbol is not enabled in whitelist.")

        if not is_within_trading_window(
            now,
            settings.default_trading_start,
            settings.default_trading_end,
        ):
            return SafetyResult(False, "Outside trading window.")

        if not is_condition_executable(
            condition["status"],
            condition.get("cooldown_until"),
            now,
        ):
            return SafetyResult(False, "Condition is not executable due to status or cooldown.")

        quantity = int(condition["quantity"])
        order_amount = current_price * quantity
        limit = self.repo.get_global_risk_limit()

        max_order_amount = float(limit["max_order_amount"])
        allow_one_share_exception = bool(limit["allow_one_share_exception"])

        if order_amount > max_order_amount:
            if not (allow_one_share_exception and quantity == 1):
                return SafetyResult(
                    False,
                    f"Order amount {order_amount:.0f} exceeds max order amount {max_order_amount:.0f}.",
                )

        today_amount = self.repo.today_order_amount()
        max_daily_amount = float(limit["max_daily_amount"])
        if today_amount + order_amount > max_daily_amount:
            return SafetyResult(False, "Daily order amount limit exceeded.")

        return SafetyResult(True, "Allowed.")
