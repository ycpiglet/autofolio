---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-AUTOFOLIO-SAFETY-FIXES
work_uid: a331324f-e00d-5d15-9c68-b536d741b339
kind: taskset
parent_id: INIT-AUTOFOLIO-SAFETY-FIXES
status: planned
owner: Lead Engineer
created_at: 2026-06-14T02:16:15+09:00
updated_at: 2026-06-14T02:16:15+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-13-007
created_by: Lead Engineer
title: 안전 버그 수정 태스크셋 (TASK-050/051/052)
summary: 일일한도 UTC 버그, compliance fail-open, trade ack 루프 — 3건 독립 실행 가능
tags: [bug, safety, backend, ui]
priority: P0
---

# TASKSET-AUTOFOLIO-SAFETY-FIXES — 안전 버그 3건

## 부모 이니셔티브

`INIT-AUTOFOLIO-SAFETY-FIXES`

## 포함 태스크

| work_id | unit 스펙 | 파일 |
|---------|-----------|------|
| TASK-050 | `agents/lead_engineer/tasks/units/TASK-050/UNIT-TASK-050-001.md` | `app/database/repositories.py` |
| TASK-051 | `agents/lead_engineer/tasks/units/TASK-051/UNIT-TASK-051-001.md` | `app/services/trading.py` |
| TASK-052 | `agents/lead_engineer/tasks/units/TASK-052/UNIT-TASK-052-001.md` | `app/ui/views/trade.py` |

## 의존 관계

세 태스크는 서로 독립적이며 동시 실행 가능하다 (`depends_on: []`).

## Wave 실행 계획

Wave 1: TASK-050, TASK-051, TASK-052 (병렬)
