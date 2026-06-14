---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-PLATFORM-EVAL
work_uid: 2a4278c1-3c1b-478b-8d2d-71892f48bbd9
kind: taskset
parent_id: INIT-PLATFORM-EVAL
status: active
owner: Performance Analyst
created_at: 2026-06-14T14:36:48+09:00
updated_at: 2026-06-14T14:36:48+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-14-002
created_by: performance_analyst
title: 플랫폼 평가 태스크셋 (TASK-068)
summary: agent_runtime 파일럿 측정 1건 — TASK-050/051/052를 baseline vs wave로 비교 측정
tags: [agent-runtime, eval, benchmark, pilot, dogfooding]
priority: P2
---

# TASKSET-PLATFORM-EVAL — agent_runtime 평가 파일럿 태스크셋

## 부모 이니셔티브

`INIT-PLATFORM-EVAL`

## 포함 태스크

tasks:
  - TASK-068

| work_id | 설명 | 파일/대상 |
|---------|------|-----------|
| TASK-068 | agent_runtime 평가 파일럿 — 순차 baseline vs 병렬 wave 측정 | TASK-050/051/052 + docs/AGENT_RUNTIME_EVAL_METRICS.md §3 |

## 의존 관계

TASK-068은 독립적으로 실행 가능하다. TASK-050·051·052는 이미 완료된 상태이므로 이력
데이터를 소급 분석하거나, 해당 태스크를 재현 실행하는 방식을 택할 수 있다.
실행 방법은 TASK-068 수행자가 파일럿 착수 시 결정한다.
