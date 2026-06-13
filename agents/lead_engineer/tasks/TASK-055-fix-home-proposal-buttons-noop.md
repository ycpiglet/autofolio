---
type: task
id: TASK-055
status: 대기
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 20000
tags: [bug, ui, home, ic, proposals]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-055 fix: 홈 화면 제안 승인/거부 버튼 no-op (home.py)

작업 ID: TASK-055
상태: 대기
Owner: UI/UX Designer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: UI/UX Designer
의도: home.py IC 제안 승인/거부 버튼에 실제 핸들러 구현
대상: app/ui/home.py, app/database/repositories.py (또는 store)
방법: approve/reject_proposal 핸들러 구현 + DB 상태 저장 + 홈 재렌더 시 반영 확인 + pytest 검증
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/home.py`의 IC 제안 카드에서 "승인" 및 "거부" 버튼에 `on_click` 핸들러가 없어 클릭해도 아무 동작이 없음.

**증상**: 투자위원회(IC) 제안을 승인하거나 거부해도 상태가 변경되지 않으며, 페이지 새로고침 후에도 동일한 제안이 그대로 표시됨.

**원인**: 버튼 렌더링 코드는 있지만 클릭 이벤트를 처리하는 핸들러 함수가 미구현.

## 수정 방향

1. `approve_proposal(proposal_id)` 핸들러 구현 → DB/store에 `accepted` 상태로 저장
2. `reject_proposal(proposal_id)` 핸들러 구현 → DB/store에 `rejected` 상태로 저장
3. 상태 변경 후 홈 화면 재렌더 시 처리된 제안 필터링 또는 상태 표시

## 완료 기준

- 버튼 클릭 시 제안 상태 업데이트
- 홈 재렌더 시 상태 반영
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## Done When

- 버튼 클릭 시 제안 상태 업데이트
- 홈 재렌더 시 상태 반영
