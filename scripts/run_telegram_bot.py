#!/usr/bin/env python3
"""Autofolio Telegram 명령봇 실행기 (읽기 전용 명령). [Autofolio 호스트 스크립트]

`.env` 의 TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID 를 읽어 봇을 띄운다. 토큰이 없으면 안내 후 종료.
허용 대화(allowlist)는 TELEGRAM_CHAT_ID 로 한정한다(그 대화에서 온 명령만 응답).

사용:
  python scripts/run_telegram_bot.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.notification.telegram_bot import (  # noqa: E402
    BackendProvider,
    TelegramCommandBot,
    make_telegram_sender,
    poll_loop,
)


def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token:
        print("[중단] TELEGRAM_BOT_TOKEN 미설정. .env 에 봇 토큰을 넣어주세요.")
        return 2
    if not chat_id:
        print("[중단] TELEGRAM_CHAT_ID 미설정. 허용할 대화 id 가 없으면 모든 명령이 거부됩니다.")
        return 2

    bot = TelegramCommandBot(
        provider=BackendProvider(),
        send_fn=make_telegram_sender(token),
        allowed_chat_ids=[chat_id],
    )
    print(f"[telegram] 봇 시작 — 허용 chat_id={chat_id}. Ctrl+C 로 종료.")
    try:
        poll_loop(bot, token)
    except KeyboardInterrupt:
        print("\n[telegram] 종료.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
