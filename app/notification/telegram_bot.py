"""Telegram 명령봇 — 읽기 전용 조회 + 상태 변경 명령. [Autofolio]

지원 명령(읽기 전용): `/help` `/status` `/pnl` `/positions`
`/conditions` `/engine` `/propose`
상태 변경 명령: `/kill` `/kill off` `/approve confirm` `/pause`

설계
----
- 명령 해석(`handle_text`)은 순수 함수 → 단위 테스트가 쉽다(네트워크 불필요).
- 데이터는 `PortfolioProvider`(상태/손익/포지션/조건/엔진/제안/상태변경)로 주입 → `BackendProvider` 는
  `app.ui.backend`(KIS_ENV 에 따라 mock/실 브로커)를 감싼다.
- 전송은 `send_fn(chat_id, text)` 주입 → 운영은 Telegram API, 테스트는 기록용 페이크.
- **보안**: allowlist(허용 chat_id)에 있는 대화에만 응답한다(기본 전체 거부).

상태 변경 안전 규칙
-------------------
- /kill — 킬스위치 활성화(확인 불필요, 안전 방향).
- /kill off — 킬스위치 해제("off" 키워드 필수).
- /approve confirm — 자동매매 활성화("confirm" 키워드 필수).
- /pause — 자동매매 비활성화(확인 불필요).
"""
from __future__ import annotations

from typing import Callable, Protocol

from app.common.logger import get_logger

logger = get_logger("autofolio.telegram_bot")

HELP_TEXT = (
    "🤖 Autofolio 봇\n"
    "/status — 운영 상태(환경·자동매매·킬스위치·화이트리스트)\n"
    "/pnl — 평가손익 요약\n"
    "/positions — 보유 종목\n"
    "/quote <심볼> — 현재가 조회 (예: /quote 005930)\n"
    "/alert <심볼> <가격> [above|below] — 가격 알림 설정\n"
    "/conditions — 활성 거래 조건 목록\n"
    "/engine — 엔진 1회 실행(읽기 전용)\n"
    "/propose <심볼> [BUY|SELL] — IC 조건 제안\n"
    "/ask <에이전트> <질문> — 에이전트에게 질문 (예: /ask cio 환율 전망)\n"
    "/mode <심볼> <L0..L4> — 종목 자율성 레벨 설정\n"
    "/kill — 킬스위치 즉시 활성화\n"
    "/kill off — 킬스위치 해제\n"
    "/approve confirm — 자동매매 활성화(confirm 필수)\n"
    "/pause — 자동매매 비활성화\n"
    "/retro — 최근 30일 회고 요약\n"
    "/help — 도움말"
)


