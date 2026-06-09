#!/usr/bin/env python3
"""Telegram 봇 설정 도우미 — BotFather 토큰 검증 + chat_id 확인. [Autofolio]

사용:
  python scripts/setup_telegram.py --verify           # .env 토큰으로 봇 정보 확인
  python scripts/setup_telegram.py --get-chat-id      # 봇에 /start 보낸 후 chat_id 조회
  python scripts/setup_telegram.py --send "테스트"    # 테스트 메시지 발송

설정 순서:
  1) @BotFather에서 /newbot → 토큰 발급
  2) .env에 TELEGRAM_BOT_TOKEN=<토큰> 입력
  3) python scripts/setup_telegram.py --verify
  4) 봇에게 /start 메시지 전송
  5) python scripts/setup_telegram.py --get-chat-id
  6) .env에 TELEGRAM_CHAT_ID=<chat_id> 입력
  7) python scripts/setup_telegram.py --send "연동 완료"
"""
from __future__ import annotations

import argparse
import json
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


def _api(token: str, method: str, **params) -> dict:
    import requests
    r = requests.get(
        f"https://api.telegram.org/bot{token}/{method}",
        params=params or None, timeout=10,
    )
    return r.json()


def verify(token: str) -> None:
    res = _api(token, "getMe")
    if res.get("ok"):
        bot = res["result"]
        print(f"✅ 봇 확인: @{bot['username']} ({bot['first_name']})")
        print(f"   bot_id={bot['id']}")
    else:
        print(f"❌ 실패: {res.get('description')}")
        print("   토큰을 다시 확인하세요. (.env: TELEGRAM_BOT_TOKEN=...)")


def get_chat_id(token: str) -> None:
    print("봇에 /start 를 먼저 보냈는지 확인하세요.")
    res = _api(token, "getUpdates", limit=10, timeout=5)
    if not res.get("ok"):
        print(f"❌ {res.get('description')}")
        return
    updates = res.get("result", [])
    if not updates:
        print("업데이트 없음 — 봇에게 /start 를 먼저 보낸 후 다시 시도하세요.")
        return
    seen: set[str] = set()
    for u in updates:
        msg = u.get("message") or u.get("channel_post") or {}
        chat = msg.get("chat", {})
        cid = str(chat.get("id", ""))
        name = chat.get("title") or chat.get("first_name") or "?"
        if cid and cid not in seen:
            seen.add(cid)
            print(f"  chat_id={cid}  ({chat.get('type','?')}) {name}")
    if seen:
        print(f"\n.env에 TELEGRAM_CHAT_ID={list(seen)[0]}  # 을 추가하세요")


def send_test(token: str, chat_id: str, text: str) -> None:
    import requests
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text}, timeout=10,
    )
    d = r.json()
    if d.get("ok"):
        print(f"✅ 발송 완료 (message_id={d['result']['message_id']})")
    else:
        print(f"❌ 발송 실패: {d.get('description')}")
        print("   TELEGRAM_CHAT_ID를 확인하세요.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Telegram 봇 설정 도우미")
    ap.add_argument("--verify", action="store_true", help="봇 토큰 검증")
    ap.add_argument("--get-chat-id", action="store_true", help="최근 업데이트에서 chat_id 조회")
    ap.add_argument("--send", metavar="TEXT", help="테스트 메시지 발송")
    args = ap.parse_args()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN 미설정. .env에 토큰을 입력하세요.")
        return 2

    if args.verify or (not args.get_chat_id and not args.send):
        verify(token)

    if args.get_chat_id:
        get_chat_id(token)

    if args.send:
        if not chat_id:
            print("❌ TELEGRAM_CHAT_ID 미설정. --get-chat-id로 먼저 확인하세요.")
            return 2
        send_test(token, chat_id, args.send)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
