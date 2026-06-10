"""Discord 웹훅 알림 어댑터 — BaseNotifier 구현. [Autofolio]

설정: .env에 DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
Discord 서버에서: 채널 설정 → 연동 → 웹훅 → 웹훅 URL 복사.
"""
from __future__ import annotations

import os

from app.common.logger import get_logger
from app.notification.base import BaseNotifier

logger = get_logger("autofolio.discord")


class DiscordNotifier(BaseNotifier):
    """Discord 웹훅 BaseNotifier 구현."""

    def __init__(self, webhook_url: str = ""):
        self._webhook_url = webhook_url

    @property
    def channel_name(self) -> str:
        return "discord"

    @property
    def enabled(self) -> bool:
        return bool(self._webhook_url)

    def send(self, text: str) -> None:
        if not self.enabled:
            logger.debug("[discord] 웹훅 미설정 — 스킵")
            return
        try:
            import requests
            r = requests.post(
                self._webhook_url,
                json={"content": text[:2000]},  # Discord 2000자 제한
                timeout=8,
            )
            if r.status_code >= 400:
                logger.warning("[discord] 발송 실패: %s %s", r.status_code, r.text[:100])
        except Exception as exc:  # noqa: BLE001
            logger.warning("[discord] 예외: %s", exc)

    def send_fill(self, symbol: str, side: str, qty: int, price: float | None) -> None:
        price_str = f"@{price:,.0f}" if price else ""
        # Discord embed 형태로 전송
        embed = {
            "embeds": [{
                "title": f"✅ 체결 — {symbol}",
                "description": f"**{side}** {qty}주 {price_str}",
                "color": 0x2ECC71 if side == "BUY" else 0xE74C3C,
            }]
        }
        if not self.enabled:
            return
        try:
            import requests
            requests.post(self._webhook_url, json=embed, timeout=8)
        except Exception as exc:  # noqa: BLE001
            logger.warning("[discord] embed 발송 실패: %s", exc)


def make_discord_notifier_from_env() -> DiscordNotifier:
    return DiscordNotifier(webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""))