class PortfolioProvider(Protocol):
    def status(self) -> dict: ...
    def pnl(self) -> dict: ...
    def positions(self) -> list[dict]: ...
    def conditions(self) -> list[dict]: ...
    def run_engine(self) -> list[str]: ...
    def propose(self, symbol: str, side: str) -> str: ...
    def set_auto_enabled(self, value: bool) -> None: ...
    def set_kill_switch(self, value: bool) -> None: ...
    def quote(self, symbol: str) -> float: ...
    def ask_agent(self, agent: str, question: str) -> str: ...
    def set_symbol_mode(self, symbol: str, mode: str) -> None: ...
    def add_alert(self, symbol: str, price: float, direction: str) -> int: ...


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
        if cmd == "/quote":
            return self._quote(args)
        if cmd == "/alert":
            return self._alert(args)
        if cmd == "/conditions":
            return self._conditions()
        if cmd == "/engine":
            return self._engine()
        if cmd == "/propose":
            return self._propose(args)
        if cmd == "/ask":
            return self._ask(args)
        if cmd == "/mode":
            return self._mode(args)
        if cmd == "/retro":
            return self._retro()
        if cmd == "/kill":
            return self._kill(args)
        if cmd == "/approve":
            return self._approve(args)
        if cmd == "/pause":
            return self._pause()
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

    # ----- read-only handlers -----
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

    def _quote(self, args: list[str]) -> str:
        if not args:
            return "사용법: /quote <심볼>\n예: /quote 005930"
        symbol = args[0].upper()
        try:
            price = self.provider.quote(symbol)
            return f"📈 {symbol} 현재가: {price:,.0f}원"
        except Exception as exc:  # noqa: BLE001
            return f"조회 실패: {exc}"

    def _alert(self, args: list[str]) -> str:
        """가격 알림 설정: /alert <심볼> <가격> [above|below]"""
        if len(args) < 2:
            return "사용법: /alert <심볼> <가격> [above|below]\n예: /alert 005930 70000 above"
        symbol = args[0].upper()
        try:
            target = float(args[1].replace(",", ""))
        except ValueError:
            return f"가격 형식 오류: '{args[1]}'"
        direction = (args[2].upper() if len(args) > 2 else "ABOVE")
        if direction not in ("ABOVE", "BELOW"):
            direction = "ABOVE"
        try:
            alert_id = self.provider.add_alert(symbol, target, direction)
            return f"🔔 알림 설정 완료 (id={alert_id})\n{symbol} {target:,.0f}원 {'이상' if direction=='ABOVE' else '이하'} 도달 시 알림"
        except Exception as exc:  # noqa: BLE001
            return f"알림 설정 실패: {exc}"

    def _ask(self, args: list[str]) -> str:
        if len(args) < 2:
            return "사용법: /ask <에이전트> <질문>\n예: /ask cio 반도체 ETF 전망"
        agent = args[0].lower()
        question = " ".join(args[1:])
        try:
            return self.provider.ask_agent(agent, question)
        except Exception as exc:  # noqa: BLE001
            return f"에이전트 오류: {exc}"

    def _mode(self, args: list[str]) -> str:
        if len(args) < 2:
            return "사용법: /mode <심볼> <L0..L4>\n예: /mode 005930 L2"
        symbol = args[0].upper()
        mode = args[1].upper()
        if mode not in ("L0", "L1", "L2", "L3", "L4"):
            return f"레벨 오류: '{mode}' — L0~L4 중 하나를 입력하세요."
        try:
            self.provider.set_symbol_mode(symbol, mode)
            return f"✅ {symbol} 자율성 레벨 → {mode}"
        except Exception as exc:  # noqa: BLE001
            return f"모드 설정 실패: {exc}"

    def _retro(self) -> str:
        """회고 요약 — run_retro.py를 dry-run으로 실행 후 Forward Actions만 발췌."""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
            from scripts.run_retro import run_retro
            result = run_retro(days=30, dry_run=True)
            forward = result.get("forward_actions", "(분석 없음)")
            return f"📋 회고 (최근 30일)\n\n{forward[:600]}"
        except Exception as exc:  # noqa: BLE001
            return f"회고 실행 실패: {exc}"

    # ----- state-changing handlers -----
    def _kill(self, args: list[str]) -> str:
        """킬스위치 활성화(/kill) 또는 해제(/kill off).

        /kill     — 확인 없이 즉시 활성화(안전 방향).
        /kill off — "off" 키워드 필수; 킬스위치 해제.
        """
        if args and args[0].lower() == "off":
            self.provider.set_kill_switch(False)
            logger.info("telegram: /kill off — 킬스위치 해제됨")
            return "✅ 킬스위치 해제됨. 자동매매가 재개될 수 있습니다."
        # 인자 없음 또는 다른 인자 → 즉시 활성화
        self.provider.set_kill_switch(True)
        logger.info("telegram: /kill — 킬스위치 활성화됨")
        return "🚨 킬스위치 활성화됨. 모든 자동 주문이 즉시 중단됩니다."

    def _approve(self, args: list[str]) -> str:
        """자동매매 활성화 — 반드시 '/approve confirm' 형식이어야 한다."""
        if not args or args[0].lower() != "confirm":
            return (
                "⚠️ 자동매매 활성화는 확인이 필요합니다.\n"
                "명령: /approve confirm"
            )
        self.provider.set_auto_enabled(True)
        logger.info("telegram: /approve confirm — 자동매매 활성화됨")
        return "✅ 자동매매 활성화됨."

    def _pause(self) -> str:
        """자동매매 비활성화 — 확인 불필요."""
        self.provider.set_auto_enabled(False)
        logger.info("telegram: /pause — 자동매매 비활성화됨")
        return "⏸️ 자동매매 비활성화됨."


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

    def set_auto_enabled(self, value: bool) -> None:
        from app.ui import backend

        backend.set_flag("auto_trading_enabled", value)

    def set_kill_switch(self, value: bool) -> None:
        from app.ui import backend
        backend.set_flag("kill_switch_active", value)

    def quote(self, symbol: str) -> float:
        from app.ui import backend
        return backend.price(symbol)

    def ask_agent(self, agent: str, question: str) -> str:
        from app.ui import agents_runtime as ar
        return ar.ask(agent, question)

    def set_symbol_mode(self, symbol: str, mode: str) -> None:
        from app.ui import backend
        backend.set_flag(f"symbol_mode_{symbol}", mode)

    def add_alert(self, symbol: str, price: float, direction: str) -> int:
        from app.ui import backend
        return backend.add_price_alert(symbol, price, direction)


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
