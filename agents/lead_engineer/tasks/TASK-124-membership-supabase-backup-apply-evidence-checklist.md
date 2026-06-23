---
type: task
id: TASK-124
display_id: TASK-124
task_uid: 3ea9fe0e-923b-4f6d-bf97-3a89392ded69
registered_at: 2026-06-19T22:02:58+09:00
created_at: 2026-06-19T22:02:58+09:00
updated_at: 2026-06-19T22:06:04+09:00
started_at: 2026-06-19T22:02:58+09:00
completed_at: 2026-06-19T22:06:04+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Lead Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 1
est_tokens: 16000
tags: [membership, supabase, staging, backup, evidence]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE
gate: checklist only; no Supabase connection, migration/apply, backup download, or deploy
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-035
created: 2026-06-19
---

# TASK-124 Membership Supabase backup/apply evidence checklist

작업 ID: TASK-124
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T22:02:58+09:00
기록 시각: 2026-06-19T22:02:58+09:00
요청자: Owner goal continuation
수행자: Backend Engineer + Lead Engineer + QA perspective (Codex)
검토자: Backend Engineer self-review + Supabase evidence review + QA gate perspective; 협업 waiver(사유): single-session local checklist scope; no Supabase connection, migration/apply, backup download/restore, advisor execution, Data API grant change, external env write, deploy, public URL, secret, production data, KIS/payment/provider, order/risk boundary crossed.
routing_ref: TASKSET-MEMBERSHIP-SUPABASE-APPLY-EVIDENCE / TASK-124
의도: future Owner/R3 Supabase staging apply 전에 필요한 backup/restore/apply/advisor/cross-user evidence checklist를 고정한다.
대상: backup/restore review, migration apply evidence, advisor evidence, Data API grant evidence, cross-user evidence, rollback evidence.
방법: local checklist/gate/test only. No Supabase connection, migration/apply, backup download, or deploy.
감사 로그: AUDIT-2026-06-19-035
완료 시각: 2026-06-19T22:06:04+09:00
실측 비용 (시간): 약 0.1h
실측 비용 (LLM 토큰): unknown

## 완료 조건

- [x] Future apply evidence stages and required evidence IDs are listed.
- [x] Checklist keeps no-apply/no-backup/no-project-mutation boundary explicit.
- [x] Local gate and tests validate the checklist.

## 완료 내용

- `MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`/`.md`를 추가해 future Owner/R3 Supabase staging apply lane의 evidence stages를 고정했다.
- Pre-apply review, apply execution, post-apply security, post-apply isolation, deploy-smoke prerequisite stage별 required evidence IDs를 기록했다.
- `scripts/membership_supabase_apply_evidence_gate.py`와 focused tests를 추가해 not-applied 상태, no connection/apply/backup/advisor/grant/env boundary, required evidence coverage, stage assignment, forbidden backup/secret/apply key rejection을 검증한다.
- TASK-119 preflight checklist/gate에 apply evidence checklist gate를 launch gate와 required local check로 연결했다.

## 완료 기록

완료일: 2026-06-19
결과: TASK-124 Supabase backup/apply evidence checklist가 완료됐다. Actual Supabase project selection, backup/restore, migration creation/apply, advisors, Data API grant changes, live cross-user tests, deploy, and external users remain Owner/R3.
변경 파일: `agents/project/MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`, `agents/project/MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.md`, `scripts/membership_supabase_apply_evidence_gate.py`, `tests/unit/test_membership_supabase_apply_evidence_gate.py`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.md`, `scripts/membership_staging_deploy_preflight_gate.py`.
이슈: Evidence names are recorded, but no real evidence exists because no external Supabase apply lane ran.
다음 담당자 인수 사항: Remaining work is Owner/R3 actual Supabase staging project/migration/apply/deploy, or a new explicitly-scoped local R2 packet if one is identified.

## 증거

- `agents/project/MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`
- `agents/project/MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.md`
- `scripts/membership_supabase_apply_evidence_gate.py`
- `tests/unit/test_membership_supabase_apply_evidence_gate.py`

## 검증

- `python -m json.tool agents\project\MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`
- `python scripts\membership_supabase_apply_evidence_gate.py --check`
- `python -m pytest tests\unit\test_membership_supabase_apply_evidence_gate.py -q`
- `python scripts\membership_staging_deploy_preflight_gate.py --check`
- `python -m pytest tests\unit\test_membership_staging_deploy_preflight_gate.py -q`

## 리뷰

- Backend Engineer self-review: The checklist only names future evidence and does not make a project, migration, or apply claim.
- Supabase evidence review: Backup/restore, advisors, Data API grants, and cross-user tests stay post-apply Owner/R3 evidence.
- QA perspective: The gate rejects applied status, backup keys, missing required evidence, and stage assignment drift.

## Independent Audit

판정: 통과
- Same-session audit note: Only local checklist, docs, gate, tests, and preflight checklist state changed.
- No Supabase connection, project selection/mutation, migration/apply, backup download/restore, advisor execution, Data API grant change, external env write, deploy/public URL, secret, production data, KIS/payment/provider, order, or risk boundary changed.
