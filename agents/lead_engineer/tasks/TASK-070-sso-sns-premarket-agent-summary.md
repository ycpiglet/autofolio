---
type: task
id: TASK-070
display_id: TASK-070
task_uid: a9ce75b9-df26-4ec4-9ac2-637eae5870ee
registered_at: 2026-06-16T20:49:58+09:00
started_at: 2026-06-16T20:49:58+09:00
completed_at: 2026-06-16T21:05:31+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, UI/UX Designer, QA]
priority: High
difficulty: 중-상
est_hours: 5
est_tokens: 45000
tags: [authentication, sso, sns-login, agents, premarket, lint, ui-overhaul]
gate: no secrets; no live orders; CLI-generated reports only; external OAuth providers require Owner-managed credentials
trigger_meeting: Owner direct request 2026-06-16
audit_log: AUDIT-2026-06-16-001
created: 2026-06-16
created_at: 2026-06-16T20:49:58+09:00
updated_at: 2026-06-16T21:05:31+09:00
---

# TASK-070 SSO/SNS + 프리마켓 에이전트 요약 + lint gate

작업 ID: TASK-070
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-16T20:49:58+09:00
기록 시각: 2026-06-16T20:49:58+09:00
요청자: Owner
수행자: Lead Engineer, Backend Engineer, UI/UX Designer, QA
의도: Next/FastAPI UI에 SSO/SNS 로그인 표면을 추가하고, 에이전트 탭에서 리서치·금융 전문가 에이전트를 모두 표시하며, CLI 명시 실행으로 정규장 시작 전 핵심 요약 파일을 저장하고 UI에서 다시 띄운다.
대상: `app/api/routers/auth.py`, `app/services/agents.py`, `app/services/premarket_summary.py`, `scripts/run_premarket_summary.py`, `web/src/app/{login,agents,settings}/`, `tests/api/`, `web/e2e/`
방법: provider-env 기반 OAuth redirect/callback, no-secret public provider listing, `.autofolio/premarket/` markdown report storage, GET-only report read API, focused API/E2E/lint validation
감사 로그: AUDIT-2026-06-16-001

## 배경

TASK-045/048로 FastAPI 인증과 에이전트 화면은 구축되었지만, Phase 1b SSO/SNS 구현과 저장형 프리마켓 에이전트 요약은 아직 제품 코드에 연결되지 않았다.

Owner 요청:

- `lint`를 통과시킨다.
- SSO/SNS 로그인을 구현한다.
- 에이전트 탭에 리서치 및 금융 전문가 에이전트를 일단 모두 띄운다.
- 정규장 시작 전 기준의 그날 핵심 요약을 제공한다.
- 자동 스케줄이 아니라 CLI에서 명시적으로 요청하면 파일로 저장하고, UI가 그 저장 파일을 다시 띄운다.

## 범위

- 포함:
  - Google/Kakao/Naver provider 설정이 있을 때만 활성화되는 SSO/SNS redirect/callback.
  - provider secret이나 token을 프론트/API 응답에 노출하지 않는 public provider list.
  - 리서치/금융 전문가 에이전트 metadata 표면화.
  - CLI 명시 실행형 프리마켓 요약 파일 생성.
  - 에이전트 탭에서 최신/지정 요약 파일 조회.
  - focused pytest, `npm run lint`, 필요한 Playwright 갱신.
- 제외:
  - 실제 OAuth 앱/시크릿 생성, provider console 설정, live callback 실인증.
  - 자동 데몬/스케줄러.
  - 주문/조건 저장/리스크 정책 변경.
  - 실전 주문 또는 prod 전환.

## 완료 기준

- SSO/SNS provider가 미설정이면 죽은 버튼 없이 비활성 상태가 표시된다.
- provider 설정이 있으면 `/api/auth/sso/{provider}/login`이 state cookie와 함께 provider authorization URL로 redirect한다.
- callback은 state 검증 후 owner 세션 쿠키를 발급하고 `/home`으로 redirect한다.
- `/api/agents/list`가 전문가 에이전트 metadata를 반환하고, 프론트가 전문가 목록을 표시한다.
- `python scripts/run_premarket_summary.py`가 `.autofolio/premarket/PREMARKET_YYYYMMDD.md`를 저장한다.
- `/api/agents/premarket/summary`와 에이전트 탭이 저장된 요약을 로드한다.
- focused API tests와 `npm run lint`가 green이다.

