---
type: task
id: TASK-072
display_id: TASK-072
task_uid: 623ec89c-153a-449b-87b6-b164ab04656d
registered_at: 2026-06-16T22:36:08+09:00
created_at: 2026-06-16T22:36:08+09:00
started_at: 2026-06-16T22:36:08+09:00
updated_at: 2026-06-16T22:38:52+09:00
completed_at: 2026-06-16T22:38:52+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, UI/UX Designer, QA]
priority: Medium
difficulty: 낮
est_hours: 1
est_tokens: 12000
tags: [authentication, sso, mock, dev-mode, ui-overhaul]
gate: dev-only mock SSO; default off; no secrets; no external provider calls; no live orders or risk changes
trigger_meeting: Owner direct request 2026-06-16
audit_log: AUDIT-2026-06-16-003
created: 2026-06-16
---

# TASK-072 Dev mock SSO provider

작업 ID: TASK-072
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-16T22:36:08+09:00
기록 시각: 2026-06-16T22:38:52+09:00
요청자: Owner
수행자: Lead Engineer, Backend Engineer, UI/UX Designer, QA
의도: 실제 Google/Kakao/Naver 개발자 콘솔과 secret이 준비되기 전에도 SSO/SNS 로그인 UI와 callback 세션 발급 흐름을 로컬에서 검증할 수 있게 dev-only mock provider를 추가한다.
대상: `app/services/sso.py`, SSO API tests, Next login E2E, external app/API owner manual
방법: env-gated mock provider registry, internal callback redirect, mock profile exchange, focused API/E2E validation
감사 로그: AUDIT-2026-06-16-003

## 배경

TASK-070에서 Google/Kakao/Naver provider-env 기반 SSO/SNS 로그인 surface는 구현됐다.
다만 실제 provider app, redirect URI, client secret이 Owner-managed 외부 준비물이라, 설정 전에는 end-to-end 로그인 UX를 닫아볼 수 없었다.

Owner 요청:

- SSO/SNS도 일단 목업으로 구현해 둔다.
- 필요한 정보만 넣으면 동작하게 한다.

## 범위

- 포함:
  - `AUTOFOLIO_SSO_MOCK_ENABLED=1`일 때만 활성화되는 `mock` SSO provider.
  - `/api/auth/sso/mock/login` -> 내부 callback redirect.
  - callback의 signed state cookie 검증과 owner session 발급.
  - mock email/name/subject env override.
  - allowed-email gate 적용.
  - 로그인 UI provider 버튼 회귀 테스트.
  - owner manual의 local/dev mock SSO 설정 안내.
- 제외:
  - 실제 Google/Kakao/Naver OAuth console 생성 또는 secret 입력.
  - provider token endpoint live call.
  - prod 로그인 정책 변경.
  - 주문, 리스크, DB schema, CI workflow 변경.

## 완료 기준

- mock provider는 기본 OFF이며 provider list에는 `enabled: false`로만 노출된다.
- `AUTOFOLIO_SSO_MOCK_ENABLED=1` 설정 시 로그인 화면에 `Mock SSO로 계속하기` 버튼이 표시된다.
- mock login은 외부 provider가 아니라 `/api/auth/sso/mock/callback`으로 redirect한다.
- callback은 정상 state/code일 때 owner session을 발급하고 `/home`으로 보낸다.
- allowlist email이 설정된 경우 mock email도 동일하게 차단/허용된다.
- focused API tests, Playwright login test, lint가 green이다.

## 사용 방법

로컬 `.env`에 아래 값을 넣고 backend/frontend를 재시작한다.

```text
AUTOFOLIO_SSO_MOCK_ENABLED=1
AUTOFOLIO_SSO_MOCK_EMAIL=owner@example.com
AUTOFOLIO_SSO_MOCK_NAME=Owner
AUTOFOLIO_SSO_ALLOWED_EMAILS=owner@example.com
```

선택 값:

```text
AUTOFOLIO_SSO_MOCK_SUBJECT=mock-owner
AUTOFOLIO_SSO_MOCK_CODE=mock
AUTOFOLIO_SSO_MOCK_CLIENT_ID=mock-client
```

## 완료 기록

완료 시각: 2026-06-16T22:38:52+09:00
검토자: Backend Engineer perspective + UI/UX Designer perspective + QA automated gates
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): Codex session local meter unavailable
협업 waiver: single-session env scope. 실제 외부 subagent dispatch는 사용하지 않았고 Backend/UI/QA 관점과 자동 게이트 증거로 대체했다.
routing waiver: main-session scope. selected_model/policy_model telemetry는 Codex harness에서 노출되지 않아 focused tests/lint/playwright gate로 대체했다.

