---
unit_id: UNIT-TASK-062-001
task_id: TASK-062
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "SafetyChecker.check()가 KRX 공휴일·휴장일 캘린더를 검사하지 않아 공휴일에 주문 시도 → consecutive_failure 카운터 증가 → 서킷브레이커 오발동 위험. app/data/krx_holidays.py 작성 + SafetyChecker.check()에 휴장일 거부 게이트 추가."
inputs:
  - agents/lead_engineer/tasks/TASK-062-feat-krx-holiday-calendar.md
  - app/risk/safety_checker.py
  - app/risk/trading_window.py
target_files:
  - app/data/krx_holidays.py
  - app/risk/safety_checker.py
  - tests/unit/test_krx_holidays.py
  - tests/unit/test_safety_checker.py
scope: "app/data/krx_holidays.py 신규 작성. app/risk/safety_checker.py에 is_krx_holiday 호출 추가 (deny-only). 다른 risk/engine 로직 변경 금지. 주문 기능 추가 금지."
acceptance:
  - "KRX 휴장일에 SafetyChecker.check() → allowed=False, reason 포함 '휴장' or 'holiday' or 'KRX'"
  - "평일(비휴장일)에 SafetyChecker.check() → holiday 사유로 차단하지 않음"
  - "is_krx_holiday(date(2026,1,1)) == True (신정)"
  - "is_krx_holiday(date(2026,6,10)) == False (평일)"
  - "python -m pytest tests/ -q 전체 그린"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_krx_holidays.py -v"
  - "python -m pytest tests/unit/test_safety_checker.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과 (unit + full), 오늘이 휴장일인지 여부 + 타 테스트 영향 분석, KST 처리 방식, 실패 테스트 선행 증거."
stop_condition: "is_krx_holiday 추가 후 즉시 중단. 거래창 로직, TradingWindow, 다른 risk 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-062-001 — KRX 휴장일 캘린더 SafetyChecker 연동

## Context

`SafetyChecker.check()`(`app/risk/safety_checker.py`)가 KRX 공휴일·휴장일을 검사하지 않아
공휴일에 주문 시도 → KIS API 거부 → `consecutive_failure` 카운터 증가 → 서킷브레이커 오발동 위험.

## Target Files

- `app/data/krx_holidays.py` (신규)
- `app/risk/safety_checker.py` (수정: import + holiday gate)
- `tests/unit/test_krx_holidays.py` (신규)
- `tests/unit/test_safety_checker.py` (수정: 2개 테스트 추가)

## Scope

In scope: `app/data/krx_holidays.py` 작성, `SafetyChecker.check()`에 deny-only 휴장일 게이트 추가.

Out of scope: `TradingWindow.is_open()` 수정, 주문 기능, UI 코드, 다른 risk 모듈.

## Steps

1. `tests/unit/test_krx_holidays.py` 작성 → FAIL 확인 (ModuleNotFoundError)
2. `app/data/krx_holidays.py` 작성 → 테스트 PASS 확인
3. `tests/unit/test_safety_checker.py`에 `test_krx_holiday_blocks_order`, `test_non_holiday_does_not_block` 추가 → FAIL 확인 (AttributeError: 'is_krx_holiday' not in module)
4. `app/risk/safety_checker.py`에 `is_krx_holiday` 임포트 + 게이트 추가 → 테스트 PASS 확인
5. 전체 suite (`tests/`) 그린 확인 (run-date 독립성 보장)

## Acceptance Criteria

- KRX 휴장일에 SafetyChecker.check() → allowed=False, reason 포함 '휴장' or 'holiday' or 'KRX'
- 평일에 holiday 사유로 차단 없음
- is_krx_holiday(date(2026,1,1)) True, is_krx_holiday(date(2026,6,10)) False
- `python -m pytest tests/ -q` 전체 그린
- `python scripts/check_agent_docs.py` 0 error

## Verification

```
python -m pytest tests/unit/test_krx_holidays.py -v
python -m pytest tests/unit/test_safety_checker.py -v
python -m pytest tests/ -q
python scripts/check_agent_docs.py
```

## Handoff

변경 파일 목록, pytest pass counts (unit + full), 오늘 휴장일 여부 + 타 테스트 영향,
KST 처리 방식, 실패 테스트 선행 증거, 커밋 SHA.

## Stop Boundary

`is_krx_holiday` 추가 후 즉시 중단. TradingWindow, 다른 risk 모듈로 확장 금지.

## 완료 기록

완료 시각: 2026-06-14T16:39:01+09:00

**변경 내용:**
- `app/data/krx_holidays.py` 신규: `KRX_HOLIDAYS` frozenset (2025·2026 공식 휴장일 34개) + `is_krx_holiday(Union[date, str]) -> bool`.
- `app/risk/safety_checker.py`: `from app.data.krx_holidays import is_krx_holiday` 임포트 추가. `SafetyChecker.check()` 내 거래창 체크 직후 `if is_krx_holiday(now.date())` 차단 게이트 추가.
- `tests/unit/test_krx_holidays.py` 신규: 8개 테스트 (데이터 검증 5, helper 함수 3).
- `tests/unit/test_safety_checker.py`: `test_krx_holiday_blocks_order`, `test_non_holiday_does_not_block` 추가 (monkeypatch로 날짜 고정).

**검증 결과:**
- 수정 전: `test_krx_holiday_blocks_order` → AttributeError (is_krx_holiday 미존재) FAILED
- 수정 후: 17 passed (test_krx_holidays + test_safety_checker), 693 passed (전체)
- `python scripts/check_agent_docs.py` → 0 error, 104 warning (기존 경고)
