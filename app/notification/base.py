"""채널 어댑터 추상화 — BaseNotifier 인터페이스 + 팬아웃 버스. [Autofolio]

설계 원칙:
- 모든 채널(Telegram·Discord·Email·Kakao·Notion 등)은 BaseNotifier를 구현.
- NotificationBus가 등록된 어댑터에 팬아웃.
- 어댑터를 끼웠다 뺐다 할 수 있다(PRODUCT_BLUEPRINT §5 채널 어댑터).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from app.common.logger import get_logger

logger = get_logger("autofolio.notification.bus")


class BaseNotifier(ABC):
    """모든 알림 채널이 구현해야 하는 인터페이스."""

    @property
    @abstractmethod
    def channel_name(self) -> str: ...

    @property
    @abstractmethod
    def enabled(self) -> bool: ...

    @abstractmethod
    def send(self, text: str) -> None: ...

    # ── 편의 메서드 (기본 구현 = send() 위임) ──────────────────────────────

    def send_fill(self, symbol: str, side: str, qty: int, price: float | None) -> None:
        price_str = f"@{price:,.0f}" if price else ""
        self.send(f"✅ 체결: {symbol} {side} {qty}주 {price_str}")

    def send_error(self, context: str, detail: str) -> None:
        self.send(f"❌ 오류 [{context}]: {detail}")

    def send_engine_summary(self, run: int, executed: int, errors: int) -> None:
        self.send(f"🤖 엔진 #{run}: 체결={executed} 오류={errors}")


class NotificationBus:
    """등록된 어댑터 전체에 팬아웃하는 버스.

    Example::
        bus = NotificationBus([TelegramAdapter(...), DiscordAdapter(...)])
        bus.send("주문 완료")
    """

    def __init__(self, adapters: Sequence[BaseNotifier] | None = None) -> None:
        self._adapters: list[BaseNotifier] = list(adapters or [])

    def register(self, adapter: BaseNotifier) -> None:
        self._adapters.append(adapter)

    def send(self, text: str) -> None:
        for a in self._adapters:
            if not a.enabled:
                continue
            try:
                a.send(text)
            except Exception as exc:  # noqa: BLE001
                logger.warning("[%s] 발송 실패: %s", a.channel_name, exc)

    def send_fill(self, symbol: str, side: str, qty: int, price: float | None) -> None:
        for a in self._adapters:
            if a.enabled:
                try:
                    a.send_fill(symbol, side, qty, price)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("[%s] send_fill 실패: %s", a.channel_name, exc)

    def send_error(self, context: str, detail: str) -> None:
        for a in self._adapters:
            if a.enabled:
                try:
                    a.send_error(context, detail)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("[%s] send_error 실패: %s", a.channel_name, exc)

    def send_engine_summary(self, run: int, executed: int, errors: int) -> None:
        for a in self._adapters:
            if a.enabled:
                try:
                    a.send_engine_summary(run, executed, errors)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("[%s] summary 실패: %s", a.channel_name, exc)

    @property
    def enabled(self) -> bool:
        return any(a.enabled for a in self._adapters)
