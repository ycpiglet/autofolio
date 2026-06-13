---
type: task
id: TASK-062
status: 대기
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
상태: 대기
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
