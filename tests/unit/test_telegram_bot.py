"""Telegram 명령봇 단위 테스트 — 순수 해석 + allowlist + 전송(페이크). 네트워크 없음."""
from __future__ import annotations

from app.notification.telegram_bot import HELP_TEXT, TelegramCommandBot


class FakeProvider:
    def __init__(self):
        self._auto_enabled: bool = False
        self._kill_switch: bool = False

    def status(self) -> dict:
        return {
            "env": "paper",
            "auto_enabled": self._auto_enabled,
            "kill_switch": self._kill_switch,
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

    def conditions(self) -> list[dict]:
        return [
            {
                "symbol": "005930",
                "side": "BUY",
                "target_price": 68000.0,
                "quantity": 5,
                "status": "ACTIVE",
            },
            {
                "symbol": "035420",
                "side": "SELL",
                "target_price": 220000.0,
                "quantity": 2,
                "status": "ACTIVE",
            },
        ]

    def run_engine(self) -> list[str]:
        return ["005930 BUY 트리거 (68,000 <= 현재가 67,900)", "조건 2건 검사"]

    def propose(self, symbol: str, side: str) -> str:
        return (
            f"💡 IC 제안 [{symbol} {side}]\n"
            "목표가: 68,000\n"
            "수량: 5\n"
            "근거: 52주 저점 근접, PBR 0.8x"
        )

    def set_auto_enabled(self, value: bool) -> None:
        self._auto_enabled = value

    def set_kill_switch(self, value: bool) -> None:
        self._kill_switch = value


def _bot(allowed=("100",)):
    provider = FakeProvider()
    sent: list[tuple] = []
    bot = TelegramCommandBot(
        provider=provider,
        send_fn=lambda chat_id, text: sent.append((chat_id, text)),
        allowed_chat_ids=list(allowed),
    )
    return bot, sent, provider


def _update(text: str, chat_id="100") -> dict:
    return {"message": {"chat": {"id": chat_id}, "text": text}}


# ----- 명령 해석 -----
def test_help_for_unknown_and_help():
    bot, _, _ = _bot()
    assert bot.handle_text("/help") == HELP_TEXT
    assert bot.handle_text("") == HELP_TEXT
    assert "알 수 없는 명령" in bot.handle_text("/frobnicate")
    assert HELP_TEXT in bot.handle_text("/frobnicate")


def test_status_command():
    bot, _, _ = _bot()
    out = bot.handle_text("/status")
    assert "환경: paper" in out
    assert "자동매매: OFF" in out
    assert "킬스위치: 해제" in out
    assert "화이트리스트: 3종목" in out


def test_pnl_command_formats_numbers():
    bot, _, _ = _bot()
    out = bot.handle_text("/pnl")
    assert "1,234,567" in out
    assert "89,000" in out
    assert "2종목" in out


def test_positions_command_lists_holdings():
    bot, _, _ = _bot()
    out = bot.handle_text("/positions")
    assert "005930" in out and "10주" in out
    assert "069500" in out and "40주" in out


def test_command_normalizes_botname_suffix():
    bot, _, _ = _bot()
    assert "환경: paper" in bot.handle_text("/status@AutofolioBot")


def test_positions_empty():
    class Empty(FakeProvider):
        def positions(self):
            return []

    bot = TelegramCommandBot(provider=Empty(), allowed_chat_ids=["100"])
    assert bot.handle_text("/positions") == "보유 종목이 없습니다."


# ----- /conditions -----
def test_conditions_command_lists_active():
    bot, _, _ = _bot()
    out = bot.handle_text("/conditions")
    assert "활성 거래 조건" in out
    assert "005930" in out
    assert "BUY" in out
    assert "68,000" in out
    assert "035420" in out
    assert "SELL" in out


def test_conditions_empty():
    class NoConditions(FakeProvider):
        def conditions(self):
            return []

    bot = TelegramCommandBot(provider=NoConditions(), allowed_chat_ids=["100"])
    out = bot.handle_text("/conditions")
    assert "활성 거래 조건이 없습니다" in out


def test_conditions_shows_status_field():
    bot, _, _ = _bot()
    out = bot.handle_text("/conditions")
    assert "ACTIVE" in out


# ----- /engine -----
def test_engine_command_shows_results():
    bot, _, _ = _bot()
    out = bot.handle_text("/engine")
    assert "엔진 실행 결과" in out
    assert "005930" in out
    assert "트리거" in out


def test_engine_command_no_triggers():
    class NoTriggers(FakeProvider):
        def run_engine(self):
            return []

    bot = TelegramCommandBot(provider=NoTriggers(), allowed_chat_ids=["100"])
    out = bot.handle_text("/engine")
    assert "트리거된 조건 없음" in out


def test_engine_each_result_on_own_line():
    bot, _, _ = _bot()
    out = bot.handle_text("/engine")
    lines = out.splitlines()
    # header + 2 result lines
    assert len(lines) >= 3


# ----- /propose -----
def test_propose_command_returns_proposal():
    bot, _, _ = _bot()
    out = bot.handle_text("/propose 005930 BUY")
    assert "IC 제안" in out
    assert "005930" in out
    assert "BUY" in out
    assert "목표가" in out
    assert "근거" in out


def test_propose_defaults_to_buy_when_side_omitted():
    bot, _, _ = _bot()
    out = bot.handle_text("/propose 005930")
    assert "BUY" in out


def test_propose_sell_side():
    bot, _, _ = _bot()
    out = bot.handle_text("/propose 035420 SELL")
    assert "SELL" in out


def test_propose_symbol_uppercased():
    bot, _, _ = _bot()
    # lowercase symbol → should still work (uppercased internally)
    out = bot.handle_text("/propose 005930 buy")
    # invalid side "BUY" normalised, but "buy" → upper → "BUY" which is valid
    assert "IC 제안" in out


def test_propose_invalid_side_returns_error():
    bot, _, _ = _bot()
    out = bot.handle_text("/propose 005930 LONG")
    assert "방향 오류" in out


def test_propose_no_args_returns_usage():
    bot, _, _ = _bot()
    out = bot.handle_text("/propose")
    assert "사용법" in out


# ----- HELP_TEXT 포함 여부 -----
def test_help_text_includes_new_commands():
    assert "/conditions" in HELP_TEXT
    assert "/engine" in HELP_TEXT
    assert "/propose" in HELP_TEXT


def test_help_text_includes_state_commands():
    assert "/kill" in HELP_TEXT
    assert "/approve" in HELP_TEXT
    assert "/pause" in HELP_TEXT


# ----- allowlist + 전송 -----
def test_handle_update_allowed_sends_reply():
    bot, sent, _ = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/status", chat_id="100"))
    assert reply is not None and "상태" in reply
    assert len(sent) == 1
    assert sent[0][0] == "100"  # 보낸 사람에게 회신


def test_handle_update_unauthorized_ignored():
    bot, sent, _ = _bot(allowed=("100",))
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


def test_conditions_via_handle_update_sends_reply():
    bot, sent, _ = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/conditions", chat_id="100"))
    assert reply is not None
    assert "005930" in reply
    assert len(sent) == 1


def test_engine_via_handle_update_sends_reply():
    bot, sent, _ = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/engine", chat_id="100"))
    assert reply is not None
    assert "엔진 실행 결과" in reply
    assert len(sent) == 1


def test_propose_via_handle_update_sends_reply():
    bot, sent, _ = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/propose 005930 BUY", chat_id="100"))
    assert reply is not None
    assert "IC 제안" in reply
    assert len(sent) == 1


# ----- /kill -----
def test_kill_activates_kill_switch():
    bot, _, provider = _bot()
    assert provider._kill_switch is False
    out = bot.handle_text("/kill")
    assert provider._kill_switch is True
    assert "킬스위치 활성화" in out


def test_kill_off_deactivates_kill_switch():
    bot, _, provider = _bot()
    provider._kill_switch = True
    out = bot.handle_text("/kill off")
    assert provider._kill_switch is False
    assert "킬스위치 해제" in out


def test_kill_off_case_insensitive():
    bot, _, provider = _bot()
    provider._kill_switch = True
    out = bot.handle_text("/kill OFF")
    assert provider._kill_switch is False
    assert "킬스위치 해제" in out


def test_kill_with_unknown_arg_still_activates():
    """알 수 없는 인자는 무시하고 활성화."""
    bot, _, provider = _bot()
    out = bot.handle_text("/kill now")
    assert provider._kill_switch is True
    assert "킬스위치 활성화" in out


# ----- /approve -----
def test_approve_without_confirm_is_refused():
    bot, _, provider = _bot()
    out = bot.handle_text("/approve")
    assert provider._auto_enabled is False
    assert "confirm" in out.lower() or "확인" in out


def test_approve_with_wrong_keyword_is_refused():
    bot, _, provider = _bot()
    out = bot.handle_text("/approve yes")
    assert provider._auto_enabled is False
    assert "confirm" in out.lower() or "확인" in out


def test_approve_confirm_enables_auto_trading():
    bot, _, provider = _bot()
    assert provider._auto_enabled is False
    out = bot.handle_text("/approve confirm")
    assert provider._auto_enabled is True
    assert "자동매매 활성화" in out


def test_approve_confirm_case_insensitive():
    bot, _, provider = _bot()
    out = bot.handle_text("/approve CONFIRM")
    assert provider._auto_enabled is True
    assert "자동매매 활성화" in out


# ----- /pause -----
def test_pause_disables_auto_trading():
    bot, _, provider = _bot()
    provider._auto_enabled = True
    out = bot.handle_text("/pause")
    assert provider._auto_enabled is False
    assert "비활성화" in out


def test_pause_when_already_disabled_is_idempotent():
    bot, _, provider = _bot()
    assert provider._auto_enabled is False
    out = bot.handle_text("/pause")
    assert provider._auto_enabled is False
    assert "비활성화" in out


# ----- state change commands blocked for unauthorized users -----
def test_kill_unauthorized_is_ignored():
    bot, sent, provider = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/kill", chat_id="999"))
    assert reply is None
    assert provider._kill_switch is False
    assert sent == []


def test_approve_confirm_unauthorized_is_ignored():
    bot, sent, provider = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/approve confirm", chat_id="999"))
    assert reply is None
    assert provider._auto_enabled is False
    assert sent == []


def test_pause_unauthorized_is_ignored():
    bot, sent, provider = _bot(allowed=("100",))
    reply = bot.handle_update(_update("/pause", chat_id="999"))
    assert reply is None
    assert provider._auto_enabled is False
    assert sent == []
