---
schema_version: agent-runtime-work-item/v1
work_id: INIT-PLATFORM-EVAL
work_uid: ed1c0223-c055-4d15-92f8-024c7ed26102
kind: initiative
status: active
owner: Performance Analyst
created_at: 2026-06-14T14:36:48+09:00
updated_at: 2026-06-14T14:36:48+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-14-002
created_by: performance_analyst
title: Platform Evaluation — agent_runtime Dogfooding and Quantitative Benchmarking
summary: agent_runtime 플랫폼 버전의 효과를 autofolio 실작업으로 정량 측정한다. 고정 지표(§1)로 종단 비교하고, 버전별 변동 지표(§2)로 새 기능을 검증한다. 측정 결과는 agent_runtime#128에 실사용 데이터로 공급한다.
tags: [agent-runtime, eval, benchmark, pilot, dogfooding]
priority: P2
---

# INIT-PLATFORM-EVAL — agent_runtime 플랫폼 평가·도그푸딩 이니셔티브

## 목적

agent_runtime 플랫폼의 각 버전이 autofolio 운영에 실제로 기여하는지를 정량적으로 검증한다.
`docs/AGENT_RUNTIME_EVAL_METRICS.md`에 정의된 고정(§1) + 변동(§2) 지표 틀을 따른다.

- **고정 지표(§1)**: `first_pass_rate`, `rework_count`, `gate_failure_count`, `reopened_count`, `wall_clock_per_task`, `tokens_per_task`, `merge_conflict_count`, `owner_interventions` — 버전에 무관하게 종단 비교에 사용
- **변동 지표(§2 v0.2.0)**: `wave_parallelism`, `footprint_violation`, `wave_defer_rate`, `pane_utilization`, `parallel_speedup` — 해당 버전의 새 기능 검증

관련 upstream 이슈: agent_runtime#128(self-eval 데이터 공급)·#125(footprint 게이트)·#121(관계).

## 포함 태스크

| ID | 설명 | 우선순위 |
|----|------|----------|
| TASK-068 | agent_runtime 평가 파일럿 — 순차 baseline vs 병렬 wave | Medium |

## 완료 기준

- TASK-068 완료 (파일럿 측정·비교·#128 코멘트)
- 고정 지표 §1 최초 기록 수립 (이후 버전 비교 기준선)
- `python scripts/check_agent_docs.py` 0 errors 유지
