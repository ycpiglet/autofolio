---
type: task
id: TASK-057
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중-상
est_hours: 6
est_tokens: 40000
tags: [bug, backend, kpi, performance]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-057 fix: 일손익률/누적손익률 KPI 0.0 하드코딩 (backend.kpis)

작업 ID: TASK-057
상태: 대기
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: backend.kpis()의 일손익률/누적손익률 실계산 구현
대상: app/ui/backend.py kpis() 함수, app/database/repositories.py
방법: execution_logs 기반 일손익률/누적손익률 쿼리 헬퍼 추가 + kpis() 실계산 구현 + AppTest 검증
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/backend.py`의 `kpis()` 함수가 일손익률(`daily_return`)과 누적손익률(`total_return`)을 `0.0`으로 하드코딩.

**증상**: 홈 화면 KPI 카드의 일손익률과 누적손익률이 항상 0.00% 표시.

**원인**: 실제 SQLite `order_logs`/`execution_logs` 테이블에서 계산하는 로직이 구현되지 않고 placeholder `0.0` 반환.

## 수정 방향

1. **일손익률** (`daily_return`):
   - 당일 체결된 SELL 주문의 (체결가 - 평균매입가) × 수량 합산
   - 분모: 전일 종가 기준 보유 평가액

2. **누적손익률** (`total_return`):
   - 전체 기간 실현 손익 + 미실현 평가손익
   - 분모: 초기 투입 원금 (첫 매수 기준 또는 설정값)

3. `repositories.py`에 필요한 쿼리 헬퍼 추가

4. AppTest로 0이 아닌 실계산값 반환 검증

## 완료 기준

- 당일 체결 기준 일손익률 실계산
- 누적 기간 기준 누적손익률 실계산
- AppTest 통과
- `python -m pytest tests/ -q` green

## Done When

- 당일 체결 기준 일손익률 실계산
- 누적 기간 기준 누적손익률 실계산
- AppTest 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`
