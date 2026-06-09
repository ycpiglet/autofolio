"""Telegram 명령봇 단위 테스트 — 순수 해석 + allowlist + 전송(페이크). 네트워크 없음."""
from __future__ import annotations

from app.notification.telegram_bot import HELP_TEXT, TelegramCommandBot


class FakeProvider:
    def status(self) -> dict:
        return {
            "env": "paper",
            "auto_enabled": False,
            "kill_switch": False,
            "whitelist_count": 3,
            "order_log_count": 2,
        }

    def pnl(self) -> dict:
        return {"market_value": 1_234_567.0, "pnl": 89_000.0, "positions": 2}

    def positions(self) -> list[dict]:
        return [
            {"symbol": "005930", "quantity": 10, "avg_price": 70000.0},
            {"symbol": "069500", "quantity": 40, "avg_price": 36500.0},
        ]


def _bot(allowed=("100",)):
    sent: list[tuple] = []
    bot = TelegramCommandBot(
        provider=FakeProvider(),
        send_fn=lambda chat_id, text: sent.append((chat_id, text)),
        allowed_chat_ids=list(allowed),
    )
    return bot, sent


def _update(text: str, chat_id="100") -> dict:
    return {"message": {"chat": {"id": chat_id}, "text": text}}


# ----- 명령 해석 -----
def test_help_for_unknown_and_help():
    bot, _ = _bot()
    assert bot.handle_text("/help") == HELP_TEXT
    assert bot.handle_text("") == HELP_TEXT
    assert "알 수 없는 명령" in bot.handle_text("/frobnicate")
    assert HELP_TEXT in bot.handle_text("/frobnicate")


def test_status_command():
    bot, _ = _bot()
    out = bot.handle_text("/status")
    assert "환경: paper" in out
    assert "자동매매: OFF" in out
    assert "킬스위치: 해제" in out
    assert "화이트리스트: 3종목" in out


def test_pnl_command_formats_numbers():
    bot, _ = _bot()
    out = bot.handle_text("/pnl")
    assert "1,234,567" in out
    assert "89,000" in out
    assert "2종목" in out


def test_positions_command_lists_holdings():
    bot, _ = _bot()
    out = bot.handle_text("/positions")
    assert "005930" in out and "10주" in out
    assert "069500" in out and "40주" in out


def test_command_normalizes_botname_suffix():
    bot, _ = _bot()
    assert "환경: paper" in bot.handle_text("/status@AutofolioBot")


def test_positions_empty():
    class Empty(FakeProvider):
        def positions(self):
            return []

    bot = TelegramCommandBot(provider=Empty(), allowed_chat_ids=["100"])
    assert bot.handle_text("/positions") == "보유 종목이 없습니다."


# ----- allowlist + 전송 -----
def test_handle_update_allowed_sends_reply():
    bot, sent = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/status", chat_id="100"))
    assert reply is not None and "상태" in reply
    assert len(sent) == 1
    assert sent[0][0] == "100"  # 보낸 사람에게 회신


def test_handle_update_unauthorized_ignored():
    bot, sent = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/status", chat_id="999"))  # 허용 외
    assert reply is None
    assert sent == []  # 전송 없음


def test_empty_allowlist_rejects_everything():
    bot = TelegramCommandBot(provider=FakeProvider(), allowed_chat_ids=None)
    assert bot.handle_update(_update("/status", chat_id="100")) is None


def test_send_failure_does_not_raise():
    def boom(chat_id, text):
        raise RuntimeError("network down")

    bot = TelegramCommandBot(provider=FakeProvider(), send_fn=boom, allowed_chat_ids=["100"])
    # 전송 실패해도 예외가 봇을 죽이지 않고 reply 는 반환된다.
    reply = bot.handle_update(_update("/status", chat_id="100"))
    assert reply is not None