## Done When

- 변경 파일, 검증 명령, 결과가 이 TASK와 AUDIT-LOG/STATUS에 기록된다.
- `python scripts/check_agent_docs.py` 0 error를 유지한다.

## 완료 기록

완료 시각: 2026-06-16T21:05:31+09:00
검토자: Backend Engineer perspective + UI/UX Designer perspective + QA automated gates
실측 비용 (시간): 약 1.3h
실측 비용 (LLM 토큰): Codex session local meter unavailable
협업 waiver: single-session env scope. 실제 외부 subagent dispatch는 사용하지 않았고 Backend/UI/QA 관점과 자동 게이트 증거로 대체했다.
routing waiver: main-session scope. selected_model/policy_model telemetry는 Codex harness에서 노출되지 않아 focused tests/lint/build/playwright gate로 대체했다.

## 완료 내용

- FastAPI SSO/SNS auth surface 추가:
  - `GET /api/auth/sso/providers`
  - `GET /api/auth/sso/{provider}/login`
  - `GET /api/auth/sso/{provider}/callback`
  - Google/Kakao/Naver provider env 설정 기반 활성화, state cookie 검증, callback owner 세션 발급, allowlist 이메일 게이트.
- 에이전트 API metadata 보강:
  - `/api/agents/list`가 문자열 배열 대신 role/category/description/expert metadata를 반환.
  - `.claude/agents/asset-team/**`와 `agents/*/SKILL.md` 기반 리서치·금융 전문가를 expert로 표기.
- 프리마켓 요약 파일 저장 구현:
  - `scripts/run_premarket_summary.py`
  - `app/services/premarket_summary.py`
  - `.autofolio/premarket/PREMARKET_YYYYMMDD.md` 저장, `GET /api/agents/premarket/summary`로 로드.
- Next.js UI 반영:
  - 로그인 화면 provider 활성 시 SSO/SNS 버튼 표시.
  - 설정 화면 SSO/SNS 활성 provider 표시.
  - 에이전트 화면 상단에 전문가 목록과 저장된 프리마켓 요약 패널 표시.
- lint 정리:
  - 신규 로그인 코드 ESLint error 수정.
  - 기존 `history/page.tsx` hooks warning 제거.

## 변경 파일

- `app/services/sso.py`
- `app/services/premarket_summary.py`
- `app/api/routers/auth.py`
- `app/api/routers/agents.py`
- `app/api/security.py`
- `app/api/schemas/__init__.py`
- `app/services/agents.py`
- `scripts/run_premarket_summary.py`
- `web/src/lib/api.ts`
- `web/src/app/login/page.tsx`
- `web/src/app/settings/page.tsx`
- `web/src/app/agents/page.tsx`
- `web/src/app/history/page.tsx`
- `tests/api/test_auth_sso.py`
- `tests/api/test_premarket_summary.py`
- `tests/api/test_agents_stream.py`
- `web/e2e/login.spec.ts`
- `web/e2e/phase4.spec.ts`

## 검증

- `.\\.venv\\Scripts\\python.exe -m pytest tests/api/test_auth.py tests/api/test_auth_sso.py tests/api/test_agents_stream.py tests/api/test_premarket_summary.py tests/api/test_agents_research.py -q` -> 56 passed, 3 warnings.
- `.\\.venv\\Scripts\\python.exe scripts/run_premarket_summary.py --date 2026-06-16 --dry-run --limit-symbols 2` -> 프리마켓 요약 stdout 생성 성공.
- `.\\.venv\\Scripts\\python.exe scripts/run_premarket_summary.py --date 2026-06-16 --limit-symbols 2` -> `.autofolio/premarket/PREMARKET_20260616.md` 저장 성공.
- `.\\.venv\\Scripts\\python.exe -m py_compile app/services/sso.py app/services/premarket_summary.py app/api/routers/auth.py app/api/routers/agents.py scripts/run_premarket_summary.py` -> OK.
- `npm run lint` (`web/`) -> 0 errors, 0 warnings.
- `npm run build` (`web/`) -> Next.js production build successful, 13 static routes.
- `npx playwright test web/e2e/login.spec.ts web/e2e/phase4.spec.ts` (`web/`) -> 16 passed.
- `git diff --check` -> OK (기존 `logs/events.jsonl` CRLF warning only).

