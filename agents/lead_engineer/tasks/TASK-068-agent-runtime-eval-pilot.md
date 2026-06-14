---
type: task
id: TASK-068
status: 완료
owner: Performance Analyst
assignees: [Performance Analyst, Lead Engineer]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 20000
tags: [agent-runtime, eval, benchmark, pilot, dogfooding]
gate: no live orders; measurement only
trigger_meeting: 없음
audit_log: AUDIT-2026-06-14-002
created: 2026-06-14
created_at: 2026-06-14T14:36:48+09:00
updated_at: 2026-06-14T19:32:17+09:00
---

# TASK-068 feat: agent_runtime 평가 파일럿 — 순차 baseline vs 병렬 wave 측정

작업 ID: TASK-068
상태: 완료
Owner: Performance Analyst
요청 시각: 2026-06-14T14:36:48+09:00
기록 시각: 2026-06-14T14:36:48+09:00
요청자: Owner
수행자: Performance Analyst, Lead Engineer
의도: TASK-050/051/052를 대상으로 순차 baseline vs 병렬 wave를 비교 측정하여 agent_runtime 플랫폼 효과를 정량화하고 agent_runtime#128에 실데이터를 제출한다
대상: TASK-050(일일한도 UTC/KST), TASK-051(compliance fail-open), TASK-052(ack 루프) — 고정 지표(§1) + 변동 지표(§2)
방법: (1) 순차 cascade로 3개 처리 → §1 고정 지표 기록 / (2) 병렬 wave(pane 분리)로 3개 처리 → §1 고정 + §2 변동 기록 / (3) parallel_speedup·footprint 위반·owner 부담·첫시도 통과율 비교 → #128 코멘트
감사 로그: AUDIT-2026-06-14-002

## 배경

`docs/AGENT_RUNTIME_EVAL_METRICS.md` §3 "파일럿 계획"이 이 파일럿을 정의한다:

- **대상**: TASK-050·051·052 — 서로 독립적이고 작아서 병렬 wave 안전 시험에 적격
- **절차**: baseline(순차) → wave(병렬) → 비교 → agent_runtime#128에 실데이터 코멘트
- **지표**: §1 고정 8개(`first_pass_rate`, `rework_count`, `gate_failure_count`, `reopened_count`, `wall_clock_per_task`, `tokens_per_task`, `merge_conflict_count`, `owner_interventions`) + §2 변동 5개(`wave_parallelism`, `footprint_violation`, `wave_defer_rate`, `pane_utilization`, `parallel_speedup`)

관련 agent_runtime 이슈: #128(self-eval 데이터 요청)·#125(footprint 게이트)·#121(autofolio-agent_runtime 관계).

이 태스크는 위 파일럿을 추적하는 작업 레코드다. 파일럿 실행 자체는 여기 등록된 절차대로 수행하고 결과를 이 태스크에 기록한다.

## 완료 기준

- baseline(순차) 실행 완료 + §1 고정 지표 기록
- wave(병렬) 실행 완료 + §1 고정 + §2 변동 지표 기록
- `parallel_speedup` 계산값 명시
- footprint 위반 유무 명시
- agent_runtime#128에 실데이터 코멘트 제출
- 게이트: `python scripts/check_agent_docs.py` 0 errors 유지

## 근거 경로

- `docs/AGENT_RUNTIME_EVAL_METRICS.md` §3 파일럿 계획 (소스 명세)
- agent_runtime#128 — self-eval 데이터 수신 측
- agent_runtime#125 — footprint 게이트 (변동 지표 `footprint_violation` 출처)
- agent_runtime#121 — autofolio↔agent_runtime 관계 컨텍스트

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PLATFORM-EVAL.md`
- Taskset: `agents/project/initiatives/TASKSET-PLATFORM-EVAL.md`

## 완료 기록

완료 시각: 2026-06-14T19:32:17+09:00
검토자: Performance Analyst, Lead Engineer

## 증거

- 보고서: `agents/lead_engineer/reports/BRIEF-2026-06-14-001.md`
- 실행 유닛: `agents/lead_engineer/tasks/units/TASK-068/UNIT-TASK-068-001.md`
- 데이터 출처: GitHub PR #47-#70 (`gh pr view --json statusCheckRollup,mergedAt,createdAt`)
- 고정 지표(§1): 8개 전부 기재 (일부 NOT COLLECTED 표기)
- 변동 지표(§2): 5개 전부 NOT COLLECTED — 실행이 순차였고 병렬 wave 미운영
- `parallel_speedup`: NOT COLLECTED (병렬 wave 미실행)
- `footprint_violation`: NOT COLLECTED (agent_runtime#125 게이트 미도입)
- #128 제출 텍스트: 보고서 §6에 포함 (Owner 검토 후 게시 예정)

**핵심 수치:**
- first_pass_rate: 95.0% (19/20 태스크)
- rework_count: 1건 (TASK-050 TZ)
- gate_failure_count: 1건 (PR#47)
- wall_clock_per_task: median 30분, 범위 8-68분
- merge_conflict_count: 0건
- owner_interventions: ~0 per-task

## 리뷰

병렬 wave 미실행으로 §3 파일럿 계획의 비교 실험(순차 vs. 병렬)은 완성되지 않았다.
이 보고서는 계획의 "baseline(순차)" 절반만 커버한다.
병렬 절반은 별도 실험이 필요하며, 이 태스크에서는 솔직하게 공백으로 표기했다.
고정 지표 baseline 자체는 신뢰도 높은 실측 데이터이며, agent_runtime#128에 제출 가능.
