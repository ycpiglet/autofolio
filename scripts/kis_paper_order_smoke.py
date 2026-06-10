#!/usr/bin/env python3
"""KIS **모의(paper) 전용** 주문 생애주기 스모크 — place → status → cancel → status. [감독형]

목적: `KisClient` 의 쓰기 경로(주문/취소/체결조회)를 **모의투자 서버**에서 실제로 검증한다.
체결을 피하려고 **시장가 한참 아래 지정가 매수 1주**(미체결)를 넣고 바로 취소한다.

안전
----
- **paper(모의투자) 환경에서만 동작**한다. prod 면 즉시 중단(주문 미발주). 실전 1주 테스트는
  사람 승인 하에 별도 절차로(MVP_SPEC §10/오류표).
- 모의투자는 가상자금이라 실손실이 없다. 그래도 주문 행위이므로 사람이 직접 실행한다
  (에이전트 자동 발주 금지). Claude Code 세션에서는 `! python scripts/kis_paper_order_smoke.py`.

사용:
  python scripts/kis_paper_order_smoke.py                 # 005930, 시세*0.5 미체결가
  python scripts/kis_paper_order_smoke.py --symbol 069500
  python scripts/kis_paper_order_smoke.py --no-cancel     # 취소 생략(직접 확인용)

전제: `.env` 에 KIS_PAPER_APP_KEY/SECRET/ACCOUNT 입력. 정규장 시간(09:00~15:30)에 실행해야
주문이 접수된다(장 마감 후엔 거부될 수 있음 — 그 경우 에러 메시지로 확인).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.config.settings import resolve_settings  # noqa: E402
from app.brokers.base import OrderRequest  # noqa: E402
from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.common.enums import OrderType, Side  # noqa: E402
from app.common.errors import BrokerError  # noqa: E402


def _tick(price: float) -> int:
    """KRX 호가단위 (2023 기준)."""
    if price < 2_000:
        return 1
    if price < 5_000:
        return 5
    if price < 20_000:
        return 10
    if price < 50_000:
        return 50
    if price < 200_000:
        return 100
    if price < 500_000:
        return 500
    return 1_000


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KIS 모의(paper) 전용 주문 생애주기 스모크")
    ap.add_argument("--symbol", default="005930")
    ap.add_argument("--qty", type=int, default=1)
    ap.add_argument("--no-cancel", action="store_true", help="취소 생략")
    args = ap.parse_args(argv)

    settings = resolve_settings("paper")
    # 하드 가드: paper 외에는 절대 발주하지 않는다.
    if settings.kis_env != "paper":
        print(f"[중단] paper 전용 스크립트인데 해석된 env={settings.kis_env}. 주문 미발주.")
        return 2
    if "openapivts" not in settings.kis_base_url:
        print(f"[중단] paper base_url 이 아님: {settings.kis_base_url}. 주문 미발주.")
        return 2
    if not settings.kis_app_key or not settings.kis_account_no:
        print("[중단] KIS_PAPER_APP_KEY / KIS_PAPER_ACCOUNT_NO 미설정. 주문 미발주.")
        return 2

    print(f"[paper] base={settings.kis_base_url} account={settings.kis_account_no}-{settings.kis_account_product_code}")
    client = KisClient(settings)

    cur = client.get_current_price(args.symbol).price
    # 상/하한가(±30%) 이내, 미체결 의도. 모의서버 내부 기준가와 차이를 줄이기 위해 95% 사용
    raw = cur * 0.95
    tick = _tick(raw)
    target = int(raw // tick * tick)  # 호가단위 정합
    print(f"현재가 {args.symbol} = {cur:,.0f} → 지정가 매수 {args.qty}주 @ {target:,} (미체결 예상, 호가단위 {tick:,.0f}원)")
    time.sleep(0.7)

    try:
        placed = client.place_order(
            OrderRequest(symbol=args.symbol, side=Side.BUY, order_type=OrderType.LIMIT,
                         quantity=args.qty, price=float(target))
        )
    except BrokerError as exc:
        print(f"[거부] 주문 접수 실패(장 마감/예수금/권한 등): {exc}")
        return 1

    print(f"PLACE  -> {placed.status.value} | odno={placed.broker_order_id} | {placed.message}")
    odno = placed.broker_order_id
    time.sleep(0.8)

    status = client.get_order_status(odno)
    print(f"STATUS -> {status.status.value} | 체결 {status.filled_quantity} | {status.message}")

    if args.no_cancel:
        print("(--no-cancel) 취소 생략. 모의 계좌에 미체결 주문이 남아있을 수 있음 — 직접 취소 권장.")
        return 0

    time.sleep(0.8)
    cancel = client.cancel_order(odno)
    print(f"CANCEL -> {cancel.status.value} | {cancel.message}")
    time.sleep(0.8)
    status2 = client.get_order_status(odno)
    print(f"STATUS -> {status2.status.value} | {status2.message}")

    ok = cancel.status.value == "CANCELED"
    print("\n결과:", "OK (주문→조회→취소 생애주기 검증 완료)" if ok else "확인 필요 — 위 메시지 점검")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
