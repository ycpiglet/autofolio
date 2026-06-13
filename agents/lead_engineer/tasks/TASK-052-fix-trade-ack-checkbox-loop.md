---
type: task
id: TASK-052
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: Low
difficulty: 중
est_hours: 2
est_tokens: 15000
tags: [bug, ui, streamlit, trade, acknowledgement, checkbox]
gate: view-only fix; no backend change
trigger_meeting: 없음
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-14T04:30:06+09:00
---

# TASK-052 fix: trade 뷰 ack 체크박스 영구 루프

작업 ID: TASK-052
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: trade 뷰 ack 체크박스 위젯 클린업으로 인한 영구 루프 UX 버그 수정
대상: app/ui/views/trade.py lv_comply_ack 체크박스 렌더 로직
방법: lv_comply_ack를 st.session_state["trade_ack_checked"]로 분리하여 위젯 클린업 방지 및 재제출 시 ack 상태 정상 전달
감사 로그: AUDIT-2026-06-13-007

## 배경

Streamlit trade 화면에서 컴플라이언스 CAUTION 조건 저장 시 `needs_acknowledgement` 상태가 영구 루프에 빠지는 UX 버그.

## 버그 내용

`app/ui/views/trade.py`의 `lv_comply_ack` 체크박스가 버튼 블록(`st.form` 또는 조건부 블록) 안에서만 렌더된다. Streamlit은 재렌더 사이클에서 해당 블록이 사라지면 위젯을 클린업한다.

**증상**:
1. 조건 저장 → CAUTION → `needs_acknowledgement=True` → ack 체크박스 렌더
2. 체크박스 체크 → 버튼 블록 구조 변경 → Streamlit 위젯 클린업
3. 체크박스 상태 소실 → `caution_acknowledged=False` 유지
4. 재제출 → 다시 CAUTION → 무한 루프

**서비스 레이어**: `app/services/trading.py`의 `save_condition_with_gates()`는 이미 `caution_acknowledged` 파라미터를 지원하므로 **뷰 수정만 필요**.

## 수정 방향

`lv_comply_ack` 체크박스를 버튼 블록 밖(`st.session_state`)으로 꺼내거나, Streamlit `key=`를 안정화하여 위젯 클린업을 방지한다.

구체적으로:
- `st.session_state["trade_ack_checked"]` 변수로 ack 상태 관리
- 체크박스를 조건부 블록 밖에 독립 위젯으로 렌더
- 재제출 시 `caution_acknowledged=st.session_state.get("trade_ack_checked", False)` 전달

## 완료 기준

- `needs_acknowledgement=True` 상태에서 체크박스 체크 → 재제출 → 통과 (루프 없음)
- `python -m pytest tests/ -q` green (기존 trade 화면 테스트 유지)
- `python scripts/check_agent_docs.py` 0 error

## 근거 경로

- `app/ui/views/trade.py` — `lv_comply_ack` 체크박스 렌더 로직
- `app/services/trading.py` — `save_condition_with_gates(caution_acknowledged=...)` 서명

## Done When

- ack 체크박스 체크 → 재제출 → 루프 없이 정상 저장
- 기존 pytest green

## v1 이행 (파일럿)

이 태스크는 agent_runtime v0.2.0 work-item 스키마로 이행되었다.
실행 상세 명세는 v1 unit 스펙을 참고:

- Initiative: `agents/project/initiatives/INIT-AUTOFOLIO-SAFETY-FIXES.md`
- Taskset: `agents/project/initiatives/TASKSET-AUTOFOLIO-SAFETY-FIXES.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-052/UNIT-TASK-052-001.md`

## 완료 노트 (2026-06-14T04:30:06+09:00)

`lv_comply_ack` 체크박스를 버튼 블록 밖으로 분리하여 Streamlit 위젯 클린업 문제 해소.
`trade_ack_checked` 세션 키로 ack 상태 영속화. 617 pytest, 0 doc error.

## 완료 기록

완료 시각: 2026-06-14T04:39:57+09:00
검토자: UI/UX Designer + QA (Codex self-review)

## 증거

- `app/ui/views/trade.py`: `lv_comply_ack` 체크박스를 버튼 블록 밖으로 분리. 비위젯 세션키 `_trade_ack_pending_message`/`trade_ack_checked`/`_trade_ack_context`로 ack 상태를 rerun 간 영속화. needs_acknowledgement 시 메시지 저장 후 블록 밖 렌더, 저장 성공 시 키 클리어. fresh CAUTION 자동 승인 방지(context 변경 시 초기화).
- `tests/unit/test_trade_order_book_view.py`: ack 체크박스가 버튼 블록 밖에 렌더되는 구조 검증 + `trade_ack_checked` 세션키 지속 검증 2건 추가.
- 전체 pytest 617 passed, check_agent_docs 0 error.

## 리뷰

- 근본 원인(위젯키 클린업)을 비위젯 세션키 분리로 해소 — Streamlit 위젯 생명주기 정석 패턴.
- Fail-safe: ack 키 없으면 `caution_acknowledged=False` — 자동 승인 없음.
- 한계(정직): 완전 2단계 E2E(저장→CAUTION→체크→재저장)는 AppTest rerun 경계 mock 미생존으로 미구현. 구조+지속 메커니즘을 분리 검증.
- scope 준수: trade.py만 수정, 서비스 레이어 무변경.

## Independent Audit

판정: 통과 (구조 수정 + 세션키 지속 분리 검증, 전체 617 passed, 0 doc error).
