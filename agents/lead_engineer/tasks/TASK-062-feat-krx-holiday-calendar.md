---
type: task
id: TASK-062
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 6
est_tokens: 40000
tags: [feature, safety, trading-window, holidays]
gate: -
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-062 feat: KRX 휴장일 캘린더 (safety_checker.py)

작업 ID: TASK-062
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: SafetyChecker에 KRX 휴장일 캘린더 연동으로 공휴일 주문 시도 차단
대상: app/trading/safety_checker.py, app/trading/trading_window.py
방법: krx_holidays.py 정적 리스트 작성 + SafetyChecker/TradingWindow 연동 + 휴장일/평일 단위테스트
감사 로그: AUDIT-2026-06-14-001

## 배경

`SafetyChecker` 및 `TradingWindow`가 KRX 공휴일·휴장일 캘린더를 검사하지 않아 공휴일에도 주문 시도가 발생.

**증상**: KRX 공휴일에 엔진이 주문을 시도 → KIS API가 거부 → `consecutive_failure` 카운터 증가 → 서킷브레이커 오발동 위험.

**원인**: `SafetyChecker.check()`와 `TradingWindow.is_open()`이 날짜만 체크하고 KRX 휴장일 목록을 참조하지 않음.

## 수정 방향

1. KRX 휴장일 정적 리스트 작성 (연간 공식 휴장일):
   - `app/data/krx_holidays.py` 또는 `data/krx_holidays.json`
   - 2025, 2026년 KRX 공식 휴장일 포함
2. `SafetyChecker.check()`에 휴장일 여부 검사 추가
3. `TradingWindow.is_open()`에도 연동
4. 단위테스트: 휴장일 차단, 차단 사유 로그, 평일 정상 통과

## 완료 기준

- 휴장일 `SafetyChecker.check()` 차단
- 차단 사유 로그 기록
- 휴장일/평일 단위테스트 통과

## Done When

- 휴장일 SafetyChecker.check() 차단
- 차단 사유 로그
- 휴장일/평일 단위테스트

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T16:39:01+09:00
검토자: Backend Engineer / QA

## 증거

- `app/data/krx_holidays.py` 신규: `KRX_HOLIDAYS` frozenset 2025·2026 공식 휴장일 34개 + `is_krx_holiday(Union[date, str]) -> bool` 헬퍼.
- `app/risk/safety_checker.py`: `is_krx_holiday` 임포트 추가. `SafetyChecker.check()` 내 거래창 체크 직후 holiday deny 게이트 추가. `now.date()` (KST-aware datetime의 date)를 전달 — OS TZ 무관.
- `tests/unit/test_krx_holidays.py` 신규: 8개 테스트 (TDD — 모듈 작성 전 FAIL 확인).
- `tests/unit/test_safety_checker.py`: `test_krx_holiday_blocks_order`, `test_non_holiday_does_not_block` 추가 (monkeypatch `is_krx_holiday` → run-date 독립 결정론적).
- 실패 테스트 선행 증거:
  - Step 1: `ModuleNotFoundError: No module named 'app.data.krx_holidays'` (krx_holidays.py 작성 전)
  - Step 3: `AttributeError: ... has no attribute 'is_krx_holiday'` (safety_checker.py 수정 전)
- 오늘(2026-06-14) 휴장일 여부: False (현충일은 2026-06-06). 기존 테스트 영향 없음.
- 수정 후: 693 passed, 0 failed (전체), 17 passed (test_krx_holidays + test_safety_checker).
- `python scripts/check_agent_docs.py` → 0 error.

## 리뷰

- KST 날짜 처리: `SafetyChecker.check()`에 이미 `now_kst()` 기반 `now` 인자가 전달됨. `now.date()`는 KST 기준 calendar date → OS UTC 무관.
- monkeypatch 결정론적: `is_krx_holiday` 패치로 현재 날짜에 무관하게 테스트 동작.
- deny-only: 주문 기능 미추가. 기존 deny 패턴과 동일 스타일 (`SafetyResult(False, ...)`) 사용.

실측 비용 (시간): ~0.3h (subagent)
실측 비용 (LLM 토큰): ~42k (subagent)

## Independent Audit

판정: 통과 — TDD(실패 테스트 선행 2회), monkeypatch 결정론적, KST date 처리, deny-only 안전 게이트, 전체 693 passed, 0 doc error. 기존 테스트 영향 없음(오늘 비휴장일). 2025·2026 공식 휴장일 34개 포함.
