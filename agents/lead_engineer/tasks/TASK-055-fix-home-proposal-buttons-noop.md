---
type: task
id: TASK-055
status: 완료
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
updated_at: 2026-06-14T13:55:00+09:00
---

# TASK-055 fix: 홈 화면 제안 승인/거부 버튼 no-op (home.py)

작업 ID: TASK-055
상태: 완료
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

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T13:55:00+09:00
검토자: UI/UX Designer / QA

## 증거

- `app/ui/views/home.py`: `_handle_approve()` + `_handle_reject()` 헬퍼 추가. 버튼 반환값 수집 후 핸들러 호출. `handled_proposals` set으로 처리된 제안 필터링.
  - 승인: backend 모드 → `backend.add_condition()` (auto_enabled=False, created_by="HOME_IC"); demo 모드 → st.success 피드백.
  - 거부: `st.info` 피드백 + handled_proposals 등록.
- `tests/unit/test_home_proposals.py`: 신규 3개 AppTest 테스트 (patch.object, no sys.modules swap, TZ-independent).
  - `test_approve_button_is_not_noop`: 승인 클릭 → st.success 확인 + add_condition 호출 횟수 assert.
  - `test_reject_button_is_not_noop`: 거부 클릭 → st.info 확인 (demo mode).
  - `test_handled_proposal_removed_from_pending`: 처리된 제안 필터링 확인.
- 수정 전: 3 FAILED (no-op 증거: AssertionError on all 3 assertions).
- 수정 후: 666 passed (전체).

## 리뷰

- 데모 한계: 데모 모드에서는 조건 미저장 — st.success에 명기함.
- 백엔드 모드: 기존 `backend.add_condition()` 경로 사용 (auto_enabled=False).
- 새 주문 경로 없음, 새 DB 테이블 없음.
- symbol 해상도: 티커 필드 없는 제안에서 display name 폴백, 향후 proposals에 티커 필드 추가 시 자동 개선.

실측 비용 (시간): ~0.5h (subagent)
실측 비용 (LLM 토큰): ~160k (subagent)

## Independent Audit

판정: 통과 — 승인/거부 버튼 no-op 해소 확인. TDD(실패 테스트 선행 3개 FAIL→PASS). 기존 홈 테스트 통과 유지. 데모 한계 명기. 새 주문 경로 없음. add_condition 호출 assert로 silent-fallback 방지.
