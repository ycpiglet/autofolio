"""통합 알림 발송 — Telegram 채널 우선, 미설정 시 로그만. [Autofolio]

사용처: LiveTradingEngine.run_once() 체결/오류 시 호출.
"""
from __future__ import annotations

from app.common.logger import get_logger

logger = get_logger("autofolio.notifier")


class Notifier:
    """Telegram 토큰이 있으면 발송, 없으면 로그만."""

    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self._bot_token = bot_token
        self._chat_id = chat_id

    @property
    def enabled(self) -> bool:
        return bool(self._bot_token and self._chat_id)

    def send(self, text: str) -> None:
        logger.info("[notify] %s", text)
        if not self.enabled:
            return
        try:
            import requests
            requests.post(
                f"https://api.telegram.org/bot{self._bot_token}/sendMessage",
                json={"chat_id": self._chat_id, "text": text},
                timeout=8,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Telegram 발송 실패: %s", exc)

    def send_fill(self, symbol: str, side: str, qty: int, price: float | None) -> None:
        price_str = f"@{price:,.0f}" if price else ""
        self.send(f"✅ 체결: {symbol} {side} {qty}주 {price_str}")

    def send_error(self, context: str, detail: str) -> None:
        self.send(f"❌ 오류 [{context}]: {detail}")

    def send_engine_summary(self, run_count: int, executed: int, errors: int) -> None:
        self.send(
            f"🤖 엔진 실행 #{run_count}: 처리={executed} 체결, 오류={errors}"
        )


def make_notifier_from_env() -> Notifier:
    import os
    return Notifier(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
