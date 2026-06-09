"""Telegram 명령봇 — 읽기 전용 조회 명령. [Autofolio]

지원 명령(읽기 전용, **주문 실행 없음**): `/help` `/status` `/pnl` `/positions`
`/conditions` `/engine` `/propose`.
주문·킬스위치 등 상태 변경 명령은 안전상 별도 사이클(사람 승인 게이트)에서 다룬다.

설계
----
- 명령 해석(`handle_text`)은 순수 함수 → 단위 테스트가 쉽다(네트워크 불필요).
- 데이터는 `PortfolioProvider`(상태/손익/포지션/조건/엔진/제안)로 주입 → `BackendProvider` 는
  `app.ui.backend`(KIS_ENV 에 따라 mock/실 브로커)를 감싼다.
- 전송은 `send_fn(chat_id, text)` 주입 → 운영은 Telegram API, 테스트는 기록용 페이크.
- **보안**: allowlist(허용 chat_id)에 있는 대화에만 응답한다(기본 전체 거부).
"""
from __future__ import annotations

from typing import Callable, Protocol

from app.common.logger import get_logger

logger = get_logger("autofolio.telegram_bot")

HELP_TEXT = (
    "🤖 Autofolio 봇 (읽기 전용)\n"
    "/status — 운영 상태(환경·자동매매·킬스위치·화이트리스트)\n"
    "/pnl — 평가손익 요약\n"
    "/positions — 보유 종목\n"
    "/conditions — 활성 거래 조건 목록\n"
    "/engine — 엔진 1회 실행(읽기 전용, 트리거 시뮬레이션)\n"
    "/propose <심볼> [BUY|SELL] — IC 에이전트 조건 제안\n"
    "/help — 도움말"
)


class PortfolioProvider(Protocol):
    def status(self) -> dict: ...
    def pnl(self) -> dict: ...
    def positions(self) -> list[dict]: ...
    def conditions(self) -> list[dict]: ...
    def run_engine(self) -> list[str]: ...
    def propose(self, symbol: str, side: str) -> str: ...


class TelegramCommandBot:
    def __init__(
        self,
        provider: PortfolioProvider,
        send_fn: Callable[[object, str], None] | None = None,
        allowed_chat_ids: list | set | None = None,
    ):
        self.provider = provider
        self.send_fn = send_fn
        # allowlist: 빈 값 → 전부 거부(보안 기본). 명시된 chat_id 만 응답.
        self.allowed_chat_ids = {str(c) for c in (allowed_chat_ids or [])}

    # ----- 보안 -----
    def is_allowed(self, chat_id) -> bool:
        return chat_id is not None and str(chat_id) in self.allowed_chat_ids

    # ----- 명령 해석 (순수) -----
    def handle_text(self, text: str) -> str:
        raw = (text or "").strip()
        parts = raw.split() if raw else []
        cmd = parts[0].lower() if parts else ""
        cmd = cmd.split("@", 1)[0]  # /status@MyBot → /status
        args = parts[1:]

        if cmd == "/status":
            return self._status()
        if cmd == "/pnl":
            return self._pnl()
        if cmd == "/positions":
            return self._positions()
        if cmd == "/conditions":
            return self._conditions()
        if cmd == "/engine":
            return self._engine()
        if cmd == "/propose":
            return self._propose(args)
        if cmd in ("/help", "/start", ""):
            return HELP_TEXT
        return f"알 수 없는 명령: {cmd}\n\n{HELP_TEXT}"

    # ----- update 처리 (allowlist + 전송) -----
    def handle_update(self, update: dict) -> str | None:
        msg = (update or {}).get("message") or {}
        chat_id = (msg.get("chat") or {}).get("id")
        text = msg.get("text", "")
        if not self.is_allowed(chat_id):
            logger.warning("telegram: unauthorized chat_id=%s 무시", chat_id)
            return None
        reply = self.handle_text(text)
        logger.info("telegram cmd chat=%s text=%r", chat_id, (text or "")[:32])
        if self.send_fn is not None:
            try:
                self.send_fn(chat_id, reply)
            except Exception as exc:  # noqa: BLE001 — 전송 실패가 봇을 죽이지 않게
                logger.error("telegram reply 전송 실패: %s", exc)
        return reply

    # ----- handlers -----
    def _status(self) -> str:
        s = self.provider.status()
        return (
            "📊 상태\n"
            f"환경: {s.get('env', '?')}\n"
            f"자동매매: {'ON' if s.get('auto_enabled') else 'OFF'}\n"
            f"킬스위치: {'활성' if s.get('kill_switch') else '해제'}\n"
            f"화이트리스트: {s.get('whitelist_count', 0)}종목\n"
            f"주문로그: {s.get('order_log_count', 0)}건"
        )

    def _pnl(self) -> str:
        p = self.provider.pnl()
        return (
            "💰 손익\n"
            f"평가금액: {p.get('market_value', 0):,.0f}\n"
            f"평가손익: {p.get('pnl', 0):,.0f}\n"
            f"보유 종목: {p.get('positions', 0)}종목"
        )

    def _positions(self) -> str:
        rows = self.provider.positions()
        if not rows:
            return "보유 종목이 없습니다."
        lines = ["📦 보유 종목"]
        for r in rows:
            avg = r.get("avg_price")
            avg_s = f"{avg:,.0f}" if isinstance(avg, (int, float)) else "-"
            lines.append(f"- {r.get('symbol')} {r.get('quantity')}주 @ {avg_s}")
        return "\n".join(lines)

    def _conditions(self) -> str:
        rows = self.provider.conditions()
        if not rows:
            return "활성 거래 조건이 없습니다."
        lines = ["📋 활성 거래 조건"]
        for r in rows:
            symbol = r.get("symbol", "?")
            side = r.get("side", "?")
            target = r.get("target_price")
            target_s = f"{target:,.0f}" if isinstance(target, (int, float)) else "-"
            qty = r.get("quantity", "-")
            status = r.get("status", "-")
            lines.append(f"- {symbol} {side} {qty}주 @ {target_s} [{status}]")
        return "\n".join(lines)

    def _engine(self) -> str:
        results = self.provider.run_engine()
        if not results:
            return "엔진 실행 결과: 트리거된 조건 없음"
        lines = ["⚙️ 엔진 실행 결과"] + [f"- {r}" for r in results]
        return "\n".join(lines)

    def _propose(self, args: list[str]) -> str:
        if not args:
            return "사용법: /propose <심볼> [BUY|SELL]\n예: /propose 005930 BUY"
        symbol = args[0].upper()
        side = args[1].upper() if len(args) > 1 else "BUY"
        if side not in ("BUY", "SELL"):
            return f"방향 오류: '{side}' — BUY 또는 SELL 을 입력하세요."
        return self.provider.propose(symbol, side)


