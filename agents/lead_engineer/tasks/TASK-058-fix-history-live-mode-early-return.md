---
type: task
id: TASK-058
status: 대기
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: High
difficulty: 낮
est_hours: 1
est_tokens: 10000
tags: [bug, ui, history, pnl]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-058 fix: history.py 라이브 모드 조기 return으로 PnL/배당 탭 미렌더

작업 ID: TASK-058
상태: 대기
Owner: UI/UX Designer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: UI/UX Designer
의도: history.py 라이브 모드 조기 return 제거로 전체 탭 렌더링
대상: app/ui/history.py ~line 41
방법: 라이브 모드 분기 끝 불필요 return 제거 + test_history_kis_view.py 라이브 3탭 렌더링 검증 추가
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/history.py` 약 41번째 줄에서 라이브 모드 주문 로그 표시 후 `return`이 있어 fills/PnL/dividend 탭이 라이브 모드에서 영원히 미렌더.

**증상**: 라이브 모드에서 내역 화면에 주문 로그만 표시되고 PnL 탭과 배당 탭이 렌더링되지 않음.

**원인**: 라이브 모드 분기 처리 블록 끝에 불필요한 `return` 문이 있어 이후 탭 렌더링 코드에 도달하지 못함.

## 수정 방향

1. `history.py` ~line 41의 `return` 제거
2. 라이브 모드에서도 fills/PnL/dividend 탭 전부 렌더링 확인
3. `test_history_kis_view.py`에 라이브 모드 3탭 렌더링 검증 추가

## 완료 기준

- 라이브 모드에서 주문 로그 + PnL + 배당 탭 모두 표시
- `test_history_kis_view.py` 통과
- `python -m pytest tests/ -q` green

## Done When

- 라이브 모드에서 주문 로그 + PnL + 배당 탭 모두 표시
- `test_history_kis_view.py` 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`
