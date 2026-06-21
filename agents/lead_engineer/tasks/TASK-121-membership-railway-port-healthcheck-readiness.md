---
type: task
id: TASK-121
display_id: TASK-121
task_uid: c05e8ab3-e86d-4577-aec5-2117dac3e04b
registered_at: 2026-06-19T21:17:00+09:00
created_at: 2026-06-19T21:17:00+09:00
updated_at: 2026-06-19T21:33:20+09:00
started_at: 2026-06-19T21:30:36+09:00
completed_at: 2026-06-19T21:33:20+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, CI/CD Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 1
est_tokens: 16000
tags: [membership, deploy, railway, healthcheck, preflight]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION
gate: local backend start/healthcheck readiness only; no Railway deploy or env write
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-032
created: 2026-06-19
---

# TASK-121 Membership Railway port and healthcheck readiness

작업 ID: TASK-121
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T21:17:00+09:00
기록 시각: 2026-06-19T21:17:00+09:00
요청자: Owner goal continuation
수행자: Backend Engineer + CI/CD Engineer + QA perspective (Codex)
검토자: Backend Engineer self-review + CI/CD handoff review + QA gate perspective; 협업 waiver(사유): single-session local Docker/start readiness scope; no Railway deploy, external env write, public URL, Supabase apply, secret, KIS/payment/provider, order/risk boundary crossed.
routing_ref: TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION / TASK-121
의도: TASK-119에서 기록한 Railway `$PORT`/`/api/health` blocker를 local readiness evidence로 줄인다.
대상: backend container/start behavior and healthcheck documentation or reversible patch.
방법: local review/patch/test only. No deploy and no external Railway setting mutation.
감사 로그: AUDIT-2026-06-19-032
완료 시각: 2026-06-19T21:33:20+09:00
실측 비용 (시간): 약 0.15h
실측 비용 (LLM 토큰): unknown

## 완료 조건

- [x] Backend start path can honor platform-provided `PORT` or has an explicit documented blocker.
- [x] `/api/health` smoke path is documented for staging readiness.
- [x] No Railway project, variable, domain, or deployment is changed.

## 완료 내용

- Root `Dockerfile` CMD를 shell expansion 기반으로 바꿔 `uvicorn ... --port ${PORT:-8000}`를 사용하게 했다.
- `/api/health` healthcheck readiness를 `MEMBERSHIP-RAILWAY-BACKEND-READINESS.json`/`.md`에 기록했다.
- `scripts/membership_railway_backend_readiness_gate.py`와 focused tests를 추가해 `0.0.0.0`, `${PORT:-8000}`, `/api/health`, not-deployed boundary를 검증한다.
- TASK-119 preflight checklist/gate를 Railway fixed-port blocker에서 Railway local readiness done but external deploy blocked 상태로 갱신했다.

## 완료 기록

완료일: 2026-06-19
결과: TASK-121 Railway backend local readiness가 완료됐다. Actual Railway deploy, env var write, public URL/domain publication은 여전히 Owner/R3이다.
변경 파일: `Dockerfile`, `agents/project/MEMBERSHIP-RAILWAY-BACKEND-READINESS.json`, `agents/project/MEMBERSHIP-RAILWAY-BACKEND-READINESS.md`, `scripts/membership_railway_backend_readiness_gate.py`, `tests/unit/test_membership_railway_backend_readiness_gate.py`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.md`, `scripts/membership_staging_deploy_preflight_gate.py`, `tests/unit/test_membership_staging_deploy_preflight_gate.py`.
이슈: Local container readiness improved, but no Docker image build, Railway deploy, or external platform config was executed.
다음 담당자 인수 사항: TASK-122 persistent storage decision packet is the next no-Owner R2 remediation item.

## 증거

- `Dockerfile`
- `agents/project/MEMBERSHIP-RAILWAY-BACKEND-READINESS.json`
- `agents/project/MEMBERSHIP-RAILWAY-BACKEND-READINESS.md`
- `scripts/membership_railway_backend_readiness_gate.py`
- `tests/unit/test_membership_railway_backend_readiness_gate.py`

## 검증

- `python -m json.tool agents\project\MEMBERSHIP-RAILWAY-BACKEND-READINESS.json`
- `python scripts\membership_railway_backend_readiness_gate.py --check`
- `python scripts\membership_staging_deploy_preflight_gate.py --check`
- `python -m pytest tests\unit\test_membership_railway_backend_readiness_gate.py tests\unit\test_membership_staging_deploy_preflight_gate.py -q`

## 리뷰

- Backend Engineer self-review: Dockerfile now honors a platform-provided `PORT` while retaining local fallback `8000`.
- CI/CD perspective: The readiness artifact remains local evidence only and does not perform Railway configuration or deploy.
- QA perspective: The gate rejects fixed-port regression and missing health route evidence.

## Independent Audit

판정: 통과
- Same-session audit note: Only local Dockerfile start readiness, docs, gate, and tests changed.
- No Railway project/env/domain/deploy, public URL, Supabase apply, secret, KIS/payment/provider, production DB, order, or risk boundary changed.