class BackendProvider:
    "`app.ui.backend` 를 감싼 라이브 provider. backend 는 KIS_ENV 로 mock/실 브로커 결정."

    def status(self) -> dict:
        from app.ui import backend

        wl = backend.list_whitelist()
        logs = backend.list_order_logs()
        return {
            "env": backend.env(),
            "auto_enabled": backend.get_flag("auto_trading_enabled"),
            "kill_switch": backend.get_flag("kill_switch_active"),
            "whitelist_count": 0 if wl is None or wl.empty else len(wl),
            "order_log_count": 0 if logs is None or logs.empty else len(logs),
        }

    def pnl(self) -> dict:
        from app.ui import backend

        df = backend.holdings_df()
        if df is None or df.empty:
            return {"market_value": 0.0, "pnl": 0.0, "positions": 0}
        return {
            "market_value": float(df["평가금액"].sum()),
            "pnl": float(df["평가손익"].sum()),
            "positions": int(len(df)),
        }

    def positions(self) -> list[dict]:
        from app.ui import backend

        df = backend.positions()
        if df is None or df.empty:
            return []
        return df.to_dict("records")

    def conditions(self) -> list[dict]:
        from app.ui import backend

        df = backend.list_conditions()
        if df is None or df.empty:
            return []
        # active only
        if "status" in df.columns:
            df = df[df["status"] == "ACTIVE"]
        return df.to_dict("records")

    def run_engine(self) -> list[str]:
        from app.ui import backend

        return backend.run_engine_once()

    def propose(self, symbol: str, side: str) -> str:
        from app.ui import backend

        proposal = backend.propose(symbol, side)
        target = proposal.target_price
        target_s = f"{target:,.0f}" if isinstance(target, (int, float)) else str(target)
        return (
            f"💡 IC 제안 [{proposal.symbol} {proposal.side}]\n"
            f"목표가: {target_s}\n"
            f"수량: {proposal.quantity}\n"
            f"근거: {proposal.rationale}"
        )


def make_telegram_sender(bot_token: str) -> Callable[[object, str], None]:
    """운영용 send_fn — 명령을 보낸 chat 으로 직접 회신."""
    import requests

    base = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def _send(chat_id, text: str) -> None:
        requests.post(base, json={"chat_id": chat_id, "text": text}, timeout=10)

    return _send


def poll_loop(bot: TelegramCommandBot, bot_token: str, *, long_poll_sec: int = 30) -> None:
    """getUpdates 롱폴링 루프 (운영용 — 테스트에서 호출하지 않음)."""
    import requests

    base = f"https://api.telegram.org/bot{bot_token}"
    offset: int | None = None
    logger.info("telegram poll_loop 시작")
    while True:
        try:
            resp = requests.get(
                f"{base}/getUpdates",
                params={"timeout": long_poll_sec, "offset": offset},
                timeout=long_poll_sec + 10,
            )
            for upd in resp.json().get("result", []):
                offset = upd["update_id"] + 1
                bot.handle_update(upd)
        except Exception as exc:  # noqa: BLE001 — 일시 오류로 루프가 죽지 않게
            logger.error("telegram poll 오류: %s", exc)
