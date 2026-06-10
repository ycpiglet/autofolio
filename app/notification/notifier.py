"""Telegram 알림 어댑터 — BaseNotifier 구현. [Autofolio]

Telegram 토큰이 있으면 발송, 없으면 로그만.
사용처: LiveTradingEngine, NotificationBus 등.
"""
from __future__ import annotations

from app.common.logger import get_logger
from app.notification.base import BaseNotifier

logger = get_logger("autofolio.notifier")


class Notifier(BaseNotifier):
    """Telegram BaseNotifier 구현. 토큰 없으면 로그-only 폴백."""

    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self._bot_token = bot_token
        self._chat_id = chat_id

    @property
    def channel_name(self) -> str:
        return "telegram"

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

    def send_engine_summary(self, run_count: int, executed: int, errors: int) -> None:
        self.send(f"🤖 엔진 실행 #{run_count}: 처리={executed} 체결, 오류={errors}")


def make_notifier_from_env() -> Notifier:
    import os
    return Notifier(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
