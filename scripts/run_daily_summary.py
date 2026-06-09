#!/usr/bin/env python3
"""Daily summary — 장 종료 후 오늘 활동 요약 생성.

오늘의 조건 점검 건수, 발행 주문, 체결, PnL 추정치를 텍스트로 생성하고
Telegram(설정된 경우)으로 발송한 뒤 .autofolio/daily/SUMMARY_YYYYMMDD.md 에 저장한다.

NOTE: 포지션/잔고는 DB 상태(execution_logs + order_logs)만 참조한다. 장 중 KIS API 호출 없음.

Usage
-----
    python scripts/run_daily_summary.py
    python scripts/run_daily_summary.py --dry-run
    python scripts/run_daily_summary.py --date 2026-06-10

설계 제약
----------
- 모든 숫자는 DB(order_logs, execution_logs)에서 읽는다.
- KIS API 직접 호출 없음 — DB state 만으로 동작.
- 15:30 이후(cron: 30 15 * * 1-5) 실행 권장. --dry-run 은 시간 제약 없음.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

# ── 프로젝트 루트를 sys.path 에 추가 ────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

from app.common.logger import get_logger  # noqa: E402
from app.config.settings import settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402
from app.database.sqlite_db import get_connection  # noqa: E402
from app.notification.notifier import make_notifier_from_env  # noqa: E402

logger = get_logger("autofolio.daily_summary")

SUMMARY_DIR = ROOT / ".autofolio" / "daily"

# ── 파싱 ────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="장 종료 후 일일 요약 생성 및 Telegram 발송 (KIS API 호출 없음)."
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="알림 발송 및 파일 저장을 건너뛰고 요약을 stdout 만 출력한다.",
    )
    ap.add_argument(
        "--date",
        default=None,
        help="집계 기준일 (YYYY-MM-DD). 기본값: 오늘.",
    )
    ap.add_argument(
        "--db",
        default=None,
        help="SQLite DB 경로 (기본: settings.db_path).",
    )
    return ap


# ── DB 조회 헬퍼 ─────────────────────────────────────────────────────────────

def _fetch_today_orders(db_path: Path, target_date: str) -> list[dict[str, Any]]:
    """오늘 생성된 order_logs 를 반환한다."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM order_logs
            WHERE DATE(created_at) = ?
            ORDER BY id
            """,
            (target_date,),
        ).fetchall()
    return [dict(r) for r in rows]


def _fetch_today_fills(db_path: Path, target_date: str) -> list[dict[str, Any]]:
    """오늘 체결된 execution_logs 를 반환한다 (order_logs 와 join)."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.symbol, e.filled_price, e.filled_quantity,
                   e.filled_at, o.side, o.order_price, o.condition_id
            FROM execution_logs e
            JOIN order_logs o ON o.id = e.order_log_id
            WHERE DATE(e.filled_at) = ?
            ORDER BY e.filled_at
            """,
            (target_date,),
        ).fetchall()
    return [dict(r) for r in rows]


def _fetch_active_conditions_count(db_path: Path) -> int:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM trade_conditions WHERE status = 'ACTIVE'"
        ).fetchone()
    return int(row["cnt"] or 0)


def _fetch_system_state(db_path: Path) -> dict[str, str]:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT key, value FROM system_state").fetchall()
    return {r["key"]: r["value"] for r in rows}


# ── PnL 추정 ─────────────────────────────────────────────────────────────────

def _estimate_pnl(fills: list[dict[str, Any]]) -> dict[str, float]:
    """체결 내역에서 단순 PnL 추정.

    BUY: 매수 비용 누계
    SELL: (체결가 - 주문가) * 수량 으로 단순 추정 (슬리피지 미반영)
    Returns: {realized_gross, buy_cost, sell_proceeds, net_est}
    """
    buy_cost = 0.0
    sell_proceeds = 0.0
    for f in fills:
        qty = f.get("filled_quantity") or 0
        price = f.get("filled_price") or 0.0
        if f.get("side", "").upper() == "BUY":
            buy_cost += price * qty
        else:
            sell_proceeds += price * qty
    net_est = sell_proceeds - buy_cost
    return {
        "buy_cost": buy_cost,
        "sell_proceeds": sell_proceeds,
        "net_est": net_est,
    }


# ── 요약 렌더링 ───────────────────────────────────────────────────────────────

def render_summary(
    *,
    target_date: str,
    generated_at: str,
    orders: list[dict[str, Any]],
    fills: list[dict[str, Any]],
    active_conditions: int,
    system_state: dict[str, str],
    pnl: dict[str, float],
    dry_run: bool,
) -> str:
    auto_enabled = system_state.get("auto_trading_enabled", "unknown")
    kill_switch = system_state.get("kill_switch_active", "unknown")
    kis_env = system_state.get("kis_env", settings.kis_env)

    order_count = len(orders)
    fill_count = len(fills)
    error_count = sum(1 for o in orders if o.get("order_status") == "ERROR")
    requested_count = sum(1 for o in orders if o.get("order_status") == "REQUESTED")
    filled_orders = sum(1 for o in orders if o.get("order_status") == "FILLED")

    lines = [
        f"# Autofolio 일일 요약 — {target_date}",
        "",
        f"> 생성: {generated_at}  |  KIS 환경: `{kis_env}`  |  dry_run: `{dry_run}`",
        "",
        "## 시스템 상태",
        f"- 자동매매 활성: `{auto_enabled}`",
        f"- 킬스위치 활성: `{kill_switch}`",
        f"- 활성 조건 수: {active_conditions}",
        "",
        "## 오늘 주문 현황",
        f"- 총 발행 주문: {order_count}건",
        f"  - FILLED: {filled_orders}",
        f"  - REQUESTED: {requested_count}",
        f"  - ERROR: {error_count}",
        "",
    ]

    if orders:
        lines.append("### 주문 내역")
        lines.append("| # | 종목 | 방향 | 수량 | 주문가 | 상태 | 시각 |")
        lines.append("|---|------|------|------|--------|------|------|")
        for o in orders:
            lines.append(
                f"| {o.get('id')} | {o.get('symbol')} | {o.get('side')} "
                f"| {o.get('quantity')} | {o.get('order_price') or '-'} "
                f"| {o.get('order_status')} | {o.get('created_at', '')[:16]} |"
            )
        lines.append("")

    lines += [
        "## 체결 현황",
        f"- 체결 건수: {fill_count}",
    ]

    if fills:
        lines.append("")
        lines.append("### 체결 내역")
        lines.append("| 종목 | 방향 | 체결량 | 체결가 | 체결시각 |")
        lines.append("|------|------|--------|--------|----------|")
        for f in fills:
            lines.append(
                f"| {f.get('symbol')} | {f.get('side')} "
                f"| {f.get('filled_quantity')} | {f.get('filled_price')} "
                f"| {str(f.get('filled_at', ''))[:16]} |"
            )
        lines.append("")

    lines += [
        "## PnL 추정 (단순, 슬리피지 미반영)",
        f"- 매수 비용 합계: {pnl['buy_cost']:,.0f}원",
        f"- 매도 수익 합계: {pnl['sell_proceeds']:,.0f}원",
        f"- 순 추정치:      {pnl['net_est']:+,.0f}원",
        "",
        "> **주의**: PnL 은 DB 기록 기반 추정치입니다. 실제 손익은 KIS 계좌에서 확인하세요.",
    ]

    return "\n".join(lines)


def _short_telegram_text(
    target_date: str,
    order_count: int,
    fill_count: int,
    pnl_net: float,
    dry_run: bool,
) -> str:
    prefix = "[DRY-RUN] " if dry_run else ""
    return (
        f"{prefix}Autofolio 일일 요약 {target_date}\n"
        f"주문 {order_count}건 / 체결 {fill_count}건\n"
        f"PnL 추정: {pnl_net:+,.0f}원"
    )


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main() -> int:
    args = _build_parser().parse_args()

    target_date: str = args.date or date.today().isoformat()
    generated_at: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    db_path: Path = Path(args.db) if args.db else settings.db_path

    logger.info("[daily_summary] 집계 기준일=%s, db=%s, dry_run=%s",
                target_date, db_path, args.dry_run)

    # ── DB 조회 ──────────────────────────────────────────────────────────────
    orders = _fetch_today_orders(db_path, target_date)
    fills = _fetch_today_fills(db_path, target_date)
    active_conditions = _fetch_active_conditions_count(db_path)
    system_state = _fetch_system_state(db_path)
    pnl = _estimate_pnl(fills)

    # ── 요약 렌더링 ───────────────────────────────────────────────────────────
    summary_md = render_summary(
        target_date=target_date,
        generated_at=generated_at,
        orders=orders,
        fills=fills,
        active_conditions=active_conditions,
        system_state=system_state,
        pnl=pnl,
        dry_run=args.dry_run,
    )

    print(summary_md)

    if args.dry_run:
        logger.info("[daily_summary] dry-run 완료 — 파일/알림 저장 건너뜀")
        return 0

    # ── 파일 저장 ─────────────────────────────────────────────────────────────
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    date_str = target_date.replace("-", "")
    out_path = SUMMARY_DIR / f"SUMMARY_{date_str}.md"
    out_path.write_text(summary_md, encoding="utf-8")
    logger.info("[daily_summary] 저장: %s", out_path)

    # ── Telegram 발송 ─────────────────────────────────────────────────────────
    notifier = make_notifier_from_env()
    tg_text = _short_telegram_text(
        target_date=target_date,
        order_count=len(orders),
        fill_count=len(fills),
        pnl_net=pnl["net_est"],
        dry_run=False,
    )
    notifier.send(tg_text)
    if notifier.enabled:
        logger.info("[daily_summary] Telegram 발송 완료")
    else:
        logger.info("[daily_summary] Telegram 미설정 — stdout 출력만")

    return 0


if __name__ == "__main__":
    sys.exit(main())
