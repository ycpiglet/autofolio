---
type: task
id: TASK-126
display_id: TASK-126
task_uid: cc4e0ea7-efd9-4221-889a-d0868d051af8
registered_at: 2026-06-19T22:10:53+09:00
created_at: 2026-06-19T22:10:53+09:00
updated_at: 2026-06-19T22:24:09+09:00
started_at: 2026-06-19T22:10:53+09:00
completed_at: 2026-06-19T22:24:09+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, QA]
priority: Medium
difficulty: 낮
est_hours: 1
est_tokens: 12000
tags: [membership, readiness, governance, owner-surface]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC
gate: local readiness API/docs/tests only; no Supabase apply, deploy, secret, payment, KIS, order, risk, or production data boundary
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-037
created: 2026-06-19
---

# TASK-126 Membership readiness surface sync

작업 ID: TASK-126
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-19T22:10:53+09:00
기록 시각: 2026-06-19T22:10:53+09:00
요청자: Owner goal continuation
수행자: Lead Engineer + Backend Engineer + QA perspective (Codex)
검토자: Lead Engineer self-review + QA focused API test; 협업 waiver(사유): single-session local readiness surface scope; no Supabase connection, migration/apply, deploy, external env write, secret, payment, KIS, order, risk, or production data boundary crossed.
routing_ref: TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC / TASK-126
의도: TASK-116~TASK-125에서 완료된 R2 증거물이 Owner-visible membership readiness API에 보이도록 정합화한다.
대상: `app/services/membership_readiness.py`, `tests/api/test_membership.py`, TASK/STATUS/AUDIT/BRIEF/taskset records.
방법: local API wording/artifact-presence checks/tests only. No external deploy, Supabase apply, secret, payment, KIS, order, risk, or production data changes.
감사 로그: AUDIT-2026-06-19-037
완료 시각: 2026-06-19T22:24:09+09:00
실측 비용 (시간): 약 0.1h
실측 비용 (LLM 토큰): unknown

## 완료 조건

- [x] Readiness API reports completed R2 pre-apply artifacts as pass items.
- [x] Actual R3 blockers remain block/watch and `can_launch=false`.
- [x] Focused tests validate the new readiness item split.

## 완료 내용

- `app/services/membership_readiness.py`에 artifact-presence helper를 추가해 `$schema`/`schema` JSON 산출물을 모두 읽을 수 있게 했다.
- TASK-116~TASK-125 산출물의 readiness pass 항목을 추가했다: Supabase field map, payment recognition decision, secret store plan, deploy preflight, env inventory, Railway readiness, persistent storage decision, migration/RLS review packet, apply evidence checklist, KIS terms review packet.
- 기존 R3 block 항목은 최신 증거를 참조하도록 설명을 갱신했지만, Supabase schema/RLS, production secret storage, payment recognition, per-user engine/safety, external deploy는 계속 block으로 유지했다.
- `tests/api/test_membership.py`가 새 pass 항목과 기존 R3 block 항목을 함께 검증하도록 확장했다.

## 완료 기록

완료일: 2026-06-19
결과: Owner-visible readiness surface가 완료된 R2 evidence와 실제 R3 blocker를 분리해서 보여준다. `can_launch=false`는 유지된다.
변경 파일: `app/services/membership_readiness.py`, `tests/api/test_membership.py`, `agents/project/initiatives/TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC.md`, `agents/lead_engineer/tasks/TASK-126-membership-readiness-surface-sync.md`, STATUS/AUDIT/BRIEF/generated views.
이슈: 기본 `python` 환경에는 FastAPI가 없어 focused API test가 실패했다. repo `.venv\Scripts\python.exe` 기준으로 재실행해 통과했다.
다음 담당자 인수 사항: 현재 확인된 no-Owner R2 후보는 없음. 남은 TASK-087 work는 Owner/R3 actual Supabase staging project/migration/apply/deploy, external env write, production secret/payment/KIS/provider handling, or separately approved local implementation slice가 필요하다.

## 증거

- `app/services/membership_readiness.py`
- `tests/api/test_membership.py`
- `agents/project/initiatives/TASKSET-MEMBERSHIP-READINESS-SURFACE-SYNC.md`

## 검증

- `python -m py_compile app\services\membership_readiness.py`
- `.venv\Scripts\python.exe -m py_compile app\services\membership_readiness.py`
- `.venv\Scripts\python.exe -m pytest tests\api\test_membership.py -q`

## 리뷰

- Lead Engineer self-review: The readiness surface now matches current task evidence and still refuses launch readiness for missing R3 evidence.
- Backend Engineer perspective: Artifact checks are local file-presence/schema/status checks only; they do not replace the existing focused gates and do not connect to external services.
- QA perspective: Focused membership API tests require both the new R2 pass IDs and the remaining R3 block IDs.

## Independent Audit

판정: 통과
- Same-session audit note: Only local readiness API code, focused test expectations, and governance records changed.
- No Supabase connection, project selection/mutation, migration/apply, backup download/restore, advisor execution, Data API grant change, external env write, deploy/public URL, secret, production data, KIS/payment/provider, order, or risk boundary changed.
