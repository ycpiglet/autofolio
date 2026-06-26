from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.config.settings import settings
from app.data.quality import validate_price_quote
from app.database.repositories import Repository
from app.data.krx_holidays import is_krx_holiday
from app.risk.order_policy import validate_order_policy
from app.risk.duplicate_guard import is_condition_executable
from app.risk.trading_window import is_within_order_session, is_within_trading_window, now_kst


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
        quote: object | None = None,
        now: datetime | None = None,
    ) -> SafetyResult:
        now = now or now_kst()

        if quote is not None:
            data_quality = validate_price_quote(quote, now=now)
            if not data_quality.ok:
                return SafetyResult(False, f"Market data rejected: {data_quality.reason}")

        if self.repo.get_system_state("kill_switch_active", "false") == "true":
            return SafetyResult(False, "Kill switch is active.")

        from app.services import flags as _flags
        if not _flags.auto_exec_enabled():
            return SafetyResult(False, "Auto-exec locked: AUTOFOLIO_AUTO_EXEC_ENABLED not set.")

        if self.repo.get_system_state("auto_trading_enabled", "false") != "true":
            return SafetyResult(False, "Auto trading is disabled.")

        # --- L0-L4 종목별 모드 체크 ---
        # L0(관찰)/L1(자문)은 자동 실행 금지. L2+ 만 엔진이 실행한다.
        symbol = condition.get("symbol", "")
        symbol_mode = self.repo.get_system_state(f"symbol_mode_{symbol}", None)
        if symbol_mode is None:
            # 전역 모드 폴백 — 기본 L2(반자동)로 엔진 실행 허용
            symbol_mode = self.repo.get_system_state("global_mode", "L2")
        if symbol_mode in ("L0", "L1"):
            return SafetyResult(
                False,
                f"Autonomy level {symbol_mode} — manual approval required for {symbol}.",
            )
        condition = dict(condition)
        condition["symbol_mode"] = symbol_mode

        # --- Circuit breaker: consecutive order failures ---
        consecutive_failures_str = self.repo.get_system_state("consecutive_order_failures", "0")
        try:
            consecutive_failures = int(consecutive_failures_str)
        except (ValueError, TypeError):
            consecutive_failures = 0
        if consecutive_failures >= 3:
            self.repo.set_system_state("auto_trading_enabled", "false")
            return SafetyResult(False, "Circuit breaker: 3 consecutive order failures.")

        # --- Circuit breaker: daily loss threshold ---
        threshold_pct_str = self.repo.get_system_state("circuit_breaker_threshold_pct", "3.0")
        try:
            threshold_pct = float(threshold_pct_str)
        except (ValueError, TypeError):
            threshold_pct = 3.0

        today_pnl = self.repo.today_realized_pnl()
        # today_pnl is negative when net cash outflow exceeds inflow (net loss).
        # We compare the absolute loss against the threshold expressed as a
        # fraction of |today_pnl| relative to a reference. Because we do not
        # track total portfolio value here, we use the magnitude of the realized
        # loss directly: if the loss expressed as a positive percentage of the
        # daily-amount limit exceeds the threshold, we trip the breaker.
        if today_pnl < 0:
            try:
                limit = self.repo.get_global_risk_limit()
                reference = float(limit["max_daily_amount"])
            except Exception:
                reference = 0.0
            if reference > 0:
                loss_pct = abs(today_pnl) / reference * 100.0
                if loss_pct >= threshold_pct:
                    self.repo.set_system_state("auto_trading_enabled", "false")
                    return SafetyResult(
                        False,
                        "Circuit breaker triggered: daily loss exceeded threshold.",
                    )

        symbol_info = self.repo.get_whitelist_symbol(condition["symbol"])
        if not symbol_info:
            return SafetyResult(False, "Symbol is not enabled in whitelist.")

        order_session = str(condition.get("order_session") or "REGULAR").upper()
        if order_session == "REGULAR":
            in_window = is_within_trading_window(
                now,
                settings.default_trading_start,
                settings.default_trading_end,
            )
        else:
            in_window = is_within_order_session(order_session, now)
        if not in_window:
            return SafetyResult(False, f"Outside {order_session.lower()} trading window.")

        # --- KRX 휴장일 차단 ---
        if is_krx_holiday(now.date()):
            return SafetyResult(False, "KRX 휴장일 — 오늘은 KRX 휴장일입니다.")

        policy = validate_order_policy(
            condition=condition,
            current_price=current_price,
            whitelist_symbol=symbol_info,
            system_state=self._policy_state(condition["symbol"]),
            kis_env=settings.kis_env,
        )
        if not policy.allowed:
            return SafetyResult(False, policy.reason)

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

    def _policy_state(self, symbol: str) -> dict[str, str]:
        keys = (
            "global_mode",
            "market_wide_halt",
            "derivatives_mock_enabled",
            "basket_mock_enabled",
            "overseas_paper_enabled",
            f"symbol_mode_{symbol}",
            f"market_halt_{symbol}",
            f"vi_active_{symbol}",
            f"disclosure_block_{symbol}",
        )
        return {key: self.repo.get_system_state(key, "false") for key in keys}
