---
type: task
id: TASK-099
display_id: TASK-099
task_uid: 1aba8b0a-6c56-444a-848b-9f9c8501691c
registered_at: 2026-06-19T13:29:14+09:00
created_at: 2026-06-19T13:29:14+09:00
started_at: 2026-06-19T13:29:14+09:00
updated_at: 2026-06-19T13:29:14+09:00
completed_at: 2026-06-19T13:29:14+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Lead Engineer, QA]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 16000
tags: [auth, membership, approval, safety, tests]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local auth fail-closed only; no production DB, deploy, payment, bank API, secret, KIS/order/risk/prod change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-009
created: 2026-06-19
---

# TASK-099 Membership local auto-register fail-closed

작업 ID: TASK-099
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T13:29:14+09:00
기록 시각: 2026-06-19T13:29:14+09:00
완료 시각: 2026-06-19T13:29:14+09:00
요청자: Owner
수행자: Backend Engineer + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + QA perspective
협업 waiver(사유): 단일 세션 local auth 범위 작업. 외부 worker dispatch 없이 focused tests와 governance gates로 검증.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-099
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible code lane; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.2h
실측 비용 (LLM 토큰): unknown
의도: 승인제 멤버십 모델과 충돌하던 로컬 ID/PW 자동가입을 기본 차단한다.
대상: `app/services/auth_service.py`, `app/api/routers/auth.py`, `app/ui/auth.py`, `web/src/app/login/page.tsx`, auth/account tests
방법: 기존 계정 로그인은 유지하고, 모르는 로컬 계정은 기본적으로 401로 차단한다. first-run/dev 자동가입은 `AUTOFOLIO_LOCAL_AUTO_REGISTER=1` 명시 opt-in일 때만 허용한다.
감사 로그: AUDIT-2026-06-19-009

## 범위

포함:

- unknown local username의 자동 owner session 생성을 기본 차단.
- 기존 로컬 계정 로그인은 계속 허용.
- local/dev first-run을 위한 `AUTOFOLIO_LOCAL_AUTO_REGISTER=1` opt-in 유지.
- API 401 detail과 로그인 화면 에러 표시를 승인제 문구로 연결.
- 서비스/API 회귀 테스트 추가.

제외:

- 회원가입 신청 API.
- 입금대기/승인 admin UI.
- DB schema/migration.
- production deploy.
- 실제 계좌번호, 입금기록, 고객 개인정보 저장.
- 외부 은행 API/OAuth/PG 연동.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] 알 수 없는 로컬 계정은 기본값에서 로그인/자동가입되지 않는다.
- [x] first-run/dev 자동가입은 명시 환경변수 opt-in으로만 가능하다.
- [x] 로그인 화면은 승인되지 않은 계정 오류를 비밀번호 오류와 구분해 표시한다.
- [x] 테스트가 기본 차단과 opt-in 동작을 고정한다.

## 완료 기록

완료일: 2026-06-19
결과: 로컬 자동가입이 fail-closed로 바뀌었고, 승인제 회원가입 모델의 첫 코드 충돌이 제거됐다.
변경 파일: `app/services/auth_service.py`, `app/api/routers/auth.py`, `app/ui/auth.py`, `app/services/__init__.py`, `web/src/app/login/page.tsx`, `tests/api/test_account.py`, `tests/api/test_auth.py`.
이슈: 실제 가입신청/입금대기/Owner 승인/활성화 상태 저장은 TASK-087 후속 구현 대상이다.
다음 담당자 인수 사항: TASK-087 구현 시 `register request -> verification_pending -> deposit_pending -> active` 상태 저장과 admin audit log를 별도 schema/admin flow로 설계해야 한다.

## 완료 내용

- `login_or_register()`가 알 수 없는 계정을 기본 차단한다.
- `AUTOFOLIO_LOCAL_AUTO_REGISTER=1`을 설정한 local/dev 상황에서만 신규 로컬 계정 생성이 가능하다.
- 로그인 페이지는 401 detail을 표시해 "승인된 계정이 아닙니다" 오류를 사용자에게 보여준다.
- 관련 docstring과 서비스 인덱스 설명을 승인제 모델에 맞췄다.

## 결과

TASK-099 완료. TASK-087 전체는 여전히 대기/후속 구현이며, 이번 변경은 로컬 자동가입 차단만 수행했다.

## 증거

- `app/services/auth_service.py`
- `web/src/app/login/page.tsx`
- `tests/api/test_account.py`
- `tests/api/test_auth.py`

## 리뷰

- Backend Engineer self-review: 기존 계정 로그인 경로는 유지하고 unknown account 경로만 fail-closed로 좁혔다.
- QA perspective: 기본 차단, opt-in 생성, 기존 계정 로그인 유지, API detail 전파를 focused tests로 고정했다.
- Compliance perspective: 미승인 사용자가 owner session을 얻는 경로를 기본값에서 제거해 verified-person signup policy와 맞췄다.

## Independent Audit

판정: 통과

Same-session audit note: 승인제 멤버십의 로컬 인증 충돌만 해결했다. DB schema, production deploy, payment/bank integration, real account number, customer PII, KIS/order/risk/prod/secret 변경은 없다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_auth.py tests/api/test_account.py -q`
- `npm run lint`
- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/validate_task_schema.py`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/continuity_contract_gate.py --check`
- `python scripts/conversation_work_audit.py --check`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts/check_agent_docs.py`
- `git diff --check`