## 완료 내용

- `app/services/sso.py`:
  - `mock_sso_enabled()`, `_truthy_env()`, `_mock_authorization_code()` 추가.
  - `providers()`에 `mock` provider 추가. env가 꺼져 있으면 `enabled: false`.
  - `build_authorization_url()`에서 mock provider는 내부 callback URL을 생성.
  - `exchange_code_for_profile()`에서 mock provider는 외부 HTTP 없이 `mock_profile()` 반환.
  - mock code 검증과 env 기반 subject/email/name 적용.
- `tests/api/test_auth_sso.py`:
  - mock provider default-off, env-on, internal callback redirect, owner session issuance, allowlist, invalid code 테스트 추가.
- `web/e2e/login.spec.ts`:
  - enabled mock provider 버튼 표시 회귀 테스트 추가.
- `docs/EXTERNAL_APP_API_OWNER_MANUAL.md`:
  - Development Mock SSO 설정값과 주의사항 기록.

## 변경 파일

- `app/services/sso.py`
- `tests/api/test_auth_sso.py`
- `web/e2e/login.spec.ts`
- `docs/EXTERNAL_APP_API_OWNER_MANUAL.md`
- `agents/lead_engineer/tasks/TASK-072-dev-mock-sso-provider.md`

## 검증

- `.\\.venv\\Scripts\\python.exe -m pytest tests/api/test_auth_sso.py -q` -> 14 passed, 1 warning.
- `.\\.venv\\Scripts\\python.exe -m py_compile app/services/sso.py app/api/routers/auth.py` -> OK.
- `.\\.venv\\Scripts\\python.exe -m pytest tests/api/test_auth.py tests/api/test_auth_sso.py -q` -> 25 passed, 2 warnings.
- `npm run lint` (`web/`) -> pass.
- `npm run build` (`web/`) -> successful, 13 static routes.
- `npx playwright test web/e2e/login.spec.ts` (`web/`) -> 5 passed.
- `.\\.venv\\Scripts\\python.exe scripts/validate_task_schema.py` -> OK.
- `.\\.venv\\Scripts\\python.exe scripts/build_task_index.py --check` -> OK.
- `.\\.venv\\Scripts\\python.exe scripts/generate_views.py --check` -> OK.
- `.\\.venv\\Scripts\\python.exe scripts/check_agent_docs.py` -> OK, 0 errors / 121 pre-existing warnings.
- `.\\.venv\\Scripts\\python.exe scripts/owner_governance_gate.py --allow-empty-owner-docs` -> pass.
- `git diff --check` -> OK; CRLF normalization warnings only.

## 증거

- SSO/SNS API contract: `tests/api/test_auth_sso.py`.
- Login UI regression: `web/e2e/login.spec.ts`.
- Manual setup note: `docs/EXTERNAL_APP_API_OWNER_MANUAL.md §2.5`.

## 남은 이슈 / 한계

- Mock SSO는 local/dev 검증 수단이며 production SSO를 대체하지 않는다.
- 실제 Google/Kakao/Naver OAuth app, redirect URI, consent, token exchange는 Owner-managed external setup 후 별도 live callback 검증이 필요하다.
- mock email이 `AUTOFOLIO_SSO_ALLOWED_EMAILS`에 없으면 403으로 차단된다.

## 리뷰

- Backend review: mock path도 기존 signed state cookie와 allowed-email gate를 그대로 통과한다. 외부 HTTP/token endpoint를 호출하지 않는다.
- UI/UX review: 로그인 UI는 기존 provider list 기반이라 별도 죽은 버튼 없이 enabled provider만 표시한다.
- QA review: default-off, env-on, callback success/fail, UI button rendering 회귀가 자동화됐다.
- Self-review note: 같은 Codex 세션에서 구현과 기록을 수행했으므로 Independent Audit은 evidence-based same-session review로 제한한다.

## Independent Audit

판정: 통과

근거:

- 기본값이 OFF라 운영 로그인 표면을 확장하지 않는다.
- secret/token/key를 생성하거나 저장하지 않는다.
- public provider response에는 id/label/kind/enabled만 포함된다.
- callback은 기존 OAuth state cookie 검증을 재사용한다.
- 주문, risk, broker, DB schema, CI workflow를 변경하지 않았다.