## 증거

- SSO/SNS API contract: `tests/api/test_auth_sso.py`.
- 프리마켓 요약 저장/로드 contract: `tests/api/test_premarket_summary.py`.
- 에이전트 metadata contract: `tests/api/test_agents_stream.py`.
- 로그인/에이전트 UI flow: `web/e2e/login.spec.ts`, `web/e2e/phase4.spec.ts`.
- 저장된 local runtime output: `.autofolio/premarket/PREMARKET_20260616.md` (gitignored).

## 남은 이슈 / 한계

- 실제 Google/Kakao/Naver OAuth 앱 생성과 redirect URI 등록, client secret 입력은 Owner-managed 외부 설정이다. 이 작업에서는 secret을 생성·저장·노출하지 않았다.
- OAuth token exchange는 테스트에서 mocked; live provider callback 검증은 credentials 설정 후 별도 수동 확인 필요.
- 프리마켓 요약은 자동 스케줄이 아니라 CLI 명시 실행만 지원한다.
- `.autofolio/premarket/PREMARKET_20260616.md`는 gitignored local runtime output이다.

## 2026-06-17 보강 기록

- 로그인 화면은 Google/Kakao/Naver provider가 미설정 상태여도 setup shell을 표시하고, 클릭 시 Owner가 준비해야 할 redirect URI와 `.env` 변수 안내를 보여준다.
- 이 보강은 실제 외부 OAuth를 활성화하지 않는다. provider는 credential/env가 준비될 때까지 disabled 상태이며, secret 생성·저장·노출과 live token call은 수행하지 않는다.
- mock provider는 기존 TASK-072 정책대로 `AUTOFOLIO_SSO_MOCK_ENABLED=1`일 때만 개발용 버튼으로 표시된다.
- CI에서 기존 `login.spec.ts`가 "disabled provider는 숨김"을 기대해 실패한 것을 새 UX 계약에 맞게 갱신했다. 검증: `npm run lint`, `npm run build`, `npm run test:e2e -- e2e/login.spec.ts --reporter=line` -> 5 passed, Next demo walkthrough E2E, `check_agent_docs`, `owner_governance_gate`.

## 리뷰

- Backend review: OAuth state는 short-lived signed cookie로 검증하고 provider secret/token은 응답에 포함하지 않았다. 미설정 provider는 503으로 fail-closed한다.
- UI/UX review: 로그인 버튼은 provider가 활성화된 경우에만 표시해 죽은 CTA를 만들지 않았다. 에이전트 탭은 전문가 roster와 저장 요약을 상단에 배치했다.
- QA review: API 56 passed, Playwright 16 passed, lint/build green. 실제 provider callback은 external credential boundary라 mocked test로 제한했다.
- Self-review note: 같은 Codex 세션에서 구현과 기록을 수행했으므로 Independent Audit은 evidence-based same-session review로 제한한다.

## Independent Audit

판정: 통과

근거:

- 주문/조건 저장/리스크/prod surface를 변경하지 않았다.
- OAuth provider secret은 환경변수에서만 읽고 public API에는 enabled/label/kind/id만 노출한다.
- state mismatch, missing provider, unconfigured provider, allowed-email gate가 테스트에 포함됐다.
- 프리마켓 요약 생성은 CLI 명시 실행이고 API는 read-only load만 수행한다.
- lint/build/API/E2E 게이트가 모두 green이다.
