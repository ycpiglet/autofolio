---
unit_id: UNIT-TASK-055-001
task_id: TASK-055
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "home.py IC 제안 카드 승인/거부 버튼 반환값이 무시됨 — 핸들러 미구현. 수정: _handle_approve()/_handle_reject() 추가, handled_proposals set으로 처리된 제안 필터링, 백엔드 모드에서 backend.add_condition() 호출."
inputs:
  - agents/lead_engineer/tasks/TASK-055-fix-home-proposal-buttons-noop.md
  - app/ui/views/home.py
  - tests/unit/test_home_proposals.py
target_files:
  - app/ui/views/home.py
  - tests/unit/test_home_proposals.py
scope: "app/ui/views/home.py 제안 버튼 핸들러 + 필터링만. 새 DB 테이블, 새 주문 경로 없음."
acceptance:
  - "승인 버튼 클릭 → st.success 메시지"
  - "거부 버튼 클릭 → st.info 메시지"
  - "처리된 제안은 재렌더 시 제거됨"
  - "백엔드 모드 승인 → backend.add_condition() 호출 확인 (assert)"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_home_proposals.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과, 버튼 동작 방식 보고."
stop_condition: "home.py 버튼 수정 후 즉시 중단. 다른 뷰나 DB 스키마로 확장 금지."
depends_on: []
---

# UNIT-TASK-055-001 — 홈 IC 제안 버튼 핸들러 구현

## Context

`app/ui/views/home.py`의 IC 제안 카드:
```python
b.button("승인", key=f"ap_{p['id']}", width="stretch")  # 반환값 무시
b.button("거부", key=f"rj_{p['id']}", width="stretch")  # 반환값 무시
```
클릭해도 아무 동작 없음 (완전 no-op).

## Target Files

- `app/ui/views/home.py`
- `tests/unit/test_home_proposals.py`

## Scope

In scope: `home.py` 제안 버튼 로직 + 필터링 + 신규 테스트.

Out of scope: 새 DB 테이블, 새 API 엔드포인트, 다른 뷰 수정.

## 완료 기록

완료 시각: 2026-06-14T13:55:00+09:00
검토자: UI/UX Designer / QA

## 증거

- `app/ui/views/home.py`: `_handle_approve()`, `_handle_reject()` 추가; 버튼 반환값 수집; `handled_proposals` set으로 필터링.
  - 승인: backend 모드 → `backend.add_condition()` 호출 (auto_enabled=False, created_by="HOME_IC"); demo 모드 → st.success 피드백
  - 거부: `st.info` 피드백 + handled_proposals 등록
- `tests/unit/test_home_proposals.py`: 3개 AppTest 테스트 (all patch.object, no sys.modules swap, TZ-independent).
  - `test_approve_button_is_not_noop`: 승인 클릭 → st.success + add_condition 호출 횟수 assert.
  - `test_reject_button_is_not_noop`: 거부 클릭 → st.info 확인 (demo mode).
  - `test_handled_proposal_removed_from_pending`: handled_proposals에 P-101 사전 등록 → ap_P-101 버튼 미렌더 확인.
- 수정 전: 3 FAILED (no-op 증거).
- 수정 후: 666 passed (전체).

## 리뷰

- 데모 한계 명시: 데모 모드에서는 조건이 저장되지 않으며 st.success에 이를 명기.
- 백엔드 모드: 기존 `backend.add_condition()` 경로만 사용, 새 주문 경로 없음.
- 안전: `auto_enabled=False` — 자동주문은 매매 화면에서 별도 활성화.
- symbol 해상도: `proposal_row.get("티커") or proposal_row.get("종목", "")` — 티커 필드 없는 제안에서 display name 폴백.
