# Compound Log

> 반복 실수·비효율을 기록하고 프로세스에 반영한다(Plan→Work→Review→**Compound**, §17).
> 형식: `### COMPOUND-NNN` + 카테고리/재발 횟수/5 Whys/검증 방법 (TASK-146 §17 v2).

### COMPOUND-001

카테고리: 버그
재발 횟수: 1
날짜: 2026-06-11
상태: 완료

발견한 패턴: `datetime.now()`(timezone-naive)를 거래시간 판정·예약 타이머에 사용. Windows(KST) 개발환경에서는 정상이나 Linux/UTC 서버에서 9시간 오차 발생.

근본 원인: `trading_window.py`, `safety_checker.py`, `run_paper_engine.py`가 모두 `datetime.now()` 사용. KST 명시 없이 로컬 시각을 가정. Windows 개발 환경(로컬=KST)에서는 오류 미노출. Linux/UTC 배포 시 정규장 09:10-15:20 KST가 00:10-06:20 UTC로 인식 → 자동매매 전혀 미작동.

개선 조치: `trading_window.py`에 `now_kst()` 추가(`datetime.now(timezone(timedelta(hours=9)))`). `is_within_trading_window(now=None)` KST 기본값. `safety_checker.py`, `run_paper_engine.py` `datetime.now()` → `now_kst()` 교체. Bash 타이머 → `scripts/wait_and_market_test.py`(KST Python).

적용 대상: `app/risk/trading_window.py`, `app/risk/safety_checker.py`, `scripts/run_paper_engine.py`, `scripts/wait_and_market_test.py`

검증 방법:
- `pytest tests/unit/test_trading_window.py` → 3 passed
- `python -c "from app.risk.trading_window import is_within_trading_window; print(is_within_trading_window())"` Linux UTC 서버에서 KST 기준 정확 판정

규칙: 모든 거래시간 판정·예약 타이머는 `now_kst()` 사용. `datetime.now()` 직접 사용 금지.
