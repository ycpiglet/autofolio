---
type: task
id: TASK-028
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: High
difficulty: 상
est_hours: 4
est_tokens: 45000
tags: [ui, trade, safety, guardrail, streamlit]
trigger_meeting: 자가발생
audit_log: AUDIT-2026-06-11-006
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
---

# TASK-028 UI Trade Guarded Workflow

작업 ID: TASK-028
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-11T12:50:32+09:00
기록 시각: 2026-06-11T12:50:32+09:00

## 배경 및 목적

최근 paper 계좌의 의도치 않은 다종목 주문 사고 이후, Trade 화면은 주문 입력보다
환경·출처·guard checklist·확인 흐름을 먼저 보여줘야 한다. 사용자가 주문 가능 상태와
차단 사유를 오해하지 않도록 guard-first workflow로 재구성한다.

## 구현 범위

- `app/ui/views/trade.py` guard checklist 우선 배치
- 주문/조건 관련 action 전에 환경, 출처, mode, auto, kill, whitelist, budget, circuit breaker 상태 표시
- 주문 가능 action은 checklist 통과 시에만 노출 또는 활성화
- 기존 주문 실행 로직은 변경하지 않고 UI guard 표시 계약만 테스트로 고정

## 완료 기준

- [x] kill switch active 상태에서 실행 가능 UI가 표시되지 않음
- [x] 환경과 출처가 Trade 화면 상단에 명시
- [x] guard checklist가 색상만이 아니라 텍스트/사유로 표시
- [x] `pytest tests/unit/test_ui_trade_guard_workflow.py -v` 통과

## 계획 링크

- `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md` Task 4

## 리스크 및 경계

- 주문 실행 로직, KIS client, `app/risk/**` 정책은 변경하지 않는다. UI 표면만 변경한다.

## 완료 기록

### 2026-06-11T18:19:48+09:00

- `app/ui/views/trade.py`의 guard-first 헤더와 체크리스트 흐름을 완료 기준에 맞춰 확인했다.
- `backend.list_whitelist()`가 `DataFrame`을 반환하는 실제 UI 계약에서 Trade guard가 `UNKNOWN`으로 떨어지던 문제를 수정했다.
- `app/ui/backend.py`에 Trade guard 표시용 읽기 래퍼 `today_order_amount()`와 `get_global_risk_limit()`를 추가했다.
- `tests/unit/test_ui_trade_guard_workflow.py`를 추가해 paper 환경/출처/한도 표시와 kill-switch 차단 상태를 회귀 테스트로 고정했다.
- 검증: `pytest tests/unit/test_ui_trade_guard_workflow.py -v` 및 clean branch focused UI suite 통과.
