"""Notion 알림 어댑터 — IC 결정·회고·일일 요약을 Notion DB에 기록. [Autofolio]

설정(.env):
  NOTION_TOKEN=secret_xxx              # Integration 토큰
  NOTION_DATABASE_ID=xxxxxxxxxxxxxxxx  # 기록할 DB page ID

Notion Integration 생성: https://www.notion.so/my-integrations
"""
from __future__ import annotations

import os
from datetime import datetime

from app.common.logger import get_logger
from app.notification.base import BaseNotifier

logger = get_logger("autofolio.notion")


class NotionNotifier(BaseNotifier):
    """Notion API BaseNotifier 구현 — 텍스트를 Notion DB 행으로 추가."""

    def __init__(self, token: str = "", database_id: str = ""):
        self._token = token
        self._database_id = database_id

    @property
    def channel_name(self) -> str:
        return "notion"

    @property
    def enabled(self) -> bool:
        return bool(self._token and self._database_id)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def send(self, text: str) -> None:
        if not self.enabled:
            logger.debug("[notion] 토큰 미설정 — 스킵")
            return
        try:
            import requests
            payload = {
                "parent": {"database_id": self._database_id},
                "properties": {
                    "Name": {"title": [{"text": {"content": text[:100]}}]},
                    "Date": {"date": {"start": datetime.now().isoformat(timespec="seconds")}},
                    "Content": {"rich_text": [{"text": {"content": text[:2000]}}]},
                },
            }
            r = requests.post(
                "https://api.notion.com/v1/pages",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
            if r.status_code >= 400:
                logger.warning("[notion] 기록 실패: %s %s", r.status_code, r.text[:200])
            else:
                logger.info("[notion] 기록 완료")
        except Exception as exc:  # noqa: BLE001
            logger.warning("[notion] 예외: %s", exc)

    def log_ic_decision(self, topic: str, decision: str, path: str = "") -> None:
        """IC 결정을 Notion에 기록."""
        text = f"[IC 결정] {topic}\n\n{decision[:1500]}"
        if path:
            text += f"\n\n파일: {path}"
        self.send(text)

    def log_retro(self, period: str, forward_actions: str) -> None:
        """회고 결과를 Notion에 기록."""
        self.send(f"[회고 {period}]\n\n{forward_actions[:1500]}")


def make_notion_notifier_from_env() -> NotionNotifier:
    return NotionNotifier(
        token=os.getenv("NOTION_TOKEN", ""),
        database_id=os.getenv("NOTION_DATABASE_ID", ""),
    )
