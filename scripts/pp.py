#!/usr/bin/env python3
"""짧은 prod 최소 스모크 래퍼 (터미널 줄바꿈 회피용 — 긴 플래그를 안에 넣음).

사용:
  python scripts/pp.py               # 읽기전용 플랜 (주문 안 나감)
  python scripts/pp.py EXECUTE-REAL  # 실계좌 최소 주문 (≤5주·≤5,000원, 매수→매도→지정가취소 자동청산)

당일 모의(paper) 증거 게이트는 우회한다(모의 모의투자 유니버스가 저가 화이트리스트 종목을
거래 못 해 PASS 생성 불가). prod 경로는 TASK-080에서 검증됐고 하드캡은 그대로 유지된다.
실주문은 'EXECUTE-REAL' 토큰을 명시할 때만 나간다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.kis_minimal_order_smoke import main  # noqa: E402

argv = ["--no-require-paper-evidence", "--request-timeout", "20"]
if len(sys.argv) > 1 and sys.argv[1] == "EXECUTE-REAL":
    argv += ["--execute", "--i-understand-this-places-real-orders"]

raise SystemExit(main(argv, default_env="prod", locked_env=True))
