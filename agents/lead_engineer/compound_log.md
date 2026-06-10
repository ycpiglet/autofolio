# Compound Log

> 반복 실수·비효율을 기록하고 프로세스에 반영한다(Plan→Work→Review→**Compound**, §17).
> 형식: `### COMPOUND-NNN` + 카테고리/재발 횟수/5 Whys/검증 방법 (TASK-146 §17 v2).

### COMPOUND-001

**카테고리:** 시간/타임존 버그  
**재발 횟수:** 1 (2026-06-11 첫 발견)

#### 문제
`datetime.now()`(timezone-naive)를 거래시간 판정에 사용.
Linux/UTC 서버에서 9시간 오차 → 정규장 09:10-15:20 KST가 00:10-06:20 UTC로 인식 → 자동매매 미작동.

#### 수정
- `trading_window.py`: `now_kst()` 추가, `is_within_trading_window(now=None)` KST 기본값
- `safety_checker.py`, `run_paper_engine.py`: `datetime.now()` → `now_kst()`
- Bash 타이머 → `scripts/wait_and_market_test.py` (KST Python, 서버 무관)

#### 규칙
> **모든 거래시간 판정·예약 타이머는 `now_kst()` 사용. `datetime.now()` 직접 사용 금지.**
