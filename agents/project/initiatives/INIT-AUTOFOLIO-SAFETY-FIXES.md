---
schema_version: agent-runtime-work-item/v1
work_id: INIT-AUTOFOLIO-SAFETY-FIXES
work_uid: 38fda8f5-d995-47ee-a7ae-683abcb3bee8
kind: initiative
status: planned
owner: Lead Engineer
created_at: 2026-06-14T02:16:15+09:00
updated_at: 2026-06-14T02:16:15+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-13-007
created_by: Lead Engineer
title: Autofolio 안전 버그 수정 — 일일한도·컴플라이언스·ACK 루프
summary: KST/UTC 불일치, compliance fail-open, trade ack 무한루프 3건 버그 수정 (Phase 3 전 필수)
tags: [bug, safety, compliance, utc, ui, phase3-blocker]
priority: P0
---

# INIT-AUTOFOLIO-SAFETY-FIXES — 안전 버그 수정 이니셔티브

## 목적

Autofolio 매매 엔진에서 발견된 안전-임계 버그 3건을 Phase 3 UI 대개편(TASK-047) 착수 전에
수정한다.

## 포함 작업

| ID | 설명 | 우선순위 |
|----|------|----------|
| TASK-050 | `today_order_amount()` UTC/KST 불일치 → 일일 주문한도 우회 | High |
| TASK-051 | `save_condition_with_gates()` compliance fail-open → 오류 시 통과 | High |
| TASK-052 | `trade.py` ack 체크박스 위젯 루프 → `needs_acknowledgement` 영구 루프 | Low |

## 완료 기준

- 3건 모두 pytest green
- `python scripts/check_agent_docs.py` 0 error
- `python scripts/work_schema_gate.py --items --check` findings=0

## v1 이행 노트 (파일럿)

이 이니셔티브는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 파일럿으로,
기존 `TASK-*.md` 한국어 상태 게이트와 v1 영어 상태 게이트를 공존시키는 방식을 확립한다.

- v1 레코드: `agents/project/initiatives/`, `agents/lead_engineer/tasks/units/TASK-NNN/`
- 기존 TASK stubs: `agents/lead_engineer/tasks/TASK-NNN.md` (한국어 상태 유지, v1 포인터 추가)

### 호스트 프로젝트 식별자

각 유닛의 `project_id: PROJECT-AUTOFOLIO`는 이 저장소의 호스트 프로젝트를 가리키는
자유 문자열 레이블이다. `task_unit_readiness_gate` 및 `work_schema_gate`는 이 값을
파일 참조로 검증하지 않으므로, 별도의 PROJECT-CONTEXT.yml 레코드 없이도 게이트를 통과한다.
호스트 프로젝트 컨텍스트 상세는 `agents/project/VISION.md` 및 `agents/project/ROADMAP.md`를
참조한다 — Autofolio = KIS 기반 개인 자산운용 OS.

### 유닛 스키마 vs v1 work-item 봉투

유닛 스펙(`units/TASK-NNN/UNIT-TASK-NNN-NNN.md`)은 readiness-gate 유닛 스키마
(`unit_id / task_id / task_set_id / project_id / ...`)를 사용하며, v1 work-item 봉투가 아니다.
따라서 유닛 파일에는 `work_uid` / `schema_version` 필드가 의도적으로 없으며,
`work_schema_gate --items`가 아닌 `task_unit_readiness_gate`로 검증한다.
